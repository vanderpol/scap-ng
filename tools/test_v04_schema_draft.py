#!/usr/bin/env python3
"""Focused 0.4.0 canonical grammar tests; not scanner conformance."""
from __future__ import annotations

import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schema" / "v0.4.0"
SCHEMAS = {
    p.name: json.loads(p.read_text(encoding="utf-8"))
    for p in sorted(SCHEMA_DIR.glob("*.schema.json"))
}
REGISTRY = Registry().with_resources(
    (s["$id"], Resource.from_contents(s)) for s in SCHEMAS.values())
ASSESSMENT = SCHEMAS["assessment.schema.json"]
COMMON = SCHEMAS["capability-common.schema.json"]
VALIDATOR = Draft202012Validator(ASSESSMENT, registry=REGISTRY)
FILTER_VALIDATOR = Draft202012Validator(
    {"$ref": COMMON["$id"] + "#/$defs/state_filter"}, registry=REGISTRY,
)
REQUIRED = {"values_found": "one_or_more", "values_matching": "every"}


def requirement(field="owner_uid", operand=0):
    return {
        "items_found": "one_or_more",
        "items_satisfying": "every",
        "field_requirement": dict(REQUIRED),
        "fields": {field: {"equals": operand}},
    }


def fixture(*, req=None, obj=None):
    test = {
        "test_title": "0.4 canonical example",
        "capability": "unix.file",
        "reported_elements": "all",
        "object": {"object_title": "Collect file metadata", "filepath": "/etc/passwd"}
            if obj is None else obj,
        "require": requirement() if req is None else req,
    }
    return {"assessment": {
        "id": "draft-schema-assessment", "version": 1,
        "assessment_title": "0.4 canonical example", "mode": "automated",
        "class": "compliance",
        "specification": {"id": "scap-ng.pre-alpha.assessment", "version": "0.4.0"},
        "tests": {"demo-test": test}, "evaluate": {"test": "demo-test"},
    }}


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
                    schema.get("$id"), "https://scap-ng.dev/schema/v0.4.0/" + name)
                self.assertNotIn("schema/v0.3.0", json.dumps(schema))
        mappings = sorted((SCHEMA_DIR / "capability-mappings").rglob("*.json"))
        self.assertGreaterEqual(len(mappings), 100)
        for path in mappings:
            with self.subTest(mapping=path.name):
                value = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(value.get("specification_version"), "0.4.0")
                self.assertNotIn("schema/v0.3.0", json.dumps(value))

    def test_inline_and_referenced_objects_are_both_optional_forms(self):
        self.assertFalse(errors(fixture()))
        self.assertFalse(errors(fixture(obj="shared-file-object")))
        shared = fixture(obj="shared-file-object")
        shared["assessment"]["shared_objects"] = {
            "shared-file-object": {
                "object_title": "Shared file metadata",
                "capability": "unix.file",
                "filepath": "/etc/passwd",
            }
        }
        self.assertFalse(errors(shared))
        self.assertTrue(errors(fixture(obj=[])))

    def test_structured_item_only_and_field_requirements(self):
        self.assertFalse(errors(fixture(req={"items_found": "none"})))
        self.assertFalse(errors(fixture(req={"items_found": "exactly_one"})))
        for field in ("owner_uid", "value", "all"):
            with self.subTest(field=field):
                self.assertFalse(errors(fixture(req=requirement(field))))
        no_scope = requirement()
        del no_scope["field_requirement"]
        self.assertTrue(errors(fixture(req=no_scope)))

    def test_reject_scalar_require_and_legacy_state_forms(self):
        missing = fixture()
        del missing["assessment"]["tests"]["demo-test"]["require"]
        self.assertTrue(errors(missing))
        for scalar in ("only_one_exists", "at_least_one_exists_and_all_match"):
            with self.subTest(scalar=scalar):
                self.assertTrue(errors(fixture(req=scalar)))
        for name, value in (
            ("state", {"owner_uid": {"equals": 0}}),
            ("states", [{"owner_uid": {"equals": 0}}]),
            ("states_match", "all"),
            ("state_fields_require", REQUIRED),
            ("existence", "one_or_more"),
            ("match", "all"),
        ):
            with self.subTest(name=name):
                document = fixture()
                document["assessment"]["tests"]["demo-test"][name] = value
                self.assertTrue(errors(document))
        document = fixture()
        document["assessment"]["tests"]["demo-test"]["require"]["states"] = []
        self.assertTrue(errors(document))

    def test_unknown_test_keys_rejected_without_dropping_variable_sources(self):
        for unknown in ("item_conditions", "state", "selection_check", "unexpected"):
            document = fixture()
            document["assessment"]["tests"]["demo-test"][unknown] = {}
            self.assertTrue(errors(document), unknown)
        document = fixture()
        document["assessment"]["tests"]["demo-test"].pop("object")
        document["assessment"]["tests"]["demo-test"]["capability"] = "variable.value"
        document["assessment"]["tests"]["demo-test"]["variable"] = "chosen-variable"
        self.assertFalse(errors(document))

    def test_reject_obsolete_evaluate_aliases(self):
        for old in ("all", "any", "odd"):
            document = fixture()
            document["assessment"]["evaluate"] = {old: [{"test": "demo-test"}]}
            self.assertTrue(errors(document))
        for current in ("and", "or", "one", "xor"):
            document = fixture()
            document["assessment"]["evaluate"] = {
                current: [{"test": "demo-test"}]}
            self.assertFalse(errors(document))

    def test_array_and_dynamic_references_retain_value_match(self):
        for operand in ([0, 1000], {"variable": "allowed-uids-variable"},
                        {"input": "organization-uid-input"}):
            document = fixture(req=requirement(operand=operand))
            field = document["assessment"]["tests"]["demo-test"]["require"][
                "fields"]["owner_uid"]
            field["datatype"] = "integer"
            self.assertTrue(errors(document))
            field["value_match"] = "exactly_one"
            self.assertFalse(errors(document))

    def test_reject_ambiguous_fields_and_unrecognized_operations(self):
        for predicate in ({"equals": 1, "not_equal": 2},
                          {"operation": "equals", "value": 0},
                          {"unrecognized_operator": 0}):
            document = fixture()
            document["assessment"]["tests"]["demo-test"]["require"][
                "fields"]["owner_uid"] = predicate
            self.assertTrue(errors(document))

    def test_set_filter_requires_one_action(self):
        valid = {"exclude": {"mode": {
            "greater_than": 493,
            "values_found": "one_or_more",
            "values_matching": "every",
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
