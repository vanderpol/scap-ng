#!/usr/bin/env python3
"""Read-only 0.4 review inventory and cross-format regression checks (#232)."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from zipfile import ZipFile

sys.path.insert(0, str(Path(__file__).resolve().parent))

from audit_v04_review_readiness import inventory, review


def fixture():
    return {
        "authoring/example/benchmark.json": {
            "benchmark": {"id": "benchmark.example", "assessment_specifications": [
                {"id": "scap-ng.automated", "version": "0.4.0"}]}},
        "authoring/example/rules/SV-example.json": {"rule": {
            "id": "SV-example", "default_assessment_choice": "manual",
            "assessment_choices": {
                "manual": {"assessment": "example.manual"},
                "automated": {"assessment": "example.automated"}}}},
        "authoring/example/assessments/manual/check.json": {"assessment": {
            "id": "example.manual", "mode": "manual",
            "procedure": "Verify the documented setting."}},
        "authoring/example/assessments/automated/check.json": {"assessment": {
            "id": "example.automated", "mode": "automated",
            "tests": {
                "simple": {"require": {"items": "at_least_one"},
                           "reported_elements": ["name"]},
                "source": {"require": "at_least_one_exists_and_all_match",
                           "states": [{"value": {"equals": "on"}}],
                           "reported_elements": ["value"]}},
            "evaluate": {"and": [{"test": "simple"}, {"test": "source"}]}}},
    }


def zip_archive(path: Path, documents: dict, *, fmt: str):
    with ZipFile(path, "w") as archive:
        for source_path, doc in sorted(documents.items()):
            if fmt == "yaml":
                import yaml
                archive.writestr(source_path.replace(".json", ".yaml"),
                                 yaml.safe_dump(doc, sort_keys=False))
            else:
                archive.writestr(source_path, json.dumps(doc, sort_keys=True))


class ReviewReadinessTests(unittest.TestCase):
    def test_counts_are_factual_and_scanner_conformance_not_claimed(self):
        result = inventory(fixture())
        counts = result["counts"]
        self.assertEqual(counts["rule_documents"], 1)
        self.assertEqual(counts["rules_with_both_choices"], 1)
        self.assertEqual(counts["source_exact_fallback"], 1)
        self.assertEqual(counts["presence_only"], 1)
        self.assertEqual(counts["explicit_reported_elements"], 2)
        self.assertEqual(counts["manual_assessments"], 1)
        self.assertEqual(counts["automated_assessments"], 1)
        self.assertEqual(result["public_tool_readiness"]["automatic_semantic_rewriting"], False)
        self.assertIn("NOT_SCANNER_OR_OVAL_CONFORMANCE", result["status"])

    def test_identical_json_yaml_reports_match_independently(self):
        with TemporaryDirectory() as directory:
            json_path = Path(directory) / "authoring-json.zip"
            yaml_path = Path(directory) / "authoring-yaml.zip"
            zip_archive(json_path, fixture(), fmt="json")
            zip_archive(yaml_path, fixture(), fmt="yaml")
            result = review(json_path, yaml_path)
            self.assertEqual(result["inputs"]["json_yaml_review_parity"], "PASS")
            self.assertEqual(result["counts"]["automated_tests"], 2)

    def test_changed_yaml_procedure_fails_parity(self):
        with TemporaryDirectory() as directory:
            json_path = Path(directory) / "authoring-json.zip"
            yaml_path = Path(directory) / "authoring-yaml.zip"
            zip_archive(json_path, fixture(), fmt="json")
            changed = deepcopy(fixture())
            changed["authoring/example/assessments/manual/check.json"]["assessment"][
                "procedure"] = "Check a changed procedure."
            zip_archive(yaml_path, changed, fmt="yaml")
            with self.assertRaisesRegex(ValueError, "JSON/YAML human-review inventory differs"):
                review(json_path, yaml_path)

    def test_malformed_rule_reference_fails_before_reporting(self):
        documents = fixture()
        documents["authoring/example/rules/SV-example.json"]["rule"][
            "assessment_choices"]["manual"]["assessment"] = "missing"
        with self.assertRaisesRegex(ValueError, "unresolved authoring graph"):
            inventory(documents)

    def test_review_baseline_is_not_satisfied_by_tiny_fixture(self):
        with TemporaryDirectory() as directory:
            json_path = Path(directory) / "authoring-json.zip"
            zip_archive(json_path, fixture(), fmt="json")
            with self.assertRaisesRegex(ValueError, "six-STIG review baseline changed"):
                review(json_path, assert_six=True)


if __name__ == "__main__":
    unittest.main()
