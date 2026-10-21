#!/usr/bin/env python3
"""Native v0.4 generated flat-Object schema transformation regressions."""
from copy import deepcopy
import unittest
from jsonschema import Draft202012Validator
from flatten_v04_object_schema import UnsafeObjectSchema, flatten_schema

CAP="linux.partition"


def sample_object(*, select=True, collect=False, file_scope=False, selectors=None,
                  parameters=None):
    selectors = selectors or {"mount_point": {"type": "object",
                                               "required": ["equals"],
                                               "properties": {"equals": {"type": "string"}},
                                               "additionalProperties": False}}
    parameters = parameters or {"include_default": {"type": "boolean"}}
    properties = {"capability": {"const": CAP},
                  "set": {"type": "object"},
                  "filters": {"type": "array"},
                  "for_each": {"type": "object"},
                  "object_title": {"type": ["string", "null"]}}
    variants = []
    if select:
        properties["select"] = {
            "type": "object", "properties": selectors,
            "oneOf": [{"required": [next(iter(selectors))]}],
            "additionalProperties": False}
        variants.append({"required": ["select"] + (["collect"] if collect else []),
                         "not": {"required": ["set"]}})
    if collect:
        properties["collect"] = {"type": "object",
                                 "properties": parameters,
                                 "required": [next(iter(parameters))],
                                 "additionalProperties": False}
        if not select:
            variants.append({"required": ["collect"],
                             "not": {"required": ["set"]}})
    variants.append({"required": ["set"],
                     "not": {"anyOf": [
                         {"required": ["select"]}, {"required": ["collect"]}]}})
    obj = {"type": "object", "required": ["capability"],
           "properties": properties, "additionalProperties": False, "oneOf": variants}
    if file_scope:
        obj["properties"]["filesystem"] = {"type": "string"}
        obj["allOf"] = [{"if": {
            "properties": {"select": {"anyOf": [
                {"required": ["mount_point"]}]}},
            "required": ["select"]},
            "then": {"required": ["filesystem"]}}]
    return obj


class FlatObjectSchemaTests(unittest.TestCase):
    def _assert(self, schema, valid, invalid):
        Draft202012Validator.check_schema(schema)
        v = Draft202012Validator(schema)
        for item in valid:
            with self.subTest(valid=item):
                self.assertTrue(v.is_valid(item), list(v.iter_errors(item)))
        for item in invalid:
            with self.subTest(invalid=item):
                self.assertFalse(v.is_valid(item))

    def test_selector_direct_and_generic_wrapper_rejected(self):
        mapping = {"selector_map": {"mount_point": "mount_point"}}
        original = sample_object()
        result = flatten_schema(original, mapping, capability=CAP)
        self.assertIn("select", original["properties"])
        self.assertNotIn("select", result["properties"])
        self._assert(result, [
            {"capability": CAP, "mount_point": {"equals": "/home"}},
            {"capability": CAP, "set": {}}],
            [{"capability": CAP, "select": {"mount_point": {"equals": "/home"}}},
             {"capability": CAP, "mount_point": {"not_equal": "/home"}},
             {"capability": CAP, "mount_point": {"equals": "/home"}, "set": {}},
             {"capability": CAP}])

    def test_flat_selector_and_acquisition_parameters_both_required(self):
        mapping = {"selector_map": {"mount_point": "mount_point"},
                   "collection_parameters": {"include_default": {}}}
        original = sample_object(collect=True)
        result = flatten_schema(original, mapping, capability=CAP)
        self._assert(result, [
            {"capability": CAP, "mount_point": {"equals": "/home"},
             "include_default": False}],
            [{"capability": CAP, "mount_point": {"equals": "/home"}},
             {"capability": CAP, "include_default": True},
             {"capability": CAP, "mount_point": {"equals": "/home"},
              "collect": {"include_default": False}}])

    def test_native_cmdlet_select_is_preserved_without_wrapper(self):
        native = {"collection_parameters": {"select": {}}}
        old = sample_object(select=False, collect=True,
                            parameters={"select": {"type": "object"}})
        old["properties"]["capability"] = {"const": "windows.cmdlet"}
        result = flatten_schema(old, native, capability="windows.cmdlet")
        self._assert(result,
            [{"capability": "windows.cmdlet", "select": {"Name": True}}],
            [{"capability": "windows.cmdlet", "collect": {"select": {"Name": True}}},
             {"capability": "windows.cmdlet", "select": "Name"}])

    def test_filesystem_condition_moves_from_select_to_flat(self):
        mapping = {"selector_map": {"mount_point": "mount_point"}}
        old = sample_object(file_scope=True)
        new = flatten_schema(old, mapping, capability=CAP)
        self._assert(new, [
            {"capability": CAP, "mount_point": {"equals": "/home"},
             "filesystem": "local"},
            {"capability": CAP, "set": {}}],
            [{"capability": CAP, "mount_point": {"equals": "/home"}}])

    def test_acquisition_only_foreach_without_selectors_is_rejected(self):
        native = {"collection_parameters": {"command": {}}}
        original = sample_object(
            select=False, collect=True,
            parameters={"command": {"type": "string"}})
        # In the legacy schema for_each required generic select. Where a
        # capability has no selectors, keep that branch impossible.
        original["allOf"] = [
            {"if": {"required": ["for_each"]},
             "then": {"required": ["select"]}}]
        flattened = flatten_schema(
            original, native, capability="independent.shellcommand")
        self._assert(flattened,
            [{"capability": "linux.partition", "command": "echo ok"}],
            [{"capability": "linux.partition", "command": "echo ok",
              "for_each": {"item": "x", "in": "y"}}])

    def test_collisions_fail_closed(self):
        for mapping in (
            {"selector_map": {"mount_point": "filters"}},
            {"selector_map": {"mount_point": "mount_point"},
             "collection_parameters": {"mount_point": {}}},
            {"collection_parameters": {"select": {}}},
            {"selector_map": {"mount_point": "select"}},
        ):
            with self.subTest(mapping=mapping):
                with self.assertRaises(UnsafeObjectSchema):
                    flatten_schema(sample_object(), mapping, capability=CAP)

    def test_unknown_legacy_variant_fails_closed(self):
        native = {"selector_map": {"mount_point": "mount_point"}}
        obj = sample_object()
        obj["oneOf"].append({"required": ["unknown"]})
        with self.assertRaisesRegex(UnsafeObjectSchema, "unexpected"):
            flatten_schema(obj, native, capability=CAP)


if __name__ == "__main__":
    unittest.main()
