#!/usr/bin/env python3
"""Refs #246 strict compact D original OVAL nested Sets and typed selectors."""
from copy import deepcopy
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
import yaml

from test_research_d_oval_sets import original
from research_d_set_factoring import present_factored_sets
from research_d_compact_collections import (
    present_compact_collections, compile_compact_collections,
    prove_compact_collections, export_compact_collections)


class ExactSourceCompactCollections(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = original()

    def setUp(self):
        self.author, self.sidecar, self.counts = present_compact_collections(self.source)

    def _leaf(self):
        return next(x for x in self.author["collections"].values() if "select" in x)

    def test_full_original_source_equality_and_reversible_yaml(self):
        self.assertEqual(compile_compact_collections(self.author, self.sidecar),
                         self.source)
        proof = prove_compact_collections(
            self.source, self.author, self.sidecar)
        self.assertTrue(proof["native_source_graph_identical"])
        self.assertEqual(proof["source_object_count"], 11)
        self.assertEqual(proof["source_set_count"], 7)
        self.assertEqual(proof["source_test_count"], 7)
        self.assertEqual(proof["source_variable_count"], 3)
        self.assertEqual(proof["short_literal_unix_file_selectors"], 4)
        self.assertEqual(proof["authored_redundant_source_titles"], 0)

    def test_actual_authoring_reduction_without_hiding_comparison(self):
        factored, _, _ = present_factored_sets(self.source)
        compact_yaml = yaml.safe_dump(self.author, sort_keys=False)
        base_yaml = yaml.safe_dump(factored, sort_keys=False)
        self.assertLess(len(compact_yaml.splitlines()),
                        len(base_yaml.splitlines()) - 20)
        self.assertLess(len(compact_yaml.encode()), len(base_yaml.encode()))
        leaf = self._leaf()
        self.assertEqual(leaf["select"]["filename"], {"nil": True})
        self.assertIsInstance(leaf["select"]["path"], str)
        self.assertNotIn("object_title", leaf)
        self.assertNotIn("operation", str(leaf["select"]))
        self.assertNotIn("datatype", str(leaf["select"]))

    def test_unknown_nil_shortcut_cannot_silently_alter_filename(self):
        modified = deepcopy(self.author)
        next(x for x in modified["collections"].values() if "select" in x)[
            "select"]["filename"] = {"nil": False}
        with self.assertRaisesRegex(ValueError, "original literal"):
            compile_compact_collections(modified, self.sidecar)

    def test_nonstring_selector_not_accepted_as_original_source(self):
        modified = deepcopy(self.author)
        next(x for x in modified["collections"].values() if "select" in x)[
            "select"]["path"] = ["/opt/support"]
        with self.assertRaisesRegex(ValueError, "original literal"):
            compile_compact_collections(modified, self.sidecar)

    def test_wrong_path_is_a_new_assessment_not_original_source(self):
        modified = deepcopy(self.author)
        next(x for x in modified["collections"].values() if "select" in x)[
            "select"]["path"] = "/opt/unrelated"
        self.assertNotEqual(compile_compact_collections(
            modified, self.sidecar), self.source)
        with self.assertRaisesRegex(ValueError, "diverged"):
            prove_compact_collections(self.source, modified, self.sidecar)

    def test_missing_source_documentation_provenance_fail_closed(self):
        altered = deepcopy(self.sidecar)
        altered["object_titles"].pop(next(iter(altered["object_titles"])))
        with self.assertRaisesRegex(ValueError, "every named source Object"):
            compile_compact_collections(self.author, altered)

    def test_wrong_source_documentation_does_not_pass_original_proof(self):
        altered = deepcopy(self.sidecar)
        key = next(iter(altered["object_titles"]))
        altered["object_titles"][key] = "Something unrelated"
        with self.assertRaisesRegex(ValueError, "diverged"):
            prove_compact_collections(self.source, self.author, altered)

    def test_reused_nested_set_still_has_original_filter_action(self):
        self.assertIn("reuse_set", str(self.author["collections"]))
        filter_obs = next(x for x in self.author["collections"].values()
                          if "filters" in x.get("set", {}))
        self.assertEqual(filter_obs["set"]["filters"][0]["action"], "exclude")

    def test_export_checked_yaml_and_provenance(self):
        with TemporaryDirectory() as td:
            report = export_compact_collections(self.source, td)
            self.assertEqual(report["source_test_count"], 7)
            self.assertEqual(report["compact_literal_path_selectors"], 4)
            author = yaml.safe_load((Path(td) /
                "unix-set-seven-tests.0.4-D-compact-author.yaml").read_text())
            prov = yaml.safe_load((Path(td) /
                "unix-set-seven-tests.0.4-D-compact-provenance.yaml").read_text())
            self.assertEqual(compile_compact_collections(author, prov), self.source)


if __name__ == "__main__":
    unittest.main()
