#!/usr/bin/env python3
"""Canonical 0.4.0 six-state expression backend acceptance fixtures (#232)."""
from copy import deepcopy
from itertools import product
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from v04_canonical_result_plan import (
    STAGE, SPEC, compile_canonical_result_plan, evaluate_supplied_results,
    census_authoring, _legacy_result_tree,
)
from v04_a_truth_plan import combine, SIX, UnsupportedExpression


def authored(expression, tests=("left-test", "right-test", "third-test")):
    return {
        "id": "native-040-bool-assessment",
        "mode": "automated",
        "specification": deepcopy(SPEC),
        "tests": {name: {"capability": "unix.file"} for name in tests},
        "evaluate": expression,
    }


def paired(operator):
    return {operator: [{"test": "left-test"}, {"test": "right-test"}]}


class CanonicalResultPlanTests(unittest.TestCase):
    def test_canonical_and_or_xor_match_original_oval_six_state_algebra(self):
        for modern, legacy in (("and", "all"), ("or", "any"),
                               ("one", "one"), ("xor", "odd")):
            modern_plan = compile_canonical_result_plan(authored(paired(modern)))
            legacy_plan = compile_canonical_result_plan(authored(paired(legacy)))
            self.assertEqual(modern_plan["instructions"], legacy_plan["instructions"])
            self.assertNotEqual(modern_plan["source_sha256"],
                                legacy_plan["source_sha256"]) if modern != legacy else None
            for left, right in product(sorted(SIX), repeat=2):
                supplied = {"left-test": left, "right-test": right}
                result = evaluate_supplied_results(modern_plan, supplied)
                self.assertEqual(result["outcome"], combine(legacy, (left, right)))
                self.assertEqual(result["outcome"], evaluate_supplied_results(
                    legacy_plan, supplied)["outcome"])
                self.assertFalse(result["scanner_executed"])
                self.assertFalse(result["tests_evaluated"])
                self.assertEqual(result["stage"], STAGE)

    def test_nested_composition_and_not_preserve_unknown_and_absence(self):
        tree = {"or": [
            {"not": {"test": "left-test"}},
            {"and": [{"test": "right-test"},
                     {"not_applicable": {"reason": "Not installed"}}]},
        ]}
        plan = compile_canonical_result_plan(authored(tree))
        self.assertEqual(evaluate_supplied_results(
            plan, {"left-test": "true", "right-test": "false"})["outcome"],
            "false")
        self.assertEqual(evaluate_supplied_results(
            plan, {"left-test": "unknown", "right-test": "false"})["outcome"],
            "unknown")
        self.assertEqual(evaluate_supplied_results(
            plan, {"left-test": "false", "right-test": "error"})["outcome"],
            "true")
        self.assertEqual(plan["requires"]["tests"], ["left-test", "right-test"])

    def test_dependency_leaf_requires_explicit_result(self):
        x = authored({"and": [{"test": "left-test"}, {"assessment": "server-assessment"}]})
        x["dependencies"] = {"server-assessment": {"expected_id": "some-assessment"}}
        plan = compile_canonical_result_plan(x)
        result = evaluate_supplied_results(
            plan, {"left-test": "true"}, {"server-assessment": "unknown"})
        self.assertEqual(result["outcome"], "unknown")
        for bad in (None, {}, {"other": "true"}):
            with self.subTest(bad=bad), self.assertRaisesRegex(ValueError, "result keys"):
                evaluate_supplied_results(plan, {"left-test": "true"}, bad)

    def test_conditional_is_explicitly_unsupported_not_assumed_false(self):
        conditional = {"if": {"test": "left-test"},
                       "then": {"test": "right-test"},
                       "else": {"test": "third-test"}}
        with self.assertRaises(UnsupportedExpression):
            compile_canonical_result_plan(authored(conditional))
        report = census_authoring({
            "authoring/a/first.json": {"assessment": authored(paired("and"))},
            "authoring/a/second.json": {"assessment": authored(conditional)},
        })
        self.assertEqual(report["counts"]["automated_assessments"], 2)
        self.assertEqual(report["counts"]["compiled_supplied_result_plans"], 1)
        self.assertEqual(report["counts"]["unsupported_result_expressions"], 1)
        self.assertFalse(report["conditional_semantics_implemented"])

    def test_fail_closed_unsupported_and_malformed_source(self):
        base = authored(paired("and"))
        changed = deepcopy(base)
        changed["specification"]["version"] = "0.3.0"
        with self.assertRaisesRegex(ValueError, "0.4.0"):
            compile_canonical_result_plan(changed)
        for expr in (
            {"and": []},
            {"and": [{"test": "left-test"}, {"test": "nonexistent-test"}]},
            {"and": [{"test": "left-test"}], "or": [{"test": "right-test"}]},
            {"and": [{"test": "left-test"}, {"not": []}]},
            {"mystery": [{"test": "left-test"}]},
        ):
            with self.subTest(expr=expr), self.assertRaises((ValueError, UnsupportedExpression)):
                compile_canonical_result_plan(authored(expr))
        plan = compile_canonical_result_plan(base)
        with self.assertRaisesRegex(ValueError, "result keys"):
            evaluate_supplied_results(plan, {"left-test": "true"})
        with self.assertRaisesRegex(ValueError, "invalid six-state"):
            evaluate_supplied_results(plan, {"left-test": "true",
                                              "right-test": "pass"})
        bad_plan = deepcopy(plan)
        bad_plan["stage"] = "SCANNER_EXECUTABLE"
        with self.assertRaisesRegex(ValueError, "unsupported native"):
            evaluate_supplied_results(bad_plan, {"left-test": "true",
                                                "right-test": "true"})


if __name__ == "__main__":
    unittest.main()
