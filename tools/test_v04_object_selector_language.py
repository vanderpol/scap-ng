#!/usr/bin/env python3
"""SCAP-NG 0.4 pre-alpha Object selectors must use the ONE authoring grammar.

Test both the standalone Object predicate and its embedding in the real
version-local full Assessment schema. Selection cardinality value_match is
independent of Test/State require; Organizational Input is not Object selector.
"""
from copy import deepcopy
import unittest
from test_v04_schema_draft import (
    SCHEMAS, VALIDATOR, fixture, errors,
    Draft202012Validator, RefResolver,
)

COMMON = SCHEMAS["capability-common.schema.json"]
LANGUAGE = SCHEMAS["assessment-language.schema.json"]
STORE = {schema["$id"]: schema for schema in SCHEMAS.values()}
SELECTOR = Draft202012Validator(
    {"$ref": COMMON["$id"] + "#/$defs/object_entity_base"},
    resolver=RefResolver.from_schema(COMMON, store=STORE),
)


def assessment_with_directory(predicate):
    doc = fixture(requirement="at_least_one_exists")
    doc["assessment"]["tests"]["demo-test"]["object"] = {
        "capability": "unix.file",
        "select": {"directory": predicate},
    }
    return doc


class V04ObjectSelectorTests(unittest.TestCase):
    def valid(self, pred):
        return not list(SELECTOR.iter_errors(pred))

    def test_versioned_selector_contract_is_local(self):
        self.assertEqual(
            COMMON["$defs"]["object_entity_base"]["$ref"],
            "assessment-language.schema.json#/$defs/object_selector_predicate",
        )
        self.assertIn("object_selector_predicate", LANGUAGE["$defs"])

    def test_scalar_selector_works_in_complete_assessment(self):
        for key, value in [
            ("equals", "/etc/passwd"),
            ("matches_regex", r"^/etc/.*"),
            ("version_greater_than", "1.0"),
        ]:
            with self.subTest(key=key):
                pred = {key: value}
                self.assertTrue(self.valid(pred))
                self.assertFalse(errors(assessment_with_directory(pred)))

    def test_array_with_explicit_independent_value_match(self):
        pred = {
            "equals": ["/lib", "/lib64", "/usr/lib"],
            "value_match": "one",
            "datatype": "string",
        }
        self.assertTrue(self.valid(pred))
        self.assertFalse(errors(assessment_with_directory(pred)))
        removed = deepcopy(pred)
        del removed["value_match"]
        self.assertFalse(self.valid(removed))
        self.assertTrue(errors(assessment_with_directory(removed)))

    def test_variable_requires_explicit_value_match(self):
        pred = {
            "equals": {"variable": "package-directories-variable"},
            "value_match": "one_or_more",
            "datatype": "string",
        }
        self.assertTrue(self.valid(pred))
        self.assertFalse(errors(assessment_with_directory(pred)))
        del pred["value_match"]
        self.assertFalse(self.valid(pred))
        self.assertTrue(errors(assessment_with_directory(pred)))

    def test_object_selectors_reject_organizational_input(self):
        pred = {
            "equals": {"input": "organization-file-input"},
            "datatype": "string",
            "value_match": "all",
        }
        self.assertFalse(self.valid(pred))
        self.assertTrue(errors(assessment_with_directory(pred)))

    def test_object_selectors_reject_state_requirement(self):
        for predicate in (
            {"equals": "/etc/passwd", "require": "at_least_one_exists_and_all_match"},
            {"equals": "/etc/passwd", "existence": "one_or_more", "match": "all"},
            {"equals": "/etc/passwd", "selection_match": "all"},
        ):
            with self.subTest(predicate=predicate):
                self.assertFalse(self.valid(predicate))
                self.assertTrue(errors(assessment_with_directory(predicate)))

    def test_legacy_object_selectors_no_longer_valid(self):
        for predicate in (
            {"value": "/etc/passwd", "operation": "equals"},
            {"value": ["/lib", "/lib64"], "operation": "equals", "value_match": "one"},
            {"equals": "/etc/passwd", "operation": "equals"},
        ):
            with self.subTest(predicate=predicate):
                self.assertFalse(self.valid(predicate))
                self.assertTrue(errors(assessment_with_directory(predicate)))

    def test_no_hidden_comparator_or_multiple_operator_choices(self):
        for predicate in (
            {"datatype": "string"},
            {"value_match": "one"},
            {"equals": "/tmp", "not_equal": "/var"},
            {"equals": "/tmp", "matches_regex": ".*"},
            {"equals": ["/tmp", "/var"], "value_match": "one", "require": "none_exist"},
            {"equals": "/tmp", "value_match": "one"},
        ):
            with self.subTest(predicate=predicate):
                self.assertFalse(self.valid(predicate))
                self.assertTrue(errors(assessment_with_directory(predicate)))

    def test_collector_record_field_has_independent_selection_match(self):
        collector=Draft202012Validator(
            {"$id":COMMON["$id"],"$defs":COMMON["$defs"],
             "$ref":"#/$defs/object_record_field"},
            resolver=RefResolver.from_schema(COMMON,store=STORE),
        )
        good={"equals":"tpmpresent,tpmready","selection_match":"all"}
        self.assertFalse(list(collector.iter_errors(good)))
        for broken in (
            {"equals":"tpmpresent,tpmready"},
            {"equals":"tpmpresent","match":"all"},
            {"equals":"tpmpresent","selection_match":"all","require":"none_exist"},
            {"value":"tpmpresent","operation":"equals","selection_match":"all"},
            {"equals":"tpmpresent","selection_match":"all",
             "not_equal":"tpmready"},
        ):
            with self.subTest(broken=broken):
                self.assertTrue(list(collector.iter_errors(broken)))

    def test_nullable_named_selector_and_correlated_binding_have_explicit_shapes(self):
        named=assessment_with_directory({"equals":"/etc/audit"})
        obj=named["assessment"]["tests"]["demo-test"]["object"]
        obj["select"]["name"]=None
        self.assertFalse(errors(named))

        foreach=assessment_with_directory({"from":"item.directory"})
        obj=foreach["assessment"]["tests"]["demo-test"]["object"]
        obj["for_each"]={"item":"item","in":"directories-object"}
        obj["select"]["name"]={"matches_regex":".*"}
        self.assertFalse(errors(foreach))

        for bad in (
            {"directory":None,"name":{"equals":"config"}},
            {"directory":{"equals":"/etc"},"not_a_name":None},
            {"directory":{"from":"not-a-lineage-binding"},"name":None},
            {"directory":{"input":"unknown-input"},"name":None},
        ):
            with self.subTest(bad=bad):
                doc=assessment_with_directory({"equals":"/etc"})
                doc["assessment"]["tests"]["demo-test"]["object"]["select"]=bad
                self.assertTrue(errors(doc))

    def test_native_object_without_select_remains_possible(self):
        # Native collectors can have capability-specific sources other than
        # select (e.g. Variable/cmdlet). This test does not validate them;
        # separate generated capability schemas must close those alternatives.
        doc = fixture(requirement="at_least_one_exists")
        doc["assessment"]["tests"]["demo-test"]["object"] = {"capability": "unix.file"}
        self.assertFalse(errors(doc))


if __name__ == "__main__":
    unittest.main()
