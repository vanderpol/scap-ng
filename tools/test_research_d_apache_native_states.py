#!/usr/bin/env python3
"""Refs #246 — source-backed D authoring with native Test/State relationships."""
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import sys
import unittest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from research_d_apache_native_states import (
    source_fixture, present_d_apache, compile_d_apache, export_review)


class ApacheDTests(unittest.TestCase):
    def setUp(self):
        self.source = source_fixture()
        self.author, self.sidecar = present_d_apache(self.source)

    def _cookie(self):
        return self.author["checks"][
            "if-sessioncookiename-directive-exists-in-other-loaded-configuration-files-verify"]

    def test_full_original_complex_graph_reconstructed_without_source_input(self):
        self.assertEqual(compile_d_apache(self.author, self.sidecar), self.source)
        self.assertEqual(len(self.author["checks"]), 5)
        self.assertEqual(len(self.author["derived_values"]), 19)
        self.assertEqual(len(self.author["observations"]), 1)
        native = compile_d_apache(
            yaml.safe_load(yaml.safe_dump(self.author, sort_keys=False)),
            yaml.safe_load(yaml.safe_dump(self.sidecar, sort_keys=False)))
        self.assertEqual(native["tests"], self.source["tests"])
        self.assertEqual(native["variables"], self.source["variables"])
        self.assertEqual(native["shared_objects"], self.source["shared_objects"])
        self.assertEqual(native["evaluate"], self.source["evaluate"])

    def test_two_cookie_states_same_item_and_explicit_combination(self):
        cookie = self._cookie()
        self.assertEqual(
            cookie["require"], "at_least_one_exists_and_all_match")
        self.assertEqual(cookie["states_match"], "all")
        self.assertEqual(cookie["states"], [
            {"stdout_line": {
                "require": "may_be_absent_and_all_match",
                "matches_regex": "(?i)HttpOnly"}},
            {"stdout_line": {
                "require": "may_be_absent_and_all_match",
                "matches_regex": "(?i)Secure"}},
        ])
        self.assertNotIn("fields_join", str(cookie))
        self.assertNotIn("items_exist", str(cookie))
        self.assertNotIn("items_match", str(cookie))
        native = compile_d_apache(self.author, self.sidecar)
        orig = native["tests"][
            "if-sessioncookiename-directive-exists-in-other-loaded-configuration-files-verify-test"]
        self.assertEqual(orig["states_match"], "all")
        self.assertEqual(orig["existence"], "one_or_more")
        self.assertEqual(orig["match"], "all")
        self.assertEqual([v["field"] for v in orig["states"]],
                         ["stdout_line", "stdout_line"])

    def test_optional_field_not_automatically_required(self):
        native = compile_d_apache(self.author, self.sidecar)
        target = native["tests"][
            "if-sessioncookiename-directive-exists-in-other-loaded-configuration-files-verify-test"]
        self.assertEqual(
            [x["existence"] for x in target["states"]],
            ["optional", "optional"])
        required = deepcopy(self.author)
        target = required["checks"][
            "if-sessioncookiename-directive-exists-in-other-loaded-configuration-files-verify"]
        target["states"][0]["stdout_line"]["require"] = (
            "at_least_one_exists_and_all_match")
        with self.assertRaisesRegex(ValueError, "source equivalence not proven"):
            compile_d_apache(required, self.sidecar)
        changed = compile_d_apache(
            required, self.sidecar, require_original_source=False)
        self.assertNotEqual(changed, self.source)

    def test_must_have_explicit_same_item_states_join(self):
        x = deepcopy(self.author)
        cookie = x["checks"][
            "if-sessioncookiename-directive-exists-in-other-loaded-configuration-files-verify"]
        cookie.pop("states_match")
        with self.assertRaisesRegex(ValueError, "must explicitly match all"):
            compile_d_apache(x, self.sidecar)
        cookie["states_match"] = "any"
        with self.assertRaisesRegex(ValueError, "must explicitly match all"):
            compile_d_apache(x, self.sidecar)

    def test_regression_prevents_unverified_test_cardinality(self):
        x = deepcopy(self.author)
        cookie = x["checks"][
            "if-sessioncookiename-directive-exists-in-other-loaded-configuration-files-verify"]
        cookie["require"] = "at_least_one_exists_and_some_match"
        with self.assertRaisesRegex(ValueError, "unsupported Test requirement"):
            compile_d_apache(x, self.sidecar)

    def test_regression_prevents_unverified_state_cardinality(self):
        x = deepcopy(self.author)
        cookie = x["checks"][
            "if-sessioncookiename-directive-exists-in-other-loaded-configuration-files-verify"]
        cookie["states"][0]["stdout_line"]["require"] = "none_exist"
        with self.assertRaisesRegex(ValueError, "unsupported State requirement"):
            compile_d_apache(x, self.sidecar)

    def test_source_pin_rejects_variable_and_collection_mutation(self):
        x = deepcopy(self.author)
        x["derived_values"][0]["description"] = "wrong source description"
        with self.assertRaisesRegex(ValueError, "source equivalence not proven"):
            compile_d_apache(x, self.sidecar)
        x = deepcopy(self.author)
        first = next(iter(x["checks"]))
        item = x["checks"][first]["from"]["independent.shellcommand"]["collect"]
        item["shell"] = "powershell"
        with self.assertRaisesRegex(ValueError, "source equivalence not proven"):
            compile_d_apache(x, self.sidecar)

    def test_managed_sidecar_is_required(self):
        with self.assertRaisesRegex(ValueError, "separate complete"):
            compile_d_apache(self.author, {})
        x = deepcopy(self.sidecar)
        key = next(iter(x["check_sources"]))
        x["check_sources"].pop(key)
        with self.assertRaisesRegex(ValueError, "binding catalog incomplete"):
            compile_d_apache(self.author, x)

    def test_explicit_modified_source_mode_preserves_type_checks(self):
        x = deepcopy(self.author)
        cookie = x["checks"][
            "if-sessioncookiename-directive-exists-in-other-loaded-configuration-files-verify"]
        cookie["states"][0]["stdout_line"]["matches_regex"] = "(?i)HttpOnly\\b"
        with self.assertRaisesRegex(ValueError, "source equivalence not proven"):
            compile_d_apache(x, self.sidecar)
        native = compile_d_apache(
            x, self.sidecar, require_original_source=False)
        self.assertNotEqual(native, self.source)
        self.assertEqual(len(native["variables"]), 19)
        self.assertEqual(len(native["tests"]), 5)

    def test_export_completely_browsable_authored_and_provenance_yaml(self):
        with TemporaryDirectory() as temp:
            report = export_review(temp)
            self.assertTrue(report["original_source_structural_equality"])
            self.assertEqual((report["tests"], report["variables"]), (5, 19))
            self.assertFalse(report["source_scanner_runtime_parity"])
            authored = yaml.safe_load((Path(temp) /
                "apache-sv214268.0.4-D-author.yaml").read_text())
            sidecar = yaml.safe_load((Path(temp) /
                "apache-sv214268.0.4-D-provenance.yaml").read_text())
            self.assertEqual(
                compile_d_apache(authored, sidecar), self.source)


if __name__ == "__main__":
    unittest.main()
