#!/usr/bin/env python3
"""Focused equivalence model for foreach collection expansion research.

This does not implement OVAL collection. It proves the selector-level identity
used by the first proposed modernization class:

  OVAL entity comparison against projected variable values with
  var_check="at least one"

is equivalent, for a pure selector comparison, to evaluating the selector once
per projected value and unioning the matching child Items.

It also contains a counterexample showing why var_check="all" is not equivalent
to that same union expansion.
"""
from __future__ import annotations

import itertools
import unittest


def oval_selector_matches(actual, variable_values, *, var_check, compare=lambda a,b: a == b):
    results=[bool(compare(actual, value)) for value in variable_values]
    if not results:
        raise ValueError("OVAL variable with zero values is handled by the referencing Object")
    if var_check == "at least one":
        return any(results)
    if var_check == "all":
        return all(results)
    if var_check == "only one":
        return sum(results) == 1
    if var_check == "none satisfy":
        return not any(results)
    raise ValueError(var_check)


def faithful_selection(items, variable_values, *, var_check, compare=lambda a,b: a == b):
    return [
        item for item in items
        if oval_selector_matches(item, variable_values, var_check=var_check, compare=compare)
    ]


def foreach_union_selection(items, variable_values, *, compare=lambda a,b: a == b):
    """Union matches from one child selector instantiation per projected value."""
    matched=[]
    for value in variable_values:
        for item in items:
            if compare(item, value) and item not in matched:
                matched.append(item)
    return matched


class ForeachSelectorEquivalenceTests(unittest.TestCase):
    def test_at_least_one_equals_union_expansion_for_equality(self):
        universe=("a","b","c")
        value_sets=(("a",),("a","b"),("a","a"),("x",),("x","b"))
        for values in value_sets:
            self.assertEqual(
                faithful_selection(universe, values, var_check="at least one"),
                foreach_union_selection(universe, values),
                values,
            )

    def test_at_least_one_equals_union_expansion_across_small_exhaustive_space(self):
        atoms=("a","b","c")
        item_sets=[]
        for size in range(1,4):
            item_sets.extend(itertools.product(atoms, repeat=size))
        value_sets=[]
        for size in range(1,4):
            value_sets.extend(itertools.product(atoms, repeat=size))
        for items in item_sets:
            for values in value_sets:
                self.assertEqual(
                    set(faithful_selection(items, values, var_check="at least one")),
                    set(foreach_union_selection(items, values)),
                    (items,values),
                )

    def test_all_is_not_union_expansion(self):
        items=("a","b")
        values=("a","b")
        self.assertEqual(
            faithful_selection(items, values, var_check="all"),
            [],
        )
        self.assertEqual(
            foreach_union_selection(items, values),
            ["a","b"],
        )

    def test_duplicate_projected_values_do_not_change_union_selection(self):
        items=("a","b","c")
        self.assertEqual(
            foreach_union_selection(items, ("a","a","b")),
            foreach_union_selection(items, ("a","b")),
        )


if __name__=="__main__":
    unittest.main()
