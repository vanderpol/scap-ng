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
from audit_v04_canonical_result_plans import export_plans, verify_export


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
            if modern != legacy:
                with self.assertRaises(UnsupportedExpression):
                    compile_canonical_result_plan(authored(paired(legacy)))
            for left, right in product(sorted(SIX), repeat=2):
                supplied = {"left-test": left, "right-test": right}
                result = evaluate_supplied_results(modern_plan, supplied)
                self.assertEqual(result["outcome"], combine(legacy, (left, right)))
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

    def test_approved_conditional_propagates_unknown_without_selecting_a_branch(self):
        conditional = {"if": {"test": "left-test"},
                       "then": {"test": "right-test"},
                       "else": {"test": "third-test"}}
        plan = compile_canonical_result_plan(authored(conditional))
        observed = evaluate_supplied_results(plan, {'left-test': 'unknown'})
        self.assertEqual(observed['outcome'], 'unknown')
        self.assertEqual(len(observed['trace']), 2)
        report = census_authoring({
            "authoring/a/first.json": {"assessment": authored(paired("and"))},
            "authoring/a/second.json": {"assessment": authored(conditional)},
        })
        self.assertEqual(report["counts"]["automated_assessments"], 2)
        self.assertEqual(report["counts"]["compiled_supplied_result_plans"], 2)
        self.assertEqual(report["counts"].get("unsupported_result_expressions", 0), 0)
        self.assertTrue(report["conditional_semantics_implemented"])

    def test_serialized_source_pinned_result_plan_manifest_rejects_changes(self):
        docs = {
            "authoring/demo/assessment-a.json": {"assessment": authored(paired("and"))},
            "authoring/demo/assessment-b.json": {
                "assessment": authored({"xor": [
                    {"test": "left-test"}, {"test": "right-test"}]})},
            "authoring/demo/manual.json": {"assessment": {
                "id": "manual", "mode": "manual"}},
        }
        manifest = export_plans(docs, source_archive_sha256="a" * 64)
        self.assertEqual(manifest["compiled_plan_count"], 2)
        self.assertEqual(manifest["compiled_instruction_count"], 6)
        self.assertFalse(manifest["native_executable_bundle"])
        self.assertFalse(manifest["test_collectors_compiled"])
        self.assertTrue(verify_export(docs, manifest))
        self.assertEqual(manifest, export_plans(
            dict(reversed(list(docs.items()))), source_archive_sha256="a" * 64))
        damaged = deepcopy(manifest)
        damaged["entries"][0]["plan"]["instructions"][-1]["op"] = "or"
        with self.assertRaisesRegex(ValueError, "differs from canonical source"):
            verify_export(docs, damaged)
        damaged = deepcopy(manifest)
        damaged["entries"].pop()
        with self.assertRaisesRegex(ValueError, "differs from canonical source"):
            verify_export(docs, damaged)

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
