#!/usr/bin/env python3
"""Focused native 0.4 .scapng compiler, inverse and tamper regressions."""
from copy import deepcopy
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_v04_canonical_source_ir import sample
from v04_a_authoring_graph_index import canonical_json
from v04_canonical_source_ir import validate_docs
from v04_canonical_unsigned_package import (
    _package_validators, build_package as source_package,
)
from v04_native_bundle_compiler import (
    build_bundle, compile_from_archive, compile_from_pair, compile_from_source_package,
    compile_test_instruction, verify_bundle, MANIFEST_MEMBER,
)


def fixture():
    docs = sample()
    docs["authoring/demo/benchmark.demo.json"]["benchmark"].update(
        rules=["r1"], version={"value": "1"})
    return docs


def rewrite(raw, mutate):
    with zipfile.ZipFile(io.BytesIO(raw)) as zf:
        members = {name: zf.read(name) for name in zf.namelist()}
    mutate(members)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        for name, content in members.items():
            zf.writestr(name, content)
    return buffer.getvalue()


def authoring_archives(docs, folder):
    paths = [folder / name for name in ("json.zip", "yaml.zip")]
    for target, ext in zip(paths, ("json", "yaml")):
        with zipfile.ZipFile(target, "w") as zf:
            for name, doc in sorted(docs.items()):
                content = (canonical_json(doc) if ext == "json" else
                           yaml.safe_dump(doc).encode())
                zf.writestr(name[:-5] + "." + ext, content)
    return paths


