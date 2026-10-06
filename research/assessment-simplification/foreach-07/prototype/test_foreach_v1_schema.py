#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
SCHEMA = json.loads((HERE / "foreach-v1.schema.json").read_text(encoding="utf-8"))
VALIDATOR = Draft202012Validator(SCHEMA)


class ForeachV1Schema(unittest.TestCase):
    def assert_valid(self, instance):
        errors = sorted(VALIDATOR.iter_errors(instance), key=lambda e: list(e.path))
        self.assertEqual(errors, [], "\n".join(e.message for e in errors))

    def assert_invalid(self, instance):
        self.assertTrue(list(VALIDATOR.iter_errors(instance)))

    def test_simple_binding_is_valid(self):
        self.assert_valid({
            "for_each": {
                "item": "user",
                "in": "non-system-users",
            },
            "select": {
                "directory": {
                    "from": "user.home_dir",
                },
                "name": {
                    "value": r"^\.[^\s\.]+",
                    "operation": "pattern_match",
                    "datatype": "string",
                },
            },
        })

    def test_from_rejects_redundant_operation(self):
        self.assert_invalid({
            "for_each": {
                "item": "user",
                "in": "users",
            },
            "select": {
                "directory": {
                    "from": "user.home_dir",
                    "operation": "equals",
                },
            },
        })

    def test_for_each_rejects_old_verbose_form(self):
        self.assert_invalid({
            "for_each": {
                "source": {"object": "users"},
                "as": "user",
                "collect": "union",
            },
            "select": {
                "directory": {"from": "user.home_dir"},
            },
        })

    def test_from_requires_binding_field_shape(self):
        self.assert_invalid({
            "for_each": {
                "item": "user",
                "in": "users",
            },
            "select": {
                "directory": {"from": "home_dir"},
            },
        })


if __name__ == "__main__":
    unittest.main()
