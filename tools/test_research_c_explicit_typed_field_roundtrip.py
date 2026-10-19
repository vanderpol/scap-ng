#!/usr/bin/env python3
"""Refs #245: no silent datatype erasure in explicit C-to-A State lowering.

This is a typed representation regression, NOT a source OVAL runtime parity
claim. macos.plist511.value_of is polymorphic in the version-pinned A mapping:
plain string and OVAL version equality cannot be treated interchangeably.
"""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from research_c_require_language import compile_c_requirement


def authored(value, *, datatype=None):
    predicate = {"equals": value}
    if datatype is not None:
        predicate["datatype"] = datatype
    return {
        "from": {"macos.plist511": {
            "filepath": "/Library/Preferences/com.example.test.plist",
            "xpath": "/plist/dict/key",
        }},
        "must": {"every_item": {"value_of": predicate}},
    }


class ExplicitTypedFieldLoweringTests(unittest.TestCase):
    def test_string_and_version_compilations_retain_distinct_explicit_type(self):
        plain = compile_c_requirement(authored("1.0", datatype="string"))
        version = compile_c_requirement(authored("1.0", datatype="version"))
        ps = plain["test"]["states"][0]["value_of"]
        vs = version["test"]["states"][0]["value_of"]
        self.assertEqual(ps["datatype"], "string")
        self.assertEqual(vs["datatype"], "version")
        self.assertEqual(ps["equals"], vs["equals"])
        self.assertNotEqual(ps, vs)
        self.assertFalse(plain["source_parity_verified"])
        self.assertFalse(version["scanner_executed"])

    def test_explicit_boolean_and_integer_types_are_not_lost(self):
        for datatype, value in [("boolean", True), ("integer", 1)]:
            with self.subTest(datatype=datatype):
                result = compile_c_requirement(authored(value, datatype=datatype))
                field = result["test"]["states"][0]["value_of"]
                self.assertEqual(field["datatype"], datatype)
                self.assertIs(type(field["equals"]), type(value))

    def test_reject_declared_type_that_disagrees_with_yaml_value(self):
        for datatype, value in [
            ("integer", "1"),
            ("boolean", "true"),
            ("version", 1),
            ("string", True),
        ]:
            with self.subTest(datatype=datatype, value=value):
                with self.assertRaisesRegex(
                    ValueError, "typed value_of literal does not match declared datatype"
                ):
                    compile_c_requirement(authored(value, datatype=datatype))

    def test_bad_declared_type_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "invalid typed value_of datatype"):
            compile_c_requirement(authored("1.0", datatype="not_a_datatype"))

    def test_untyped_literal_keeps_existing_inference_behavior(self):
        doc = {"from": authored(True)["from"],
               "must": {"every_item": {"value_of": True}}}
        baseline = deepcopy(doc)
        result = compile_c_requirement(doc)
        self.assertEqual(doc, baseline)
        self.assertNotIn("datatype", result["test"]["states"][0]["value_of"])


if __name__ == "__main__":
    unittest.main()
