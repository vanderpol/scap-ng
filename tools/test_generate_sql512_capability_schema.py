#!/usr/bin/env python3
import json
from pathlib import Path
import unittest

import jsonschema
from referencing import Registry, Resource

from generate_capability_schema import generate

ROOT=Path(__file__).resolve().parents[1]
MAPPING=ROOT/"schema/v0.1.0/capability-mappings/independent.sql512.json"

class SQL512CapabilityTests(unittest.TestCase):
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

    def test_newer_item_engine_is_filterable(self):
        self.validate("object",{
            "object_title":"Aurora query","capability":"independent.sql512",
            "collect":{
                "engine":"aurora","version":"15","instance":"prod","database":"app","sql":"select 1"
            }
        })
        self.validate("state",{
            "state_title":None,"capability":"independent.sql512",
            "state":{
                "field":"engine","value":"aurora","operation":"equal","datatype":"string",
                "mask":False,"match":"all","existence":"some"
            }
        })

    def test_record_result_is_multi_valued(self):
        self.validate("collected_item",{
            "id":"sql-1","capability":"independent.sql512","status":"exists",
            "fields":{
                "engine":{"datatype":"string","value":"postgresql"},
                "result":[
                    {"datatype":"record","value":{"name":{"datatype":"string","value":"alice"}}},
                    {"datatype":"record","value":{"name":{"datatype":"string","value":"bob"}}}
                ]
            },"provenance":{}
        })

    def test_unknown_engine_rejected(self):
        with self.assertRaises(jsonschema.ValidationError):
            self.validate("object",{
                "object_title":"bad","capability":"independent.sql512",
                "collect":{"engine":"madeupdb","version":"1","instance":"x","database":"x","sql":"select 1"}
            })

if __name__=="__main__":
    unittest.main()
