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

OUTCOMES = ("true", "false", "error", "unknown", "not_evaluated", "not_applicable")


class ContentError(ValueError):
    def __init__(self, code, detail):
        super().__init__(f"{code}: {detail}")
        self.code = code


def load_assessments(directory):
    sources = {}
    paths = {}
    for path in sorted(directory.glob("*.assessment.yaml")):
        assessment = yaml.safe_load(path.read_text())["assessment"]
        identity = assessment["id"]
        if identity in sources:
            raise ContentError("duplicate_assessment", identity)
        sources[identity] = assessment
        paths[path.resolve()] = identity
    for path in sorted(directory.glob("*.assessment.yaml")):
        assessment = sources[paths[path.resolve()]]
        for alias, dep in assessment.get("dependencies", {}).items():
            resolved = (path.parent / dep["assessment"]).resolve()
            if resolved not in paths:
                raise ContentError("missing_dependency", alias)
            if dep.get("expected_id") != paths[resolved]:
                raise ContentError("dependency_identity", alias)
            if dep.get("expected_version") != sources[paths[resolved]]["version"]:
                raise ContentError("dependency_version", alias)
    return sources


class ConditionalModel:
    def __init__(self, assessments, *, max_depth=200):
        self.assessments = assessments
        self.max_depth = max_depth
        for identity, assessment in assessments.items():
            if assessment.get("id") != identity:
                raise ContentError("assessment_identity", identity)
            for alias, dep in assessment.get("dependencies", {}).items():
                if not isinstance(dep, dict) or not isinstance(dep.get("expected_id"), str):
                    raise ContentError("dependency_shape", alias)
                target = assessments.get(dep["expected_id"])
                if target is None:
                    raise ContentError("missing_dependency", alias)
                if dep.get("expected_version") != target["version"]:
                    raise ContentError("dependency_version", alias)
            self._validate(identity, assessment["evaluate"], 0)
            if "applicability" in assessment:
                self._validate(identity, assessment["applicability"], 0)
        self._check_cycles()

    def _validate(self, identity, node, depth):
        if depth > self.max_depth:
            raise ContentError("resource_limit", "expression depth budget exceeded")
        if not isinstance(node, dict):
            raise ContentError("expression_shape", str(node))
        keys = set(node)
        assessment = self.assessments[identity]
        if keys == {"test"}:
            if not isinstance(node["test"], str) or node["test"] not in assessment.get("tests", {}):
                raise ContentError("missing_test", str(node["test"]))
        elif keys == {"assessment"}:
            if not isinstance(node["assessment"], str) or node["assessment"] not in assessment.get("dependencies", {}):
                raise ContentError("undeclared_dependency", str(node["assessment"]))
        elif keys == {"not_applicable"}:
            terminal = node["not_applicable"]
            if (not isinstance(terminal, dict) or set(terminal) != {"reason"}
                    or not isinstance(terminal["reason"], str) or not terminal["reason"].strip()):
                raise ContentError("not_applicable_reason", "explicit nonempty authored reason required")
        elif keys == {"if", "then", "else"}:
            for key in ("if", "then", "else"):
                self._validate(identity, node[key], depth + 1)
        elif keys == {"not"}:
            self._validate(identity, node["not"], depth + 1)
        elif keys in ({"all"}, {"any"}):
            children = node[next(iter(keys))]
            if not isinstance(children, list) or not children:
                raise ContentError("empty_expression", str(keys))
            for child in children:
                self._validate(identity, child, depth + 1)
        else:
            raise ContentError("expression_shape", str(sorted(keys)))

    def _check_cycles(self):
        active, finished = set(), set()

        def visit(identity, depth):
            if identity in active:
                raise ContentError("dependency_cycle", identity)
            if identity in finished:
                return
            if depth > self.max_depth:
                raise ContentError("resource_limit", "dependency depth budget exceeded")
            active.add(identity)
            # All declared dependencies, including unused and unselected ones.
            for dep in self.assessments[identity].get("dependencies", {}).values():
                visit(dep["expected_id"], depth + 1)
            active.remove(identity)
            finished.add(identity)

        for identity in self.assessments:
            visit(identity, 0)

    def run(self, entry, test_results, *, target="controlled-target", bindings=None):
        if entry not in self.assessments:
            raise ContentError("missing_entry", entry)
        context = json.dumps({"target": target, "bindings": bindings or {}}, sort_keys=True)
        test_cache, assessment_cache, trace, executed, diagnostics = {}, {}, [], [], []

        def skip(path, reason):
            trace.append({"path": path, "kind": "expression", "outcome": "not_evaluated", "reason": reason})

        def expression(identity, node, path):
            if "not_applicable" in node:
                trace.append({"path": path, "kind": "terminal", "outcome": "not_applicable",
                              "reason": node["not_applicable"]["reason"]})
                return "not_applicable"
            if "test" in node:
                name = node["test"]
                key = (identity, name, context)
                reused = key in test_cache
                if not reused:
                    source = test_results.get(f"{identity}:{name}")
                    if source is None:
                        source = "error"
                        diagnostics.append({"code": "missing_test_result", "test": f"{identity}:{name}"})
                    if not isinstance(source, str) or source not in OUTCOMES:
                        raise ContentError("invalid_fixture_outcome", str(source))
                    test_cache[key] = source
                    executed.append(f"{identity}:{name}")
                result = test_cache[key]
                trace.append({"path": path, "kind": "test", "test": name, "assessment": identity,
                              "outcome": result, "reused": reused})
                return result
            if "assessment" in node:
                alias = node["assessment"]
                dep = self.assessments[identity]["dependencies"][alias]
                dependent = dep["expected_id"]
                reused = (dependent, context) in assessment_cache
                result = invocation(dependent)
                trace.append({"path": path, "kind": "dependency", "alias": alias,
                              "assessment": dependent, "context": context, "outcome": result, "reused": reused})
                return result
            if "if" in node:
                guard = expression(identity, node["if"], path + "/if")
                selected = None
                if guard in ("true", "false"):
                    selected = "then" if guard == "true" else "else"
                    result = expression(identity, node[selected], path + "/" + selected)
                    skip(path + "/" + ("else" if selected == "then" else "then"), "conditional_branch_not_selected")
                else:
                    result = guard
                    skip(path + "/then", "condition_unresolved")
                    skip(path + "/else", "condition_unresolved")
                trace.append({"path": path, "kind": "conditional", "condition_outcome": guard,
                              "selected_branch": selected, "outcome": result})
                return result
            if "not" in node:
                result = expression(identity, node["not"], path + "/not")
                return {"true": "false", "false": "true"}.get(result, result)
            operator = "all" if "all" in node else "any"
            # Eager sibling evaluation isolates the conditional rule from the
            # separate open question of AND/OR short-circuit diagnostic policy.
            results = [expression(identity, child, f"{path}/{operator}/{i}")
                       for i, child in enumerate(node[operator])]
            return aggregate_operator("AND" if operator == "all" else "OR",
                                      [r.replace("_", " ") for r in results]).replace(" ", "_")

        def invocation(identity):
            key = (identity, context)
            if key in assessment_cache:
                return assessment_cache[key]
            assessment = self.assessments[identity]
            if "applicability" in assessment:
                outcome = expression(identity, assessment["applicability"], identity + "/applicability")
                if outcome != "true":
                    result = "not_applicable" if outcome == "false" else outcome
                    skip(identity + "/evaluate", "intrinsic_applicability_not_true")
                    assessment_cache[key] = result
                    return result
            result = expression(identity, assessment["evaluate"], identity + "/evaluate")
            assessment_cache[key] = result
            return result

        outcome = invocation(entry)
        return {"outcome": outcome, "executed_tests": executed, "trace": trace, "diagnostics": diagnostics,
                "context": json.loads(context), "model_only": True}


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
