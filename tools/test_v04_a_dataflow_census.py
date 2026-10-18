#!/usr/bin/env python3
"""#240: source-backed IR census proof and deliberately narrow expected fixtures."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_v04_a_lossless_ir import fixture, automated
from v04_a_lossless_ir import normalize_documents
from v04_a_dataflow_census import census


def sample():
    docs = fixture()
    auto = automated(docs)
    auto["shared_objects"] = {
        "users-object": {"capability": "unix.password"},
        "files-object": {"capability": "unix.file",
                         "for_each": {"item": "user", "in": "users-object"},
                         "select": {"directory": {"from": "user.home"}}},
        "filtered-object": {"capability": "unix.file",
                            "set": {"operator": "union", "operands": [
                                {"object": "files-object", "filters": [
                                    {"exclude": {"uid": {"equals": 0}}}]}]}},
    }
    auto["variables"] = {
        "a-variable": {"kind": "constant", "expression": {"literal": "a"}},
        "b-variable": {"kind": "local", "expression": {
            "concat": [{"variable": "a-variable"}, ".txt"]}},
    }
    test = next(iter(auto["tests"].values()))
    test["object"] = "filtered-object"
    return docs


class SourceCensusTests(unittest.TestCase):
    def test_counts_distinct_nodes_and_real_source_paths(self):
        ir = normalize_documents(sample())
        a = census(ir)
        self.assertEqual(a["status"], "VERIFIED_SOURCE_STRUCTURE_NOT_EXECUTABLE")
        self.assertEqual(a["document_count"], 4)
        counts = a["counts"]
        self.assertEqual(counts["automated_assessments"], 1)
        self.assertEqual(counts["named_test_nodes"], 1)
        self.assertEqual(counts["named_variable_nodes"], 2)
        self.assertEqual(counts["named_object_nodes"], 3)
        self.assertEqual(counts["edge_for_each_source"], 1)
        self.assertEqual(counts["edge_variable_value"], 1)
        self.assertEqual(counts["edge_object_acquisition"], 2)
        self.assertEqual(counts["site_filter"], 1)
        self.assertEqual(counts["site_set"], 1)
        self.assertEqual(counts["site_projection"], 1)
        self.assertEqual(counts["site_for_each"], 1)
        self.assertEqual(set(a["source_backed_examples"]),
                         {"for_each", "projection", "set", "filter"})
        self.assertTrue(all(row["source_path"].startswith("authoring/")
                            for row in a["largest_dataflow_examples"]))
        self.assertEqual(a["source_backed_examples"]["filter"]["assessment_id"],
                         automated(sample())["id"])
        self.assertEqual(len(a["foreach_source_bindings"]), 1)
        binding = a["foreach_source_bindings"][0]
        self.assertEqual(binding["source_object"], "users-object")
        self.assertEqual(binding["item_alias"], "user")
        self.assertEqual(binding["projections"], [
            {"selector": "directory", "from": "user.home"}])

    def test_order_independence_and_reference_sha(self):
        docs = sample()
        original = census(normalize_documents(docs))
        reordered = dict(reversed(list(docs.items())))
        self.assertEqual(original, census(normalize_documents(reordered)))
        wrong = normalize_documents(docs)
        wrong["documents"][0]["source_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "digest"):
            census(wrong)

    def test_absent_semantic_operators_are_not_invented(self):
        a = census(normalize_documents(fixture()))
        self.assertEqual(a["counts"].get("site_for_each", 0), 0)
        self.assertEqual(a["counts"].get("edge_variable_value", 0), 0)
        self.assertNotIn("for_each", a["source_backed_examples"])


if __name__ == "__main__":
    unittest.main()
