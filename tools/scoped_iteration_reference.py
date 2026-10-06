#!/usr/bin/env python3
"""Reference semantics for the SCAP-NG 0.3 scoped-iteration proposal.

Research-only. This module defines the proposed scope aggregation contract
independently of YAML serialization and capability collection. It deliberately
reuses established OVAL result/existence vocabulary where the proposal says the
semantics are inherited, while keeping native partial-population handling
separate from OVAL collected_object flag=incomplete.
"""
from __future__ import annotations

from tools.oval_result_truth_tables import (
    TRUE,
    FALSE,
    ERROR,
    UNKNOWN,
    NOT_EVALUATED,
    NOT_APPLICABLE,
    aggregate_check,
    aggregate_existence,
    decisive_partial_check,
)

TECHNICAL_OUTCOMES = {
    TRUE, FALSE, ERROR, UNKNOWN, NOT_EVALUATED, NOT_APPLICABLE
}

_CHECK_ALIASES = {
    "all": "all",
    "at_least_one": "at least one",
    "at least one": "at least one",
    "only_one": "only one",
    "only one": "only one",
    "none_satisfy": "none satisfy",
    "none satisfy": "none satisfy",
}


def canonical_check_semantics(value):
    """Map provisional NG token spelling to inherited OVAL check semantics."""
    try:
        return _CHECK_ALIASES[value]
    except KeyError as exc:
        raise ValueError(f"unsupported scoped check: {value}") from exc



def evaluate_complete_scope(
    *,
    check_existence,
    check,
    body_outcomes,
    exists=None,
    does_not_exist=0,
    error=0,
    not_collected=0,
):
    """Evaluate one complete scoped source population.

    body_outcomes contains one technical outcome for each source Item whose
    scoped body was evaluated. For ordinary successful Items, exists defaults
    to len(body_outcomes).

    Source existence is evaluated before body aggregation. If existence is not
    true, that result is returned and body aggregation does not control the
    scope. If zero source Items are explicitly acceptable under the selected
    existence rule, the scope returns the existence result without invoking an
    empty host-language all()/any() aggregation.
    """
    vals = list(body_outcomes)
    if any(v not in TECHNICAL_OUTCOMES for v in vals):
        raise ValueError("unsupported scoped body outcome")
    if exists is None:
        exists = len(vals)

    existence = aggregate_existence(
        check_existence,
        exists=exists,
        does_not_exist=does_not_exist,
        error=error,
        not_collected=not_collected,
    )
    if existence != TRUE:
        return {
            "outcome": existence,
            "existence_outcome": existence,
            "body_evaluated": bool(vals),
            "logical_complete": True,
            "population_complete": True,
        }

    if exists == 0:
        # This is an explicit existence-policy outcome, not vacuous Boolean
        # truth over an empty loop body.
        return {
            "outcome": TRUE,
            "existence_outcome": TRUE,
            "body_evaluated": False,
            "logical_complete": True,
            "population_complete": True,
        }

    if len(vals) != exists:
        raise ValueError(
            "complete scope requires one body outcome for each existing source Item"
        )

    outcome = aggregate_check(canonical_check_semantics(check), vals)
    return {
        "outcome": outcome,
        "existence_outcome": TRUE,
        "body_evaluated": True,
        "logical_complete": True,
        "population_complete": True,
    }


def evaluate_partial_scope(
    *,
    check_existence,
    check,
    observed_body_outcomes,
    observed_exists,
    existence_already_true=False,
):
    """Evaluate a native evaluator-controlled partial source population.

    This is NOT OVAL collected_object flag=incomplete semantics.

    A partial population may return true/false only when the result is
    irreversible under every unseen continuation. Otherwise it returns unknown
    and marks logical_complete false.

    existence_already_true is supplied only when the existence requirement is
    itself monotonic and already established by the observed population (for
    example at_least_one_exists after observing one existing Item).
    """
    vals = list(observed_body_outcomes)
    if any(v not in TECHNICAL_OUTCOMES for v in vals):
        raise ValueError("unsupported scoped body outcome")
    if observed_exists < 0:
        raise ValueError("observed_exists must be non-negative")

    # Some existence modes can become decisively false from a prefix.
    if check_existence == "none_exist" and observed_exists >= 1:
        return {
            "outcome": FALSE,
            "existence_outcome": FALSE,
            "logical_complete": True,
            "population_complete": False,
        }
    if check_existence == "only_one_exists" and observed_exists >= 2:
        return {
            "outcome": FALSE,
            "existence_outcome": FALSE,
            "logical_complete": True,
            "population_complete": False,
        }

    if check_existence in {"at_least_one_exists", "any_exist"} and observed_exists >= 1:
        existence_already_true = True

    if not existence_already_true:
        return {
            "outcome": UNKNOWN,
            "existence_outcome": UNKNOWN,
            "logical_complete": False,
            "population_complete": False,
        }

    decisive = decisive_partial_check(canonical_check_semantics(check), vals)
    if decisive is None:
        return {
            "outcome": UNKNOWN,
            "existence_outcome": TRUE,
            "logical_complete": False,
            "population_complete": False,
        }

    return {
        "outcome": decisive,
        "existence_outcome": TRUE,
        "logical_complete": True,
        "population_complete": False,
    }


def compact_scope_summary(outcomes, retained, *, population_complete, evidence_complete):
    """Build a compact result summary without requiring one result per scope."""
    vals = list(outcomes)
    counts = {k: 0 for k in (
        TRUE, FALSE, ERROR, UNKNOWN, NOT_EVALUATED, NOT_APPLICABLE
    )}
    for value in vals:
        if value not in counts:
            raise ValueError(f"unsupported outcome {value}")
        counts[value] += 1
    return {
        "evaluated_scopes": len(vals),
        "outcome_counts": counts,
        "population_complete": bool(population_complete),
        "evidence_complete": bool(evidence_complete),
        "retained_scope_evidence": list(retained),
    }
