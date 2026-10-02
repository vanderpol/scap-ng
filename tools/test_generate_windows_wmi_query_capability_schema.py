#!/usr/bin/env python3
import json
from pathlib import Path
import unittest

import jsonschema
from referencing import Registry, Resource

from generate_capability_schema import generate
from validate_generated_capability_semantics import validate_assessment_capability_semantics


ROOT=Path(__file__).resolve().parents[1]
MAPPING=ROOT/"schema/v0.1.0/capability-mappings/windows.wmi.query.json"


class WindowsWmiQueryCapabilitySchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mapping=json.loads(MAPPING.read_text(encoding="utf-8"))
        cls.schema=generate(cls.mapping,ROOT)
        common=json.loads(
            (ROOT/"schema/v0.1.0/capability-common.schema.json").read_text(encoding="utf-8")
        )
        cls.registry=Registry().with_resource(
            common["$id"],Resource.from_contents(common)
        )

    def validate_def(self,name,value):
        jsonschema.Draft202012Validator(
            self.schema["$defs"][name],
            registry=self.registry,
        ).validate(value)

    def test_query_is_collector_input_not_fake_selector(self):
        obj=self.schema["$defs"]["object"]
        self.assertNotIn("select",obj["properties"])
        self.assertIn("collect",obj["properties"])
        self.validate_def("object",{
            "object_title":"operating system rows",
            "capability":"windows.wmi.query",
            "collect":{
                "namespace":"root\\cimv2",
                "query":"SELECT Caption, Version FROM Win32_OperatingSystem",
            },
        })

    def test_collector_inputs_can_use_variables(self):
        self.validate_def("object",{
            "object_title":"parameterized query",
            "capability":"windows.wmi.query",
            "collect":{
                "namespace":{"variable":"wmi-namespace"},
                "query":{"variable":"wql"},
            },
        })

    def test_record_state_is_explicit_native_structure(self):
        self.validate_def("state",{
            "state_title":"expected operating system",
            "capability":"windows.wmi.query",
            "state":{
                "field":"result",
                "record":{
                    "mask":False,
                    "match":"all",
                    "existence":"some",
                    "fields":{
                        "Caption":{
                            "value":"Microsoft Windows 11 Enterprise",
                            "operation":"equal",
                            "datatype":"string",
                            "mask":False,
                            "match":"all",
                            "existence":"some",
                        },
                        "Version":{
                            "value":"10.0",
                            "operation":"greater_or_equal",
                            "datatype":"version",
                            "mask":False,
                            "match":"all",
                            "existence":"some",
                        },
                    },
                },
            },
        })

    def test_record_fields_are_not_forced_to_legacy_lowercase(self):
        self.validate_def("state",{
            "state_title":None,
            "capability":"windows.wmi.query",
            "state":{
                "field":"result",
                "record":{
                    "mask":False,
                    "match":"all",
                    "existence":"some",
                    "fields":{
                        "CSName":{
                            "value":"HOST1",
                            "operation":"equal_ci",
                            "datatype":"string",
                            "mask":False,
                            "match":"all",
                            "existence":"some",
                        }
                    },
                },
            },
        })

    def test_complex_wmi_result_can_be_nested_without_flattening(self):
        self.validate_def("state",{
            "state_title":"nested result",
            "capability":"windows.wmi.query",
            "state":{
                "field":"result",
                "record":{
                    "mask":False,
                    "match":"all",
                    "existence":"some",
                    "fields":{
                        "Adapters":{
                            "list":{
                                "mask":False,
                                "match":"any",
                                "existence":"some",
                                "item":{
                                    "record":{
                                        "mask":False,
                                        "match":"all",
                                        "existence":"some",
                                        "fields":{
                                            "Name":{
                                                "value":"Ethernet",
                                                "operation":"equal",
                                                "datatype":"string",
                                                "mask":False,
                                                "match":"all",
                                                "existence":"some",
                                            }
                                        },
                                    }
                                },
                            }
                        }
                    },
                },
            },
        })

    def test_record_does_not_use_scalar_datatype_wrapper(self):
        with self.assertRaises(jsonschema.ValidationError):
            self.validate_def("state",{
                "state_title":None,
                "capability":"windows.wmi.query",
                "state":{
                    "field":"result",
                    "value":"x",
                    "operation":"equal",
                    "datatype":"record",
                    "mask":False,
                    "match":"all",
                    "existence":"some",
                },
            })

    def test_set_object_does_not_require_collector_parameters(self):
        self.validate_def("object",{
            "object_title":"combined result set",
            "capability":"windows.wmi.query",
            "set":{
                "operator":"union",
                "operands":[
                    {"object":"query-a", "filters":[]},
                    {"object":"query-b", "filters":[]},
                ],
            },
        })

    def test_graph_capability_mismatch_is_detected(self):
        doc={
            "assessment":{
                "objects":{
                    "q":{
                        "capability":"windows.wmi.query",
                        "collect":{
                            "namespace":"root\\cimv2",
                            "query":"SELECT Caption FROM Win32_OperatingSystem",
                        },
                    }
                },
                "states":{"s":{"capability":"unix.file","state":{}}},
                "tests":{
                    "t":{
                        "capability":"windows.wmi.query",
                        "object":"q",
                        "states":["s"],
                    }
                },
            }
        }
        rows=validate_assessment_capability_semantics(doc)
        self.assertIn("test.state_capability",{row["code"] for row in rows})

    def test_legacy_wmi57_vocabulary_is_not_runtime_schema(self):
        encoded=json.dumps(self.schema).lower()
        self.assertNotIn("wmi57",encoded)
        self.assertNotIn('"wql"',encoded)
        self.assertNotIn('"datatype": "record"',encoded)


if __name__=="__main__":
    unittest.main()
