#!/usr/bin/env python3
import unittest

from measure_post_modernization_variable_patterns import (
    analyze_remaining_variables,
    compile_time_static_variables,
    exact_variable_refs,
)


class VariableResidualPatternTests(unittest.TestCase):
    def test_exact_variable_reference_paths(self):
        value={
            "objects":{
                "o":{"select":{"path":{"value":{"variable":"v"}}}}
            },
            "variables":{
                "other":{"expression":{"variable":{"variable":"v"}}}
            },
        }
        paths=list(exact_variable_refs(value,"v"))
        self.assertEqual(len(paths),2)
        self.assertIn(("objects","o","select","path","value"),paths)

    def test_compile_time_static_variable_closure(self):
        variables={
            "constant":{
                "kind":"constant",
                "datatype":"string",
                "expression":{"literal":["/lib","/lib64"]},
            },
            "static-concat":{
                "kind":"local",
                "datatype":"string",
                "expression":{
                    "concat":[
                        {"variable":"constant"},
                        {"literal":{"value":"/x","datatype":"string"}},
                    ]
                },
            },
            "object-derived":{
                "kind":"local",
                "datatype":"string",
                "expression":{"values":{"object":"source","field":"name"}},
            },
            "depends-on-object":{
                "kind":"local",
                "datatype":"string",
                "expression":{
                    "concat":[
                        {"variable":"object-derived"},
                        {"literal":{"value":"/x","datatype":"string"}},
                    ]
                },
            },
            "external":{
                "kind":"external",
                "datatype":"string",
            },
            "depends-on-external":{
                "kind":"local",
                "datatype":"string",
                "expression":{"variable":"external"},
            },
            "cycle-a":{
                "kind":"local",
                "datatype":"string",
                "expression":{"variable":"cycle-b"},
            },
            "cycle-b":{
                "kind":"local",
                "datatype":"string",
                "expression":{"variable":"cycle-a"},
            },
        }
        result=compile_time_static_variables(variables)
        self.assertTrue(result["constant"])
        self.assertTrue(result["static-concat"])
        self.assertFalse(result["object-derived"])
        self.assertFalse(result["depends-on-object"])
        self.assertFalse(result["external"])
        self.assertFalse(result["depends-on-external"])
        self.assertFalse(result["cycle-a"])
        self.assertFalse(result["cycle-b"])

    def test_analysis_counts_fanout_and_chaining(self):
        assessment={
            "variables":{
                "v1":{
                    "kind":"local",
                    "datatype":"string",
                    "expression":{"values":{"object":"source","field":"name"}},
                },
                "v2":{
                    "kind":"local",
                    "datatype":"string",
                    "expression":{
                        "concat":[
                            {"variable":{"variable":"v1"}},
                            {"literal":{"value":"/x","datatype":"string"}},
                        ]
                    },
                },
            },
            "objects":{
                "source":{"capability":"unix.file"},
                "target":{
                    "capability":"unix.file",
                    "select":{
                        "path":{
                            "value":{"variable":"v1"},
                            "operation":"equal",
                            "datatype":"string",
                            "variable_match":"all",
                        }
                    },
                },
            },
            "tests":{},
            "evaluate":{},
        }
        foreach_report={
            "review_required":[
                {"variable":"v1","reasons":["target_variable_match_not_any"]}
            ]
        }
        result=analyze_remaining_variables(assessment,foreach_report)
        self.assertEqual(result["variables"],2)
        self.assertEqual(result["compile_time_static_variables"],0)
        self.assertEqual(result["runtime_variables"],2)
        self.assertEqual(result["expression_kind_counts"]["direct_object_projection"],1)
        self.assertEqual(result["variables_consumed_by_variables"],1)
        self.assertGreaterEqual(result["variable_dependency_edges"],1)
        row=next(x for x in result["rows"] if x["variable_id"]=="v1")
        self.assertEqual(
            row["foreach_v1_refusal_reasons"],
            ["target_variable_match_not_any"],
        )


if __name__=="__main__":
    unittest.main()
