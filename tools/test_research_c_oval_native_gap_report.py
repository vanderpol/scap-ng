#!/usr/bin/env python3
"""Refs #245 prove exact original Definition inventory and blocker triage."""
import sys
from copy import deepcopy
from pathlib import Path
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_c_oval_native_gap_report import gap_report

def fixture():
    return {"stage":"SOURCE_BACKED_NATIVE_C_SUBSET_NOT_SCANNER_PARITY",
        "A_compatible_Definitions_seen":4,
        "native_C_Definitions":2,
        "source_compatible_not_yet_native_C":2,
        "native_C_converted":[
            {"definition_id":"oval:example:def:1","file":"unix/unix-def_a.xml",
             "C_compilation_stage":"NATIVE_C_FROM_MUST_SOURCE_COMPATIBILITY_PROVED",
             "native_C_compilation_passed":True,"A_projection_equivalence_checked":True},
            {"definition_id":"oval:example:def:2","file":"windows/win-def_b.xml",
             "C_compilation_stage":"NATIVE_C_FROM_MUST_SOURCE_COMPATIBILITY_PROVED",
             "native_C_compilation_passed":True,"A_projection_equivalence_checked":True}],
        "unsupported":[
            {"definition_id":"oval:example:def:3","file":"unix/unix-def_c.xml",
             "reason":"OBJECT_ADVANCED_OR_UNREVIEWED_METADATA"},
            {"definition_id":"oval:example:def:4","file":"linux/linux-def_d.xml",
             "reason":"MULTI_TEST: OBJECT_ADVANCED_OR_UNREVIEWED_METADATA"}]}

class NativeCOriginalGapTests(unittest.TestCase):
    def test_report_counts_every_definition_once_and_links_original(self):
        r=gap_report(fixture(),min_expected_total=4)
        self.assertEqual((r["converted"],r["unsupported"]),(2,2))
        self.assertEqual(r["categories"],{"OBJECT_ADVANCED_OR_UNREVIEWED_METADATA":1,
                                          "MULTI_TEST":1})
        self.assertEqual(r["selected_multi_test_categories"],
                         {"SELECTED_ROUTE_NOT_ATTEMPTED":1})
        self.assertEqual(r["distinct_multi_test_categories"],
                         {"DISTINCT_ROUTE_NOT_ATTEMPTED":1})
        self.assertEqual(r["native_stages"],
                         {"NATIVE_C_FROM_MUST_SOURCE_COMPATIBILITY_PROVED":2})
        self.assertIn("original-oval",r["markdown"].lower().replace(" ","-"))
        self.assertIn("OVAL-Community/SCAP-Self-Assertion",r["markdown"])
        self.assertIn("unix/unix-def_c.xml",r["markdown"])
        self.assertIn("not an exhaustive",r["markdown"].lower())

    def test_multi_test_nested_selected_blockers_are_not_double_counted(self):
        m=fixture()
        m["unsupported"][1]["reason"]=(
            "MULTI_TEST: SOURCE_OBJECTS_NOT_SINGLETON; "
            "SELECTED: SHARED_SELECTED_SOURCE_INVENTORY_UNSUPPORTED")
        report=gap_report(m)
        self.assertEqual(report["categories"]["MULTI_TEST"],1)
        self.assertEqual(report["selected_multi_test_categories"],{
            "SHARED_SELECTED_SOURCE_INVENTORY_UNSUPPORTED":1})
        self.assertIn("Selected multi-Test blocker",report["markdown"])
        self.assertEqual(report["distinct_multi_test_categories"],{
            "DISTINCT_ROUTE_NOT_ATTEMPTED":1})

    def test_specific_distinct_blockers_not_double_counted(self):
        m=fixture()
        m["unsupported"][1]["reason"]=(
            "MULTI_TEST: SOURCE_OBJECTS_NOT_SINGLETON; "
            "SELECTED: SHARED_SELECTED_SOURCE_INVENTORY_UNSUPPORTED; "
            "DISTINCT: STATE_FIELD_CARDINALITY_COMPLEX")
        r=gap_report(m,min_expected_total=4)
        self.assertEqual(r["categories"]["MULTI_TEST"],1)
        self.assertEqual(r["distinct_multi_test_categories"],{
            "STATE_FIELD_CARDINALITY_COMPLEX":1})
        self.assertIn("linux/linux-def_d.xml",r["markdown"])
        self.assertIn("Multi-Test distinct-collection final blocker",r["markdown"])
        self.assertEqual(sum(r["distinct_multi_test_categories"].values()),
                         r["categories"]["MULTI_TEST"])

    def test_missing_source_definition_and_double_count_fail(self):
        m=fixture()
        m["unsupported"].pop()
        with self.assertRaisesRegex(ValueError,"coverage mismatch"):
            gap_report(m)
        m=fixture()
        m["unsupported"][0]["definition_id"]="oval:example:def:1"
        m["unsupported"][0]["file"]="unix/unix-def_a.xml"
        with self.assertRaisesRegex(ValueError,"more than once"):
            gap_report(m)

    def test_rejection_without_reason_is_not_counted_as_compatible(self):
        m=fixture()
        m["unsupported"][0].pop("reason")
        with self.assertRaisesRegex(ValueError,"without explicit reason"):
            gap_report(m)

    def test_untrusted_or_renamed_source_rejected(self):
        m=fixture()
        m["stage"]="OVAL_TESTS_ALL_CONVERTED"
        with self.assertRaisesRegex(ValueError,"untrusted"):
            gap_report(m)
        m=fixture()
        m["unsupported"][0]["file"]="../untrusted.xml"
        with self.assertRaisesRegex(ValueError,"unverifiable"):
            gap_report(m)
        with self.assertRaisesRegex(ValueError,"pinned baseline"):
            gap_report(fixture(),min_expected_total=162)

    def test_conversion_without_source_compiler_proof_is_not_counted(self):
        m=fixture()
        m["native_C_converted"][0]["native_C_compilation_passed"]=False
        with self.assertRaisesRegex(ValueError,"lacks checked stage"):
            gap_report(m)

    def test_all_compatible_no_unsupported_is_a_valid_future_result(self):
        m=fixture()
        for item in m["unsupported"]:
            item.update({"C_compilation_stage":"NATIVE_C_FROM_MUST_SOURCE_COMPATIBILITY_PROVED",
                         "native_C_compilation_passed":True,
                         "A_projection_equivalence_checked":True})
        m["native_C_converted"].extend(m["unsupported"])
        m["unsupported"]=[]
        m["native_C_Definitions"]=4
        m["source_compatible_not_yet_native_C"]=0
        out=gap_report(m)
        self.assertEqual((out["converted"],out["unsupported"]),(4,0))
        self.assertEqual(out["categories"],{})

if __name__=="__main__":
    unittest.main()
