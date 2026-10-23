#!/usr/bin/env python3
"""Canonical generation/guard boundaries, with legacy input compatibility.

Refs #248 #239.
"""
from copy import deepcopy
import json
import unittest
import yaml

from build_v04_canonical_six_stigs import promote, recover, render_authoring
from test_v04_canonical_authoring_guard import check_assessment
from v04_flat_object_authoring import object_nodes


def fixture():
    leaf = {"object_title": None, "full_path": {"equals": "/tmp/input"}}
    return {"assessment": {"id": "cleanup-assessment", "mode": "automated",
        "shared_objects": {"shared-object": {"capability": "unix.file",
            "object_title": "Shared title", "set": {"operation": "union", "operands": [
                {"object": deepcopy(leaf)}]}}},
        "objects": {"named-object": {"capability": "unix.file", "object_title": None}},
        "variables": {"literal-variable": {"expression": {"literal": {
            "object": {"object_title": None}}}}},
        "tests": {"input-test": {"capability": "unix.file",
            "object": {"object_title": None, "set": {"operation": "union", "operands": [
                {"set": {"operation": "intersection", "operands": [
                    {"object": deepcopy(leaf)}, {"object": "shared-object"}]}},
                {"object": {**leaf, "object_title": "Keep this title"}}]}},
            "require": "at_least_one_exists"}},
        "evaluate": {"all": [{"test": "input-test"}, {"not": {"any": [
            {"odd": [{"test": "input-test"}]}]}}]}}}


class AuthoringCleanupTests(unittest.TestCase):
    def test_generation_formats_guard_and_recovery(self):
        source = fixture()
        untouched = deepcopy(source)
        candidate, stats = promote(source)
        a = candidate["assessment"]
        self.assertEqual(stats["evaluate_operators_canonicalized"], 3)
        self.assertEqual(stats["private_null_object_titles_removed"], 3)
        self.assertTrue(check_assessment(a, "promoted"))
        self.assertEqual(a["evaluate"], {"and": [{"test": "input-test"}, {"not": {"or": [
            {"xor": [{"test": "input-test"}]}]}}]})
        for obj, _, _, private in object_nodes(a):
            if private:
                self.assertFalse("object_title" in obj and obj["object_title"] is None)
        self.assertEqual(a["shared_objects"]["shared-object"]["object_title"], "Shared title")
        self.assertIsNone(a["objects"]["named-object"]["object_title"])
        self.assertEqual(a["variables"], source["assessment"]["variables"])
        self.assertEqual(a["tests"]["input-test"]["object"]["set"]["operands"][1]
                         ["object"]["object_title"], "Keep this title")
        for is_yaml in (True, False):
            text = render_authoring(candidate, is_yaml=is_yaml)
            parsed = yaml.safe_load(text) if is_yaml else json.loads(text)
            self.assertEqual(parsed, candidate)
            self.assertTrue(check_assessment(parsed["assessment"], "rendered"))
        self.assertEqual(promote(candidate)[0], candidate)
        recover(candidate, source)
        self.assertEqual(source, untouched)
        bad = deepcopy(candidate)
        bad["assessment"]["tests"]["input-test"]["object"]["object_title"] = "Invented"
        with self.assertRaisesRegex(ValueError, "differs"):
            recover(bad, source)

    def test_guard_rejects_each_legacy_operator_at_nested_scope(self):
        for op in ("all", "any", "odd"):
            a = promote(fixture())[0]["assessment"]
            a["evaluate"] = {"if": {"test": "input-test"}, "then": {"not": {
                op: [{"test": "input-test"}]}}, "else": {"not_applicable": {"reason": "skip"}}}
            with self.subTest(op=op), self.assertRaisesRegex(ValueError, "legacy evaluate"):
                check_assessment(a, "legacy")

    def test_guard_rejects_null_title_at_every_private_object_site(self):
        a = promote(fixture())[0]["assessment"]
        routes = [route for _, _, route, private in object_nodes(a) if private]
        self.assertEqual(len(routes), 4)
        for route in routes:
            mutated = deepcopy(a)
            obj = {"assessment": mutated}
            for key in route:
                obj = obj[key]
            obj["object_title"] = None
            with self.subTest(route=route), self.assertRaisesRegex(ValueError, "object_title"):
                check_assessment(mutated, "null")

    def test_guard_and_generator_reject_malformed_evaluate(self):
        for expr in ({"all": [], "and": []}, {"xor": []},
                     {"if": {"test": "input-test"}, "then": {"test": "input-test"}}):
            source = fixture()
            source["assessment"]["evaluate"] = expr
            with self.subTest(expr=expr):
                with self.assertRaises(ValueError):
                    promote(source)
                with self.assertRaises(ValueError):
                    check_assessment(source["assessment"], "malformed")

    def test_nonautomated_documents_are_unchanged(self):
        for source in ({"rule": {"title": "Manual"}},
                       {"assessment": {"mode": "manual", "procedure": "Review"}}):
            self.assertEqual(promote(source)[0], source)


if __name__ == "__main__":
    unittest.main()
