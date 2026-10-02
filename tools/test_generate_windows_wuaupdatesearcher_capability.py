#!/usr/bin/env python3
import json
from pathlib import Path
import unittest
import jsonschema
from referencing import Registry, Resource
from generate_capability_schema import generate

ROOT=Path(__file__).resolve().parents[1]
MAPPING=ROOT/"schema/v0.1.0/capability-mappings/windows.wuaupdatesearcher.json"

class WuaUpdateSearcherCapabilityTests(unittest.TestCase):
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

    def test_direct_object_materializes_superseded_behavior(self):
        self.validate("object",{
            "object_title":"updates","capability":"windows.wuaupdatesearcher",
            "select":{"search_criteria":self.e("IsInstalled=0")},
            "collect":{"include_superseded_updates":True}
        })

    def test_source_path_is_filterable_native_state(self):
        self.validate("state",{
            "state_title":None,"capability":"windows.wuaupdatesearcher",
            "state":{"field":"source_path","value":"https://wsus.example/","operation":"equal",
                     "datatype":"string","mask":False,"match":"all","existence":"some"}
        })

    def test_source_path_is_collected_item_field(self):
        self.validate("collected_item",{
            "id":"wua-1","capability":"windows.wuaupdatesearcher","status":"exists",
            "fields":{
                "source":{"datatype":"string","value":"WSUS"},
                "source_path":{"datatype":"string","value":"https://wsus.example/"},
                "days_since_source_modified":{"datatype":"integer","value":0}
            },"provenance":{}
        })

    def test_source_vocabulary(self):
        self.validate("state",{
            "state_title":None,"capability":"windows.wuaupdatesearcher",
            "state":{"field":"source","value":"Offline_Cab_File","operation":"equal",
                     "datatype":"string","mask":False,"match":"all","existence":"some"}
        })
        with self.assertRaises(jsonschema.ValidationError):
            self.validate("state",{
                "state_title":None,"capability":"windows.wuaupdatesearcher",
                "state":{"field":"source","value":"Internet","operation":"equal",
                         "datatype":"string","mask":False,"match":"all","existence":"some"}
            })

if __name__=="__main__":
    unittest.main()
