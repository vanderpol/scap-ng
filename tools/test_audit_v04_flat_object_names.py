#!/usr/bin/env python3
"""Strict 0.4 capability namespace checks, including native cmdlet.select."""
import unittest
from audit_v04_flat_object_names import CollisionError, inspect


class FlatObjectCatalogTests(unittest.TestCase):
    def test_normal_registry_and_shellcommand(self):
        for cap, native in (
            ("windows.registry", {"selector_map": {
                "hive": "hive", "key": "key", "name": "name"}}),
            ("independent.shellcommand", {"collection_parameters": {
                "command": {}, "shell": {}}}),
        ):
            self.assertEqual(inspect({"capability": cap, "native": native})["capability"], cap)

    def test_windows_cmdlet_native_select_is_not_legacy_wrapper(self):
        out = inspect({"capability": "windows.cmdlet",
                       "native": {"collection_parameters": {
                           "select": {}, "module_name": {}, "noun": {}}}})
        self.assertTrue(out["native_select_parameter"])
        self.assertEqual(out["selector_count"], 0)

    def test_generic_select_selector_is_invalid(self):
        with self.assertRaises(CollisionError):
            inspect({"capability": "unix.file",
                     "native": {"selector_map": {"x": "select"}}})

    def test_other_capabilities_cannot_invent_native_select(self):
        with self.assertRaises(CollisionError):
            inspect({"capability": "independent.shellcommand",
                     "native": {"collection_parameters": {"select": {}}}})

    def test_real_control_name_collisions_rejected(self):
        for key in ("collect", "filters", "set", "traversal", "filesystem",
                    "for_each", "behaviors", "object_title", "capability"):
            with self.subTest(key=key), self.assertRaises(CollisionError):
                inspect({"capability": "unix.file",
                         "native": {"selector_map": {"x": key}}})

    def test_parameter_selector_overlap_rejected(self):
        with self.assertRaisesRegex(CollisionError, "duplicated"):
            inspect({"capability": "unix.file",
                     "native": {"selector_map": {"old": "name"},
                                "collection_parameters": {"name": {}}}})

    def test_duplicate_native_selector_targets_rejected(self):
        with self.assertRaisesRegex(CollisionError, "duplicate normalized"):
            inspect({"capability": "unix.file",
                     "native": {"selector_map": {"name": "name",
                                                 "filename": "name"}}})


if __name__ == "__main__":
    unittest.main()
