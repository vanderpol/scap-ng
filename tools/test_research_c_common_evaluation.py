#!/usr/bin/env python3
"""#245 C shared logic proof: independent source truth and empty-state boundaries."""
from __future__ import annotations
from copy import deepcopy
from itertools import product
from pathlib import Path
import sys
import unittest
import yaml

sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_c_common_evaluation import (
    population_outcome,lower_c_assessment_logic,evaluate_c_assessment_logic,SIX)
from v04_a_truth_plan_source_oracle import source_expected_outcome
from research_c_registry_boundary import lower_c_registry_exact
from research_b_source_registry_lowering import lower_source_registry_assessment
from research_b_source_registry_snapshot import normalize,PROVIDER
from research_b_source_registry_evaluator import evaluate_source_registry

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"research/assessment-simplification/compact-authoring-04"
REG_C=BASE/"c-source-exact-wdigest.research.yaml"
REG_A=ROOT/("research/requirements-first-language/contract-candidate/corpus/"
            "source-specimens/windows-registry-state-all-0fef40d33c90.source.yaml")

def request(cap, status, results=(), missing=0,error=0,not_collected=0):
    return {"capability":cap,"status":status,"items":[
        {"id":f"item-{i}","outcome":v} for i,v in enumerate(results)],
        "does_not_exist":missing,"error":error,"not_collected":not_collected}

def reg_evidence(plan,records,status="complete",by_view=None):
    views={}
    for view in ("32bit","64bit"):
        using={**plan["using"],"view":view}
        given=(by_view or {}).get(view,records)
        snap={"query":using,"status":status,"records":[
            {"value_kind":k,"raw_value":v} for k,v in given]}
        views[view]=normalize(snap,**using)
    return {PROVIDER:{"views":views}}


class UniversalPopulationTests(unittest.TestCase):
    def test_same_no_data_semantics_independent_of_collection_capability(self):
        contract={"exists":"at_least_one_exists","items_match":"every","has_state":True}
        for cap in ("linux.partition","unix.file","windows.registry","windows.wmi.query"):
            with self.subTest(capability=cap):
                self.assertEqual(population_outcome(contract,request(cap,"complete")), "false")
                self.assertEqual(population_outcome(contract,request(cap,"incomplete")), "unknown")
                self.assertEqual(population_outcome(contract,request(cap,"not_collected")), "unknown")
                self.assertEqual(population_outcome(contract,request(cap,"error")), "error")
                self.assertEqual(population_outcome(contract,request(cap,"not_applicable")), "not_applicable")
                self.assertEqual(population_outcome(contract,request(cap,"does_not_exist")), "false")
                none={"exists":"none_exist","items_match":"every","has_state":False}
                self.assertEqual(population_outcome(none,request(cap,"complete")), "true")
                self.assertEqual(population_outcome(none,request(cap,"incomplete")), "unknown")
                self.assertEqual(population_outcome(none,request(cap,"does_not_exist")), "true")

    def test_state_free_presence_and_absence_on_identified_items(self):
        for cap in ("linux.partition","unix.file","windows.registry","windows.wmi.query"):
            with self.subTest(capability=cap):
                for mode,expect_empty,expect_one in (
                    ("at_least_one_exists","false","true"),
                    ("none_exist","true","false"),
                    ("only_one_exists","false","true"),
                    ("all_exist","false","true"),
                    ("any_exist","true","true"),
                ):
                    contract={"exists":mode,"items_match":"every","has_state":False}
                    empty=request(cap,"complete")
                    found=dict(empty,items=[{"id":"observed-1"}])
                    self.assertEqual(population_outcome(contract,empty),expect_empty)
                    self.assertEqual(population_outcome(contract,found),expect_one)
                    if mode=="only_one_exists":
                        two=dict(empty,items=[{"id":"a"},{"id":"b"}])
                        self.assertEqual(population_outcome(contract,two),"false")
                    wrong=dict(empty,items=[{"id":"observed-1","outcome":"true"}])
                    with self.assertRaisesRegex(ValueError,"Item identity"):
                        population_outcome(contract,wrong)
                    self.assertEqual(population_outcome(contract,request(cap,"error")),"error")
                    self.assertEqual(population_outcome(contract,request(cap,"not_collected")),"unknown")

    def test_incomplete_can_be_decisive_but_cannot_infer_success(self):
        for cap in ("linux.partition","windows.registry"):
            base={"exists":"at_least_one_exists","items_match":"every","has_state":True}
            self.assertEqual(population_outcome(base,request(cap,"complete",["true"])),"true")
            self.assertEqual(population_outcome(base,request(cap,"incomplete",["true"])),"unknown")
            self.assertEqual(population_outcome(base,request(cap,"incomplete",["false"])),"false")
            any_req={**base,"items_match":"one_of"}
            self.assertEqual(population_outcome(any_req,request(cap,"incomplete",["true"])),"true")
            self.assertEqual(population_outcome(any_req,request(cap,"incomplete",["false"])),"unknown")
            exactly={**base,"exists":"only_one_exists"}
            self.assertEqual(population_outcome(exactly,request(cap,"incomplete",["false"])),"false")
            self.assertEqual(population_outcome(exactly,request(cap,"incomplete",["true"])),"unknown")

    def test_invalid_input_and_true_ambiguity_fail_closed(self):
        c={"exists":"at_least_one_exists","items_match":"every","has_state":True}
        e=request("windows.registry","complete",["true"])
        for altered in (
            dict(e,items=[e["items"][0],e["items"][0]]),
            dict(e,status="none"),
            dict(e,items=[{"id":"i","outcome":"pass"}]),
            dict(e,not_collected=-1),
            dict(e,items=[{"id":"i","outcome":True}]),
            dict(e,status="not_collected"),
        ):
            with self.subTest(altered=altered):
                with self.assertRaises(ValueError):
                    population_outcome(c,altered)
        c["exists"]="none_exist"
        with self.assertRaisesRegex(ValueError,"unresolved aggregation"):
            population_outcome(c,request("linux.partition","complete"))


