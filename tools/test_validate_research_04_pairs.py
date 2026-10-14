#!/usr/bin/env python3
"""Negative and positive tests for research-only 0.4 presentation round trip."""
import unittest
from copy import deepcopy

from validate_research_04_pairs import restore_with_original_witness

def fixtures():
    source = {"assessment": {
        "id": "example",
        "variables": {
            "derived-path-variable": {
                "kind": "local", "datatype": "string",
                "expression": {"concat": [{"literal": "/etc/"}, {"object": "source-object"}]},
                "title": "Resolved path",
            },
            "other-variable": {"kind": "constant", "datatype": "string",
                               "expression": {"literal": "keep"}},
        },
        "objects": {"target-object": {"select": {"path": {
            "value": {"variable": "derived-path-variable"},
            "value_match": "one_or_more"}}}},
    }}
    after = deepcopy(source)
    target = after["assessment"]["objects"]["target-object"]["select"]["path"]
    target["value"] = {
        "expression": deepcopy(source["assessment"]["variables"]["derived-path-variable"]["expression"]),
        "research_inline_source_variable": "derived-path-variable",
    }
    del after["assessment"]["variables"]["derived-path-variable"]
    return source, after

class PairValidationTest(unittest.TestCase):
    def test_round_trip_with_original_witness(self):
        before, after = fixtures()
        self.assertEqual(restore_with_original_witness(before, after), before)

    def test_changed_expression_must_fail(self):
        before, after = fixtures()
        after["assessment"]["objects"]["target-object"]["select"]["path"]["value"]["expression"] = {"literal": "/wrong"}
        with self.assertRaises(ValueError):
            restore_with_original_witness(before, after)

    def test_other_fields_cannot_change(self):
        before, after = fixtures()
        after["assessment"]["objects"]["target-object"]["select"]["path"]["value_match"] = "all"
        with self.assertRaises(ValueError):
            restore_with_original_witness(before, after)

    def test_missing_source_variable_witness(self):
        before, after = fixtures()
        del before["assessment"]["variables"]["derived-path-variable"]
        with self.assertRaises(ValueError):
            restore_with_original_witness(before, after)

    def test_second_consumer_refused(self):
        before, after = fixtures()
        before["assessment"]["objects"]["other-object"] = {"select": {
            "path": {"value": {"variable": "derived-path-variable"}}}}
        with self.assertRaises(ValueError):
            restore_with_original_witness(before, after)

    def test_extra_inline_marker_refused(self):
        before, after = fixtures()
        after["assessment"]["objects"]["other-object"] = {"select": {
            "path": {"value": {
                "expression": {"literal": "x"},
                "research_inline_source_variable": "other-variable",
            }}}}
        with self.assertRaises(ValueError):
            restore_with_original_witness(before, after)

if __name__ == "__main__":
    unittest.main()
