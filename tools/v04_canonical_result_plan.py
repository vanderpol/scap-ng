#!/usr/bin/env python3
"""Canonical 0.4.0 six-state expression plan, with supplied Test outcomes only.

Compiles the native 0.4.0 Boolean syntax (and/or/one/xor/not and legacy
aliases) to the independently audited six-state OVAL result combiner.
No Test/State/Item/Variable collection, IF/ELSE branching, host execution,
runtime applicability decisions, or scanner parity is claimed.

This is the first bounded logical-result backend, NOT an executable scanner.
Refs #232 #229.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from collections import Counter

from v04_a_authoring_graph_index import canonical_json
from v04_a_truth_plan import (
    compile_expression, execute_supplied_results, UnsupportedExpression,
)

STAGE = "CANONICAL_040_SUPPLIED_TEST_RESULTS_ONLY_NOT_SCANNER"
SPEC = {"id": "scap-ng.pre-alpha.assessment", "version": "0.4.0"}
OP_ALIASES = {"and": "all", "or": "any", "xor": "odd"}
OPERATORS = frozenset(("and", "or", "one", "xor", "all", "any", "odd"))
MAX_NODES = 16384


def _legacy_result_tree(source, *, max_nodes=MAX_NODES):
    """Rewrite only equivalent operator names, preserving all other source."""
    count = 0

    def visit(node, depth):
        nonlocal count
        count += 1
        if count > max_nodes or depth > 256:
            raise ValueError("canonical expression resource budget exceeded")
        if not isinstance(node, dict):
            raise ValueError("canonical expression node must be an object")
        if set(node) == {"if", "then", "else"}:
            raise UnsupportedExpression(
                "conditional result semantics require separate six-state acceptance")
        if len(node) != 1:
            raise ValueError("expression must have exactly one operator")
        kind, payload = next(iter(node.items()))
        if kind in OPERATORS:
            if not isinstance(payload, list) or not payload:
                raise ValueError(f"operator {kind} requires nonempty children")
            return {OP_ALIASES.get(kind, kind):
                    [visit(child, depth + 1) for child in payload]}
        if kind == "not":
            return {"not": visit(payload, depth + 1)}
        if kind in ("test", "assessment", "not_applicable"):
            return {kind: deepcopy(payload)}
        raise UnsupportedExpression(f"unsupported 0.4.0 result operator: {kind}")

    return visit(source, 0)


def compile_canonical_result_plan(assessment, field="evaluate"):
    if not isinstance(assessment, dict) or assessment.get("specification") != SPEC:
        raise ValueError("0.4.0 Assessment specification required")
    if assessment.get("mode") != "automated":
        raise ValueError("automated 0.4.0 Assessment required")
    if field not in ("evaluate", "applicability") or field not in assessment:
        raise ValueError("explicit 0.4.0 evaluate/applicability required")
    normalized = deepcopy(assessment)
    normalized[field] = _legacy_result_tree(assessment[field])
    original_plan = compile_expression(normalized, field)
    return {
        "stage": STAGE,
        "assessment_id": assessment["id"],
        "field": field,
        "source_sha256": sha256(canonical_json(assessment[field])).hexdigest(),
        "normalized_source_sha256": sha256(canonical_json(normalized[field])).hexdigest(),
        "instructions": original_plan["instructions"],
        "instruction_count": original_plan["instruction_count"],
        "requires": original_plan["requires"],
        "scanner_executed": False,
        "tests_evaluated": False,
        "conditional_semantics_implemented": False,
    }


def evaluate_supplied_results(plan, test_results, dependency_results=None):
    """Full OVAL six-state Boolean composition; no hidden Test defaults."""
    if not isinstance(plan, dict) or plan.get("stage") != STAGE:
        raise ValueError("unsupported native 0.4 result plan")
    # Delegate six-state truth algebra to audited OVAL-aligned operator core.
    legacy = {
        "stage": "RESEARCH_SUPPLIED_RESULTS_ONLY_NOT_SCANNER",
        "assessment_id": plan["assessment_id"],
        "expression_field": plan["field"],
        "instructions": plan["instructions"],
        "instruction_count": plan["instruction_count"],
        "requires": plan["requires"],
    }
    result = execute_supplied_results(legacy, test_results, dependency_results)
    return {
        **result,
        "stage": STAGE,
        "scanner_executed": False,
        "tests_evaluated": False,
        "outcomes_provided_by_caller": True,
    }


def census_authoring(documents):
    """Report exact result-plan eligibility; unsupported cases stay visible."""
    counts = Counter()
    examples = {}
    plans = []
    for path, doc in sorted(documents.items()):
        assessment = doc.get("assessment")
        if not isinstance(assessment, dict) or assessment.get("mode") != "automated":
            continue
        counts["automated_assessments"] += 1
        try:
            plan = compile_canonical_result_plan(assessment)
        except UnsupportedExpression as error:
            counts["unsupported_result_expressions"] += 1
            if len(examples) < 12:
                examples[path] = str(error)
        else:
            counts["compiled_supplied_result_plans"] += 1
            counts["compiled_result_instructions"] += plan["instruction_count"]
            plans.append({
                "path": path,
                "assessment_id": plan["assessment_id"],
                "source_sha256": plan["source_sha256"],
                "instruction_count": plan["instruction_count"],
                "required_tests": len(plan["requires"]["tests"]),
                "required_dependencies": len(plan["requires"]["dependencies"]),
            })
    return {
        "stage": STAGE,
        "counts": dict(sorted(counts.items())),
        "unsupported_examples": examples,
        "plan_manifest_sha256": sha256(canonical_json(plans)).hexdigest(),
        "scanner_executed": False,
        "tests_evaluated": False,
        "conditional_semantics_implemented": False,
    }
