#!/usr/bin/env python3
import copy
import unittest
from tools.migrate_v04_field_requirement import migrate, restore
from tools.build_v04_and_or_fields_candidate import project_document, restore_document


def example():
    return {"assessment": {"mode": "automated", "tests": {"edition-test": {
        "capability": "windows.registry",
        "state_fields_require": "at_least_one_exists_and_all_match",
        "require": {"items": "one_or_more", "all_items_must": [
            {"and": [{"type": {"equals": "string"}},
                     {"value": {"equals": "Enterprise"}}]},
            {"and": [{"type": {"equals": "string"}},
                     {"value": {"equals": "EnterpriseS"}}]}]},
        "states_match": "any"}}}}


class FieldRequirementMigration(unittest.TestCase):
    def test_composition_preserves_entire_source(self):
        original = example()
        intermediate, logic = project_document(original)
        candidate, fields = migrate(intermediate)
        test = candidate["assessment"]["tests"]["edition-test"]
        self.assertEqual(test["require"]["items"], "one_or_more")
        self.assertEqual(test["require"]["field_requirement"],
                         "at_least_one_exists_and_all_match")
        self.assertNotIn("states_match", test)
        self.assertNotIn("state_fields_require", test)
        self.assertEqual(len(test["require"]["all_items_must"][0]["or"]), 2)
        self.assertEqual(
            restore_document(restore(candidate, fields), logic), original)

    def test_mutation_rejected(self):
        intermediate, _ = project_document(example())
        candidate, fields = migrate(intermediate)
        broken = copy.deepcopy(candidate)
        broken["assessment"]["tests"]["edition-test"]["require"]["items"] = "none"
        with self.assertRaises(ValueError):
            restore(broken, fields)

    def test_missing_and_conflicting_scopes_fail_closed(self):
        old = example()
        old["assessment"]["tests"]["edition-test"]["require"] = "all_exist_all_match"
        with self.assertRaises(ValueError):
            migrate(old)
        old = example()
        old["assessment"]["tests"]["edition-test"]["require"]["field_requirement"] = "none_exist"
        with self.assertRaises(ValueError):
            migrate(old)

    def test_condition_and_leaf_overrides(self):
        old = example()
        test = old["assessment"]["tests"]["edition-test"]
        test.pop("states_match")
        test["require"]["all_items_must"] = [{
            "or": [{"require": "may_be_absent_and_all_match",
                    "fields": {"value": {"equals": "Enterprise",
                                         "require": "only_one_exists_and_matches"}}},
                   {"fields": {"value": {"equals": "EnterpriseS"}}}]}]
        candidate, ledger = migrate(old)
        first = candidate["assessment"]["tests"]["edition-test"]["require"]["all_items_must"][0]["or"][0]
        self.assertEqual(first["field_requirement"], "may_be_absent_and_all_match")
        self.assertEqual(first["fields"]["value"]["field_requirement"],
                         "only_one_exists_and_matches")
        self.assertEqual(restore(candidate, ledger), old)

    def test_state_free_bluetooth_unchanged(self):
        old = {"assessment": {"mode": "automated", "tests": {
            "bluetooth-test": {"object": {"command": "Get-PnpDevice"},
                               "require": {"items": "one_or_more"}}}}}
        candidate, ledger = migrate(old)
        self.assertEqual(candidate, old)
        self.assertFalse(ledger["changes"])


if __name__ == "__main__":
    unittest.main()
