#!/usr/bin/env python3
"""#232/#239: reversible scoped A research input, typed population separation."""
from copy import deepcopy
import io
import json
from pathlib import Path
import sys
import unittest
from contextlib import redirect_stdout
from tempfile import TemporaryDirectory
from zipfile import ZipFile
sys.path.insert(0, str(Path(__file__).resolve().parent))

from research_04_scoped_state_require import compact
from v04_a_lower_scoped_to_base import lower_one, lower_all, main


SPEC = {"id": "scap-ng.pre-alpha.assessment", "version": "0.4.0"}
REQ = "at_least_one_exists_and_all_match"


def base():
    return {"assessment": {
        "id": "ng.synthetic.reversible",
        "mode": "automated",
        "specification": deepcopy(SPEC),
        "tests": {"test": {
            "require": REQ,
            "capability": "linux.partition",
            "states": [{"all": [
                {"a": {"equals": 1, "require": REQ}},
                {"b": {"equals": 2, "require": REQ}},
                {"c": {"equals": 3, "require": "none_exist"}},
            ]}],
        }},
        "evaluate": {"test": "test"},
    }}


def scoped(doc=None):
    s, _ = compact(deepcopy(doc or base()))
    for test in s["assessment"]["tests"].values():
        test["collected_items_require"] = test.pop("require")
    return s


class LowerScopedToBaseTests(unittest.TestCase):
    def test_exact_inverse(self):
        source = scoped()
        out = lower_one(source)
        self.assertEqual(out, base())
        self.assertEqual(source, scoped())  # original object unchanged
        self.assertNotIn("collected_items_require", out["assessment"]["tests"]["test"])

    def test_item_existence_does_not_inherit_into_state(self):
        before = scoped()
        after = lower_one(before)
        self.assertEqual(after["assessment"]["tests"]["test"]["require"], REQ)
        group = after["assessment"]["tests"]["test"]["states"][0]["all"]
        self.assertEqual(group[2]["c"]["require"], "none_exist")
        self.assertEqual(group[0]["a"]["require"], REQ)

    def test_records_kept_independent(self):
        doc = base()
        doc["assessment"]["tests"]["test"]["states"] = [
            {"value": {"record": {"require": "at_least_one_exists_and_all_match",
                                 "fields": {"name": {"equals": "x", "require": "none_exist"}}}}},
            {"first": {"equals": 1, "require": REQ}},
            {"second": {"equals": 2, "require": REQ}},
        ]
        self.assertEqual(lower_one(scoped(doc)), doc)

    def test_rejects_missing_explicit_field_requirement(self):
        invalid = scoped()
        test = invalid["assessment"]["tests"]["test"]
        test.pop("state_fields_require", None)
        for node in test["states"]:
            node.pop("state_fields_require", None)
        # Deliberately unscoped a child field.
        node = test["states"][0]
        # group is under and after compaction
        group = node.get("and", node.get("all"))
        group[0]["a"].pop("require", None)
        with self.assertRaises(ValueError):
            lower_one(invalid)

    def test_rejects_mixed_base_and_research_item_keys(self):
        invalid = scoped()
        invalid["assessment"]["tests"]["test"]["require"] = REQ
        with self.assertRaisesRegex(ValueError, "mixed or missing"):
            lower_one(invalid)

    def test_rejects_unapproved_spec_version(self):
        invalid = scoped()
        invalid["assessment"]["specification"]["version"] = "0.3.0"
        with self.assertRaisesRegex(ValueError, "requires declared pre-alpha"):
            lower_one(invalid)

    def test_rejects_noncanonical_shorthand(self):
        invalid = scoped()
        test = invalid["assessment"]["tests"]["test"]
        # Extra override identical to the inherited policy is invalid.
        if test.get("state_fields_require"):
            override = test["state_fields_require"]
            test["states"][0]["and"][0]["a"]["require"] = override
            with self.assertRaises(ValueError):
                lower_one(invalid)
        else:
            self.skipTest("optimizer selected local group scope, not Test scope")

    def test_nonautomated_documents_are_unchanged(self):
        source = scoped()
        documents = {
            "authoring/rhel_9/assessments/a.json": source,
            "authoring/rhel_9/assessments/m.json": {"assessment": {
                "id": "ng.synthetic.manual", "mode": "manual"}},
            "authoring/rhel_9/benchmark.json": {"benchmark": {
                "id": "ng.synthetic.rhel", "assessment_specifications": [SPEC]}},
            "authoring/rhel_9/rules/r.json": {"rule": {
                "id": "SV-TEST", "default_assessment_choice": "automated",
                "assessment_choices": {
                    "automated": {"assessment": "ng.synthetic.reversible"},
                    "manual": {"assessment": "ng.synthetic.manual"}},
            }},
        }
        before = deepcopy(documents)
        staged, report = lower_all(documents, validate_base=False)
        self.assertEqual(report["counters"]["lowered_automated_assessments"], 1)
        self.assertEqual(report["counters"]["lowered_tests"], 1)
        self.assertEqual(report["counters"]["untouched_documents"], 3)
        self.assertEqual(report["source_counts"], report["lowered_counts"])
        self.assertEqual(staged["authoring/rhel_9/assessments/a.json"], base())
        for path in documents:
            if path != "authoring/rhel_9/assessments/a.json":
                self.assertEqual(staged[path], documents[path])
        self.assertEqual(documents, before)

    def test_rejects_research_only_string_on_test_level(self):
        source = scoped()
        source["assessment"]["tests"]["test"]["collected_items_require"] = None
        with self.assertRaises(ValueError):
            lower_one(source)

    def test_rejects_missing_automated_specification(self):
        source = scoped()
        del source["assessment"]["specification"]
        with self.assertRaises(ValueError):
            lower_one(source)

    def test_invalid_evaluate_reference_is_not_ignored(self):
        source = scoped()
        source["assessment"]["evaluate"]["test"] = "missing"
        documents = {
            "authoring/rhel_9/a.json": source,
            "authoring/rhel_9/benchmark.json": {"benchmark": {
                "id": "ng.synthetic.rhel", "assessment_specifications": [SPEC]}},
            "authoring/rhel_9/rules/r.json": {"rule": {
                "id": "SV-TEST", "default_assessment_choice": "automated",
                "assessment_choices": {"automated": {"assessment": "ng.synthetic.reversible"}}}},
        }
        with self.assertRaisesRegex(ValueError, "unresolved authoring graph"):
            lower_all(documents, validate_base=False)


if __name__ == "__main__":
    unittest.main()
