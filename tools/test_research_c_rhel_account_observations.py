#!/usr/bin/env python3
"""Refs #245: real RHEL 9 two-population source graph and status boundaries."""
from copy import deepcopy
from itertools import product
from pathlib import Path
import sys
import unittest
import yaml

sys.path.insert(0,str(Path(__file__).resolve().parent))
from oval_result_truth_tables import evaluate_collected_object_test, aggregate_operator
from v04_a_truth_plan_source_oracle import source_expected_outcome
from research_c_rhel_account_observations import (
    present_source_account_observations,reconstruct_source_account_observations,
    SOURCE_SITES,
)

SOURCE=Path(__file__).resolve().parents[1]/(
    "research/assessment-simplification/samples/rhel_9/assessments/automated/"
    "niwc.rhel_9.SV-257889.automated.assessment.yaml"
)

def scenario(name, existence):
    cases={
        "complete_good":("complete",["true"]),
        "complete_bad":("complete",["false"]),
        "does_not_exist":("does not exist",[]),
        "incomplete_good":("incomplete",["true"]),
        "incomplete_bad":("incomplete",["false"]),
        "error":("error",[]),
        "not_collected":("not collected",[]),
        "not_applicable":("not applicable",[]),
    }
    flag,values=cases[name]
    return evaluate_collected_object_test(
        flag,existence=existence,check="all",
        has_state=True,item_results=values,
        exists=len(values)).replace(" ","_")

class AccountDerivedRhelObservationGate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=yaml.safe_load(SOURCE.read_text(encoding="utf-8"))["assessment"]
        cls.view=present_source_account_observations(cls.source)

    def test_source_remains_two_separate_observations_with_distinct_existence(self):
        v=self.view
        self.assertEqual(set(v["observations"]),set(SOURCE_SITES))
        regular=v["observations"]["non_system_users_home_files"]
        root=v["observations"]["root_home_files"]
        self.assertEqual(regular["source_item_existence"],"any_exist")
        self.assertEqual(root["source_item_existence"],"at_least_one_exists")
        self.assertNotEqual(regular["source_variable"],root["source_variable"])
        self.assertNotEqual(regular["source_object"],root["source_object"])
        self.assertEqual(v["require"],{"every":[
            {"check":"non_system_users_home_files"},
            {"check":"root_home_files"}]})
        self.assertFalse(v["source_conversion_authorized"])
        self.assertFalse(v["scanner_executed"])

    def test_source_graph_full_inverse_and_original_input_immutability(self):
        initial=deepcopy(self.source)
        reconstructed=reconstruct_source_account_observations(self.view,self.source)
        self.assertEqual(reconstructed,self.source)
        self.assertEqual(self.source,initial)
        self.assertEqual(present_source_account_observations(reconstructed),self.view)

    def test_selectors_filters_and_global_variable_are_not_per_parent_foreach(self):
        for card in self.view["observations"].values():
            self.assertEqual(card["permission_bits"],
                             {"no_more_permissive_than":"0740"})
            self.assertTrue(card["global_source_variable_values"])
            self.assertFalse(card["per_parent_foreach_invented"])
            self.assertEqual(card["original_population"]["filters"],
                             [{"action":"exclude","state":"state-unix-file"}])
            self.assertEqual(card["original_population"]["behaviors"]["max_depth"],"1")
            self.assertEqual(
                card["original_population"]["select"]["path"]["variable_check"],
                "at least one")
            self.assertFalse(card["original_population"].get("for_each"))
        self.assertEqual(len(self.view["source_compatibility_graph"]["objects"]),5)
        self.assertEqual(len(self.view["source_compatibility_graph"]["variables"]),2)

    def test_missing_root_is_fail_missing_other_population_can_pass(self):
        regular=SOURCE_SITES["non_system_users_home_files"]["exists"]
        root=SOURCE_SITES["root_home_files"]["exists"]
        self.assertEqual(scenario("complete_good",regular),"true")
        self.assertEqual(scenario("does_not_exist",regular),"true")
        self.assertEqual(scenario("does_not_exist",root),"false")
        self.assertEqual(scenario("complete_good",root),"true")
        source=aggregate_operator("AND",[
            scenario("complete_good",regular).replace("_"," "),
            scenario("does_not_exist",root).replace("_"," "),
        ])
        self.assertEqual(source,"false")
        # Global merged population would incorrectly certify one good file.
        wrong_merge=evaluate_collected_object_test(
            "complete",existence="at_least_one_exists",check="all",
            has_state=True,item_results=["true"],exists=1)
        self.assertEqual(wrong_merge,"true")

    def test_eight_by_eight_collected_outcomes_match_independent_source_logic(self):
        cases=("complete_good","complete_bad","does_not_exist",
               "incomplete_good","incomplete_bad","error",
               "not_collected","not_applicable")
        names=list(SOURCE_SITES)
        for r,rt in product(cases,repeat=2):
            words=[scenario(r,SOURCE_SITES[names[0]]["exists"]),
                   scenario(rt,SOURCE_SITES[names[1]]["exists"])]
            actual=aggregate_operator("AND",
                     [word.replace("_"," ") for word in words]).replace(" ","_")
            supplied={
                SOURCE_SITES[names[0]]["test"]:words[0],
                SOURCE_SITES[names[1]]["test"]:words[1],
            }
            want=source_expected_outcome(self.source["evaluate"],supplied,{})
            with self.subTest(regular=r,root=rt):
                self.assertEqual(actual,want)

    def test_source_mutations_never_silently_normalize(self):
        actions=[
            lambda a:a["tests"][SOURCE_SITES["root_home_files"]["test"]].update(
                check_existence="any_exist"),
            lambda a:a["objects"][SOURCE_SITES["root_home_files"]["object"]][
                "behaviors"].update(max_depth="2"),
            lambda a:a["objects"][SOURCE_SITES["root_home_files"]["object"]][
                "filters"].clear(),
            lambda a:a["objects"][SOURCE_SITES["root_home_files"]["object"]][
                "select"]["filename"].update(value=r"^.+"),
            lambda a:a["objects"][SOURCE_SITES["non_system_users_home_files"]["object"]][
                "select"]["path"].update(variable_check="all"),
            lambda a:a["variables"][SOURCE_SITES["root_home_files"]["variable"]][
                "expression"]["values"].update(field="user_id"),
            lambda a:a["evaluate"]["all"].reverse(),
            lambda a:a["tests"][SOURCE_SITES["root_home_files"]["test"]].update(
                states=[]),
        ]
        for change in actions:
            mutated=deepcopy(self.source)
            change(mutated)
            with self.subTest(change=str(change)),self.assertRaises(ValueError):
                present_source_account_observations(mutated)

    def test_read_only_card_cannot_replace_source_backing(self):
        view=deepcopy(self.view)
        view["observations"]["root_home_files"]["permission_bits"]={
            "no_more_permissive_than":"0750"}
        with self.assertRaises(ValueError):
            reconstruct_source_account_observations(view,self.source)
        view=deepcopy(self.view)
        view["source_compatibility_graph"]["objects"].clear()
        with self.assertRaises(ValueError):
            reconstruct_source_account_observations(view,self.source)

if __name__=="__main__":
    unittest.main()
