#!/usr/bin/env python3
"""Synthetic checks for SCAP-NG explicit defaults."""
import unittest
from audit_v003_explicit_defaults import audit_doc

class ExplicitDefaultsTests(unittest.TestCase):
    def fixture(self):
        obj = {"value": {"variable": "v"}, "variable_check": "all",
               "operation": "equals", "datatype": "string", "mask": False}
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
    def test_record_fields(self):
        doc = self.fixture()
        record = {"name": "key", "value": "value", "operation": "equals",
                  "datatype": "string", "mask": False, "entity_check": "all"}
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
