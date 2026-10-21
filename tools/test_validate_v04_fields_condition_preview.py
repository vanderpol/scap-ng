#!/usr/bin/env python3
"""Scoped expected-condition fields naming: no hidden requirement defaults."""
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest
from jsonschema import Draft202012Validator

from validate_v04_fields_condition_preview import candidate_schema,field_scopes


def fixture(*,scope="local"):
    condition={"fields":{"type":{"equals":"dword"},"value":{"equals":0}}}
    if scope=="local":
        condition={"require":"at_least_one_exists_and_all_match",**condition}
    if scope=="own":
        condition["fields"]["type"]["require"]="at_least_one_exists_and_all_match"
        condition["fields"]["value"]["require"]="at_least_one_exists_and_all_match"
    test={"require":{"items":"one_or_more","all_items_must":[condition]}}
    if scope=="inherited":
        test["state_fields_require"]="at_least_one_exists_and_all_match"
    return test


class ProposedFieldsScopeTests(unittest.TestCase):
    def test_local_inherited_and_per_field_are_distinct_declared_scopes(self):
        for mode,expected in (("local","local"),("inherited","inherited"),
                              ("own","each_field")):
            with self.subTest(mode=mode):
                report=field_scopes(fixture(scope=mode))
                self.assertEqual(len(report),1)
                self.assertEqual(report[0]["scope"],expected)
                self.assertEqual(report[0]["fields"],["type","value"])

    def test_missing_field_scope_is_rejected_instead_of_defaulting(self):
        with self.assertRaisesRegex(ValueError,"missing explicit or inherited"):
            field_scopes(fixture(scope="none"))

    def test_each_field_override_remains_explicit(self):
        doc=fixture()
        doc["require"]["all_items_must"][0]["fields"]["value"]["require"]="none_exist"
        self.assertEqual(field_scopes(doc)[0]["scope"],"local")
        self.assertEqual(doc["require"]["items"],"one_or_more")
        self.assertEqual(doc["require"]["all_items_must"][0]["fields"]["value"]["require"],
                         "none_exist")

    def test_nested_or_preserves_two_complete_original_state_boundaries(self):
        left=fixture()["require"]["all_items_must"][0]
        right=deepcopy(left)
        right["fields"]["value"]["equals"]=1
        doc={"state_fields_require":"all_exist_and_all_match",
             "require":{"items":"one_or_more","all_items_must":[
                 {"or":[left,right]}]}}
        scopes=field_scopes(doc)
        self.assertEqual(len(scopes),2)
        self.assertEqual([s["scope"] for s in scopes],["local","local"])
        self.assertEqual(doc["require"]["items"],"one_or_more")

    def test_record_fields_are_not_scalar_fields(self):
        test=fixture()
        test["require"]["all_items_must"][0]["fields"]["type"]={
            "record":{"require":"all_exist_and_all_match",
                      "fields":{"name":{"equals":"A","require":"none_exist"}}}}
        with self.assertRaisesRegex(ValueError,"Record cardinality"):
            field_scopes(test)

    def test_shared_requirement_can_precede_or_alternatives_once(self):
        doc=fixture(scope="inherited")
        base=doc["require"]["all_items_must"][0]
        alternate=deepcopy(base)
        alternate["fields"]["value"]["equals"]=1
        doc.pop("state_fields_require")
        doc["require"]["all_items_must"]=[{
            "require":"at_least_one_exists_and_all_match",
            "or":[base,alternate]}]
        scopes=field_scopes(doc)
        self.assertEqual(len(scopes),2)
        self.assertEqual([s["scope"] for s in scopes],["inherited","inherited"])
        self.assertEqual(doc["require"]["items"],"one_or_more")

    def test_one_field_or_mixed_logical_operator_not_in_safe_subset(self):
        test=fixture()
        test["require"]["all_items_must"][0]["or"]=[{"type":{"equals":"dword"}}]
        with self.assertRaisesRegex(ValueError,"Ambiguous fields"):
            field_scopes(test)
        test=fixture()
        test["require"]["all_items_must"][0]["fields"].pop("type")
        with self.assertRaisesRegex(ValueError,"two-or-more"):
            field_scopes(test)

    def test_isolated_candidate_schema_does_not_modify_active_schema(self):
        root=Path(__file__).resolve().parents[1]
        active=(root/"schema/v0.4.0/assessment-language.schema.json").read_bytes()
        with TemporaryDirectory() as td:
            proposal=candidate_schema(Path(td)/"v0.4.0")
            d=json.loads((proposal/"assessment-language.schema.json").read_text())
            good=fixture()["require"]["all_items_must"][0]
            for scope in ("scoped_state_entry","state_entry"):
                v=Draft202012Validator({
                    "$ref":"#/$defs/"+scope,
                    "$defs":d["$defs"],
                })
                self.assertEqual(list(v.iter_errors(good)),[],scope)
                bad=deepcopy(good)
                bad["or"]=[{"value":{"equals":0}}]
                self.assertTrue(list(v.iter_errors(bad)),scope)
                self.assertTrue(list(v.iter_errors({"fields":{}})),scope)
                shared={"require":"at_least_one_exists_and_all_match",
                        "or":[{"fields":{"type":{"equals":"string"},
                                          "value":{"equals":0}}},
                              {"fields":{"type":{"equals":"dword"},
                                          "value":{"equals":1}}}]}
                self.assertFalse(list(v.iter_errors(shared)),scope)
                mixed=deepcopy(shared)
                mixed["state_fields_require"]="none_exist"
                self.assertTrue(list(v.iter_errors(mixed)),scope)
        self.assertEqual(active,(root/"schema/v0.4.0/assessment-language.schema.json").read_bytes())


    def test_uniform_field_requirement_has_explicit_test_local_and_leaf_scope(self):
        shared=fixture(scope="none")
        shared["require"]["field_requirement"]="at_least_one_exists_and_all_match"
        condition=shared["require"]["all_items_must"][0]
        self.assertEqual(field_scopes(shared)[0]["scope"],"inherited")
        condition["field_requirement"]="may_be_absent_and_all_match"
        self.assertEqual(field_scopes(shared)[0]["scope"],"local")
        condition["fields"]["value"]["field_requirement"]="none_exist"
        self.assertEqual(field_scopes(shared)[0]["scope"],"local")
        self.assertEqual(condition["fields"]["value"]["field_requirement"],"none_exist")
        self.assertEqual(shared["require"]["items"],"one_or_more")
        self.assertNotIn("state_fields_require",shared)

    def test_uniform_test_field_requirement_inherits_across_complete_or_branches(self):
        doc=fixture(scope="none")
        doc["require"]["field_requirement"]="at_least_one_exists_and_all_match"
        first=doc["require"]["all_items_must"][0]
        second=deepcopy(first)
        second["fields"]["value"]["equals"]=1
        second["field_requirement"]="may_be_absent_and_all_match"
        doc["require"]["all_items_must"]=[{"or":[first,second]}]
        sites=field_scopes(doc)
        self.assertEqual([site["scope"] for site in sites],["inherited","local"])
        self.assertEqual(doc["require"]["items"],"one_or_more")
        # A policy on the nearest complete condition cannot change its sibling.
        doc["require"]["all_items_must"][0]["or"][0]["fields"]["value"][
            "field_requirement"]="none_exist"
        self.assertEqual([site["scope"] for site in field_scopes(doc)],
                         ["inherited","local"])

    def test_uniform_scope_conflicts_and_missing_policy_fail_closed(self):
        missing=fixture(scope="none")
        with self.assertRaisesRegex(ValueError,"missing explicit or inherited"):
            field_scopes(missing)
        legacy=fixture(scope="inherited")
        legacy["require"]["field_requirement"]="none_exist"
        with self.assertRaisesRegex(ValueError,"Conflicting legacy"):
            field_scopes(legacy)
        mixed=fixture(scope="local")
        mixed["require"]["all_items_must"][0]["field_requirement"]="none_exist"
        with self.assertRaisesRegex(ValueError,"Ambiguous fields"):
            field_scopes(mixed)
        leaf=fixture(scope="own")
        leaf["require"]["all_items_must"][0]["fields"]["type"][
            "field_requirement"]="none_exist"
        with self.assertRaisesRegex(ValueError,"Conflicting field-level"):
            field_scopes(leaf)
        nested=fixture(scope="none")
        nested["require"]["all_items_must"]=[{
            "field_requirement":"all_exist_and_all_match",
            "require":"none_exist",
            "or":[fixture(scope="none")["require"]["all_items_must"][0]]
        }]
        with self.assertRaisesRegex(ValueError,"Ambiguous nested"):
            field_scopes(nested)

    def test_isolated_uniform_schema_accepts_valid_scopes_and_rejects_alias_mix(self):
        with TemporaryDirectory() as td:
            proposal=candidate_schema(Path(td)/"v0.4.0")
            d=json.loads((proposal/"assessment-language.schema.json").read_text())
            leaf=d["$defs"]["inherited_field_predicate"]
            self.assertIn("field_requirement",leaf["properties"])
            for definition in ("all_items_requirement","scoped_all_items_requirement"):
                self.assertIn("field_requirement",d["$defs"][definition]["properties"])
            for shape in ("state_entry","scoped_state_entry"):
                v=Draft202012Validator({"$ref":"#/$defs/"+shape,"$defs":d["$defs"]})
                good={"field_requirement":"at_least_one_exists_and_all_match",
                      "fields":{"type":{"equals":"string"},
                                "value":{"equals":0,
                                         "field_requirement":"none_exist"}}}
                self.assertEqual(list(v.iter_errors(good)),[],shape)
                for bad in (
                    {**good,"require":"none_exist"},
                    {**good,"or":[{"value":{"equals":0}}]},
                    {"field_requirement":"none_exist",
                     "fields":{"type":{"equals":"string"}}},
                    {"fields":{"type":{"equals":"string","require":"none_exist",
                                      "field_requirement":"none_exist"},
                               "value":{"equals":0}}}
                ):
                    self.assertTrue(list(v.iter_errors(bad)),(shape,bad))
            v=Draft202012Validator({"$ref":"#/$defs/all_items_requirement",
                                    "$defs":d["$defs"]})
            self.assertFalse(list(v.iter_errors(
                {"items":"one_or_more",
                 "field_requirement":"at_least_one_exists_and_all_match",
                 "all_items_must":[{"field_requirement":"may_be_absent_and_all_match",
                                    "fields":{"type":{"equals":"string"},
                                              "value":{"equals":0}}}]})))
            self.assertTrue(list(v.iter_errors(
                {"items":"one_or_more","field_requirement":"typo",
                 "all_items_must":[{"fields":{"type":{"equals":"string"},
                                               "value":{"equals":0}}}]})))


if __name__=="__main__":
    unittest.main()
