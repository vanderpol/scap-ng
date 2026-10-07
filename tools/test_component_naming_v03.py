#!/usr/bin/env python3
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, RefResolver

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schema" / "v0.3.0"


def load(name):
    return json.loads((SCHEMA_DIR / name).read_text(encoding="utf-8"))


def validator(name):
    schema = load(name)
    store = {}
    for path in SCHEMA_DIR.glob("*.schema.json"):
        doc = json.loads(path.read_text(encoding="utf-8"))
        if "$id" in doc:
            store[doc["$id"]] = doc
    return Draft202012Validator(
        schema,
        resolver=RefResolver.from_schema(schema, store=store),
    )


def valid_assessment():
    return {
        "assessment": {
            "id": "SV-1.automated",
            "version": 1,
            "assessment_title": "Example",
            "mode": "automated",
            "class": "compliance",
            "purpose": "assessment",
            "specification": {
                "id": "scap-ng.pre-alpha.assessment",
                "version": "0.3.0",
            },
            "shared_objects": {
                "forward-zones-object": {
                    "object_title": "Forward zones",
                    "capability": "independent.shellcommand",
                }
            },
            "variables": {
                "zone-names-variable": {
                    "kind": "local",
                    "datatype": "string",
                }
            },
            "states": {
                "dnssec-enabled-state": {
                    "capability": "independent.shellcommand",
                }
            },
            "inputs": {
                "minimum-key-size-input": {
                    "datatype": "integer",
                    "cardinality": "one",
                    "required": True,
                }
            },
            "tests": {
                "zone-signing-test": {
                    "test_title": "Zone signing",
                    "reported_elements": "all",
                    "capability": "independent.shellcommand",
                    "object": "forward-zones-object",
                    "states": ["dnssec-enabled-state"],
                }
            },
            "evaluate": {"test": "zone-signing-test"},
        }
    }


class ComponentNamingV03Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.assessment_validator = validator("assessment.schema.json")
        cls.expression_validator = validator("expression.schema.json")

    def errors(self, doc):
        return list(self.assessment_validator.iter_errors(doc))

    def test_suffix_form_named_components_validate(self):
        self.assertEqual(self.errors(valid_assessment()), [])

    def test_prefix_form_test_id_is_rejected(self):
        doc = valid_assessment()
        test = doc["assessment"]["tests"].pop("zone-signing-test")
        doc["assessment"]["tests"]["test-zone-signing"] = test
        doc["assessment"]["evaluate"]["test"] = "test-zone-signing"
        self.assertTrue(self.errors(doc))


    def test_legacy_objects_registry_is_rejected_in_canonical_v03(self):
        doc = valid_assessment()
        doc["assessment"]["objects"] = doc["assessment"].pop("shared_objects")
        self.assertTrue(self.errors(doc))

    def test_untyped_object_id_is_rejected(self):
        doc = valid_assessment()
        obj = doc["assessment"]["shared_objects"].pop("forward-zones-object")
        doc["assessment"]["shared_objects"]["forward-zones"] = obj
        doc["assessment"]["tests"]["zone-signing-test"]["object"] = "forward-zones"
        self.assertTrue(self.errors(doc))

    def test_untyped_state_reference_is_rejected(self):
        doc = valid_assessment()
        doc["assessment"]["tests"]["zone-signing-test"]["states"] = ["dnssec-enabled"]
        self.assertTrue(self.errors(doc))

    def test_evaluate_requires_test_suffix(self):
        self.assertFalse(
            self.expression_validator.is_valid({"test": "zone-signing"})
        )
        self.assertTrue(
            self.expression_validator.is_valid({"test": "zone-signing-test"})
        )


if __name__ == "__main__":
    unittest.main()
