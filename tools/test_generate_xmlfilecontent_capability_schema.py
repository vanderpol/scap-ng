#!/usr/bin/env python3
import json
from pathlib import Path
import unittest

import jsonschema
from referencing import Registry, Resource

from generate_capability_schema import generate

ROOT=Path(__file__).resolve().parents[1]
MAPPING=ROOT/"schema/v0.1.0/capability-mappings/independent.xmlfilecontent.json"

class XMLFileContentCapabilitySchemaTests(unittest.TestCase):
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

    def behavior_defaults(self):
        return {"item_creation":"all_object_elements_fullfilled"}

    def entity(self,value,datatype="string",operation="equal"):
        return {"value":value,"operation":operation,"datatype":datatype}

    def test_full_path_and_directory_name_xpath_alternatives(self):
        self.validate_def("object",{
            "object_title":"xml direct","capability":"independent.xmlfilecontent",
            "select":{"full_path":self.entity("/etc/example.xml"),"xpath":self.entity("/a/b/text()")},
            "filesystem":"any",
            "collect":self.behavior_defaults(),
        })
        self.validate_def("object",{
            "object_title":"xml split","capability":"independent.xmlfilecontent",
            "select":{"directory":self.entity("/etc"),"name":self.entity("example.xml"),"xpath":self.entity("/a/b/text()")},
            "filesystem":"any",
            "collect":self.behavior_defaults(),
        })

    def test_item_creation_default_is_explicit(self):
        base={
            "object_title":"xml",
            "capability":"independent.xmlfilecontent",
            "select":{
                "full_path":{"value":"/etc/example.xml","operation":"equal","datatype":"string"},
                "xpath":{"value":"/a/b/text()","operation":"equal","datatype":"string"},
            },
            "filesystem":"any",
            "collect":{"item_creation":"all_object_elements_fullfilled"},
        }
        self.validate_def("object",base)
        missing={**base}
        missing.pop("collect")
        with self.assertRaises(jsonschema.ValidationError):
            self.validate_def("object",missing)
        alternate={**base,"collect":{"item_creation":"filepath_exists"}}
        self.validate_def("object",alternate)

    def test_value_of_is_multi_valued_item_with_single_state_field(self):
        self.validate_def("state",{
            "state_title":None,"capability":"independent.xmlfilecontent",
            "state":{"field":"value_of","value":"enabled","operation":"equal","datatype":"string","match":"all","existence":"some"},
        })
        self.validate_def("collected_item",{
            "id":"xml-1","capability":"independent.xmlfilecontent","status":"exists",
            "fields":{
                "full_path":{"datatype":"string","value":"/etc/example.xml"},
                "xpath":{"datatype":"string","value":"/a/b/text()"},
                "value_of":[
                    {"datatype":"string","value":"enabled"},
                    {"datatype":"integer","value":1}
                ],
            },"provenance":{},
        })

    def test_deprecated_windows_view_not_native(self):
        with self.assertRaises(jsonschema.ValidationError):
            self.validate_def("collected_item",{
                "id":"xml-2","capability":"independent.xmlfilecontent","status":"exists",
                "fields":{"windows_view":{"datatype":"string","value":"64_bit"}},"provenance":{},
            })

if __name__=="__main__":
    unittest.main()
