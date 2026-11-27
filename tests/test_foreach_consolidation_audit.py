"""Pinned full-corpus for_each consolidation audit receipts."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "docs/contracts/evidence/foreach-consolidation-65.json"


class ForeachConsolidationAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = json.loads(RECEIPT.read_text())

    def test_receipt_is_source_pinned_and_scope_is_explicit(self):
        source = self.receipt["source"]
        self.assertEqual(source["benchmark_count"], 65)
        self.assertEqual(source["source_rules"], 8892)
        self.assertEqual(source["converted_rules"], 4524)
        self.assertEqual(source["blocked_rules"], 4368)
        self.assertEqual(len(source["tools_commit"]), 40)
        self.assertEqual(len(source["schema_commit"]), 40)
        self.assertRegex(source["stage_manifest_sha256"], r"^[0-9a-f]{64}$")
        self.assertEqual(source["source_repository"], "niwc-atlantic/scap-content-library")
        self.assertEqual(len(source["source_revision"]), 40)
        self.assertRegex(source["source_pins_sha256"], r"^[0-9a-f]{64}$")
        self.assertTrue(source["scope"])

    def test_transfer_pool_and_no_false_replacement_claim(self):
        counts = self.receipt["counts"]
        decision = self.receipt["replacement_decision"]
        self.assertEqual(counts["object_derived_variable_definitions"], 160)
        self.assertEqual(counts["sole_transfer_variable_definitions"], 121)
        self.assertEqual(counts["sole_transfer_selector_references"], 145)
        self.assertEqual(decision["current_for_each_replacements_verified"], 0)
        self.assertEqual(decision["upper_bound_transfer_variables_removable"], 121)
        self.assertEqual(self.receipt["yaml_estimate"]["strict_candidates"], 0)

    def test_legitimate_computation_remains_in_inventory(self):
        counts = self.receipt["counts"]
        self.assertEqual(counts["variable_expression_concat"], 337)
        self.assertEqual(counts["variable_expression_regex_capture"], 90)
        self.assertEqual(counts["variable_expression_merge"], 54)
        self.assertEqual(counts["variable_expression_unique"], 24)
        self.assertEqual(counts["object_derived_not_selector"], 37)
        self.assertEqual(counts["also_used_outside_selector"], 2)

    def test_every_candidate_requires_semantic_review(self):
        candidates = self.receipt["candidates"]
        self.assertEqual(len(candidates), 121)
        self.assertTrue(all(not row["strict_structural_candidate"] for row in candidates))
        self.assertTrue(all(row["reasons"] for row in candidates))


if __name__ == "__main__":
    unittest.main()
