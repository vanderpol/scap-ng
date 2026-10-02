#!/usr/bin/env python3
import json
from pathlib import Path
import unittest

import jsonschema
from referencing import Registry, Resource

from generate_capability_schema import generate


ROOT = Path(__file__).resolve().parents[1]
MAPPING = ROOT / "schema/v0.1.0/capability-mappings/linux.rpminfo.json"


class LinuxRpmInfoGeneratedCapabilitySchemaTests(unittest.TestCase):
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

    def test_direct_object_requires_explicit_file_path_collection_choice(self):
        self.validate_def("object", {
            "object_title": "installed openssh-server",
            "capability": "linux.rpminfo",
            "select": {
                "package_name": {
                    "value": "openssh-server",
                    "operation": "equal",
                    "datatype": "string",
                    "mask": False,
                }
            },
            "collect": {
                "include_file_paths": False,
            },
        })

        with self.assertRaises(jsonschema.ValidationError):
            self.validate_def("object", {
                "object_title": "missing explicit source default",
                "capability": "linux.rpminfo",
                "select": {
                    "package_name": {
                        "value": "openssh-server",
                        "operation": "equal",
                        "datatype": "string",
                        "mask": False,
                    }
                },
            })

    def test_set_object_does_not_require_direct_collection_parameter(self):
        self.validate_def("object", {
            "object_title": "combined package objects",
            "capability": "linux.rpminfo",
            "set": {
                "operator": "union",
                "operands": [
                    {"object": "packages-a", "filters": []},
                    {"object": "packages-b", "filters": []},
                ],
            },
        })

    def test_native_state_names_and_datatypes(self):
        self.validate_def("state", {
            "state_title": "installed RPM EVR is at least required version",
            "capability": "linux.rpminfo",
            "state": {
                "field": "evr",
                "value": "0:9.0p1-1.el9",
                "operation": "greater_or_equal",
                "datatype": "rpm_evr",
                "mask": False,
                "match": "all",
                "existence": "some",
            },
        })

        self.validate_def("state", {
            "state_title": "epoch as integer",
            "capability": "linux.rpminfo",
            "state": {
                "field": "epoch",
                "value": 0,
                "operation": "equal",
                "datatype": "integer",
                "mask": False,
                "match": "all",
                "existence": "some",
            },
        })

    def test_wrong_evr_datatype_is_rejected(self):
        with self.assertRaises(jsonschema.ValidationError):
            self.validate_def("state", {
                "state_title": None,
                "capability": "linux.rpminfo",
                "state": {
                    "field": "evr",
                    "value": "0:1.2-3",
                    "operation": "equal",
                    "datatype": "string",
                    "mask": False,
                    "match": "all",
                    "existence": "some",
                },
            })

    def test_mapping_materializes_oval_behavior_default(self):
        self.assertEqual(
            self.mapping["migration_crosswalk"]["materialized_defaults"]["behaviors.filepaths"],
            False,
        )

    def test_semantic_rules_preserved(self):
        rules = {row["id"] for row in self.schema["x-semantic-validator-rules"]}
        self.assertIn("linux.rpminfo.filter_state_capability", rules)
        self.assertIn("linux.rpminfo.filepaths_collection", rules)


if __name__ == "__main__":
    unittest.main()
