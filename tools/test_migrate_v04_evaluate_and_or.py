#!/usr/bin/env python3
"""Adversarial Test-result AND/OR scope migration, not Item/State renaming."""
from copy import deepcopy
import unittest

from migrate_v04_evaluate_and_or import migrate,restore,assert_inverse


def fixture():
    return {"assessment":{
        "id":"sv-combined.assessment","mode":"automated",
        "specification":{"version":"0.4.0"},
        "tests":{"a-test":{
            "states_match":"any",
            "state_fields_require":"at_least_one_exists_and_all_match",
            "object":{"select":{"field":{"value_match":"any","equals":["x","y"]}}},
            "require":{"items":"one_or_more","all_items_must":[
                {"and":[{"type":{"equals":"dword"}},{"value":{"equals":0}}]},
                {"and":[{"type":{"equals":"string"}},{"value":{"equals":"Disabled"}}]}]},
            "reported_elements":"all"}},
        "evaluate":{"all":[{"test":"a-test"},
            {"not":{"any":[{"test":"b-test"},
                           {"odd":[{"test":"c-test"},
                                   {"test":"d-test"}]}]}}]}}}


class EvaluateOnlyMigrationTests(unittest.TestCase):
    def test_source_evaluate_and_or_xor_without_touching_state_or_items(self):
        src=fixture()
        changed,ledger=migrate(src)
        self.assertEqual(len(ledger),1)
        e=changed["assessment"]["evaluate"]
        self.assertEqual(list(e),["and"])
        self.assertEqual(list(e["and"][1]["not"]),["or"])
        self.assertEqual(list(e["and"][1]["not"]["or"][1]),["xor"])
        self.assertEqual(len(ledger[0]["replaced_operators"]),3)
        t=changed["assessment"]["tests"]["a-test"]
        self.assertEqual(t,src["assessment"]["tests"]["a-test"])
        self.assertEqual(t["states_match"],"any")
        self.assertEqual(t["require"]["items"],"one_or_more")
        self.assertEqual(t["object"]["select"]["field"]["value_match"],"any")
        self.assertTrue(assert_inverse(src,changed,ledger))

    def test_direct_test_with_no_logical_operator_remains_byte_equivalent(self):
        src=fixture()
        src["assessment"]["evaluate"]={"test":"a-test"}
        new,proof=migrate(src)
        self.assertEqual(new,src)
        self.assertEqual(proof,[])
        self.assertTrue(assert_inverse(src,new,proof))

    def test_conditionals_and_not_applicable_preserved(self):
        src=fixture()
        src["assessment"]["evaluate"]={
            "if":{"test":"a-test"},
            "then":{"all":[{"test":"b-test"},{"test":"c-test"}]},
            "else":{"not_applicable":{"reason":"Source case skipped"}}}
        new,proof=migrate(src)
        self.assertEqual(list(new["assessment"]["evaluate"]["then"]),["and"])
        self.assertEqual(new["assessment"]["evaluate"]["else"],
                         src["assessment"]["evaluate"]["else"])
        self.assertTrue(assert_inverse(src,new,proof))

    def test_corruption_in_changed_source_expression_detected(self):
        src=fixture()
        new,proof=migrate(src)
        bad=deepcopy(new)
        bad["assessment"]["evaluate"]["and"][0]["test"]="different-test"
        with self.assertRaisesRegex(ValueError,"Changed normalized"):
            restore(bad,proof)

    def test_canonical_input_is_idempotent_and_mixed_input_restores_exactly(self):
        src=fixture()
        src["assessment"]["evaluate"]={"and":[{"test":"a-test"},
            {"any":[{"one":[{"test":"b-test"}]},
                    {"xor":[{"test":"c-test"}, {"odd":[{"test":"d-test"}]}]}]}]}
        new, proof=migrate(src)
        self.assertTrue(assert_inverse(src,new,proof))
        again, empty=migrate(new)
        self.assertEqual(again,new)
        self.assertEqual(empty,[])
        self.assertEqual(restore(new,empty),new)
        bad=deepcopy(proof)
        bad[0]["replaced_operators"][0]["site"]=["missing"]
        with self.assertRaises((ValueError,KeyError)):
            restore(new,bad)

    def test_illegal_mixed_alias_or_extra_expression_fails_closed(self):
        for mutant in (
            {"all":[{"test":"a-test"}],"any":[{"test":"b-test"}]},
            {"or":[],"any":[{"test":"b-test"}]},
            {"all":[]},
            {"if":{"test":"a-test"},"then":{"test":"b-test"}},
        ):
            doc=fixture()
            doc["assessment"]["evaluate"]=mutant
            with self.subTest(mutant=mutant),self.assertRaises(ValueError):
                migrate(doc)


if __name__=="__main__":
    unittest.main()
