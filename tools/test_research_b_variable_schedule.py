#!/usr/bin/env python3
"""#237 prove source Variable plan deterministic, complete, nonexecuting."""
from __future__ import annotations

import copy
from pathlib import Path
import sys
import unittest
import yaml

sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_b_variable_schedule import plan_source_variables,FORMAT
from research_b_variable_dag_inventory import variable_references

SOURCES=Path(__file__).resolve().parents[1]/(
    "research/requirements-first-language/contract-candidate/corpus/source-specimens")
SIMPLE=SOURCES/"independent-shellcommand-apache-small-575d1e0ee9d2.source.yaml"
COMPLEX=SOURCES/"independent-shellcommand-1-3d964d126ca8.source.yaml"


class SourceVariablePlanTests(unittest.TestCase):
    def load(self,path):
        return yaml.safe_load(path.read_text())["assessment"]

    def test_simple_source_dag_dependency_order_and_original_expression(self):
        a=self.load(SIMPLE)
        p=plan_source_variables(a)
        self.assertEqual(p["format"],FORMAT)
        self.assertFalse(p["execution_supported"])
        self.assertFalse(p["original_source_parity_verified"])
        self.assertEqual([x["operator"] for x in p["nodes"]],
                         ["regex_capture","concat"])
        self.assertEqual(len(p["nodes"]),2)
        self.assertEqual(p["nodes"][1]["depends_on"],[p["nodes"][0]["id"]])
        self.assertEqual(p["nodes"][1]["source_expression"],
                         a["variables"][p["nodes"][1]["id"]]["expression"])
        self.assertEqual(p,plan_source_variables(a))

    def test_complex_real_apache_source_dag_complete_and_topological(self):
        a=self.load(COMPLEX)
        p=plan_source_variables(a)
        self.assertEqual(p["source_assessment_id"],"SV-214268.automated")
        self.assertEqual(len(p["nodes"]),19)
        self.assertEqual(p["max_variable_depth"],9)
        self.assertEqual({n["id"] for n in p["nodes"]},set(a["variables"]))
        order={n["id"]:i for i,n in enumerate(p["nodes"])}
        for i,node in enumerate(p["nodes"]):
            self.assertTrue(all(order[dep]<i for dep in node["depends_on"]))
            self.assertEqual(node["source_expression"],
                             a["variables"][node["id"]]["expression"])
        self.assertEqual({n["operator"] for n in p["nodes"]},
                         {"regex_capture","concat","merge","unique"})

    def test_unbound_references_and_cycles_rejected(self):
        a=self.load(SIMPLE)
        first=next(iter(a["variables"]))
        a["variables"][first]["expression"]={"concat":[{"variable":"ghost"}]}
        with self.assertRaisesRegex(ValueError,"unresolved"):
            plan_source_variables(a)

        a=self.load(SIMPLE)
        names=list(a["variables"])
        for first,second in ((names[0],names[1]),(names[1],names[0])):
            a["variables"][first]["expression"]={"concat":[{"variable":second}]}
        with self.assertRaisesRegex(ValueError,"cyclic"):
            plan_source_variables(a)

    def test_missing_source_expression_or_unknown_operator_rejected(self):
        a=self.load(SIMPLE)
        x=next(iter(a["variables"]))
        a["variables"][x]["expression"]={"magic_unsupported":{"variable":"other"}}
        with self.assertRaises(ValueError):
            plan_source_variables(a)
        a=self.load(SIMPLE)
        x=next(iter(a["variables"]))
        a["variables"][x]["expression"]={"magic_unsupported":"literal"}
        with self.assertRaisesRegex(ValueError,"operator"):
            plan_source_variables(a)

    def test_source_plan_immutable_and_nonexecutable(self):
        a=self.load(SIMPLE)
        original=copy.deepcopy(a)
        p=plan_source_variables(a)
        self.assertEqual(original,a)
        p["nodes"][0]["source_expression"]={"changed":True}
        self.assertEqual(original,a)


if __name__=="__main__":
    unittest.main()
