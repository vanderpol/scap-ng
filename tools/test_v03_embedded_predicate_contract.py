#!/usr/bin/env python3
"""#208 — typed inline Test/Filter schema and locality conformance."""
import copy
import unittest
from pathlib import Path

from validate_native_json_schemas import build_validators, document_errors


ROOT = Path(__file__).resolve().parents[1]
V03 = ROOT / "schema" / "v0.3.0"


def predicate(value=0, field="owner_uid", datatype="integer"):
    return {"field": field, "value": value, "operation": "equals",
            "datatype": datatype, "match": "all", "existence": "one_or_more"}


def valid():
    return {"assessment": {
        "id": "file-owner.automated", "version": 1,
        "assessment_title": "Owner check", "mode": "automated",
        "class": "compliance", "purpose": "assessment",
        "specification": {"id": "scap-ng.pre-alpha.assessment", "version": "0.3.0"},
        "shared_objects": {
            "source-file-object": {
                "object_title": "Source", "capability": "unix.file",
                "select": {
                    "full_path": {"value": "/etc/example.conf", "operation": "equals", "datatype": "string"}
                },
                "filesystem": "all",
            },
            "filtered-files-object": {
                "object_title": "Filtered", "capability": "unix.file",
                "set": {
                    "operator": "union",
                    "operands": [{
                        "object": "source-file-object",
                        "filters": [{"action": "exclude", **predicate()}],
                    }],
                },
            },
        },
        "tests": {
            "file-owner-test": {
                "test_title": "Owner must be root",
                "reported_elements": "all",
                "capability": "unix.file",
                "object": "filtered-files-object",
                "existence": "none",
                "match": "all",
                "states": [predicate()],
            },
        },
        "evaluate": {"test": "file-owner-test"},
    }}


class EmbeddedPredicateContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.v = build_validators(V03)["assessment.schema.json"]

    def errors(self, doc):
        return list(document_errors(self.v, doc))

    def test_valid_typed_comparisons_for_test_and_filter(self):
        self.assertEqual(self.errors(valid()), [])

    def test_no_legacy_state_registry(self):
        doc = valid()
        doc["assessment"]["states"] = {"owner-state": {"capability": "unix.file", "state": predicate()}}
        self.assertTrue(self.errors(doc))

    def test_no_state_references_or_wrappers(self):
        for entry in ("owner-state", {"capability": "unix.file", "state": predicate()},
                      {"state_title": "Owner", **predicate()}):
            with self.subTest(entry=entry):
                doc = valid()
                doc["assessment"]["tests"]["file-owner-test"]["states"] = [entry]
                self.assertTrue(self.errors(doc))

    def test_filter_is_not_a_legacy_state(self):
        for new_filter in (
            {"action": "exclude", "state": predicate()},
            {"action": "exclude", "capability": "unix.file", **predicate()},
            {"action": "exclude", "filter_title": "Root", **predicate()},
            {"action": "exclude", "field": "owner_uid", "value": 0},
        ):
            with self.subTest(filter=new_filter):
                doc = valid()
                doc["assessment"]["shared_objects"]["filtered-files-object"]["set"]["operands"][0]["filters"] = [new_filter]
                self.assertTrue(self.errors(doc))

    def test_generated_capability_field_and_datatype_enforced_for_filter(self):
        for invalid in (predicate(field="never-an-item-field"),
                        predicate(value="not an integer"),
                        predicate(datatype="boolean", value=True)):
            with self.subTest(invalid=invalid):
                doc = valid()
                doc["assessment"]["shared_objects"]["filtered-files-object"]["set"]["operands"][0]["filters"][0] = {
                    "action": "exclude", **invalid}
                self.assertTrue(self.errors(doc))

    def test_generated_capability_field_and_datatype_enforced_for_test(self):
        for invalid in (predicate(field="never-an-item-field"), predicate(value="a word")):
            with self.subTest(invalid=invalid):
                doc = valid()
                doc["assessment"]["tests"]["file-owner-test"]["states"] = [invalid]
                self.assertTrue(self.errors(doc))

    def test_nested_boolean_predicates_preserved(self):
        doc = valid()
        doc["assessment"]["tests"]["file-owner-test"]["states"] = [
            {"any": [predicate(), predicate(value=1000)]}
        ]
        self.assertEqual(self.errors(doc), [])

    def test_filter_action_explicit(self):
        for flt in (predicate(), {"action": "reject", **predicate()}):
            doc = valid()
            doc["assessment"]["shared_objects"]["filtered-files-object"]["set"]["operands"][0]["filters"] = [flt]
            self.assertTrue(self.errors(doc))


if __name__ == "__main__":
    unittest.main()
