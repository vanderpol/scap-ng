#!/usr/bin/env python3
import tempfile
import unittest
from pathlib import Path

import yaml

from measure_full_modernization_census import build_report


class FullModernizationCensusTests(unittest.TestCase):
    def write_assessment(self,root,name,assessment):
        path=Path(root)/"assessments"/"automated"/f"{name}.assessment.yaml"
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(yaml.safe_dump({"assessment":assessment},sort_keys=False),encoding="utf-8")
        return path

    def test_single_local_test_becomes_local_simple(self):
        with tempfile.TemporaryDirectory() as td:
            self.write_assessment(td,"one",{
                "id":"benchmark.test.SV-1.automated",
                "version":1,
                "mode":"automated",
                "purpose":"assessment",
                "class":"compliance",
                "objects":{
                    "obj":{"capability":"unix.file","select":{"path":"/tmp/example"}}
                },
                "states":{
                    "state":{"capability":"unix.file","expect":{"owner":"root"}}
                },
                "tests":{
                    "test":{"capability":"unix.file","object":"obj","states":["state"]}
                },
                "evaluate":{"test":"test"},
            })
            report=build_report(Path(td),label="synthetic")
            s=report["summary"]
            self.assertEqual(s["automated_assessments"],1)
            self.assertEqual(s["classification_counts"],{"local_simple":1})
            self.assertEqual(s["modernized_objects"],0)
            self.assertEqual(s["modernized_states"],0)
            self.assertEqual(s["single_test_explicit_root_authoring_opportunities"],1)

    def test_single_use_external_input_is_binding_not_dataflow_complexity(self):
        with tempfile.TemporaryDirectory() as td:
            self.write_assessment(td,"external",{
                "id":"benchmark.test.SV-ext.automated",
                "version":1,
                "mode":"automated",
                "purpose":"assessment",
                "class":"compliance",
                "objects":{
                    "obj":{"capability":"unix.file","select":{"path":"/tmp/example"}}
                },
                "states":{
                    "state":{
                        "capability":"unix.file",
                        "state":{
                            "field":"owner",
                            "value":{"variable":"expected-owner"},
                        },
                    }
                },
                "variables":{
                    "expected-owner":{
                        "kind":"external",
                        "datatype":"string",
                        "input":{"required":True,"cardinality":"one_or_more"},
                    }
                },
                "tests":{
                    "test":{"capability":"unix.file","object":"obj","states":["state"]}
                },
                "evaluate":{"test":"test"},
            })
            report=build_report(Path(td),label="synthetic")
            row=report["assessments"][0]
            s=report["summary"]
            self.assertEqual(row["classification"],"local_simple")
            self.assertEqual(row["after"]["variables"],0)
            self.assertEqual(s["private_external_variables_localized"],1)
            self.assertNotIn("derived_variable_graph",row["residual_reasons"])

    def test_single_use_leaf_derived_variable_localizes(self):
        with tempfile.TemporaryDirectory() as td:
            self.write_assessment(td,"local-variable",{
                "id":"benchmark.test.SV-local.automated",
                "version":1,
                "mode":"automated",
                "purpose":"assessment",
                "class":"compliance",
                "objects":{
                    "source":{"capability":"unix.file","select":{"path":"/tmp/source"}},
                    "target":{
                        "capability":"unix.file",
                        "select":{
                            "path":{
                                "value":{"variable":"derived-path"},
                                "operation":"equals",
                                "datatype":"string",
                                "variable_match":"all",
                            }
                        },
                    },
                },
                "variables":{
                    "derived-path":{
                        "kind":"local",
                        "datatype":"string",
                        "expression":{
                            "concat":[
                                {"values":{"object":"source","field":"path"}},
                                {"literal":{"value":"/x","datatype":"string"}},
                            ]
                        },
                    }
                },
                "tests":{"test":{"capability":"unix.file","object":"target"}},
                "evaluate":{"test":"test"},
            })
            report=build_report(Path(td),label="synthetic")
            row=report["assessments"][0]
            s=report["summary"]
            self.assertEqual(row["classification"],"local_simple")
            self.assertNotIn("derived_variable_graph",row["residual_reasons"])
            self.assertEqual(row["after"]["variables"],0)
            self.assertEqual(s["private_local_variables_localized"],1)

    def test_shared_local_derived_variable_remains_complex(self):
        with tempfile.TemporaryDirectory() as td:
            self.write_assessment(td,"shared-local-variable",{
                "id":"benchmark.test.SV-shared-local.automated",
                "version":1,
                "mode":"automated",
                "purpose":"assessment",
                "class":"compliance",
                "objects":{
                    "source":{"capability":"unix.file","select":{"path":"/tmp/source"}},
                    "a":{
                        "capability":"unix.file",
                        "select":{
                            "path":{
                                "value":{"variable":"derived-path"},
                                "operation":"equals",
                                "datatype":"string",
                                "variable_match":"all",
                            }
                        },
                    },
                    "b":{
                        "capability":"unix.file",
                        "select":{
                            "path":{
                                "value":{"variable":"derived-path"},
                                "operation":"equals",
                                "datatype":"string",
                                "variable_match":"all",
                            }
                        },
                    },
                },
                "variables":{
                    "derived-path":{
                        "kind":"local",
                        "datatype":"string",
                        "expression":{"values":{"object":"source","field":"path"}},
                    }
                },
                "tests":{
                    "one":{"capability":"unix.file","object":"a"},
                    "two":{"capability":"unix.file","object":"b"},
                },
                "evaluate":{"all":[{"test":"one"},{"test":"two"}]},
            })
            report=build_report(Path(td),label="synthetic")
            row=report["assessments"][0]
            self.assertEqual(row["classification"],"meaningfully_complex")
            self.assertIn("derived_variable_graph",row["residual_reasons"])
            self.assertEqual(row["after"]["variables"],1)

    def test_shared_acquisition_is_retained_and_classified_complex(self):
        with tempfile.TemporaryDirectory() as td:
            self.write_assessment(td,"shared",{
                "id":"benchmark.test.SV-2.automated",
                "version":1,
                "mode":"automated",
                "purpose":"assessment",
                "class":"compliance",
                "objects":{
                    "shared":{"capability":"unix.file","select":{"path":"/tmp/example"}}
                },
                "tests":{
                    "one":{"capability":"unix.file","object":"shared"},
                    "two":{"capability":"unix.file","object":"shared"},
                },
                "evaluate":{"all":[{"test":"one"},{"test":"two"}]},
            })
            report=build_report(Path(td),label="synthetic")
            row=report["assessments"][0]
            self.assertEqual(row["classification"],"meaningfully_complex")
            self.assertIn("shared_acquisition",row["residual_reasons"])
            self.assertEqual(row["after"]["objects"],1)
            self.assertEqual(
                report["summary"]["retained_object_reason_counts"],
                {"multiple_tests":1},
            )
            self.assertEqual(
                report["summary"]["retained_object_context_signature_counts"],
                {"test_object:2":1},
            )

    def test_graph_only_object_scope_is_reported_separately_from_shared_acquisition(self):
        with tempfile.TemporaryDirectory() as td:
            self.write_assessment(td,"graph-only",{
                "id":"benchmark.test.SV-graph.automated",
                "version":1,
                "mode":"automated",
                "purpose":"assessment",
                "class":"compliance",
                "objects":{
                    "source":{"capability":"unix.file","select":{"path":"/tmp/source"}},
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
                                {"variable":{"variable":"other"}},
                            ]
                        },
                    },
                    "other":{
                        "kind":"local",
                        "datatype":"string",
                        "expression":{"literal":{"value":"/x","datatype":"string"}},
                    },
                },
                "tests":{"test":{"capability":"unix.file","object":"target"}},
                "evaluate":{"test":"test"},
            })
            report=build_report(Path(td),label="synthetic")
            row=report["assessments"][0]
            self.assertIn("named_object_graph",row["residual_reasons"])
            self.assertNotIn("shared_acquisition",row["residual_reasons"])
            self.assertEqual(
                report["summary"]["retained_object_reason_counts"],
                {"graph_only":1},
            )
            self.assertEqual(
                report["summary"]["retained_object_context_signature_counts"],
                {"variable:1":1},
            )


if __name__=="__main__":
    unittest.main()
