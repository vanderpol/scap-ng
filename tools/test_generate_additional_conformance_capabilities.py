#!/usr/bin/env python3
import json
from pathlib import Path
import unittest

import jsonschema
from referencing import Registry, Resource

from generate_capability_schema import generate

ROOT=Path(__file__).resolve().parents[1]

class AdditionalConformanceCapabilitiesTests(unittest.TestCase):
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
        schema=self.schema(cap)
        jsonschema.Draft202012Validator(schema["$defs"][kind],registry=self.registry).validate(value)

    def entity(self,value,datatype="string"):
        return {"value":value,"operation":"equal","datatype":datatype,"mask":False}

    def test_uname_singleton_and_item(self):
        self.validate("unix.uname","test",{
            "test_title":"uname","capability":"unix.uname",
            "existence":"some","match":"all",
        })
        self.validate("unix.uname","collected_item",{
            "id":"uname-1","capability":"unix.uname","status":"exists",
            "fields":{"os_name":{"datatype":"string","value":"Linux"}},"provenance":{},
        })

    def test_sshd_multivalue_item(self):
        self.validate("unix.sshd","object",{
            "object_title":"sshd","capability":"unix.sshd",
            "select":{"filepath":self.entity("/etc/ssh/sshd_config"),"name":self.entity("ciphers")},
        })
        self.validate("unix.sshd","collected_item",{
            "id":"sshd-1","capability":"unix.sshd","status":"exists",
            "fields":{"value":[
                {"datatype":"string","value":"aes256-gcm@openssh.com"},
                {"datatype":"string","value":"aes256-ctr"}
            ]},"provenance":{},
        })

    def test_process58_posix_capability_is_multivalue(self):
        self.validate("unix.process58","object",{
            "object_title":"sshd proc","capability":"unix.process58",
            "select":{"pid":self.entity(1,"integer")},
        })
        self.validate("unix.process58","collected_item",{
            "id":"proc-1","capability":"unix.process58","status":"exists",
            "fields":{
                "pid":{"datatype":"integer","value":1},
                "posix_capability":[
                    {"datatype":"string","value":"CAP_CHOWN"},
                    {"datatype":"string","value":"CAP_SETUID"}
                ]
            },"provenance":{},
        })

    def test_systemd_dependencies_are_multivalue(self):
        self.validate("linux.systemdunitdependency","collected_item",{
            "id":"unit-1","capability":"linux.systemdunitdependency","status":"exists",
            "fields":{
                "unit":{"datatype":"string","value":"sshd.service"},
                "dependency":[
                    {"datatype":"string","value":"network.target"},
                    {"datatype":"string","value":"system.slice"}
                ]
            },"provenance":{},
        })

    def test_selinuxboolean_boolean_types(self):
        self.validate("linux.selinuxboolean","state",{
            "state_title":None,"capability":"linux.selinuxboolean",
            "state":{"field":"current_status","value":True,"operation":"equal","datatype":"boolean",
                     "mask":False,"match":"all","existence":"some"},
        })
        with self.assertRaises(jsonschema.ValidationError):
            self.validate("linux.selinuxboolean","collected_item",{
                "id":"bool-1","capability":"linux.selinuxboolean","status":"exists",
                "fields":{"current_status":{"datatype":"string","value":"true"}},"provenance":{},
            })

    def test_sestatus_singleton(self):
        self.validate("linux.sestatus","test",{
            "test_title":"SELinux mode","capability":"linux.sestatus",
            "existence":"some","match":"all",
        })
        self.validate("linux.sestatus","collected_item",{
            "id":"se-1","capability":"linux.sestatus","status":"exists",
            "fields":{"current_mode":{"datatype":"string","value":"enforcing"}},"provenance":{},
        })

if __name__=="__main__":
    unittest.main()