class NativeBundleCompilerTests(unittest.TestCase):
    def test_real_native_program_and_deterministic_bundle(self):
        docs = fixture()
        raw, manifest = build_bundle(docs, validate_schema=False)
        other, _ = build_bundle(dict(reversed(list(docs.items()))), validate_schema=False)
        self.assertEqual(raw, other)
        result = verify_bundle(raw, validate_schema=False)
        self.assertEqual(result["status"],
                         "NATIVE_040_COMPILED_CONTENT_BUNDLE_NOT_SCANNER_TESTED")
        self.assertEqual((result["documents"], result["programs"], result["tests"]),
                         (3, 1, 1))
        self.assertFalse(result["scanner_evaluated"])
        self.assertEqual(manifest["entrypoint"], "demo")
        self.assertIn("assessment-1", manifest["objects"])
        self.assertIn("assessment-1", manifest["build_provenance"]["compiled_programs"])
        path = manifest["build_provenance"]["compiled_programs"]["assessment-1"]["path"]
        with zipfile.ZipFile(io.BytesIO(raw)) as zf:
            program = json.loads(zf.read(path))
        self.assertEqual(program["test_instructions"][0]["opcode"],
                         "CHECK_ITEM_CONDITION")
        self.assertEqual(program["test_instructions"][0]["operands"]["require"],
                         docs["authoring/demo/assessments/a1.json"]["assessment"]["tests"]["t1"]["require"])
        self.assertEqual(len(program["result_instructions"]), 1)

    def test_independent_yaml_json_compile_parity(self):
        docs = fixture()
        with tempfile.TemporaryDirectory() as td:
            paths = authoring_archives(docs, Path(td))
            json_bundles, json_report = compile_from_archive(
                paths[0], "json", validate_schema=False)
            yaml_bundles, yaml_report = compile_from_archive(
                paths[1], "yaml", validate_schema=False)
            packages, results = compile_from_pair(*paths, validate_schema=False)
        self.assertEqual(set(packages), {"demo"})
        self.assertEqual(results["demo"]["programs"], 1)
        self.assertEqual(json_bundles, yaml_bundles)
        self.assertEqual(packages, json_bundles)
        self.assertEqual(results, json_report)
        self.assertEqual(results, yaml_report)

    def test_single_format_fails_closed_on_versions_and_bad_source(self):
        docs = fixture()
        docs["authoring/demo/benchmark.demo.json"]["benchmark"][
            "assessment_specifications"][0]["version"] = "0.3.0"
        with tempfile.TemporaryDirectory() as td:
            paths = authoring_archives(docs, Path(td))
            for source_format, path in zip(("json", "yaml"), paths):
                with self.subTest(source_format=source_format):
                    with self.assertRaisesRegex(ValueError, "versions are incompatible"):
                        compile_from_archive(path, source_format, validate_schema=False)

            with zipfile.ZipFile(paths[0], "w") as zf:
                zf.writestr("authoring/demo/assessment.json",
                            b'{"assessment":{"id":"first","id":"second"}}')
            with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                compile_from_archive(paths[0], "json", validate_schema=False)

            with zipfile.ZipFile(paths[1], "w") as zf:
                zf.writestr("authoring/demo/assessment.yaml", b"assessment: [")
            with self.assertRaises(ValueError):
                compile_from_archive(paths[1], "yaml", validate_schema=False)

    def test_single_format_rejects_missing_and_duplicate_references(self):
        docs = fixture()
        docs["authoring/demo/rules/r1.json"]["rule"]["assessment_choices"][
            "automated"]["assessment"] = "nonexistent"
        with tempfile.TemporaryDirectory() as td:
            paths = authoring_archives(docs, Path(td))
            for source_format, path in zip(("json", "yaml"), paths):
                with self.subTest(source_format=source_format):
                    with self.assertRaisesRegex(ValueError, "unresolved"):
                        compile_from_archive(path, source_format, validate_schema=False)
        docs = fixture()
        docs["authoring/demo/assessments/duplicate.json"] = deepcopy(
            docs["authoring/demo/assessments/a1.json"])
        with tempfile.TemporaryDirectory() as td:
            paths = authoring_archives(docs, Path(td))
            for source_format, path in zip(("json", "yaml"), paths):
                with self.subTest(source_format=source_format):
                    with self.assertRaisesRegex(ValueError, "duplicate"):
                        compile_from_archive(path, source_format, validate_schema=False)

    def test_paired_compilation_rejects_divergent_bundle_bytes(self):
        with tempfile.TemporaryDirectory() as td:
            paths = authoring_archives(fixture(), Path(td))
            with patch("v04_native_bundle_compiler._build_partitioned_bundles",
                       side_effect=[{"demo": b"json"}, {"demo": b"yaml"}]):
                with self.assertRaisesRegex(ValueError, "compiled bundle mismatch"):
                    compile_from_pair(*paths, validate_schema=False)

    def test_source_package_is_input_not_mislabeled_bundle(self):
        source, _ = source_package(fixture(), validate_schema=False)
        with self.assertRaisesRegex(ValueError, "supported compiled"):
            verify_bundle(source, validate_schema=False)
        compiled, report = compile_from_source_package(source, validate_schema=False)
        self.assertNotEqual(compiled, source)
        self.assertEqual(report["programs"], 1)
        with tempfile.TemporaryDirectory() as td:
            paths = authoring_archives(fixture(), Path(td))
            directly_compiled, direct_report = compile_from_pair(*paths,
                                                                  validate_schema=False)
        self.assertEqual(directly_compiled, {"demo": compiled})
        self.assertEqual(direct_report["demo"], report)

    def test_manual_alternative_retained_without_inventing_a_native_program(self):
        docs = fixture()
        manual = {"assessment": {
            "id": "manual-assessment-1", "version": 1,
            "assessment_title": "Check the configured file permission",
            "mode": "manual", "class": "compliance", "purpose": "assessment",
            "procedure": "Review the configured permission with the system owner.",
            "response": {
                "type": "human-compliance-disposition",
                "choices": [
                    {"value": "compliant", "outcome": "true"},
                    {"value": "noncompliant", "outcome": "false"},
                ],
                "allow_comment": True, "allow_evidence": True,
            },
        }}
        validate_docs({"authoring/demo/assessments/manual.json": manual},
                      _package_validators())
        invalid_manual = deepcopy(manual)
        invalid_manual["assessment"].pop("response")
        with self.assertRaisesRegex(ValueError, "native 0.4.0 schema failure"):
            validate_docs({"authoring/demo/assessments/manual.json": invalid_manual},
                          _package_validators())
        docs["authoring/demo/assessments/manual.json"] = manual
        choices = docs["authoring/demo/rules/r1.json"]["rule"]["assessment_choices"]
        choices["manual"] = {"assessment": "manual-assessment-1"}
        raw, manifest = build_bundle(docs, validate_schema=False)
        checked = verify_bundle(raw, validate_schema=False)
        self.assertEqual((checked["documents"], checked["programs"], checked["tests"]),
                         (4, 1, 1))
        self.assertIn("manual-assessment-1", manifest["objects"])
        self.assertNotIn("manual-assessment-1",
                         manifest["build_provenance"]["compiled_programs"])
        with zipfile.ZipFile(io.BytesIO(raw)) as zf:
            member = manifest["objects"]["manual-assessment-1"]["path"]
            self.assertEqual(json.loads(zf.read(member)), manual)
        self.assertFalse(checked["scanner_evaluated"])
        with tempfile.TemporaryDirectory() as td:
            paths = authoring_archives(docs, Path(td))
            independent, report = compile_from_pair(*paths, validate_schema=False)
        self.assertEqual(independent, {"demo": raw})
        self.assertEqual(report["demo"], checked)

    def test_legacy_source_exact_fallback_is_rejected(self):
        test = deepcopy(fixture()["authoring/demo/assessments/a1.json"]["assessment"]["tests"]["t1"])
        test["require"] = "at_least_one_exists_and_some_match"
        test["states"] = [{"mode": {"equals": "0600",
                                      "require": "at_least_one_exists_and_all_match"}}]
        with self.assertRaises(ValueError):
            compile_test_instruction("t1", test)

    def test_approved_requirements_reject_legacy_unknown_and_invalid_counts(self):
        original = fixture()['authoring/demo/assessments/a1.json']['assessment']['tests']['t1']
        changes = [('state', {}), ('states', []), ('states_match', 'all'),
                   ('item_conditions', []), ('unknown', True)]
        for key, value in changes:
            bad = deepcopy(original); bad[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                compile_test_instruction('t1', bad)
        for key in ('items_found', 'items_satisfying'):
            for value in ('all', 'one', 'invalid', 'all_exist'):
                bad = deepcopy(original); bad['require'][key] = value
                with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                    compile_test_instruction('t1', bad)
        bad = deepcopy(original); bad['require'] = 'none_exist'
        with self.assertRaises(ValueError): compile_test_instruction('t1', bad)
        for key in ('values_found', 'values_matching'):
            bad = deepcopy(original); bad['require']['fields']['mode'][key] = 'invalid'
            with self.assertRaises(ValueError): compile_test_instruction('t1', bad)

    def test_referenced_object_resolution_and_capability_conflicts(self):
        from v04_native_bundle_compiler import compile_assessment_program
        a = deepcopy(fixture()['authoring/demo/assessments/a1.json']['assessment'])
        obj = a['tests']['t1']['object']
        a['shared_objects'] = {'shared-object': {'capability': 'unix.file', **obj}}
        a['tests']['t1']['object'] = 'shared-object'
        self.assertEqual(len(compile_assessment_program(a)['test_instructions']), 1)
        a['shared_objects']['shared-object']['capability'] = 'windows.registry'
        with self.assertRaisesRegex(ValueError, 'capability conflicts'):
            compile_assessment_program(a)
        a['shared_objects'] = {}
        with self.assertRaisesRegex(ValueError, 'unresolved'):
            compile_assessment_program(a)

    def test_reject_missing_or_damaged_program(self):
        raw, manifest = build_bundle(fixture(), validate_schema=False)
        program_path = manifest["build_provenance"]["compiled_programs"]["assessment-1"]["path"]
        with self.assertRaisesRegex(ValueError, "missing or duplicate compiled program"):
            verify_bundle(rewrite(raw, lambda files: files.pop(program_path)),
                          validate_schema=False)
        with self.assertRaisesRegex(ValueError, "compiled program digest mismatch"):
            verify_bundle(rewrite(raw, lambda files: files.__setitem__(program_path,
                                                                       files[program_path] + b" ")),
                          validate_schema=False)

    def test_reject_stale_plan_even_with_rehashed_manifest(self):
        raw, manifest = build_bundle(fixture(), validate_schema=False)
        program_path = manifest["build_provenance"]["compiled_programs"]["assessment-1"]["path"]

        def forge(files):
            from hashlib import sha256
            program = json.loads(files[program_path])
            program["test_instructions"][0]["operands"]["require"]["items_found"] = "none"
            altered = canonical_json(program)
            files[program_path] = altered
            revised = json.loads(files[MANIFEST_MEMBER])
            row = revised["build_provenance"]["compiled_programs"]["assessment-1"]
            row.update(size=len(altered), sha256=sha256(altered).hexdigest())
            files[MANIFEST_MEMBER] = canonical_json(revised)

        with self.assertRaisesRegex(ValueError, "stale or has altered Test semantics"):
            verify_bundle(rewrite(raw, forge), validate_schema=False)

    def test_reject_unlisted_member_and_incomplete_rule_inventory(self):
        raw, _ = build_bundle(fixture(), validate_schema=False)
        with self.assertRaisesRegex(ValueError, "extra or unlisted"):
            verify_bundle(rewrite(raw, lambda files: files.update({"extra": b"payload"})),
                          validate_schema=False)
        docs = fixture()
        docs["authoring/demo/benchmark.demo.json"]["benchmark"]["rules"] = []
        with self.assertRaisesRegex(ValueError, "Rule list"):
            build_bundle(docs, validate_schema=False)


if __name__ == "__main__":
    unittest.main()
