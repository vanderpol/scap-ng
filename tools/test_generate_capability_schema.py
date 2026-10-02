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
                },
                "name": {
                    "value": "passwd",
                    "operation": "equal",
                    "datatype": "string",
                },
            },
            "traversal": {
                "max_depth": 0,
                "recurse": "symlinks_and_directories",
                "filesystem": "local",
            },
        })

    def test_unix_traversal_preserves_symlink_terminology(self):
        self.validate_def("object", {
            "object_title": "symlink traversal",
            "capability": "unix.file",
            "select": {
                "directory": {
                    "value": "/etc",
                    "operation": "equal",
                    "datatype": "string",
                },
                "name": {
                    "value": ".*",
                    "operation": "match",
                    "datatype": "string",
                },
            },
            "traversal": {
                "max_depth": 2,
                "recurse": "symlinks",
                "filesystem": "local",
            },
        })
        with self.assertRaises(jsonschema.ValidationError):
            self.validate_def("object", {
                "object_title": "Windows terminology is not Unix traversal syntax",
                "capability": "unix.file",
                "select": {
                    "directory": {
                        "value": "/etc",
                        "operation": "equal",
                        "datatype": "string",
                    },
                    "name": {
                        "value": ".*",
                        "operation": "match",
                        "datatype": "string",
                    },
                },
                "traversal": {
                    "max_depth": 2,
                    "recurse": "junctions",
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
                },
                "directory": {
                    "value": "/etc",
                    "operation": "equal",
                    "datatype": "string",
                },
                "name": {
                    "value": "passwd",
                    "operation": "equal",
                    "datatype": "string",
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
                        "existence": "none",
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
                    "match": "all",
                    "existence": "some",
                    "variable_match": "all",
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
                "match": "all",
                "existence": "some",
                "variable_match": "all",
            },
        })

    def test_wrong_capability_is_rejected(self):
        with self.assertRaises(jsonschema.ValidationError):
            self.validate_def("test", {
                "test_title": None,
                "capability": "linux.rpminfo",
                "object": "passwd-object",
                "existence": "some",
                "match": "all",
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
                "match": "all",
                "existence": "some",
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
                    "match": "all",
                    "existence": "some",
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
                "match": "all",
                "existence": "some",
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
                    "match": "all",
                    "existence": "some",
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
                        "match": "all",
                        "existence": "some",
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
                            "match": "all",
                            "existence": "some",
                        },
                    })

    def test_mapping_state_fields_have_collected_item_parity(self):
        source_names = set(self.mapping["native"].get("state_field_map", {}))
        source_names.update(self.mapping["native"].get("native_added_state_fields", {}))
        item_only = set(self.mapping["native"].get("item_only_field_map", {}))
        collected = self.schema["$defs"]["collected_item"]["allOf"][1]["properties"]["fields"]["properties"]
        native_state_names = set(self.mapping["native"].get("state_field_map", {}).values())
        native_state_names.update(
            spec.get("native_name", source)
            for source, spec in self.mapping["native"].get("native_added_state_fields", {}).items()
        )
        native_item_only = set(self.mapping["native"].get("item_only_field_map", {}).values())
        self.assertTrue(source_names)
        self.assertTrue(native_state_names.issubset(set(collected)))
        self.assertTrue(native_item_only.issubset(set(collected)))
        self.assertTrue(item_only.isdisjoint(source_names))

    def test_mapped_behavior_families_have_explicit_native_contracts(self):
        behavior_contracts = {
            "file.hash": {"traversal": "file_traversal"},
            "independent.shellcommand": {
                "required_collect": {"error_if_exit_status_not_0", "error_if_stderr_exists"},
            },
            "independent.textfilecontent54": {
                "traversal": "file_traversal",
                "required_collect": {"ignore_case", "multiline", "singleline", "item_creation"},
            },
            "independent.xmlfilecontent": {
                "traversal": "file_traversal",
                "required_collect": {"item_creation"},
            },
            "independent.yamlfilecontent": {"traversal": "file_traversal"},
            "linux.rpminfo": {"required_collect": {"include_file_paths"}},
            "linux.rpmverifyfile": {
                "required_collect": {
                    "skip_link_target", "skip_size", "skip_owner", "skip_group",
                    "skip_mtime", "skip_mode", "skip_rdev", "skip_config_files",
                    "skip_ghost_files", "skip_file_digest", "skip_capabilities",
                },
            },
            "linux.rpmverifypackage": {
                "required_collect": {"skip_dependencies", "skip_scripts"},
            },
            "linux.selinuxsecuritycontext": {"traversal": "file_traversal"},
            "unix.file": {"traversal": "file_traversal"},
            "windows.file": {"traversal": "windows_file_traversal"},
            "windows.fileeffectiverights53": {"traversal": "windows_file_traversal"},
            "windows.ntuser": {
                "traversal": "hierarchy_traversal",
                "required_collect": {"include_default", "item_creation"},
            },
            "windows.registry": {"traversal": "hierarchy_traversal"},
            "windows.regkeyeffectiverights53": {"traversal": "hierarchy_traversal"},
            "windows.sid": {"required_collect": {"include_group", "resolve_group"}},
            "windows.sid_sid": {"required_collect": {"include_group", "resolve_group"}},
            "windows.wuaupdatesearcher": {
                "required_collect": {"include_superseded_updates"},
            },
        }
        mapping_dir = ROOT / "schema/v0.1.0/capability-mappings"
        for capability, expected in behavior_contracts.items():
            with self.subTest(capability=capability):
                mapping = json.loads(
                    (mapping_dir / f"{capability}.json").read_text(encoding="utf-8")
                )
                native = mapping["native"]
                if "traversal" in expected:
                    self.assertEqual(native.get("traversal_definition"), expected["traversal"])
                required = expected.get("required_collect", set())
                parameters = native.get("collection_parameters") or {}
                self.assertTrue(required.issubset(parameters), required - set(parameters))
                for name in required:
                    self.assertIs(parameters[name].get("required"), True)

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
