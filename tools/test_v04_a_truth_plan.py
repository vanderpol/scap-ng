#!/usr/bin/env python3
"""#232/#229: result-only 0.4-A expression execution boundary tests."""
from copy import deepcopy
from itertools import product
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from oval_result_truth_tables import aggregate_operator
from v04_a_truth_plan import (STAGE, SIX, UnsupportedExpression,
                              compile_expression, combine,
                              execute_supplied_results)


def source(expression, *, deps=None):
    return {"id": "synthetic.0.4.expression", "mode": "automated",
            "tests": {"a-test": {}, "b-test": {}, "c-test": {}},
            "dependencies": deps or {},
            "evaluate": expression}


class ExpressionTruthTests(unittest.TestCase):
    def test_exhaustive_six_state_pair_and_triple_crosscheck_independent_oval_reference(self):
        operations = {"all": "AND", "any": "OR", "one": "ONE", "odd": "XOR"}
        for operator, reference in operations.items():
            for size in (2, 3):
                for sample in product(sorted(SIX), repeat=size):
                    with self.subTest(operator=operator, values=sample):
                        expected = aggregate_operator(
                            reference, [s.replace("_", " ") for s in sample]
                        ).replace(" ", "_")
                        self.assertEqual(combine(operator, sample), expected)

    def test_evaluate_nested_six_state_and_source_paths(self):
        exp = {"all": [{"test": "a-test"},
                       {"any": [{"test": "b-test"},
                                {"not": {"test": "c-test"}}]}]}
        assessment = source(exp)
        before = deepcopy(assessment)
        plan = compile_expression(assessment)
        self.assertEqual(assessment, before)
        self.assertEqual(plan["requires"]["tests"], ["a-test", "b-test", "c-test"])
        self.assertEqual(plan["requires"]["dependencies"], [])
        self.assertEqual(plan["instruction_count"], 6)
        self.assertEqual(plan["instructions"][-1]["op"], "all")
        result = execute_supplied_results(
            plan, {"a-test": "true", "b-test": "false", "c-test": "false"})
        self.assertEqual(result["outcome"], "true")
        self.assertEqual(result["stage"], STAGE)
        self.assertFalse(result["scanner_executed"])
        self.assertEqual(result["trace"][2]["path"],
                         ["evaluate", "all", 1, "any", 0])
        self.assertEqual(result["trace"][-1]["path"], ["evaluate"])

    def test_logical_not_maps_only_true_false(self):
        for value in SIX:
            plan = compile_expression(source({"not": {"test": "a-test"}}))
            outcome = execute_supplied_results(plan, {"a-test": value})["outcome"]
            self.assertEqual(outcome,
                             {"true": "false", "false": "true"}.get(value, value))

    def test_not_applicable_reason_retained_as_terminal(self):
        exp = {"any": [{"not_applicable": {"reason": "not installed"}},
                       {"test": "a-test"}]}
        plan = compile_expression(source(exp))
        self.assertEqual(plan["instructions"][0]["reason"], "not installed")
        result = execute_supplied_results(plan, {"a-test": "false"})
        self.assertEqual(result["outcome"], "false")

    def test_not_applicable_only_is_not_silently_true(self):
        exp = {"all": [{"not_applicable": {"reason": "not installed"}},
                       {"not_applicable": {"reason": "excluded"}}]}
        result = execute_supplied_results(compile_expression(source(exp)), {})
        self.assertEqual(result["outcome"], "not_applicable")

    def test_assessment_truth_dependency_alias_separate_from_test(self):
        exp = {"one": [{"test": "a-test"}, {"assessment": "other"}]}
        plan = compile_expression(source(exp, deps={
            "other": {"assessment": "ng.other", "expected_version": 1,
                      "purpose": "assessment"}}))
        self.assertEqual(plan["requires"]["tests"], ["a-test"])
        self.assertEqual(plan["requires"]["dependencies"], ["other"])
        self.assertEqual(execute_supplied_results(
            plan, {"a-test": "true"}, {"other": "true"})["outcome"], "false")
        self.assertEqual(execute_supplied_results(
            plan, {"a-test": "true"}, {"other": "unknown"})["outcome"], "unknown")

    def test_repeat_test_leaf_retains_both_appearances_and_single_input(self):
        exp = {"odd": [{"test": "a-test"}, {"test": "a-test"},
                       {"test": "a-test"}]}
        plan = compile_expression(source(exp))
        self.assertEqual(len(plan["requires"]["tests"]), 1)
        report = execute_supplied_results(plan, {"a-test": "true"})
        self.assertEqual(report["outcome"], "true")
        self.assertEqual(len([x for x in report["trace"]
                              if x["operation"] == "read_test"]), 3)

    def test_applicability_explicitly_separate_not_auto_gate(self):
        a = source({"test": "a-test"})
        a["applicability"] = {"test": "b-test"}
        plan = compile_expression(a, field="applicability")
        self.assertEqual(plan["expression_field"], "applicability")
        self.assertEqual(execute_supplied_results(
            plan, {"b-test": "false"})["outcome"], "false")
        evaluate = compile_expression(a)
        self.assertEqual(evaluate["requires"]["tests"], ["a-test"])

    def test_missing_or_unexpected_result_rejected(self):
        plan = compile_expression(source({"test": "a-test"}))
        for supplied in ({}, {"a-test": "true", "b-test": "false"},
                         {"a-test": "TRUE"}, {"a-test": None},
                         {"a-test": "incomplete"}):
            with self.subTest(supplied=supplied):
                with self.assertRaises(ValueError):
                    execute_supplied_results(plan, supplied)

    def test_undeclared_test_and_dependency_fail_at_compile(self):
        with self.assertRaisesRegex(ValueError, "unresolved test"):
            compile_expression(source({"test": "no-test"}))
        with self.assertRaisesRegex(ValueError, "unresolved assessment"):
            compile_expression(source({"assessment": "missing"}))

    def test_conditional_unapproved_and_fails_closed(self):
        expression = {"if": {"test": "a-test"},
                      "then": {"test": "b-test"}, "else": {"test": "c-test"}}
        with self.assertRaisesRegex(UnsupportedExpression, "conditional"):
            compile_expression(source(expression))

    def test_malformed_tree_and_implicit_default_fail(self):
        samples = [
            {"all": []}, {"one": None}, {"all": [{"test": "a-test"}, "x"]},
            {"not_applicable": {}}, {"not_applicable": {"reason": " "}},
            {"test": "a-test", "not": {"test": "b-test"}},
            {"xor": [{"test": "a-test"}, {"test": "b-test"}]},
        ]
        for exp in samples:
            with self.subTest(exp=exp):
                with self.assertRaises((ValueError, UnsupportedExpression)):
                    compile_expression(source(exp))

    def test_reject_oversized_expression_not_silent_truncate(self):
        exp = {"all": [{"test": "a-test"}] * 10}
        with self.assertRaisesRegex(ValueError, "budget"):
            compile_expression(source(exp), max_nodes=4)

    def test_malformed_plan_stack_fails_closed(self):
        plan = compile_expression(source({"test": "a-test"}))
        bad = deepcopy(plan)
        bad["instructions"].append({"op": "all", "count": 2, "path": ["bad"]})
        bad["instruction_count"] += 1
        with self.assertRaisesRegex(ValueError, "cardinality"):
            execute_supplied_results(bad, {"a-test": "true"})


if __name__ == "__main__":
    unittest.main()
