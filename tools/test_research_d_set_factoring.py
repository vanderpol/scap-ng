#!/usr/bin/env python3
"""Refs #246 D exact-source authored nested Set reuse adversarial tests."""
from copy import deepcopy
import unittest

from test_research_d_oval_sets import original
from research_d_oval_sets import present_d_oval_sets
from research_d_set_factoring import (
    present_factored_sets, compile_factored_sets, prove_factored_sets,
    _count_reuse, export_factored_sets)
from tempfile import TemporaryDirectory
from pathlib import Path
import yaml


class SourceExactFactoring(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = original()

    def setUp(self):
        self.author, self.sidecar, self.reuses = present_factored_sets(self.source)

    def test_full_source_graph_reconstructed_and_actual_reuse(self):
        self.assertEqual(compile_factored_sets(self.author, self.sidecar), self.source)
        proof = prove_factored_sets(self.source, self.author, self.sidecar)
        self.assertTrue(proof["native_source_graph_identical"])
        self.assertEqual(proof["source_set_count"], 7)
        self.assertEqual(proof["source_test_count"], 7)
        self.assertEqual(proof["source_variable_count"], 3)
        self.assertEqual(proof["authored_constant_variable_declarations"], 0)
        self.assertFalse(proof["new_runtime_set_collector_required"])
        self.assertGreaterEqual(self.reuses, 2)

    def test_authoring_subtree_is_really_less_than_original_d(self):
        a, _ = present_d_oval_sets(self.source)
        old = yaml.safe_dump(a, sort_keys=False)
        new = yaml.safe_dump(self.author, sort_keys=False)
        self.assertLess(len(new.splitlines()), len(old.splitlines()))
        self.assertLess(len(new.encode()), len(old.encode()))
        self.assertEqual(self.reuses, _count_reuse(self.author["collections"]))

    def test_unknown_set_reuse_fails_closed(self):
        corrupted = deepcopy(self.author)
        key = next(k for k, x in corrupted["collections"].items()
                   if _count_reuse(x))
        # Mutation to a specifically nested reused Set alias.
        node = corrupted["collections"][key]
        def corrupt(node):
            if isinstance(node, list):
                for x in node:
                    if corrupt(x): return True
            elif isinstance(node, dict):
                if set(node) == {"reuse_set"}:
                    node["reuse_set"] = "no_such_source_set"
                    return True
                for value in node.values():
                    if corrupt(value): return True
            return False
        self.assertTrue(corrupt(node))
        with self.assertRaisesRegex(ValueError, "unresolved"):
            compile_factored_sets(corrupted, self.sidecar)

    def test_recursive_set_alias_is_rejected(self):
        corrupted = deepcopy(self.author)
        key = next(k for k, x in corrupted["collections"].items()
                   if "set" in x)
        corrupted["collections"][key]["set"]["members"][0] = {"reuse_set": key}
        with self.assertRaisesRegex(ValueError, "recursive"):
            compile_factored_sets(corrupted, self.sidecar)

    def test_select_and_nonmember_context_reject_reuse(self):
        corrupted = deepcopy(self.author)
        key = next(k for k, x in corrupted["collections"].items()
                   if "select" in x)
        target = next(k for k, x in corrupted["collections"].items()
                      if "set" in x)
        corrupted["collections"][key]["select"] = {"reuse_set": target}
        with self.assertRaisesRegex(ValueError, "only allowed"):
            compile_factored_sets(corrupted, self.sidecar)

    def test_filter_action_cannot_change_without_proof(self):
        corrupted = deepcopy(self.author)
        key = next(k for k, obs in corrupted["collections"].items()
                   if "filters" in obs.get("set", {}))
        corrupted["collections"][key]["set"]["filters"][0]["action"] = "include"
        with self.assertRaisesRegex(ValueError, "factored Set graph differs"):
            prove_factored_sets(self.source, corrupted, self.sidecar)

    def test_alias_change_to_distinct_source_set_causes_source_drift(self):
        corrupted = deepcopy(self.author)
        set_names = [k for k, obs in corrupted["collections"].items()
                     if "set" in obs]
        def change(node):
            if isinstance(node, list):
                return any(change(x) for x in node)
            if isinstance(node, dict):
                if set(node) == {"reuse_set"}:
                    node["reuse_set"] = next(k for k in set_names
                                             if k != node["reuse_set"])
                    return True
                return any(change(x) for x in node.values())
            return False
        self.assertTrue(change(corrupted["collections"]))
        with self.assertRaisesRegex(ValueError, "factored Set graph differs"):
            prove_factored_sets(self.source, corrupted, self.sidecar)

    def test_export_factored_yaml_and_reload(self):
        with TemporaryDirectory() as td:
            result = export_factored_sets(self.source, td)
            self.assertEqual(result["source_set_count"], 7)
            author = yaml.safe_load(
                (Path(td) / "unix-set-seven-tests.0.4-D-reused-sets.yaml").read_text())
            self.assertEqual(compile_factored_sets(author, self.sidecar), self.source)


if __name__ == "__main__":
    unittest.main()
