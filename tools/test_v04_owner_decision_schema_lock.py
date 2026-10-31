#!/usr/bin/env python3
"""Focused schema contract regressions for 2026-10-31 owner decisions.

Run: uv run --no-project --with jsonschema python tools/test_v04_owner_decision_schema_lock.py
This is intentionally not an OVAL source-equivalence or scanner proof.
"""

import copy
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schema" / "v0.4.0"
SCHEMA_BASE = "https://scap-ng.dev/schema/v0.4.0/"


def schema_registry():
    registry = Registry()
    for file in SCHEMA_DIR.glob("*.schema.json"):
        schema = json.loads(file.read_text(encoding="utf-8"))
        registry = registry.with_resource(
            SCHEMA_BASE + file.name,
            Resource.from_contents(schema, default_specification=DRAFT202012),
        )
    return registry


def validator(name):
    document = json.loads((SCHEMA_DIR / name).read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(document)
    return Draft202012Validator(document, registry=schema_registry())


def assessment(capability="windows.registry"):
    test = {
        "test_title": "Example content-authoring regression",
        "capability": capability,
        "require": {
            "items_found": "one_or_more",
            "items_satisfying": "every",
            "field_requirement": {
                "values_found": "one_or_more",
                "values_matching": "every",
            },
            "fields": {"value": {"equals": 1}},
        },
    }
    if capability != "independent.unknown":
        test["reported_elements"] = "all"
    return {
        "assessment": {
            "id": "windows-registry-value-assessment",
            "version": 1,
            "assessment_title": "Example",
            "mode": "automated",
            "class": "compliance",
            "tests": {"registry-value-test": test},
            "evaluate": {"test": "registry-value-test"},
            "specification": {
                "id": "scap-ng.pre-alpha.assessment",
                "version": "0.4.0",
            },
        }
    }


class OwnerDecisionsSchemaLock(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.assessment_validator = validator("assessment.schema.json")
        cls.expression_validator = validator("expression.schema.json")

    def assert_valid(self, value, target=None):
        target = target or self.assessment_validator
        errors = list(target.iter_errors(value))
        self.assertFalse(errors, "\n".join(str(error) for error in errors[:3]))

    def assert_invalid(self, value, target=None):
        target = target or self.assessment_validator
        self.assertTrue(list(target.iter_errors(value)), "Unexpectedly accepted old syntax")

    def test_standard_comparison_valid(self):
        self.assert_valid(assessment())

    def test_test_wide_field_requirement_mandatory(self):
        data = assessment()
        del data["assessment"]["tests"]["registry-value-test"]["require"]["field_requirement"]
        self.assert_invalid(data)

    def test_field_override_must_supply_both_members(self):
        data = assessment()
        data["assessment"]["tests"]["registry-value-test"]["require"]["fields"]["value"]["values_matching"] = "one_or_more"
        self.assert_invalid(data)
        data["assessment"]["tests"]["registry-value-test"]["require"]["fields"]["value"]["values_found"] = "one_or_more"
        self.assert_valid(data)

    def test_optional_cardinality_uses_zero_or_more_only(self):
        data = assessment()
        data["assessment"]["tests"]["registry-value-test"]["require"]["field_requirement"]["values_found"] = "zero_or_more"
        self.assert_valid(data)
        data["assessment"]["tests"]["registry-value-test"]["require"]["field_requirement"]["values_found"] = "may_be_absent"
        self.assert_invalid(data)

    def test_existence_only_without_field_requirement(self):
        data = assessment()
        data["assessment"]["tests"]["registry-value-test"]["require"] = {"items_found": "none"}
        self.assert_valid(data)

    def test_confirmed_field_absence_is_not_failed_collection(self):
        data = assessment()
        data["assessment"]["tests"]["registry-value-test"]["require"]["fields"] = {"value": {"values_found": "none"}}
        self.assert_valid(data)

    def test_purpose_removed(self):
        data = assessment()
        data["assessment"]["purpose"] = "assessment"
        self.assert_invalid(data)
        data = assessment()
        data["assessment"]["dependencies"] = {
            "local-ref": {"assessment": "other-assessment", "expected_version": 1}
        }
        self.assert_valid(data)
        data["assessment"]["dependencies"]["local-ref"]["purpose"] = "applicability"
        self.assert_invalid(data)

    def test_native_id_limit(self):
        data = assessment()
        data["assessment"]["id"] = "x" * 65
        self.assert_invalid(data)
        data = assessment()
        data["assessment"]["tests"] = {"a" * 60 + "-test": data["assessment"]["tests"]["registry-value-test"]}
        self.assert_invalid(data)

    def test_reported_elements_must_be_explicit(self):
        data = assessment()
        del data["assessment"]["tests"]["registry-value-test"]["reported_elements"]
        self.assert_invalid(data)
        self.assert_valid(assessment())

    def test_case_comparison_is_explicit_independent_of_selector(self):
        data = assessment()
        data["assessment"]["tests"]["registry-value-test"]["require"]["fields"]["value"] = {
            "case_insensitive_equals": "Test"
        }
        self.assert_valid(data)

    def test_conditional_elif_and_terminals(self):
        expression = {
            "if": {"test": "registry-value-test"},
            "then": {"test": "registry-value-test"},
            "else_if": [
                {"if": {"test": "registry-value-test"},
                 "then": {"not_evaluated": {
                     "reason": "Remote ACL outside collection scope",
                     "follow_up": "Inspect remote share ACL manually"
                 }}},
                {"if": {"test": "registry-value-test"},
                 "then": {"not_applicable": {"reason": "Feature absent"}}},
            ],
            "else": {"not_applicable": {"reason": "No branch applies"}},
        }
        self.assert_valid(expression, self.expression_validator)
        data = assessment()
        data["assessment"]["evaluate"] = expression
        self.assert_valid(data)
        invalid = copy.deepcopy(expression)
        del invalid["else_if"][0]["then"]
        self.assert_invalid(invalid, self.expression_validator)
        invalid = copy.deepcopy(expression)
        invalid["else_if"][0]["then"]["not_evaluated"]["reason"] = ""
        self.assert_invalid(invalid, self.expression_validator)
        invalid = copy.deepcopy(expression)
        invalid["else_if"] = []
        self.assert_invalid(invalid, self.expression_validator)

    def test_case_and_version_contract_metadata(self):
        mapping = SCHEMA_DIR / "capability-mappings" / "supported"
        registry = json.loads((mapping / "windows.registry.json").read_text(encoding="utf-8"))
        self.assertEqual(registry["native"]["selector_case_semantics"]["key"]["mode"], "case_insensitive")
        self.assertEqual(registry["native"]["selector_case_semantics"]["name"]["mode"], "case_insensitive")
        file = json.loads((mapping / "windows.file.json").read_text(encoding="utf-8"))
        self.assertEqual(file["native"]["selector_case_semantics"]["name"]["mode"], "filesystem_per_directory")
        cmdlet = json.loads((mapping / "windows.cmdlet.json").read_text(encoding="utf-8"))
        self.assertEqual(cmdlet["native"]["collection_parameters"]["module_version"]["semantic_datatype"], "version")
        self.assertEqual(cmdlet["native"]["field_datatypes"]["module_version"], ["version"])

    def test_schema_authoring_default_is_not_missing_field_acceptance(self):
        fields = json.loads((SCHEMA_DIR / "assessment-language.schema.json").read_text(encoding="utf-8"))
        req = fields["$defs"]["canonical_all_items_requirement"]
        self.assertIn("field_requirement", req["required"])
        self.assertEqual(req["properties"]["items_found"]["default"], "one_or_more")
        self.assertTrue(req["properties"]["field_requirement"]["x-scap-ng-authoring"]["hide_when_default"])


if __name__ == "__main__":
    unittest.main()
