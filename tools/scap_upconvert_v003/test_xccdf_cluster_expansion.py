#!/usr/bin/env python3
import unittest

from xccdf_cluster_expansion import (
    ClusterExpansionError,
    expand_cluster_operations,
)


class XccdfClusterExpansionTests(unittest.TestCase):
    def test_cluster_expands_in_member_order_at_source_position(self):
        operations = [
            {"type": "select", "idref": "rule-before", "selected": True},
            {"type": "select", "idref": "cluster-a", "selected": False},
            {"type": "select", "idref": "rule-after", "selected": True},
        ]
        clusters = {
            "cluster-a": [
                {"id": "rule-1", "kind": "rule"},
                {"id": "group-1", "kind": "group"},
                {"id": "rule-2", "kind": "rule"},
            ]
        }
        result = expand_cluster_operations(
            operations,
            clusters,
            {"rule-before", "rule-after", "rule-1", "group-1", "rule-2"},
        )
        self.assertEqual(
            [x["idref"] for x in result],
            ["rule-before", "rule-1", "group-1", "rule-2", "rule-after"],
        )
        self.assertEqual(
            [x["source_index"] for x in result],
            [0, 1, 1, 1, 2],
        )
        self.assertEqual(
            [x.get("expanded_from_cluster") for x in result[1:4]],
            ["cluster-a", "cluster-a", "cluster-a"],
        )

    def test_value_operation_ignores_rule_group_members(self):
        result = expand_cluster_operations(
            [{"type": "set-value", "idref": "mixed", "value": "x"}],
            {
                "mixed": [
                    {"id": "rule-1", "kind": "rule"},
                    {"id": "value-1", "kind": "value"},
                    {"id": "group-1", "kind": "group"},
                    {"id": "value-2", "kind": "value"},
                ]
            },
            {"rule-1", "value-1", "group-1", "value-2"},
        )
        self.assertEqual([x["idref"] for x in result], ["value-1", "value-2"])

    def test_rule_operation_ignores_value_members(self):
        result = expand_cluster_operations(
            [{"type": "refine-rule", "idref": "mixed", "severity": "high"}],
            {
                "mixed": [
                    {"id": "value-1", "kind": "value"},
                    {"id": "rule-1", "kind": "rule"},
                ]
            },
            {"value-1", "rule-1"},
        )
        self.assertEqual([x["idref"] for x in result], ["rule-1"])

    def test_direct_reference_remains_direct(self):
        op = {"type": "select", "idref": "rule-1", "selected": False}
        result = expand_cluster_operations([op], {}, {"rule-1"})
        self.assertEqual(result[0]["idref"], "rule-1")
        self.assertNotIn("expanded_from_cluster", result[0])

    def test_ambiguous_direct_and_cluster_identity_fails_closed(self):
        with self.assertRaises(ClusterExpansionError):
            expand_cluster_operations(
                [{"type": "select", "idref": "same", "selected": True}],
                {"same": [{"id": "rule-1", "kind": "rule"}]},
                {"same", "rule-1"},
            )

    def test_cluster_with_no_compatible_members_fails(self):
        with self.assertRaises(ClusterExpansionError):
            expand_cluster_operations(
                [{"type": "set-value", "idref": "rules-only", "value": "x"}],
                {"rules-only": [{"id": "rule-1", "kind": "rule"}]},
                {"rule-1"},
            )

    def test_later_explicit_member_operation_remains_later(self):
        operations = [
            {"type": "select", "idref": "cluster-a", "selected": False},
            {"type": "select", "idref": "rule-2", "selected": True},
        ]
        result = expand_cluster_operations(
            operations,
            {
                "cluster-a": [
                    {"id": "rule-1", "kind": "rule"},
                    {"id": "rule-2", "kind": "rule"},
                ]
            },
            {"rule-1", "rule-2"},
        )
        self.assertEqual(
            [(x["idref"], x["selected"]) for x in result],
            [("rule-1", False), ("rule-2", False), ("rule-2", True)],
        )


if __name__ == "__main__":
    unittest.main()
