#!/usr/bin/env python3
"""Regression tests for NIWC census accounting."""
import json
import tempfile
import unittest
from pathlib import Path

from summarize_niwc_census import summarize, render_markdown


class CensusSummaryTests(unittest.TestCase):
    def test_source_content_defects_are_accounted(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            row = {
                "source": "Current/example.zip",
                "definitions": 5,
                "semantic_equal": 2,
                "deprecated_blockers": 0,
                "publisher_extension_blockers": 0,
                "source_content_defects": 3,
                "unexpected_failures": 0,
                "parse_failures": 0,
            }
            (root / "001-summary.json").write_text(
                json.dumps(row), encoding="utf-8"
            )
            report = summarize(root, ["Current/example.zip"])

        self.assertEqual(report["unaccounted_packages"], [])
        self.assertEqual(report["totals"]["source_content_defects"], 3)
        self.assertEqual(report["totals"]["definitions"], 5)
        markdown = render_markdown(report)
        self.assertIn("Source-content defects quarantined: 3", markdown)
        self.assertIn("| Source defects |", markdown)

    def test_unaccounted_still_fails_classification_contract(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            row = {
                "source": "Current/example.zip",
                "definitions": 5,
                "semantic_equal": 2,
                "deprecated_blockers": 0,
                "publisher_extension_blockers": 0,
                "source_content_defects": 2,
                "unexpected_failures": 0,
                "parse_failures": 0,
            }
            (root / "001-summary.json").write_text(
                json.dumps(row), encoding="utf-8"
            )
            report = summarize(root, ["Current/example.zip"])

        self.assertEqual(
            report["unaccounted_packages"],
            [{"source": "Current/example.zip", "definitions": 5, "classified": 4}],
        )


if __name__ == "__main__":
    unittest.main()
