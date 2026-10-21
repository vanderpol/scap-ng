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
        self.assertEqual(active,(root/"schema/v0.4.0/assessment-language.schema.json").read_bytes())


if __name__=="__main__":
    unittest.main()
