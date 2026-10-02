#!/usr/bin/env python3
import json
from pathlib import Path
import unittest

import jsonschema
from referencing import Registry, Resource

from generate_capability_schema import generate


ROOT=Path(__file__).resolve().parents[1]
MAPPING=ROOT/"schema/v0.1.0/capability-mappings/windows.userright.json"


class WindowsUserRightCapabilitySchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mapping=json.loads(MAPPING.read_text(encoding="utf-8"))
        cls.schema=generate(cls.mapping,ROOT)
        common=json.loads((ROOT/"schema/v0.1.0/capability-common.schema.json").read_text(encoding="utf-8"))
        cls.registry=Registry().with_resource(common["$id"],Resource.from_contents(common))

    def validate_def(self,name,value):
        jsonschema.Draft202012Validator(self.schema["$defs"][name],registry=self.registry).validate(value)

    def entity(self,value,operation="equal"):
        return {"value":value,"operation":operation,"datatype":"string","mask":False}

    def test_valid_userright_object(self):
        self.validate_def("object",{
            "object_title":"Log on as a service",
            "capability":"windows.userright",
            "select":{"userright":"SE_SERVICE_LOGON_NAME"},
        })

    def test_invalid_userright_constant_rejected(self):
        with self.assertRaises(jsonschema.ValidationError):
            self.validate_def("object",{
                "object_title":None,
                "capability":"windows.userright",
                "select":{"userright":"SeServiceLogonRight"},
            })

    def test_state_preserves_trustee_fields(self):
        self.validate_def("state",{
            "state_title":None,
            "capability":"windows.userright",
            "state":{
                "field":"trustee_sid",
                "value":"S-1-5-32-544",
                "operation":"equal",
                "datatype":"string",
                "mask":False,
                "match":"all",
                "existence":"some",
            },
        })
        self.validate_def("state",{
            "state_title":None,
            "capability":"windows.userright",
            "state":{
                "field":"trustee_name",
                "value":"BUILTIN\\Administrators",
                "operation":"equal_ci",
                "datatype":"string",
                "mask":False,
                "match":"all",
                "existence":"some",
            },
        })

    def test_state_userright_values_preserved(self):
        self.validate_def("state",{
            "state_title":None,
            "capability":"windows.userright",
            "state":{
                "field":"userright",
                "value":"SE_DENY_REMOTE_INTERACTIVE_LOGON_NAME",
                "operation":"equal",
                "datatype":"string",
                "mask":False,
                "match":"all",
                "existence":"some",
            },
        })

    def test_semantic_rules_preserved(self):
        ids={row["id"] for row in self.schema["x-semantic-validator-rules"]}
        self.assertIn("windows.userright.filter_state_capability",ids)
        self.assertIn("windows.userright.trustee_name_case",ids)


if __name__=="__main__":
    unittest.main()
