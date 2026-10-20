#!/usr/bin/env python3
"""Focused positive/negative corpus-style fixtures for official 0.4.0 lint."""
from copy import deepcopy
import unittest

from audit_v04_authoring_patterns import scan, compare


PATH = "authoring/ms_windows_11/assessments/demo.json"


def docs():
    return {PATH: {"assessment": {
        "id": "demo-assessment", "mode": "automated",
        "tests": {"check-test": {
            "capability": "independent.shellcommand",
            "object": {"collect": {"command": "Write-Output Bluetooth"}},
            "require": {"items": "one_or_more"},
        }},
        "evaluate": {"test": "check-test"}
    }}}


def set_object():
    return {
        "object_title": "Collect Bluetooth items",
        "set": {"operator": "union", "operands": [{
            "object": {"object_title": "Collect Bluetooth items",
                       "collect": {"command": "Write-Output Bluetooth"}},
            "filters": [{"include": {"stdout_line": {
                "case_insensitive_equals": "Bluetooth"}}}],
        }]},
    }


class AuthoringPatternsTests(unittest.TestCase):
    def test_simple_leaf_collect_has_no_structural_patterns(self):
        r = scan(docs())
        self.assertEqual(r["documents"], 1)
        self.assertEqual(r["automated_tests"], 1)
        self.assertFalse(r["counts"])
        self.assertFalse(r["original_oval_identity_checked"])

    def test_bluetooth_like_wrapper_is_reported_not_assumed_bad_oval(self):
        old = docs()
        old[PATH]["assessment"]["tests"]["check-test"]["object"] = set_object()
        r = scan(old)
        self.assertEqual(r["counts"]["singleton_set"], 1)
        self.assertEqual(r["counts"]["singleton_set_with_filters"], 1)
        self.assertEqual(r["counts"]["mirrored_singleton_set_object"], 1)
        self.assertEqual(r["counts"].get("identical_consecutive_filters", 0), 0)
        self.assertFalse(r["scanner_runtime_equivalence_checked"])
        new = deepcopy(old)
        inner = set_object()["set"]["operands"][0]
        new[PATH]["assessment"]["tests"]["check-test"]["object"] = {
            **inner["object"], "filters": inner["filters"],
        }
        report = compare(scan(old), scan(new))
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(scan(new)["counts"].get("singleton_set", 0), 0)

    def test_new_set_wrapper_regresses(self):
        old = scan(docs())
        changed = docs()
        changed[PATH]["assessment"]["tests"]["check-test"]["object"] = set_object()
        report = compare(old, scan(changed))
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(report["new_structural_regressions"][0]["pattern"],
                         "mirrored_singleton_set_object")

    def test_genuine_two_operand_set_not_synthetic(self):
        val = docs()
        ob = val[PATH]["assessment"]["tests"]["check-test"]["object"]
        ob.clear()
        ob["set"] = {"operator": "difference", "operands": [
            {"object": "files-object", "filters": []},
            {"object": "excluded-files-object", "filters": []},
        ]}
        r = scan(val)
        self.assertEqual(r["counts"].get("singleton_set", 0), 0)
        self.assertEqual(r["counts"]["empty_set_operand_filters"], 2)

    def test_duplicate_set_operands_and_nested_sets_are_only_candidates(self):
        d = docs()
        obj = d[PATH]["assessment"]["tests"]["check-test"]["object"]
        op = {"object": "same-object", "filters": []}
        obj.clear()
        obj["set"] = {"operator": "union", "operands": [
            deepcopy(op), deepcopy(op)]}
        r = scan(d)
        self.assertEqual(r["counts"]["repeated_identical_set_operand"], 1)
        self.assertEqual(r["counts"].get("singleton_set", 0), 0)
        obj["set"]["operands"] = [{"set": {
            "operator": "union", "operands": [deepcopy(op)]}}]
        r = scan(d)
        self.assertEqual(r["counts"]["nested_singleton_set"], 1)
        self.assertEqual(r["counts"]["singleton_set"], 2)

    def test_boolean_triviality_and_unreferenced_test_inventory(self):
        d = docs()
        a = d[PATH]["assessment"]
        a["tests"]["unused-test"] = deepcopy(a["tests"]["check-test"])
        a["evaluate"] = {"all": [{"all": [{"test": "check-test"}]}]}
        r = scan(d)
        self.assertEqual(r["counts"]["single_child_boolean"], 2)
        self.assertEqual(r["counts"]["same_operator_boolean_nesting"], 1)
        self.assertEqual(r["counts"]["unreferenced_test"], 1)

    def test_identical_filters_and_capability_duplication(self):
        d = docs()
        test = d[PATH]["assessment"]["tests"]["check-test"]
        test["object"]["capability"] = test["capability"]
        filt = {"exclude": {"field": {"equals": "none"}}}
        test["object"]["filters"] = [deepcopy(filt), deepcopy(filt)]
        r = scan(d)
        self.assertEqual(r["counts"]["redundant_inline_capability"], 1)
        self.assertEqual(r["counts"]["identical_consecutive_filters"], 1)

    def test_same_count_moved_to_new_test_is_still_a_regression(self):
        baseline = docs()
        baseline[PATH]["assessment"]["tests"]["check-test"]["object"] = set_object()
        candidate = deepcopy(baseline)
        a = candidate[PATH]["assessment"]
        old = a["tests"]["check-test"]["object"]
        a["tests"]["check-test"]["object"] = {
            "collect": {"command": "Write-Output Bluetooth"}}
        a["tests"]["another-test"] = deepcopy(a["tests"]["check-test"])
        a["tests"]["another-test"]["object"] = deepcopy(old)
        # Compare a stable Test population rather than adding/removing Tests.
        baseline[PATH]["assessment"]["tests"]["another-test"] = deepcopy(
            a["tests"]["check-test"])
        report = compare(scan(baseline), scan(candidate))
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(report["new_structural_regressions"][0]["baseline"], 1)
        self.assertEqual(report["new_structural_regressions"][0]["candidate"], 1)
        self.assertTrue(report["new_structural_regressions"][0]["new_sites"])

    def test_unrelated_scope_change_requires_review(self):
        before = scan(docs())
        after = scan(docs())
        after["automated_tests"] += 1
        with self.assertRaisesRegex(ValueError, "scope changed"):
            compare(before, after)


if __name__ == "__main__":
    unittest.main()
