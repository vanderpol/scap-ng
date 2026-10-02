#!/usr/bin/env python3
import json
from pathlib import Path
import unittest

import jsonschema
from referencing import Registry, Resource

from generate_capability_schema import generate

ROOT=Path(__file__).resolve().parents[1]
MAPPING=ROOT/"schema/v0.1.0/capability-mappings/unix.shadow.json"

class UnixShadowCapabilitySchemaTests(unittest.TestCase):
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

    def entity(self,value,datatype="string"):
        return {"value":value,"operation":"equal","datatype":datatype}

    def state_entity(self,field,value,datatype="string"):
        return {
            "state_title":None,
            "capability":"unix.shadow",
            "state":{
                "field":field,"value":value,"operation":"equal","datatype":datatype,"match":"all","existence":"some",
            },
        }

    def test_username_is_object_selector(self):
        self.validate_def("object",{
            "object_title":"root shadow",
            "capability":"unix.shadow",
            "select":{"username":self.entity("root")},
        })

    def test_shadow_state_item_field_surface(self):
        encoded=json.dumps(self.schema)
        for field in ("username","password","chg_lst","chg_allow","chg_req",
                      "exp_warn","exp_inact","exp_date","flag","encrypt_method"):
            self.assertIn(field,encoded)

    def test_dual_string_integer_shadow_fields(self):
        for field in ("chg_lst","chg_allow","chg_req","exp_warn","exp_inact","exp_date","flag"):
            with self.subTest(field=field):
                self.validate_def("state",self.state_entity(field,1,"integer"))
                self.validate_def("state",self.state_entity(field,"1","string"))

    def test_encrypt_method_uses_source_vocabulary(self):
        self.validate_def("state",self.state_entity("encrypt_method","SHA-512","string"))
        with self.assertRaises(jsonschema.ValidationError):
            self.validate_def("state",self.state_entity("encrypt_method","argon2id","string"))

    def test_collected_item_reuses_same_field_types(self):
        self.validate_def("collected_item",{
            "id":"shadow-1",
            "capability":"unix.shadow",
            "status":"exists",
            "fields":{
                "username":{"datatype":"string","value":"root"},
                "chg_lst":{"datatype":"integer","value":20000},
                "encrypt_method":{"datatype":"string","value":"SHA-512"},
            },
            "provenance":{},
        })
        with self.assertRaises(jsonschema.ValidationError):
            self.validate_def("collected_item",{
                "id":"shadow-2",
                "capability":"unix.shadow",
                "status":"exists",
                "fields":{"chg_lst":{"datatype":"boolean","value":True}},
                "provenance":{},
            })

if __name__=="__main__":
    unittest.main()
