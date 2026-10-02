#!/usr/bin/env python3
import json
from pathlib import Path
import unittest
import jsonschema
from referencing import Registry, Resource
from generate_capability_schema import generate

ROOT=Path(__file__).resolve().parents[1]

class AixAsaCapabilityTests(unittest.TestCase):
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

    def test_aix_fileset(self):
        self.validate("aix.fileset","object",{"object_title":"bos","capability":"aix.fileset","select":{"flstinst":self.e("bos.rte")}})
        self.validate("aix.fileset","collected_item",{
            "id":"aix-fs","capability":"aix.fileset","status":"exists",
            "fields":{"level":{"datatype":"version","value":"7.3.0.0"},"state":{"datatype":"string","value":"COMMITTED"}},"provenance":{}
        })

    def test_aix_fix(self):
        self.validate("aix.fix","object",{"object_title":"apar","capability":"aix.fix","select":{"apar_number":self.e("IJ00000")}})
        self.validate("aix.fix","collected_item",{
            "id":"aix-fix","capability":"aix.fix","status":"exists",
            "fields":{"installation_status":{"datatype":"string","value":"ALL_INSTALLED"}},"provenance":{}
        })

    def test_asa_line(self):
        self.validate("asa.line","object",{"object_title":"show","capability":"asa.line","select":{"show_subcommand":self.e("running-config")}})
        self.validate("asa.line","collected_item",{
            "id":"asa-line","capability":"asa.line","status":"exists",
            "fields":{"config_line":{"datatype":"string","value":"no http server enable"}},"provenance":{}
        })

    def test_asa_version_singleton(self):
        self.validate("asa.version","test",{"test_title":"ASA version","capability":"asa.version","existence":"some","match":"all"})
        self.validate("asa.version","collected_item",{
            "id":"asa-ver","capability":"asa.version","status":"exists",
            "fields":{"asa_build":{"datatype":"integer","value":10}},"provenance":{}
        })

if __name__=="__main__":
    unittest.main()
