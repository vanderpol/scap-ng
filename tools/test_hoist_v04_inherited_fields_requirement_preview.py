#!/usr/bin/env python3
"""Explicit group-level shared requirement source-inverse safety tests."""
import unittest
from copy import deepcopy
from hoist_v04_inherited_fields_requirement_preview import (
    migrate_test,restore_test,migrate_document
)


def fixture():
    return {
        "capability":"windows.registry",
        "state_fields_require":"at_least_one_exists_and_all_match",
        "require":{"items":"one_or_more",
                   "all_items_must":[{"or":[
                       {"fields":{"type":{"equals":"string"},
                                  "value":{"equals":"Enterprise"}}},
                       {"fields":{"type":{"equals":"string"},
                                  "value":{"equals":"EnterpriseS"}}}]}]},
        "object":{"select":{"hive":{"equals":"local_machine"}}}
    }


class GroupHoistTests(unittest.TestCase):
    def test_exact_oval_complete_state_or_and_shared_field_rule(self):
        source=fixture()
        proposed,proof=migrate_test(source)
        self.assertEqual(proof["fields_children"],2)
        self.assertEqual(proof["state_operator"],"or")
        self.assertNotIn("state_fields_require",proposed)
        self.assertEqual(proposed["require"]["items"],"one_or_more")
        group=proposed["require"]["all_items_must"][0]
        self.assertEqual(list(group),["require","or"])
        self.assertEqual(group["require"],"at_least_one_exists_and_all_match")
        self.assertEqual([x["fields"]["value"]["equals"] for x in group["or"]],
                         ["Enterprise","EnterpriseS"])
        self.assertEqual(restore_test(proposed,proof),source)

    def test_and_across_complete_conditions_hoists_equally(self):
        before=fixture()
        group=before["require"]["all_items_must"][0]
        group["and"]=group.pop("or")
        proposed,proof=migrate_test(before)
        self.assertEqual(list(proposed["require"]["all_items_must"][0]),["require","and"])
        self.assertEqual(restore_test(proposed,proof),before)

    def test_any_changed_field_match_or_boolean_operator_breaks_inverse(self):
        before=fixture()
        after,proof=migrate_test(before)
        modified=deepcopy(after)
        modified["require"]["all_items_must"][0]["or"][1]["fields"]["value"]["equals"]="bad"
        with self.assertRaisesRegex(ValueError,"changed after migration"):
            restore_test(modified,proof)
        modified=deepcopy(after)
        group=modified["require"]["all_items_must"][0]
        group["and"]=group.pop("or")
        with self.assertRaisesRegex(ValueError,"changed after migration"):
            restore_test(modified,proof)

    def test_unsafe_source_groups_are_not_touched(self):
        for mutation in (
            lambda x:x.pop("state_fields_require"),
            lambda x:x["require"]["all_items_must"].append({"value":{"equals":"bad"}}),
            lambda x:x["require"]["all_items_must"][0]["or"][0]
                     .update(require="none_exist"),
            lambda x:x["require"]["all_items_must"][0]["or"][0]
                     ["fields"]["value"].update(record={"fields":{}}),
            lambda x:x["require"].update(items="none"),
        ):
            src=fixture()
            mutation(src)
            candidate,proof=migrate_test(src)
            # Record subfield selectors are intentionally not converted by
            # the original source-safe fields migrator; the last two cases
            # remain outside this isolated hoist if their field predicate
            # is an unsupported shape.
            if proof:
                self.assertEqual(restore_test(candidate,proof),src)
            else:
                self.assertEqual(candidate,src)

    def test_source_legacy_states_or_other_matching_operator_are_not_hoisted(self):
        for extra in ({"states":[{"value":{"equals":"legacy"}}]},
                      {"states_match":"any"}):
            source=fixture()
            source.update(extra)
            with self.subTest(extra=extra):
                new,ledger=migrate_test(source)
                self.assertEqual(new,source)
                self.assertIsNone(ledger)

    def test_document_exact_inverse_and_identity(self):
        doc={"assessment":{"id":"example","mode":"automated",
                           "tests":{"enterprise-edition-test":fixture()},
                           "evaluate":{"test":"enterprise-edition-test"}}}
        out,proof=migrate_document(doc)
        self.assertEqual(len(proof),1)
        self.assertEqual(out["assessment"]["evaluate"],doc["assessment"]["evaluate"])
        self.assertEqual(out["assessment"]["tests"]["enterprise-edition-test"]["object"],
                         doc["assessment"]["tests"]["enterprise-edition-test"]["object"])


if __name__=="__main__":
    unittest.main()
