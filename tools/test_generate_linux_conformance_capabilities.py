#!/usr/bin/env python3
import json
from pathlib import Path
import unittest

import jsonschema
from referencing import Registry, Resource

from generate_capability_schema import generate

ROOT=Path(__file__).resolve().parents[1]

class LinuxConformanceCapabilitiesTests(unittest.TestCase):
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
        mapping=json.loads((ROOT/f"schema/v0.1.0/capability-mappings/{cap}.json").read_text())
        return generate(mapping,ROOT)

    def validate(self,cap,kind,value):
        jsonschema.Draft202012Validator(self.schema(cap)["$defs"][kind],registry=self.registry).validate(value)

    def entity(self,value,datatype="string"):
        return {"value":value,"operation":"equal","datatype":datatype,"mask":False}

    def test_apparmorstatus_is_singleton(self):
        self.validate("linux.apparmorstatus","test",{
            "test_title":"AppArmor","capability":"linux.apparmorstatus","existence":"some","match":"all"
        })
        self.validate("linux.apparmorstatus","collected_item",{
            "id":"aa-1","capability":"linux.apparmorstatus","status":"exists",
            "fields":{"loaded_profiles_count":{"datatype":"integer","value":12}},"provenance":{}
        })

    def test_dpkginfo_dual_datatypes(self):
        self.validate("linux.dpkginfo","object",{
            "object_title":"pkg","capability":"linux.dpkginfo",
            "select":{"name":self.entity("openssh-server")}
        })
        for datatype,value in (("string","(none)"),("integer",0)):
            self.validate("linux.dpkginfo","state",{
                "state_title":None,"capability":"linux.dpkginfo",
                "state":{"field":"epoch","value":value,"operation":"equal","datatype":datatype,
                         "mask":False,"match":"all","existence":"some"}
            })

    def test_inet_listening_server_state_item_surface(self):
        self.validate("linux.inetlisteningservers","object",{
            "object_title":"ssh","capability":"linux.inetlisteningservers",
            "select":{
                "protocol":self.entity("tcp"),
                "local_address":self.entity("0.0.0.0"),
                "local_port":self.entity(22,"integer")
            }
        })
        self.validate("linux.inetlisteningservers","collected_item",{
            "id":"net-1","capability":"linux.inetlisteningservers","status":"exists",
            "fields":{
                "protocol":{"datatype":"string","value":"tcp"},
                "local_port":{"datatype":"integer","value":22},
                "pid":{"datatype":"integer","value":123}
            },"provenance":{}
        })

    def test_kernelmodule_boolean_status(self):
        self.validate("linux.kernelmodule","object",{
            "object_title":"usb","capability":"linux.kernelmodule",
            "select":{"module_name":self.entity("usb-storage")}
        })
        self.validate("linux.kernelmodule","collected_item",{
            "id":"km-1","capability":"linux.kernelmodule","status":"exists",
            "fields":{
                "module_name":{"datatype":"string","value":"usb-storage"},
                "loaded":{"datatype":"boolean","value":False},
                "loadable":{"datatype":"boolean","value":False}
            },"provenance":{}
        })

if __name__=="__main__":
    unittest.main()
