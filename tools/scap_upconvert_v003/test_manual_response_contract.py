#!/usr/bin/env python3
"""Regression coverage for the native Manual Assessment response contract."""
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator

from convert_collection_review import manual_response_contract


ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "schema" / "v0.1.0" / "manual-assessment.schema.json"


class ManualResponseContractTests(unittest.TestCase):
    def test_generated_contract_is_schema_valid(self):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        doc = {
            "assessment": {
                "id": "example.manual",
                "version": 1,
                "assessment_title": "Example manual check",
                "mode": "manual",
                "class": "compliance",
                "purpose": "assessment",
                "procedure": "Inspect the configured value and determine compliance.",
                "response": manual_response_contract(),
            }
        }
        errors = list(Draft202012Validator(schema).iter_errors(doc))
        self.assertEqual([], [error.message for error in errors])

    def test_contract_has_unambiguous_compliance_outcomes(self):
        choices = {row["value"]: row["outcome"] for row in manual_response_contract()["choices"]}
        self.assertEqual("true", choices["pass"])
        self.assertEqual("false", choices["fail"])
        self.assertEqual("unknown", choices["unknown"])
        self.assertEqual("not_applicable", choices["not_applicable"])
        self.assertEqual(len(choices), len(manual_response_contract()["choices"]))


if __name__ == "__main__":
    unittest.main()
