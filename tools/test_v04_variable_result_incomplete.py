"""Owner-approved representation of partial Variable values; no evaluator parity claim."""

import copy
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, RefResolver


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schema" / "v0.4.0"
SCHEMA = json.loads((SCHEMA_DIR / "variable-result.schema.json").read_text())
RESULT_TYPES = json.loads((SCHEMA_DIR / "result-types.schema.json").read_text())
VALIDATOR = Draft202012Validator(
    SCHEMA,
    resolver=RefResolver.from_schema(SCHEMA, store={RESULT_TYPES["$id"]: RESULT_TYPES}),
)


def result(status, values):
    cardinality = "zero" if not values else ("one" if len(values) == 1 else "many")
    return {"id": "var:partial", "datatype": "string", "status": status,
            "cardinality": cardinality, "values": values,
            "item_refs": ["item:observed"] if values else [],
            "provenance": {"collection_status": "incomplete"},
            "diagnostics": [{"reason": "collection_not_complete"}]}


def observed(value):
    return {"datatype": "string", "status": "exists", "value": value}


class IncompleteVariableResultSchemaTests(unittest.TestCase):
    def test_incomplete_zero_one_many_observed_values(self):
        for values in ([], [observed("")], [observed("a"), observed("a")]):
            with self.subTest(observed_count=len(values)):
                candidate = result("incomplete", values)
                self.assertTrue(VALIDATOR.is_valid(candidate), list(VALIDATOR.iter_errors(candidate)))

    def test_existing_statuses_remain_valid(self):
        for status in ("complete", "error", "unknown", "not_evaluated",
                       "not_applicable", "zero_values"):
            with self.subTest(status=status):
                self.assertTrue(VALIDATOR.is_valid(result(status, [])))

    def test_unknown_status_and_untyped_observation_rejected(self):
        candidate = result("partial", [observed("a")])
        self.assertFalse(VALIDATOR.is_valid(candidate))
        candidate = result("incomplete", [observed("a")])
        candidate["values"][0].pop("datatype")
        self.assertFalse(VALIDATOR.is_valid(candidate))

    def test_incomplete_still_requires_provenance_refs_and_cardinality(self):
        candidate = result("incomplete", [observed("a")])
        for required in ("id", "datatype", "status", "cardinality", "values", "item_refs"):
            with self.subTest(required=required):
                mutated = copy.deepcopy(candidate)
                del mutated[required]
                self.assertFalse(VALIDATOR.is_valid(mutated))

    def test_no_status_precedence_asserted(self):
        """A schema-valid partial value set is not a computed count/unique result."""
        self.assertTrue(VALIDATOR.is_valid(result("incomplete", [observed("a")])))


if __name__ == "__main__":
    unittest.main()
