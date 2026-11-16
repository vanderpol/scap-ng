"""Pinned 0.4.1 Profile authoring invariant: independent Rule-ID disable lists."""
import json
from pathlib import Path
import unittest

SCHEMA = Path(__file__).parents[1] / "schema" / "benchmark.schema.json"


class ProfileDisabledOnly041Tests(unittest.TestCase):
    def test_profile_has_no_inheritance_or_enabled_rule_controls(self):
        schema = json.loads(SCHEMA.read_text())
        self.assertEqual(schema["x-scap-ng-version"], "0.4.1")
        profile = schema["properties"]["benchmark"]["properties"]["profiles"]["items"]
        self.assertFalse(profile["additionalProperties"])
        self.assertIn("disabled_rules", profile["required"])
        self.assertIn("id", profile["required"])
        self.assertNotIn("extends", profile["properties"])
        self.assertNotIn("enabled_rules", profile["properties"])
        self.assertNotIn("disabled_groups", profile["properties"])
        self.assertNotIn("enabled_groups", profile["properties"])
        rules = profile["properties"]["disabled_rules"]
        self.assertEqual(rules["type"], "array")
        self.assertTrue(rules["uniqueItems"])
        self.assertEqual(rules["items"]["type"], "string")
        self.assertEqual(rules["items"]["minLength"], 1)

    def test_profiles_do_not_depend_on_group_structure(self):
        schema = json.loads(SCHEMA.read_text())
        profile = schema["properties"]["benchmark"]["properties"]["profiles"]["items"]
        self.assertNotIn("groups", profile["properties"])
        self.assertIn("groups", schema["properties"]["benchmark"]["properties"])
        self.assertIn("disabled_rules", profile["properties"])


if __name__ == "__main__":
    unittest.main()
