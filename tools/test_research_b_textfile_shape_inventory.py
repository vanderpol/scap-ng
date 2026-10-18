#!/usr/bin/env python3
"""#237 B source-pattern census unit guards: Tests != unique Assessments."""
from __future__ import annotations
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_b_textfile_shape_inventory import shape_inventory,render_markdown,FORMAT


def test(existence="one_or_more",match="all",state=None,pattern=r"val=(\w+)"):
    t={"capability":"independent.textfilecontent54","existence":existence,"match":match,
       "object":{"capability":"independent.textfilecontent54",
                 "collect":{"multiline":True,"ignore_case":False},
                 "select":{"full_path":{"operation":"equals","value":"/etc/config"},
                           "pattern":{"operation":"pattern_match","value":pattern}}},
       "reported_elements":"all","test_title":"test"}
    if state is not None:t["states"]=state
    return t


def capsule(aid,tests,evaluate=None):
    if evaluate is None:evaluate={"test":next(iter(tests))}
    return {"source_path":"authoring/shared/assessments/"+aid+".yaml",
            "source_document":{"assessment":{
                "id":aid,"mode":"automated","tests":tests,"evaluate":evaluate}}}


class PatternCensusTests(unittest.TestCase):
    def test_multitest_assessment_counted_once_but_test_nodes_twice(self):
        one=test(state=[{"field":"subexpression","operation":"equals",
                         "existence":"one_or_more","match":"all","value":"0"}])
        two=test(existence="all",pattern=r"foo(\d+)(\d+)")
        three=test(existence="none",pattern=r"bar")
        caps={
            "A":capsule("A",{"a":one,"b":two},evaluate={"all":[{"test":"a"},{"test":"b"}]}),
            "B":capsule("B",{"x":three}),
            "manual":{"source_path":"manual.yaml","source_document":{
                "assessment":{"id":"manual","mode":"manual","tests":{}}}},
        }
        r=shape_inventory(caps)
        self.assertEqual(r["format"],FORMAT)
        self.assertFalse(r["source_equivalence_proven"])
        self.assertEqual(r["assessments_using_textfile"],2)
        self.assertEqual(r["textfile_test_nodes"],3)
        self.assertEqual(r["dimensions"]["capture_groups"],{"0":1,"1":1,"2":1})
        self.assertEqual(r["dimensions"]["direct_single_test"],{"False":2,"True":1})
        self.assertEqual(r["dimensions"]["test_existence"],{
            "one_or_more":1,"all":1,"none":1})
        self.assertEqual(len(r["combinations"]),3)
        self.assertIn("0.4-B textfile",render_markdown(r))

    def test_dynamic_regex_and_source_variable_are_not_treated_as_literal(self):
        t=test(pattern={"variable":"source-regex"})
        a=capsule("vars",{"x":t})
        a["source_document"]["assessment"]["variables"]={"source-regex":{"kind":"local"}}
        r=shape_inventory({"vars":a})
        self.assertEqual(r["dimensions"]["capture_groups"],{"dynamic":1})
        self.assertEqual(r["dimensions"]["has_variables"],{"True":1})
        self.assertIn("dynamic",render_markdown(r))

    def test_invalid_pattern_is_recorded_instead_of_crashing_census(self):
        r=shape_inventory({"bad":capsule("bad",{"x":test(pattern="[")})})
        self.assertEqual(r["dimensions"]["capture_groups"],{"regex_unrecognized":1})

if __name__=="__main__":
    unittest.main()
