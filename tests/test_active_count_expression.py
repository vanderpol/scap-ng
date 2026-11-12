"""Guard the active SCAP-NG 0.4.0 native count expression contract.

Run: python3 -m unittest tests/test_active_count_expression.py
This is a schema-shape test, NOT a runtime or OVAL equivalence proof.
"""
import json
import unittest
from pathlib import Path

SCHEMA = Path(__file__).resolve().parents[1] / "schema" / "variable-expression.schema.json"


class ActiveCountContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        cls.branches = cls.schema["$defs"]["expression"]["oneOf"]

    def test_count_is_active_and_recursively_composable(self):
        forms = {
            next(iter(branch["required"])): branch for branch in self.branches
        }
        self.assertEqual(
            set(forms),
            {"literal", "variable", "values", "concat", "regex_capture",
             "unique", "merge", "count", "split", "substring", "arithmetic",
             "begin", "end"},
        )
        counted = forms["count"]
        self.assertEqual(counted["properties"]["count"]["$ref"], "#/$defs/expression")
        self.assertFalse(counted["additionalProperties"])
        self.assertEqual(counted["required"], ["count"])

    def test_existing_variable_shapes_remain_unchanged_in_number(self):
        self.assertEqual(self.schema["x-scap-ng-version"], "0.4.0")
        self.assertEqual(len(self.branches), 13)

    def test_count_describes_duplicates_and_failed_collection(self):
        definition = next(branch for branch in self.branches if branch["required"] == ["count"])
        help_text = definition["properties"]["count"]["description"].lower()
        self.assertIn("duplicates", help_text)
        self.assertIn("zero", help_text)
        self.assertIn("error", help_text)
        self.assertIn("not-collected", help_text)


if __name__ == "__main__":
    unittest.main()
