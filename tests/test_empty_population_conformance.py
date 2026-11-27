"""Canonical 0.4.1 empty-population fixture admission; not RI execution."""
import json
import unittest
from pathlib import Path

from conformance.tools.runner import validator

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "conformance/0.4/empty-populations"


class EmptyPopulationConformance(unittest.TestCase):
    def setUp(self):
        self.document = json.loads((PACK / "assessment.json").read_text())
        self.expected = json.loads((PACK / "expected.json").read_text())

    def test_schema_admission(self):
        validator().validate(self.document)

    def test_independent_expected_outcomes_and_evaluate_wiring(self):
        # Independent, explicitly reviewed truth table, not derived from the
        # Assessment generator or from scanner outputs.
        false_ids = {
            "empty-expected-one-or-more", "empty-expected-exactly-one",
            "alias-empty", "unique-empty", "concat-empty", "shell-empty",
            "shell-concat-empty", "empty-source-field",
        }
        true_ids = {
            "empty-expected-none", "empty-expected-every",
            "blank-is-not-empty", "blank-scalar-match", "nonempty-control",
            "count-empty", "shell-positive", "shell-item-exists",
            "shell-capture-absent",
        }
        outcomes = {name + "-test": "false" for name in false_ids}
        outcomes.update({name + "-test": "true" for name in true_ids})
        assessment = self.document["assessment"]
        self.assertEqual(set(assessment["tests"]), set(outcomes))
        self.assertEqual(
            {k: v["outcome"] for k, v in self.expected["tests"].items()}, outcomes
        )
        branches = [
            (node["not"]["test"], "false") if "not" in node else (node["test"], "true")
            for node in assessment["evaluate"]["and"]
        ]
        self.assertEqual(len(branches), len(outcomes))
        self.assertEqual(dict(branches), outcomes)
        self.assertEqual(self.expected["assessment_outcome"], "true")

    def test_empty_and_blank_are_distinct(self):
        variables = self.document["assessment"]["variables"]
        self.assertEqual(variables["empty-variable"]["expression"]["literal"],
                         {"datatype": "string", "value": []})
        self.assertEqual(variables["blank-variable"]["expression"]["literal"], "")
        expected = self.expected["variables"]
        self.assertEqual(expected["empty-variable"], [])
        self.assertEqual(expected["blank-variable"], [""])
        self.assertEqual(expected["count-variable"], [0])
        self.assertEqual(expected["shell-empty-variable"], [])
        self.assertEqual(expected["shell-match-variable"], ["22"])

    def test_mutating_cardinality_is_detected(self):
        # Check the fixture's actual operands, independently of its ID/labels.
        tests = self.document["assessment"]["tests"]
        for mode in ("one_or_more", "exactly_one", "none", "every"):
            field = tests["empty-expected-" + mode.replace("_", "-") + "-test"]["require"]["fields"]["value"]
            self.assertEqual(field["value_match"], mode)
            self.assertEqual(field["equals"], {"variable": "empty-variable"})


if __name__ == "__main__":
    unittest.main()
