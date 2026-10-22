#!/usr/bin/env python3
import copy
import unittest

from jsonschema import Draft202012Validator
from tools.v04_field_requirement_schema_candidate import build


def example():
    return {
        "items": "one_or_more",
        "field_requirement": "at_least_one_exists_and_all_match",
        "all_items_must": [{
            "or": [
                {"fields": {"type": {"equals": "string"},
                            "value": {"equals": "Enterprise"}}},
                {"fields": {"type": {"equals": "string"},
                            "value": {"equals": "EnterpriseS"}}},
            ],
        }],
    }


class CanonicalGrammarCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = build()
        Draft202012Validator.check_schema(cls.schema)
        cls.validator = Draft202012Validator({
            "$schema": cls.schema["$schema"],
            "$defs": cls.schema["$defs"],
            "$ref": "#/$defs/canonical_test_requirement",
        })

    def test_approved_short_condition_and_scope_validate(self):
        self.assertTrue(self.validator.is_valid(example()))
        with_leaf = copy.deepcopy(example())
        with_leaf["all_items_must"][0]["or"][1]["fields"]["value"][
            "field_requirement"] = "only_one_exists_and_matches"
        self.assertTrue(self.validator.is_valid(with_leaf))

    def test_legacy_mixed_names_rejected(self):
        for path in ("test", "group", "condition", "field"):
            with self.subTest(path=path):
                value = copy.deepcopy(example())
                if path == "test":
                    value["state_fields_require"] = value.pop("field_requirement")
                elif path == "group":
                    value["all_items_must"][0]["state_fields_require"] = "may_be_absent_and_all_match"
                elif path == "condition":
                    value["all_items_must"][0]["or"][0]["require"] = "may_be_absent_and_all_match"
                else:
                    value["all_items_must"][0]["or"][0]["fields"]["value"]["require"] = "none_exist"
                self.assertFalse(self.validator.is_valid(value))

    def test_item_and_field_existence_remain_separate(self):
        value = example()
        value["items"] = "none"
        self.assertFalse(self.validator.is_valid(value))
        value = example()
        value["field_requirement"] = "one_or_more"
        self.assertFalse(self.validator.is_valid(value))

    def test_empty_and_ambiguous_condition_rejected(self):
        value = example()
        value["all_items_must"][0] = {"or": []}
        self.assertFalse(self.validator.is_valid(value))
        value = example()
        value["all_items_must"][0]["and"] = []
        self.assertFalse(self.validator.is_valid(value))
        value = example()
        value["all_items_must"][0]["or"][0]["fields"] = {}
        self.assertFalse(self.validator.is_valid(value))


if __name__ == "__main__":
    unittest.main()
