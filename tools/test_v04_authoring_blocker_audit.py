"""Focused regression for canonical 0.4 authoring audit classifications."""

import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from audit_v04_authoring_blockers import check


class CanonicalAuthoringBlockerAuditTests(unittest.TestCase):
    def audit(self, tests):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "fixture.zip"
            document = {"assessment": {"mode": "automated", "tests": tests}}
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("authoring/fixture/assessment.json", json.dumps(document))
            return check(path)["counts"]

    def test_test_level_field_requirement_is_native(self):
        counts = self.audit({"edition-test": {
            "require": {
                "items": "one_or_more",
                "field_requirement": "at_least_one_exists_and_all_match",
                "all_items_must": [{"fields": {"type": {"equals": "string"},
                                               "value": {"equals": "EnterpriseS"}}}],
            },
        }})
        self.assertEqual(counts["native_all_items_must_tests"], 1)
        self.assertEqual(counts["native_test_inherited_field_requirement"], 1)
        self.assertNotIn("unrecognized_structured_requirement", counts)

    def test_invalid_requirement_shape_is_not_silently_accepted(self):
        counts = self.audit({"invalid-test": {"require": {"items": "one_or_more", "unexpected": 1}}})
        self.assertEqual(counts["unrecognized_structured_requirement"], 1)

    def test_explicit_legacy_fallback_remains_visible(self):
        counts = self.audit({"fallback-test": {
            "require": "at_least_one_exists_and_some_match",
            "states": [{"fields": {"value": {"equals": "example"}}}],
        }})
        self.assertEqual(counts["legacy_string_require_tests"], 1)
        self.assertEqual(counts["legacy_states"], 1)
        self.assertNotIn("native_all_items_must_tests", counts)


if __name__ == "__main__":
    unittest.main()
