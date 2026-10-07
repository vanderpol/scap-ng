#!/usr/bin/env python3
import unittest

from research_violation_query_semantics import (
    compare_violation_query,
    lossless_shorthand_contract,
    positive_authoring_rewrite_preconditions,
)


class ViolationQuerySemanticTests(unittest.TestCase):
    def test_complete_boolean_matrix_is_equivalent(self):
        cases = [
            ([], "true"),
            (["true"], "true"),
            (["false"], "false"),
            (["true", "true"], "true"),
            (["true", "false"], "false"),
            (["false", "false"], "false"),
        ]
        for values, expected in cases:
            with self.subTest(values=values):
                result = compare_violation_query("complete", values)
                self.assertTrue(result["equivalent"])
                self.assertEqual(result["faithful"], expected)

    def test_incomplete_boolean_matrix_is_equivalent(self):
        cases = [
            ([], "unknown"),
            (["true"], "unknown"),
            (["true", "true"], "unknown"),
            (["false"], "false"),
            (["true", "false"], "false"),
        ]
        for values, expected in cases:
            with self.subTest(values=values):
                result = compare_violation_query("incomplete", values)
                self.assertTrue(result["equivalent"])
                self.assertEqual(result["faithful"], expected)

    def test_complete_unknown_state_is_counterexample(self):
        result = compare_violation_query("complete", ["unknown"])
        self.assertFalse(result["equivalent"])
        self.assertEqual(result["faithful"], "error")
        self.assertEqual(result["candidate"], "unknown")

    def test_complete_not_evaluated_state_is_counterexample(self):
        result = compare_violation_query("complete", ["not evaluated"])
        self.assertFalse(result["equivalent"])
        self.assertEqual(result["faithful"], "error")
        self.assertEqual(result["candidate"], "not evaluated")

    def test_complete_not_applicable_state_is_counterexample(self):
        result = compare_violation_query("complete", ["not applicable"])
        self.assertFalse(result["equivalent"])
        self.assertEqual(result["faithful"], "error")
        self.assertEqual(result["candidate"], "not applicable")

    def test_incomplete_false_plus_unknown_is_counterexample(self):
        result = compare_violation_query(
            "incomplete",
            ["false", "unknown"],
        )
        self.assertFalse(result["equivalent"])
        self.assertEqual(result["faithful"], "error")
        self.assertEqual(result["candidate"], "false")

    def test_filter_error_matches_positive_error_only_for_error_state(self):
        result = compare_violation_query("complete", ["error"])
        self.assertTrue(result["equivalent"])
        self.assertEqual(result["faithful"], "error")

    def test_structural_match_still_cannot_authorize_independent_rewrite(self):
        report = positive_authoring_rewrite_preconditions({
            "source_shape": "exclude_matching_state_then_none_exist",
            "filter_action": "exclude",
            "existence": "none_exist",
        })
        self.assertFalse(report["eligible"])
        self.assertEqual(
            report["reasons"],
            ["non_boolean_filter_state_results_change_semantics"],
        )

    def test_lossless_positive_syntax_must_desugar_to_violation_query(self):
        contract = lossless_shorthand_contract()
        self.assertEqual(contract["semantic_form"], "authoring_shorthand")
        self.assertIn(
            "filter-state non-Boolean error behavior",
            contract["preserves"],
        )


if __name__ == "__main__":
    unittest.main()
