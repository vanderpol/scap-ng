#!/usr/bin/env python3
"""Refs #245: bounded C-to-A Windows source-independent Test/record compiler."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest
import yaml
from jsonschema import Draft202012Validator

sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_c_windows_shared_native import compile_native_c_windows
from research_c_windows_shared_observations import (
    present_windows_shared_observations, CHECKS
)
from research_c_require_language import parse_c_yaml

ROOT=Path(__file__).resolve().parents[1]
C=ROOT/("research/assessment-simplification/compact-authoring-04/"
        "c-source-exact-windows-rdp-rights.research.yaml")
SOURCE=ROOT/("research/requirements-first-language/contract-candidate/"
             "corpus/source-specimens/windows-userright-1-39dad4df5336.source.yaml")
SCHEMA=ROOT/"schema/v0.4.0/assessment-language.schema.json"

class WindowsNativeCompilation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # This compiler consumes C alone. Original 0.3 Assessment is not an
        # input to compilation; it is opened only for independent comparison.
        cls.c=parse_c_yaml(C.read_text(encoding="utf-8"))
        cls.plan=compile_native_c_windows(cls.c)
        cls.original=yaml.safe_load(SOURCE.read_text(encoding="utf-8"))["assessment"]

    def test_source_independent_native_a_test_coverage(self):
        a=self.plan
        self.assertFalse(a["source_document_required"])
        self.assertFalse(a["runtime_collectors_implemented"])
        self.assertFalse(a["original_source_parity_verified"])
        self.assertFalse(a["scan_result_authoritative"])
        self.assertEqual(a["native_specification"],"0.4.0")
        self.assertEqual(set(a["shared_objects"]),set(self.original["shared_objects"]))
        self.assertEqual(set(a["tests"]),set(self.original["tests"]))
        self.assertEqual(a["evaluate"],self.original["evaluate"])

    def test_compiled_native_04_a_states_pass_base_schema(self):
        schema=json.loads(SCHEMA.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate({"assessment":{"tests":self.plan["tests"]}})
        for t in self.plan["tests"].values():
            self.assertIn(t["require"],schema["$defs"]["paired_requirement"]["enum"])

    def test_reuse_same_native_collection_across_multiple_checks(self):
        sources=self.plan["shared_objects"]
        self.assertEqual(len(sources),2)
        uses=[test["object"] for test in self.plan["tests"].values()]
        self.assertEqual(uses.count("windows-userright-object"),5)
        self.assertEqual(uses.count("windows-wmi57-object"),2)
        self.assertEqual(
            sources["windows-userright-object"]["select"]["userright"]["equals"],
            "SE_DENY_REMOTE_INTERACTIVE_LOGON_NAME")
        self.assertEqual(
            sources["windows-wmi57-object"]["collect"]["query"],
            "SELECT DomainRole FROM win32_computersystem")

    def test_field_requirements_and_comparators_preserve_source_tokens(self):
        for test_id,source in self.original["tests"].items():
            output=self.plan["tests"][test_id]
            self.assertEqual(output["capability"],source["capability"])
            self.assertEqual(output["object"],source["object"])
            self.assertEqual(output["reported_elements"],source["reported_elements"])
            if source["capability"]=="windows.wmi.query":
                self.assertEqual(output["require"],
                                 "at_least_one_exists_and_all_match")
                self.assertEqual(output["states_match"],"any")
                self.assertEqual(len(output["states"]),2)
                for old,new in zip(source["states"],output["states"]):
                    self.assertEqual(new["result"]["record"]["require"],
                                     "at_least_one_exists_and_all_match")
                    self.assertEqual(
                        new["result"]["record"]["fields"]["domainrole"]["equals"],
                        old["record"]["fields"]["domainrole"]["value"])
            else:
                self.assertEqual(output["require"],
                                 "at_least_one_exists_and_some_match")
                original_state=source["states"][0]
                native_state=output["states"][0]["trustee_name"]
                expect=("matches_regex" if original_state["operation"]=="pattern_match"
                        else original_state["operation"])
                self.assertEqual(native_state[expect],original_state["value"])
                self.assertEqual(native_state["require"],
                                 "at_least_one_exists_and_all_match")

    def test_input_document_never_mutated(self):
        before=deepcopy(self.c)
        out=compile_native_c_windows(self.c)
        self.assertEqual(self.c,before)
        self.assertEqual(out,self.plan)

    def test_unapproved_fields_cardinalities_and_data_sources_fail_closed(self):
        changes=[
            lambda a:a["checks"]["standalone"]["must"].update(
                field_requirement="at_least_one_exists_and_some_match"),
            lambda a:a["checks"]["standalone"]["must"].update(
                any_record_state_every_value_equals=["0",2]),
            lambda a:a["checks"]["deny_guests"]["must"].update(items="every_item"),
            lambda a:a["checks"]["deny_guests"]["must"]["predicate"].update(
                unknown_comparator="Guests"),
            lambda a:a["observations"]["system_role"]["from"][
                "windows.wmi.query"].update(namespace=""),
            lambda a:a["observations"]["denied_remote_logon_trustees"]["from"][
                "windows.userright"].update(userright="NONEXISTENT_RIGHT"),
            lambda a:a["checks"]["deny_guests"].update(
                observation="unknown_observation"),
            lambda a:a["checks"]["deny_everyone"].update(
                source_test=CHECKS["deny_guests"]),
            lambda a:a["checks"]["deny_domain_admins"]["must"].update(
                same_item_field="trustee_sid"),
            lambda a:a["require"]["one_of"].pop(),
        ]
        for mutate in changes:
            doc=deepcopy(self.c)
            mutate(doc)
            with self.subTest(mutation=str(mutate)),self.assertRaises(ValueError):
                compile_native_c_windows(doc)

    def test_cannot_conflate_two_record_alternatives_into_one_field_membership(self):
        bad=deepcopy(self.c)
        check=bad["checks"]["domain_joined_non_dc"]["must"]
        check.pop("any_record_state_every_value_equals")
        check["some_domainrole_matches_one_of"]=["1","3"]
        with self.assertRaisesRegex(ValueError,"nested WMI record"):
            compile_native_c_windows(bad)

    def test_reviewer_yaml_matches_source_read_only_projection(self):
        old=present_windows_shared_observations(self.original)
        for key in ("observations","checks","require"):
            self.assertEqual(old[key],self.c[key])

if __name__=="__main__":
    unittest.main()
