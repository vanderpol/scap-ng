#!/usr/bin/env python3
import json
from pathlib import Path
import unittest

import jsonschema
from referencing import Registry, Resource

from generate_capability_schema import generate
from validate_generated_capability_semantics import validate_assessment_capability_semantics


ROOT=Path(__file__).resolve().parents[1]
MAPPING=ROOT/"schema/v0.1.0/capability-mappings/windows.fileeffectiverights53.json"


class WindowsFileEffectiveRights53Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mapping=json.loads(MAPPING.read_text(encoding="utf-8"))
        cls.schema=generate(cls.mapping,ROOT)
        common=json.loads((ROOT/"schema/v0.1.0/capability-common.schema.json").read_text(encoding="utf-8"))
        cls.registry=Registry().with_resource(common["$id"],Resource.from_contents(common))

    def validate_def(self,name,value):
        jsonschema.Draft202012Validator(self.schema["$defs"][name],registry=self.registry).validate(value)

    def entity(self,value,operation="equal",datatype="string"):
        return {"value":value,"operation":operation,"datatype":datatype}

    def test_file_and_trustee_sid_are_both_required(self):
        self.validate_def("object",{
            "object_title":"Administrators rights on hosts",
            "capability":"windows.fileeffectiverights53",
            "select":{
                "full_path":self.entity(r"C:\\Windows\\System32\\drivers\\etc\\hosts"),
                "trustee_sid":self.entity("S-1-5-32-544"),
            },
        })
        with self.assertRaises(jsonschema.ValidationError):
            self.validate_def("object",{
                "object_title":None,
                "capability":"windows.fileeffectiverights53",
                "select":{"full_path":self.entity(r"C:\\Windows\\win.ini")},
            })

    def test_windows_junction_traversal_is_shared(self):
        self.validate_def("object",{
            "object_title":"rights below config directory",
            "capability":"windows.fileeffectiverights53",
            "select":{
                "directory":self.entity(r"C:\\ProgramData"),
                "name":self.entity(".*",operation="match"),
                "trustee_sid":self.entity("S-1-5-18"),
            },
            "traversal":{
                "max_depth":1,
                "recurse":"junctions_and_directories",
                "filesystem":"same",
            },
        })

    def test_case_insensitive_equal_directory_allows_traversal(self):
        rows=validate_assessment_capability_semantics({
            "assessment":{
                "objects":{"o":{
                    "capability":"windows.fileeffectiverights53",
                    "select":{
                        "directory":self.entity(r"C:\\ProgramData",operation="equal_ci"),
                        "name":self.entity(".*",operation="match"),
                        "trustee_sid":self.entity("S-1-5-18"),
                    },
                    "traversal":{
                        "max_depth":None,
                        "recurse":"junctions_and_directories",
                        "filesystem":"any",
                    },
                }},
                "states":{},
                "tests":{},
            }
        })
        self.assertNotIn(
            "windows.fileeffectiverights53.pattern_directory_no_traversal",
            {row["code"] for row in rows},
        )

    def test_full_path_with_traversal_is_semantic_error(self):
        rows=validate_assessment_capability_semantics({
            "assessment":{
                "objects":{"o":{
                    "capability":"windows.fileeffectiverights53",
                    "select":{
                        "full_path":self.entity(r"C:\\\\Windows\\\\win.ini"),
                        "trustee_sid":self.entity("S-1-5-18"),
                    },
                    "traversal":{"max_depth":1,"recurse":"junctions","filesystem":"same"},
                }},
                "states":{},
                "tests":{},
            }
        })
        self.assertIn("windows.fileeffectiverights53.full_path_no_traversal",{row["code"] for row in rows})

    def test_effective_right_boolean_state(self):
        self.validate_def("state",{
            "state_title":None,
            "capability":"windows.fileeffectiverights53",
            "state":{
                "field":"file_write_data","value":False,"operation":"equal","datatype":"boolean","match":"all","existence":"some",
            },
        })

    def test_deprecated_behaviors_and_windows_view_absent(self):
        encoded=json.dumps(self.schema)
        self.assertNotIn("include_group",encoded)
        self.assertNotIn("resolve_group",encoded)
        self.assertNotIn("windows_view",encoded)


if __name__=="__main__":
    unittest.main()
