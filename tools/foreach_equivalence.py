#!/usr/bin/env python3
"""Research helpers for proving direct foreach collection-expansion equivalence.

These helpers model only the value-selection identity needed by the first
foreach modernization class. They do not model target acquisition status or
replace the OVAL result truth tables.

For an Object entity using var_check="at least one":

    match(item, projected_values)
      == OR(match(item, value) for value in projected_values)

Therefore the Object population selected by one multi-valued selector equals
the set-union of populations selected independently for each projected value,
provided the same comparison predicate and source value semantics are used.

The analogous identity is deliberately false for var_check="all".
"""
from __future__ import annotations

from collections.abc import Callable, Iterable
import json


def canonical(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def unique(values: Iterable):
    seen = set()
    out = []
    for value in values:
        key = canonical(value)
        if key not in seen:
            seen.add(key)
            out.append(value)
    return out


def faithful_at_least_one_selection(items, projected_values, predicate: Callable):
    """Select Items exactly as an at-least-one multi-valued Object entity."""
    values = list(projected_values)
    if not values:
        return []
    return unique(
        item
        for item in items
        if any(predicate(item, value) for value in values)
    )


def foreach_union_selection(items, projected_values, predicate: Callable):
    """Conceptual foreach expansion: select per value, then set-union Items."""
    selected = []
    for value in projected_values:
        selected.extend(item for item in items if predicate(item, value))
    return unique(selected)


def faithful_all_selection(items, projected_values, predicate: Callable):
    """Select Items under var_check=all for a non-empty projected value set."""
    values = list(projected_values)
    if not values:
        return []
    return unique(
        item
        for item in items
        if all(predicate(item, value) for value in values)
    )


def equivalent_population(left, right) -> bool:
    """Compare Object populations as sets, independent of collection order."""
    return {canonical(x) for x in left} == {canonical(x) for x in right}


def direct_at_least_one_equivalent(items, projected_values, predicate: Callable) -> bool:
    return equivalent_population(
        faithful_at_least_one_selection(items, projected_values, predicate),
        foreach_union_selection(items, projected_values, predicate),
    )
