#!/usr/bin/env python3
from __future__ import annotations

import itertools
import sys
from pathlib import Path
import unittest

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from foreach_equivalence import (
    direct_at_least_one_equivalent,
    faithful_at_least_one_selection,
    faithful_all_selection,
    foreach_union_selection,
    equivalent_population,
)
from oval_result_truth_tables import (
    TRUE,
    FALSE,
    resolve_variable_reference,
    apply_variable_reference_context,
    evaluate_collected_object_test,
)


def evaluate_population(population, *, existence, check, state_by_item, has_state=True):
    """Feed a selected Object population through the existing OVAL Test tables."""
    population = list(population)
    kwargs = {
        "flag": "complete",
        "existence": existence,
        "check": check,
        "has_state": has_state,
        "exists": len(population),
    }
    if has_state:
        kwargs["item_results"] = [state_by_item[item] for item in population]
    return evaluate_collected_object_test(**kwargs)


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

    def test_zero_projected_values_preserves_object_reference_status_obligation(self):
        variable = resolve_variable_reference([])
        self.assertEqual(
            apply_variable_reference_context(variable, "object"),
            "does_not_exist",
        )
        # A native foreach lowering cannot silently turn this into a normal
        # complete Object with an empty Item set. It must preserve the
        # Object-reference no-values status before Test evaluation.
        for existence, expected in (
            ("any_exist", TRUE),
            ("none_exist", TRUE),
            ("at_least_one_exists", FALSE),
            ("all_exist", FALSE),
            ("only_one_exists", FALSE),
        ):
            with self.subTest(existence=existence):
                self.assertEqual(
                    evaluate_collected_object_test(
                        "does not exist",
                        existence=existence,
                    ),
                    expected,
                )


class DownstreamTestResultEquivalence(unittest.TestCase):
    """If collection population/status are equal, all later Test scopes stay equal."""

    def test_complete_population_preserves_existence_and_check_results(self):
        items = ["a", "b", "c"]
        predicate = lambda item, value: item == value
        state_assignments = list(itertools.product((TRUE, FALSE), repeat=len(items)))
        value_sequences = [
            ["a"],
            ["b"],
            ["a", "b"],
            ["a", "a", "b"],
            ["a", "b", "c"],
            ["missing"],
        ]
        existence_modes = (
            "any_exist",
            "at_least_one_exists",
            "all_exist",
            "none_exist",
            "only_one_exists",
        )
        checks = ("all", "at least one", "only one", "none satisfy")

        for values in value_sequences:
            faithful = faithful_at_least_one_selection(items, values, predicate)
            modern = foreach_union_selection(items, values, predicate)
            self.assertTrue(equivalent_population(faithful, modern))
            for assignment in state_assignments:
                state_by_item = dict(zip(items, assignment))
                for existence in existence_modes:
                    for check in checks:
                        # For any_exist + zero Items + State, the repository's
                        # generic truth-table helper intentionally has no empty
                        # Boolean aggregation rule. That specific OVAL corner is
                        # tracked separately rather than guessed here.
                        if not faithful and existence == "any_exist":
                            continue
                        with self.subTest(
                            values=values,
                            assignment=assignment,
                            existence=existence,
                            check=check,
                        ):
                            left = evaluate_population(
                                faithful,
                                existence=existence,
                                check=check,
                                state_by_item=state_by_item,
                            )
                            right = evaluate_population(
                                modern,
                                existence=existence,
                                check=check,
                                state_by_item=state_by_item,
                            )
                            self.assertEqual(left, right)

    def test_existence_only_tests_include_zero_item_cases(self):
        items = ["a", "b"]
        predicate = lambda item, value: item == value
        for values in ([], ["a"], ["a", "b"], ["missing"]):
            faithful = faithful_at_least_one_selection(items, values, predicate)
            modern = foreach_union_selection(items, values, predicate)
            for existence in (
                "any_exist",
                "at_least_one_exists",
                "all_exist",
                "none_exist",
                "only_one_exists",
            ):
                with self.subTest(values=values, existence=existence):
                    left = evaluate_population(
                        faithful,
                        existence=existence,
                        check="all",
                        state_by_item={},
                        has_state=False,
                    )
                    right = evaluate_population(
                        modern,
                        existence=existence,
                        check="all",
                        state_by_item={},
                        has_state=False,
                    )
                    self.assertEqual(left, right)


if __name__ == "__main__":
    unittest.main()
