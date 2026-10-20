#!/usr/bin/env python3
"""Refs #246: non-Apache real original OVAL nested Set/Filter/Variable D pilot."""
from __future__ import annotations
from copy import deepcopy
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import yaml

from research_d_oval_sets import (
    present_d_oval_sets, compile_d_oval_sets, prove_d_oval_sets,
    export_d_oval_sets)


def original():
    p = os.environ.get("D_OVAL_SEVEN_SOURCE")
    if not p:
        p = str(Path(__file__).resolve().parents[1] /
                "research/assessment-simplification/04d-lossless-oval-set/"
                "original-source-compatible-a.json")
    path = Path(p)
    if not path.is_file():
        raise ValueError("Pinned seven-Test native source fixture missing: " + str(path))
    return json.loads(path.read_text(encoding="utf-8"))


class RealSevenTestNestedOVALSets(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.native = original()

    def setUp(self):
        self.author, self.provenance = present_d_oval_sets(self.native)

    def test_reconstruct_entire_native_source_graph_with_no_original_input(self):
        snapshot = deepcopy(self.native)
        actual = compile_d_oval_sets(self.author, self.provenance)
        self.assertEqual(actual, snapshot)
        self.assertEqual(self.native, snapshot)
        result = prove_d_oval_sets(self.native, self.author, self.provenance)
        self.assertTrue(result["native_source_graph_identical"])
        self.assertEqual(result["source_test_count"], 7)
        self.assertEqual(result["source_object_count"], 11)
        self.assertEqual(result["source_set_count"], 7)
        self.assertEqual(result["source_state_count"], 4)
        self.assertEqual(result["source_variable_count"], 3)
        self.assertEqual(result["authored_constant_variable_declarations"], 0)
        self.assertFalse(result["runtime_oval_scanner_parity_proven"])

    def test_explicit_test_requirement_no_items_split_or_fields_join(self):
        self.assertEqual(len(self.author["tests"]), 7)
        self.assertEqual(
            self.author["tests"]["three_level_sets"]["require"], "none_exist")
        self.assertNotIn("states", self.author["tests"]["three_level_sets"])
        self.assertEqual(
            self.author["tests"]["complement"]["require"],
            "only_one_exists_and_matches")
        self.assertEqual(
            self.author["tests"]["union"]["require"],
            "at_least_one_exists_and_all_match")
        for test in self.author["tests"].values():
            self.assertNotIn("must", test)
            self.assertNotIn("items_exist", test)
            self.assertNotIn("items_match", test)
            if "states" in test:
                self.assertEqual(len(test["states"]), 1)

    def test_full_nested_sets_and_original_filter_action_preserved(self):
        collections = self.author["collections"]
        self.assertEqual(len(collections), 11)
        set_nodes = [x for x in collections.values() if "set" in x]
        self.assertEqual(len(set_nodes), 7)
        actions = [
            f["action"] for x in set_nodes for f in x["set"].get("filters", [])]
        self.assertIn("exclude", actions)
        self.assertEqual(len(self.provenance["object_source_ids"]), 11)
        self.assertEqual(len(self.provenance["test_source_ids"]), 7)

    def test_literal_values_are_inline_without_authored_variables(self):
        self.assertNotIn("variables", self.author)
        self.assertEqual(len(self.author["expected_values"]), 4)
        self.assertEqual(len(self.provenance["constant_sources"]), 3)
        literals = [x for x in self.author["expected_values"].values()
                    if isinstance(x["equals"], list)]
        self.assertEqual(len(literals), 3)
        self.assertTrue(all(x["value_match"] == "one" for x in literals))

    def test_source_proof_catches_filter_rewrite(self):
        modified = deepcopy(self.author)
        key = next(key for key, obs in modified["collections"].items()
                   if "filters" in obs.get("set", {}))
        modified["collections"][key]["set"]["filters"][0]["action"] = "include"
        self.assertNotEqual(
            compile_d_oval_sets(modified, self.provenance), self.native)
        with self.assertRaisesRegex(ValueError, "authoring changed|differs"):
            prove_d_oval_sets(self.native, modified, self.provenance)

    def test_cardinality_none_not_replaced_with_some_or_all(self):
        modified = deepcopy(self.author)
        modified["tests"]["three_level_sets"]["require"] = (
            "at_least_one_exists_and_all_match")
        with self.assertRaisesRegex(ValueError, "States/existence"):
            compile_d_oval_sets(modified, self.provenance)
        modified = deepcopy(self.author)
        modified["tests"]["complement"]["require"] = "none_exist"
        with self.assertRaisesRegex(ValueError, "States/existence"):
            compile_d_oval_sets(modified, self.provenance)

    def test_source_proof_catches_changed_expected_values(self):
        modified = deepcopy(self.author)
        key = next(k for k, v in modified["expected_values"].items()
                   if isinstance(v["equals"], list))
        modified["expected_values"][key]["equals"][0] = "/not-original"
        self.assertNotEqual(
            compile_d_oval_sets(modified, self.provenance), self.native)
        with self.assertRaisesRegex(ValueError, "authoring changed|differs"):
            prove_d_oval_sets(self.native, modified, self.provenance)

    def test_declared_multivalue_quantifier_cannot_be_guessed(self):
        modified = deepcopy(self.author)
        key = next(k for k, v in modified["expected_values"].items()
                   if isinstance(v["equals"], list))
        modified["expected_values"][key]["value_match"] = "every"
        with self.assertRaises(ValueError):
            compile_d_oval_sets(modified, self.provenance)

    def test_unbound_and_reused_source_object_identity_fail(self):
        modified = deepcopy(self.provenance)
        key = next(iter(modified["object_source_ids"]))
        del modified["object_source_ids"][key]
        with self.assertRaisesRegex(ValueError, "binding catalog incomplete"):
            compile_d_oval_sets(self.author, modified)
        modified = deepcopy(self.provenance)
        keys = list(modified["object_source_ids"])
        modified["object_source_ids"][keys[1]] = modified["object_source_ids"][keys[0]]
        with self.assertRaisesRegex(ValueError, "source identity reused"):
            compile_d_oval_sets(self.author, modified)

    def test_result_expression_structure_and_test_references_preserved(self):
        self.assertEqual(self.author["evaluate"].keys(), {"all"})
        leafs = self.author["evaluate"]["all"]
        self.assertEqual(len(leafs), 7)
        self.assertEqual({x["test"] for x in leafs}, set(self.author["tests"]))
        modified = deepcopy(self.author)
        modified["evaluate"]["all"].pop()
        with self.assertRaisesRegex(ValueError, "reference each Test|authoring changed"):
            compile_d_oval_sets(modified, self.provenance)

    def test_json_yaml_roundtrip_and_review_files(self):
        with TemporaryDirectory() as temp:
            report = export_d_oval_sets(self.native, temp)
            self.assertEqual(report["source_test_count"], 7)
            a = yaml.safe_load((Path(temp) /
                "unix-set-seven-tests.0.4-D-author.yaml").read_text())
            p = yaml.safe_load((Path(temp) /
                "unix-set-seven-tests.0.4-D-provenance.yaml").read_text())
            self.assertEqual(compile_d_oval_sets(a, p), self.native)
            self.assertEqual(prove_d_oval_sets(self.native, a, p)[
                "source_set_count"], 7)


if __name__ == "__main__":
    unittest.main()
