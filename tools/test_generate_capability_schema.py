#!/usr/bin/env python3
import json
from pathlib import Path
import unittest

import jsonschema
from referencing import Registry, Resource

from generate_capability_schema import generate


ROOT = Path(__file__).resolve().parents[1]
MAPPING = ROOT / "schema/v0.1.0/capability-mappings/unix.file.json"


class UnixFileGeneratedCapabilitySchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mapping = json.loads(MAPPING.read_text(encoding="utf-8"))
        cls.schema = generate(cls.mapping, ROOT)
        common_path = ROOT / "schema/v0.1.0/capability-common.schema.json"
        cls.common = json.loads(common_path.read_text(encoding="utf-8"))
        cls.registry = Registry().with_resource(
            cls.common["$id"], Resource.from_contents(cls.common)
        )

    def validate_def(self, name, value):
        jsonschema.Draft202012Validator(
            self.schema["$defs"][name],
            registry=self.registry,
        ).validate(value)


    def test_generated_schema_reuses_shared_common_primitives(self):
        encoded = json.dumps(self.schema)
        self.assertIn("capability-common.schema.json#/$defs/object_entity_base", encoded)
        self.assertIn("capability-common.schema.json#/$defs/state_entity_base", encoded)
        self.assertIn("capability-common.schema.json#/$defs/set_expression", encoded)
        self.assertIn("capability-common.schema.json#/$defs/set_expression", encoded)
        self.assertNotIn('"variable_reference":', encoded)

    def test_generated_schema_uses_clean_native_vocabulary(self):
        encoded = json.dumps(self.schema)
        self.assertNotIn('"behaviors"', encoded)
        self.assertNotIn('"recurse_direction"', encoded)
        self.assertNotIn('"filepath"', encoded)
        self.assertNotIn('"user_id"', encoded)
        self.assertIn('"full_path"', encoded)
        self.assertIn('"owner_uid"', encoded)
        self.assertIn('"traversal"', encoded)

    def test_mapping_keeps_legacy_crosswalk_outside_runtime_schema(self):
        self.assertIn("migration_crosswalk", self.mapping)
        encoded = json.dumps(self.schema)
        self.assertNotIn("migration_crosswalk", encoded)
        self.assertNotIn("OVAL 5.12.3", encoded)
        self.assertNotIn("filepath", encoded)
        self.assertNotIn("user_id", encoded)

    def test_native_field_names_are_present(self):
        encoded = json.dumps(self.schema)
        for name in ("full_path", "directory", "name", "owner_uid", "owner_gid", "setuid", "setgid"):
            self.assertIn(f'"{name}"', encoded)

    def test_valid_filepath_object(self):
        self.validate_def("object", {
            "object_title": "passwd",
            "capability": "unix.file",
            "select": {
                "full_path": {
                    "value": "/etc/passwd",
                    "operation": "equal",
                    "datatype": "string",
                    "mask": False,
                }
            },
        })

    def test_valid_path_filename_object(self):
        self.validate_def("object", {
            "object_title": "config files",
            "capability": "unix.file",
            "select": {
                "directory": {
                    "value": "/etc",
                    "operation": "equal",
                    "datatype": "string",
                    "mask": False,
                },
                "name": {
                    "value": "passwd",
                    "operation": "equal",
                    "datatype": "string",
                    "mask": False,
                },
            },
            "traversal": {
                "max_depth": 0,
                "follow_symlinks": True,
                "filesystem": "local",
            },
        })

    def test_directory_selection_uses_native_null_name(self):
        self.validate_def("object", {
            "object_title": "directory itself",
            "capability": "unix.file",
            "select": {
                "directory": {
                    "value": "/etc",
                    "operation": "equal",
                    "datatype": "string",
                    "mask": False,
                },
                "name": None,
            },
        })

    def test_filepath_and_path_filename_are_mutually_exclusive(self):
        bad = {
            "object_title": None,
            "capability": "unix.file",
            "select": {
                "full_path": {
                    "value": "/etc/passwd",
                    "operation": "equal",
                    "datatype": "string",
                    "mask": False,
                },
                "directory": {
                    "value": "/etc",
                    "operation": "equal",
                    "datatype": "string",
                    "mask": False,
                },
                "name": {
                    "value": "passwd",
                    "operation": "equal",
                    "datatype": "string",
                    "mask": False,
                },
            },
        }
        with self.assertRaises(jsonschema.ValidationError):
            self.validate_def("object", bad)

    def test_object_selector_rejects_state_only_quantifiers(self):
        with self.assertRaises(jsonschema.ValidationError):
            self.validate_def("object", {
                "object_title": None,
                "capability": "unix.file",
                "select": {
                    "full_path": {
                        "value": "/etc/passwd",
                        "operation": "equal",
                        "datatype": "string",
                    "mask": False,
                        "entity_existence": "none",
                    }
                },
            })

    def test_var_check_requires_variable_value(self):
        with self.assertRaises(jsonschema.ValidationError):
            self.validate_def("state", {
                "state_title": None,
                "capability": "unix.file",
                "state": {
                    "field": "name",
                    "value": "passwd",
                    "operation": "equal",
                    "datatype": "string",
                    "mask": False,
                    "entity_check": "all",
                    "entity_existence": "some",
                    "var_check": "all",
                },
            })

        self.validate_def("state", {
            "state_title": None,
            "capability": "unix.file",
            "state": {
                "field": "name",
                "value": {"variable": "approved-name"},
                "operation": "equal",
                "datatype": "string",
                    "mask": False,
                "entity_check": "all",
                "entity_existence": "some",
                "var_check": "all",
            },
        })

    def test_wrong_capability_is_rejected(self):
        with self.assertRaises(jsonschema.ValidationError):
            self.validate_def("test", {
                "test_title": None,
                "capability": "linux.rpminfo",
                "object": "passwd-object",
                "check_existence": "some",
                "check": "all",
            })

    def test_valid_state_field(self):
        self.validate_def("state", {
            "state_title": "owner is root",
            "capability": "unix.file",
            "state": {
                "field": "owner_uid",
                "value": 0,
                "operation": "equal",
                "datatype": "integer",
                    "mask": False,
                "entity_check": "all",
                "entity_existence": "some",
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
                    "operation": "equal",
                    "datatype": "string",
                    "mask": False,
                },
            })

    def test_state_datatype_is_field_specific(self):
        with self.assertRaises(jsonschema.ValidationError):
            self.validate_def("state", {
                "state_title": None,
                "capability": "unix.file",
                "state": {
                    "field": "setuid",
                    "value": 1,
                    "operation": "equal",
                    "datatype": "integer",
                    "mask": False,
                    "entity_check": "all",
                    "entity_existence": "some",
                },
            })

        self.validate_def("state", {
            "state_title": None,
            "capability": "unix.file",
            "state": {
                "field": "setuid",
                "value": True,
                "operation": "equal",
                "datatype": "boolean",
                    "mask": False,
                "entity_check": "all",
                "entity_existence": "some",
            },
        })

    def test_user_id_rejects_boolean_datatype(self):
        with self.assertRaises(jsonschema.ValidationError):
            self.validate_def("state", {
                "state_title": None,
                "capability": "unix.file",
                "state": {
                    "field": "owner_uid",
                    "value": True,
                    "operation": "equal",
                    "datatype": "boolean",
                    "mask": False,
                    "entity_check": "all",
                    "entity_existence": "some",
                },
            })

    def test_shared_set_model_accepts_nested_native_sets(self):
        self.validate_def("object", {
            "object_title": "combined files",
            "capability": "unix.file",
            "set": {
                "operator": "union",
                "operands": [
                    {
                        "object": "files-a",
                        "filters": [
                            {"state": "only-root-owned", "action": "include"}
                        ],
                    },
                    {
                        "set": {
                            "operator": "difference",
                            "operands": [
                                {"object": "files-b", "filters": []},
                                {"object": "excluded-files", "filters": []},
                            ],
                        }
                    },
                ],
            },
        })

    def test_native_numeric_fields_are_integer_only(self):
        for field in ("owner_uid","owner_gid","access_time","change_time","modify_time","size"):
            with self.subTest(field=field):
                self.validate_def("state", {
                    "state_title": None,
                    "capability": "unix.file",
                    "state": {
                        "field": field,
                        "value": 1,
                        "operation": "equal",
                        "datatype": "integer",
                        "mask": False,
                        "entity_check": "all",
                        "entity_existence": "some",
                    },
                })
                with self.assertRaises(jsonschema.ValidationError):
                    self.validate_def("state", {
                        "state_title": None,
                        "capability": "unix.file",
                        "state": {
                            "field": field,
                            "value": "1",
                            "operation": "equal",
                            "datatype": "string",
                            "mask": False,
                            "entity_check": "all",
                            "entity_existence": "some",
                        },
                    })

    def test_semantic_validator_rules_are_not_lost(self):
        rules = {
            row["id"]: row
            for row in self.schema["x-semantic-validator-rules"]
        }
        self.assertIn("unix.file.filter_state_capability", rules)
        self.assertIn("unix.file.full_path_no_traversal", rules)
        self.assertIn("unix.file.pattern_directory_no_traversal", rules)


if __name__ == "__main__":
    unittest.main()
