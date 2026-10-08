#!/usr/bin/env python3
"""Focused checks for SCAP-NG 0.3 Test-centered Assessment evidence."""
import copy
import json
import unittest
from pathlib import Path

from validate_v03_assessment_result_semantics import validate_assessment_result_semantics

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "specification" / "examples" / "0.3.0" / "results"
AUTOMATED = (
    "assessment-result.json",
    "assessment-result-multi-file.json",
    "assessment-result-bounded-evidence.json",
    "assessment-result-diagnostic-override.json",
)


def load(name="assessment-result.json"):
    return json.loads((EXAMPLES / name).read_text(encoding="utf-8"))


def codes(document):
    return {entry["code"] for entry in validate_assessment_result_semantics(document)}


class AssessmentEvidenceIntegrityTests(unittest.TestCase):
    def test_checked_in_automated_examples_are_consistent(self):
        for filename in AUTOMATED:
            with self.subTest(filename=filename):
                self.assertEqual(validate_assessment_result_semantics(load(filename)), [])

    def test_missing_item_summary_rejected(self):
        doc = load()
        del doc["assessment_result"]["tests"][0]["item_summary"]
        self.assertIn("test.missing_item_summary", codes(doc))

    def test_returned_count_cannot_disagree_with_inline_items(self):
        doc = load()
        doc["assessment_result"]["tests"][0]["item_summary"]["returned_items"] = 99
        self.assertIn("test.returned_count_mismatch", codes(doc))

    def test_item_id_must_resolve_to_retained_item_ref(self):
        doc = load()
        doc["assessment_result"]["tests"][0]["per_item_results"][0]["item"]["id"] = "other-item"
        self.assertIn("item.identity_mismatch", codes(doc))

    def test_retention_cap_is_not_ignored(self):
        doc = load("assessment-result-multi-file.json")
        doc["assessment_result"]["evidence_retention"]["maximum_items"] = 2
        self.assertIn("test.exceeds_retention_limit", codes(doc))

    def test_omitted_failures_must_be_reported_honestly(self):
        doc = load("assessment-result-bounded-evidence.json")
        doc["assessment_result"]["tests"][0]["item_summary"]["truncated_evidence"] = False
        doc["assessment_result"]["evidence_summary"]["truncated_population"] = False
        self.assertIn("test.omitted_failures_not_marked", codes(doc))
        self.assertIn("evidence.omission_not_marked", codes(doc))

    def test_known_totals_cannot_be_below_observed(self):
        doc = load("assessment-result-bounded-evidence.json")
        doc["assessment_result"]["tests"][0]["item_summary"]["actual_mismatches"] = 1
        doc["assessment_result"]["evidence_summary"]["actual_failures"] = 1
        self.assertIn("test.actual_below_observed", codes(doc))
        self.assertIn("evidence.actual_below_observed", codes(doc))

    def test_two_distinct_checks_can_report_same_system_item(self):
        doc = load("assessment-result-multi-file.json")
        results = doc["assessment_result"]["tests"]
        self.assertEqual(results[0]["per_item_results"][1]["item"],
                         results[1]["per_item_results"][0]["item"])
        self.assertEqual(validate_assessment_result_semantics(doc), [])

    def test_normal_and_debug_scans_share_content_identity_and_truth(self):
        a = load("assessment-result-bounded-evidence.json")["assessment_result"]
        b = load("assessment-result-diagnostic-override.json")["assessment_result"]
        for key in ("assessment", "outcome", "logical_complete", "population_complete"):
            self.assertEqual(a[key], b[key])
        self.assertEqual(a["tests"][0]["item_summary"]["observed_mismatches"],
                         b["tests"][0]["item_summary"]["observed_mismatches"])
        self.assertLess(a["evidence_retention"]["maximum_items"],
                        b["evidence_retention"]["maximum_items"])
        self.assertLess(len(a["tests"][0]["per_item_results"]),
                        len(b["tests"][0]["per_item_results"]))


if __name__ == "__main__":
    unittest.main()
