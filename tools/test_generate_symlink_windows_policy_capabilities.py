#!/usr/bin/env python3
import json
from pathlib import Path
import unittest

import jsonschema
from referencing import Registry, Resource

from generate_capability_schema import generate


ROOT=Path(__file__).resolve().parents[1]
COMMON=json.loads((ROOT/"schema/v0.1.0/capability-common.schema.json").read_text(encoding="utf-8"))
REGISTRY=Registry().with_resource(COMMON["$id"],Resource.from_contents(COMMON))


def generated(name):
    mapping=json.loads((ROOT/f"schema/v0.1.0/capability-mappings/{name}.json").read_text(encoding="utf-8"))
    return mapping,generate(mapping,ROOT)


def validate(schema,name,value):
    jsonschema.Draft202012Validator(schema["$defs"][name],registry=REGISTRY).validate(value)


def entity(value,operation="equal",datatype="string"):
    return {"value":value,"operation":operation,"datatype":datatype}


class UnixSymlinkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mapping,cls.schema=generated("unix.symlink")

    def test_symlink_path_and_canonical_path(self):
        validate(self.schema,"object",{
            "object_title":"current symlink",
            "capability":"unix.symlink",
            "select":{"full_path":entity("/etc/mtab")},
        })
        validate(self.schema,"state",{
            "state_title":None,
            "capability":"unix.symlink",
            "state":{
                "field":"canonical_path","value":"/proc/mounts","operation":"equal",
                "datatype":"string","match":"all","existence":"some",
            },
        })


class WindowsLockoutPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mapping,cls.schema=generated("windows.lockoutpolicy")

    def test_singleton_has_no_object(self):
        self.assertNotIn("object",self.schema["$defs"])
        validate(self.schema,"test",{
            "test_title":None,"capability":"windows.lockoutpolicy",
            "existence":"all","match":"all","states":["lockout-threshold"],
        })

    def test_lockout_threshold_is_integer(self):
        validate(self.schema,"state",{
            "state_title":None,"capability":"windows.lockoutpolicy",
            "state":{
                "field":"lockout_threshold","value":5,"operation":"equal","datatype":"integer","match":"all","existence":"some",
            },
        })


class WindowsPasswordPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mapping,cls.schema=generated("windows.passwordpolicy")

    def test_singleton_has_no_object(self):
        self.assertNotIn("object",self.schema["$defs"])

    def test_integer_and_boolean_policy_fields(self):
        validate(self.schema,"state",{
            "state_title":None,"capability":"windows.passwordpolicy",
            "state":{
                "field":"min_passwd_len","value":14,"operation":"greater_or_equal","datatype":"integer","match":"all","existence":"some",
            },
        })
        validate(self.schema,"state",{
            "state_title":None,"capability":"windows.passwordpolicy",
            "state":{
                "field":"password_complexity","value":True,"operation":"equal","datatype":"boolean","match":"all","existence":"some",
            },
        })


if __name__=="__main__":
    unittest.main()
