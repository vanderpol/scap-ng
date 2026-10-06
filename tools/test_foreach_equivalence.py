#!/usr/bin/env python3
from __future__ import annotations

import itertools
import unittest

from foreach_equivalence import (
    direct_at_least_one_equivalent,
    faithful_all_selection,
    foreach_union_selection,
    equivalent_population,
)


class DirectCollectionExpansionEquivalence(unittest.TestCase):
    def test_exhaustive_equals_domain(self):
        domain = ["a", "b", "c"]
        item_sets = []
        for n in range(len(domain) + 1):
            item_sets.extend(itertools.combinations(domain, n))
        value_sets = []
        for n in range(len(domain) + 1):
            value_sets.extend(itertools.product(domain, repeat=n))

        for items in item_sets:
            for values in value_sets:
                with self.subTest(items=items, values=values):
                    self.assertTrue(
                        direct_at_least_one_equivalent(
                            items,
                            values,
                            lambda item, value: item == value,
                        )
                    )

    def test_duplicate_projected_values_do_not_change_population(self):
        items = ["/home/a", "/home/b", "/home/c"]
        self.assertTrue(
            direct_at_least_one_equivalent(
                items,
                ["/home/a", "/home/a", "/home/b"],
                lambda item, value: item == value,
            )
        )

    def test_arbitrary_binary_predicate_preserves_or_identity(self):
        items = [1, 2, 3, 4, 5]
        values = [2, 3]
        # "divisible by projected value" is intentionally not equality; the
        # proof depends on at-least-one quantification, not a specific operator.
        self.assertTrue(
            direct_at_least_one_equivalent(
                items,
                values,
                lambda item, value: item % value == 0,
            )
        )

    def test_all_values_is_not_union_equivalent(self):
        items = [1, 2, 3, 4, 6]
        values = [2, 3]
        predicate = lambda item, value: item % value == 0
        faithful = faithful_all_selection(items, values, predicate)
        foreach_union = foreach_union_selection(items, values, predicate)
        self.assertFalse(equivalent_population(faithful, foreach_union))
        self.assertEqual(faithful, [6])
        self.assertEqual(set(foreach_union), {2, 3, 4, 6})

    def test_zero_projected_values_remains_empty_for_value_selection_model(self):
        # This establishes only the selector population identity. OVAL's
        # context-specific zero-value Variable status still has to be preserved
        # by the source/Variable control-flow proof before automatic rewriting.
        self.assertTrue(
            direct_at_least_one_equivalent(
                ["a", "b"],
                [],
                lambda item, value: item == value,
            )
        )


if __name__ == "__main__":
    unittest.main()
