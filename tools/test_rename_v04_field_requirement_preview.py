#!/usr/bin/env python3
"""Source-invertible SCAP-NG 0.4 field_requirement naming regressions."""
from copy import deepcopy
import unittest

from rename_v04_field_requirement_preview import (
    migrate_test, restore_test, migrate_document
)
from research_v04_oval_logic_scopes import candidate_logic
from oval_result_truth_tables import aggregate_operator


def source_fixture():
    return {
        "capability": "windows.registry",
        "state_fields_require": "at_least_one_exists_and_all_match",
        "object": {"select": {"hive": {"equals": "local_machine"}}},
        "require": {"items": "one_or_more", "all_items_must": [{
            "or": [
                {"fields": {"type": {"equals": "string"},
                            "value": {"equals": "Enterprise"}}},
                {"require": "may_be_absent_and_all_match",
                 "fields": {"type": {"equals": "string"},
                            "value": {"equals": "EnterpriseS",
                                      "require": "none_exist"}}}
            ]
        }]}
    }


class ReversibleFieldRequirementTests(unittest.TestCase):
    def test_test_policy_inherits_all_fields_unless_condition_or_leaf_overrides(self):
        source = source_fixture()
        output, proof = migrate_test(source)
        self.assertIsNotNone(proof)
        self.assertEqual(proof["field_groups"], 2)
        self.assertEqual(proof["local_groups"], 1)
        self.assertEqual(proof["field_overrides"], 1)
        self.assertEqual(output["require"]["items"], "one_or_more")
        self.assertNotIn("state_fields_require", output)
        self.assertEqual(output["require"]["field_requirement"],
                         "at_least_one_exists_and_all_match")
        branch1, branch2 = output["require"]["all_items_must"][0]["or"]
        self.assertEqual(set(branch1), {"fields"})
        self.assertEqual(branch1["fields"]["value"]["equals"], "Enterprise")
        self.assertEqual(branch2["field_requirement"],
                         "may_be_absent_and_all_match")
        self.assertNotIn("require", branch2)
        self.assertEqual(branch2["fields"]["value"]["field_requirement"],
                         "none_exist")
        self.assertNotIn("require", branch2["fields"]["value"])
        self.assertEqual(restore_test(output, proof), source)

    def test_field_map_and_is_independent_of_whole_condition_or(self):
        source = source_fixture()
        output, proof = migrate_test(source)
        branches = output["require"]["all_items_must"][0]["or"]
        self.assertEqual(len(branches), 2)
        self.assertTrue(all(set(branch) <= {"field_requirement", "fields"}
                            for branch in branches))
        self.assertTrue(all("fields_operator" not in branch
                            for branch in branches))
        # Two complete States that each contain a false field must
        # remain false, even though a flattened field OR would be true.
        per_field = [["true", "false"], ["false", "true"]]
        proposed = candidate_logic("or", [
            candidate_logic("and", values) for values in per_field
        ])
        original = aggregate_operator("OR", [
            aggregate_operator("AND", values) for values in per_field
        ])
        self.assertEqual(proposed, original)
        self.assertEqual(proposed, "false")
        self.assertEqual(candidate_logic("or", sum(per_field, [])), "true")
        self.assertEqual(restore_test(output, proof), source)

    def test_shared_policy_applies_to_both_and_branches_and_item_mode_is_orthogonal(self):
        for op in ("and", "or", "one", "xor"):
            for items in ("one_or_more", "may_be_absent"):
                with self.subTest(op=op, items=items):
                    source = source_fixture()
                    root = source["require"]["all_items_must"][0]
                    root[op] = root.pop("or")
                    source["require"]["items"] = items
                    output, proof = migrate_test(source)
                    self.assertEqual(output["require"]["items"], items)
                    self.assertEqual(output["require"]["field_requirement"],
                                     source["state_fields_require"])
                    self.assertEqual(list(output["require"]["all_items_must"][0]), [op])
                    self.assertEqual(restore_test(output, proof), source)

    def test_mutation_to_logic_field_value_or_requirement_breaks_inverse(self):
        source = source_fixture()
        output, proof = migrate_test(source)
        mutations = [
            lambda t: t["require"]["all_items_must"][0].update(
                and_=t["require"]["all_items_must"][0].pop("or")),
            lambda t: t["require"]["all_items_must"][0]["or"][0][
                "fields"]["value"].update(equals="wrong"),
            lambda t: t["require"]["field_requirement"].__class__ == str
                      and t["require"].update(field_requirement="none_exist"),
            lambda t: t["require"]["all_items_must"][0]["or"][1].update(
                field_requirement="none_exist"),
            lambda t: t["require"]["items"].__class__ == str
                      and t["require"].update(items="may_be_absent"),
        ]
        for change in mutations:
            tampered = deepcopy(output)
            change(tampered)
            with self.assertRaisesRegex(ValueError, "edited"):
                restore_test(tampered, proof)

    def test_unsafe_record_repeated_or_mixed_condition_stays_unchanged(self):
        for change in (
            lambda t: t["require"]["all_items_must"][0]["or"][1][
                "fields"]["value"].update(record={"fields": {}}),
            lambda t: t["require"]["all_items_must"][0]["or"].append(
                {"value": {"equals": "other"}}),
            lambda t: t["require"]["all_items_must"][0]["or"][1].update(
                field_requirement="none_exist"),
            lambda t: t["require"]["all_items_must"][0]["or"][1][
                "fields"]["value"].update(field_requirement="none_exist"),
            lambda t: t["require"]["all_items_must"][0]["or"][0].update(
                fields_operator="or"),
            lambda t: t["require"]["all_items_must"][0]["or"][0].update(
                fields=[{"type": {"equals": "string"}},
                        {"value": {"equals": "Enterprise"}}]),
        ):
            source = source_fixture()
            change(source)
            output, proof = migrate_test(source)
            self.assertEqual(output, source)
            self.assertIsNone(proof)

    def test_unrelated_tests_and_object_evaluate_are_not_rewritten(self):
        original = {"assessment": {"mode": "automated",
                    "tests": {"edition-test": source_fixture(),
                              "plain": {"require": {"items": "one_or_more"}}},
                    "evaluate": {"and": [{"test": "edition-test"},
                                         {"test": "plain"}]}}}
        candidate, changed = migrate_document(original)
        self.assertEqual(len(changed), 1)
        self.assertEqual(changed[0]["test"], "edition-test")
        self.assertEqual(candidate["assessment"]["tests"]["plain"],
                         original["assessment"]["tests"]["plain"])
        self.assertEqual(candidate["assessment"]["evaluate"],
                         original["assessment"]["evaluate"])
        self.assertEqual(candidate["assessment"]["tests"]["edition-test"]["object"],
                         original["assessment"]["tests"]["edition-test"]["object"])
        self.assertEqual(restore_test(candidate["assessment"]["tests"][
                         "edition-test"], changed[0]),
                         original["assessment"]["tests"]["edition-test"])


if __name__ == "__main__":
    unittest.main()
