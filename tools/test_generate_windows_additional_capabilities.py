#!/usr/bin/env python3
import json
from pathlib import Path
import unittest
import jsonschema
from referencing import Registry, Resource
from generate_capability_schema import generate

ROOT=Path(__file__).resolve().parents[1]

class WindowsAdditionalCapabilitiesTests(unittest.TestCase):
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
        return {"value":value,"operation":"equal","datatype":datatype}

    def test_appcmd_identifier_vocabulary(self):
        self.validate("windows.appcmd","object",{
            "object_title":"IIS site","capability":"windows.appcmd",
            "select":{"identifier_type":"Site","identifier":self.e("Default Web Site"),"parameter":self.e("state")}
        })

    def test_appcmdlistconfig_nullable_identifier(self):
        self.validate("windows.appcmdlistconfig","object",{
            "object_title":"IIS config","capability":"windows.appcmdlistconfig",
            "select":{"identifier_type":"Webserver","identifier":None,"section":self.e("system.webServer/security"),"parameter":self.e("enabled")}
        })

    def test_group_sid_multivalue_membership(self):
        self.validate("windows.group_sid","collected_item",{
            "id":"g1","capability":"windows.group_sid","status":"exists",
            "fields":{
                "group_sid":{"datatype":"string","value":"S-1-5-32-544"},
                "user_sid":[{"datatype":"string","value":"S-1-5-21-1"},{"datatype":"string","value":"S-1-5-21-2"}]
            },"provenance":{}
        })

    def test_service_multivalue_fields(self):
        self.validate("windows.service","collected_item",{
            "id":"svc","capability":"windows.service","status":"exists",
            "fields":{
                "service_name":{"datatype":"string","value":"WinDefend"},
                "service_type":[{"datatype":"string","value":"SERVICE_WIN32_OWN_PROCESS"}],
                "controls_accepted":[{"datatype":"string","value":"SERVICE_ACCEPT_STOP"}],
                "dependencies":[{"datatype":"string","value":"RpcSs"}]
            },"provenance":{}
        })

    def test_sid_behavior_defaults_materialized(self):
        self.validate("windows.sid","object",{
            "object_title":"Administrators","capability":"windows.sid",
            "select":{"trustee_name":self.e("BUILTIN\\Administrators")},
            "collect":{"include_group":True,"resolve_group":False}
        })
        self.validate("windows.sid_sid","object",{
            "object_title":"Administrators SID","capability":"windows.sid_sid",
            "select":{"trustee_sid":self.e("S-1-5-32-544")},
            "collect":{"include_group":True,"resolve_group":False}
        })

    def test_user_sid55_multivalue_groups(self):
        self.validate("windows.user_sid55","collected_item",{
            "id":"u1","capability":"windows.user_sid55","status":"exists",
            "fields":{
                "user_sid":{"datatype":"string","value":"S-1-5-21-1000"},
                "group_sid":[{"datatype":"string","value":"S-1-5-32-545"}],
                "group":[{"datatype":"string","value":"Users"}]
            },"provenance":{}
        })

if __name__=="__main__":
    unittest.main()
