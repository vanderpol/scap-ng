#!/usr/bin/env python3
"""Research-only semantic probe for OVAL violation-query modernization.

Models the recurring source idiom:

    collect candidate Items
      -> exclude Items whose requirement State is TRUE
      -> Test check_existence="none_exist"

and compares it with the intuitive positive authoring statement:

    all target Items satisfy the requirement State

The positive form here is deliberately a semantic probe, not an accepted
SCAP-NG Test rule. A lossless authoring shorthand would have to desugar to the
faithful violation-query graph rather than silently inherit different State
propagation.
"""
from __future__ import annotations

from oval_result_truth_tables import (
    TRUE,
    FALSE,
    ERROR,
    UNKNOWN,
    NOT_EVALUATED,
    NOT_APPLICABLE,
    apply_filter_state_result,
    aggregate_check,
    evaluate_collected_object_test,
)

REWRITE_ID = "violation-query.positive-all.v1"


def faithful_violation_query(collection_flag, requirement_results):
    """Evaluate exclude-good + none_exist for already-target-scoped Items."""
    results = list(requirement_results)
    violations = 0
    for state_result in results:
        selected = apply_filter_state_result("exclude", state_result)
        if selected == ERROR:
            # A non-Boolean Filter State result is a collection/evaluation
            # failure in the current SCAP-NG OVAL processing model.
            return ERROR
        if selected:
            violations += 1

    return evaluate_collected_object_test(
        collection_flag,
        existence="none_exist",
        check="all",
        has_state=False,
        exists=violations,
    )


def positive_all_intent(collection_flag, requirement_results):
    """Natural universal-quantification semantics for comparison only.

    This intentionally treats an empty complete target population as vacuously
    true, matching the source violation-query intent. It preserves ordinary
    State result distinctions rather than converting all non-Booleans to error.
    """
    values = list(requirement_results)

    if collection_flag == "error":
        return ERROR
    if collection_flag == "not collected":
        return UNKNOWN
    if collection_flag == "not applicable":
        return NOT_APPLICABLE
    if collection_flag == "does not exist":
        return TRUE
    if collection_flag not in {"complete", "incomplete"}:
        raise ValueError(f"unsupported collection flag: {collection_flag}")

    if not values:
        return TRUE if collection_flag == "complete" else UNKNOWN

    combined = aggregate_check("all", values)
    if collection_flag == "complete":
        return combined

    # Additional Items may still arrive. A FALSE is decisive for universal
    # quantification; otherwise incomplete collection remains UNKNOWN.
    if combined == FALSE:
        return FALSE
    return UNKNOWN


def compare_violation_query(collection_flag, requirement_results):
    faithful = faithful_violation_query(collection_flag, requirement_results)
    candidate = positive_all_intent(collection_flag, requirement_results)
    return {
        "rewrite_id": REWRITE_ID,
        "faithful": faithful,
        "candidate": candidate,
        "equivalent": faithful == candidate,
        "collection_flag": collection_flag,
        "requirement_results": list(requirement_results),
    }


def positive_authoring_rewrite_preconditions(candidate):
    """Fail closed for automatic conversion to independent positive semantics."""
    reasons = []
    if candidate.get("source_shape") != "exclude_matching_state_then_none_exist":
        reasons.append("source_shape_not_supported")
    if candidate.get("filter_action") != "exclude":
        reasons.append("requirement_filter_is_not_exclude")
    if candidate.get("existence") != "none_exist":
        reasons.append("source_test_is_not_none_exist")

    # Even an otherwise perfect structural match cannot statically guarantee
    # that every runtime State comparison is Boolean.
    reasons.append("non_boolean_filter_state_results_change_semantics")

    return {
        "rewrite_id": REWRITE_ID,
        "eligible": False,
        "reasons": sorted(set(reasons)),
    }


def lossless_shorthand_contract():
    """Describe the only currently safe positive-syntax direction."""
    return {
        "semantic_form": "authoring_shorthand",
        "desugars_to": [
            "collect target items",
            "exclude items whose requirement State is true",
            "assert none_exist",
        ],
        "preserves": [
            "filter-state non-Boolean error behavior",
            "collection flag",
            "zero-item vacuity",
            "incomplete collection decisiveness",
            "source item evidence",
        ],
    }
