"""Independent regression tests for the approved Model A truth oracle."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "conformance/tools"))
from model_a_oracle import evaluate  # noqa: E402


CASES = {
    "one-group": "true", "field-every-false": "false", "duplicate-count": "false",
    "no-match": "true", "string-alias": "true", "string-alias-false": "false",
    "item-existence-false": "false", "field-existence-false": "false", "item-none-satisfy": "true", "expected-any": "true",
    "expected-duplicate-count": "false", "expected-every-false": "false", "expected-none": "true",
    "alias-one-group": "true", "not-zipwise": "true",
}


class ModelAOracleTests(unittest.TestCase):
    def test_independent_outcomes_and_cardinality_observations(self):
        for case, expected in CASES.items():
            with self.subTest(case=case):
                document = json.loads((ROOT / f"conformance/0.4/model-a/{case}.json").read_text())
                result = evaluate(document)
                self.assertEqual(result["technical_outcome"], expected)
                self.assertGreaterEqual(result["items_found"], 1)
                self.assertLessEqual(result["items_satisfying"], result["items_found"])
                self.assertLessEqual(result["values_matching"], result["values_found"])

    def test_duplicate_values_are_counted_not_deduplicated(self):
        document = json.loads((ROOT / "conformance/0.4/model-a/duplicate-count.json").read_text())
        result = evaluate(document)
        self.assertEqual(result["values_found"], 2)
        self.assertEqual(result["values_matching"], 2)
        self.assertEqual(result["technical_outcome"], "false")

    def test_oracle_rejects_outside_model_a_domain(self):
        document = json.loads((ROOT / "conformance/0.4/model-a/one-group.json").read_text())
        document["assessment"]["variables"]["source-variable"]["expression"]["literal"] = []
        with self.assertRaises(ValueError):
            evaluate(document)


if __name__ == "__main__":
    unittest.main()
