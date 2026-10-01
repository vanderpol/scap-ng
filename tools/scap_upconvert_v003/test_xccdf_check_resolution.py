#!/usr/bin/env python3
import unittest

from xccdf_check_resolution import (
    CheckContentResolutionError,
    resolve_check_content,
)


class XccdfCheckContentResolutionTests(unittest.TestCase):
    def test_first_successful_reference_wins_and_later_refs_are_not_touched(self):
        calls = []
        refs = [
            {"href": "missing.xml", "name": "a"},
            {"href": "chosen.xml", "name": "b"},
            {"href": "later.xml", "name": "c"},
        ]

        def resolver(href, name):
            calls.append((href, name))
            if href == "missing.xml":
                return None
            if href == "chosen.xml":
                return "chosen-content"
            raise AssertionError("later alternative must not be evaluated")

        result = resolve_check_content(refs, "embedded", resolver)
        self.assertEqual(result["source"], "check-content-ref")
        self.assertEqual(result["selected_index"], 1)
        self.assertEqual(result["content"], "chosen-content")
        self.assertEqual(
            calls,
            [("missing.xml", "a"), ("chosen.xml", "b")],
        )
        self.assertEqual([x["resolved"] for x in result["attempts"]], [False, True])

    def test_lookup_failure_continues_to_next_reference(self):
        refs = [
            {"href": "one.xml"},
            {"href": "two.xml"},
        ]

        def resolver(href, name):
            if href == "one.xml":
                raise FileNotFoundError("not present in pinned source set")
            return "two"

        result = resolve_check_content(refs, None, resolver)
        self.assertEqual(result["selected_index"], 1)
        self.assertIn("not present", result["attempts"][0]["error"])

    def test_embedded_content_is_only_fallback_after_all_refs_fail(self):
        refs = [{"href": "one.xml"}, {"href": "two.xml", "name": "x"}]
        result = resolve_check_content(refs, "embedded", lambda href, name: None)
        self.assertEqual(result["source"], "check-content")
        self.assertEqual(result["content"], "embedded")
        self.assertEqual(len(result["attempts"]), 2)
        self.assertTrue(all(not x["resolved"] for x in result["attempts"]))

    def test_embedded_content_is_used_when_no_references_exist(self):
        result = resolve_check_content([], "embedded", lambda href, name: None)
        self.assertEqual(result["source"], "check-content")
        self.assertEqual(result["attempts"], [])

    def test_no_resolvable_content_is_a_conversion_blocker(self):
        with self.assertRaises(CheckContentResolutionError):
            resolve_check_content(
                [{"href": "missing.xml"}],
                None,
                lambda href, name: None,
            )


if __name__ == "__main__":
    unittest.main()
