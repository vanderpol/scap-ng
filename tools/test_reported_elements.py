#!/usr/bin/env python3
import copy
import json
from pathlib import Path
import tempfile
import unittest

import yaml
from jsonschema import Draft202012Validator, ValidationError
from referencing import Registry, Resource
from assessment_expression import AssessmentExpressionEvaluator, ContentError
from reported_elements import (ROOT, CONTROL, capability_fields, validate_control, source_errors,
                               generate_reporting_capability, project_items)
from generate_capability_schema import generate
from validate_native_json_schemas import build_validators, document_errors, schema_store, validator
from scap_ng_content_compiler import compile_benchmark

SUITE = ROOT / "tests/reported-elements-0.2.0"


class ReportedElementsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.assessment = yaml.safe_load((SUITE / "ownership.assessment.yaml").read_text())["assessment"]
        cls.fixture = json.loads((SUITE / "cases.json").read_text())
        cls.expected = json.loads((SUITE / "expected-results/field-selections.json").read_text())
        cls.validators = build_validators(ROOT / "schema/v0.2.0")
        cls.report_validator = validator(ROOT / "schema/v0.2.0", "item-report.schema.json", schema_store(ROOT / "schema/v0.2.0"))

    def report(self, assessment=None, items=None, uses=None, completeness=None):
        return project_items(assessment or self.assessment,
            copy.deepcopy(self.fixture["items"]) if items is None else items,
            copy.deepcopy(self.fixture["uses"]) if uses is None else uses,
            source_execution_ref=self.fixture["source_execution_ref"],
            source_completeness=completeness or self.fixture["source_completeness"])["item_report"]

    def test_committed_known_result_cases(self):
        for case in self.fixture["cases"]:
            assessment = copy.deepcopy(self.assessment)
            assessment["tests"]["test-owner"].pop("reported_elements")
            if "control" in case:
                assessment["tests"]["test-owner"]["reported_elements"] = case["control"]
            report = self.report(assessment)
            with self.subTest(case=case["id"]):
                self.report_validator.validate({"item_report": report})
                expected = self.expected[case["id"]]
                self.assertEqual(sorted(report["items"][0]["item"]["fields"]), expected["fields"])
                self.assertEqual(report["items"][0]["selection"]["unavailable_elements"], expected["unavailable_elements"])

    def test_control_grammar_and_unknown_names(self):
        for control in ["all", "compared", [], ["owner_uid", "owner_user_name"]]:
            validate_control(control, "unix.file")
        for control in [None, True, "mask", {}, [""], ["  "], ["owner_uid", "owner_uid"], ["typo"]]:
            with self.subTest(control=control), self.assertRaises((ValueError, ValidationError)):
                validate_control(control, "unix.file")

    def test_all_capability_overlays_only_change_test_reporting(self):
        count = 0
        for path in (ROOT / "schema/v0.1.0/capability-mappings").glob("*.json"):
            mapping = json.loads(path.read_text())
            if "capability" not in mapping:
                continue
            old, new = generate(mapping, ROOT, schema_version="0.2.0"), generate_reporting_capability(mapping)
            Draft202012Validator.check_schema(new)
            for key in ["object", "state", "collected_item"]:
                self.assertEqual(new["$defs"].get(key), old["$defs"].get(key))
            self.assertIn("reported_elements", new["$defs"]["test"]["properties"])
            count += 1
        self.assertEqual(count, 100)

    def test_closed_generated_test_schema_accepts_control(self):
        mapping = json.loads((ROOT / "schema/v0.1.0/capability-mappings/unix.file.json").read_text())
        schema = generate_reporting_capability(mapping)
        common = json.loads((ROOT / "schema/v0.1.0/capability-common.schema.json").read_text())
        registry = Registry().with_resource(common["$id"], Resource.from_contents(common))
        test = self.assessment["tests"]["test-owner"]
        v = Draft202012Validator(schema["$defs"]["test"], registry=registry)
        v.validate(test)
        invalid = copy.deepcopy(test)
        invalid["reported_elements"] = ["typo"]
        with self.assertRaises(ValidationError):
            v.validate(invalid)

    def test_draft_assessment_control_is_test_only(self):
        self.assertFalse(list(document_errors(self.validators["assessment.schema.json"], {"assessment": self.assessment})))
        invalid = copy.deepcopy(self.assessment)
        invalid["reported_elements"] = "compared"
        self.assertTrue(list(document_errors(self.validators["assessment.schema.json"], {"assessment": invalid})))
        invalid = copy.deepcopy(self.assessment)
        invalid["tests"]["test-owner"]["reported_elements"] = {"elements": ["owner_uid"]}
        self.assertTrue(list(document_errors(self.validators["assessment.schema.json"], {"assessment": invalid})))

    def test_shared_item_union_and_all_dominance(self):
        assessment = copy.deepcopy(self.assessment)
        assessment["tests"]["test-second"] = copy.deepcopy(assessment["tests"]["test-owner"])
        uses = copy.deepcopy(self.fixture["uses"])
        uses.append({"test_ref": "test-second", "item_ref": "file-1", "used_elements": ["owner_gid"], "required_elements": []})
        assessment["tests"]["test-second"]["reported_elements"] = ["size"]
        fields = self.report(assessment, uses=uses)["items"][0]["item"]["fields"]
        self.assertEqual(set(fields), {"full_path", "owner_uid", "owner_user_name", "owner_gid", "size"})
        assessment["tests"]["test-second"].pop("reported_elements")
        self.assertEqual(set(self.report(assessment, uses=uses)["items"][0]["item"]["fields"]), set(self.fixture["items"][0]["fields"]))
        self.assertEqual(self.report(assessment, uses=list(reversed(uses))), self.report(assessment, uses=uses))

    def test_indirect_variable_and_filter_fields_are_retained(self):
        assessment = copy.deepcopy(self.assessment)
        assessment["tests"]["test-owner"]["reported_elements"] = "compared"
        uses = copy.deepcopy(self.fixture["uses"])
        # Recorder lineage includes ownership through a Variable and size through
        # a Filter; the projector must not infer only the final State field.
        uses[0]["used_elements"] = ["owner_uid", "size"]
        fields = self.report(assessment, uses=uses)["items"][0]["item"]["fields"]
        self.assertEqual(set(fields), {"full_path", "owner_uid", "size"})

    def test_indirect_variable_use_crosses_capability_boundary_explicitly(self):
        assessment = copy.deepcopy(self.assessment)
        assessment["tests"] = {"test-variable": {"test_title": "Derived ownership", "capability": "variable.value", "reported_elements": "compared"}}
        uses = [{"test_ref": "test-variable", "item_ref": "file-1", "used_elements": ["owner_uid"],
                 "required_elements": ["full_path"], "relationship": "variable"}]
        self.assertEqual(set(self.report(assessment, uses=uses)["items"][0]["item"]["fields"]), {"full_path", "owner_uid"})
        assessment["tests"]["test-variable"]["reported_elements"] = ["value"]
        item = self.report(assessment, uses=uses)["items"][0]
        self.assertEqual(item["selection"]["unavailable_elements"], [])
        self.assertEqual(set(item["item"]["fields"]), {"full_path", "owner_uid"})
        uses[0]["relationship"] = "direct"
        with self.assertRaisesRegex(ValueError, "capability mismatch"):
            self.report(assessment, uses=uses)

    def test_projection_preserves_import_origin_and_removes_dangling_metadata(self):
        items = copy.deepcopy(self.fixture["items"])
        items[0]["imported"] = True
        items[0]["context"]["origin"] = {"result_ref": "original-result", "item_ref": "original-item"}
        result = self.report(items=items)["items"][0]["item"]
        self.assertTrue(result["imported"])
        self.assertEqual(result["context"]["origin"], items[0]["context"]["origin"])
        self.assertNotIn("owner_group_name", result["context"]["name_resolution"])
        self.assertEqual(result["context"]["locators"], [])

    def test_redaction_is_independent_and_never_restored(self):
        items = copy.deepcopy(self.fixture["items"])
        items[0]["fields"]["owner_user_name"] = {"datatype": "string", "redacted": True}
        item = self.report(items=items)["items"][0]["item"]
        self.assertEqual(item["fields"]["owner_user_name"], {"datatype": "string", "redacted": True})
        # A pre-existing leak is rejected even when that field would be omitted.
        items[0]["fields"]["owner_group_name"] = {"datatype": "string", "redacted": True, "value": "leak"}
        with self.assertRaisesRegex(ValueError, "Redacted typed value"):
            self.report(items=items)

    def test_resolved_name_never_detaches_from_numeric_identity(self):
        for invalid_source in [None, {"datatype": "integer", "redacted": True}]:
            items = copy.deepcopy(self.fixture["items"])
            if invalid_source is None:
                del items[0]["fields"]["owner_uid"]
            else:
                items[0]["fields"]["owner_uid"] = invalid_source
            with self.assertRaises(ValueError):
                self.report(items=items)

    def test_runtime_rejects_bad_controls_before_any_test_callback(self):
        assessment = copy.deepcopy(self.assessment)
        assessment["tests"]["test-owner"]["reported_elements"] = ["typo"]
        with self.assertRaisesRegex(ContentError, "reported_elements"):
            AssessmentExpressionEvaluator({assessment["id"]: assessment})

    def test_authored_reporting_requires_explicit_version_opt_in(self):
        assessment = copy.deepcopy(self.assessment)
        assessment["specification"]["version"] = "0.1.0"
        self.assertTrue(source_errors(assessment))
        with self.assertRaisesRegex(ContentError, "0.2.0 specification"):
            AssessmentExpressionEvaluator({assessment["id"]: assessment})

    def test_unresolved_names_and_source_caps_are_honest(self):
        items = copy.deepcopy(self.fixture["items"])
        items[0]["fields"]["owner_user_name"] = {"datatype": "string", "status": "error"}
        completeness = {"logical_complete": True, "population_complete": False, "evidence_complete": False}
        report = self.report(items=items, completeness=completeness)
        self.assertEqual(report["source_completeness"], completeness)
        self.assertEqual(report["items"][0]["item"]["fields"]["owner_user_name"]["status"], "error")

    def test_selection_never_changes_numeric_truth_or_input_items(self):
        original = copy.deepcopy(self.fixture["items"])
        for control in ["all", "compared", [], ["owner_user_name"]]:
            assessment = copy.deepcopy(self.assessment)
            assessment["tests"]["test-owner"]["reported_elements"] = control
            def provider(identity, name, context):
                observed = original[0]["fields"]["owner_uid"]["value"]
                return "true" if observed == assessment["states"]["owner"]["state"]["value"] else "false"
            outcome = AssessmentExpressionEvaluator({assessment["id"]: assessment}).run(assessment["id"], provider)
            self.report(assessment, items=original)
            self.assertEqual(outcome["outcome"], "false")
            self.assertEqual(original, self.fixture["items"])

    def test_bad_lineage_is_rejected_and_unassociated_items_preserved(self):
        for change in ["unknown-test", "unknown-item", "missing-fields"]:
            uses = copy.deepcopy(self.fixture["uses"])
            if change == "unknown-test": uses[0]["test_ref"] = "missing"
            elif change == "unknown-item": uses[0]["item_ref"] = "missing"
            else: del uses[0]["used_elements"]
            with self.assertRaises(ValueError): self.report(uses=uses)
        self.assertEqual(self.report(uses=[])["items"][0]["item"]["fields"], self.fixture["items"][0]["fields"])

    def test_compiler_validates_controls_in_unselected_tests(self):
        assessment = copy.deepcopy(self.assessment)
        assessment["tests"]["test-unused"] = copy.deepcopy(assessment["tests"]["test-owner"])
        assessment["tests"]["test-unused"]["reported_elements"] = ["typo"]
        self.assertTrue(source_errors(assessment))
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            def dump(path, data):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(yaml.safe_dump(data, sort_keys=False))
            dump(root / "benchmark.yaml", {"benchmark": {"id": "reporting", "version": {"value": "1"}, "rules": ["R1"], "profiles": []}})
            dump(root / "assessments/owner.assessment.yaml", {"assessment": assessment})
            dump(root / "rules/R1.rule.yaml", {"rule": {"id": "R1", "assessment_choices": {"auto": {"assessment": "../assessments/owner.assessment.yaml"}}}})
            with self.assertRaisesRegex(ValueError, "invalid (reported_elements|0\\.2\\.0 Assessment)"):
                compile_benchmark(root, root)


if __name__ == "__main__":
    unittest.main()
