#!/usr/bin/env python3
"""#232/#229: bounded 0.4-A six-state expression *result* executor.

Accepts already-evaluated Test/dependency outcomes only. No collectors,
Test/State/Variable evaluation, conditional semantics, scanner integration,
signed bundle, short-circuit assumptions or authoring/schema changes.

The typed postorder plan is deterministic, tracks exact source paths, and
applies independently audited OVAL 5.12.3 Boolean result-combiner behavior.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256

from v04_a_authoring_graph_index import canonical_json

STAGE = "RESEARCH_SUPPLIED_RESULTS_ONLY_NOT_SCANNER"
SIX = frozenset(("true", "false", "error", "unknown",
                 "not_evaluated", "not_applicable"))
OPS = frozenset(("all", "any", "one", "odd"))


class UnsupportedExpression(ValueError):
    """Unsettled language meaning; never invent a result default."""


def compile_expression(assessment, field="evaluate", *, max_nodes=16384):
    """Validate a source tree and compile stack operations in postorder.

    'applicability' may be compiled separately but has no implicit control
    effect on 'evaluate' here. Dependency aliases refer to assessment-level
    truth, *never* collection objects/Variables. 'if' is deliberately blocked.
    """
    if not isinstance(assessment, dict) or assessment.get("mode") != "automated":
        raise ValueError("automated Assessment required")
    if field not in ("evaluate", "applicability") or assessment.get(field) is None:
        raise ValueError("missing explicit evaluate/applicability expression")
    tests = assessment.get("tests")
    deps = assessment.get("dependencies", {})
    if not isinstance(tests, dict) or not isinstance(deps, dict):
        raise ValueError("invalid Test or Assessment dependency table")
    tree = assessment[field]
    plan = []
    pending = [(tree, [field], False)]
    while pending:
        value, path, exit_node = pending.pop()
        if not isinstance(value, dict):
            raise ValueError(f"{path}: expression node must be an object")
        if len(value) != 1:
            if set(value) == {"if", "then", "else"}:
                raise UnsupportedExpression(f"{path}: conditional six-state meaning unapproved")
            raise ValueError(f"{path}: expression must have one operator")
        kind, payload = next(iter(value.items()))
        if kind in ("if", "then", "else"):
            raise UnsupportedExpression(f"{path}: conditional six-state meaning unapproved")
        if exit_node:
            if kind in OPS:
                plan.append({"op": kind, "count": len(payload), "path": path})
            elif kind == "not":
                plan.append({"op": "not", "path": path})
            else:
                raise AssertionError("unexpected exiting expression")
            continue
        if kind in ("test", "assessment"):
            if not isinstance(payload, str) or not payload:
                raise ValueError(f"{path}: missing reference identity")
            references = tests if kind == "test" else deps
            if payload not in references:
                raise ValueError(f"{path}: unresolved {kind} reference {payload!r}")
            plan.append({"op": "read_" + kind, "id": payload, "path": path})
        elif kind == "not_applicable":
            if (not isinstance(payload, dict) or set(payload) != {"reason"}
                    or not isinstance(payload["reason"], str)
                    or not payload["reason"].strip()):
                raise ValueError(f"{path}: explicit not_applicable reason required")
            plan.append({"op": "not_applicable", "reason": payload["reason"],
                         "path": path})
        elif kind == "not":
            pending.append((value, path, True))
            pending.append((payload, path + ["not"], False))
        elif kind in OPS:
            if not isinstance(payload, list) or not payload:
                raise ValueError(f"{path}: operator {kind} requires nonempty children")
            pending.append((value, path, True))
            for i in reversed(range(len(payload))):
                pending.append((payload[i], path + [kind, i], False))
        else:
            raise UnsupportedExpression(f"{path}: unapproved expression operator {kind!r}")
        if len(plan) + len(pending) > max_nodes:
            raise ValueError("expression node budget exceeded")
    return {
        "stage": STAGE,
        "assessment_id": assessment["id"],
        "expression_field": field,
        "expression_sha256": sha256(canonical_json(tree)).hexdigest(),
        "instructions": plan,
        "instruction_count": len(plan),
        "requires": {
            "tests": sorted({i["id"] for i in plan if i["op"] == "read_test"}),
            "dependencies": sorted({i["id"] for i in plan if i["op"] == "read_assessment"}),
        },
    }


def combine(operator, values):
    """Independent six-state result combiner, validated against pinned OVAL oracle.

    This is NOT an Item-existence, State/record, incomplete-collection or
    conditional evaluator. 'not applicable' values do not become true/false.
    """
    values = list(values)
    if operator not in OPS or not values or any(v not in SIX for v in values):
        raise ValueError("unsupported six-state operator or outcome")
    c = Counter(values)
    t, f, e, u, ne, na = (c[x] for x in
                            ("true", "false", "error", "unknown",
                             "not_evaluated", "not_applicable"))
    if operator == "all":
        if f: return "false"
        if e: return "error"
        if u: return "unknown"
        if ne: return "not_evaluated"
        return "true" if t else "not_applicable"
    if operator == "any":
        if t: return "true"
        if e: return "error"
        if u: return "unknown"
        if ne: return "not_evaluated"
        return "false" if f else "not_applicable"
    if operator == "one":
        if t >= 2: return "false"
        if e: return "error"
        if u: return "unknown"
        if ne: return "not_evaluated"
        if t == 1: return "true"
        return "false" if f else "not_applicable"
    if operator == "odd":
        if e: return "error"
        if u: return "unknown"
        if ne: return "not_evaluated"
        if t or f:
            return "true" if t % 2 else "false"
        return "not_applicable"
    raise AssertionError("unsupported operator")


def execute_supplied_results(plan, test_results, dependency_results=None):
    """Evaluate compiled expression from explicitly supplied six-state leaves.

    All structural sibling leaves are consumed (no short-circuit policy).
    Missing, extra, malformed and incorrectly scoped outcomes are errors,
    not implicit unknown/false/success. No runtime completeness inference.
    """
    if (not isinstance(plan, dict) or plan.get("stage") != STAGE
            or not isinstance(test_results, dict)
            or not isinstance(dependency_results, (dict, type(None)))):
        raise ValueError("invalid supplied-results plan or mappings")
    deps = dependency_results or {}
    if (set(test_results) != set(plan["requires"]["tests"]) or
            set(deps) != set(plan["requires"]["dependencies"])):
        raise ValueError("Test/Assessment supplied result keys do not match declared leaves")
    if any(type(v) is not str or v not in SIX
           for v in list(test_results.values()) + list(deps.values())):
        raise ValueError("invalid six-state supplied leaf outcome")
    stack, trace = [], []
    for inst in plan["instructions"]:
        kind, path = inst["op"], inst["path"]
        if kind == "read_test":
            value = test_results[inst["id"]]
        elif kind == "read_assessment":
            value = deps[inst["id"]]
        elif kind == "not_applicable":
            value = "not_applicable"
        elif kind == "not":
            if not stack: raise ValueError("malformed unary expression stack")
            before = stack.pop()
            value = {"true": "false", "false": "true"}.get(before, before)
        elif kind in OPS:
            count = inst["count"]
            if type(count) is not int or count < 1 or count > len(stack):
                raise ValueError("malformed operator stack cardinality")
            values = stack[-count:]
            del stack[-count:]
            value = combine(kind, values)
        else:
            raise ValueError(f"unsupported expression plan opcode {kind!r}")
        stack.append(value)
        trace.append({"path": path, "operation": kind, "outcome": value})
    if len(stack) != 1 or len(trace) != plan["instruction_count"]:
        raise ValueError("malformed expression stack / instruction tally")
    return {"stage": STAGE, "assessment_id": plan["assessment_id"],
            "expression_field": plan["expression_field"],
            "outcome": stack[0], "trace": trace,
            "tests_supplied": len(test_results),
            "dependencies_supplied": len(deps),
            "scanner_executed": False, "collections_evaluated": False}