class SixStateLogicTests(unittest.TestCase):
    def setUp(self):
        self.a={"id":"c.logic-proof","mode":"automated","tests":{"first":{},"second":{}}}

    def test_all_six_by_six_outcomes_from_independent_source_oracle(self):
        # 4*36 pairs + nested/not below, no capability dependence.
        for name in ("every","one_of","exactly_one","odd_count"):
            c={name:[{"check":"first"},{"check":"second"}]}
            plan=lower_c_assessment_logic(c,self.a)
            for one,two in product(sorted(SIX),repeat=2):
                vals={"first":one,"second":two}
                oracle=source_expected_outcome(plan["source_tree"],vals,{})
                got=evaluate_c_assessment_logic(plan,vals)["outcome"]
                self.assertEqual(got,oracle,(name,one,two))

    def test_nested_logic_reuses_existing_oval_tables(self):
        cases=[
            {"every":[{"check":"first"},{"not":{"check":"second"}}]},
            {"one_of":[{"every":[{"check":"first"},{"check":"second"}]},
                       {"not":{"check":"first"}}]},
        ]
        for logic in cases:
            plan=lower_c_assessment_logic(logic,self.a)
            for pair in product(sorted(SIX),repeat=2):
                vals=dict(zip(("first","second"),pair))
                self.assertEqual(
                    evaluate_c_assessment_logic(plan,vals)["outcome"],
                    source_expected_outcome(plan["source_tree"],vals,{}))
        for bad in (
            {"every":[]},{"check":"missing"},{"and":[{"check":"first"}]},
            {"every":[{"check":"first"}],"one_of":[{"check":"second"}]},
            {"if":{"check":"first"}},
        ):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    lower_c_assessment_logic(bad,self.a)


class WindowsSameItemBoundaryTests(unittest.TestCase):
    def setUp(self):
        c=yaml.safe_load(REG_C.read_text(encoding="utf-8"))
        self.research=c["require"]
        self.a=yaml.safe_load(REG_A.read_text(encoding="utf-8"))
        self.compiled=lower_c_registry_exact(self.research,self.a)
        self.ir=self.compiled["compatibility_ir"]

    def test_independent_c_matches_existing_source_compatibility_ast(self):
        self.assertEqual(self.ir,lower_source_registry_assessment(self.a))
        self.assertEqual(self.ir["source_view"],"unspecified_requires_xml_parity")
        self.assertEqual({v["field"] for v in self.ir["state"]["all"]},{"type","value"})
        self.assertEqual({type(v["expected"]) for v in self.ir["state"]["all"]},{str,int})
        self.assertFalse(self.compiled["source_parity_verified"])

    def test_typed_same_item_checks_and_missing_partial_view_conflicts(self):
        fixtures=[
            ([("REG_DWORD",0)],"complete","true"),
            ([("REG_DWORD",1)],"complete","false"),
            ([("REG_SZ","0")],"complete","false"),
            ([("REG_DWORD",1),("REG_SZ","0")],"complete","false"),
            ([], "complete","false"),
            ([("REG_DWORD",0)],"incomplete","unknown"),
            ([], "incomplete","unknown"),
            ([], "error","error"),
            ([], "not collected","unknown"),
        ]
        for records,status,expected in fixtures:
            with self.subTest(records=records,status=status):
                observed=evaluate_source_registry(self.ir,reg_evidence(
                    self.ir,records,status=status))
                self.assertEqual(observed[0],expected)
        conflict=reg_evidence(self.ir,[],by_view={
            "32bit":[("REG_DWORD",0)],"64bit":[("REG_DWORD",1)]})
        self.assertEqual(evaluate_source_registry(self.ir,conflict)[0],"unknown")

    def test_no_cross_item_type_and_value_borrowing_or_numeric_string_cast(self):
        bad=[("REG_DWORD",1),("REG_SZ","0")]
        self.assertEqual(evaluate_source_registry(self.ir,reg_evidence(self.ir,bad))[0],"false")
        forged=deepcopy(self.research)
        forged["on_same_item"]["all"][1]["value"]["equals"]="0"
        with self.assertRaisesRegex(ValueError,"typed field"):
            lower_c_registry_exact(forged,self.a)
        forged=deepcopy(self.research)
        forged["registry_view"]="64bit"
        with self.assertRaisesRegex(ValueError,"view cannot"):
            lower_c_registry_exact(forged,self.a)


if __name__=="__main__":
    unittest.main()
