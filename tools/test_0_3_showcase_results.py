#!/usr/bin/env python3
"""Validate checked-in SCAP-NG 0.3 showcase result examples."""

from __future__ import annotations

import copy
import json
import re
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, RefResolver
import yaml


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schema" / "v0.3.0"
EXAMPLE_DIR = ROOT / "specification" / "examples" / "0.3.0" / "results"

CASES = {
    "scan-result.json": "scan-result.schema.json",
    "benchmark-result.json": "benchmark-result.schema.json",
    "benchmark-result-organizational-input.json": "benchmark-result.schema.json",
    "assessment-result-organizational-input.json": "assessment-result.schema.json",
    "benchmark-result-organizational-input.json": "benchmark-result.schema.json",
    "assessment-result-organizational-input.json": "assessment-result.schema.json",
    "assessment-result.json": "assessment-result.schema.json",
    "assessment-result-pass-omitted.json": "assessment-result.schema.json",
    "assessment-result-pass-witness.json": "assessment-result.schema.json",
    "assessment-result-multi-file.json": "assessment-result.schema.json",
    "assessment-result-diagnostic-override.json": "assessment-result.schema.json",
    "assessment-result-bounded-evidence.json": "assessment-result.schema.json",
    "manual-assessment-result.json": "assessment-result.schema.json",
}


def schema_store():
    store = {}
    for path in SCHEMA_DIR.glob("*.schema.json"):
        document = json.loads(path.read_text(encoding="utf-8"))
        if "$id" in document:
            store[document["$id"]] = document
    return store


class ShowcaseResultExamplesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.store = schema_store()

    def test_all_showcase_results_validate_against_0_3(self):
        for example_name, schema_name in CASES.items():
            with self.subTest(example=example_name):
                schema = json.loads(
                    (SCHEMA_DIR / schema_name).read_text(encoding="utf-8")
                )
                Draft202012Validator.check_schema(schema)
                validator = Draft202012Validator(
                    schema,
                    resolver=RefResolver.from_schema(schema, store=self.store),
                )
                document = json.loads(
                    (EXAMPLE_DIR / example_name).read_text(encoding="utf-8")
                )
                errors = sorted(
                    validator.iter_errors(document),
                    key=lambda error: tuple(map(str, error.absolute_path)),
                )
                if errors:
                    details = "\n".join(
                        f"{'/'.join(map(str, error.absolute_path))}: {error.message}"
                        for error in errors
                    )
                    self.fail(f"{example_name} failed {schema_name}:\n{details}")


    def test_benchmark_embeds_typed_rule_finding_without_execution_graph(self):
        schema = json.loads((SCHEMA_DIR / "benchmark-result.schema.json").read_text())
        validator = Draft202012Validator(schema, resolver=RefResolver.from_schema(schema, store=self.store))
        doc = json.loads((EXAMPLE_DIR / "benchmark-result.json").read_text())
        rules = doc["benchmark_result"]["rule_results"]
        self.assertEqual(len(rules), 2)
        finding = rules[0]["findings"][0]
        self.assertEqual(finding["observed"]["value"], 1001)
        self.assertEqual(finding["expected"]["value"], 0)
        self.assertEqual(finding["subject"]["identifier"], "/etc/example.conf")
        self.assertEqual(finding["instance_id"], rules[0]["instances"][0]["id"])
        self.assertEqual(rules[1]["findings"], [], "Manual decisions do not invent Items")
        for field in ("tests", "items", "observed_state", "expected_state"):
            self.assertNotIn(field, rules[0])
        missing = copy.deepcopy(doc)
        del missing["benchmark_result"]["rule_results"][0]["findings"]
        self.assertTrue(list(validator.iter_errors(missing)))
        fabricated = copy.deepcopy(doc)
        fabricated["benchmark_result"]["rule_results"][0]["findings"][0]["item"] = {"id": "bogus"}
        self.assertTrue(list(validator.iter_errors(fabricated)))
        redacted_leak = copy.deepcopy(doc)
        redacted_leak["benchmark_result"]["rule_results"][0]["findings"][0]["observed"]["redacted"] = True
        self.assertTrue(list(validator.iter_errors(redacted_leak)))

    def test_assessment_intro_contains_real_inline_rule_and_local_object(self):
        example_page = (ROOT / "specification" / "examples" / "assessments.md").read_text(
            encoding="utf-8"
        )
        main_page = (ROOT / "specification" / "examples" / "README.md").read_text(
            encoding="utf-8"
        )
        intro = example_page.split("## The alternative: a manual Assessment", 1)[0]
        blocks = re.findall(r"```yaml\n([\s\S]*?)\n```", intro)
        self.assertEqual(len(blocks), 2, "Start with Rule linkage and the real Assessment YAML")
        rule = yaml.safe_load(blocks[0])["rule"]
        assessment = yaml.safe_load(blocks[1])
        self.assertEqual(rule["id"], "SV-257851")
        choices = rule["assessment_choices"]
        self.assertIn("automated", choices)
        self.assertIn("manual", choices)
        self.assertEqual(choices["default"], choices["automated"])
        self.assertEqual(
            choices["automated"]["assessment"],
            "home-is-mounted-with-the-nosuid-option",
        )
        self.assertEqual(choices["manual"]["assessment"], "SV-257851.manual")
        for selection in choices.values():
            reference = selection["assessment"]
            self.assertNotIn("/", reference, "Authors use IDs, not file paths")
            self.assertNotIn("\\", reference, "Authors use IDs, not file paths")
            self.assertFalse(reference.endswith(".yaml"))
        self.assertIn("compiler now resolves these logical IDs", intro)
        test = assessment["tests"]["home-mounted-nosuid-option-test"]
        self.assertEqual(test["object"]["capability"], "linux.partition")
        self.assertIn("mount_point", test["object"]["select"])
        self.assertEqual(test["states"][0]["state"]["field"], "mount_options")
        self.assertEqual(test["states"][0]["state"]["value"], "nosuid")
        self.assertEqual(assessment["evaluate"]["test"], "home-mounted-nosuid-option-test")
        self.assertIn("assessments.md#start-here-the-rule-and-its-automated-assessment", main_page)

    def test_applicability_example_uses_logical_assessment_id(self):
        example_page = (
            ROOT / "specification" / "examples" / "assessments.md"
        ).read_text(encoding="utf-8")
        applicability = example_page.split(
            "## Applicability: first check whether a rule applies", 1
        )[1].split("## Practical authoring improvements", 1)[0]
        blocks = re.findall(r"```yaml\n([\s\S]*?)\n```", applicability)
        self.assertEqual(len(blocks), 1)
        entry = yaml.safe_load(blocks[0])["applicability"]
        ref = next(iter(entry["conditions"].values()))["assessment"]
        self.assertEqual(ref, "condition.gnome-shell-package")
        self.assertNotIn("/", ref)
        self.assertFalse(ref.endswith(".yaml"))

    def test_assessment_page_reads_simple_to_advanced(self):
        page = (ROOT / "specification" / "examples" / "assessments.md").read_text(
            encoding="utf-8"
        )
        headings = [
            "## Start here: the Rule and its automated Assessment",
            "## The alternative: a manual Assessment",
            "## After scanning: Assessment Results that explain why",
            "## Applicability: first check whether a rule applies",
            "## Practical authoring improvements",
            "## Advanced or not-yet-automated features",
            "## Evidence and further reading (optional)",
        ]
        positions = [page.index(heading) for heading in headings]
        self.assertEqual(positions, sorted(positions))
        self.assertEqual(page.count("### Organizational Input"), 1)
        self.assertNotIn('"maximum": 20', page, "Example must match current cap")
        self.assertNotIn('"stop_reason": "evidence_maximum_reached"', page)
        self.assertNotIn("## Additional authoring details", page)

    def test_inline_collected_items_and_comparisons(self):
        for name in (
            "assessment-result.json",
            "assessment-result-multi-file.json",
            "assessment-result-bounded-evidence.json",
            "assessment-result-diagnostic-override.json",
        ):
            with self.subTest(name=name):
                result = json.loads((EXAMPLE_DIR / name).read_text())["assessment_result"]
                self.assertNotIn("items", result, "Test evidence should be inline, not duplicated")
                policy = result["evidence_retention"]
                self.assertEqual(policy["scope"], "per_test")
                self.assertIn(policy["source"], ("scanner_configuration", "operator_override"))
                for test in result["tests"]:
                    details = test["per_item_results"]
                    self.assertEqual(test["item_summary"]["returned_items"], len(details))
                    maximum = policy["maximum_items"]
                    if maximum is not None:
                        self.assertLessEqual(len(details), maximum)
                    self.assertGreaterEqual(test["item_summary"]["evaluated_items"], len(details))
                    self.assertGreaterEqual(
                        test["item_summary"]["observed_mismatches"],
                        sum(detail["outcome"] == "false" for detail in details),
                    )
                    for detail in details:
                        self.assertEqual(detail["item_ref"], detail["item"]["id"])
                        self.assertEqual(detail["item"]["status"], "exists")
                        item_fields = detail["item"]["fields"]
                        self.assertIn("full_path", item_fields)
                        self.assertIn("owner_uid", item_fields)
                        for state in detail["state_results"]:
                            for entity in state["entity_results"]:
                                if entity["entity"] == "owner_uid":
                                    value = item_fields["owner_uid"]["value"]
                                    self.assertEqual(entity["item_values"][0]["value"], value)
                                    for comparison in entity["comparison_results"]:
                                        self.assertEqual(comparison["item_value"]["value"], value)
                                        self.assertEqual(comparison["expected_value"]["value"], 0)

    def test_two_tests_can_interpret_the_same_observed_file_differently(self):
        result = json.loads(
            (EXAMPLE_DIR / "assessment-result-multi-file.json").read_text()
        )["assessment_result"]
        self.assertEqual(len(result["tests"]), 2)
        owner, mode = result["tests"]
        owner_item = next(
            row["item"] for row in owner["per_item_results"]
            if row["item_ref"] == "config-agent-file"
        )
        mode_item = mode["per_item_results"][0]["item"]
        self.assertEqual(owner_item, mode_item, "Repeated observation must not diverge")
        owner_cmp = next(
            row for row in owner["per_item_results"]
            if row["item_ref"] == "config-agent-file"
        )["state_results"][0]["entity_results"][0]["comparison_results"][0]
        mode_cmp = mode["per_item_results"][0]["state_results"][0]["entity_results"][0]["comparison_results"][0]
        self.assertEqual((owner_cmp["item_value"]["value"], owner_cmp["expected_value"]["value"]), (1001, 0))
        self.assertEqual((mode_cmp["item_value"]["value"], mode_cmp["expected_value"]["value"]), ("0644", "0600"))
        self.assertEqual(result["evidence_summary"]["observed_failures"], 2)

    def test_debug_override_changes_retention_not_assessment(self):
        normal = json.loads((EXAMPLE_DIR / "assessment-result-bounded-evidence.json").read_text())["assessment_result"]
        debug = json.loads((EXAMPLE_DIR / "assessment-result-diagnostic-override.json").read_text())["assessment_result"]
        self.assertEqual(normal["assessment"], debug["assessment"])
        self.assertEqual(normal["outcome"], debug["outcome"])
        self.assertEqual(normal["tests"][0]["id"], debug["tests"][0]["id"])
        self.assertEqual(normal["tests"][0]["item_summary"]["observed_mismatches"],
                         debug["tests"][0]["item_summary"]["observed_mismatches"])
        self.assertLess(normal["evidence_retention"]["maximum_items"],
                        debug["evidence_retention"]["maximum_items"])
        self.assertLess(len(normal["tests"][0]["per_item_results"]),
                        len(debug["tests"][0]["per_item_results"]))
        self.assertEqual(debug["evidence_retention"]["source"], "operator_override")
        self.assertTrue(debug["evidence_retention"]["override_reason"])

    def test_evidence_schema_rejects_missing_item_and_override_reason(self):
        schema = json.loads((SCHEMA_DIR / "assessment-result.schema.json").read_text())
        validator = Draft202012Validator(schema, resolver=RefResolver.from_schema(schema, store=self.store))
        valid = json.loads((EXAMPLE_DIR / "assessment-result.json").read_text())
        without_item = copy.deepcopy(valid)
        del without_item["assessment_result"]["tests"][0]["per_item_results"][0]["item"]
        self.assertTrue(list(validator.iter_errors(without_item)))
        without_summary = copy.deepcopy(valid)
        del without_summary["assessment_result"]["tests"][0]["item_summary"]
        self.assertTrue(list(validator.iter_errors(without_summary)))
        without_policy = copy.deepcopy(valid)
        del without_policy["assessment_result"]["evidence_retention"]
        self.assertTrue(list(validator.iter_errors(without_policy)))
        without_reason = copy.deepcopy(valid)
        without_reason["assessment_result"]["evidence_retention"]["source"] = "operator_override"
        self.assertTrue(list(validator.iter_errors(without_reason)))
        with_leak = copy.deepcopy(valid)
        value = with_leak["assessment_result"]["tests"][0]["per_item_results"][0]["item"]["fields"]["owner_uid"]
        value["redacted"] = True
        self.assertTrue(list(validator.iter_errors(with_leak)))


if __name__ == "__main__":
    unittest.main()
