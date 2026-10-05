#!/usr/bin/env python3
"""Synthetic checks for SCAP-NG explicit defaults."""
import json
from pathlib import Path
import unittest
from audit_v003_explicit_defaults import audit_doc

ROOT = Path(__file__).resolve().parents[1]

def default_keyword_paths(value, path="$"):
    hits = []
    if isinstance(value, dict):
        for key, child in value.items():
            here = f"{path}.{key}"
            if key == "default":
                hits.append(here)
            hits.extend(default_keyword_paths(child, here))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            hits.extend(default_keyword_paths(child, f"{path}[{index}]"))
    return hits

class ExplicitDefaultsTests(unittest.TestCase):
    def fixture(self):
        obj = {"value": {"variable": "v"}, "variable_check": "all",
               "operation": "equals", "datatype": "string"}
        state = dict(obj, field="filename", entity_check="all",
                     entity_existence="at_least_one_exists")
        return {"assessment": {"mode": "automated",
                "checks": {"x": {
                    "collect": {"select": {"filename": obj}},
                    "assert": {"existence": "at_least_one_exists",
                               "check": "all", "state": state}}},
                "variables": {"v": {"datatype": "string", "kind": "constant",
                                    "expression": {"literal": "value"}}}}}
    def test_complete(self):
        issues, totals = audit_doc(self.fixture())
        self.assertFalse(issues, issues)
        self.assertEqual(totals["variable_references"], 2)
    def test_missing_check_detected(self):
        doc = self.fixture()
        del doc["assessment"]["checks"]["x"]["collect"]["select"]["filename"]["variable_check"]
        issues, _ = audit_doc(doc)
        self.assertIn("HIDDEN_VARIABLE_CHECK", [r["code"] for r in issues])
    def test_missing_state_existence_detected(self):
        doc = self.fixture()
        del doc["assessment"]["checks"]["x"]["assert"]["state"]["entity_existence"]
        issues, _ = audit_doc(doc)
        self.assertIn("HIDDEN_STATE_DEFAULT_ENTITY_EXISTENCE",
                      [r["code"] for r in issues])
    def test_independent_variable_object_selector_is_not_var_check(self):
        doc = self.fixture()
        check = doc["assessment"]["checks"]["x"]
        check["collect"]["capability"] = "independent.variable"
        check["collect"]["select"] = {"var_ref": {
            "operation": "equals", "datatype": "string", "mask": False,
            "value": {"variable": "v"}}}
        issues, counts = audit_doc(doc)
        self.assertFalse(issues, issues)
        self.assertEqual(counts["independent_variable_id_selectors"], 1)

    def test_missing_reported_elements_detected(self):
        doc = self.fixture()
        doc["assessment"]["specification"] = {
            "id": "scap-ng.pre-alpha.assessment",
            "version": "0.2.0",
        }
        doc["assessment"]["tests"] = {
            "test-x": {
                "test_title": "x",
                "capability": "unix.file",
            }
        }
        issues, _ = audit_doc(doc)
        self.assertIn("HIDDEN_TEST_DEFAULT_REPORTED_ELEMENTS",
                      [r["code"] for r in issues])
        doc["assessment"]["tests"]["test-x"]["reported_elements"] = "all"
        issues, _ = audit_doc(doc)
        self.assertNotIn("HIDDEN_TEST_DEFAULT_REPORTED_ELEMENTS",
                         [r["code"] for r in issues])


    def test_v020_schemas_have_no_json_schema_defaults(self):
        hits = []
        for path in sorted((ROOT / "schema/v0.2.0").rglob("*.json")):
            doc = json.loads(path.read_text(encoding="utf-8"))
            for where in default_keyword_paths(doc):
                hits.append(f"{path.relative_to(ROOT)}:{where}")
        self.assertEqual([], hits)

    def test_v020_schema_requires_semantically_meaningful_choices(self):
        assessment = json.loads((ROOT / "schema/v0.2.0/assessment.schema.json").read_text())
        test_schema = assessment["properties"]["assessment"]["properties"]["tests"]["additionalProperties"]
        self.assertIn("reported_elements", test_schema["required"])

        result_types = json.loads((ROOT / "schema/v0.2.0/result-types.schema.json").read_text())
        self.assertIn("status", result_types["$defs"]["typed_value"]["required"])

        assessment_result = json.loads((ROOT / "schema/v0.2.0/assessment-result.schema.json").read_text())
        ar = assessment_result["properties"]["assessment_result"]["properties"]
        self.assertIn("relationship", ar["field_uses"]["items"]["required"])
        dependency = ar["dependent_assessments"]["items"]
        self.assertIn("purpose", dependency["required"])
        self.assertIn("reused", dependency["required"])

        test_result = json.loads((ROOT / "schema/v0.2.0/test-result.schema.json").read_text())
        self.assertIn("state_refs", test_result["required"])
        self.assertIn("per_item_results", test_result["required"])

        variable_result = json.loads((ROOT / "schema/v0.2.0/variable-result.schema.json").read_text())
        self.assertIn("item_refs", variable_result["required"])

    def test_record_fields(self):
        doc = self.fixture()
        record = {"name": "key", "value": "value", "operation": "equals",
                  "datatype": "string", "entity_check": "all"}
        doc["assessment"]["checks"]["x"]["collect"]["select"]["record"] = {
            "operation": "equals", "datatype": "record", "mask": False,
            "value": {"record": [record]}}
        issues, totals = audit_doc(doc)
        self.assertFalse(issues, issues)
        self.assertEqual(totals["record_fields"], 1)
        del record["entity_check"]
        issues, _ = audit_doc(doc)
        self.assertIn("HIDDEN_RECORD_FIELD_ENTITY_CHECK",
                      [r["code"] for r in issues])

if __name__ == "__main__":
    unittest.main()
