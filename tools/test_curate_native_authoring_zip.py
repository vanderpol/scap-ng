#!/usr/bin/env python3
"""Focused packaging regression: converter reports never enter native authoring ZIPs."""
from pathlib import Path
import tempfile
import unittest
import zipfile

from curate_native_authoring_zip import (
    BENCHMARKS, ENGINEERING_SIDECARS, curate, native_yaml,
)


class CurateNativeAuthoringTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.input = self.root / "input.zip"
        self.output = self.root / "clean.zip"
        self.files = {"README.md": b"old generated readme"}
        for key in BENCHMARKS:
            self.files[f"authoring/{key}/benchmark.yaml"] = (
                f"benchmark:\n  id: benchmark.{key}\n  metadata:\n    publisher: [DISA]\n"
            ).encode()
            self.files[f"authoring/{key}/applicability.yaml"] = b"applicability: {}\n"
            for sidecar in ENGINEERING_SIDECARS:
                self.files[f"authoring/{key}/{sidecar}"] = b'{"report":true}\n'
        self.files["authoring/shared/assessments/linux/files/common.assessment.yaml"] = (
            b"assessment:\n  id: ng.shared.common\n"
        )

    def write_input(self):
        with zipfile.ZipFile(self.input, "w") as archive:
            for name, data in self.files.items():
                archive.writestr(name, data)

    def test_native_yaml_and_authority_metadata_preserved(self):
        self.write_input()
        result = curate(self.input, self.output, expected_yaml=13)
        self.assertEqual(48, result["removed_engineering_json_files"])
        self.assertTrue(result["native_yaml_unchanged"])
        with zipfile.ZipFile(self.output) as archive:
            names = set(archive.namelist())
            self.assertEqual(14, len(names))
            self.assertEqual({"README.md"}, {n for n in names if not n.endswith(".yaml")})
            for name, payload in self.files.items():
                if name.endswith(".yaml"):
                    self.assertEqual(payload, archive.read(name))
            self.assertIn(b"DISA", archive.read("authoring/rhel_9/benchmark.yaml"))

    def test_unknown_sidecar_fails_closed(self):
        self.files["authoring/rhel_9/not-native.json"] = b"{}"
        self.write_input()
        with self.assertRaisesRegex(ValueError, "classify explicitly"):
            curate(self.input, self.output)

    def test_missing_benchmark_fails_closed(self):
        del self.files["authoring/rhel_9/benchmark.yaml"]
        self.write_input()
        with self.assertRaisesRegex(ValueError, "Missing Benchmark"):
            curate(self.input, self.output)

    def test_nonnative_and_traversal_paths_not_allowed(self):
        self.assertFalse(native_yaml("authoring/rhel_9/rules/../../escape.yaml"))
        self.assertFalse(native_yaml("authoring/rhel_9/grouping-provenance.json"))
        self.assertFalse(native_yaml("authoring/unknown/benchmark.yaml"))
        self.assertFalse(native_yaml("authoring/rhel_9/source-generation.yaml"))
        self.assertTrue(native_yaml("authoring/shared/assessments/linux/files/one.assessment.yaml"))


if __name__ == "__main__":
    unittest.main()
