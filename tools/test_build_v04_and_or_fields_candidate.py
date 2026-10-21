#!/usr/bin/env python3
"""Regression tests for reversible 0.4-C whole-State operators + fields."""
from copy import deepcopy
import unittest

from build_v04_and_or_fields_candidate import (
    project_document, restore_document, simple_and_group,
    transform_test,
)


def field(name, value, *, required=None):
    predicate = {"equals": value}
    if required is not None:
        predicate["require"] = required
    return {name: predicate}


def source_fixture(operator="any"):
    return {"assessment": {
        "id": "SV-253254.automated", "mode": "automated",
        "tests": {"edition-test": {
            "capability": "windows.registry",
            "state_fields_require": "at_least_one_exists_and_all_match",
            "states_match": operator,
            "require": {
                "items": "one_or_more",
                "all_items_must": [
                    {"and": [field("type", "string"),
                             field("value", "Enterprise")]},
                    {"state_fields_require": "may_be_absent_and_all_match",
                     "and": [field("type", "string"),
                             field("value", "EnterpriseS")]},
                ]}}},
        "evaluate": {"test": "edition-test"}}}


class SixStigFieldPreviewTests(unittest.TestCase):
    def test_whole_state_or_joins_complete_fields_condition_groups(self):
        original = source_fixture("any")
        candidate, ledger = project_document(original)
        self.assertEqual(restore_document(candidate, ledger), original)
        test = candidate["assessment"]["tests"]["edition-test"]
        self.assertNotIn("states_match", test)
        self.assertEqual(test["require"]["items"], "one_or_more")
        self.assertEqual(len(ledger["states"]), 1)
        self.assertEqual(len(ledger["fields"]), 1)
        self.assertEqual(len(ledger["fields"][0]["changed_field_groups"]), 2)
        group = test["require"]["all_items_must"][0]
        self.assertEqual(set(group), {"or"})
        first, second = group["or"]
        self.assertEqual(set(first), {"fields"})
        self.assertEqual(first["fields"]["value"]["equals"], "Enterprise")
        self.assertEqual(list(second), ["require", "fields"])
        self.assertEqual(second["require"], "may_be_absent_and_all_match")
        self.assertEqual(second["fields"]["value"]["equals"], "EnterpriseS")
        # The original Test-wide scope is retained for inherited predicates.
        self.assertEqual(test["state_fields_require"],
                         "at_least_one_exists_and_all_match")

    def test_whole_state_and_not_flattened_even_if_fields_are_unique(self):
        original = source_fixture("all")
        candidate, ledger = project_document(original)
        self.assertEqual(restore_document(candidate, ledger), original)
        group = candidate["assessment"]["tests"]["edition-test"][
            "require"]["all_items_must"][0]
        self.assertEqual(set(group), {"and"})
        self.assertEqual(len(group["and"]), 2)
        self.assertTrue(all("fields" in x for x in group["and"]))

    def test_original_duplicate_fields_stay_explicit(self):
        original = source_fixture("any")
        t = original["assessment"]["tests"]["edition-test"]
        t["require"]["all_items_must"][0] = {"and": [
            field("value", "a"), field("value", "b")]}
        candidate, ledger = project_document(original)
        self.assertEqual(restore_document(candidate, ledger), original)
        group = candidate["assessment"]["tests"]["edition-test"][
            "require"]["all_items_must"][0]["or"][0]
        self.assertEqual(group, t["require"]["all_items_must"][0])
        self.assertEqual(len(ledger["fields"][0]["changed_field_groups"]), 1)

    def test_record_or_unscoped_and_not_blindly_collapsed(self):
        self.assertIsNone(simple_and_group({
            "and": [field("type", "a"), {"value": {"record": {}}}]}))
        original = source_fixture()
        t = original["assessment"]["tests"]["edition-test"]
        t.pop("state_fields_require")
        t["require"]["all_items_must"][0] = {
            "and": [field("type", "string"), field("value", "x")]}
        # The first AND has no known shared or per-leaf presence policy,
        # so it is preserved without guessing field cardinalities.
        candidate, ledger = project_document(original)
        self.assertEqual(restore_document(candidate, ledger), original)
        group = candidate["assessment"]["tests"]["edition-test"][
            "require"]["all_items_must"][0]["or"][0]
        self.assertIn("and", group)

    def test_group_of_individually_scoped_fields_is_reversible(self):
        t = {"require": {
            "items": "one_or_more", "all_items_must": [
              {"and": [field("type", "string",
                             required="at_least_one_exists_and_all_match"),
                       field("value", "0",
                             required="none_exist")]}]}}
        updated, ledger = transform_test(t)
        self.assertEqual(len(ledger), 1)
        self.assertEqual(updated["require"]["all_items_must"][0]["fields"],
                         {"type": {"equals": "string",
                                   "require": "at_least_one_exists_and_all_match"},
                          "value": {"equals": "0", "require": "none_exist"}})

    def test_mutation_of_any_group_or_field_breaks_inverse(self):
        original = source_fixture()
        candidate, ledger = project_document(original)
        corruptions = [
            lambda a: a["assessment"]["tests"]["edition-test"]["require"][
                "all_items_must"][0]["or"][0]["fields"]["value"].update(
                    equals="Education"),
            lambda a: a["assessment"]["tests"]["edition-test"]["require"][
                "all_items_must"][0]["or"][1].update(
                    require="none_exist"),
            lambda a: a["assessment"]["tests"]["edition-test"].update(
                    state_fields_require="none_exist"),
            lambda a: a["assessment"]["tests"]["edition-test"]["require"][
                "all_items_must"][0].update(
                    {"and": a["assessment"]["tests"]["edition-test"][
                        "require"]["all_items_must"][0].pop("or")}),
        ]
        for change in corruptions:
            edited = deepcopy(candidate)
            change(edited)
            with self.assertRaises(ValueError):
                restore_document(edited, ledger)


if __name__ == "__main__":
    unittest.main()
