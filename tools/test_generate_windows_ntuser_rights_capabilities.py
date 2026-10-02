#!/usr/bin/env python3
import json
from pathlib import Path
import unittest
import jsonschema
from referencing import Registry, Resource
from generate_capability_schema import generate

ROOT=Path(__file__).resolve().parents[1]

class CapabilityDefaultsAndRightsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        common=json.loads((ROOT/"schema/v0.1.0/capability-common.schema.json").read_text())
        collected=json.loads((ROOT/"schema/v0.1.0/collected-item.schema.json").read_text())
        result_types=json.loads((ROOT/"schema/v0.1.0/result-types.schema.json").read_text())
        cls.registry=(Registry()
            .with_resource(common["$id"],Resource.from_contents(common))
            .with_resource(collected["$id"],Resource.from_contents(collected))
            .with_resource(result_types["$id"],Resource.from_contents(result_types)))

    def schema(self,cap):
        m=json.loads((ROOT/f"schema/v0.1.0/capability-mappings/{cap}.json").read_text())
        return generate(m,ROOT)

    def validate(self,cap,kind,value):
        jsonschema.Draft202012Validator(self.schema(cap)["$defs"][kind],registry=self.registry).validate(value)

    def e(self,value,datatype="string"):
        return {"value":value,"operation":"equal","datatype":datatype,"mask":False}

    def test_ntuser_explicit_collection_defaults(self):
        self.validate("windows.ntuser","object",{
            "object_title":"user policy","capability":"windows.ntuser",
            "select":{"key":self.e("Software\\Policies"),"name":None},
            "collect":{"include_default":False,"item_creation":"key_and_name_exist"}
        })

    def test_ntuser_collection_defaults_are_required(self):
        base={
            "object_title":"user policy","capability":"windows.ntuser",
            "select":{"key":self.e("Software\\\\Policies"),"name":None},
        }
        with self.assertRaises(jsonschema.ValidationError):
            self.validate("windows.ntuser","object",base)
        with self.assertRaises(jsonschema.ValidationError):
            self.validate("windows.ntuser","object",{**base,"collect":{"include_default":False}})

    def test_ntuser_downward_traversal(self):
        self.validate("windows.ntuser","object",{
            "object_title":"recursive policy","capability":"windows.ntuser",
            "select":{"key":self.e("Software"),"name":None},
            "traversal":{"max_depth":None},
            "collect":{"include_default":False,"item_creation":"every_ntuser"}
        })

    def test_ntuser_multivalue_registry_value(self):
        self.validate("windows.ntuser","collected_item",{
            "id":"ntu-1","capability":"windows.ntuser","status":"exists",
            "fields":{
                "key":{"datatype":"string","value":"Software\\Example"},
                "type":{"datatype":"string","value":"multi_string"},
                "value":[{"datatype":"string","value":"a"},{"datatype":"string","value":"b"}]
            },"provenance":{}
        })

    def test_linux_rpmverify_behavior_defaults_are_explicit(self):
        expected={
            "linux.rpmverifyfile":{
                "skip_link_target","skip_size","skip_owner","skip_group","skip_mtime","skip_mode",
                "skip_rdev","skip_config_files","skip_ghost_files","skip_file_digest","skip_capabilities",
            },
            "linux.rpmverifypackage":{"skip_dependencies","skip_scripts"},
        }
        for cap,names in expected.items():
            with self.subTest(cap=cap):
                schema=self.schema(cap)
                collect=schema["$defs"]["object"]["properties"]["collect"]
                self.assertEqual(set(collect["required"]),names)
                for name in names:
                    self.assertEqual(collect["properties"][name]["type"],"boolean")

    def test_sid_behavior_defaults_are_explicit(self):
        for cap in ("windows.sid","windows.sid_sid"):
            with self.subTest(cap=cap):
                schema=self.schema(cap)
                collect=schema["$defs"]["object"]["properties"]["collect"]
                self.assertEqual(set(collect["required"]),{"include_group","resolve_group"})
                self.assertEqual(collect["properties"]["include_group"]["type"],"boolean")
                self.assertEqual(collect["properties"]["resolve_group"]["type"],"boolean")

    def test_regkey_effective_rights(self):
        self.validate("windows.regkeyeffectiverights53","object",{
            "object_title":"HKLM rights","capability":"windows.regkeyeffectiverights53",
            "select":{"hive":"local_machine","key":self.e("SOFTWARE\\Example"),"trustee_sid":self.e("S-1-5-32-544")}
        })
        self.validate("windows.regkeyeffectiverights53","collected_item",{
            "id":"rke-1","capability":"windows.regkeyeffectiverights53","status":"exists",
            "fields":{
                "hive":{"datatype":"string","value":"local_machine"},
                "key":{"datatype":"string","value":"SOFTWARE\\Example"},
                "trustee_sid":{"datatype":"string","value":"S-1-5-32-544"},
                "generic_read":{"datatype":"boolean","value":True},
                "key_set_value":{"datatype":"boolean","value":False}
            },"provenance":{}
        })

if __name__=="__main__":
    unittest.main()
