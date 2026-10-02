#!/usr/bin/env python3
import json
from pathlib import Path
import unittest
import jsonschema
from referencing import Registry, Resource
from generate_capability_schema import generate

ROOT=Path(__file__).resolve().parents[1]

class SolarisCapabilityTests(unittest.TestCase):
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

    def test_package511(self):
        self.validate("solaris.package511","object",{
            "object_title":"pkg","capability":"solaris.package511",
            "select":{"publisher":self.e("solaris"),"name":self.e("pkg:/system/library"),"version":self.e("1.0","version"),"timestamp":self.e("2026-01-01")}
        })
        self.validate("solaris.package511","collected_item",{
            "id":"p511","capability":"solaris.package511","status":"exists",
            "fields":{"updates_available":{"datatype":"boolean","value":False}},"provenance":{}
        })

    def test_legacy_package(self):
        self.validate("solaris.package","collected_item",{
            "id":"pkg","capability":"solaris.package","status":"exists",
            "fields":{"pkginst":{"datatype":"string","value":"SUNWfoo"},"version":{"datatype":"string","value":"1.0"}},"provenance":{}
        })

    def test_smf_protocol_multivalue(self):
        self.validate("solaris.smf","collected_item",{
            "id":"smf","capability":"solaris.smf","status":"exists",
            "fields":{"fmri":{"datatype":"string","value":"svc:/network/ssh:default"},
                      "protocol":[{"datatype":"string","value":"tcp"},{"datatype":"string","value":"tcp6"}]},"provenance":{}
        })

    def test_smfproperty_anysimple_value(self):
        self.validate("solaris.smfproperty","state",{
            "state_title":None,"capability":"solaris.smfproperty",
            "state":{"field":"value","value":22,"operation":"equal","datatype":"integer","mask":False,"match":"all","existence":"some"}
        })

if __name__=="__main__":
    unittest.main()
