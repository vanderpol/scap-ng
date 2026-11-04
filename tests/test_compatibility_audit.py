"""Cross-repository Issue #14/#19 audit integrity checks.

These checks intentionally use only the repository's JSON artifacts. They do not
claim that the separately pinned converter can execute against this snapshot.
"""
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def load(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


class CompatibilityAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit = load("docs/metadata/compatibility-audit.json")
        cls.selector_audit = load("docs/metadata/native-selector-audit.json")
        cls.contracts = load("schema/native-selector-contracts.json")
        cls.generated = load("schema/native-selector.schema.json")
        cls.mappings = {
            path.stem: json.loads(path.read_text(encoding="utf-8"))
            for path in (ROOT / "schema/capability-mappings/supported").glob("*.json")
        }

    def test_inventory_reconciles_with_generated_contract_inventory(self):
        reconciliation = self.audit["inventory_reconciliation"]
        self.assertTrue(reconciliation["reconciled"])
        self.assertEqual(
            (reconciliation["total"], reconciliation["resolved"], reconciliation["unresolved"]),
            (
                self.selector_audit["selector_count"],
                self.selector_audit["resolved_count"],
                self.selector_audit["unresolved_count"],
            ),
        )
        self.assertEqual(
            reconciliation["total"],
            reconciliation["resolved"] + reconciliation["unresolved"],
        )
        resolved = {
            (item["capability"], item["selector"])
            for item in self.selector_audit["selectors"]
            if item["status"] == "resolved"
        }
        matrix = {
            (item["capability"], item["selector"])
            for item in self.audit["selector_matrix"]
        }
        self.assertEqual(matrix, resolved)
        self.assertEqual(len(matrix), reconciliation["resolved"])
        for capability, selector in matrix:
            prefix = capability.replace(".", "_")
            self.assertIn(f"{prefix}_object", self.generated["$defs"])
            self.assertIn(f"{prefix}_{selector}_selector", self.generated["$defs"])

    def test_selector_matrix_is_derived_from_mapping_emission(self):
        mismatches = []
        for row in self.audit["selector_matrix"]:
            mapping = self.mappings[row["capability"]]
            emitted = mapping["native"]["selector_map"][row["selector"]]
            self.assertEqual(emitted, row["converter_emission"]["native_yaml_key"])
            if emitted != row["selector"]:
                mismatches.append((row["capability"], row["selector"], emitted))
        self.assertEqual(len(self.audit["selector_matrix"]), 28)
        self.assertEqual(len(mismatches), 9)
        self.assertEqual(
            set(mismatches),
            {
                ("unix.file", "filepath", "full_path"),
                ("unix.file", "path", "directory"),
                ("unix.file", "filename", "name"),
                ("windows.file", "filepath", "full_path"),
                ("windows.file", "path", "directory"),
                ("windows.file", "filename", "name"),
                ("windows.fileeffectiverights", "filepath", "full_path"),
                ("windows.fileeffectiverights", "path", "directory"),
                ("windows.fileeffectiverights", "filename", "name"),
            },
        )

    def test_all_retained_forms_and_runtime_boundaries_are_explicit(self):
        self.assertEqual(
            {item["name"] for item in self.audit["variable_forms"]},
            {"literal", "variable", "values", "concat", "regex_capture", "unique", "merge"},
        )
        self.assertEqual(
            self.audit["variable_forms"]
            [next(i for i, item in enumerate(self.audit["variable_forms"]) if item["name"] == "unique")]
            ["status"],
            "owner_review_required_oval_arity_gap",
        )
        for axis in self.audit["semantic_axes"]:
            self.assertNotIn("runtime_verified", axis["status"])
        self.assertEqual(self.audit["snapshot_gate"]["status"], "blocked_for_direct_execution")

    def test_source_resolved_count_remains_distinct_from_matrix_count(self):
        # The contract input and generated audit both cover the accumulated
        # resolved selectors across the two reviewed batches.
        self.assertEqual(
            sum(len(value.get("selectors", {})) for value in self.contracts["resolved"].values()),
            28,
        )
        self.assertEqual(self.audit["inventory_reconciliation"]["source_resolved"], 28)


if __name__ == "__main__":
    unittest.main()
