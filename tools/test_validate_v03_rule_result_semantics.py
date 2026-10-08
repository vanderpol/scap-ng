#!/usr/bin/env python3
"""Positive/negative regressions for #203 bounded Benchmark Rule findings."""
import copy
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, RefResolver
from validate_v03_rule_result_semantics import validate_rule_result_semantics

ROOT = Path(__file__).resolve().parents[1]
S = ROOT / "schema" / "v0.3.0"
E = ROOT / "specification" / "examples" / "0.3.0" / "results"


class RuleFindingSemanticsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads((S / "benchmark-result.schema.json").read_text())
        store = {}
        for path in S.glob("*.schema.json"):
            value = json.loads(path.read_text())
            if "$id" in value:
                store[value["$id"]] = value
        cls.validator = Draft202012Validator(
            cls.schema, resolver=RefResolver.from_schema(cls.schema, store=store)
        )

    def doc(self):
        return json.loads((E / "benchmark-result.json").read_text())

    def test_embedded_rule_finding_and_manual_empty_projection(self):
        doc = self.doc()
        self.assertEqual(list(self.validator.iter_errors(doc)), [])
        rules = doc["benchmark_result"]["rule_results"]
        self.assertEqual(len(rules), 2)
        for rule in rules:
            self.assertEqual(validate_rule_result_semantics(rule), [])
        self.assertEqual(rules[1]["findings"], [])

    def test_finding_matches_authoritative_assessment_witness(self):
        rule = self.doc()["benchmark_result"]["rule_results"][0]
        assessment = json.loads((E / "assessment-result.json").read_text())["assessment_result"]
        test = assessment["tests"][0]
        witness = test["per_item_results"][0]
        comparison = witness["state_results"][0]["entity_results"][0]["comparison_results"][0]
        projected = rule["findings"][0]
        self.assertEqual(projected["item_ref"], witness["item_ref"])
        self.assertEqual(projected["test_ref"], test["id"])
        self.assertEqual(projected["observed"], comparison["item_value"])
        self.assertEqual(projected["expected"], comparison["expected_value"])
        self.assertEqual(projected["subject"]["identifier"],
                         witness["item"]["fields"]["full_path"]["value"])

    def test_missing_resource_no_fictional_item(self):
        doc = self.doc()
        rule = doc["benchmark_result"]["rule_results"][0]
        rule["findings"] = [{
            "kind": "missing", "instance_id": "instance-1",
            "subject": {"kind": "file", "identifier": "/etc/missing.conf"},
            "predicate": "required configuration file",
            "expected_existence": "exists",
            "observed_existence": "does_not_exist",
            "outcome": "fail", "test_ref": "required-file-exists"
        }]
        self.assertEqual(list(self.validator.iter_errors(doc)), [])
        self.assertEqual(validate_rule_result_semantics(rule), [])
        rule["findings"][0]["item_ref"] = "invented"
        self.assertTrue(list(self.validator.iter_errors(doc)))

    def test_multifile_counts_not_conflated_with_sample(self):
        doc = self.doc()
        rule = doc["benchmark_result"]["rule_results"][0]
        rule["finding_counts"] = {
            "evaluated_items": 50000, "observed_violations": 12,
            "actual_violations": 12, "population_complete": True,
            "reported_items": 1, "sample_truncated": True
        }
        self.assertEqual(list(self.validator.iter_errors(doc)), [])
        self.assertEqual(validate_rule_result_semantics(rule), [])
        rule["finding_counts"]["sample_truncated"] = False
        self.assertIn("counts.omission_not_marked",
                      [e["code"] for e in validate_rule_result_semantics(rule)])
        rule["finding_counts"]["sample_truncated"] = True
        rule["finding_counts"]["population_complete"] = False
        rule["finding_counts"]["actual_violations"] = "unknown"
        self.assertEqual(list(self.validator.iter_errors(doc)), [])
        self.assertEqual(validate_rule_result_semantics(rule), [])
        rule["finding_counts"]["actual_violations"] = 12
        self.assertTrue(list(self.validator.iter_errors(doc)))

    def test_wrong_instance_and_retained_count(self):
        rule = self.doc()["benchmark_result"]["rule_results"][0]
        rule["findings"][0]["instance_id"] = "unbound"
        self.assertIn("finding.unbound_instance",
                      [e["code"] for e in validate_rule_result_semantics(rule)])
        rule["findings"][0]["instance_id"] = "instance-1"
        rule["finding_counts"] = {
            "evaluated_items": 2, "observed_violations": 1,
            "actual_violations": 1, "population_complete": True,
            "reported_items": 2, "sample_truncated": False
        }
        self.assertIn("counts.retained_mismatch",
                      [e["code"] for e in validate_rule_result_semantics(rule)])

    def test_redacted_value_cannot_be_exposed(self):
        doc = self.doc()
        value = doc["benchmark_result"]["rule_results"][0]["findings"][0]["observed"]
        value["redacted"] = True
        self.assertTrue(list(self.validator.iter_errors(doc)))
        value.pop("value")
        self.assertEqual(list(self.validator.iter_errors(doc)), [])
        self.assertEqual(validate_rule_result_semantics(doc["benchmark_result"]["rule_results"][0]), [])


if __name__ == "__main__":
    unittest.main()
