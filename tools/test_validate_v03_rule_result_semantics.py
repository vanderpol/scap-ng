#!/usr/bin/env python3
"""Positive/negative regressions for #203 bounded Benchmark Rule findings."""
import copy
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, RefResolver
from validate_v03_rule_result_semantics import validate_rule_result_semantics, validate_organizational_consumption_links

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

    def test_organizational_input_value_and_provenance_are_linked_not_duplicated(self):
        doc = json.loads((E / "benchmark-result-organizational-input.json").read_text())
        assessment = json.loads((E / "assessment-result-organizational-input.json").read_text())
        self.assertEqual(list(self.validator.iter_errors(doc)), [])
        rule = doc["benchmark_result"]["rule_results"][0]
        registry = doc["benchmark_result"]["effective_policy"]["organizational_inputs"]
        consumed = assessment["assessment_result"]["consumed_organizational_inputs"]
        required = {entry["organizational_input_ref"] for entry in consumed
                    if entry["materialized"]}
        self.assertEqual(
            validate_rule_result_semantics(
                rule, organizational_input_registry=registry,
                required_organizational_input_refs=required,
            ), [],
        )
        self.assertEqual(rule["organizational_inputs"][0]["value"], 0)
        self.assertNotIn("supplied_by", rule["organizational_inputs"][0])
        self.assertIn("supplied_by", registry["org-file-owner"]["provenance"])

    def test_organizational_input_mismatch_unknown_ref_and_missing_disclosure(self):
        doc = json.loads((E / "benchmark-result-organizational-input.json").read_text())
        rule = doc["benchmark_result"]["rule_results"][0]
        registry = doc["benchmark_result"]["effective_policy"]["organizational_inputs"]
        params = {"organizational_input_registry":registry,
                  "required_organizational_input_refs":{"org-file-owner"}}
        rule["organizational_inputs"][0]["value"] = 17
        self.assertIn("organizational_input.value_mismatch",
                      [e["code"] for e in validate_rule_result_semantics(rule, **params)])
        rule["organizational_inputs"][0]["value"] = 0
        rule["organizational_inputs"][0]["provenance_summary"]["authorization_reference"] = "FALSE-42"
        self.assertIn("organizational_input.provenance_mismatch",
                      [e["code"] for e in validate_rule_result_semantics(rule, **params)])
        rule["organizational_inputs"][0]["provenance_summary"]["authorization_reference"] = "EXAMPLE-SEC-42"
        rule["organizational_inputs"][0]["organizational_input_ref"] = "unrecognized"
        failures = [e["code"] for e in validate_rule_result_semantics(rule, **params)]
        self.assertIn("organizational_input.unknown_ref", failures)
        self.assertIn("organizational_input.consumed_ref_not_exposed", failures)
        rule["organizational_inputs"] = []
        self.assertIn("organizational_input.consumed_ref_not_exposed",
                      [e["code"] for e in validate_rule_result_semantics(rule, **params)])

    def test_organizational_input_redaction_and_no_duplicate_policy_values(self):
        doc = json.loads((E / "benchmark-result-organizational-input.json").read_text())
        rule = doc["benchmark_result"]["rule_results"][0]
        registry = doc["benchmark_result"]["effective_policy"]["organizational_inputs"]
        entry = rule["organizational_inputs"][0]
        entry["redacted"] = True
        self.assertTrue(list(self.validator.iter_errors(doc)),
                        "schema must prohibit a redacted value being copied")
        entry.pop("value")
        self.assertEqual(list(self.validator.iter_errors(doc)), [])
        self.assertEqual(validate_rule_result_semantics(
            rule, organizational_input_registry=registry), [])
        registry["org-file-owner"]["redacted"] = True
        registry["org-file-owner"].pop("value")
        self.assertEqual(validate_rule_result_semantics(
            rule, organizational_input_registry=registry), [])
        entry["redacted"] = False
        entry["value"] = 0
        failures = [e["code"] for e in validate_rule_result_semantics(
            rule, organizational_input_registry=registry)]
        self.assertIn("organizational_input.authority_redaction_violation", failures)
        self.assertIn("organizational_input.value_mismatch", failures)

    def complete_organizational_execution_results(self):
        documents = {}
        for filename in ("assessment-result-organizational-input.json",
                         "manual-assessment-result.json"):
            doc = json.loads((E / filename).read_text())
            documents[doc["assessment_result"]["execution_id"]] = doc
        return documents

    def test_org_input_cross_layer_consumption_is_consistent(self):
        document = json.loads((E / "benchmark-result-organizational-input.json").read_text())
        results = self.complete_organizational_execution_results()
        self.assertEqual(validate_organizational_consumption_links(document, results), [])

    def test_missing_or_extra_rule_input_is_not_silently_accepted(self):
        document = json.loads((E / "benchmark-result-organizational-input.json").read_text())
        results = self.complete_organizational_execution_results()
        rule = document["benchmark_result"]["rule_results"][0]
        rule.pop("organizational_inputs")
        self.assertIn("rule.missing_consumed_organizational_input",
                      {row["code"] for row in validate_organizational_consumption_links(
                          document, results)})
        rule["organizational_inputs"] = [{
            "parameter": "site_approved_file_owner_uid",
            "organizational_input_ref": "org-file-owner",
            "value": 0,
            "redacted": False
        }]
        results["example-file-owner-1"]["assessment_result"]["consumed_organizational_inputs"] = []
        self.assertIn("rule.unconsumed_organizational_input",
                      {row["code"] for row in validate_organizational_consumption_links(
                          document, results)})

    def test_unmaterialized_input_does_not_invent_rule_expected_value(self):
        document = json.loads((E / "benchmark-result-organizational-input.json").read_text())
        results = self.complete_organizational_execution_results()
        rule = document["benchmark_result"]["rule_results"][0]
        assessment = results["example-file-owner-1"]["assessment_result"]
        binding = assessment["consumed_organizational_inputs"][0]
        binding["materialized"] = False
        binding.pop("value")
        assessment["outcome"] = "not_evaluated"
        rule["outcome"] = "not_evaluated"
        rule["organizational_inputs"] = []
        self.assertEqual(validate_organizational_consumption_links(document, results), [])
        binding["value"] = 0
        self.assertIn("assessment.unmaterialized_input_value",
                      {entry["code"] for entry in validate_organizational_consumption_links(
                          document, results)})

    def test_missing_assessment_result_is_not_certified_as_complete(self):
        document = json.loads((E / "benchmark-result-organizational-input.json").read_text())
        results = self.complete_organizational_execution_results()
        del results["example-file-owner-1"]
        self.assertIn("assessment.missing_execution_result",
                      {row["code"] for row in validate_organizational_consumption_links(
                          document, results)})

    def test_assessment_value_mismatch_and_canonical_redaction_are_detected(self):
        document = json.loads((E / "benchmark-result-organizational-input.json").read_text())
        results = self.complete_organizational_execution_results()
        consumed = results["example-file-owner-1"]["assessment_result"]["consumed_organizational_inputs"][0]
        consumed["value"] = 7
        self.assertIn("assessment.organizational_input_value_mismatch",
                      {row["code"] for row in validate_organizational_consumption_links(
                          document, results)})
        consumed["value"] = 0
        entry = document["benchmark_result"]["effective_policy"]["organizational_inputs"]["org-file-owner"]
        entry["redacted"] = True
        entry.pop("value")
        self.assertIn("assessment.redacted_registry_leak",
                      {row["code"] for row in validate_organizational_consumption_links(
                          document, results)})

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
