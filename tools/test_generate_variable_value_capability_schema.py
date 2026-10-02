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
MAPPING=ROOT/"schema/v0.1.0/capability-mappings/variable.value.json"


class VariableValueCapabilitySchemaTests(unittest.TestCase):
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

    def test_direct_variable_source_replaces_fake_object(self):
        self.assertNotIn("object",self.schema["$defs"])
        test_schema=self.schema["$defs"]["test"]
        self.assertIn("variable",test_schema["required"])
        self.assertNotIn("object",test_schema["properties"])

        self.validate_def("test",{
            "test_title":"threshold check",
            "capability":"variable.value",
            "variable":"threshold",
            "existence":"some",
            "match":"all",
            "states":["expected"],
        })

    def test_object_backed_shape_is_rejected(self):
        with self.assertRaises(jsonschema.ValidationError):
            self.validate_def("test",{
                "test_title":"legacy-shaped check",
                "capability":"variable.value",
                "object":"variable-object",
                "existence":"some",
                "match":"all",
            })

    def test_state_has_only_native_value_field(self):
        state_schema=self.schema["$defs"]["state"]
        def field_consts(node):
            values=set()
            if isinstance(node,dict):
                field=(node.get("properties") or {}).get("field")
                if isinstance(field,dict):
                    if isinstance(field.get("const"),str):
                        values.add(field["const"])
                    for value in field.get("enum") or []:
                        if isinstance(value,str):
                            values.add(value)
                for value in node.values():
                    values.update(field_consts(value))
            elif isinstance(node,list):
                for value in node:
                    values.update(field_consts(value))
            return values
        self.assertEqual(field_consts(state_schema),{"value"})
        encoded=json.dumps(self.schema)
        self.assertNotIn('"var_ref"',encoded)

        self.validate_def("state",{
            "state_title":"minimum",
            "capability":"variable.value",
            "state":{
                "field":"value",
                "value":5,
                "operation":"greater_or_equal",
                "datatype":"integer",
                "match":"all",
                "existence":"some",
            },
        })

    def test_variable_source_must_exist(self):
        missing={
            "assessment":{
                "variables":{},
                "objects":{},
                "states":{},
                "tests":{
                    "t":{
                        "capability":"variable.value",
                        "variable":"missing",
                    }
                },
            }
        }
        rows=validate_assessment_capability_semantics(missing)
        self.assertIn("variable.value.source_exists",{row["code"] for row in rows})

        present=json.loads(json.dumps(missing))
        present["assessment"]["variables"]["missing"]={"datatype":"integer"}
        rows=validate_assessment_capability_semantics(present)
        self.assertNotIn("variable.value.source_exists",{row["code"] for row in rows})

    def test_legacy_variable_object_is_not_runtime_schema(self):
        encoded=json.dumps(self.schema)
        self.assertNotIn("variable_object",encoded)
        self.assertNotIn("independent",encoded.lower())


if __name__=="__main__":
    unittest.main()
