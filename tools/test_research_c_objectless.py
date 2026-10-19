#!/usr/bin/env python3
"""Refs #245: real objectless A capability contracts through one C frontend."""
from copy import deepcopy
from itertools import product
import json
from pathlib import Path
import sys
import unittest
from jsonschema import Draft202012Validator

sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_c_require_language import compile_c_requirement,parse_c_yaml
from research_c_unified_compiler import compile_c_unified,evaluate_c_unified_supplied_results
from v04_a_truth_plan_source_oracle import source_expected_outcome
from research_c_common_evaluation import SIX

ROOT=Path(__file__).resolve().parents[1]
SAMPLE=ROOT/("research/assessment-simplification/compact-authoring-04/"
             "c-windows-objectless-policy.research.yaml")

class ObjectlessSources(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document=parse_c_yaml(SAMPLE.read_text(encoding="utf-8"))
        cls.plan=compile_c_unified(cls.document)
        cls.schema=json.loads((ROOT/"schema/v0.4.0/assessment-language.schema.json").read_text())

    def test_three_objectless_native_sources_compile_without_fake_objects(self):
        self.assertEqual(self.plan["shared_objects"],{})
        self.assertEqual(len(self.plan["tests"]),3)
        self.assertEqual(self.plan["source_compatibility_inputs"],[])
        self.assertFalse(self.plan["scanner_executed"])
        self.assertFalse(self.plan["source_parity_verified"])
        for test in self.plan["tests"].values():
            self.assertNotIn("object",test)
            self.assertEqual(test["require"],"at_least_one_exists_and_all_match")
            self.assertEqual(len(test["states"]),1)
        Draft202012Validator(self.schema).validate(
            {"assessment":{"tests":self.plan["tests"]}})

    def test_real_pinned_state_fields_and_integer_operator(self):
        a=self.plan["tests"]["operating_system_is_windows"]
        b=self.plan["tests"]["password_history_at_least_24"]
        c=self.plan["tests"]["audit_file_share_success_failure"]
        self.assertEqual(a["states"],[
            {"family":{"require":"at_least_one_exists_and_all_match","equals":"windows"}}])
        self.assertEqual(b["states"],[
            {"password_hist_len":{"require":"at_least_one_exists_and_all_match",
                                   "greater_than_or_equal":24}}])
        self.assertEqual(c["states"],[
            {"file_share":{"require":"at_least_one_exists_and_all_match",
                           "equals":"AUDIT_SUCCESS_FAILURE"}}])

    def test_full_six_state_triples_share_existing_A_expression_engine(self):
        expr={"all":[{"test":key} for key in self.document["checks"]]}
        for values in product(sorted(SIX),repeat=3):
            leaves=dict(zip(self.document["checks"],values))
            expected=source_expected_outcome(expr,leaves,{})
            actual=evaluate_c_unified_supplied_results(self.plan,checks=leaves)
            with self.subTest(leaves=leaves):
                self.assertEqual(actual["outcome"],expected)

    def test_pinned_mapping_rejects_source_parameters_for_singleton(self):
        document=deepcopy(self.document)
        document["checks"]["operating_system_is_windows"]["from"][
            "independent.family"]={"name":"invented-family-source"}
        with self.assertRaisesRegex(ValueError,"objectless"):
            compile_c_unified(document)
        self.assertNotIn("object",self.plan["tests"]["operating_system_is_windows"])

    def test_invalid_family_enum_is_rejected(self):
        document=deepcopy(self.document)
        document["checks"]["operating_system_is_windows"]["must"][
            "every_item"]["family"]="nonesuch"
        with self.assertRaisesRegex(ValueError,"pinned native State"):
            compile_c_unified(document)

    def test_bad_numeric_coercions_and_regex_on_integer_fail_closed(self):
        for changed in (
            {"greater_than_or_equal":"24"},
            {"greater_than_or_equal":True},
            {"matches_regex":".*"},
        ):
            document=deepcopy(self.document)
            document["checks"]["password_history_at_least_24"]["must"][
                "every_item"]["password_hist_len"]=changed
            with self.subTest(changed=changed),self.assertRaises(ValueError):
                compile_c_unified(document)

    def test_empty_parameter_map_not_allowed_for_selector_capabilities(self):
        requirement={"from":{"windows.registry":{}},
                     "must":{"every_item":{"type":"dword"}}}
        with self.assertRaisesRegex(ValueError,"selector fields"):
            compile_c_requirement(requirement)

    def test_unknown_field_rejected_before_claiming_native_valid(self):
        document=deepcopy(self.document)
        document["checks"]["audit_file_share_success_failure"]["must"][
            "every_item"]={"file_shar": "AUDIT_FAILURE"}
        with self.assertRaises(ValueError):
            compile_c_unified(document)

    def test_named_objectless_observations_do_not_create_fake_A_objects(self):
        doc=parse_c_yaml((ROOT/"research/assessment-simplification/compact-authoring-04/"
                          "c-shared-objectless-policy.research.yaml").read_text())
        old=deepcopy(doc)
        plan=compile_c_unified(doc)
        self.assertEqual(doc,old)
        self.assertEqual(plan["shared_objects"],{})
        self.assertEqual(len(plan["tests"]),3)
        self.assertEqual(set(plan["shared_singletons"]),
                         {"system_family","windows_password_policy"})
        self.assertEqual(plan["shared_singletons"]["windows_password_policy"],{
            "capability":"windows.passwordpolicy",
            "consumer_tests":["password_history_24","password_complexity_enabled"]})
        self.assertEqual(plan["shared_singletons"]["system_family"]["consumer_tests"],
                         ["is_windows_family"])
        for test in plan["tests"].values():
            self.assertNotIn("object",test)
        for check in plan["checks"].values():
            self.assertNotIn("object",check["test"])
            self.assertFalse(check["independent_collection_plan"])
        self.assertFalse(plan["runtime_acquisition_sharing_verified"])
        Draft202012Validator(self.schema).validate(
            {"assessment":{"tests":plan["tests"]}})

    def test_named_objectless_shared_check_results_are_independent(self):
        doc=parse_c_yaml((ROOT/"research/assessment-simplification/compact-authoring-04/"
                          "c-shared-objectless-policy.research.yaml").read_text())
        plan=compile_c_unified(doc)
        expr={"all":[{"test":key} for key in doc["checks"]]}
        for values in product(sorted(SIX),repeat=3):
            supplied=dict(zip(doc["checks"],values))
            expected=source_expected_outcome(expr,supplied,{})
            actual=evaluate_c_unified_supplied_results(plan,checks=supplied)
            with self.subTest(values=values):
                self.assertEqual(actual["outcome"],expected)

    def test_fabricated_source_object_for_singleton_fails_closed(self):
        doc=parse_c_yaml((ROOT/"research/assessment-simplification/compact-authoring-04/"
                          "c-shared-objectless-policy.research.yaml").read_text())
        doc["observations"]["windows_password_policy"]["source_object"]="fake-object"
        with self.assertRaisesRegex(ValueError,"objectless observation"):
            compile_c_unified(doc)

    def test_shared_singleton_rejects_unsupported_parameters_and_types(self):
        doc=parse_c_yaml((ROOT/"research/assessment-simplification/compact-authoring-04/"
                          "c-shared-objectless-policy.research.yaml").read_text())
        doc["observations"]["windows_password_policy"]["from"]["windows.passwordpolicy"]={
            "invented_parameter":"no"}
        with self.assertRaisesRegex(ValueError,"objectless"):
            compile_c_unified(doc)
        doc=parse_c_yaml((ROOT/"research/assessment-simplification/compact-authoring-04/"
                          "c-shared-objectless-policy.research.yaml").read_text())
        doc["checks"]["password_complexity_enabled"]["must"]["every_item"][
            "password_complexity"]="true"
        with self.assertRaisesRegex(ValueError,"string value incompatible"):
            compile_c_unified(doc)

    def test_no_mutation_of_parsed_C_input(self):
        d=deepcopy(self.document)
        compile_c_unified(self.document)
        self.assertEqual(self.document,d)

if __name__=="__main__":
    unittest.main()
