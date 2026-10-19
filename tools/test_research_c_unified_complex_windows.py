#!/usr/bin/env python3
"""Refs #245: unified C compiler routes source-backed complex Windows records.

It is an integration gate for an existing narrowly pinned record compiler.
It does not claim arbitrary WMI records, live scanner results or XML parity.
"""
from copy import deepcopy
from itertools import product
import json
from pathlib import Path
import sys
import unittest

from jsonschema import Draft202012Validator
import yaml

sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_c_require_language import parse_c_yaml
from research_c_unified_compiler import compile_c_unified,evaluate_c_unified_supplied_results
from research_c_windows_shared_native import compile_native_c_windows
from research_c_windows_shared_observations import CHECKS
from research_c_common_evaluation import SIX
from v04_a_truth_plan_source_oracle import source_expected_outcome

ROOT=Path(__file__).resolve().parents[1]
C=ROOT/"research/assessment-simplification/compact-authoring-04/c-source-exact-windows-rdp-rights.research.yaml"
SOURCE=ROOT/"research/requirements-first-language/contract-candidate/corpus/source-specimens/windows-userright-1-39dad4df5336.source.yaml"

class ComplexWindowsUnifiedCompiler(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c=parse_c_yaml(C.read_text())
        cls.compiled=compile_c_unified(cls.c)
        cls.special=compile_native_c_windows(cls.c)
        cls.source=yaml.safe_load(SOURCE.read_text())["assessment"]

    def test_seven_real_tests_share_exact_two_native_objects(self):
        c=self.compiled
        self.assertEqual(c["stage"],"C_RESEARCH_UNIFIED_A_COMPILER_NO_SCANNER")
        self.assertEqual(c["record_support"],"PINNED_WINDOWS_SEVEN_CHECK_FAMILY_ONLY")
        self.assertEqual(len(c["shared_objects"]),2)
        self.assertEqual(len(c["tests"]),7)
        self.assertEqual(c["shared_singletons"],{})
        self.assertFalse(c["scanner_executed"])
        self.assertFalse(c["source_parity_verified"])
        self.assertFalse(c["runtime_acquisition_sharing_verified"])
        self.assertEqual(c["shared_objects"],self.special["shared_objects"])
        self.assertEqual(c["source_test_provenance"],CHECKS)
        for alias,test in c["tests"].items():
            self.assertEqual(test,self.special["tests"][CHECKS[alias]])
            self.assertEqual(c["checks"][alias]["test"],test)
            self.assertFalse(c["checks"][alias]["independent_collection_plan"])

    def test_one_frontend_still_compiles_a_schema_valid_native_A_test_set(self):
        schema=json.loads((ROOT/"schema/v0.4.0/assessment-language.schema.json").read_text())
        Draft202012Validator(schema).validate({
            "assessment":{"tests":self.compiled["tests"]}})
        self.assertEqual(
            self.compiled["tests"]["domain_joined_non_dc"]["states_match"],
            "any")

    def test_seven_test_boolean_truth_parity_against_original_source(self):
        for states in product(("true","false"),repeat=7):
            values=dict(zip(CHECKS,states))
            source_leaf={CHECKS[key]:value for key,value in values.items()}
            expected=source_expected_outcome(self.source["evaluate"],source_leaf,{})
            got=evaluate_c_unified_supplied_results(
                self.compiled,checks=values)
            with self.subTest(leaves=values):
                self.assertEqual(got["outcome"],expected)

    def test_six_state_mixed_and_decisive_branches(self):
        for key in CHECKS:
            for status in sorted(SIX):
                values={name:"true" for name in CHECKS}
                values[key]=status
                expected=source_expected_outcome(
                    self.source["evaluate"],
                    {CHECKS[k]:v for k,v in values.items()}, {})
                got=evaluate_c_unified_supplied_results(
                    self.compiled,checks=values)
                with self.subTest(check=key,status=status):
                    self.assertEqual(got["outcome"],expected)

    def test_input_not_modified_and_no_original_source_document_required(self):
        original=deepcopy(self.c)
        plan=compile_c_unified(self.c)
        self.assertEqual(self.c,original)
        self.assertEqual(plan,self.compiled)
        with self.assertRaisesRegex(ValueError,"needs no legacy source"):
            compile_c_unified(self.c,source_documents={"domain_joined_non_dc":{}})

    def test_unsupported_WMI_record_shapes_fail_closed(self):
        for alteration in (
            lambda a:a["checks"]["domain_joined_non_dc"]["must"].update(
                field_requirement="at_least_one_exists_and_some_match"),
            lambda a:a["checks"]["deny_guests"]["must"].update(
                same_item_field="unrelated_parent"),
            lambda a:a["checks"]["domain_joined_non_dc"]["must"].update(
                any_record_state_every_value_equals=["1","3","4"]),
            lambda a:a["observations"]["system_role"]["from"][
                "windows.wmi.query"].update(query="SELECT OS FROM win32_computersystem"),
        ):
            doc=deepcopy(self.c)
            alteration(doc)
            with self.subTest(alteration=str(alteration)):
                with self.assertRaises(ValueError):
                    compile_c_unified(doc)

    def test_outside_pinned_record_family_is_not_auto_supported(self):
        doc=deepcopy(self.c)
        doc["checks"]["invented_extra"]={
            "observation":"denied_remote_logon_trustees",
            "source_test":"invented-test",
            "must":deepcopy(doc["checks"]["deny_guests"]["must"])}
        doc["require"]["one_of"].append({"check":"invented_extra"})
        with self.assertRaisesRegex(ValueError,"unsupported source-independent C Windows composition"):
            compile_c_unified(doc)

if __name__=="__main__":
    unittest.main()
