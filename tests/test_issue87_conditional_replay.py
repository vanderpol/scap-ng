"""Verify conditional selection and distinguish runtime holds from wire validation."""
from hashlib import sha256
import unittest

from conformance.tools.runner import CONFORMANCE, load, schema_validator, validator

REPLAY = CONFORMANCE / "conditional-replay"


class ConditionalReplayCases(unittest.TestCase):
    def test_named_branches_and_explicit_empty_input(self):
        expected = load(REPLAY / "expected.json")
        receipt = load(REPLAY / "ri-receipt.json")
        self.assertEqual(receipt["schema_pin"], expected["schema_pin"])
        for name, digest in receipt["source_sha256"].items():
            self.assertEqual(sha256((CONFORMANCE / name).read_bytes()).hexdigest(), digest)
        document = load(REPLAY / "mixed-guards.assessment.yaml")
        validator().validate(document)
        mixed = document["assessment"]["evaluate"]
        present = expected["mixed"]["present-empty-selects-later"]["supplied_inputs"]
        self.assertEqual(present, {"fallback-input": []})
        self.assertEqual(mixed["else_if"][1]["if"], {"input_provided": "fallback-input"})

        existing = load(CONFORMANCE / "expected/conditional-ordered.json")["variants"]
        cases = receipt["cases"]
        self.assertEqual(len(cases), len(expected["mixed"]) + len(expected["ordered"]))
        for family in ("mixed", "ordered"):
            for name, row in expected[family].items():
                observed = cases[f"{family}/{name}"]
                self.assertEqual(observed["selected"], row["selected"])
                self.assertEqual(observed["branch_index"], row["branch_index"])
                self.assertEqual(observed["terminal_paths"], [row["terminal_path"]] if "terminal_path" in row else [])
                if "ri_hold" not in row:
                    outcome = row["outcome"] if family == "mixed" else existing[name]["assessment_outcome"]
                    self.assertEqual(observed["expected_outcome"], outcome)
                    self.assertEqual(observed["observed_outcome"], outcome)
                    self.assertEqual(observed["status"], "matched")
                    self.assertEqual(observed["wire_diagnostics"], [])

    def test_later_indeterminate_guards_have_incompatible_projected_trace(self):
        report = load(REPLAY / "ri-receipt.json")["cases"]
        schema = schema_validator("expression-invocation.schema.json")
        for cause in ("error", "unknown"):
            observed = report[f"mixed/later-{cause}"]
            self.assertEqual(observed["status"], "wire-rejected")
            self.assertEqual(observed["observed_outcome"], cause)
            self.assertEqual((observed["condition_outcome"], observed["selected"]), ("false", None))
            wire = {
                "assessment": "conformance-conditional-mixed-guards",
                "invocation_ref": "fixture-invocation",
                "outcome": cause,
                "executed_tests": ["initial-guard-test", "secondary-guard-test"],
                "trace": [{
                    "path": "/evaluate", "kind": "conditional", "outcome": cause,
                    "owner_invocation_ref": "fixture-invocation",
                    "condition_outcome": observed["condition_outcome"], "selected_branch": observed["selected"],
                }],
                "diagnostics": [],
            }
            self.assertEqual([error.message for error in schema.iter_errors(wire)], observed["wire_diagnostics"])
            self.assertFalse(schema.is_valid(wire))

    def test_first_guard_statuses_remain_independent_of_normalized_observation(self):
        report = load(REPLAY / "ri-receipt.json")["cases"]
        for cause in ("not_applicable", "not_evaluated"):
            observed = report[f"mixed/initial-{cause}"]
            self.assertEqual(observed["status"], "status-normalized")
            self.assertEqual(observed["expected_outcome"], cause)
            self.assertEqual(observed["observed_outcome"], "unknown")
            self.assertIsNone(observed["selected"])


if __name__ == "__main__":
    unittest.main()
