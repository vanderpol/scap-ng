#!/usr/bin/env python3
"""Canonical 0.4.0 unsigned native-manifest package gates (not scanner parity)."""
from copy import deepcopy
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
    _manifest_schema,
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
