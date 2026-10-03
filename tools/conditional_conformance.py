#!/usr/bin/env python3
"""Experimental conditional semantics over controlled Test results, not a scanner.

This model does not collect resources, compare States or implement 0.2.0.
The proposed guard table and the limitations live with its fixture suite.
"""
from __future__ import annotations

import argparse
import copy
import itertools
import json
from pathlib import Path

import yaml

from oval_result_truth_tables import aggregate_operator

from assessment_expression import (
    AssessmentExpressionEvaluator, ContentError, OUTCOMES, load_assessments,
)


class ConditionalModel(AssessmentExpressionEvaluator):
    """Compatibility fixture adapter over the maintained expression evaluator."""
    def run(self, entry, test_results, **kwargs):
        try:
            result = super().run(entry, lambda identity, name, context:
                                 test_results.get(f"{identity}:{name}"), **kwargs)
        except ContentError as exc:
            if exc.code == "invalid_test_outcome":
                raise ContentError("invalid_fixture_outcome", str(exc)) from exc
            raise
        context = {"target": kwargs.get("target", "controlled-target"), "bindings": kwargs.get("bindings") or {}}
        result["context"] = context
        for node in result["trace"]:
            if node["kind"] == "dependency":
                node["context"] = json.dumps(context, sort_keys=True)
        result.pop("evaluation_scope")
        result["model_only"] = True
        return result


def run_suite(suite_dir):
    assessments = load_assessments(suite_dir / "content")
    model = ConditionalModel(assessments)
    cases = yaml.safe_load((suite_dir / "cases.yaml").read_text())["cases"]
    results = []
    for case in cases:
        actual = model.run(case["assessment"], case["test_results"])
        checks = {"outcome": actual["outcome"] == case["expected_outcome"]}
        if "expected_executed_tests" in case:
            checks["execution"] = actual["executed_tests"] == case["expected_executed_tests"]
        if "expected_branches" in case:
            checks["branch_selection"] = [n["selected_branch"] for n in actual["trace"]
                                            if n["kind"] == "conditional"] == case["expected_branches"]
        results.append({"id": case["id"], "passed": all(checks.values()), "checks": checks, "actual": actual})
    oracle = json.loads((suite_dir / "guard-table.json").read_text())
    # The expected table is checked-in review data; the model does not read it.
    for entry, guard_id in (("conditional.local", "conditional.local:test-guard"),
                            ("conditional.dependent", "conditional.role:test-role")):
        for guard, then, otherwise in itertools.product(OUTCOMES, repeat=3):
            supplied = {guard_id: guard, f"{entry}:test-then": then, f"{entry}:test-else": otherwise}
            expected = oracle[guard]
            expected_outcome = {"then": then, "else": otherwise}.get(expected["selected_branch"], expected["outcome"])
            actual = model.run(entry, supplied)
            branches = [n["selected_branch"] for n in actual["trace"] if n["kind"] == "conditional"]
            required = [guard_id] + ([f"{entry}:test-{expected['selected_branch']}"] if expected["selected_branch"] else [])
            results.append({"id": f"matrix:{entry}:{guard}:{then}:{otherwise}",
                            "passed": actual["outcome"] == expected_outcome
                            and branches == [expected["selected_branch"]] and actual["executed_tests"] == required})
    invalid_results = []
    invalid_cases = yaml.safe_load((suite_dir / "invalid-cases.yaml").read_text())["cases"]
    for case in invalid_cases:
        changed = copy.deepcopy(assessments)
        parent = changed
        for segment in case["path"][:-1]:
            parent = parent[segment]
        if case.get("operation") == "delete":
            del parent[case["path"][-1]]
        else:
            parent[case["path"][-1]] = case["value"]
        try:
            ConditionalModel(changed)
            error = None
        except ContentError as exc:
            error = exc.code
        invalid_results.append({"id": case["id"], "passed": error == case["expected_error"], "actual_error": error})
    failures = [r for r in results + invalid_results if not r["passed"]]
    return {"status": "experimental_model_passed" if not failures else "failed",
            "curated_cases": len(cases), "matrix_cases": 432, "cases_checked": len(results),
            "invalid_cases": len(invalid_cases), "failed": failures,
            "invalid_results": invalid_results, "curated_results": results[:len(cases)],
            "limits": ["Controlled Test outcomes, no target collection or State evaluator",
                       "Proposed non-Boolean guard propagation, not Board-ratified",
                       "No SCAP 1.4 equivalence, 0.2.0 implementation or general normalizer proof"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--suite", type=Path, default=Path(__file__).resolve().parents[1] / "tests/conditional-0.2.0")
    ap.add_argument("--report", type=Path)
    args = ap.parse_args()
    report = run_suite(args.suite)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "curated_results"}, indent=2))
    return 0 if report["status"] == "experimental_model_passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
