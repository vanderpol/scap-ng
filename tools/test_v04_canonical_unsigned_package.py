#!/usr/bin/env python3
"""Canonical 0.4.0 unsigned native-manifest package gates (not scanner parity)."""
from copy import deepcopy
from unittest.mock import patch
import io
import json
from pathlib import Path
import sys
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_v04_canonical_source_ir import sample
from v04_canonical_unsigned_package import (
    build_package, verify_package, partition_documents, MANIFEST_MEMBER,
    _manifest_schema, package_pair, _package_validators,
)

def mutate(raw, fn):
    with zipfile.ZipFile(io.BytesIO(raw)) as zf:
        members = {n: zf.read(n) for n in zf.namelist()}
    fn(members)
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as zf:
        for key, value in members.items():
            zf.writestr(key, value)
    return stream.getvalue()


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.docs = sample()
        self.docs['authoring/demo/benchmark.demo.json']['benchmark']['rules'] = ['r1']
        self.docs['authoring/demo/benchmark.demo.json']['benchmark']['version'] = {'value': '1'}

    def test_deterministic_and_manifest_v04(self):
        archive, manifest = build_package(self.docs, validate_schema=False)
        other, _ = build_package(dict(reversed(list(self.docs.items()))), validate_schema=False)
        self.assertEqual(archive, other)
        _manifest_schema().validate(manifest)
        result = verify_package(archive, validate_schema=False)
        self.assertEqual(result["documents"], 3)
        self.assertEqual(result["rule_choice_links"], 1)
        self.assertFalse(result["signature_verified"])
        self.assertIn("NOT_EXECUTABLE", result["status"])
        self.assertEqual(manifest["signature"]["format"], None)

    def test_package_pair_keeps_independent_schema_verification(self):
        """The writer does not repeat input schema checks; decoder still does."""
        from v04_canonical_source_ir import normalize_documents
        from v04_a_authoring_graph_index import canonical_json
        source_ir = canonical_json(normalize_documents(self.docs))
        with patch("v04_canonical_unsigned_package.compile_pair",
                   return_value=(source_ir, {"version_conflicting_choice_links": 0})), \
             patch("v04_canonical_unsigned_package.build_package",
                   return_value=(b"fixture", {})) as writer, \
             patch("v04_canonical_unsigned_package.verify_package",
                   return_value={"status": "VALIDATED_UNSIGNED_SOURCE_PACKAGE_NOT_EXECUTABLE",
                                 "signature_verified": False}) as decoder:
            archives, report = package_pair(None, None, validate_schema=True)
        self.assertEqual(list(archives), ["demo"])
        self.assertFalse(report["native_compiler_complete"])
        self.assertFalse(report["signed"])
        self.assertEqual(writer.call_args.kwargs["validate_schema"], False)
        self.assertEqual(decoder.call_args.kwargs["validate_schema"], True)

    def test_checked_in_package_validators_reused(self):
        self.assertIs(_package_validators(), _package_validators())

    def test_partition_scope_and_missing_rule_rejected(self):
        src = deepcopy(self.docs)
        folders = partition_documents(src)
        self.assertEqual(set(folders), {"demo"})
        self.assertEqual(len(folders["demo"]), 3)
        bench = src["authoring/demo/benchmark.demo.json"]["benchmark"]
        bench["rules"] = ["unlisted"]
        with self.assertRaisesRegex(ValueError, "Rule list"):
            partition_documents(src)

    def test_unsigned_package_rejects_extra_member(self):
        archive, _ = build_package(self.docs, validate_schema=False)
        with self.assertRaisesRegex(ValueError, "extra unlisted"):
            verify_package(mutate(archive, lambda files: files.update({"hidden": b"evil"})),
                           validate_schema=False)

    def test_unsigned_package_rejects_damaged_document(self):
        archive, _ = build_package(self.docs, validate_schema=False)
        def damage(files):
            name = next(p for p in files if p.startswith("documents/assessment"))
            files[name] += b" "
        with self.assertRaisesRegex(ValueError, "member digest"):
            verify_package(mutate(archive, damage), validate_schema=False)

    def test_unsigned_package_rejects_falsely_signed_manifest(self):
        archive, _ = build_package(self.docs, validate_schema=False)
        def forge(files):
            manifest = json.loads(files[MANIFEST_MEMBER])
            manifest["build_provenance"]["signature_verified"] = True
            files[MANIFEST_MEMBER] = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
        with self.assertRaisesRegex(ValueError, "unknown or falsely executable"):
            verify_package(mutate(archive, forge), validate_schema=False)

    def test_manifest_cannot_claim_another_format_version(self):
        archive, _ = build_package(self.docs, validate_schema=False)
        def forge(files):
            manifest = json.loads(files[MANIFEST_MEMBER])
            manifest["format_version"] = "0.3.0"
            files[MANIFEST_MEMBER] = json.dumps(
                manifest, sort_keys=True, separators=(",", ":")
            ).encode()
        with self.assertRaisesRegex(ValueError, "format_version 0.4.0"):
            verify_package(mutate(archive, forge), validate_schema=False)

    def test_manifest_cannot_change_declared_source_scope(self):
        archive, _ = build_package(self.docs, validate_schema=False)
        def forge(files):
            manifest = json.loads(files[MANIFEST_MEMBER])
            manifest["build_provenance"]["scope"] = "partial-source-only"
            files[MANIFEST_MEMBER] = json.dumps(
                manifest, sort_keys=True, separators=(",", ":")
            ).encode()
        with self.assertRaisesRegex(ValueError, "falsely executable"):
            verify_package(mutate(archive, forge), validate_schema=False)

    def test_unlisted_and_duplicate_rules_rejected_at_package_boundary(self):
        docs = deepcopy(self.docs)
        extra = deepcopy(docs["authoring/demo/rules/r1.json"])
        extra["rule"]["id"] = "r2"
        docs["authoring/demo/rules/r2.json"] = extra
        # An extra, separately valid Rule must not silently enter a bundle
        # unless its Benchmark explicitly lists it.
        with self.assertRaisesRegex(ValueError, "Rule list"):
            build_package(docs, validate_schema=False)
        with self.assertRaisesRegex(ValueError, "Rule list"):
            partition_documents(docs)
        docs = deepcopy(self.docs)
        docs["authoring/demo/benchmark.demo.json"]["benchmark"]["rules"] = ["r1", "r1"]
        with self.assertRaisesRegex(ValueError, "Rule list"):
            build_package(docs, validate_schema=False)

    def test_missing_assessment_and_old_spec_fail(self):
        x = deepcopy(self.docs)
        x["authoring/demo/rules/r1.json"]["rule"]["assessment_choices"]["automated"]["assessment"] = "missing"
        with self.assertRaisesRegex(ValueError, "unresolved"):
            build_package(x, validate_schema=False)
        x = deepcopy(self.docs)
        x["authoring/demo/benchmark.demo.json"]["benchmark"]["assessment_specifications"] = [
            {"id": "scap-ng.pre-alpha.assessment", "version": "0.3.0"}]
        with self.assertRaisesRegex(ValueError, "incompatible"):
            build_package(x, validate_schema=False)


if __name__ == "__main__":
    unittest.main()
