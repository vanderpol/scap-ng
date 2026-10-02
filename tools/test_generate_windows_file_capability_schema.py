#!/usr/bin/env python3
import json
from pathlib import Path
import unittest

import jsonschema
from referencing import Registry, Resource

from generate_capability_schema import generate
from validate_generated_capability_semantics import (
    validate_assessment_capability_semantics,
)


ROOT=Path(__file__).resolve().parents[1]
MAPPING=ROOT/"schema/v0.1.0/capability-mappings/windows.file.json"


class WindowsFileCapabilitySchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mapping=json.loads(MAPPING.read_text(encoding="utf-8"))
        cls.schema=generate(cls.mapping,ROOT)
        common=json.loads(
            (ROOT/"schema/v0.1.0/capability-common.schema.json").read_text(encoding="utf-8")
        )
        cls.registry=Registry().with_resource(
            common["$id"],Resource.from_contents(common)
        )

    def validate_def(self,name,value):
        jsonschema.Draft202012Validator(
            self.schema["$defs"][name],
            registry=self.registry,
        ).validate(value)

    def entity(self,value,operation="equal",datatype="string"):
        return {
            "value":value,
            "operation":operation,
            "datatype":datatype,
            "mask":False,
        }

    def test_reuses_shared_file_primitives(self):
        encoded=json.dumps(self.schema)
        self.assertIn("capability-common.schema.json#/$defs/object_entity_base",encoded)
        self.assertIn("capability-common.schema.json#/$defs/file_traversal",encoded)
        self.assertIn("capability-common.schema.json#/$defs/set_expression",encoded)
        self.assertNotIn("windows_view",encoded)
        self.assertNotIn("recurse_direction",encoded)

    def test_valid_windows_file_selection(self):
        self.validate_def("object",{
            "object_title":"Windows config files",
            "capability":"windows.file",
            "select":{
                "directory":self.entity(r"C:\Windows"),
                "name":self.entity("*.ini",operation="match"),
            },
            "traversal":{
                "max_depth":1,
                "follow_links":False,
                "filesystem":"same",
            },
        })

    def test_directory_itself_uses_null_name(self):
        self.validate_def("object",{
            "object_title":"Windows directory",
            "capability":"windows.file",
            "select":{
                "directory":self.entity(r"C:\Windows"),
                "name":None,
            },
        })

    def test_native_file_type_values(self):
        for value in ("directory","char","disk","pipe","remote","unknown"):
            with self.subTest(value=value):
                self.validate_def("state",{
                    "state_title":None,
                    "capability":"windows.file",
                    "state":{
                        "field":"type",
                        "value":value,
                        "operation":"equal",
                        "datatype":"string",
                        "mask":False,
                        "match":"all",
                        "existence":"some",
                    },
                })
        with self.assertRaises(jsonschema.ValidationError):
            self.validate_def("state",{
                "state_title":None,
                "capability":"windows.file",
                "state":{
                    "field":"type",
                    "value":"FILE_TYPE_DISK",
                    "operation":"equal",
                    "datatype":"string",
                    "mask":False,
                    "match":"all",
                    "existence":"some",
                },
            })

    def test_native_attribute_values(self):
        self.validate_def("state",{
            "state_title":None,
            "capability":"windows.file",
            "state":{
                "field":"attribute",
                "value":"reparse_point",
                "operation":"equal",
                "datatype":"string",
                "mask":False,
                "match":"any",
                "existence":"some",
            },
        })
        with self.assertRaises(jsonschema.ValidationError):
            self.validate_def("state",{
                "state_title":None,
                "capability":"windows.file",
                "state":{
                    "field":"attribute",
                    "value":"FILE_ATTRIBUTE_REPARSE_POINT",
                    "operation":"equal",
                    "datatype":"string",
                    "mask":False,
                    "match":"any",
                    "existence":"some",
                },
            })

    def test_windows_times_and_size_are_integer(self):
        for field in ("size","access_time","creation_time","modify_time"):
            with self.subTest(field=field):
                self.validate_def("state",{
                    "state_title":None,
                    "capability":"windows.file",
                    "state":{
                        "field":field,
                        "value":1,
                        "operation":"equal",
                        "datatype":"integer",
                        "mask":False,
                        "match":"all",
                        "existence":"some",
                    },
                })

    def test_product_version_can_be_string_or_version(self):
        for datatype,value in (("string","1.0 build x"),("version","1.0.0.0")):
            with self.subTest(datatype=datatype):
                self.validate_def("state",{
                    "state_title":None,
                    "capability":"windows.file",
                    "state":{
                        "field":"product_version",
                        "value":value,
                        "operation":"equal",
                        "datatype":datatype,
                        "mask":False,
                        "match":"all",
                        "existence":"some",
                    },
                })

    def test_literal_reserved_filename_characters_are_semantic_error(self):
        rows=validate_assessment_capability_semantics({
            "assessment":{
                "objects":{
                    "o":{
                        "capability":"windows.file",
                        "select":{
                            "directory":self.entity(r"C:\Windows"),
                            "name":self.entity("bad:name.txt"),
                        },
                    }
                },
                "states":{},
                "tests":{},
            }
        })
        self.assertIn(
            "windows.file.literal_name_characters",
            {row["code"] for row in rows},
        )

    def test_match_expression_may_contain_reserved_characters(self):
        rows=validate_assessment_capability_semantics({
            "assessment":{
                "objects":{
                    "o":{
                        "capability":"windows.file",
                        "select":{
                            "directory":self.entity(r"C:\Windows"),
                            "name":self.entity(r".*[:].*",operation="match"),
                        },
                    }
                },
                "states":{},
                "tests":{},
            }
        })
        self.assertNotIn(
            "windows.file.literal_name_characters",
            {row["code"] for row in rows},
        )


if __name__=="__main__":
    unittest.main()
