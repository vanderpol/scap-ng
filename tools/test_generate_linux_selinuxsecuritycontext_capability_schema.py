#!/usr/bin/env python3
import json
from pathlib import Path
import unittest

import jsonschema
from referencing import Registry, Resource

from generate_capability_schema import generate

ROOT=Path(__file__).resolve().parents[1]
MAPPING=ROOT/"schema/v0.1.0/capability-mappings/linux.selinuxsecuritycontext.json"

class SELinuxSecurityContextCapabilitySchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mapping=json.loads(MAPPING.read_text(encoding="utf-8"))
        cls.schema=generate(cls.mapping,ROOT)
        common=json.loads((ROOT/"schema/v0.1.0/capability-common.schema.json").read_text(encoding="utf-8"))
        collected=json.loads((ROOT/"schema/v0.1.0/collected-item.schema.json").read_text(encoding="utf-8"))
        result_types=json.loads((ROOT/"schema/v0.1.0/result-types.schema.json").read_text(encoding="utf-8"))
        cls.registry=(Registry()
            .with_resource(common["$id"],Resource.from_contents(common))
            .with_resource(collected["$id"],Resource.from_contents(collected))
            .with_resource(result_types["$id"],Resource.from_contents(result_types)))

    def validate_def(self,name,value):
        jsonschema.Draft202012Validator(self.schema["$defs"][name],registry=self.registry).validate(value)

    def entity(self,value,datatype):
        return {"value":value,"operation":"equal","datatype":datatype,"mask":False}

    def test_file_and_pid_object_alternatives(self):
        self.validate_def("object",{
            "object_title":"passwd context",
            "capability":"linux.selinuxsecuritycontext",
            "select":{"full_path":self.entity("/etc/passwd","string")},
        })
        self.validate_def("object",{
            "object_title":"pid context",
            "capability":"linux.selinuxsecuritycontext",
            "select":{"pid":self.entity(1,"integer")},
        })
        self.validate_def("object",{
            "object_title":"current scanner process",
            "capability":"linux.selinuxsecuritycontext",
            "select":{"pid":None},
        })

    def test_state_and_item_share_full_context_surface(self):
        fields=(
            "full_path","directory","name","pid","user","role","type",
            "low_sensitivity","low_category","high_sensitivity","high_category",
            "rawlow_sensitivity","rawlow_category","rawhigh_sensitivity","rawhigh_category",
        )
        encoded=json.dumps(self.schema)
        for field in fields:
            self.assertIn(field,encoded)

    def test_pid_is_integer_on_state_and_item(self):
        self.validate_def("state",{
            "state_title":None,
            "capability":"linux.selinuxsecuritycontext",
            "state":{
                "field":"pid","value":1,"operation":"equal","datatype":"integer",
                "mask":False,"match":"all","existence":"some",
            },
        })
        self.validate_def("collected_item",{
            "id":"selinux-1",
            "capability":"linux.selinuxsecuritycontext",
            "status":"exists",
            "fields":{
                "pid":{"datatype":"integer","value":1},
                "type":{"datatype":"string","value":"sshd_t"},
            },
            "provenance":{},
        })
        with self.assertRaises(jsonschema.ValidationError):
            self.validate_def("collected_item",{
                "id":"selinux-2",
                "capability":"linux.selinuxsecuritycontext",
                "status":"exists",
                "fields":{"pid":{"datatype":"string","value":"1"}},
                "provenance":{},
            })

if __name__=="__main__":
    unittest.main()
