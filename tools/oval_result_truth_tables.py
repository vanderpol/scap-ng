#!/usr/bin/env python3
"""Reference OVAL 5.12.3 result combiners used by SCAP-NG conformance tests.

This module intentionally implements only generic result aggregation and
existence truth tables documented in the pinned OVAL 5.12.3 schemas. It is not
an evaluator and does not collect target data.
"""
from collections import Counter

TRUE = "true"
FALSE = "false"
ERROR = "error"
UNKNOWN = "unknown"
NOT_EVALUATED = "not evaluated"
NOT_APPLICABLE = "not applicable"

RESULTS = {TRUE, FALSE, ERROR, UNKNOWN, NOT_EVALUATED, NOT_APPLICABLE}


def _counts(values):
    values = list(values)
    if not values:
        raise ValueError("OVAL result aggregation requires at least one input")
    unknown = [v for v in values if v not in RESULTS]
    if unknown:
        raise ValueError(f"unsupported result values: {unknown}")
    return Counter(values)


def aggregate_check(check, values):
    """Apply OVAL CheckEnumeration to individual result values."""
    c = _counts(values)
    t, f = c[TRUE], c[FALSE]
    e, u, ne, na = c[ERROR], c[UNKNOWN], c[NOT_EVALUATED], c[NOT_APPLICABLE]

    if check == "all":
        if f: return FALSE
        if e: return ERROR
        if u: return UNKNOWN
        if ne: return NOT_EVALUATED
        if t: return TRUE
        if na: return NOT_APPLICABLE
    elif check == "at least one":
        if t: return TRUE
        if e: return ERROR
        if u: return UNKNOWN
        if ne: return NOT_EVALUATED
        if f: return FALSE
        if na: return NOT_APPLICABLE
    elif check == "only one":
        if t >= 2: return FALSE
        if e: return ERROR
        if u: return UNKNOWN
        if ne: return NOT_EVALUATED
        if t == 1: return TRUE
        if f: return FALSE
        if na: return NOT_APPLICABLE
    elif check == "none satisfy":
        if t: return FALSE
        if e: return ERROR
        if u: return UNKNOWN
        if ne: return NOT_EVALUATED
        if f: return TRUE
        if na: return NOT_APPLICABLE
    else:
        raise ValueError(f"unsupported CheckEnumeration: {check}")
    raise AssertionError("unreachable result combination")


def aggregate_operator(operator, values):
    """Apply OVAL OperatorEnumeration to individual result values."""
    c = _counts(values)
    t, f = c[TRUE], c[FALSE]
    e, u, ne, na = c[ERROR], c[UNKNOWN], c[NOT_EVALUATED], c[NOT_APPLICABLE]

    if operator == "AND":
        return aggregate_check("all", values)
    if operator == "OR":
        return aggregate_check("at least one", values)
    if operator == "ONE":
        return aggregate_check("only one", values)
    if operator == "XOR":
        if e: return ERROR
        if u: return UNKNOWN
        if ne: return NOT_EVALUATED
        if t or f:
            return TRUE if t % 2 else FALSE
        if na:
            return NOT_APPLICABLE
        raise AssertionError("unreachable XOR combination")
    raise ValueError(f"unsupported OperatorEnumeration: {operator}")


def aggregate_existence(mode, *, exists=0, does_not_exist=0, error=0, not_collected=0):
    """Apply OVAL ExistenceEnumeration to item-status counts."""
    for name, value in {
        "exists": exists,
        "does_not_exist": does_not_exist,
        "error": error,
        "not_collected": not_collected,
    }.items():
        if not isinstance(value, int) or value < 0:
            raise ValueError(f"{name} must be a non-negative integer")

    if mode == "all_exist":
        if does_not_exist: return FALSE
        if error: return ERROR
        if not_collected: return UNKNOWN
        return TRUE if exists else FALSE

    if mode == "any_exist":
        # OVAL's table makes this true whenever there is no error, including
        # zero matching items; an existing item also makes an error non-fatal.
        if exists: return TRUE
        if error: return ERROR
        return TRUE

    if mode == "at_least_one_exists":
        if exists: return TRUE
        if error: return ERROR
        if not_collected: return UNKNOWN
        return FALSE

    if mode == "none_exist":
        if exists: return FALSE
        if error: return ERROR
        if not_collected: return UNKNOWN
        return TRUE

    if mode == "only_one_exists":
        if exists >= 2: return FALSE
        if error: return ERROR
        if not_collected: return UNKNOWN
        return TRUE if exists == 1 else FALSE

    raise ValueError(f"unsupported ExistenceEnumeration: {mode}")
