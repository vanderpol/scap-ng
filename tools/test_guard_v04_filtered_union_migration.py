#!/usr/bin/env python3
"""0.4.0 regression fixtures: exact Filter migration or fail closed (#248)."""
from copy import deepcopy
import unittest

from guard_v04_filtered_union_migration import compare


PATH = "authoring/ms_windows_11/assessments/applicability/bluetooth.json"


def wrapper():
    return {"object_title": "Check Bluetooth installation", "set": {
        "operator": "union", "operands": [{
            "object": {"object_title": "Check Bluetooth installation",
                       "capability": "independent.shellcommand",
                       "collect": {"command": "Get-PnpDevice", "shell": "powershell"}},
            "filters": [{"include": {"stdout_line": {"case_insensitive_equals": "Bluetooth"}}}],
        }],
    }}


def document(obj=None):
    return {PATH: {"assessment": {
        "id": "bluetooth-assessment", "mode": "automated",
        "tests": {"bluetooth-test": {
            "capability": "independent.shellcommand",
            "object": deepcopy(wrapper() if obj is None else obj),
            "require": {"items": "one_or_more"},
        }},
    }}}


def result(baseline, candidate):
    return compare(baseline, candidate, expected_baseline_candidates=1)


class FilterMigrationGateTests(unittest.TestCase):
    def test_existing_baseline_wrapper_is_accepted_only_unchanged(self):
        report = result(document(), document())
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["unchanged_wrapper_sites"], 1)
        self.assertEqual(report["exact_direct_filter_migrations"], 0)
        self.assertFalse(report["original_oval_semantics_proven"])

    def test_exact_object_local_filter_migration(self):
        spec = wrapper()["set"]["operands"][0]
        obj = deepcopy(spec["object"])
        obj.pop("capability")
        obj["filters"] = deepcopy(spec["filters"])
        report = result(document(), document(obj))
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["current_wrapper_sites"], 0)
        self.assertEqual(report["exact_direct_filter_migrations"], 1)
        self.assertEqual(report["baseline_filter_occurrences"], report["current_filter_occurrences"])

    def test_lost_filter_or_changed_value_fails_closed(self):
        src = wrapper()["set"]["operands"][0]
        no_filter = deepcopy(src["object"])
        no_filter.pop("capability")
        self.assertEqual(result(document(), document(no_filter))["status"], "FAIL")
        changed = deepcopy(wrapper())
        changed["set"]["operands"][0]["filters"][0]["include"]["stdout_line"]["case_insensitive_equals"] = "WiFi"
        report = result(document(), document(changed))
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("Filter" in msg for msg in report["errors"]))

    def test_capability_change_during_migration_fails_closed(self):
        spec = wrapper()["set"]["operands"][0]
        new = deepcopy(spec["object"])
        new.pop("capability")
        new["filters"] = deepcopy(spec["filters"])
        doc = document(new)
        doc[PATH]["assessment"]["tests"]["bluetooth-test"]["capability"] = "windows.registry"
        self.assertEqual(result(document(), doc)["status"], "FAIL")

    def test_new_synthetic_wrapper_is_rejected(self):
        added = document()
        newtest = deepcopy(added[PATH]["assessment"]["tests"]["bluetooth-test"])
        added[PATH]["assessment"]["tests"]["another-test"] = newtest
        report = result(document(), added)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("new singleton" in error for error in report["errors"]))

    def test_real_multi_operand_set_is_not_flagged(self):
        src = document()
        real = {"set": {"operator": "intersection", "operands": [
            {"object": "collection-a-object", "filters": [{"exclude": {"owner_uid": {"equals": 1000}}}]},
            {"object": "collection-b-object", "filters": []},
        ]}}
        src[PATH]["assessment"]["tests"]["another-test"] = {
            "capability": "unix.file", "object": real, "require": {"items": "none"}}
        report = result(src, deepcopy(src))
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["baseline_wrapper_sites"], 1)

    def test_baseline_census_change_is_reported(self):
        with self.assertRaisesRegex(ValueError, "Pinned 0.4.0 baseline changed"):
            compare(document(), document(), expected_baseline_candidates=36)


if __name__ == "__main__":
    unittest.main()
