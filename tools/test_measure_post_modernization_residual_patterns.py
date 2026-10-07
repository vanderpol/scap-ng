#!/usr/bin/env python3
import tempfile
import unittest
from pathlib import Path

import yaml

from measure_post_modernization_residual_patterns import (
    build_report,
    coarse_set_signature,
    direct_filter_shapes,
    set_shapes,
)


class ResidualPatternTests(unittest.TestCase):
    def write(self,root,name,assessment):
        p=Path(root)/"assessments"/"automated"/f"{name}.assessment.yaml"
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(yaml.safe_dump({"assessment":assessment},sort_keys=False),encoding="utf-8")

    def test_set_filter_shape_after_locality(self):
        assessment={
            "id":"benchmark.test.SV-set.automated",
            "version":1,
            "mode":"automated",
            "purpose":"assessment",
            "class":"compliance",
            "objects":{
                "a":{"capability":"unix.file","select":{"path":{"value":"/a"}}},
                "b":{"capability":"unix.file","select":{"path":{"value":"/b"}}},
                "combined":{
                    "capability":"unix.file",
                    "set":{
                        "operator":"union",
                        "operands":[
                            {"object":"a","filters":[]},
                            {
                                "object":"b",
                                "filters":[
                                    {"state":"root-only","action":"include"}
                                ],
                            },
                        ],
                    },
                },
            },
            "states":{
                "root-only":{
                    "capability":"unix.file",
                    "state":{"field":"user_id","value":"0"},
                }
            },
            "tests":{"test":{"capability":"unix.file","object":"combined"}},
            "evaluate":{"test":"test"},
        }
        rows=set_shapes(assessment)
        self.assertEqual(len(rows),1)
        filters=direct_filter_shapes(assessment)
        sig=coarse_set_signature(rows,filters)
        self.assertEqual(sig["operators"],{"union":1})
        self.assertEqual(sig["filter_count"],1)
        self.assertEqual(sig["filter_actions"],{"include":1})

    def test_build_report_keeps_real_set_semantics_complex(self):
        with tempfile.TemporaryDirectory() as td:
            self.write(td,"set",{
                "id":"benchmark.test.SV-set.automated",
                "version":1,
                "mode":"automated",
                "purpose":"assessment",
                "class":"compliance",
                "objects":{
                    "shared":{"capability":"unix.file","select":{"path":{"value":"/shared"}}},
                    "combined":{
                        "capability":"unix.file",
                        "set":{
                            "operator":"union",
                            "operands":[
                                {"object":"shared","filters":[]},
                                {"object":"shared","filters":[]},
                            ],
                        },
                    },
                },
                "tests":{
                    "one":{"capability":"unix.file","object":"combined"},
                    "two":{"capability":"unix.file","object":"shared"},
                },
                "evaluate":{"all":[{"test":"one"},{"test":"two"}]},
            })
            r=build_report(Path(td),"synthetic")
            self.assertEqual(r["complex_rules"],1)
            self.assertEqual(r["set_filter_rules"],1)
            self.assertGreaterEqual(r["unique_set_filter_pattern_signatures"],1)

    def test_build_report_localizes_leaf_derived_variable(self):
        with tempfile.TemporaryDirectory() as td:
            self.write(td,"var",{
                "id":"benchmark.test.SV-var.automated",
                "version":1,
                "mode":"automated",
                "purpose":"assessment",
                "class":"compliance",
                "objects":{
                    "source":{"capability":"unix.file","select":{"path":{"value":"/src"}}},
                    "target":{
                        "capability":"unix.file",
                        "select":{
                            "path":{
                                "value":{"variable":"derived"},
                                "operation":"equals",
                                "datatype":"string",
                                "variable_match":"all",
                            }
                        },
                    },
                },
                "variables":{
                    "derived":{
                        "kind":"local",
                        "datatype":"string",
                        "expression":{
                            "concat":[
                                {"values":{"object":"source","field":"path"}},
                                {"literal":{"value":"/x","datatype":"string"}},
                            ]
                        },
                    },
                },
                "tests":{"test":{"capability":"unix.file","object":"target"}},
                "evaluate":{"test":"test"},
            })
            r=build_report(Path(td),"synthetic")
            self.assertEqual(r["complex_rules"],0)
            self.assertEqual(r["derived_variable_rules"],0)

    def test_build_report_retains_chained_derived_variable(self):
        with tempfile.TemporaryDirectory() as td:
            self.write(td,"chain",{
                "id":"benchmark.test.SV-chain.automated",
                "version":1,
                "mode":"automated",
                "purpose":"assessment",
                "class":"compliance",
                "objects":{
                    "target":{
                        "capability":"unix.file",
                        "select":{
                            "path":{
                                "value":{"variable":"outer"},
                                "operation":"equals",
                                "datatype":"string",
                                "variable_match":"all",
                            }
                        },
                    },
                },
                "variables":{
                    "inner":{
                        "kind":"local",
                        "datatype":"string",
                        "expression":{
                            "concat":[
                                {"literal":{"value":"/src","datatype":"string"}}
                            ]
                        },
                    },
                    "outer":{
                        "kind":"local",
                        "datatype":"string",
                        "expression":{
                            "concat":[
                                {"variable":{"variable":"inner"}},
                                {"literal":{"value":"/x","datatype":"string"}},
                            ]
                        },
                    },
                },
                "tests":{"test":{"capability":"unix.file","object":"target"}},
                "evaluate":{"test":"test"},
            })
            r=build_report(Path(td),"synthetic")
            self.assertEqual(r["complex_rules"],1)
            self.assertEqual(r["derived_variable_rules"],1)


if __name__=="__main__":
    unittest.main()
