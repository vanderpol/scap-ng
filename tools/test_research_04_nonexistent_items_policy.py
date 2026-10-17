#!/usr/bin/env python3
"""Issue #235/#229: demonstrate boundaries of banning phantom missing Items.

OVAL 5.12.3 generic result model, NOT native scanner parity.
The proposal concerns native Item representation, not source OVAL data mutability.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from oval_result_truth_tables import (
    TRUE, FALSE, ERROR, UNKNOWN,
    aggregate_existence, evaluate_collected_object_test,
)


class NativeItemsMustExistResearch(unittest.TestCase):
    def test_complete_existing_items_same_existence_result(self):
        for quantity in (1, 2, 7):
            with self.subTest(quantity=quantity):
                self.assertEqual(TRUE, aggregate_existence("all_exist", exists=quantity))
                self.assertEqual(TRUE, aggregate_existence("at_least_one_exists", exists=quantity))

    def test_complete_empty_collection_both_false(self):
        self.assertEqual(FALSE, aggregate_existence("all_exist"))
        self.assertEqual(FALSE, aggregate_existence("at_least_one_exists"))

    def test_phantom_absent_item_changes_existence_result(self):
        self.assertEqual(
            FALSE, aggregate_existence("all_exist", exists=1, does_not_exist=1)
        )
        self.assertEqual(
            TRUE, aggregate_existence("at_least_one_exists", exists=1, does_not_exist=1)
        )

    def test_prohibiting_phantom_absence_does_not_remove_error_divergence(self):
        self.assertEqual(ERROR, aggregate_existence("all_exist", exists=1, error=1))
        self.assertEqual(
            TRUE, aggregate_existence("at_least_one_exists", exists=1, error=1)
        )

    def test_prohibiting_phantom_absence_does_not_remove_unknown_divergence(self):
        self.assertEqual(
            UNKNOWN, aggregate_existence("all_exist", exists=1, not_collected=1)
        )
        self.assertEqual(
            TRUE, aggregate_existence("at_least_one_exists", exists=1, not_collected=1)
        )

    def test_incomplete_collector_has_additional_difference(self):
        # This case is different even if every returned Item has status exists.
        # An observed matching witness may settle at-least-one + some-match,
        # but cannot prove that ALL potential Items have been evaluated.
        self.assertEqual(
            TRUE,
            evaluate_collected_object_test(
                "incomplete", existence="at_least_one_exists",
                check="at least one", item_results=[TRUE],
                has_state=True, exists=1,
            ),
        )
        self.assertEqual(
            UNKNOWN,
            evaluate_collected_object_test(
                "incomplete", existence="all_exist",
                check="at least one", item_results=[TRUE],
                has_state=True, exists=1,
            ),
        )

    def test_known_missing_resource_does_not_require_phantom_item(self):
        # Existing OVAL collected-object-level flag preserves absence without
        # pretending a nonexistent leaf is an existing Item.
        self.assertEqual(
            FALSE, evaluate_collected_object_test(
                "does not exist", existence="at_least_one_exists", has_state=False
            )
        )
        self.assertEqual(
            TRUE, evaluate_collected_object_test(
                "does not exist", existence="none_exist", has_state=False
            )
        )

    def test_not_collected_still_unknown_without_fabricated_items(self):
        self.assertEqual(
            UNKNOWN, evaluate_collected_object_test(
                "not collected", existence="at_least_one_exists", has_state=False
            )
        )


if __name__ == "__main__":
    unittest.main()
