"""Canonical 0.4.1 for_each authoring admission and boundary tests."""
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator
from referencing import Registry, Resource


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schema"
PREFIX = "https://scap-ng.dev/schema/v0.4.1/"


def load(path):
    return json.loads(path.read_text())


def registry():
    resources = {}
    for path in SCHEMA.glob("*.json"):
        document = load(path)
        if "$schema" not in document:
            continue
        resource = Resource.from_contents(document)
        resources[PREFIX + path.name] = resource
        resources[document["$id"]] = resource
    return Registry().with_resources(resources.items())


def assessment_object(**overrides):
    document = {
        "assessment": {
            "id": "foreach-correlation-assessment",
            "version": 1,
            "assessment_title": "Correlated collection expansion",
            "mode": "automated",
            "class": "compliance",
            "specification": {
                "id": "scap-ng.pre-alpha.assessment",
                "version": "0.4.1",
            },
            "shared_objects": {
                "users-object": {
                    "object_title": "Source users",
                    "capability": "unix.file",
                    "filepath": {"equals": "/etc/passwd"},
                }
            },
            "tests": {
                "home-test": {
                    "test_title": "Check each selected path",
                    "capability": "unix.file",
                    "object": {
                        "for_each": {"item": "user", "in": "users-object"},
                        "filepath": {"from": "user.full_path"},
                    },
                    "require": {
                        "item_requirement": {
                            "items_found": "one_or_more",
                            "items_satisfying": "every",
                        },
                        "field_requirement": {
                            "values_found": "one_or_more",
                            "values_matching": "one_or_more",
                        },
                        "fields": {"full_path": {"equals": "/etc/passwd"}},
                    },
                    "reported_elements": "all",
                }
            },
            "evaluate": {"test": "home-test"},
        }
    }
    document["assessment"].update(overrides)
    return document


class ForEachSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validator = Draft202012Validator(
            load(SCHEMA / "assessment.schema.json"), registry=registry()
        )

    def assert_valid(self, document):
        errors = list(self.validator.iter_errors(document))
        self.assertEqual(errors, [], "\n".join(str(error) for error in errors))

    def test_named_source_and_correlated_selector_are_admitted(self):
        self.assert_valid(assessment_object())

    def test_chained_source_expansion_is_admitted(self):
        document = assessment_object()
        document["assessment"]["shared_objects"]["users-object"]["for_each"] = {
            "item": "parent",
            "in": "root-object",
        }
        self.assert_valid(document)

    def test_selector_binding_requires_lexical_alias_and_field(self):
        document = assessment_object()
        document["assessment"]["tests"]["home-test"]["object"]["filepath"] = {
            "from": "user"
        }
        self.assertTrue(list(self.validator.iter_errors(document)))

    def test_source_reference_is_a_named_object_id(self):
        document = assessment_object()
        document["assessment"]["tests"]["home-test"]["object"]["for_each"]["in"] = "users"
        self.assertTrue(list(self.validator.iter_errors(document)))


if __name__ == "__main__":
    unittest.main()
