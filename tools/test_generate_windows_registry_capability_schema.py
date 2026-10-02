#!/usr/bin/env python3
import json
from pathlib import Path
import unittest

import jsonschema
from referencing import Registry, Resource

from generate_capability_schema import generate
from validate_generated_capability_semantics import (
    validate_assessment_capability_semantics,
)


ROOT=Path(__file__).resolve().parents[1]
MAPPING=ROOT/"schema/v0.1.0/capability-mappings/windows.registry.json"


class WindowsRegistryCapabilitySchemaTests(unittest.TestCase):
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

    def entity(self,value,operation="equal",datatype="string"):
        return {
            "value":value,
            "operation":operation,
            "datatype":datatype,
            "mask":False,
        }

    def test_hive_is_simple_native_selector(self):
        self.validate_def("object",{
            "object_title":"registry value",
            "capability":"windows.registry",
            "select":{
                "hive":"local_machine",
                "key":self.entity(r"Software\Example"),
                "name":self.entity("Enabled"),
            },
        })
        hive_schema=self.schema["$defs"]["object"]["properties"]["select"]["properties"]["hive"]
        encoded=json.dumps(hive_schema)
        self.assertNotIn('"operation"',encoded)
        self.assertNotIn('"datatype"',encoded)
        self.assertNotIn('"mask"',encoded)

    def test_hive_may_come_from_variable(self):
        self.validate_def("object",{
            "object_title":"variable hive",
            "capability":"windows.registry",
            "select":{
                "hive":{"variable":"target-hive"},
                "key":None,
                "name":None,
            },
        })

    def test_hive_and_key_levels_use_null_not_xml_nil(self):
        self.validate_def("object",{
            "object_title":"hive itself",
            "capability":"windows.registry",
            "select":{
                "hive":"local_machine",
                "key":None,
                "name":None,
            },
        })
        self.validate_def("object",{
            "object_title":"key itself",
            "capability":"windows.registry",
            "select":{
                "hive":"local_machine",
                "key":self.entity(r"Software\Example"),
                "name":None,
            },
        })

    def test_empty_name_is_distinct_default_value(self):
        self.validate_def("object",{
            "object_title":"default registry value",
            "capability":"windows.registry",
            "select":{
                "hive":"local_machine",
                "key":self.entity(r"Software\Example"),
                "name":self.entity(""),
            },
        })

    def test_key_null_requires_name_null(self):
        rows=validate_assessment_capability_semantics({
            "assessment":{
                "objects":{
                    "o":{
                        "capability":"windows.registry",
                        "select":{
                            "hive":"local_machine",
                            "key":None,
                            "name":self.entity("Enabled"),
                        },
                    }
                },
                "states":{},
                "tests":{},
            }
        })
        self.assertIn(
            "windows.registry.key_null_requires_name_null",
            {row["code"] for row in rows},
        )

    def test_registry_traversal_is_downward_depth_only(self):
        self.validate_def("object",{
            "object_title":"registry subtree",
            "capability":"windows.registry",
            "select":{
                "hive":"local_machine",
                "key":self.entity(r"Software\Example"),
                "name":None,
            },
            "traversal":{"max_depth":2},
        })
        traversal=self.schema["$defs"]["object"]["properties"]["traversal"]
        self.assertIn("hierarchy_traversal",json.dumps(traversal))
        self.assertNotIn("follow_links",json.dumps(traversal))
        self.assertNotIn("filesystem",json.dumps(traversal))

    def test_pattern_key_rejects_traversal(self):
        rows=validate_assessment_capability_semantics({
            "assessment":{
                "objects":{
                    "o":{
                        "capability":"windows.registry",
                        "select":{
                            "hive":"local_machine",
                            "key":self.entity(r"Software\\.*",operation="match"),
                            "name":None,
                        },
                        "traversal":{"max_depth":2},
                    }
                },
                "states":{},
                "tests":{},
            }
        })
        self.assertIn(
            "windows.registry.pattern_key_no_traversal",
            {row["code"] for row in rows},
        )

    def test_native_registry_types_are_normalized(self):
        for value in (
            "binary","dword","dword_big_endian","expand_string","link",
            "multi_string","none","qword","string","resource_list",
            "full_resource_descriptor","resource_requirements_list",
        ):
            with self.subTest(value=value):
                self.validate_def("state",{
                    "state_title":None,
                    "capability":"windows.registry",
                    "state":{
                        "field":"type",
                        "value":value,
                        "operation":"equal",
                        "datatype":"string",
                        "mask":False,
                        "match":"all",
                        "existence":"some",
                    },
                })

        for legacy in ("reg_dword","reg_dword_little_endian","reg_sz"):
            with self.subTest(legacy=legacy):
                with self.assertRaises(jsonschema.ValidationError):
                    self.validate_def("state",{
                        "state_title":None,
                        "capability":"windows.registry",
                        "state":{
                            "field":"type",
                            "value":legacy,
                            "operation":"equal",
                            "datatype":"string",
                            "mask":False,
                            "match":"all",
                            "existence":"some",
                        },
                    })

    def test_registry_value_uses_typed_native_datatypes(self):
        for datatype,value in (
            ("string","enabled"),
            ("integer",1),
            ("binary","0A0B"),
            ("version","1.2.3"),
        ):
            with self.subTest(datatype=datatype):
                self.validate_def("state",{
                    "state_title":None,
                    "capability":"windows.registry",
                    "state":{
                        "field":"value",
                        "value":value,
                        "operation":"equal",
                        "datatype":datatype,
                        "mask":False,
                        "match":"all",
                        "existence":"some",
                    },
                })

    def test_exact_registry_type_constrains_value_datatype(self):
        base_states={
            "type-state":{
                "capability":"windows.registry",
                "state":{
                    "field":"type",
                    "value":"dword",
                    "operation":"equal",
                    "datatype":"string",
                    "mask":False,
                    "match":"all",
                    "existence":"some",
                },
            },
        }

        good={
            "assessment":{
                "objects":{"o":{"capability":"windows.registry"}},
                "states":{
                    **base_states,
                    "value-state":{
                        "capability":"windows.registry",
                        "state":{
                            "field":"value",
                            "value":1,
                            "operation":"equal",
                            "datatype":"integer",
                            "mask":False,
                            "match":"all",
                            "existence":"some",
                        },
                    },
                },
                "tests":{
                    "t":{
                        "capability":"windows.registry",
                        "object":"o",
                        "states":["type-state","value-state"],
                    }
                },
            }
        }
        self.assertNotIn(
            "windows.registry.value_type_datatype",
            {row["code"] for row in validate_assessment_capability_semantics(good)},
        )

        bad=json.loads(json.dumps(good))
        bad["assessment"]["states"]["value-state"]["state"]["datatype"]="string"
        bad["assessment"]["states"]["value-state"]["state"]["value"]="1"
        self.assertIn(
            "windows.registry.value_type_datatype",
            {row["code"] for row in validate_assessment_capability_semantics(bad)},
        )

    def test_string_registry_type_allows_version_comparison(self):
        doc={
            "assessment":{
                "objects":{"o":{"capability":"windows.registry"}},
                "states":{
                    "type-state":{
                        "capability":"windows.registry",
                        "state":{
                            "field":"type",
                            "value":"string",
                            "operation":"equal",
                            "datatype":"string",
                            "mask":False,
                            "match":"all",
                            "existence":"some",
                        },
                    },
                    "value-state":{
                        "capability":"windows.registry",
                        "state":{
                            "field":"value",
                            "value":"1.2.3",
                            "operation":"greater_or_equal",
                            "datatype":"version",
                            "mask":False,
                            "match":"all",
                            "existence":"some",
                        },
                    },
                },
                "tests":{
                    "t":{
                        "capability":"windows.registry",
                        "object":"o",
                        "states":["type-state","value-state"],
                    }
                },
            }
        }
        self.assertNotIn(
            "windows.registry.value_type_datatype",
            {row["code"] for row in validate_assessment_capability_semantics(doc)},
        )

    def test_resource_registry_types_do_not_guess_value_datatype(self):
        for registry_type in ("none","resource_list","full_resource_descriptor","resource_requirements_list"):
            with self.subTest(registry_type=registry_type):
                doc={
                    "assessment":{
                        "objects":{"o":{"capability":"windows.registry"}},
                        "states":{
                            "type-state":{"capability":"windows.registry","state":{
                                "field":"type","value":registry_type,"operation":"equal","datatype":"string"}},
                            "value-state":{"capability":"windows.registry","state":{
                                "field":"value","value":"opaque","operation":"equal","datatype":"string"}},
                        },
                        "tests":{"t":{"capability":"windows.registry","object":"o","states":["type-state","value-state"]}},
                    }
                }
                codes={row["code"] for row in validate_assessment_capability_semantics(doc)}
                self.assertNotIn("windows.registry.value_type_datatype",codes)

    def test_windows_view_is_not_native(self):
        self.assertNotIn("windows_view",json.dumps(self.schema))


if __name__=="__main__":
    unittest.main()
