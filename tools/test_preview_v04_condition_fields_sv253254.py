#!/usr/bin/env python3
"""Source-backed naming candidate versus OVAL whole-State OR boundary tests."""
from copy import deepcopy
import unittest

from preview_v04_condition_fields_sv253254 import preview,restore,exact_inverse


def source_fixture():
    return {"assessment":{
      "id":"SV-253254.automated","mode":"automated",
      "specification":{"version":"0.4.0"},
      "tests":{"editionid-enterprise-or-enterprises-test":{
        "test_title":"EditionID is Enterprise or EnterpriseS",
        "capability":"windows.registry",
        "state_fields_require":"at_least_one_exists_and_all_match",
        "require":{"items":"one_or_more","all_items_must":[{"or":[
          {"and":[{"type":{"equals":"string"}},{"value":{"equals":"Enterprise"}}]},
          {"and":[{"type":{"equals":"string"}},{"value":{"equals":"EnterpriseS"}}]}]}]},
        "reported_elements":"all"}},
      "evaluate":{"test":"editionid-enterprise-or-enterprises-test"}}}


class ConditionNamingTests(unittest.TestCase):
    def test_one_shared_require_before_complete_field_groups(self):
        source=source_fixture()
        new,ledger=preview(source)
        test=new["assessment"]["tests"]["editionid-enterprise-or-enterprises-test"]
        self.assertNotIn("state_fields_require",test)
        self.assertEqual(test["require"]["items"],"one_or_more")
        group=test["require"]["all_items_must"][0]
        self.assertEqual(list(group),["require","or"])
        self.assertEqual(group["require"],"at_least_one_exists_and_all_match")
        self.assertEqual(len(group["or"]),2)
        self.assertEqual(list(group["or"][0]["fields"]),["type","value"])
        self.assertEqual(group["or"][0]["fields"]["value"]["equals"],"Enterprise")
        self.assertEqual(group["or"][1]["fields"]["value"]["equals"],"EnterpriseS")
        self.assertEqual(new["assessment"]["evaluate"],source["assessment"]["evaluate"])
        self.assertTrue(exact_inverse(source,new,ledger))

    def test_mutated_or_branches_or_field_requirements_rejected(self):
        source=source_fixture()
        new,proof=preview(source)
        for mutate in (
            lambda t:t["require"]["all_items_must"][0]["or"][0]["fields"]["value"].update(equals="Education"),
            lambda t:t["require"]["all_items_must"][0].update(require="none_exist"),
            lambda t:t["require"]["all_items_must"][0].update(and=t["require"]["all_items_must"][0].pop("or")),
            lambda t:t["require"].update(items="may_be_absent"),
        ):
            corrupt=deepcopy(new)
            t=corrupt["assessment"]["tests"]["editionid-enterprise-or-enterprises-test"]
            with self.subTest(mutate=str(mutate)),self.assertRaises(ValueError):
                mutate(t)
                restore(corrupt,proof)

    def test_do_not_flatten_complete_states_to_individual_field_or(self):
        source=source_fixture()
        altered=deepcopy(source)
        t=altered["assessment"]["tests"]["editionid-enterprise-or-enterprises-test"]
        t["require"]["all_items_must"]=[{"or":[
            {"type":{"equals":"string"}},{"value":{"equals":"Enterprise"}},
            {"type":{"equals":"string"}},{"value":{"equals":"EnterpriseS"}}]}]
        with self.assertRaisesRegex(ValueError,"complete States"):
            preview(altered)

    def test_absent_or_changed_shared_field_requirement_is_not_guessed(self):
        for change in ("none_exist",None):
            a=source_fixture()
            t=a["assessment"]["tests"]["editionid-enterprise-or-enterprises-test"]
            if change is None:t.pop("state_fields_require")
            else:t["state_fields_require"]=change
            with self.assertRaises(ValueError):
                preview(a)

    def test_input_not_from_pinned_original_real_rule_is_rejected(self):
        a=source_fixture()
        a["assessment"]["id"]="SV-253260.automated"
        with self.assertRaises(ValueError):preview(a)


if __name__=="__main__":
    unittest.main()
