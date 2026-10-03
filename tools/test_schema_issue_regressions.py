"""Evidence/Audit regressions for issues #118–#121; no runtime equivalence claim."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import yaml
from jsonschema import Draft202012Validator

from validate_native_json_schemas import build_validators, classify, document_errors

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schema/v0.1.0"


def schema(name):
    return json.loads((SCHEMAS / name).read_text())


def manual():
    return {"assessment": {
        "id": "example.manual", "version": 1, "assessment_title": "Inspect",
        "mode": "manual", "class": "compliance", "purpose": "assessment",
        "procedure": "Inspect the setting.",
        "response": {"type": "yes_no", "allow_comment": True, "allow_evidence": True,
                     "choices": [{"value": "yes", "outcome": "true"},
                                 {"value": "no", "outcome": "false"}]},
    }}


class SchemaIssueRegressions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validators = build_validators(SCHEMAS)

    def errors(self, doc, name="assessment.schema.json"):
        return list(document_errors(self.validators[name], doc))

    def test_manual_contract_identical_in_generic_and_manual_schemas(self):
        for version in (1, "publisher-revision"):
            doc = manual()
            doc["assessment"]["version"] = version
            for name in ("assessment.schema.json", "manual-assessment.schema.json"):
                self.assertEqual(self.errors(doc, name), [])
                missing = copy.deepcopy(doc)
                del missing["assessment"]["response"]
                self.assertTrue(self.errors(missing, name))

    def test_all_assessment_filenames_use_same_schema(self):
        for name in ("a.manual.assessment.yaml", "a.document-review.assessment.yaml",
                     "a.assessment.yaml", "assessments/manual/arbitrary.yaml"):
            self.assertEqual(classify(Path(name)), ("assessment", "assessment.schema.json"))

    def test_invalid_modes_and_cross_mode_fields(self):
        for mode in (None, "unexpected"):
            doc = manual()
            doc["assessment"]["mode"] = mode
            self.assertTrue(self.errors(doc))
        missing = manual()
        del missing["assessment"]["mode"]
        self.assertTrue(self.errors(missing))
        doc = manual()
        doc["assessment"]["tests"] = {}
        self.assertTrue(self.errors(doc))
        automated = {"assessment": {
            "id": "example.automated", "version": 1, "assessment_title": "Check",
            "mode": "automated", "class": "compliance", "purpose": "assessment",
            "specification": {"id": "example", "version": "0.1.0"},
            "tests": {"t": {"test_title": "Check", "capability": "variable.value"}},
            "evaluate": {"test": "t"},
        }}
        self.assertEqual(self.errors(automated), [])
        for key in ("procedure", "response", "references", "evidence_guidance"):
            doc = copy.deepcopy(automated)
            doc["assessment"][key] = manual()["assessment"].get(key, [])
            self.assertTrue(self.errors(doc))
        automated["assessment"]["version"] = "1"
        self.assertTrue(self.errors(automated))

    def test_duplicate_values_rejected_including_identical_choices(self):
        for outcome in ("true", "false"):
            doc = manual()
            doc["assessment"]["response"]["choices"].append({"value": "yes", "outcome": outcome})
            errors = self.errors(doc)
            self.assertEqual(len(errors), 1)
            self.assertEqual(errors[0].validator, "unique_response_value")
            self.assertEqual(list(errors[0].absolute_path), ["assessment", "response", "choices", 2, "value"])
        doc = manual()
        doc["assessment"]["response"]["choices"][1]["outcome"] = "true"
        self.assertEqual(self.errors(doc), [])

    def test_invalid_choice_shapes_report_errors_without_crashing(self):
        for choices in ([None], [{"value": []}], ["yes"], "yes"):
            doc = manual()
            doc["assessment"]["response"]["choices"] = choices
            self.assertTrue(self.errors(doc))

    def test_cli_enforces_mode_and_semantic_uniqueness(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ("a.manual.assessment.yaml", "b.assessment.yaml"):
                doc = manual()
                doc["assessment"]["response"]["choices"].append({"value": "yes", "outcome": "false"})
                (root / name).write_text(yaml.safe_dump(doc))
            report = root / "report.json"
            result = subprocess.run([sys.executable, str(ROOT / "tools/validate_native_json_schemas.py"),
                                     str(root), "--schema-dir", str(SCHEMAS), "--report", str(report)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 1, result.stderr)
            data = json.loads(report.read_text())
            self.assertEqual(data["invalid"], 2)
            for row in data["results"]:
                self.assertEqual(row["errors"][0]["classification"], "semantic")
                self.assertEqual(row["errors"][0]["validator"], "unique_response_value")

    def test_redacted_value_prohibited_for_all_input_record_families(self):
        props = schema("assessment-result.schema.json")["properties"]["assessment_result"]["properties"]
        registry = schema("benchmark-result.schema.json")["properties"]["benchmark_result"]["properties"]["effective_policy"]["properties"]["organizational_inputs"]["additionalProperties"]
        cases = [
            (props["input_bindings"]["items"], {"input": "password", "source": "organizational_input"}),
            (props["consumed_organizational_inputs"]["items"], {"input": "password", "organizational_input_ref": "example", "materialized": True}),
            (registry, {"parameter": "password", "source": "organizational_input", "provenance": {}}),
        ]
        for contract, entry in cases:
            v = Draft202012Validator(contract)
            self.assertTrue(v.is_valid({**entry, "redacted": True}))
            for value in (None, "EXAMPLE_VALUE", [], {}):
                self.assertFalse(v.is_valid({**entry, "redacted": True, "value": value}))
                self.assertTrue(v.is_valid({**entry, "redacted": False, "value": value}))
                self.assertTrue(v.is_valid({**entry, "value": value}))
        self.assertFalse(Draft202012Validator(registry).is_valid(cases[-1][1]))

    def test_publisher_profiles_subtractive_and_closed(self):
        contract = schema("benchmark.schema.json")["properties"]["benchmark"]["properties"]["profiles"]
        v = Draft202012Validator(contract)
        for profile in ({"id": "base", "disabled_rules": []},
                        {"id": "child", "extends": "base", "disabled_rules": ["R1"],
                         "title": None, "description": None, "parameters": {"x": 1}}):
            self.assertTrue(v.is_valid([profile]))
        for profile in ({"id": "bad", "enabled_rules": ["R1"]},
                        {"id": "bad", "disabled_rules": [], "enabled_rules": []},
                        {"id": "bad"}, {"id": "bad", "disabled_rules": [""]},
                        {"id": "bad", "disabled_rules": ["R1", "R1"]}):
            self.assertFalse(v.is_valid([profile]))
        tailoring = schema("tailoring.schema.json")["properties"]["tailoring"]["properties"]["enabled_rules"]
        self.assertTrue(Draft202012Validator(tailoring).is_valid(["R1"]))


if __name__ == "__main__":
    unittest.main()
