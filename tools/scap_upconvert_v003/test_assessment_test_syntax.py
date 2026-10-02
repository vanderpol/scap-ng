#!/usr/bin/env python3
"""Focused authoring regressions before full benchmark regeneration."""
import copy
import unittest
from assessment_test_syntax import assessment_test_syntax, verify_assessment_test_syntax

class TestSyntax(unittest.TestCase):
    def source(self):
        return {"assessment": {"id": "a", "checks": {
            "alpha": {"test_title": "Alpha", "capability": "unix.file",
                      "assert": {"check": "all", "existence": "at_least_one_exists",
                                 "state": {"field": "path", "value": "/etc"}}},
            "beta": {"test_title": "Beta", "result": "unknown"}},
            "evaluate": {"and": [{"check": "alpha"},
                {"not": {"or": [{"check": "beta"}, {"check": "alpha"}]}}]}}}

    def test_nested_references_and_reused_test(self):
        original = self.source()
        before = copy.deepcopy(original)
        result = assessment_test_syntax(original)
        a = result["assessment"]
        self.assertEqual(set(a["tests"]), {"test-alpha", "test-beta"})
        self.assertEqual(a["evaluate"], {"and": [{"test": "test-alpha"},
            {"not": {"or": [{"test": "test-beta"}, {"test": "test-alpha"}]}}]})
        self.assertEqual(a["tests"]["test-alpha"]["assert"]["item_quantifier"], "all")
        self.assertEqual(original, before)
        verify_assessment_test_syntax(original, result)

    def test_deep_evaluation_tree_is_stack_safe(self):
        original = self.source()
        expr = {"check": "alpha"}
        for _ in range(1500):
            expr = {"not": expr}
        original["assessment"]["evaluate"] = expr
        converted = assessment_test_syntax(original)
        node = converted["assessment"]["evaluate"]
        for _ in range(1500):
            node = node["not"]
        self.assertEqual(node, {"test": "test-alpha"})

    def test_unknown_reference_rejected(self):
        original = self.source()
        original["assessment"]["evaluate"] = {"check": "missing"}
        with self.assertRaisesRegex(ValueError, "Unknown technical Test"):
            assessment_test_syntax(original)

    def test_semantic_changes_rejected(self):
        original = self.source()
        converted = assessment_test_syntax(original)
        converted["assessment"]["tests"]["test-alpha"]["assert"]["existence"] = "none_exist"
        with self.assertRaisesRegex(ValueError, "changed beyond"):
            verify_assessment_test_syntax(original, converted)

    def test_manual_payload_preserved(self):
        original = {"assessment": {"id": "manual", "mode": "manual",
                                  "question": "Review the documentation."}}
        self.assertEqual(assessment_test_syntax(original), original)

    def test_stale_false_metadata_removed(self):
        original = self.source()
        original["assessment"]["deprecated"] = False
        converted = assessment_test_syntax(original)
        self.assertNotIn("deprecated", converted["assessment"])
        self.assertIs(original["assessment"]["deprecated"], False)

    def test_deprecated_or_ambiguous_status_rejected(self):
        for value in (True, "false", None, 0):
            with self.subTest(value=value):
                original = self.source()
                original["assessment"]["deprecated"] = value
                with self.assertRaisesRegex(ValueError, "Deprecated Assessment"):
                    assessment_test_syntax(original)

if __name__ == "__main__":
    unittest.main()
