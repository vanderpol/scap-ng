#!/usr/bin/env python3
"""Fail-closed SCAP-NG 0.3.0 conditional modernization.

This pass recognizes a semantic *shape*, never Rule IDs or product names.

v1 recognizes two generic two-branch OVAL-style Boolean encodings:

1. Exact complementary guard:

       any:
         - all: [ G, P... ]
         - all: [ not(G), Q... ]

2. Proven mutually-exclusive enum guards over the same typed Object/field:

       any:
         - all: [ A, P... ]
         - all: [ B, Q... ]

   where A and B have the same Test semantics except for disjoint literal
   equality State value sets.

The first becomes `if G then P else Q`. The second becomes
`if A then P else all(B,Q...)`; retaining B in the else branch avoids assuming
the two value sets are exhaustive.

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

REWRITE_ID = "conditional.branch-modernization.v1"
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


def _single_literal_equality_state(state):
    """Return a comparable single-predicate equality signature, or None."""
    if not isinstance(state, dict):
        return None
    payload = state.get("state")
    if not isinstance(payload, dict):
        return None

    found = []

    def walk(value, path=()):
        if isinstance(value, dict):
            if "value" in value and "operation" in value:
                found.append((path, value))
            for key, child in value.items():
                walk(child, path + (key,))
        elif isinstance(value, list):
            for index, child in enumerate(value):
                walk(child, path + (index,))

    walk(payload)
    if len(found) != 1:
        return None
    path, predicate = found[0]
    if predicate.get("operation") not in {"equal", "equals"}:
        return None
    literal = predicate.get("value")
    if not isinstance(literal, (str, int, float, bool)):
        return None

    shape = deepcopy(state)
    shape.pop("state_title", None)
    cursor = shape["state"]
    for part in path:
        cursor = cursor[part]
    cursor["value"] = "<LITERAL>"
    return {
        "path": path,
        "value": literal,
        "shape": shape,
    }


def _enum_guard_signature(assessment, expression):
    """Return a proof signature for a Test selecting disjoint enum values."""
    if not isinstance(expression, dict) or set(expression) != {"test"}:
        return None
    tests = assessment.get("tests") or {}
    states = assessment.get("states") or {}
    test_id = expression.get("test")
    test = tests.get(test_id)
    if not isinstance(test, dict):
        return None

    # Require a nonempty collected population and all-item evaluation so two
    # disjoint value sets over the same population cannot both pass.
    existence = test.get("existence", test.get("check_existence"))
    check = test.get("match", test.get("check"))
    if existence not in {"some", "at_least_one_exists", "only_one_exists"}:
        return None
    if check != "all" or test.get("states_match") != "any":
        return None

    state_ids = test.get("states")
    if not isinstance(state_ids, list) or not state_ids:
        return None

    signatures = []
    for state_id in state_ids:
        if not isinstance(state_id, str) or state_id not in states:
            return None
        signature = _single_literal_equality_state(states[state_id])
        if signature is None:
            return None
        signatures.append(signature)

    first = signatures[0]
    shape_key = _key(first["shape"])
    if any(
        signature["path"] != first["path"]
        or _key(signature["shape"]) != shape_key
        for signature in signatures[1:]
    ):
        return None

    base = {
        key: deepcopy(value)
        for key, value in test.items()
        if key not in {"test_title", "states", "states_match", "reported_elements"}
    }
    return {
        "test": test_id,
        "base": base,
        "predicate_path": first["path"],
        "state_shape": first["shape"],
        "values": {signature["value"] for signature in signatures},
    }


def _mutually_exclusive_enum_pair(assessment, left, right):
    left_sig = _enum_guard_signature(assessment, left)
    right_sig = _enum_guard_signature(assessment, right)
    if left_sig is None or right_sig is None:
        return None
    if left_sig["base"] != right_sig["base"]:
        return None
    if left_sig["predicate_path"] != right_sig["predicate_path"]:
        return None
    if _key(left_sig["state_shape"]) != _key(right_sig["state_shape"]):
        return None
    if not left_sig["values"].isdisjoint(right_sig["values"]):
        return None
    return {
        "left": left_sig,
        "right": right_sig,
    }


def _candidate(node, assessment):
    """Return one unambiguous generic conditional rewrite candidate."""
    if not isinstance(node, dict) or set(node) != {"any"}:
        return None, None
    branches = node["any"]
    if not isinstance(branches, list) or len(branches) != 2:
        return None, None
    left = _all_children(branches[0])
    right = _all_children(branches[1])
    if left is None or right is None:
        return None, None

    complement_pairs = []
    for li, lnode in enumerate(left):
        for ri, rnode in enumerate(right):
            match = _complement(lnode, rnode)
            if match is not None:
                guard, left_positive = match
                complement_pairs.append((li, ri, guard, left_positive))

    if len(complement_pairs) == 1:
        li, ri, guard, left_positive = complement_pairs[0]
        left_payload = _payload(left, li)
        right_payload = _payload(right, ri)
        return {
            "pattern_class": "exact_complementary_guard",
            "guard": guard,
            "then": left_payload if left_positive else right_payload,
            "else": right_payload if left_positive else left_payload,
            "source_guard_pair": [deepcopy(left[li]), deepcopy(right[ri])],
            "else_retains_guard": False,
        }, None
    if len(complement_pairs) > 1:
        return None, "ambiguous_multiple_complementary_guards"

    exclusive_pairs = []
    for li, lnode in enumerate(left):
        for ri, rnode in enumerate(right):
            proof = _mutually_exclusive_enum_pair(assessment, lnode, rnode)
            if proof is not None:
                exclusive_pairs.append((li, ri, proof))

    if len(exclusive_pairs) == 1:
        li, ri, proof = exclusive_pairs[0]
        left_payload = _payload(left, li)
        right_payload = _payload(right, ri)
        # Do not assume the disjoint enum sets are exhaustive. Keep the second
        # guard inside else so values outside both sets retain a false branch.
        right_guarded_payload = {
            "all": [deepcopy(right[ri]), right_payload]
        }
        return {
            "pattern_class": "mutually_exclusive_enum_guards",
            "guard": deepcopy(left[li]),
            "then": left_payload,
            "else": right_guarded_payload,
            "source_guard_pair": [deepcopy(left[li]), deepcopy(right[ri])],
            "enum_proof": {
                "object": proof["left"]["base"].get("object"),
                "predicate_path": list(proof["left"]["predicate_path"]),
                "left_values": sorted(proof["left"]["values"], key=str),
                "right_values": sorted(proof["right"]["values"], key=str),
                "disjoint": True,
                "exhaustive": False,
            },
            "else_retains_guard": True,
        }, None
    if len(exclusive_pairs) > 1:
        return None, "ambiguous_multiple_mutually_exclusive_guard_pairs"

    return None, "no_proven_conditional_guard_pattern"


def _branch_like(node):
    if not isinstance(node, dict) or set(node) != {"any"}:
        return False
    branches = node["any"]
    return (
        isinstance(branches, list)
        and len(branches) == 2
        and all(_all_children(branch) is not None for branch in branches)
    )


def _rewrite_expression(node, path, report, assessment):
    candidate, rejection = _candidate(node, assessment)
    if candidate is not None:
        rewritten = {
            "if": _rewrite_expression(candidate["guard"], path + "/if", report, assessment),
            "then": _rewrite_expression(candidate["then"], path + "/then", report, assessment),
            "else": _rewrite_expression(candidate["else"], path + "/else", report, assessment),
        }
        report["applied"].append({
            "path": path,
            "source_pattern": candidate["pattern_class"],
            "pattern_class": candidate["pattern_class"],
            "guard": deepcopy(candidate["guard"]),
            "source_guard_pair": deepcopy(candidate.get("source_guard_pair")),
            "then": deepcopy(candidate["then"]),
            "else": deepcopy(candidate["else"]),
            "else_retains_guard": bool(candidate.get("else_retains_guard")),
            **({"enum_proof": deepcopy(candidate["enum_proof"])}
               if candidate.get("enum_proof") else {}),
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
                _rewrite_expression(child, f"{path}/{operator}/{index}", report, assessment)
                for index, child in enumerate(node[operator])
            ]
        }
    if keys == {"not"}:
        return {"not": _rewrite_expression(node["not"], path + "/not", report, assessment)}
    if keys == {"if", "then", "else"}:
        return {
            "if": _rewrite_expression(node["if"], path + "/if", report, assessment),
            "then": _rewrite_expression(node["then"], path + "/then", report, assessment),
            "else": _rewrite_expression(node["else"], path + "/else", report, assessment),
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
        expression, "/assessment/evaluate", report, assessment
    )
    report["rewrite_performed"] = bool(report["applied"])
    return result, report
