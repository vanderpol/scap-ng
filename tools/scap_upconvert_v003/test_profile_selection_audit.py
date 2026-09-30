#!/usr/bin/env python3
"""Focused tests for XCCDF baseline and inherited compact profile parity."""
import unittest

from audit_profile_selection import expected_selections, native_profile_id


class SelectionAuditTests(unittest.TestCase):
    def test_group_selection_baseline_and_inherited_override(self):
        rules = [
            {"id": "xccdf_rule_SV-123r1_rule", "native": "SV-123", "selected": True},
            {"id": "xccdf_rule_SV-124r1_rule", "native": "SV-124", "selected": False},
        ]
        groups = [{"id": "group.a", "selected": False}]
        ancestry = {"SV-123": ["group.a"], "SV-124": []}
        inherited = {
            "kind": "select",
            "target_resolution": "resolved",
            "attributes": {"selected": "true"},
            "targets": [{"kind": "group", "id": "group.a"}],
        }
        child = {
            "kind": "select",
            "target_resolution": "resolved",
            "attributes": {"selected": "true"},
            "targets": [{"kind": "rule", "id": "xccdf_rule_SV-124r1_rule"}],
        }
        baseline, profiles = expected_selections(
            rules, groups, ancestry,
            [{"id": "xccdf_example_profile_parent",
              "effective_actions": [inherited], "inheritance_chain": ["parent"]},
             {"id": "xccdf_example_profile_child",
              "effective_actions": [inherited, child],
              "inheritance_chain": ["parent", "child"]}],
        )
        self.assertFalse(baseline["SV-123"])
        self.assertFalse(baseline["SV-124"])
        self.assertTrue(profiles["parent"]["enabled"]["SV-123"])
        self.assertFalse(profiles["parent"]["enabled"]["SV-124"])
        self.assertTrue(profiles["child"]["enabled"]["SV-124"])
        self.assertEqual(profiles["child"]["problems"], [])

    def test_unresolved_profile_select_is_reported(self):
        rules = [{"id": "source-r", "native": "SV-1", "selected": True}]
        baseline, profiles = expected_selections(
            rules, [], {"SV-1": []},
            [{"id": "xccdf_profile_a",
              "effective_actions": [{"kind": "select", "target_resolution": "unresolved_idref",
                                     "attributes": {"selected": "false"}, "targets": []}]}],
        )
        self.assertEqual(baseline, {"SV-1": True})
        self.assertEqual(profiles["a"]["problems"][0]["code"], "UNRESOLVED_SELECT")

    def test_profile_identity_fails_without_id(self):
        with self.assertRaises(ValueError):
            native_profile_id(None)



# Source-pinned integration tests run in CI with the original signed package.
import os
import tempfile
from pathlib import Path
from unittest.mock import patch
import yaml
from audit_profile_selection import audit


class ComparativeSelectionTests(unittest.TestCase):
    def test_missing_and_cyclic_extends_fail_closed(self):
        from audit_profile_selection import ir
        with self.assertRaisesRegex(ValueError, "unknown profile"):
            ir.resolve_profiles([{"id": "a", "extends": "missing", "actions": []}], [], [], [])
        with self.assertRaisesRegex(ValueError, "cycle"):
            ir.resolve_profiles([{"id": "a", "extends": "b", "actions": []},
                                 {"id": "b", "extends": "a", "actions": []}], [], [], [])

    def test_duplicate_and_conflicting_actions(self):
        def action(value, owner):
            return {"kind": "select", "target_resolution": "resolved",
                    "source_profile_id": owner, "attributes": {"selected": value},
                    "targets": [{"kind": "rule", "id": "r"}]}
        rules = [{"id": "r", "native": "SV-1", "selected": False}]
        _, rows = expected_selections(rules, [], {"SV-1": []}, [
            {"id": "xccdf_profile_a", "effective_actions": [action("true", "parent"),
              action("false", "child"), action("false", "child"), action("true", "child")]}])
        self.assertEqual([p["code"] for p in rows["a"]["problems"]],
                         ["DUPLICATE_SELECT", "CONFLICTING_SELECT"])
        self.assertEqual(len(rows["a"]["explicit_selection_history"]), 4)

    def test_native_duplicate_unknown_conflict_and_enabling(self):
        source = ([{"id": "r", "native": "SV-1", "selected": False}], [],
                  {"SV-1": []}, [{"id": "xccdf_profile_a", "effective_actions": []}])
        with tempfile.TemporaryDirectory() as tmp:
            zip_path = Path(tmp) / "source.zip"
            zip_path.write_bytes(b"synthetic")
            native = Path(tmp) / "benchmark.yaml"
            def check(profile):
                native.write_text(yaml.safe_dump({"benchmark": {"rules": ["SV-1"],
                    "default_selection": False, "profiles": [{"id": "a", **profile}]}}))
                with patch("audit_profile_selection.extract_selection", return_value=source):
                    return audit(zip_path, native)
            self.assertFalse(check({})["issues"])
            codes = {i["code"] for i in check({"enabled_rules": ["SV-1", "SV-1", "unknown"],
                                              "disabled_rules": ["SV-1"]})["issues"]}
            self.assertTrue({"DUPLICATE_NATIVE_OVERRIDE", "UNKNOWN_PROFILE_RULE",
                             "CONFLICTING_PROFILE_OVERRIDE", "PROFILE_SELECTION_MISMATCH"} <= codes)

    @unittest.skipUnless(os.environ.get("SCAP_NG_RHEL9_SOURCE"), "pinned ZIP supplied by CI")
    def test_all_445_rules_in_every_profile_and_mutation(self):
        source = Path(os.environ["SCAP_NG_RHEL9_SOURCE"])
        native = Path(__file__).resolve().parents[2] / (
            "research/iterations/003/source/split-rule-assessment/rhel9-full/benchmark.yaml")
        report = audit(source, native)
        self.assertEqual(report["source_rules"], 445)
        self.assertEqual(report["source_profiles"], 11)
        self.assertEqual(report["issues"], [])
        self.assertEqual(sum(p["rules_compared"] for p in report["profile_comparison"]), 4895)
        # Flip every rule in one profile: the comparator must catch all 445.
        document = yaml.safe_load(native.read_text())
        profile = document["benchmark"]["profiles"][0]
        expected = next(p for p in report["profile_comparison"] if p["profile"] == profile["id"])
        profile["enabled_rules"] = [r for r, v in expected["effective_selection"].items() if not v]
        profile["disabled_rules"] = [r for r, v in expected["effective_selection"].items() if v]
        with tempfile.TemporaryDirectory() as tmp:
            changed = Path(tmp) / "benchmark.yaml"
            changed.write_text(yaml.safe_dump(document))
            mutated = audit(source, changed)
        mismatches = [i for i in mutated["issues"] if i["code"] == "PROFILE_SELECTION_MISMATCH"]
        self.assertEqual(len(mismatches), 1)
        self.assertEqual(mismatches[0]["count"], 445)


if __name__ == "__main__":
    unittest.main()
