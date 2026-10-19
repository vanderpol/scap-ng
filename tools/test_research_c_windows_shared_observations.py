#!/usr/bin/env python3
"""Refs #245: Windows 11 source-backed C observation/logic readability seam.

Tests source structure and supplied six-state Test outcomes only. No WMI or
userright collector is executed, no source XML oracle is claimed.
"""
from copy import deepcopy
from itertools import product
from pathlib import Path
import sys
import unittest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from research_c_windows_shared_observations import (
    present_windows_shared_observations, reconstruct_windows_source,
    CHECKS, OBSERVATIONS,
)
from research_c_common_evaluation import lower_c_assessment_logic, evaluate_c_assessment_logic
from v04_a_truth_plan_source_oracle import source_expected_outcome

SOURCE=Path(__file__).resolve().parents[1]/(
    "research/requirements-first-language/contract-candidate/corpus/"
    "source-specimens/windows-userright-1-39dad4df5336.source.yaml"
)

class ComplexWindowsSevenChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=yaml.safe_load(SOURCE.read_text(encoding="utf-8"))["assessment"]
        cls.view=present_windows_shared_observations(cls.source)
        cls.assessment={"id":cls.view["source_assessment"],"mode":"automated",
                        "tests":{alias:{} for alias in cls.view["checks"]}}
        cls.plan=lower_c_assessment_logic(cls.view["require"],cls.assessment)

    def test_real_source_has_only_two_observations_seven_checks(self):
        self.assertEqual(len(self.source["shared_objects"]),2)
        self.assertEqual(len(self.source["tests"]),7)
        self.assertEqual(len(self.view["observations"]),2)
        self.assertEqual(len(self.view["checks"]),7)
        self.assertEqual(set(self.view["checks"]),set(CHECKS))
        self.assertEqual(self.view["require"].keys(),{"one_of"})
        self.assertEqual(len(self.view["require"]["one_of"]),3)
        self.assertEqual([len(x["every"]) for x in self.view["require"]["one_of"][:2]], [5,2])
        self.assertFalse(self.view["scanner_executed"])
        self.assertTrue(self.view["read_only_source_reconstruction"])

    def test_repository_auditor_yaml_exactly_matches_source_projection(self):
        # Derive repository root from source fixture, not the cwd.
        candidate=Path(__file__).resolve().parents[1]/(
            "research/assessment-simplification/compact-authoring-04/"
            "c-source-exact-windows-rdp-rights.research.yaml"
        )
        reviewed=yaml.safe_load(candidate.read_text(encoding="utf-8"))
        self.assertEqual(set(reviewed),{"observations","checks","require"})
        for key in reviewed:
            self.assertEqual(reviewed[key],self.view[key],
                             f"C reviewer sample differs from source on {key}")

    def test_source_reconstruction_is_exact_and_nonmutating(self):
        saved=deepcopy(self.source)
        compiled=reconstruct_windows_source(self.view,self.source)
        self.assertEqual(compiled,self.source)
        self.assertIsNot(compiled,self.source)
        self.assertEqual(self.source,saved)
        self.assertEqual(self.view,present_windows_shared_observations(compiled))

    def test_domain_role_is_or_of_two_entire_record_states_not_some_value(self):
        for label,expect in (("domain_joined_non_dc",["1","3"]),
                             ("standalone",["0","2"])):
            requirement=self.view["checks"][label]["must"]
            self.assertEqual(requirement["items"],"every_item")
            self.assertEqual(requirement["record"],"result")
            self.assertEqual(requirement["field"],"domainrole")
            self.assertEqual(requirement["record_requirement"],
                             "at_least_one_exists_and_all_match")
            self.assertEqual(requirement["field_requirement"],
                             "at_least_one_exists_and_all_match")
            self.assertEqual(requirement["any_record_state_every_value_equals"],expect)

    def test_all_rights_share_one_observation_with_separate_requirements(self):
        rights=[c for c in self.view["checks"].values()
                if c["observation"]=="denied_remote_logon_trustees"]
        self.assertEqual(len(rights),5)
        for requirement in rights:
            self.assertEqual(requirement["must"]["items"],"any_item")
            self.assertEqual(requirement["must"]["same_item_field"],"trustee_name")
        self.assertTrue(len({str(r["must"]["predicate"]) for r in rights})==5)

    def test_all_boolean_leaf_assignments_match_independent_source_oracle(self):
        for outcomes in product(("true","false"),repeat=7):
            supplied=dict(zip(CHECKS,outcomes))
            source_inputs={CHECKS[key]:value for key,value in supplied.items()}
            expected=source_expected_outcome(self.source["evaluate"],source_inputs,{})
            actual=evaluate_c_assessment_logic(self.plan,supplied)
            self.assertEqual(actual["outcome"],expected,
                             f"source/C mismatch: {supplied}")

    def test_six_state_unknown_error_not_applicable_and_not_evaluated(self):
        keys=list(CHECKS)
        values=("true","false","unknown","error","not_applicable","not_evaluated")
        scenarios=[dict(zip(keys,[v]*len(keys))) for v in values]
        for i,key in enumerate(keys):
            for val in values:
                datum={x:"true" for x in keys}
                datum[key]=val
                scenarios.append(datum)
        for supplied in scenarios:
            expected=source_expected_outcome(
                self.source["evaluate"],
                {CHECKS[key]:value for key,value in supplied.items()},
                {})
            got=evaluate_c_assessment_logic(self.plan,supplied)
            with self.subTest(supplied=supplied):
                self.assertEqual(got["outcome"],expected)

    def test_mixed_domain_conditions_do_not_become_implicit_if_else(self):
        # A truthful alternative branch is decisive, even when a separate
        # condition has unknown/error. No programming-language ELSE shortcut.
        cases=[
            {"domain_joined_non_dc":"unknown","standalone":"true",
             "deny_guests":"true","deny_everyone":"false"},
            {"domain_joined_non_dc":"false","standalone":"unknown",
             "deny_everyone":"true"},
            {"domain_joined_non_dc":"error","standalone":"false",
             "deny_everyone":"false"},
        ]
        for row in cases:
            supplied={key:row.get(key,"true") for key in CHECKS}
            expected=source_expected_outcome(
                self.source["evaluate"],
                {CHECKS[key]:value for key,value in supplied.items()}, {})
            self.assertEqual(evaluate_c_assessment_logic(
                self.plan,supplied)["outcome"],expected)

    def test_source_mutations_fail_closed_not_normalized(self):
        for modify in (
            lambda a:a["tests"][CHECKS["standalone"]]["states"][0]["record"][
                "fields"]["domainrole"].update(value="5"),
            lambda a:a["tests"][CHECKS["deny_guests"]]["states"][0].update(
                operation="pattern_match"),
            lambda a:a["shared_objects"]["windows-wmi57-object"]["collect"].update(
                query="SELECT DomainRole, Name FROM win32_computersystem"),
            lambda a:a["shared_objects"]["windows-userright-object"]["select"].update(
                userright="OTHER_RIGHT"),
            lambda a:a["tests"][CHECKS["deny_guests"]].update(match="all"),
            lambda a:a["tests"][CHECKS["standalone"]]["states"][0]["record"][
                "fields"]["domainrole"].update(existence="optional"),
            lambda a:a["evaluate"]["any"].pop(1),
        ):
            mutated=deepcopy(self.source)
            modify(mutated)
            with self.subTest(mutated=str(modify)):
                with self.assertRaises(ValueError):
                    present_windows_shared_observations(mutated)

    def test_editing_read_only_source_view_is_rejected(self):
        view=deepcopy(self.view)
        view["checks"]["deny_everyone"]["must"]["predicate"]={
            "case_insensitive_equals":"Guests"}
        with self.assertRaisesRegex(ValueError,"not exactly source compatible"):
            reconstruct_windows_source(view,self.source)
        view=deepcopy(self.view)
        view["require"]["one_of"][1]["every"].reverse()
        with self.assertRaisesRegex(ValueError,"not exactly source compatible"):
            reconstruct_windows_source(view,self.source)

if __name__=="__main__":
    unittest.main()
