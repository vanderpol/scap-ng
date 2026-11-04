"""Cross-repository Issue #14/#19 audit integrity checks.

These checks use the repository's JSON artifacts and the accepted cross-repository
compatibility evidence. They do not claim scanner/runtime evaluation parity.
"""
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator
import yaml
from referencing import Registry, Resource


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
        resources = {}
        schema_root = ROOT / "schema"
        for path in sorted((*schema_root.glob("*.json"), *(schema_root / "capability-mappings").rglob("*.json"))):
            document = json.loads(path.read_text(encoding="utf-8"))
            if "$schema" not in document:
                continue
            resource = Resource.from_contents(document)
            resources["https://scap-ng.dev/schema/v0.4.0/" + path.relative_to(schema_root).as_posix()] = resource
            if "$id" in document:
                resources[document["$id"]] = resource
        cls.assessment_validator = Draft202012Validator(
            load("schema/assessment.schema.json"),
            registry=Registry().with_resources(resources.items()),
        )
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
        self.assertEqual(mismatches, [])
        for capability in ("unix.file", "windows.file", "windows.fileeffectiverights"):
            rows = [row for row in self.audit["selector_matrix"] if row["capability"] == capability]
            self.assertEqual(
                {row["selector"] for row in rows if row["selector"] in {"filepath", "path", "filename"}},
                {"filepath", "path", "filename"},
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
        self.assertEqual(self.audit["snapshot_gate"]["status"], "verified_against_accepted_candidate")
        self.assertIn("145 JSON files", self.audit["snapshot_gate"]["finding"])
        self.assertIn("673 root references", self.audit["snapshot_gate"]["finding"])
        self.assertEqual(
            self.audit["editor_pin"]["schema_digest"],
            "d2d8d59bcc722eacdba80342232f6d92d5bba812aab077753486268c3f74aa2d",
        )
        self.assertEqual(self.audit["editor_pin"]["resource_count"], 236)

    def test_filesystem_alternatives_have_recorded_compatibility_outcomes(self):
        evidence = ROOT / "docs/evidence/issue21/filesystem-selector-alternatives"
        valid = yaml.safe_load((evidence / "alternative-a.assessment.yaml").read_text())
        self.assertEqual(list(self.assessment_validator.iter_errors(valid)), [])
        for name in ("alternative-b.assessment.yaml", "tools-emission.assessment.yaml"):
            with self.subTest(name=name):
                candidate = yaml.safe_load((evidence / name).read_text())
                errors = list(self.assessment_validator.iter_errors(candidate))
                self.assertTrue(errors)
                self.assertIn("full_path", errors[0].message)

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
