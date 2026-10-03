#!/usr/bin/env python3
"""Draft 0.2.0 expression evaluator with lazy Test-provider integration.

This module schedules expression leaves; collectors and State/Test evaluation
are supplied by the caller. It is not a complete scanner.
"""
from __future__ import annotations
import json
import copy
import uuid
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


class AssessmentExpressionEvaluator:
    def __init__(self, assessments, *, max_depth=200):
        self.assessments = assessments
        self.max_depth = max_depth
        for identity, assessment in assessments.items():
            if assessment.get("id") != identity:
                raise ContentError("assessment_identity", identity)
            if assessment.get("specification", {}).get("version") == "0.2.0" or any("reported_elements" in test for test in assessment.get("tests", {}).values()):
                from reported_elements import source_errors
                errors = source_errors(assessment)
                if errors:
                    raise ContentError("reported_elements", errors[0])
            for alias, dep in assessment.get("dependencies", {}).items():
                if not isinstance(dep, dict) or not isinstance(dep.get("expected_id"), str):
                    raise ContentError("dependency_shape", alias)
                target = assessments.get(dep["expected_id"])
                if target is None:
                    raise ContentError("missing_dependency", alias)
                if dep.get("expected_version") != target["version"]:
                    raise ContentError("dependency_version", alias)
            if assessment.get("mode") != "manual":
                if "evaluate" not in assessment:
                    raise ContentError("missing_evaluate", identity)
                self._validate(identity, assessment["evaluate"], 0)
            if assessment.get("applicability") is not None:
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
        elif keys in ({"all"}, {"any"}, {"one"}, {"odd"}):
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

    def run(self, entry, evaluate_test, *, target="controlled-target", bindings=None, evaluate_manual=None):
        if entry not in self.assessments:
            raise ContentError("missing_entry", entry)
        context = json.dumps({"target": target, "bindings": bindings or {}}, sort_keys=True)
        invocation_ref = "expression-" + uuid.uuid4().hex
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
                    source = evaluate_test(identity, name, copy.deepcopy({"target": target, "bindings": bindings or {}}))
                    if source is None:
                        source = "error"
                        diagnostics.append({"code": "missing_test_result", "test": f"{identity}:{name}"})
                    if not isinstance(source, str) or source not in OUTCOMES:
                        raise ContentError("invalid_test_outcome", str(source))
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
                              "assessment": dependent, "invocation_ref": invocation_ref, "outcome": result, "reused": reused})
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
            operator = next(iter(node))
            # Eager sibling evaluation isolates the conditional rule from the
            # separate open question of AND/OR short-circuit diagnostic policy.
            results = [expression(identity, child, f"{path}/{operator}/{i}")
                       for i, child in enumerate(node[operator])]
            return aggregate_operator({"all": "AND", "any": "OR", "one": "ONE", "odd": "XOR"}[operator],
                                      [r.replace("_", " ") for r in results]).replace(" ", "_")

        def invocation(identity):
            key = (identity, context)
            if key in assessment_cache:
                return assessment_cache[key]
            assessment = self.assessments[identity]
            if assessment.get("mode") == "manual":
                if evaluate_manual is None:
                    raise ContentError("missing_manual_provider", identity)
                result = evaluate_manual(identity, copy.deepcopy({"target": target, "bindings": bindings or {}}))
                if not isinstance(result, str) or result not in OUTCOMES:
                    raise ContentError("invalid_manual_outcome", str(result))
                trace.append({"path": identity, "kind": "manual", "outcome": result})
                assessment_cache[key] = result
                return result
            if assessment.get("applicability") is not None:
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
                "context": {"target": target, "invocation_ref": invocation_ref}, "evaluation_scope": "assessment_expression"}
