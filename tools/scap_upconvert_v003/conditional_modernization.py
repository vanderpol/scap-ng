#!/usr/bin/env python3
"""Fail-closed SCAP-NG 0.3.0 conditional modernization.

This pass recognizes a semantic *shape*, never Rule IDs or product names.

v1 recognizes exactly a two-branch OVAL-style Boolean encoding:

    any:
      - all: [ G, P... ]
      - all: [ not(G), Q... ]

(or the branches reversed), where exactly one complementary guard pair exists.

It rewrites that shape to the native 0.3.0 conditional expression:

    if: G
    then: P...
    else: Q...

The rewrite is intentionally opt-in. Unlike foreach v1, this modernization is
not six-state parity-preserving: native conditional semantics select one branch
for true/false and propagate non-Boolean guard outcomes without evaluating
either branch. The source OVAL AND/OR tree can mask or combine non-Boolean
outcomes differently. The report makes that semantic delta explicit.

Two-branch any/all shapes that do not contain one unambiguous complementary
guard are never rewritten and are reported for review.
"""
from __future__ import annotations

from copy import deepcopy
import json

REWRITE_ID = "conditional.complementary-guard.v1"
TARGET_VERSION = "0.3.0"
SEMANTIC_CLASS = "intent_preserving_not_six_state_parity"


def _key(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _complement(left, right):
    """Return (positive_guard, left_is_positive) for exact X / not(X)."""
    if isinstance(right, dict) and set(right) == {"not"} and right["not"] == left:
        return deepcopy(left), True
    if isinstance(left, dict) and set(left) == {"not"} and left["not"] == right:
        return deepcopy(right), False
    return None


def _all_children(branch):
    if not isinstance(branch, dict) or set(branch) != {"all"}:
        return None
    children = branch["all"]
    if not isinstance(children, list) or len(children) < 2:
        return None
    return children


def _payload(children, guard_index):
    remaining = [deepcopy(x) for i, x in enumerate(children) if i != guard_index]
    if len(remaining) == 1:
        return remaining[0]
    return {"all": remaining}


def _candidate(node):
    """Return one unambiguous complementary-guard rewrite candidate."""
    if not isinstance(node, dict) or set(node) != {"any"}:
        return None, None
    branches = node["any"]
    if not isinstance(branches, list) or len(branches) != 2:
        return None, None
    left = _all_children(branches[0])
    right = _all_children(branches[1])
    if left is None or right is None:
        return None, None

    pairs = []
    for li, lnode in enumerate(left):
        for ri, rnode in enumerate(right):
            match = _complement(lnode, rnode)
            if match is not None:
                guard, left_positive = match
                pairs.append((li, ri, guard, left_positive))

    if not pairs:
        return None, "no_exact_complementary_guard"
    if len(pairs) != 1:
        return None, "ambiguous_multiple_complementary_guards"

    li, ri, guard, left_positive = pairs[0]
    left_payload = _payload(left, li)
    right_payload = _payload(right, ri)
    then_payload = left_payload if left_positive else right_payload
    else_payload = right_payload if left_positive else left_payload
    return {
        "guard": guard,
        "then": then_payload,
        "else": else_payload,
    }, None


def _branch_like(node):
    if not isinstance(node, dict) or set(node) != {"any"}:
        return False
    branches = node["any"]
    return (
        isinstance(branches, list)
        and len(branches) == 2
        and all(_all_children(branch) is not None for branch in branches)
    )


def _rewrite_expression(node, path, report):
    candidate, rejection = _candidate(node)
    if candidate is not None:
        rewritten = {
            "if": _rewrite_expression(candidate["guard"], path + "/if", report),
            "then": _rewrite_expression(candidate["then"], path + "/then", report),
            "else": _rewrite_expression(candidate["else"], path + "/else", report),
        }
        report["applied"].append({
            "path": path,
            "source_pattern": "any(all(G,P...),all(not(G),Q...))",
            "guard": deepcopy(candidate["guard"]),
            "then": deepcopy(candidate["then"]),
            "else": deepcopy(candidate["else"]),
            "semantic_delta": {
                "true_false_guard_results": "equivalent",
                "non_boolean_guard_results": (
                    "native conditional propagates guard outcome and does not "
                    "evaluate either branch; source OVAL Boolean aggregation may differ"
                ),
            },
        })
        return rewritten

    if _branch_like(node) and rejection:
        report["review_required"].append({
            "path": path,
            "reasons": [rejection],
        })

    if not isinstance(node, dict):
        return deepcopy(node)

    keys = set(node)
    if keys in ({"all"}, {"any"}, {"one"}, {"odd"}):
        operator = next(iter(keys))
        return {
            operator: [
                _rewrite_expression(child, f"{path}/{operator}/{index}", report)
                for index, child in enumerate(node[operator])
            ]
        }
    if keys == {"not"}:
        return {"not": _rewrite_expression(node["not"], path + "/not", report)}
    if keys == {"if", "then", "else"}:
        return {
            "if": _rewrite_expression(node["if"], path + "/if", report),
            "then": _rewrite_expression(node["then"], path + "/then", report),
            "else": _rewrite_expression(node["else"], path + "/else", report),
        }
    return deepcopy(node)


def modernize_conditionals_v1(document, *, enabled=False):
    """Return (document, report) for generic complementary-guard modernization."""
    result = deepcopy(document)
    assessment = result.get("assessment", result)
    version = (assessment.get("specification") or {}).get("version")
    report = {
        "rewrite_id": REWRITE_ID,
        "target_version": TARGET_VERSION,
        "semantic_class": SEMANTIC_CLASS,
        "enabled": bool(enabled),
        "automatic_rewrite_enabled": False,
        "rewrite_performed": False,
        "pattern_based": True,
        "rule_id_allowlist": False,
        "applied": [],
        "review_required": [],
    }
    if not enabled:
        return result, report
    if version != TARGET_VERSION:
        report["review_required"].append({
            "path": "/assessment/evaluate",
            "reasons": ["conditional_v1_requires_0.3.0"],
        })
        return result, report

    expression = assessment.get("evaluate")
    if not isinstance(expression, dict):
        report["review_required"].append({
            "path": "/assessment/evaluate",
            "reasons": ["evaluate_expression_missing"],
        })
        return result, report

    assessment["evaluate"] = _rewrite_expression(
        expression, "/assessment/evaluate", report
    )
    report["rewrite_performed"] = bool(report["applied"])
    return result, report
