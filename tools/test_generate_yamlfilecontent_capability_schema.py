#!/usr/bin/env python3
import json
from pathlib import Path
import unittest

import jsonschema
from referencing import Registry, Resource

from generate_capability_schema import generate

ROOT=Path(__file__).resolve().parents[1]
MAPPING=ROOT/"schema/v0.1.0/capability-mappings/independent.yamlfilecontent.json"

class YAMLFileContentCapabilitySchemaTests(unittest.TestCase):
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

    def entity(self,value):
        return {"value":value,"operation":"equal","datatype":"string"}

    def test_file_and_inline_content_modes(self):
        self.validate_def("object",{
            "object_title":"yaml file","capability":"independent.yamlfilecontent",
            "select":{"full_path":self.entity("/etc/example.yaml"),"yamlpath":self.entity("$.a")},
        })
        self.validate_def("object",{
            "object_title":"inline yaml","capability":"independent.yamlfilecontent",
            "select":{"content":self.entity("a: 1"),"yamlpath":self.entity("$.a")},
        })

    def test_record_state_and_collected_item(self):
        self.validate_def("state",{
            "state_title":None,"capability":"independent.yamlfilecontent",
            "state":{
                "field":"value",
                "record":{
                    "fields":{
                        "myCamelCase^Key":{
                            "value":"enabled","operation":"equal","datatype":"string","match":"all","existence":"some"
                        }
                    },
                    "match":"all","existence":"some"
                }
            },
        })
        self.validate_def("collected_item",{
            "id":"yaml-1","capability":"independent.yamlfilecontent","status":"exists",
            "fields":{
                "full_path":{"datatype":"string","value":"/etc/example.yaml"},
                "yamlpath":{"datatype":"string","value":"$.a"},
                "value":[
                    {"datatype":"record","value":{"myCamelCase^Key":{"datatype":"string","value":"enabled"}}}
                ],
            },"provenance":{},
        })

    def test_legacy_windows_view_not_native(self):
        with self.assertRaises(jsonschema.ValidationError):
            self.validate_def("collected_item",{
                "id":"yaml-2","capability":"independent.yamlfilecontent","status":"exists",
                "fields":{"windows_view":{"datatype":"string","value":"64_bit"}},"provenance":{},
            })

if __name__=="__main__":
    unittest.main()
