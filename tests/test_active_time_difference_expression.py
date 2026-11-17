"""Active SCAP-NG 0.4.1 time_difference schema contract."""
import json
import unittest
from pathlib import Path

SCHEMA = Path(__file__).resolve().parents[1] / "schema" / "variable-expression.schema.json"


class ActiveTimeDifferenceContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        document = json.loads(SCHEMA.read_text(encoding="utf-8"))
        cls.branch = next(x for x in document["$defs"]["expression"]["oneOf"] if x["required"] == ["time_difference"])
        cls.node = cls.branch["properties"]["time_difference"]

    def test_active_shape_is_not_generic_function_envelope(self):
        self.assertEqual(self.node["required"], ["values"])
        self.assertEqual(self.node["properties"]["values"]["minItems"], 1)
        self.assertEqual(self.node["properties"]["values"]["maxItems"], 2)
        self.assertFalse(self.node["additionalProperties"])
        self.assertNotIn("function", self.node["properties"])

    def test_oval_formats_are_explicit_and_utc_semantics_are_documented(self):
        formats = {"year_month_day", "month_day_year", "day_month_year", "seconds_since_epoch", "win_filetime"}
        self.assertEqual(set(self.node["properties"]["format_1"]["enum"]), formats)
        self.assertEqual(set(self.node["properties"]["format_2"]["enum"]), formats)
        description = self.node["description"].lower()
        self.assertIn("utc", description)
        self.assertIn("integer seconds", description)
        self.assertIn("current", description)


if __name__ == "__main__":
    unittest.main()
