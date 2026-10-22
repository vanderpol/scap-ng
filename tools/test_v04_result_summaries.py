#!/usr/bin/env python3
"""Focused 0.4.0 result-summary contract checks; no scanner claims."""
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schema" / "v0.4.0"


def load(name):
    return json.loads((SCHEMA / name).read_text(encoding="utf-8"))


class ResultSummaryContract(unittest.TestCase):
    def test_rule_summary_is_required_and_message_is_not_canonical(self):
        schema = load("rule-result.schema.json")
        self.assertIn("summary", schema["required"])
        self.assertNotIn("message", schema["properties"])
        self.assertNotIn("message", schema["required"])
        self.assertFalse(schema["additionalProperties"])
        prop = schema["properties"]["summary"]
        validator = Draft202012Validator(prop)
        for bad in (None, "", " ", "\n\t"):
            with self.subTest(bad=bad):
                self.assertFalse(validator.is_valid(bad))
        self.assertTrue(validator.is_valid("Required configuration file was absent."))

    def test_assessment_summary_is_required_and_standalone(self):
        schema = load("assessment-result.schema.json")["properties"]["assessment_result"]
        self.assertIn("summary", schema["required"])
        prop = schema["properties"]["summary"]
        validator = Draft202012Validator(prop)
        for bad in (None, "", " ", "\n\t"):
            with self.subTest(bad=bad):
                self.assertFalse(validator.is_valid(bad))
        self.assertTrue(validator.is_valid("Collection failed before evaluation."))

    def test_prior_snapshots_remain_unchanged_in_contract(self):
        for version in ("v0.2.0", "v0.3.0"):
            path = ROOT / "schema" / version / "rule-result.schema.json"
            old = json.loads(path.read_text(encoding="utf-8"))
            self.assertIn("message", old["properties"])
            self.assertNotIn("summary", old["required"])


if __name__ == "__main__":
    unittest.main()
