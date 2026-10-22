#!/usr/bin/env python3
"""Negative cases for source-backed OVAL existence/matching exception inventory."""
from copy import deepcopy
import unittest

from v04_exception_source_oracle import audit, AXES, BASELINE


def ledger():
    entries = []
    for i, (name, quantity) in enumerate(BASELINE.items()):
        for j in range(quantity):
            entries.append({
                "path": f"authoring/demo/a{i}.json",
                "assessment": f"assessment-{i}", "test": f"test-{j}",
                "require": name,
                "source_test": {"require": name, "states": [{"value": {"equals": "ok"}}]},
            })
    return {"by_requirement": dict(BASELINE), "entries": entries}


class SourceExceptionTests(unittest.TestCase):
    def test_all_real_requirement_families_have_independent_generic_result_axes(self):
        result = audit(ledger(), assert_six=True)
        self.assertEqual(result["source_exceptions"], 221)
        self.assertEqual(len(AXES), 11)
        self.assertEqual(result["all_match_source_exceptions_needing_state_record_review"], 47)
        self.assertGreater(result["generic_oval_scenarios_compared"], 0)
        self.assertFalse(result["native_compact_lowering_proved"])
        self.assertFalse(result["scanner_parity"])

    def test_unknown_label_is_rejected_instead_of_normalized(self):
        obj = ledger()
        obj["entries"][0]["require"] = "invented"
        with self.assertRaisesRegex(ValueError, "unknown source requirement"):
            audit(obj)

    def test_missing_source_states_fails(self):
        obj = ledger()
        obj["entries"][0]["source_test"]["states"] = []
        with self.assertRaisesRegex(ValueError, "lost its State"):
            audit(obj)

    def test_changed_population_does_not_silently_pass(self):
        obj = ledger()
        obj["entries"].pop()
        obj["by_requirement"]["only_one_exists_and_only_one_matches"] -= 1
        with self.assertRaisesRegex(ValueError, "distribution changed"):
            audit(obj, assert_six=True)

    def test_duplicate_source_test_rejected(self):
        obj = ledger()
        obj["entries"].append(deepcopy(obj["entries"][0]))
        obj["by_requirement"]["all_exist_and_all_match"] += 1
        with self.assertRaisesRegex(ValueError, "duplicate/unnamed"):
            audit(obj)


if __name__ == "__main__":
    unittest.main()
