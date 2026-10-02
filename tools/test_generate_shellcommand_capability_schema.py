#!/usr/bin/env python3
import json
from pathlib import Path
import unittest

import jsonschema
from referencing import Registry, Resource

from generate_capability_schema import generate


ROOT=Path(__file__).resolve().parents[1]
MAPPING=ROOT/"schema/v0.1.0/capability-mappings/independent.shellcommand.json"


class ShellCommandCapabilitySchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mapping=json.loads(MAPPING.read_text(encoding="utf-8"))
        cls.schema=generate(cls.mapping,ROOT)
        common=json.loads((ROOT/"schema/v0.1.0/capability-common.schema.json").read_text(encoding="utf-8"))
        cls.registry=Registry().with_resource(common["$id"],Resource.from_contents(common))

    def validate_def(self,name,value):
        jsonschema.Draft202012Validator(self.schema["$defs"][name],registry=self.registry).validate(value)

    def test_command_collection_shape(self):
        self.validate_def("object",{
            "object_title":"query current setting",
            "capability":"independent.shellcommand",
            "collect":{
                "shell":"bash",
                "command":"printf 'enabled\\n'",
                "error_if_exit_status_not_0":False,
                "error_if_stderr_exists":False,
            },
        })

    def test_optional_pattern_is_supported(self):
        self.validate_def("object",{
            "object_title":"filter output",
            "capability":"independent.shellcommand",
            "collect":{
                "shell":"pwsh",
                "command":"Write-Output enabled",
                "pattern":"^(enabled)$",
                "error_if_exit_status_not_0":True,
                "error_if_stderr_exists":True,
            },
        })

    def test_behavior_defaults_must_be_materialized(self):
        with self.assertRaises(jsonschema.ValidationError):
            self.validate_def("object",{
                "object_title":None,
                "capability":"independent.shellcommand",
                "collect":{
                    "shell":"bash",
                    "command":"true",
                },
            })

    def test_pwsh_is_testable_in_state(self):
        self.validate_def("state",{
            "state_title":None,
            "capability":"independent.shellcommand",
            "state":{
                "field":"shell",
                "value":"pwsh",
                "operation":"equal",
                "datatype":"string",
                "mask":False,
                "match":"all",
                "existence":"some",
            },
        })

    def test_exit_status_is_integer(self):
        self.validate_def("state",{
            "state_title":None,
            "capability":"independent.shellcommand",
            "state":{
                "field":"exit_status",
                "value":0,
                "operation":"equal",
                "datatype":"integer",
                "mask":False,
                "match":"all",
                "existence":"some",
            },
        })

    def test_semantic_guardrails_are_retained(self):
        ids={row["id"] for row in self.schema["x-semantic-validator-rules"]}
        self.assertIn("independent.shellcommand.trusted_content",ids)
        self.assertIn("independent.shellcommand.not_generic_escape_hatch",ids)


if __name__=="__main__":
    unittest.main()
