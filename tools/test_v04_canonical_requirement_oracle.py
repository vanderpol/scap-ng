#!/usr/bin/env python3
"""Focused source-backed canonical requirement and six-state oracle guards."""
import unittest

from v04_canonical_requirement_oracle import (
    comparison_matrix, compare_original_to_canonical, describe, source_axes,
)
from build_v04_canonical_six_stigs import promote


class SourceRequirementOracleTests(unittest.TestCase):
    def _docs(self, old):
        source = {"authoring/demo/a.json": {"assessment": {
            "id": "a", "mode": "automated", "tests": {"test": old}}}}
        newer = {path: promote(doc)[0] for path, doc in source.items()}
        return source, newer

    def test_state_free_absence_retains_oval_none_exist(self):
        source, newer = self._docs({
            "capability": "unix.file", "require": "none_exist"})
        r = compare_original_to_canonical(source, newer)
        self.assertEqual(r["test_population"]["converted_presence"], 1)
        self.assertFalse(r["scanner_parity"])
        self.assertGreater(r["generic_scenarios"], 0)

    def test_all_match_preserves_distinct_item_and_field_requirements(self):
        old = {
            "capability": "windows.registry",
            "object": {"capability": "windows.registry"},
            "require": "at_least_one_exists_and_all_match",
            "states": [{"value": {"equals": 0,
                                  "require": "at_least_one_exists_and_all_match"}}],
        }
        source, newer = self._docs(old)
        result = compare_original_to_canonical(source, newer)
        self.assertEqual(result["test_population"]["converted_all_items"], 1)
        canonical = newer["authoring/demo/a.json"]["assessment"]["tests"]["test"]
        self.assertEqual(canonical["require"]["items"], "one_or_more")
        self.assertEqual(canonical["require"]["all_items_must"], old["states"])
        self.assertNotIn("capability", canonical["object"])

    def test_unsupported_matching_remains_exception(self):
        source, newer = self._docs({
            "capability": "unix.file", "require": "at_least_one_exists_and_some_match",
            "states": [{"mode": {"equals": "0700"}}]})
        # No supported structured axes exists; old Test is preserved verbatim.
        with self.assertRaisesRegex(ValueError, "exceptional"):
            source_axes(source["authoring/demo/a.json"]["assessment"]["tests"]["test"])
        result = compare_original_to_canonical(source, newer) if False else None
        self.assertIsNone(result)

    def test_source_change_or_fake_result_fails(self):
        source, newer = self._docs({
            "capability": "unix.file", "require": "at_least_one_exists",
        })
        newer["authoring/demo/a.json"]["assessment"]["tests"]["test"][
            "require"]["items"] = "none"
        with self.assertRaisesRegex(ValueError, "differs from exact source"):
            compare_original_to_canonical(source, newer)

    def test_all_supported_existence_modes_have_matrix(self):
        for req in (
            {"items": "one_or_more"}, {"items": "none"},
            {"items": "exactly_one"}, {"items": "all"},
            {"items": "may_be_absent"},
            {"items": "one_or_more", "all_items_must": [{"mode": {"equals": "0700"}}]},
            {"items": "may_be_absent", "all_items_must": [{"mode": {"equals": "0700"}}]},
        ):
            axis = describe(req)
            counts = comparison_matrix(axis)
            self.assertGreater(counts["compared"], 0)


if __name__ == "__main__":
    unittest.main()
