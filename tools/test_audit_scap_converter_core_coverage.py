#!/usr/bin/env python3
"""Source-level, denominator-preserving 0.3/0.4 coverage audit tests."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from audit_scap_converter_core_coverage import inventory
from test_audit_v04_original_oval_forward import shell_source, registry_source


class ConverterCoverageInventoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_two_positive_original_oval_sources_separately_counted(self):
        (self.root / "shell.xml").write_bytes(shell_source())
        (self.root / "registry.xml").write_bytes(registry_source())
        r = inventory(self.root)
        self.assertEqual(r["counts"]["xml_files"], 2)
        self.assertEqual(r["counts"]["definitions"], 2)
        self.assertEqual(r["counts"]["v003_source_lowering_pass"], 2)
        self.assertEqual(r["counts"]["maintained_v004_core_source_proven"], 2)
        self.assertNotIn("v003_lowerable_but_v004_unproved", r["counts"])
        self.assertEqual({entry["maintained_v004_core"] for entry in r["definitions"]},
                         {"SOURCE_PROVEN"})
        self.assertEqual(r["lowerable_but_unproved"]["blocked_0_3_lowerable_definitions"], 0)
        self.assertTrue(all(entry["v003_shape"]["tests"] == 1
                            for entry in r["definitions"]))
        self.assertFalse(r["full_oval_coverage"])
        self.assertFalse(r["scanner_parity"])

    def test_unsupported_semantics_visible_in_denominator(self):
        (self.root / "shell.xml").write_bytes(shell_source().replace(
            b'action="include"', b'action="exclude"'))
        result = inventory(self.root)
        self.assertEqual(result["counts"]["definitions"], 1)
        self.assertEqual(result["counts"]["maintained_v004_core_blocked_nondeprecated"], 1)
        self.assertEqual(result["definitions"][0]["maintained_v004_core"], "BLOCKED")
        self.assertIn("v004_diagnostic", result["definitions"][0])
        self.assertEqual(result["lowerable_but_unproved"]["blocked_0_3_lowerable_definitions"], 1)
        self.assertIn("independent.shellcommand",
                      result["lowerable_but_unproved"]["by_capability"])

    def test_malformed_extra_file_does_not_hide_valid_definition(self):
        (self.root / "shell.xml").write_bytes(shell_source())
        (self.root / "unreadable.xml").write_text("<not-xml")
        result = inventory(self.root)
        self.assertEqual(result["counts"]["xml_files"], 2)
        self.assertEqual(result["counts"]["source_parse_blocked_files"], 1)
        self.assertEqual(result["counts"]["definitions"], 1)
        self.assertEqual(result["counts"]["maintained_v004_core_source_proven"], 1)
        self.assertEqual(len(result["definitions"]), 2)

    def test_public_readonly_cli_report(self):
        path = self.root / "original.xml"
        path.write_bytes(registry_source())
        report = self.root / "coverage.json"
        subprocess.run([
            sys.executable, str(Path(__file__).with_name("audit_scap_converter_core_coverage.py")),
            "--source", str(path), "--report", str(report),
        ], check=True, capture_output=True, text=True)
        self.assertEqual(json.loads(report.read_text())["counts"]["definitions"], 1)

    def test_both_externally_pinned_variable_cases_are_accounted_when_available(self):
        paths = [os.getenv("SCAP_NG_VARIABLE_SOURCE_XML"),
                 os.getenv("SCAP_NG_FAMILY_SOURCE_XML")]
        if not all(paths):
            self.skipTest("dedicated CI workflow supplies both pinned OVAL sources")
        for file in paths:
            with self.subTest(source=file):
                result = inventory(Path(file))
                self.assertEqual(result["counts"]["definitions"], 1)
                self.assertEqual(result["counts"]["v003_source_lowering_pass"], 1)
                self.assertEqual(result["counts"]["maintained_v004_core_source_proven"], 1)


if __name__ == "__main__":
    unittest.main()
