#!/usr/bin/env python3
"""Synthetic wrapper signatures only; no unsupported semantic normalization."""
import copy
import unittest
from audit_v04_synthetic_filter_unions import BLUETOOTH_ID, BLUETOOTH_PATH, candidate, inventory

def bluetooth():
    return {"object_title": "Run Bluetooth", "set": {
        "operator": "union", "operands": [
            {"object": {"object_title": "Run Bluetooth", "capability": "independent.shellcommand",
                        "collect": {"shell": "powershell","command": "Bluetooth"}},
             "filters": [{"include": {"stdout_line": {"case_insensitive_equals": "Bluetooth"}}}]}
        ]}}

class SyntheticWrapperTests(unittest.TestCase):
    def test_exact_converter_shaped_single_filtered_union(self):
        match = candidate(bluetooth())
        self.assertEqual(match["filters"][0].keys(), {"include"})
        self.assertEqual(match["object"]["collect"]["shell"], "powershell")

    def test_fail_closed_for_real_set_or_changed_shape(self):
        basic = bluetooth()
        for mutate in (
            lambda x: x["set"]["operands"].append(copy.deepcopy(x["set"]["operands"][0])),
            lambda x: x["set"].update(operator="difference"),
            lambda x: x.update(extra="must not lose me"),
            lambda x: x["set"]["operands"][0]["object"].update(object_title="different"),
            lambda x: x["set"]["operands"][0].update(extra="do not lose"),
            lambda x: x["set"]["operands"][0].update(filters=[]),
        ):
            obj=copy.deepcopy(basic)
            mutate(obj)
            self.assertIsNone(candidate(obj))

    def test_census_does_not_automatically_rewrite(self):
        obj=bluetooth()
        docs={BLUETOOTH_PATH:{"assessment":{"id":BLUETOOTH_ID,"mode":"automated",
            "tests":{"bluetooth":{"capability":"independent.shellcommand","object":obj}}}}}
        before=copy.deepcopy(docs)
        report=inventory(docs,assert_bluetooth=True)
        self.assertEqual(report["candidate_count"],1)
        self.assertEqual(docs,before)
        self.assertTrue(report["requires_source_oval_provenance_before_bulk_rewrite"])

if __name__=="__main__":
    unittest.main()
