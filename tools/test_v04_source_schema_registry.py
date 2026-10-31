"""Cross-document reference scope regression for the 0.4 source validators."""

import os
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator
from referencing import Registry, Resource


SCHEMA_DIR = Path(os.environ.get(
    "SCAPNG_SCHEMA_DIR", Path(__file__).resolve().parents[1] / "schema/v0.4.0"
))


def assessment(*, scoped=True):
    require = {
        "items_found": "one_or_more",
        "items_satisfying": "every",
        "or": [
            {"fields": {"type": {"equals": "string"},
                        "value": {"equals": "Enterprise"}}},
            {"fields": {"type": {"equals": "string"},
                        "value": {"equals": "EnterpriseS"}}},
        ],
    }
    if scoped:
        require["field_requirement"] = {
            "values_found": "one_or_more", "values_matching": "every"}
    return {"assessment": {
        "id": "edition-assessment", "version": 1,
        "assessment_title": "Windows Enterprise editions", "mode": "automated",
        "class": "inventory",
        "specification": {"id": "scap-ng.pre-alpha.assessment", "version": "0.4.0"},
        "tests": {"edition-test": {
            "test_title": "Enterprise or EnterpriseS",
            "capability": "windows.registry", "reported_elements": "all",
            "require": require,
        }}, "evaluate": {"test": "edition-test"},
    }}


class RegistryResolutionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        schemas = [json.loads(path.read_text()) for path in
                   SCHEMA_DIR.glob('*.schema.json')]
        registry = Registry().with_resources(
            (schema['$id'], Resource.from_contents(schema)) for schema in schemas)
        assessment_schema = next(schema for schema in schemas
                                 if schema['$id'].endswith('/assessment.schema.json'))
        cls.validator = Draft202012Validator(assessment_schema, registry=registry)

    def test_nested_field_body_resolves_against_language_schema(self):
        self.assertEqual(list(self.validator.iter_errors(assessment())), [])

    def test_missing_field_requirement_is_still_rejected(self):
        self.assertTrue(list(self.validator.iter_errors(assessment(scoped=False))))


if __name__ == "__main__":
    unittest.main()
