"""Verify canonical Set observations independently of acquisition and scale."""
from hashlib import sha256
import unittest

from conformance.tools.runner import CONFORMANCE, load

REPLAY = CONFORMANCE / "set-replay"


class SetReplayCases(unittest.TestCase):
    def test_memory_and_stream_ordering_and_incomplete_populations(self):
        receipt = load(REPLAY / "ri-receipt.json")
        controls = load(REPLAY / "controls.json")
        expected = load(CONFORMANCE / "expected/core-set-filters.json")["operations"]
        self.assertEqual(receipt["schema_pin"], controls["schema_pin"])
        for name, digest in receipt["sha256"].items():
            self.assertEqual(sha256((CONFORMANCE / name).read_bytes()).hexdigest(), digest)

        observed = receipt["observed"]
        self.assertEqual(len(observed), len(expected) + len(controls["controls"]))
        for operation, oracle in expected.items():
            case = observed[f"set-{operation}-test"]
            expected_row = {"ids": oracle["values"], "complete": True}
            self.assertEqual(case, {"memory": expected_row, "stream": expected_row})
            self.assertEqual(len(case["stream"]["ids"]), oracle["items_found"])
        for name, oracle in controls["controls"].items():
            row = {"ids": oracle.get("observed_partial_ids", []), "complete": oracle["complete"]}
            if "diagnostic" in oracle:
                row["diagnostic"] = oracle["diagnostic"]
            self.assertEqual(observed[name], {"memory": row, "stream": row})

    def test_each_indexed_operation_has_both_scale_receipts(self):
        scale = load(REPLAY / "scale.json")
        receipt = load(REPLAY / "ri-receipt.json")
        self.assertEqual(scale["ri_revision"], receipt["ri_revision"])
        operations = {"union", "intersection", "difference"}
        populations = {100_000, 1_000_000}
        self.assertEqual(len(scale["runs"]), len(operations) * len(populations))
        self.assertEqual(
            {(run["operation"], run["items_per_operand"]) for run in scale["runs"]},
            {(operation, size) for operation in operations for size in populations},
        )
        for run in scale["runs"]:
            self.assertEqual(run["status"], "pass")
            self.assertEqual(run["operands"], 2)
            count = 0 if run["operation"] == "difference" else run["items_per_operand"]
            self.assertEqual(run["matched_output_count"], count)
            self.assertGreater(run["disk_bytes"], 0)
            self.assertGreater(run["peak_sampled_rss_bytes"], 0)
        self.assertEqual(scale["shared_budget_checks"]["status"], "pass")
        self.assertEqual(len(scale["shared_budget_checks"]["tests"]), 2)


if __name__ == "__main__":
    unittest.main()
