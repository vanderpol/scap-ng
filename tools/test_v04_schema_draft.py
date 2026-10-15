#!/usr/bin/env python3
"""Focused pre-alpha v0.4.0 schema draft checks (not scanner conformance)."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator, RefResolver

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schema" / "v0.4.0"
SCHEMAS = {
    p.name: json.loads(p.read_text(encoding="utf-8"))
    for p in sorted(SCHEMA_DIR.glob("*.schema.json"))
}
STORE = {s["$id"]: s for s in SCHEMAS.values()}
ASSESSMENT = SCHEMAS["assessment.schema.json"]
COMMON = SCHEMAS["capability-common.schema.json"]
VALIDATOR = Draft202012Validator(
    ASSESSMENT, resolver=RefResolver.from_schema(ASSESSMENT, store=STORE)
)
FILTER_VALIDATOR = Draft202012Validator(
    {"$ref": COMMON["$id"] + "#/$defs/state_filter"},
    resolver=RefResolver.from_schema(COMMON, store=STORE),
)


def fixture(*, requirement="at_least_one_exists_and_all_match", states=None):
    test = {
        "test_title": "0.4 structural example",
        "capability": "unix.file",
        "reported_elements": "all",
        "require": requirement,
    }
    if states is not None:
        test["states"] = states
    return {"assessment": {
        "id": "draft-schema-assessment", "version": 1,
        "assessment_title": "0.4 structural example", "mode": "automated",
        "class": "compliance", "purpose": "assessment",
        "specification": {"id": "scap-ng.pre-alpha.assessment", "version": "0.4.0"},
        "tests": {"demo-test": test}, "evaluate": {"test": "demo-test"},
    }}


def field(name="owner_uid", operator="equals", value=0,
          requirement="at_least_one_exists_and_all_match"):
    return {name: {operator: value, "require": requirement}}


def errors(document):
    return list(VALIDATOR.iter_errors(document))


class V04DraftSchemaTests(unittest.TestCase):
    def test_complete_self_contained_versioned_snapshot(self):
        self.assertGreaterEqual(len(SCHEMAS), 25)
        for name, schema in SCHEMAS.items():
            with self.subTest(name=name):
                Draft202012Validator.check_schema(schema)
                self.assertEqual(schema.get("x-scap-ng-version"), "0.4.0")
                self.assertTrue(schema.get("x-last-modified"))
                self.assertEqual(
                    schema.get("$id"),
                    "https://scap-ng.dev/schema/v0.4.0/" + name,
                )
                self.assertNotIn("schema/v0.3.0", json.dumps(schema))
        mappings = sorted((SCHEMA_DIR / "capability-mappings").rglob("*.json"))
        self.assertGreaterEqual(len(mappings), 100)
        for path in mappings:
            with self.subTest(mapping=path.name):
                value = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(value.get("specification_version"), "0.4.0")
                self.assertNotIn("schema/v0.3.0", json.dumps(value))

    def test_one_grammar_scalar_and_literal_field_names(self):
        for key in ("owner_uid", "value", "all"):
            with self.subTest(key=key):
                self.assertFalse(errors(fixture(states=[field(key)])))

    def test_state_free_exactly_one(self):
        self.assertFalse(errors(fixture(requirement="only_one_exists")))
        self.assertTrue(errors(fixture(requirement="only_one_exists_and_matches")))

    def test_states_require_paired_quantifiers(self):
        self.assertFalse(errors(fixture(states=[
            field(requirement="only_one_exists_and_matches")
        ], requirement="only_one_exists_and_matches")))
        self.assertTrue(errors(fixture(states=[field()], requirement="only_one_exists")))
        broken = fixture(states=[field()])
        del broken["assessment"]["tests"]["demo-test"]["require"]
        self.assertTrue(errors(broken))

    def test_reject_legacy_fields_and_ambiguous_operations(self):
        old = fixture(states=[{
            "field": "owner_uid", "value": 0, "operation": "equals",
            "existence": "one_or_more", "match": "all",
        }])
        self.assertTrue(errors(old))
        old2 = fixture(states=[{"owner_uid": {
            "value": 0, "operation": "equals", "existence": "one_or_more",
            "match": "all",
        }}])
        self.assertTrue(errors(old2))
        bad = fixture(states=[field()])
        pred = bad["assessment"]["tests"]["demo-test"]["states"][0]["owner_uid"]
        pred["not_equal"] = 1
        self.assertTrue(errors(bad))
        good = fixture(states=[field()])
        good["assessment"]["tests"]["demo-test"]["existence"] = "one_or_more"
        self.assertTrue(errors(good))

    def test_array_and_variable_reference_retain_value_match(self):
        for operand in ([0, 1000], {"variable": "allowed-uids-variable"},
                        {"input": "organization-uid-input"}):
            document = fixture(states=[field(value=operand)])
            pred = document["assessment"]["tests"]["demo-test"]["states"][0]["owner_uid"]
            pred["datatype"] = "integer"
            self.assertTrue(errors(document))
            pred["value_match"] = "one"
            self.assertFalse(errors(document))

    def test_windows_record_nested_requirements(self):
        record = {"value": {"record": {
            "require": "at_least_one_exists_and_some_match",
            "fields": {"productstate": {
                "bitwise_and": 4096,
                "require": "at_least_one_exists_and_all_match",
            }},
        }}}
        self.assertFalse(errors(fixture(states=[record])))

    def test_set_filter_requires_one_action(self):
        valid = {"exclude": {"mode": {
            "greater_than": 493,
            "require": "at_least_one_exists_and_all_match",
        }}}
        self.assertFalse(list(FILTER_VALIDATOR.iter_errors(valid)))
        self.assertTrue(list(FILTER_VALIDATOR.iter_errors({
            "action": "exclude", "field": "mode",
            "value": 493, "operation": "greater_than",
        })))
        self.assertTrue(list(FILTER_VALIDATOR.iter_errors({
            "exclude": valid["exclude"], "include": valid["exclude"],
        })))


if __name__ == "__main__":
    unittest.main()
