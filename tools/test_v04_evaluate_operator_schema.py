#!/usr/bin/env python3
"""Versioned 0.4.0 Test-result operators: canonical forms only.

This test checks the actual maintained 0.4.0 expression schema, not a
temporary research dialect. AND/OR/ONE/XOR apply to whole Test outcomes,
never replace Item existence/matching quantifiers (one_or_more, all, ...).
Refs #248 #239.
"""
from pathlib import Path
import json
import unittest
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[1]
FILE=ROOT/"schema/v0.4.0/expression.schema.json"


class TestEvaluateLogicalOperators(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema=json.loads(FILE.read_text())
        cls.validator=Draft202012Validator(cls.schema)
        cls.choices={next(iter(x["required"])):x
                     for x in cls.schema["$defs"]["expression"]["oneOf"]}

    def valid(self,expression):
        return not list(self.validator.iter_errors(expression))

    def test_new_logical_vocabulary_matches_oval_four_operators(self):
        for op in ("and","or","one","xor"):
            with self.subTest(op=op):
                self.assertTrue(self.valid({op:[
                    {"test":"first-test"},{"test":"second-test"}]}))

    def test_legacy_source_aliases_are_rejected(self):
        for old,new in (("all","and"),("any","or"),("odd","xor")):
            with self.subTest(alias=old):
                self.assertFalse(self.valid({old:[{"test":"first-test"}]}))
                self.assertNotIn(old,self.choices)
                self.assertFalse(self.choices[new]["properties"][new].get("deprecated",False))

    def test_nested_if_not_and_canonical_operators(self):
        expr={"if":{"test":"applicability-test"},
              "then":{"and":[{"test":"one-test"},
                             {"not":{"or":[{"test":"two-test"},
                                           {"test":"three-test"}]}}]},
              "else":{"and":[{"test":"four-test"},
                             {"xor":[{"test":"five-test"},
                                     {"test":"six-test"}]}]}}
        self.assertTrue(self.valid(expr))

    def test_logical_operators_are_not_item_quantifiers(self):
        for invalid in (
            {"one_or_more":[{"test":"a-test"}]},
            {"exactly_one":[{"test":"a-test"}]},
            {"none":[{"test":"a-test"}]},
            {"or":"one_or_more"},
            {"and":[]},
            {"xor":[]},
            {"any":"one_or_more"},
            {"and":[{"test":"a-test"}],"or":[{"test":"b-test"}]},
            {"if":{"test":"a-test"},"then":{"test":"b-test"}},
            {"not":{"test":"a-test"},"or":[{"test":"b-test"}]},
        ):
            with self.subTest(invalid=invalid):
                self.assertFalse(self.valid(invalid))

    def test_versioned_schema_metadata_stays_self_contained(self):
        self.assertEqual(self.schema["x-scap-ng-version"],"0.4.0")
        self.assertEqual(self.schema["x-last-modified"],"2026-10-23")
        self.assertIn("/v0.4.0/",self.schema["$id"])


if __name__=="__main__":
    unittest.main()
