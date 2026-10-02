#!/usr/bin/env python3
import json
from pathlib import Path
import unittest

import jsonschema
from referencing import Registry, Resource

from generate_capability_schema import generate

ROOT=Path(__file__).resolve().parents[1]
MAPPING=ROOT/"schema/v0.1.0/capability-mappings/independent.environmentvariable58.json"

class EnvironmentVariable58CapabilitySchemaTests(unittest.TestCase):
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

    def entity(self,value,datatype):
        return {"value":value,"operation":"equal","datatype":datatype}

    def test_pid_and_name_selectors(self):
        self.validate_def("object",{
            "object_title":"PATH for pid 1","capability":"independent.environmentvariable58",
            "select":{"pid":self.entity(1,"integer"),"name":self.entity("PATH","string")},
        })
        self.validate_def("object",{
            "object_title":"PATH for scanner","capability":"independent.environmentvariable58",
            "select":{"pid":None,"name":self.entity("PATH","string")},
        })

    def test_any_simple_value_is_shared_by_state_and_item(self):
        self.validate_def("state",{
            "state_title":None,"capability":"independent.environmentvariable58",
            "state":{"field":"value","value":42,"operation":"equal","datatype":"integer","match":"all","existence":"some"},
        })
        self.validate_def("collected_item",{
            "id":"env-1","capability":"independent.environmentvariable58","status":"exists",
            "fields":{
                "pid":{"datatype":"integer","value":1},
                "name":{"datatype":"string","value":"COUNT"},
                "value":{"datatype":"integer","value":42},
            },"provenance":{},
        })

    def test_pid_datatype_is_integer(self):
        with self.assertRaises(jsonschema.ValidationError):
            self.validate_def("collected_item",{
                "id":"env-2","capability":"independent.environmentvariable58","status":"exists",
                "fields":{"pid":{"datatype":"string","value":"1"}},"provenance":{},
            })

if __name__=="__main__":
    unittest.main()
