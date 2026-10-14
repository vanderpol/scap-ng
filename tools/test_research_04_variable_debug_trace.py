#!/usr/bin/env python3
"""Fail-closed tests of static Variable DAG debug metadata; no fake runtime."""
import unittest
from research_04_variable_debug_trace import build_plan

def fixture():
    return {"assessment":{"id":"SV-TEST","mode":"automated","variables":{
      "source": {"kind":"local","datatype":"string",
                 "expression":{"values":{"object":"source-object","field":"value"}}},
      "calculate": {"kind":"local","datatype":"string",
                    "expression":{"concat":[
                        {"variable":"source"},{"literal":"/config"}]}},
      "result": {"kind":"local","datatype":"string",
                 "expression":{"regex_capture":{
                    "pattern":"^(.*)$","value":{"variable":"calculate"}}}},
      },
      "tests":{"check":{"object":{"select":{
          "path":{"value":{"variable":"result"}}}}}},
    }}

class VariableDebugPlanTests(unittest.TestCase):
    def test_topological_stages_and_operation(self):
        plan=build_plan(fixture())
        self.assertEqual([r["variable_id"] for r in plan["stages"]],["source","calculate","result"])
        self.assertEqual(plan["stages"][0]["input_objects"],["source-object"])
        self.assertEqual(plan["stages"][1]["input_variables"],["source"])
        self.assertEqual(plan["stages"][2]["input_variables"],["calculate"])
        self.assertTrue(plan["not_runtime_evidence"])

    def test_acyclic_trace_rejects_cycle(self):
        doc=fixture()
        doc["assessment"]["variables"]["source"]["expression"]={"variable":"result"}
        with self.assertRaisesRegex(ValueError,"cycle"):
            build_plan(doc)

    def test_unresolved_dependency_visible(self):
        doc=fixture()
        doc["assessment"]["variables"]["calculate"]["expression"]={"variable":"missing"}
        plan=build_plan(doc)
        self.assertEqual(plan["unresolved_variable_refs"],["missing"])

    def test_trace_plan_never_makes_up_scan_results(self):
        plan=build_plan(fixture())
        for stage in plan["stages"]:
            self.assertNotIn("observed_values",stage)
            self.assertNotIn("result",stage)
            self.assertIn("status",stage["suggested_runtime_fields"])
            self.assertIn("redaction_applied",stage["suggested_runtime_fields"])
            self.assertIn("source_item_lineage",stage["suggested_runtime_fields"])

if __name__=="__main__":
    unittest.main()
