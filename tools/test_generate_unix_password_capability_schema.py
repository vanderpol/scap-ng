#!/usr/bin/env python3
import json
from pathlib import Path
import unittest

import jsonschema
from referencing import Registry, Resource

from generate_capability_schema import generate


ROOT=Path(__file__).resolve().parents[1]
MAPPING=ROOT/"schema/v0.1.0/capability-mappings/unix.password.json"


class UnixPasswordCapabilitySchemaTests(unittest.TestCase):
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

    def entity(self,value,operation="equal",datatype="string"):
        return {"value":value,"operation":operation,"datatype":datatype,"mask":False}

    def test_username_selector(self):
        self.validate_def("object",{
            "object_title":"root account",
            "capability":"unix.password",
            "select":{"username":self.entity("root")},
        })

    def test_existing_oval_field_names_are_preserved(self):
        encoded=json.dumps(self.schema)
        for field in ("user_id","group_id","gcos","home_dir","login_shell","last_login"):
            self.assertIn(field,encoded)

    def test_user_and_group_ids_allow_string_or_integer(self):
        for field in ("user_id","group_id"):
            with self.subTest(field=field):
                self.validate_def("state",{
                    "state_title":None,
                    "capability":"unix.password",
                    "state":{
                        "field":field,"value":0,"operation":"equal","datatype":"integer",
                        "mask":False,"match":"all","existence":"some",
                    },
                })
                self.validate_def("state",{
                    "state_title":None,
                    "capability":"unix.password",
                    "state":{
                        "field":field,"value":"0","operation":"equal","datatype":"string",
                        "mask":False,"match":"all","existence":"some",
                    },
                })

    def test_collected_item_reuses_state_field_surface(self):
        self.validate_def("collected_item",{
            "id":"item-1",
            "capability":"unix.password",
            "status":"exists",
            "fields":{
                "username":{"datatype":"string","value":"root"},
                "user_id":{"datatype":"integer","value":0},
                "group_id":{"datatype":"integer","value":0},
                "home_dir":{"datatype":"string","value":"/root"},
            },
            "provenance":{},
        })
        with self.assertRaises(jsonschema.ValidationError):
            self.validate_def("collected_item",{
                "id":"item-2",
                "capability":"unix.password",
                "status":"exists",
                "fields":{
                    "user_id":{"datatype":"boolean","value":False},
                },
                "provenance":{},
            })


if __name__=="__main__":
    unittest.main()
