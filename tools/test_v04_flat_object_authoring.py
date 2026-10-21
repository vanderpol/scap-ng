#!/usr/bin/env python3
"""Focused flat-Object source-inversion and hybrid YAML regressions."""
from copy import deepcopy
import unittest
import yaml
from v04_flat_object_authoring import (
    flatten_document, restore_document, dump_hybrid, hybridize, FlowMap,
)

CATALOG = {
    "linux.partition": {"selectors": {"mount_point"}, "parameters": set()},
    "windows.registry": {"selectors": {"hive", "key", "name"}, "parameters": set()},
    "independent.shellcommand": {"selectors": set(),
        "parameters": {"shell", "command", "error_if_exit_status_not_0", "error_if_stderr_exists"}},
    "windows.cmdlet": {"selectors": set(), "parameters": {"select", "noun"}},
    "unix.file": {"selectors": {"full_path", "directory", "name"}, "parameters": set()},
}


def case(capability, obj):
    return {"assessment": {"mode": "automated", "tests": {"a": {
        "capability": capability, "object": obj}}}}


def migrated(source):
    value, proof = flatten_document(source, CATALOG)
    assert restore_document(value, proof) == source
    return value, proof


class FlatObjectAuthoringTests(unittest.TestCase):
    def test_linux_selector_and_compact_format(self):
        source = case("linux.partition", {"select": {"mount_point": {"equals": "/home"}}})
        value, proof = migrated(source)
        ob = value["assessment"]["tests"]["a"]["object"]
        self.assertEqual(ob, {"mount_point": {"equals": "/home"}})
        self.assertEqual(len(proof["edits"]), 1)
        self.assertIn("object: {mount_point: {equals: /home}}", dump_hybrid(value))

    def test_registry_selector_order_and_types_preserved(self):
        fields = {"hive": {"equals": "local_machine"},
                  "key": {"equals": r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"},
                  "name": {"equals": "CurrentVersion"}}
        value, proof = migrated(case("windows.registry", {"select": fields}))
        self.assertEqual(value["assessment"]["tests"]["a"]["object"], fields)
        rendered = dump_hybrid(value)
        self.assertIn("object: {hive: {equals: local_machine}, key:", rendered)
        self.assertIn("name: {equals: CurrentVersion}}", rendered)
        self.assertEqual(len([line for line in rendered.splitlines()
                              if "object:" in line]), 1)

    def test_command_acquisition_fields_flatten_without_selector(self):
        parameters = {"shell": "powershell", "command": "Get-PnpDevice -Class Bluetooth",
                      "error_if_exit_status_not_0": False,
                      "error_if_stderr_exists": False}
        value, proof = migrated(case("independent.shellcommand", {"collect": parameters}))
        self.assertEqual(value["assessment"]["tests"]["a"]["object"], parameters)
        self.assertNotIn("collect", value["assessment"]["tests"]["a"]["object"])

    def test_native_cmdlet_select_is_not_generic_selector(self):
        native_select = {"properties": {"name": "Name"}}
        value, proof = migrated(case("windows.cmdlet", {
            "collect": {"select": native_select, "noun": "Item"}}))
        ob = value["assessment"]["tests"]["a"]["object"]
        self.assertEqual(ob["select"], native_select)
        self.assertEqual(proof["edits"][0]["old_wrappers"]["collect"]["select"],
                         native_select)
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            flatten_document(case("windows.cmdlet", {"select": native_select}), CATALOG)

    def test_standalone_shared_objects_are_flattened_and_inverted(self):
        doc = {"assessment": {
            "tests": {"a": {"capability": "linux.partition",
                            "object": "home-mount-object"}},
            "shared_objects": {"home-mount-object": {
                "capability": "linux.partition",
                "select": {"mount_point": {"equals": "/home"}}},
                "config-object": {
                    "capability": "independent.shellcommand",
                    "collect": {"shell": "bash",
                                "command": "printf ok",
                                "error_if_exit_status_not_0": False,
                                "error_if_stderr_exists": False}}}}
        value, proof = migrated(doc)
        obj = value["assessment"]["shared_objects"]["home-mount-object"]
        self.assertEqual(obj["mount_point"], {"equals": "/home"})
        self.assertNotIn("select", obj)
        self.assertNotIn("collect",
                         value["assessment"]["shared_objects"]["config-object"])
        self.assertEqual(len(proof["edits"]), 2)
        self.assertEqual(restore_document(value, proof), doc)

    def test_condition_override_precedes_compact_fields_when_printed(self):
        expected = {"fields": {"type": {"equals": "string"},
                               "value": {"equals": "Enterprise"}},
                    "field_requirement": "at_least_one_exists_and_all_match"}
        text = dump_hybrid(expected)
        self.assertLess(text.index("field_requirement:"), text.index("fields:"))
        self.assertIn("fields: {type: {equals: string}, value: {equals: Enterprise}}", text)

    def test_real_set_operand_and_filter_position_untouched(self):
        source = case("unix.file", {"set": {"operator": "intersection",
            "operands": [
                {"object": {"select": {"full_path": {"equals": "/etc/passwd"}}},
                 "filters": [{"include": {"owner_uid": {"equals": 0}}}]},
                {"object": {"select": {"full_path": {"equals": "/etc/shadow"}}}},
            ]}})
        value, proof = migrated(source)
        operands = value["assessment"]["tests"]["a"]["object"]["set"]["operands"]
        self.assertEqual([o["object"]["full_path"]["equals"] for o in operands],
                         ["/etc/passwd", "/etc/shadow"])
        self.assertEqual(operands[0]["filters"],
                         source["assessment"]["tests"]["a"]["object"]["set"]["operands"][0]["filters"])
        self.assertEqual(len(proof["edits"]), 2)

    def test_collision_and_unknown_fields_fail_closed(self):
        for ob in (
            {"select": {"mount_point": {"equals": "/home"}}, "mount_point": {"equals": "/"}},
            {"select": {"unexpected": {"equals": "/home"}}},
            {"collect": {"shell": "powershell"}},
        ):
            with self.subTest(ob=ob):
                with self.assertRaises(ValueError):
                    flatten_document(case("linux.partition", ob), CATALOG)

    def test_modified_flat_object_cannot_be_restored(self):
        source = case("linux.partition", {"select": {"mount_point": {"equals": "/home"}}})
        value, proof = migrated(source)
        modified = deepcopy(value)
        modified["assessment"]["tests"]["a"]["object"]["mount_point"]["equals"] = "/tmp"
        with self.assertRaisesRegex(ValueError, "modified"):
            restore_document(modified, proof)

    def test_compact_and_expanded_complete_conditions_are_identical(self):
        source = {"require": {"items": "one_or_more",
            "field_requirement": "at_least_one_exists_and_all_match",
            "all_items_must": [{"or": [
                {"fields": {"type": {"equals": "string"}, "value": {"equals": "Enterprise"}}},
                {"fields": {"type": {"equals": "string"}, "value": {"equals": "EnterpriseS"}}},
            ]}]}}
        text = dump_hybrid(source)
        self.assertIn("fields: {type: {equals: string}, value: {equals: Enterprise}}", text)
        self.assertEqual(yaml.safe_load(text), source)

    def test_local_field_requirement_override_expands(self):
        source = {"fields": {"type": {"equals": "string"},
                             "value": {"equals": "Enterprise",
                                       "field_requirement": "may_be_absent_and_all_match"}}}
        text = dump_hybrid(source)
        self.assertIn("type: {equals: string}", text)
        self.assertIn("field_requirement: may_be_absent_and_all_match", text)
        self.assertEqual(yaml.safe_load(text), source)


if __name__ == "__main__":
    unittest.main()
