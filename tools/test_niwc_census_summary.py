#!/usr/bin/env python3
"""Regression checks for honest NIWC round-trip census accounting."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

MODULE = Path(__file__).resolve().parent / "scap_ng_roundtrip_v003" / "summarize_niwc_census.py"
spec = importlib.util.spec_from_file_location("niwc_census", MODULE)
census = importlib.util.module_from_spec(spec)
spec.loader.exec_module(census)


class CensusSummaryTests(unittest.TestCase):
    def write(self, folder, filename, **fields):
        (folder / filename).write_text(json.dumps(fields), encoding="utf-8")

    def test_valid_all_classes_accounted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write(root, "001-summary.json", source="a", definitions=7,
                       semantic_equal=4, deprecated_blockers=1,
                       publisher_extension_blockers=2, unexpected_failures=0)
            report = census.summarize(root, ["a"])
            self.assertEqual(report["totals"]["definitions"], 7)
            self.assertEqual(report["unaccounted_packages"], [])
            self.assertEqual(report["missing_sources"], [])

    def test_missing_report_is_visible(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = census.summarize(Path(tmp), ["a"])
            self.assertEqual(report["missing_sources"], ["a"])

    def test_unaccounted_definition_is_not_silent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write(root, "001-summary.json", source="a", definitions=3,
                       semantic_equal=2, unexpected_failures=0)
            report = census.summarize(root, ["a"])
            self.assertEqual(report["unaccounted_packages"][0]["classified"], 2)

    def test_empty_expected_corpus_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                census.summarize(Path(tmp), [])

    def test_duplicate_source_is_visible(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write(root, "001-summary.json", source="a", definitions=1,
                       semantic_equal=1)
            self.write(root, "002-summary.json", source="a", definitions=1,
                       semantic_equal=1)
            report = census.summarize(root, ["a"])
            self.assertEqual(report["duplicate_sources"], ["a"])


if __name__ == "__main__":
    unittest.main()
