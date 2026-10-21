#!/usr/bin/env python3
"""Explicit 0.4 field-scope inheritance, exceptions and source parity tests."""
import unittest
from copy import deepcopy

from audit_v04_scoped_field_require import expand,assert_equivalent


def base():
    return {"capability":"windows.registry",
            "require":{"items":"one_or_more","all_items_must":[{
                "and":[{"type":{"equals":"dword"}},
                       {"value":{"equals":0}}],
                "state_fields_require":"at_least_one_exists_and_all_match"}]}}


class ScopedFieldTests(unittest.TestCase):
    def test_single_group_requirement_applies_to_all_scalar_fields(self):
        prior=base()
        expanded,ledger=expand(prior)
        entry=expanded["require"]["all_items_must"][0]
        self.assertEqual(list(entry),["and"])
        self.assertEqual([c[next(iter(c))]["require"] for c in entry["and"]],
                         ["at_least_one_exists_and_all_match"]*2)
        self.assertEqual(expanded["require"]["items"],"one_or_more")
        self.assertEqual(assert_equivalent(prior,expanded)["inherited_scalar_fields"],2)
        self.assertNotIn("state_fields_require",entry)

    def test_test_scope_applies_across_alternative_states(self):
        src={"require":{"items":"may_be_absent","all_items_must":[
                {"or":[{"type":{"equals":"string"}},{"value":{"equals":"Enterprise"}}]},
                {"value":{"equals":"EnterpriseS"}}]},
             "state_fields_require":"at_least_one_exists_and_all_match"}
        expanded,ledger=expand(src)
        self.assertEqual(len(ledger),3)
        self.assertEqual(expanded["require"]["items"],"may_be_absent")
        self.assertNotIn("state_fields_require",expanded)
        self.assertTrue(all(x["effective_requirement"]=="at_least_one_exists_and_all_match"
                            for x in ledger))

    def test_field_exception_for_absent_stderr_does_not_change_item_existence(self):
        src={"require":{"items":"one_or_more","all_items_must":[{
            "and":[{"stdout_line":{"matches_regex":"^OK"}},
                   {"exit_status":{"equals":0}},
                   {"stderr_line":{"equals":"","require":"none_exist"}}],
            "state_fields_require":"at_least_one_exists_and_all_match"}]}}
        expanded,ledger=expand(src)
        group=expanded["require"]["all_items_must"][0]["and"]
        self.assertEqual(group[2]["stderr_line"]["require"],"none_exist")
        self.assertEqual([g[next(iter(g))]["require"] for g in group[:2]],
                         ["at_least_one_exists_and_all_match"]*2)
        self.assertEqual(assert_equivalent(src,expanded)["field_overrides"],1)
        self.assertEqual(expanded["require"]["items"],"one_or_more")

    def test_nearest_nested_group_explicit_override(self):
        src={"state_fields_require":"at_least_one_exists_and_all_match",
             "require":{"items":"one_or_more","all_items_must":[{
                 "and":[{"type":{"equals":"dword"}},
                        {"or":[{"value":{"equals":"unexpected"}},
                               {"status":{"equals":"missing"}}],
                         "state_fields_require":"none_exist"}]}]}}
        expanded,ledger=expand(src)
        a=expanded["require"]["all_items_must"][0]["and"]
        self.assertEqual(a[0]["type"]["require"],"at_least_one_exists_and_all_match")
        self.assertTrue(all(v[next(iter(v))]["require"]=="none_exist"
                            for v in a[1]["or"]))
        self.assertEqual(len(ledger),3)

    def test_record_and_record_subfield_requirements_do_not_inherit_scalar_scope(self):
        record={"record":{"require":"at_least_one_exists_and_all_match",
            "fields":{"name":{"equals":"A","require":"only_one_exists_and_matches"},
                      "status":{"equals":0,"require":"none_exist"}}}}
        src={"state_fields_require":"all_exist_and_all_match",
             "require":{"items":"one_or_more","all_items_must":[
                 {"record_field":record},{"owner_uid":{"equals":0}}]}}
        expanded,ledger=expand(src)
        self.assertEqual(expanded["require"]["all_items_must"][0]["record_field"],record)
        self.assertEqual(expanded["require"]["all_items_must"][1]["owner_uid"]["require"],
                         "all_exist_and_all_match")
        self.assertEqual(assert_equivalent(src,expanded)["record_fields_not_inherited"],1)

    def test_missing_scope_cannot_silently_default(self):
        src={"require":{"items":"one_or_more","all_items_must":[
            {"and":[{"value":{"equals":0}}]}]}}
        with self.assertRaisesRegex(ValueError,"no explicit State-field requirement|missing"):
            expand(src)

    def test_missing_record_cardinality_cannot_use_outer_scope(self):
        src={"state_fields_require":"at_least_one_exists_and_all_match",
             "require":{"items":"one_or_more","all_items_must":[
                 {"record_field":{"record":{"fields":{"a":{"equals":"A"}}}}}]}}
        with self.assertRaisesRegex(ValueError,"record-level requirement"):
            expand(src)

    def test_no_source_state_predicate_can_change_in_exact_inversion(self):
        src=base()
        expanded,_=expand(src)
        mutated=deepcopy(expanded)
        mutated["require"]["all_items_must"][0]["and"][1]["value"]["require"]="none_exist"
        with self.assertRaisesRegex(ValueError,"Expanded State"):
            assert_equivalent(src,mutated)

    def test_legacy_test_states_inherit_explicit_test_scope(self):
        src={"require":"at_least_one_exists_and_some_match",
             "state_fields_require":"at_least_one_exists_and_all_match",
             "states":[{"value":{"equals":"good"}},{"name":{"equals":"test"}}],
             "states_match":"any"}
        expanded,ledger=expand(src)
        self.assertEqual(len(ledger),2)
        self.assertEqual(expanded["states_match"],"any")
        self.assertEqual(expanded["require"],"at_least_one_exists_and_some_match")


if __name__=="__main__":
    unittest.main()
