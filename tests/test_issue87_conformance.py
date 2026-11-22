"""Regression gates for the independent SCAP-NG 0.4.1 conformance corpus."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path
from copy import deepcopy

from conformance.tools.oracle import compare

ROOT = Path(__file__).resolve().parents[1]
CONF = ROOT / "conformance"
SCHEMA = ROOT / "schema"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class Issue87Conformance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = read(CONF / "manifest.json")
        cls.inventory = read(CONF / "schema-coverage.json")

    def test_manifest_is_exactly_pinned_to_checked_out_schema(self):
        commit = self.manifest["schema_commit"]
        self.assertRegex(commit, r"^[0-9a-f]{40}$")
        self.assertEqual(subprocess.run(["git", "cat-file", "-e", f"{commit}^{{commit}}"], cwd=ROOT).returncode, 0)
        paths = sorted((ROOT / "schema").glob("*.json")) + sorted((ROOT / "schema/capability-mappings").rglob("*.json"))
        digest = hashlib.sha256()
        for path in sorted(paths):
            digest.update(path.relative_to(SCHEMA).as_posix().encode() + b"\0")
            digest.update(path.read_bytes())
        self.assertEqual(self.inventory["schema_family_sha256"], digest.hexdigest())
        self.assertEqual(self.manifest["schema_family_sha256"], self.inventory["schema_family_sha256"])

    def test_inventory_and_vectors_are_exhaustive_for_mappings(self):
        capabilities = {row["capability"] for row in self.inventory["capabilities"]}
        cases = {row["capability"] for row in self.manifest["capabilities"]}
        self.assertEqual(cases, capabilities)
        self.assertEqual(self.inventory["counts"]["capability_mappings"], len(cases))
        required = {"positive", "negative", "boundary", "empty", "permission-denied", "error", "not-applicable", "multi-item"}
        for row in self.manifest["capabilities"]:
            self.assertTrue(required.issubset(row["vectors"]), row["capability"])
            for kind in ("assessment", "fixture", "expected"):
                path = CONF / row[kind]
                self.assertTrue(path.is_file(), path)
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), row["sha256"][kind], path)

    def test_negative_variants_are_distinct_and_preserve_selectors(self):
        for row in self.manifest["capabilities"]:
            fixture = read(CONF / row["fixture"])
            positive = fixture["variants"]["positive"]
            negative = fixture["variants"]["negative"]
            self.assertFalse(
                positive == negative,
                f"{row['capability']} has identical positive/negative evidence",
            )
            contract = fixture["semantic_contract"]
            if contract["negative_strategy"] == "field-mismatch":
                self.assertEqual(len(positive["items"]), 1, row["capability"])
                self.assertEqual(len(negative["items"]), 1, row["capability"])
                for selector in contract["selector_fields"]:
                    self.assertEqual(
                        positive["items"][0]["fields"].get(selector),
                        negative["items"][0]["fields"].get(selector),
                        f"{row['capability']} negative changed selector {selector}",
                    )
                field = contract["negative_field"]
                self.assertNotEqual(
                    positive["items"][0]["fields"].get(field),
                    negative["items"][0]["fields"].get(field),
                    f"{row['capability']} negative did not change Require field",
                )
            else:
                self.assertEqual(negative["items"], [], row["capability"])
                self.assertEqual(negative["acquisition"], "collected", row["capability"])
            expected = read(CONF / row["expected"])
            self.assertNotEqual(
                expected["variants"]["positive"]["assessment_outcome"],
                expected["variants"]["negative"]["assessment_outcome"],
                row["capability"],
            )

    def _valid_receipt(self):
        row = next(row for row in self.manifest["capabilities"] if row["capability"] == "windows.registry")
        expected = read(CONF / row["expected"])
        fixture = read(CONF / row["fixture"])
        item = fixture["variants"]["positive"]["items"][0]
        evidence = [{"item_id": item["id"], "field": field, "datatype": value["datatype"], "status": value["status"], "value": value["value"]} for field, value in item["fields"].items()]
        receipt = {"format": "scap-ng-conformance-receipt-0.1", "schema_version": self.manifest["schema_version"], "schema_commit": self.manifest["schema_commit"], "case_id": "windows.registry", "variant": "positive", "fixture_sha256": row["sha256"]["fixture"], "expected_sha256": row["sha256"]["expected"], "assessment_outcome": "true", "test_outcomes": {"windows-registry-test": "true"}, "items_found": 1, "items_satisfying": 1, "decisive_reason": expected["variants"]["positive"]["reason"], "evidence": evidence, "provenance": {"source": "deterministic-fixture", "fixture_variant": "positive", "fixture_sha256": row["sha256"]["fixture"], "expected_sha256": row["sha256"]["expected"], "schema_commit": self.manifest["schema_commit"]}}
        return expected, fixture, receipt, row

    def test_oracle_accepts_complete_receipt(self):
        expected, fixture, receipt, row = self._valid_receipt()
        self.assertEqual(compare(expected, receipt, manifest=self.manifest, fixture=fixture, fixture_sha256=row["sha256"]["fixture"], expected_sha256=row["sha256"]["expected"], test_names=["windows-registry-test"]), [])

    def test_oracle_rejects_missing_or_mismatched_identity_and_proof(self):
        expected, fixture, receipt, row = self._valid_receipt()
        mutations = {
            "schema pin": ("schema_commit", "0" * 40),
            "fixture hash": ("fixture_sha256", "bad"),
            "expected hash": ("expected_sha256", "bad"),
            "test outcomes": ("test_outcomes", {}),
            "decisive reason": ("decisive_reason", "wrong"),
            "provenance": ("provenance", {"source": "deterministic-fixture"}),
            "typed evidence": ("evidence", [{"item_id": "windows-registry-item", "field": "hive", "datatype": "string", "status": "collected"}]),
        }
        for name, (key, value) in mutations.items():
            with self.subTest(name=name):
                mutant = deepcopy(receipt); mutant[key] = value
                errors = compare(expected, mutant, manifest=self.manifest, fixture=fixture, fixture_sha256=row["sha256"]["fixture"], expected_sha256=row["sha256"]["expected"], test_names=["windows-registry-test"])
                self.assertTrue(errors, name)

    def test_core_semantics_keep_false_leaf_visible_and_only_not_negates(self):
        assessment = (CONF / "cases/core/evaluate-not.assessment.yaml").read_text(encoding="utf-8")
        self.assertIn("not:", assessment)
        self.assertNotIn("negate:", assessment)
        expected = read(CONF / "expected/core-evaluate-not.json")
        self.assertEqual(expected["underlying"]["false-test"], "false")
        self.assertEqual(expected["assertions"]["not(false)"], "true")
        self.assertEqual(expected["assertions"]["unknown"], "unknown")
        self.assertEqual(expected["assertions"]["error"], "error")
        self.assertEqual(expected["assertions"]["not_applicable"], "not_applicable")

    def test_audit_reports_scope_without_false_semantic_completeness(self):
        audit = read(CONF / "coverage-audit.json")
        self.assertEqual(audit["schema_commit"], self.manifest["schema_commit"])
        self.assertEqual(audit["schema_family_sha256"], self.manifest["schema_family_sha256"])
        self.assertEqual(audit["vectors"]["base_capability_vectors_total"], 728)
        self.assertEqual(audit["vectors"]["expanded_capability_vectors_total"], 832)
        self.assertEqual(audit["vectors"]["multi_value_suite_cases"], 103)
        self.assertEqual(audit["fields"]["declared_mapping_fields"], 710)
        self.assertEqual(audit["fields"]["authored_assessment_fields"], 710)
        self.assertEqual(audit["selectors"]["uncovered_alternative_sets"], 0)
        self.assertEqual(audit["operators"]["uncovered_comparison"], [])
        self.assertEqual(audit["cardinalities"]["uncovered"], [])
        self.assertEqual(audit["exceptional_outcomes"]["uncovered_defined_outcomes"], [])
        self.assertGreater(audit["enum_boundaries"]["schema_rejected_mutations"], 0)
        self.assertFalse(audit["schema_branches"]["direct_executable_branch_coverage"])
        self.assertTrue(audit["expected_results"]["independent_justification"])
        self.assertEqual(audit["independent_oracle"]["source_cases"], 15)
        self.assertFalse(audit["independent_oracle"]["runtime_qualification"])
        derived = audit["derived_integrity"]
        self.assertEqual(derived["fields_from_source_mappings"], 710)
        self.assertEqual(derived["fields_from_authored_assessments"], 710)
        self.assertEqual(derived["fields_from_positive_fixtures"], 710)
        self.assertEqual(derived["operators_from_source_schema"], 67)
        self.assertEqual(derived["operators_from_authored_assessments"], 67)
        self.assertEqual(derived["selector_alternatives_from_source_mappings"], 94)
        self.assertEqual(derived["selector_alternatives_from_authored_assessments"], 94)
        self.assertEqual(derived["missing_witnesses"], {"fields": [], "selectors": [], "operators": [], "cardinalities": []})
        self.assertEqual(derived["non_exercising_witnesses"], [])
        for row in self.manifest["capabilities"]:
            expected = read(CONF / row["expected"])
            for assertion in expected["variants"].values():
                self.assertTrue(assertion["reason"].strip())

    def test_core_expansions_cover_operators_selectors_cardinalities_and_statuses(self):
        operators = read(CONF / "expected/core-comparison-operators.json")
        active = set(self.inventory["operator_inventory"]["field_predicate_properties"])
        self.assertEqual(set(operators["operators"]), active)
        selectors = read(CONF / "expected/core-selector-alternatives.json")
        declared = sum(len(row["selector_alternatives"]) for row in self.inventory["capabilities"])
        self.assertEqual(len(selectors["alternatives"]), declared)
        multi_values = read(CONF / "expected/core-multi-values.json")
        self.assertEqual(len(multi_values["capabilities"]), 103)
        enum_boundaries = read(CONF / "expected/core-enum-boundaries.json")
        self.assertEqual(len(enum_boundaries["enum_values"]), 12)
        self.assertEqual(read(CONF / "coverage-audit.json")["enum_boundaries"]["uncovered_native_selector_enum_values"], [])
        cardinalities = read(CONF / "expected/core-cardinalities.json")
        self.assertEqual(set(cardinalities["cardinalities"]), {"item-exactly-one", "item-none", "item-zero-or-more", "field-exactly-one", "field-none", "field-zero-or-more"})
        for row in self.manifest["status_cases"]:
            self.assertTrue(read(CONF / row["expected"])["reason"].strip())

    def test_offline_schema_runner_and_invalid_negate_gate(self):
        command = [sys.executable, str(CONF / "tools/runner.py"), "validate"]
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        result = subprocess.run([sys.executable, str(CONF / "tools/runner.py"), "coverage"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
