#!/usr/bin/env python3
import json
from pathlib import Path
import unittest

import jsonschema
from referencing import Registry, Resource

from generate_capability_schema import generate


ROOT=Path(__file__).resolve().parents[1]
MAPPING=ROOT/"schema/v0.1.0/capability-mappings/windows.cmdlet.json"


class WindowsCmdletCapabilitySchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mapping=json.loads(MAPPING.read_text(encoding="utf-8"))
        cls.schema=generate(cls.mapping,ROOT)
        common=json.loads((ROOT/"schema/v0.1.0/capability-common.schema.json").read_text(encoding="utf-8"))
        cls.registry=Registry().with_resource(common["$id"],Resource.from_contents(common))

    def validate_def(self,name,value):
        jsonschema.Draft202012Validator(self.schema["$defs"][name],registry=self.registry).validate(value)

    def object_record(self):
        return {
            "fields":{
                "name":{
                    "value":"Spooler",
                    "operation":"equal",
                    "datatype":"string",
                    "mask":False,
                    "match":"all",
                }
            },
            "mask":False,
        }

    def test_structured_cmdlet_invocation(self):
        self.validate_def("object",{
            "object_title":"Get-Service Spooler",
            "capability":"windows.cmdlet",
            "collect":{
                "module_name":"Microsoft.PowerShell.Management",
                "module_id":None,
                "module_version":None,
                "verb":"Get",
                "noun":"Service",
                "parameters":self.object_record(),
                "select":None,
            },
        })

    def test_nillable_fields_are_explicit_null(self):
        self.validate_def("object",{
            "object_title":None,
            "capability":"windows.cmdlet",
            "collect":{
                "module_name":None,
                "module_id":None,
                "module_version":None,
                "verb":"Get",
                "noun":"Process",
                "parameters":None,
                "select":None,
            },
        })

    def test_record_state_is_not_flattened(self):
        self.validate_def("state",{
            "state_title":None,
            "capability":"windows.cmdlet",
            "state":{
                "field":"value",
                "record":{
                    "fields":{
                        "status":{
                            "value":"Running",
                            "operation":"equal",
                            "datatype":"string",
                            "mask":False,
                            "match":"all",
                            "existence":"some",
                        }
                    },
                    "match":"all",
                    "existence":"some",
                    "mask":False,
                },
            },
        })

    def test_parent_record_semantics_are_implicit(self):
        encoded=json.dumps(self.schema)
        self.assertIn("object_record",encoded)
        self.assertNotIn('"record_operation"',encoded)

    def test_guardrails_preserved(self):
        ids={row["id"] for row in self.schema["x-semantic-validator-rules"]}
        self.assertIn("windows.cmdlet.select_no_wildcard",ids)
        self.assertIn("windows.cmdlet.record_fields",ids)


if __name__=="__main__":
    unittest.main()
