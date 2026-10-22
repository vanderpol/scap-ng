"""Cross-document reference scope regression for the 0.4 source validators."""

import os
from pathlib import Path
import unittest

from v04_canonical_source_ir import _schema_validators


SCHEMA_DIR = Path(os.environ.get(
    "SCAPNG_SCHEMA_DIR", Path(__file__).resolve().parents[1] / "schema/v0.4.0"
))


def assessment(*, scoped=True):
    require = {
        "items": "one_or_more",
        "all_items_must": [{"or": [
            {"fields": {"type": {"equals": "string"},
                        "value": {"equals": "Enterprise"}}},
            {"fields": {"type": {"equals": "string"},
                        "value": {"equals": "EnterpriseS"}}},
        ]}],
    }
    if scoped:
        require["field_requirement"] = "at_least_one_exists_and_all_match"
    return {"assessment": {
        "id": "edition-assessment", "version": 1,
        "assessment_title": "Windows Enterprise editions", "mode": "automated",
        "class": "inventory", "purpose": "applicability",
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
        cls.validator = _schema_validators(SCHEMA_DIR)["assessment"]

    def test_nested_field_body_resolves_against_language_schema(self):
        self.assertEqual(list(self.validator.iter_errors(assessment())), [])

    def test_missing_field_requirement_is_still_rejected(self):
        self.assertTrue(list(self.validator.iter_errors(assessment(scoped=False))))


if __name__ == "__main__":
    unittest.main()
