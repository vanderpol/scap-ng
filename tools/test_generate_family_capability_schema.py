#!/usr/bin/env python3
import json
from pathlib import Path
import unittest

import jsonschema
from referencing import Registry, Resource

from generate_capability_schema import generate

ROOT=Path(__file__).resolve().parents[1]
MAPPING=ROOT/"schema/v0.1.0/capability-mappings/independent.family.json"

class FamilyCapabilitySchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mapping=json.loads(MAPPING.read_text(encoding="utf-8"))
        cls.schema=generate(cls.mapping,ROOT)
        common=json.loads((ROOT/"schema/v0.1.0/capability-common.schema.json").read_text(encoding="utf-8"))
        collected=json.loads((ROOT/"schema/v0.1.0/collected-item.schema.json").read_text(encoding="utf-8"))
        result_types=json.loads((ROOT/"schema/v0.1.0/result-types.schema.json").read_text(encoding="utf-8"))
        cls.registry=(Registry()
            .with_resource(common["$id"],Resource.from_contents(common))
            .with_resource(collected["$id"],Resource.from_contents(collected))
            .with_resource(result_types["$id"],Resource.from_contents(result_types)))

    def validate_def(self,name,value):
        jsonschema.Draft202012Validator(self.schema["$defs"][name],registry=self.registry).validate(value)

    def test_no_native_object(self):
        self.assertNotIn("object",self.schema["$defs"])
        self.validate_def("test",{
            "test_title":"is unix",
            "capability":"independent.family",
            "existence":"some",
            "match":"all",
            "states":["state-family-unix"],
        })

    def test_family_vocabulary(self):
        self.validate_def("state",{
            "state_title":None,"capability":"independent.family",
            "state":{"field":"family","value":"unix","operation":"equal","datatype":"string","match":"all","existence":"some"},
        })
        with self.assertRaises(jsonschema.ValidationError):
            self.validate_def("state",{
                "state_title":None,"capability":"independent.family",
                "state":{"field":"family","value":"linux","operation":"equal","datatype":"string","match":"all","existence":"some"},
            })

    def test_collected_family_uses_same_field(self):
        self.validate_def("collected_item",{
            "id":"family-1","capability":"independent.family","status":"exists",
            "fields":{"family":{"datatype":"string","value":"unix"}},"provenance":{},
        })

if __name__=="__main__":
    unittest.main()
