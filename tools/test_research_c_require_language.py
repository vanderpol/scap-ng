#!/usr/bin/env python3
"""#245 Adversarial C authoring proof vs pinned A requirement schema, source-backed.

No SCAP 1.4 collector or original XML evaluation is claimed. Where source
truth is known, supplied Item results follow separately implemented generic
OVAL tables. All source tokens remain representable without magic defaults.
"""
from __future__ import annotations
from copy import deepcopy
from itertools import product
import json
from pathlib import Path
import sys
import unittest
import yaml

sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_c_require_language import compile_c_requirement,EXISTENCE,MATCH,_catalog
from oval_result_truth_tables import evaluate_collected_object_test

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"research/assessment-simplification/compact-authoring-04"
WIN=yaml.safe_load((BASE/"c-short-windows-wdigest.research.yaml").read_text())
LINUX=yaml.safe_load((BASE/"c-short-linux-home.research.yaml").read_text())
A=json.loads((BASE/"runtime-slice/home-nosuid.assessment.json").read_text())

def compiled(c):
    return compile_c_requirement(c)["test"]

def check(existence,matcher,observed,flag="complete"):
    return evaluate_collected_object_test(
        flag,existence=existence,check=matcher,has_state=True,
        item_results=list(observed),exists=len(observed))


class CandidateCGrammar(unittest.TestCase):
    def test_independently_written_linux_short_must_retains_A_semantics(self):
        result=compiled(LINUX)
        original=next(iter(A["assessment"]["tests"].values()))
        self.assertEqual(result["object"],original["object"])
        self.assertEqual(result["require"],original["require"])
        self.assertEqual(result["states"],original["states"])
        self.assertNotIn("states_match",result)
        self.assertFalse(compile_c_requirement(LINUX)["scanner_executed"])

    def test_independently_written_registry_short_must_retains_source_type_and_value(self):
        result=compiled(WIN)
        self.assertEqual(result["require"],"at_least_one_exists_and_all_match")
        self.assertEqual(result["states_match"],"all")
        self.assertEqual(result["object"]["select"]["hive"],{"equals":"local_machine"})
        self.assertEqual(result["states"],[
            {"type":{"require":"at_least_one_exists_and_all_match","equals":"dword"}},
            {"value":{"require":"at_least_one_exists_and_all_match","equals":0}},
        ])
        self.assertIs(type(result["states"][1]["value"]["equals"]),int)
        self.assertEqual(result["object"]["select"]["key"]["equals"],
            r"SYSTEM\CurrentControlSet\Control\SecurityProviders\Wdigest")

    def test_plain_must_some_not_all_with_independent_oval_check(self):
        c=deepcopy(WIN)
        c["must"]={"type":"dword","value":0}
        any_source=compiled(c)
        every_source=compiled(WIN)
        self.assertEqual(any_source["require"],"at_least_one_exists_and_some_match")
        self.assertEqual(every_source["require"],"at_least_one_exists_and_all_match")
        cases=[
            ([],("false","false")),
            (["true"],("true","true")),
            (["false"],("false","false")),
            (["true","false"],("true","false")),
            (["true","true"],("true","true")),
        ]
        for evidence,want in cases:
            with self.subTest(evidence=evidence):
                got=(check("at_least_one_exists","at least one",evidence),
                     check("at_least_one_exists","all",evidence))
                self.assertEqual(got,want)
        for op,want in [
            ("one_matching_item","at_least_one_exists_and_only_one_matches"),
            ("no_matching_item","at_least_one_exists_and_none_match"),
            ("exactly_one_item","only_one_exists_and_matches"),
        ]:
            c=deepcopy(WIN)
            c["must"]={op:{"type":"dword","value":0}}
            self.assertEqual(compiled(c)["require"],want)

    def test_authoring_can_name_each_existing_A_paired_and_presence_token(self):
        paired,presence=_catalog()
        self.assertEqual(len(paired),21) # Current pinned 0.4-A schema
        for token in paired:
            if token=="none_exist":
                # Ambiguous in schema as both paired and presence-only.
                doc=deepcopy(WIN)
                doc["must"]={"special_source_requirement":token,
                             "fields":{"type":"dword","value":0}}
            else:
                selections=[]
                for name,code in EXISTENCE.items():
                    for mode,m in MATCH.items():
                        if code+"_and_"+m==token:
                            selections.append((name,mode))
                doc=deepcopy(WIN)
                if selections:
                    name,mode=selections[0]
                    doc["must"]={"items_exist":name,"items_match":mode,
                                 "fields":{"type":"dword","value":0}}
                else:
                    doc["must"]={"special_source_requirement":token,
                                 "fields":{"type":"dword","value":0}}
            with self.subTest(token=token):
                self.assertEqual(compiled(doc)["require"],token)
        for token in presence:
            native=deepcopy(WIN)
            native["must"]=next((word for word,val in __import__(
                "research_c_require_language").PRESENCE_WORDS.items() if val==token))
            with self.subTest(presence=token):
                c=compiled(native)
                self.assertEqual(c["require"],token)
                self.assertNotIn("states",c)

    def test_refuse_implicit_semantic_drift(self):
        bads=[
            {"must":{"every_item":{"type":"dword","value":"0"}}},
            {"must":{"every_item":{"type":"DWORD","value":0}}},
            {"must":{"every_item":{"type":"dword","value":False}}},
            {"must":{"every_item":{"type":"dword","value":0,"unknown":7}}},
            {"must":{"evry_item":{"type":"dword","value":0}}},
            {"must":{"special_source_requirement":"not_a_token","fields":{"type":"dword"}}},
            {"must":{"items_exist":"zero","items_match":"every","fields":{"type":"dword"}}},
            {"from":{"windows.registry":{"hive":"not_a_real_hive","key":"hi","name":"foo"}}},
            {"from":{"windows.registry":{"hive":"local_machine","key":"hi","name":"foo","view":"64bit"}}},
            {"from":{"windows.registry":{"hive":"local_machine","key":"hi"}}},
            {"from":{"windows.registry":{"hive":"local_machine","key":"hi","name":"foo"}},
             "must":{"every_item":{"value":{"contains":"a"}}}},
            {"must":{}},
        ]
        for bad in bads:
            doc=deepcopy(WIN)
            doc.update(bad)
            with self.subTest(change=bad):
                with self.assertRaises(ValueError):
                    compiled(doc)

    def test_one_matching_item_and_exactly_one_existing_item_not_conflated(self):
        # One matching Item amongst two is not one Item in collection.
        items=["true","false"]
        self.assertEqual(check("at_least_one_exists","only one",items),"true")
        self.assertEqual(check("only_one_exists","all",items),"false")
        self.assertEqual(check("at_least_one_exists","only one",["true","true"]),"false")

    def test_incomplete_empty_not_equal_complete_empty(self):
        self.assertEqual(check("at_least_one_exists","all",[]),"false")
        self.assertEqual(check("at_least_one_exists","all",[],"incomplete"),"unknown")
        self.assertEqual(check("at_least_one_exists","all",["false"],"incomplete"),"false")
        self.assertEqual(check("at_least_one_exists","all",["true"],"incomplete"),"unknown")
        self.assertEqual(check("at_least_one_exists","at least one",["true"],"incomplete"),"true")


if __name__=="__main__":
    unittest.main()
