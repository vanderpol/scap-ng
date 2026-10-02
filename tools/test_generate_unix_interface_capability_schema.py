#!/usr/bin/env python3
import json
from pathlib import Path
import unittest

import jsonschema
from referencing import Registry, Resource

from generate_capability_schema import generate

ROOT=Path(__file__).resolve().parents[1]
MAPPING=ROOT/"schema/v0.1.0/capability-mappings/unix.interface.json"

class UnixInterfaceCapabilitySchemaTests(unittest.TestCase):
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

    def state(self,field,value):
        return {"state_title":None,"capability":"unix.interface",
                "state":{"field":field,"value":value,"operation":"equal","datatype":"string","match":"all","existence":"some"}}

    def test_name_object_selector(self):
        self.validate_def("object",{
            "object_title":"eth0","capability":"unix.interface",
            "select":{"name":{"value":"eth0","operation":"equal","datatype":"string"}},
        })

    def test_interface_type_vocabulary(self):
        self.validate_def("state",self.state("type","ARPHRD_ETHER"))
        with self.assertRaises(jsonschema.ValidationError):
            self.validate_def("state",self.state("type","ethernet"))

    def test_flags_are_multi_valued_collected_item(self):
        self.validate_def("collected_item",{
            "id":"if-1","capability":"unix.interface","status":"exists",
            "fields":{
                "name":{"datatype":"string","value":"eth0"},
                "flag":[{"datatype":"string","value":"UP"},{"datatype":"string","value":"BROADCAST"}],
            },"provenance":{},
        })

if __name__=="__main__":
    unittest.main()
