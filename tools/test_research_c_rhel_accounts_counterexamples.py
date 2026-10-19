#!/usr/bin/env python3
"""#245 Falsification against real RHEL9 source 2-Test/2-Variable quantifiers.

This is a deliberate C *no-go* boundary for oversimplified single
\`every_item\` rewriting. It does NOT claim the old 0.1.0 source is a native
0.4-A file, or establish original scanner equivalence.
"""
from __future__ import annotations

from pathlib import Path
import sys
import unittest
import yaml

sys.path.insert(0,str(Path(__file__).resolve().parent))
from oval_result_truth_tables import evaluate_collected_object_test,aggregate_operator
from research_c_permissions_macro import lower_no_more_permissive_than

SOURCE=Path(__file__).resolve().parents[1]/(
    "research/assessment-simplification/samples/rhel_9/assessments/automated/"
    "niwc.rhel_9.SV-257889.automated.assessment.yaml")

class SourceBackedAccountsNoGo(unittest.TestCase):
    def setUp(self):
        self.a=yaml.safe_load(SOURCE.read_text())["assessment"]
        tests=self.a["tests"]
        self.regular=next(t for t in tests.values() if t["check_existence"]=="any_exist")
        self.root=next(t for t in tests.values() if t["check_existence"]=="at_least_one_exists")

    def test_root_and_non_system_have_different_necessary_existence(self):
        # Both tests check the same permission State but different source
        # collections and different existence truth behavior.
        self.assertEqual(self.regular["states"],self.root["states"])
        self.assertEqual(self.regular["check"],self.root["check"])
        self.assertNotEqual(self.regular["object"],self.root["object"])
        self.assertEqual(self.regular["check_existence"],"any_exist")
        self.assertEqual(self.root["check_existence"],"at_least_one_exists")
        self.assertEqual(len(self.a["variables"]),2)
        self.assertEqual(len(self.a["tests"]),2)

    def test_cannot_collapse_the_source_two_tests_to_one_union_population(self):
        # Real-source quantifiers: non-system file missing is permitted,
        # root file missing is a failure. A global set union of both would
        # find one good regular file and falsely pass.
        s_reg=evaluate_collected_object_test(
            "complete",existence="any_exist",check="all",
            exists=1,has_state=True,item_results=["true"])
        s_root=evaluate_collected_object_test(
            "does not exist",existence="at_least_one_exists",check="all")
        source=aggregate_operator("AND",[s_reg,s_root])
        self.assertEqual(source,"false")
        wrong_merged=evaluate_collected_object_test(
            "complete",existence="at_least_one_exists",check="all",
            exists=1,has_state=True,item_results=["true"])
        self.assertEqual(wrong_merged,"true")
        self.assertNotEqual(source,wrong_merged)

    def test_cannot_change_missing_non_system_file_status_to_required(self):
        # The schema's does-not-exist flag is an independently documented
        # source status, not "complete but zero Items" which has a separate,
        # currently unresolved check/table boundary.
        source=evaluate_collected_object_test(
            "does not exist",existence="any_exist",check="all",has_state=True)
        wrong=evaluate_collected_object_test(
            "does not exist",existence="at_least_one_exists",check="all",has_state=True)
        self.assertEqual(source,"true")
        self.assertEqual(wrong,"false")

    def test_empty_complete_any_exist_and_State_requires_explicit_oracle(self):
        with self.assertRaisesRegex(ValueError,"at least one input"):
            evaluate_collected_object_test(
                "complete",existence="any_exist",check="all",
                exists=0,has_state=True,item_results=[])

    def test_exhaustive_bit_macro_does_not_prove_account_scope(self):
        m=lower_no_more_permissive_than({"no_more_permissive_than":"0740"})
        self.assertEqual(len(m["states"]),8)
        self.assertFalse(m["source_parity_verified"])
        # The original source contains two dynamically scoped selectors,
        # source ObjectComponents, two Variables, and nested filters.
        # Compiling just a bit predicate cannot erase those.
        obj=self.a["objects"]
        self.assertEqual(len(obj),5)
        self.assertTrue(any("variable" in str(v) for v in obj.values()))
        self.assertTrue(any("filters" in v or "set" in v for v in obj.values()))


if __name__=="__main__":
    unittest.main()
