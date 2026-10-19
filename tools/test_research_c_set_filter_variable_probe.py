#!/usr/bin/env python3
"""Refs #245: bounded Set/Filter/Variable probe tests, NOT OVAL parity."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parent))
from research_c_set_filter_variable_probe import (
    UnsupportedSourceSemantics, probe_complete_dataflow,
)


def fixture():
    """Three target files and derived UID filter, modeled on Board 0.2 case.

    A-style synthetic fixture: not a converted source or independent oracle.
    """
    return {
        "id": "ng.research.filtered-owner-file-assessment", "mode": "automated",
        "shared_objects": {
            "target-a-object": {"capability": "unix.file", "select": {"full_path": {"equals": "/fixture/a"}}},
            "target-b-object": {"capability": "unix.file", "select": {"full_path": {"equals": "/fixture/b"}}},
            "extra-c-object": {"capability": "unix.file", "select": {"full_path": {"equals": "/fixture/c"}}},
            "reference-owner-object": {"capability": "unix.file", "select": {"full_path": {"equals": "/fixture/reference"}}},
            "candidate-files-object": {"capability": "unix.file", "set": {
                "operator": "union", "operands": [
                    {"object": "target-a-object"}, {"object": "target-b-object"},
                    {"object": "extra-c-object"}]}},
            "filtered-target-files-object": {"capability": "unix.file", "set": {
                "operator": "intersection", "operands": [
                    {"object": "candidate-files-object", "filters": [
                        {"exclude": {"owner_uid": {
                            "require": "at_least_one_exists_and_all_match",
                            "equals": {"variable": "excluded-owner-uids-variable"},
                            "value_match": "one_or_more"}}}]},
                    {"set": {"operator": "union", "operands": [
                        {"object": "target-a-object"}, {"object": "target-b-object"}]}}
                ]}},
        },
        "variables": {
            "reference-owner-uid-variable": {"kind": "local", "datatype": "integer", "expression": {
                "values": {"object": "reference-owner-object", "field": "owner_uid"}}},
            "uid-step-variable": {"kind": "constant", "datatype": "integer", "value": 1},
            "first-excluded-uid-variable": {"kind": "local", "datatype": "integer", "expression": {
                "arithmetic": {"operation": "add", "operands": [
                    {"variable": "reference-owner-uid-variable"},
                    {"variable": "uid-step-variable"}]}}},
            "uid-band-offsets-variable": {"kind": "constant", "datatype": "integer", "value": [0, 1]},
            "excluded-owner-uids-variable": {"kind": "local", "datatype": "integer", "expression": {
                "arithmetic": {"operation": "add", "operands": [
                    {"variable": "first-excluded-uid-variable"},
                    {"variable": "uid-band-offsets-variable"}]}}},
        },
        "tests": {
            "exactly-one-surviving-file-test": {
                "test_title": "Exactly one unexcluded target file survives the filtered Set.",
                "capability": "unix.file", "object": "filtered-target-files-object",
                "require": "only_one_exists"}},
        "evaluate": {"test": "exactly-one-surviving-file-test"},
    }


def snapshots():
    return {
        "target-a-object": {"status": "complete", "items": [
            {"id": "item-a", "fields": {"owner_uid": 1000}}]},
        "target-b-object": {"status": "complete", "items": [
            {"id": "item-b", "fields": {"owner_uid": 1001}}]},
        "extra-c-object": {"status": "complete", "items": [
            {"id": "item-c", "fields": {"owner_uid": 1002}}]},
        "reference-owner-object": {"status": "complete", "items": [
            {"id": "item-ref", "fields": {"owner_uid": 1000}}]},
    }


class CDataflowProbeTests(unittest.TestCase):
    def test_nested_set_filter_variable_and_documentation_preserved(self):
        doc, data = fixture(), snapshots()
        original, observed = deepcopy(doc), deepcopy(data)
        out = probe_complete_dataflow(doc, data)
        self.assertEqual((doc, data), (original, observed))
        self.assertEqual([i["id"] for i in out["item_populations"]["filtered-target-files-object"]], ["item-a"])
        self.assertEqual(out["variable_values"]["excluded-owner-uids-variable"], [1001, 1002])
        self.assertEqual(out["source_tests_unchanged"], original["tests"])
        self.assertEqual(out["source_evaluate_unchanged"], original["evaluate"])
        self.assertEqual(len([s for s in out["source_graph"]["sites"] if s["kind"] == "set"]), 3)
        self.assertEqual(len([s for s in out["source_graph"]["sites"] if s["kind"] == "filter"]), 1)
        self.assertTrue(out["original_source_unchanged"])
        self.assertFalse(out["scanner_executed"])
        self.assertFalse(out["six_state_semantics_proven"])
        self.assertFalse(out["oval_semantics_proven"])

    def test_empty_collection_never_implies_test_truth(self):
        data = snapshots()
        for k in ("target-a-object", "target-b-object", "extra-c-object"):
            data[k]["items"] = []
        out = probe_complete_dataflow(fixture(), data)
        self.assertEqual(out["item_populations"]["filtered-target-files-object"], [])
        self.assertNotIn("outcome", out)

    def test_include_and_exclude_filters_are_separate(self):
        doc = fixture()
        fs = doc["shared_objects"]["filtered-target-files-object"]["set"]["operands"][0]["filters"]
        fs.insert(0, {"include": {"owner_uid": {
            "require": "at_least_one_exists_and_all_match", "greater_than": 999}}})
        self.assertEqual([i["id"] for i in probe_complete_dataflow(doc, snapshots())[
            "item_populations"]["filtered-target-files-object"]], ["item-a"])

    def test_expected_multivalue_quantifier_is_required(self):
        doc = fixture()
        pred = doc["shared_objects"]["filtered-target-files-object"]["set"]["operands"][0]["filters"][0]["exclude"]["owner_uid"]
        pred.pop("value_match")
        with self.assertRaisesRegex(UnsupportedSourceSemantics, "value_match"):
            probe_complete_dataflow(doc, snapshots())

    def test_unknown_comparator_rejected(self):
        doc = fixture()
        pred = doc["shared_objects"]["filtered-target-files-object"]["set"]["operands"][0]["filters"][0]["exclude"]["owner_uid"]
        pred["between"] = pred.pop("equals")
        with self.assertRaisesRegex(UnsupportedSourceSemantics, "comparator"):
            probe_complete_dataflow(doc, snapshots())

    def test_missing_fields_fail_closed(self):
        data = snapshots()
        data["target-b-object"]["items"][0]["fields"] = {}
        with self.assertRaisesRegex(UnsupportedSourceSemantics, "missing observed field"):
            probe_complete_dataflow(fixture(), data)

    def test_statuses_do_not_become_successful_empty(self):
        for status in ("error", "incomplete", "not_collected", "not_applicable", "does_not_exist"):
            with self.subTest(status=status):
                data = snapshots()
                data["target-b-object"]["status"] = status
                with self.assertRaisesRegex(UnsupportedSourceSemantics, "no fabricated Boolean"):
                    probe_complete_dataflow(fixture(), data)

    def test_duplicate_id_rejected(self):
        data = snapshots()
        data["target-a-object"]["items"].append(deepcopy(data["target-a-object"]["items"][0]))
        with self.assertRaisesRegex(UnsupportedSourceSemantics, "duplicate Item identity"):
            probe_complete_dataflow(fixture(), data)

    def test_cross_source_item_identity_conflict_rejected(self):
        data = snapshots()
        data["target-b-object"]["items"][0]["id"] = "item-a"
        with self.assertRaisesRegex(UnsupportedSourceSemantics, "conflict"):
            probe_complete_dataflow(fixture(), data)

    def test_invalid_reference_and_cycle_rejected(self):
        doc = fixture()
        doc["variables"]["reference-owner-uid-variable"]["expression"] = {
            "variable": "excluded-owner-uids-variable"}
        with self.assertRaisesRegex(ValueError, "cyclic source dataflow"):
            probe_complete_dataflow(doc, snapshots())
        doc = fixture()
        doc["shared_objects"]["candidate-files-object"]["set"]["operands"][0]["object"] = "missing-object"
        with self.assertRaisesRegex(ValueError, "unresolved object"):
            probe_complete_dataflow(doc, snapshots())

    def test_foreach_is_not_flattened(self):
        doc = fixture()
        doc["shared_objects"]["target-a-object"]["for_each"] = {
            "item": "user", "in": "reference-owner-object"}
        doc["shared_objects"]["target-a-object"]["select"] = {
            "full_path": {"from": "user.home_dir"}}
        with self.assertRaisesRegex(UnsupportedSourceSemantics, "foreach"):
            probe_complete_dataflow(doc, snapshots())

    def test_missing_test_description_fails_for_human_projection(self):
        doc = fixture()
        doc["tests"]["exactly-one-surviving-file-test"].pop("test_title")
        with self.assertRaisesRegex(UnsupportedSourceSemantics, "source Test description"):
            probe_complete_dataflow(doc, snapshots())


if __name__ == "__main__":
    unittest.main()
