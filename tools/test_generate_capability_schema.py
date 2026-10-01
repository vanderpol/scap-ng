#!/usr/bin/env python3
import json
from pathlib import Path
import unittest

import jsonschema

from generate_capability_schema import generate


ROOT = Path(__file__).resolve().parents[1]
MAPPING = ROOT / "schema/v0.1.0/capability-mappings/unix.file.json"


class UnixFileGeneratedCapabilitySchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mapping = json.loads(MAPPING.read_text(encoding="utf-8"))
        cls.schema = generate(cls.mapping, ROOT)

    def validate_def(self, name, value):
        jsonschema.Draft202012Validator(
            self.schema["$defs"][name]
        ).validate(value)

    def test_source_inventory_is_extracted_from_pinned_xsd(self):
        catalog = self.schema["x-source-field-catalog"]
        self.assertEqual(
            set(catalog["object_selectors"]),
            {"filepath", "path", "filename"},
        )
        self.assertIn("filepath", catalog["state_fields"])
        self.assertIn("path", catalog["state_fields"])
        self.assertIn("filename", catalog["state_fields"])
        self.assertIn("size", catalog["state_fields"])
        self.assertIn("suid", catalog["state_fields"])
        self.assertIn("has_extended_acl", catalog["state_fields"])

    def test_behavior_defaults_and_enums_are_source_backed(self):
        behaviors = self.schema["$defs"]["object"]["properties"]["behaviors"]
        props = behaviors["properties"]
        self.assertEqual(props["max_depth"]["default"], -1)
        self.assertEqual(props["recurse_direction"]["default"], "none")
        self.assertEqual(props["recurse_file_system"]["default"], "all")
        self.assertIn("down", props["recurse_direction"]["enum"])
        self.assertIn("local", props["recurse_file_system"]["enum"])

    def test_valid_filepath_object(self):
        self.validate_def("object", {
            "object_title": "passwd",
            "capability": "unix.file",
            "select": {
                "filepath": {
                    "value": "/etc/passwd",
                    "operation": "equals",
                    "datatype": "string",
                }
            },
        })

    def test_valid_path_filename_object(self):
        self.validate_def("object", {
            "object_title": "config files",
            "capability": "unix.file",
            "select": {
                "path": {
                    "value": "/etc",
                    "operation": "equals",
                    "datatype": "string",
                },
                "filename": {
                    "value": "passwd",
                    "operation": "equals",
                    "datatype": "string",
                },
            },
            "behaviors": {
                "max_depth": 0,
                "recurse": "symlinks and directories",
                "recurse_direction": "none",
                "recurse_file_system": "local",
            },
        })

    def test_filepath_and_path_filename_are_mutually_exclusive(self):
        bad = {
            "object_title": None,
            "capability": "unix.file",
            "select": {
                "filepath": {
                    "value": "/etc/passwd",
                    "operation": "equals",
                    "datatype": "string",
                },
                "path": {
                    "value": "/etc",
                    "operation": "equals",
                    "datatype": "string",
                },
                "filename": {
                    "value": "passwd",
                    "operation": "equals",
                    "datatype": "string",
                },
            },
        }
        with self.assertRaises(jsonschema.ValidationError):
            self.validate_def("object", bad)

    def test_wrong_capability_is_rejected(self):
        with self.assertRaises(jsonschema.ValidationError):
            self.validate_def("test", {
                "test_title": None,
                "capability": "linux.rpminfo",
                "object": "passwd-object",
                "check_existence": "at_least_one_exists",
                "check": "all",
            })

    def test_valid_state_field(self):
        self.validate_def("state", {
            "state_title": "owner is root",
            "capability": "unix.file",
            "state": {
                "field": "user_id",
                "value": 0,
                "operation": "equals",
                "datatype": "int",
                "entity_check": "all",
                "entity_existence": "at_least_one_exists",
            },
        })

    def test_unknown_state_field_is_rejected(self):
        with self.assertRaises(jsonschema.ValidationError):
            self.validate_def("state", {
                "state_title": None,
                "capability": "unix.file",
                "state": {
                    "field": "made_up_field",
                    "value": "x",
                    "operation": "equals",
                    "datatype": "string",
                },
            })

    def test_state_datatype_is_field_specific(self):
        with self.assertRaises(jsonschema.ValidationError):
            self.validate_def("state", {
                "state_title": None,
                "capability": "unix.file",
                "state": {
                    "field": "suid",
                    "value": 1,
                    "operation": "equals",
                    "datatype": "int",
                },
            })

        self.validate_def("state", {
            "state_title": None,
            "capability": "unix.file",
            "state": {
                "field": "suid",
                "value": True,
                "operation": "equals",
                "datatype": "boolean",
            },
        })

    def test_user_id_rejects_boolean_datatype(self):
        with self.assertRaises(jsonschema.ValidationError):
            self.validate_def("state", {
                "state_title": None,
                "capability": "unix.file",
                "state": {
                    "field": "user_id",
                    "value": True,
                    "operation": "equals",
                    "datatype": "boolean",
                },
            })

    def test_semantic_validator_rules_are_not_lost(self):
        rules = {
            row["id"]: row
            for row in self.schema["x-semantic-validator-rules"]
        }
        self.assertIn("unix.file.filter_state_capability", rules)
        self.assertIn("unix.file.filepath_no_recursion_behaviors", rules)
        self.assertIn("unix.file.path_pattern_no_recursion_behaviors", rules)
        self.assertIn("unix.file.filename_empty", rules)


if __name__ == "__main__":
    unittest.main()
