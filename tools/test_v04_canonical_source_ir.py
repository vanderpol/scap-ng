#!/usr/bin/env python3
"""Focused acceptance and rejection fixtures for canonical 0.4 typed source IR."""
from copy import deepcopy
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile
import json

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from v04_canonical_source_ir import normalize_documents, decode_and_verify, compile_pair


def sample():
    return {
        "authoring/demo/benchmark.demo.json": {"benchmark": {
            "id": "demo", "assessment_specifications": [
                {"id": "scap-ng.pre-alpha.assessment", "version": "0.4.0"}]}},
        "authoring/demo/rules/r1.json": {"rule": {"id": "r1",
            "assessment_choices": {"automated": {"assessment": "assessment-1"}},
            "default_assessment_choice": "automated"}},
        "authoring/demo/assessments/a1.json": {"assessment": {
            "id": "assessment-1", "mode": "automated",
            "specification": {"id": "scap-ng.pre-alpha.assessment", "version": "0.4.0"},
            "evaluate": {"test": "t1"},
            "tests": {"t1": {"capability": "unix.file",
                "object": {"select": {"filepath": {"equals": "/etc/example"}}},
                "require": {"items": "one_or_more",
                            "all_items_must": [{"mode": {"equals": "0600"}}]}}}}},
    }


class CanonicalIRTests(unittest.TestCase):
    def test_structured_requirement_preserved_and_redecoded(self):
        src = sample()
        ir = normalize_documents(src)
        self.assertEqual(ir["totals"]["all_items"], 1)
        self.assertEqual(ir["benchmark_version_conflicts"], 0)
        self.assertEqual(decode_and_verify(ir), src)

    def test_presence_and_exception_fallback_distinct(self):
        src = sample()
        a = src["authoring/demo/assessments/a1.json"]["assessment"]["tests"]["t1"]
        a["require"] = {"items": "none"}
        ir = normalize_documents(src)
        self.assertEqual(ir["totals"]["presence"], 1)
        self.assertEqual(decode_and_verify(ir), src)
        a["states"] = [{"mode": {"equals": "0600"}}]
        a["require"] = "at_least_one_exists_and_some_match"
        ir = normalize_documents(src)
        self.assertEqual(ir["totals"]["source_exact_fallback"], 1)
        self.assertEqual(decode_and_verify(ir), src)

    def test_version_mismatch_is_visible_not_rewritten(self):
        src = sample()
        src["authoring/demo/benchmark.demo.json"]["benchmark"][
            "assessment_specifications"][0]["version"] = "0.3.0"
        ir = normalize_documents(src)
        self.assertEqual(ir["benchmark_version_conflicts"], 1)
        self.assertEqual(ir["records"][0]["source_ast"]["assessment"]["specification"]["version"], "0.4.0")
        self.assertEqual(decode_and_verify(ir), src)

    def test_duplicate_id_and_dangling_reference_rejected(self):
        src = sample()
        src["authoring/demo/assessments/duplicate.json"] = deepcopy(
            src["authoring/demo/assessments/a1.json"])
        with self.assertRaisesRegex(ValueError, "duplicate"):
            normalize_documents(src)
        src.pop("authoring/demo/assessments/duplicate.json")
        src["authoring/demo/rules/r1.json"]["rule"]["assessment_choices"]["automated"]["assessment"] = "missing"
        with self.assertRaisesRegex(ValueError, "unresolved"):
            normalize_documents(src)

    def test_conflict_and_mixed_syntax_rejected(self):
        for mutation in (
            lambda t: t.update(collected_items_require="at_least_one_exists"),
            lambda t: t["object"].update(capability="unix.file"),
            lambda t: t.update(states=[]),
            lambda t: t.update(require={"items": "one_or_more", "all_items_must": []}),
        ):
            src = sample()
            t = src["authoring/demo/assessments/a1.json"]["assessment"]["tests"]["t1"]
            mutation(t)
            with self.assertRaises(ValueError):
                normalize_documents(src)

    def test_typed_index_tamper_fails_reconstruction(self):
        ir = normalize_documents(sample())
        ir["records"][0]["typed_tests"][0]["requirement"]["items"] = "none"
        with self.assertRaisesRegex(ValueError, "mismatch"):
            decode_and_verify(ir)

    def test_two_format_loader_byte_parity_and_divergence(self):
        src = sample()
        with tempfile.TemporaryDirectory() as root:
            paths = [Path(root) / "json.zip", Path(root) / "yaml.zip"]
            for path, ext in zip(paths, ("json", "yaml")):
                with zipfile.ZipFile(path, "w") as out:
                    for name, doc in src.items():
                        raw = (json.dumps(doc) if ext == "json" else yaml.safe_dump(doc))
                        out.writestr(name[:-5] + "." + ext, raw)
            data, report = compile_pair(*paths, validate_schema=False)
            self.assertEqual(report["yaml_json_byte_parity"], "PASS")
            self.assertEqual(report["native_source_schema"], "NOT_TESTED_FIXTURE")
            self.assertFalse(report["native_executable_compiler_complete"])
            self.assertEqual(json.loads(data)["format"], "scap-ng-0.4.0-canonical-typed-source-ir/0.1")
            with zipfile.ZipFile(paths[1], "a") as out:
                different = deepcopy(src["authoring/demo/assessments/a1.json"])
                different["assessment"]["tests"]["t1"]["require"]["items"] = "may_be_absent"
                out.writestr("authoring/demo/assessments/a1.yaml", yaml.safe_dump(different))
            with self.assertRaisesRegex(ValueError, "duplicate ZIP member"):
                compile_pair(*paths, validate_schema=False)


if __name__ == "__main__":
    unittest.main()
