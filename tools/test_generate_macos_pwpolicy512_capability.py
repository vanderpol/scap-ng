#!/usr/bin/env python3
import json
from pathlib import Path
import unittest

import jsonschema
from referencing import Registry, Resource

from generate_capability_schema import generate

ROOT=Path(__file__).resolve().parents[1]
MAPPING=ROOT/"schema/v0.1.0/capability-mappings/macos.pwpolicy512.json"

class PwPolicy512CapabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mapping=json.loads(MAPPING.read_text())
        cls.schema=generate(cls.mapping,ROOT)
        common=json.loads((ROOT/"schema/v0.1.0/capability-common.schema.json").read_text())
        collected=json.loads((ROOT/"schema/v0.1.0/collected-item.schema.json").read_text())
        result_types=json.loads((ROOT/"schema/v0.1.0/result-types.schema.json").read_text())
        cls.registry=(Registry()
            .with_resource(common["$id"],Resource.from_contents(common))
            .with_resource(collected["$id"],Resource.from_contents(collected))
            .with_resource(result_types["$id"],Resource.from_contents(result_types)))

    def validate(self,kind,value):
        jsonschema.Draft202012Validator(self.schema["$defs"][kind],registry=self.registry).validate(value)

    def e(self,value,datatype="string"):
        return {"value":value,"operation":"equal","datatype":datatype,"mask":False}

    def test_global_policy_null_username(self):
        self.validate("object",{
            "object_title":"global policy","capability":"macos.pwpolicy512",
            "select":{
                "username":None,
                "authenticator":None,
                "authenticator_password":None,
                "directory_node":None,
                "xpath":self.e("/dict/key/text()")
            }
        })

    def test_value_of_multi_value_item(self):
        self.validate("collected_item",{
            "id":"pwp-1","capability":"macos.pwpolicy512","status":"exists",
            "fields":{
                "xpath":{"datatype":"string","value":"/dict/key/text()"},
                "value_of":[
                    {"datatype":"integer","value":15},
                    {"datatype":"string","value":"enabled"}
                ]
            },"provenance":{}
        })

    def test_state_uses_same_value_surface(self):
        self.validate("state",{
            "state_title":None,"capability":"macos.pwpolicy512",
            "state":{"field":"value_of","value":15,"operation":"equal","datatype":"integer",
                     "mask":False,"match":"all","existence":"some"}
        })

if __name__=="__main__":
    unittest.main()
