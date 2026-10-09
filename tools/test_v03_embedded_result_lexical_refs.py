#!/usr/bin/env python3
"""#208 — consumer-local predicate location in 0.3 sample Assessment Results."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAMPLES = ROOT / "specification/examples/0.3.0/results"


class EmbeddedResultPredicateReferences(unittest.TestCase):
    def test_all_sample_comparison_references_are_lexical(self):
        inspected = 0
        for path in sorted(SAMPLES.glob("assessment-result*.json")):
            result = json.loads(path.read_text(encoding="utf-8"))["assessment_result"]
            for test in result.get("tests") or []:
                names = test.get("state_refs") or []
                expected = [f"{test['id']}.states[{i}]" for i in range(len(names))]
                with self.subTest(file=path.name, test=test["id"]):
                    self.assertEqual(names, expected)
                for item in test.get("per_item_results") or []:
                    for state in item.get("state_results") or []:
                        with self.subTest(file=path.name, test=test["id"], item=item["item_ref"]):
                            self.assertIn(state["state_ref"], names)
                inspected += 1
        self.assertGreaterEqual(inspected, 8)


if __name__ == "__main__":
    unittest.main()
