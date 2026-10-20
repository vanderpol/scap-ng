#!/usr/bin/env python3
"""Refs #245 independent Variable usage classification and fail-closed accounting."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_c_oval_variable_usage_census import classify, references

class SourceOVALUsageCensusTests(unittest.TestCase):
    def test_source_collection_binding_not_confused_with_state_expectation(self):
        v={"kind":"constant","datatype":"string","expression":{"literal":"value"}}
        self.assertEqual(classify(v,[("objects","source","select","name","value")]),
                         "constant_collection_binding")
        self.assertEqual(classify(v,[("states","source","state","value")]),
                         "constant_single_state_expectation")
        self.assertEqual(classify(v,[("states","s1","state","value"),
                                    ("states","s2","state","value")]),
                         "constant_shared_state_expectation")

    def test_runtime_derived_and_literal_feeding_derived_are_distinct(self):
        local={"kind":"local","datatype":"string","expression":{"concat":[]}}
        const={"kind":"constant","datatype":"string","expression":{"literal":"x"}}
        self.assertEqual(classify(local,[("objects","foo","select","x")]),
                         "runtime_derived")
        self.assertEqual(classify(const,[("variables","child","expression")]),
                         "constant_derived_dependency")
        self.assertEqual(classify(const,[]),"constant_other")

    def test_variable_consumers_are_found_nested_without_guessing(self):
        graph={"states":{"state":{"state":{"all":[
            {"field":"path","value":{"variable":"v"}},
            {"field":"mode","value":{"variable":"w"}}]}}},
            "objects":{"obj":{"select":{"path":{"value":{"variable":"v"}}}}},
            "variables":{"derived":{"expression":{"variable":"v"}}}}
        use=list(references(graph,"v"))
        self.assertEqual(len(use),3)
        self.assertEqual(sorted(set(p[0] for p in use)),
                         ["objects","states","variables"])
        self.assertEqual(list(references(graph,"not_in_graph")),[])

    def test_not_a_mapped_source_variable_kind_is_not_a_guess(self):
        with self.assertRaisesRegex(ValueError,"unknown original"):
            classify({"kind":"external"},[("states","s")])

if __name__=="__main__":
    unittest.main()
