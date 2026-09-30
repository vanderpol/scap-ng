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


if __name__ == "__main__":
    unittest.main()
