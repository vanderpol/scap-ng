#!/usr/bin/env python3
import json
from pathlib import Path
import unittest

import jsonschema
from referencing import Registry, Resource

from generate_capability_schema import generate
from validate_generated_capability_semantics import validate_assessment_capability_semantics


ROOT=Path(__file__).resolve().parents[1]
MAPPING=ROOT/"schema/v0.1.0/capability-mappings/independent.textfilecontent54.json"


class TextFileContent54CapabilitySchemaTests(unittest.TestCase):
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
        }

    def defaults(self):
        return {
            "ignore_case":False,
            "multiline":True,
            "singleline":False,
            "item_creation":"all_object_elements_fullfilled",
        }

    def test_direct_file_content_selection_preserves_pattern_and_instance(self):
        self.validate_def("object",{
            "object_title":"sshd setting",
            "capability":"independent.textfilecontent54",
            "select":{
                "full_path":self.entity("/etc/ssh/sshd_config"),
                "pattern":self.entity(r"(?m)^PermitRootLogin\s+(\S+)",operation="match"),
                "instance":self.entity(1,datatype="integer"),
            },
            "collect":self.defaults(),
        })

    def test_directory_traversal_preserves_symlink_mode(self):
        self.validate_def("object",{
            "object_title":"all config matches",
            "capability":"independent.textfilecontent54",
            "select":{
                "directory":self.entity("/etc"),
                "name":self.entity(r".*\.conf$",operation="match"),
                "pattern":self.entity(r"^enabled=(.*)$",operation="match"),
                "instance":self.entity(1,operation="greater_or_equal",datatype="integer"),
            },
            "traversal":{
                "max_depth":None,
                "recurse":"symlinks_and_directories",
                "filesystem":"local",
            },
            "collect":self.defaults(),
        })

    def test_all_non_deprecated_independent_recurse_modes_validate(self):
        for recurse in ("directories","symlinks","symlinks_and_directories"):
            with self.subTest(recurse=recurse):
                self.validate_def("object",{
                    "object_title":None,
                    "capability":"independent.textfilecontent54",
                    "select":{
                        "directory":self.entity("/etc"),
                        "name":self.entity(".*",operation="match"),
                        "pattern":self.entity("x",operation="match"),
                        "instance":self.entity(1,datatype="integer"),
                    },
                    "traversal":{
                        "max_depth":1,
                        "recurse":recurse,
                        "filesystem":"same",
                    },
                    "collect":self.defaults(),
                })

    def test_windows_junction_term_is_not_independent_syntax(self):
        with self.assertRaises(jsonschema.ValidationError):
            self.validate_def("object",{
                "object_title":None,
                "capability":"independent.textfilecontent54",
                "select":{
                    "directory":self.entity("/etc"),
                    "name":self.entity(".*",operation="match"),
                    "pattern":self.entity("x",operation="match"),
                    "instance":self.entity(1,datatype="integer"),
                },
                "traversal":{
                    "max_depth":1,
                    "recurse":"junctions",
                    "filesystem":"local",
                },
                "collect":self.defaults(),
            })

    def test_behavior_defaults_are_explicit_in_native_content(self):
        bad=self.defaults()
        del bad["multiline"]
        with self.assertRaises(jsonschema.ValidationError):
            self.validate_def("object",{
                "object_title":None,
                "capability":"independent.textfilecontent54",
                "select":{
                    "full_path":self.entity("/etc/example"),
                    "pattern":self.entity("x",operation="match"),
                    "instance":self.entity(1,datatype="integer"),
                },
                "collect":bad,
            })

    def test_pattern_selector_requires_match_semantics(self):
        rows=validate_assessment_capability_semantics({
            "assessment":{
                "objects":{"o":{
                    "capability":"independent.textfilecontent54",
                    "select":{
                        "full_path":self.entity("/etc/example"),
                        "pattern":self.entity("enabled=true",operation="equal"),
                        "instance":self.entity(1,datatype="integer"),
                    },
                    "collect":self.defaults(),
                }},
                "states":{},
                "tests":{},
            }
        })
        self.assertIn("independent.textfilecontent54.pattern_operation",{row["code"] for row in rows})

    def test_state_retains_text_and_subexpression(self):
        for field in ("text","subexpression"):
            with self.subTest(field=field):
                self.validate_def("state",{
                    "state_title":None,
                    "capability":"independent.textfilecontent54",
                    "state":{
                        "field":field,
                        "value":"enabled",
                        "operation":"equal",
                        "datatype":"string",
                        "match":"all",
                        "existence":"some",
                    },
                })

    def test_deprecated_and_platform_specific_fields_not_native(self):
        encoded=json.dumps(self.schema)
        self.assertNotIn("recurse_direction",encoded)
        self.assertNotIn("windows_view",encoded)
        self.assertNotIn('"follow_links"',encoded)

    def test_semantic_rules_preserved(self):
        rules={row["id"] for row in self.schema["x-semantic-validator-rules"]}
        self.assertIn("independent.textfilecontent54.pattern_operation",rules)
        self.assertIn("independent.textfilecontent54.full_path_no_traversal",rules)


if __name__=="__main__":
    unittest.main()
