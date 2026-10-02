#!/usr/bin/env python3
import json
from pathlib import Path
import unittest
import jsonschema
from referencing import Registry, Resource
from generate_capability_schema import generate

ROOT=Path(__file__).resolve().parents[1]

class JunosPanosCapabilityTests(unittest.TestCase):
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

    def test_junos_show(self):
        self.validate("junos.show","object",{
            "object_title":"show config","capability":"junos.show",
            "select":{"subcommand":self.e("configuration system services ssh")}
        })
        self.validate("junos.show","collected_item",{
            "id":"junos","capability":"junos.show","status":"exists",
            "fields":{"value":{"datatype":"string","value":"protocol-version v2;"}},"provenance":{}
        })

    def test_panos_config_multivalue(self):
        self.validate("panos.config","collected_item",{
            "id":"pan","capability":"panos.config","status":"exists",
            "fields":{"xpath":{"datatype":"string","value":"/config/devices"},
                      "value_of":[{"datatype":"string","value":"a"},{"datatype":"integer","value":1}]},"provenance":{}
        })

    def test_panos_version_singleton(self):
        self.validate("panos.version","test",{
            "test_title":"PAN-OS version","capability":"panos.version","existence":"some","match":"all"
        })
        self.validate("panos.version","collected_item",{
            "id":"panv","capability":"panos.version","status":"exists",
            "fields":{"major_version":{"datatype":"integer","value":11},
                      "minor_version":{"datatype":"integer","value":1},
                      "model_name":{"datatype":"string","value":"PA-VM"}},"provenance":{}
        })

if __name__=="__main__":
    unittest.main()
