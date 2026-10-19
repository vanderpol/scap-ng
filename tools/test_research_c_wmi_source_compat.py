#!/usr/bin/env python3
"""#245 C 'must: absent' WMI source/differential proof over original Items.

No new collector, scanner, OVAL source parser or normative grammar. Compare
the same normalized, pinned precollected WMI evidence against two separately
implemented research evaluators and independently specified expected values.
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import sys
import unittest
import yaml

sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_c_wmi_source_compat import lower_c_wmi_absence,evaluate_c_wmi_absence
from research_b_source_wmi_lowering import lower_state_free_wmi_assessment
from research_b_wmi_query_snapshot import normalize,PROVIDER
from research_b_compiled_ir import encode,evaluate_json

ROOT=Path(__file__).resolve().parents[1]
AUTHORED=ROOT / ("research/assessment-simplification/compact-authoring-04/"
                "c-short-windows-wmi-ntfs.research.yaml")
SOURCE=ROOT / ("research/requirements-first-language/contract-candidate/corpus/"
               "source-specimens/windows-wmi-query-0-a5018a53e0f6.source.yaml")


class CWindowsWmiAbsenceProof(unittest.TestCase):
    def setUp(self):
        self.source=yaml.safe_load(SOURCE.read_text())
        self.authored=yaml.safe_load(AUTHORED.read_text())
        self.c=lower_c_wmi_absence(self.authored,self.source)
        self.original=lower_state_free_wmi_assessment(self.source)
        self.payload=encode(self.original["source_assessment_id"],self.original)
        self.using=self.original["using"]

    def observe(self,rows=(),status="complete",using=None):
        return normalize({"using":using or self.using,"status":status,
                          "rows":list(rows)},**self.using)

    def compare(self,witness,expected):
        c=evaluate_c_wmi_absence(self.c,witness)
        previous=evaluate_json(self.payload,{PROVIDER:witness}).result
        self.assertEqual(c,expected)
        self.assertEqual(previous,expected)
        return c

    def test_same_capability_and_source_query_without_new_implementation(self):
        self.assertEqual(self.c["compatibility"],self.original)
        self.assertEqual(self.c["compatibility"]["existence"],"none_exist")
        self.assertEqual(self.c["compatibility"]["using"],
                         self.authored["from"]["windows.wmi.query"])
        self.assertFalse(self.c["scanner_executed"])
        self.assertFalse(self.c["source_parity_verified"])

    def test_complete_empty_bad_disks_and_incomplete_unknown(self):
        for witness,expected in (
            (self.observe(),"true"),
            (self.observe([{"deviceid":"D:"}]),"false"),
            (self.observe([{"deviceid":"D:"},{"deviceid":"E:"}]),"false"),
            (self.observe(status="incomplete"),"unknown"),
            (self.observe([{"deviceid":"D:"}],status="incomplete"),"false"),
            (self.observe(status="error"),"error"),
            (self.observe(status="not collected"),"unknown"),
            (self.observe(status="not applicable"),"not_applicable"),
        ):
            with self.subTest(expected=expected,witness=witness):
                self.compare(witness,expected)

    def test_bad_query_or_malformed_rows_do_not_prove_absence(self):
        wrong=dict(self.using,query=self.using["query"]+" WHERE 1=1")
        self.compare(self.observe(using=wrong),"error")
        self.compare(self.observe([{"deviceid":None}]),"error")
        self.assertEqual(evaluate_c_wmi_absence(self.c,None),"unknown")
        self.assertEqual(evaluate_c_wmi_absence(self.c,{}),"error")

    def test_missing_dynamic_source_and_different_wql_rejected(self):
        for mutate in (
            lambda d:d["from"]["windows.wmi.query"].update(
                query="SELECT deviceid FROM win32_logicaldisk"),
            lambda d:d["from"]["windows.wmi.query"].update(
                namespace=r"root\other"),
            lambda d:d.update(must="present"),
            lambda d:d.update(must={"every_item":{"deviceid":"C:"}}),
        ):
            other=deepcopy(self.authored)
            mutate(other)
            with self.subTest(other=other):
                with self.assertRaises(ValueError):
                    lower_c_wmi_absence(other,self.source)

    def test_cannot_claim_same_runtime_data_without_query_fidelity(self):
        # Selection of NON-NTFS rows is a source query, not a shortcut to
        # checking a generic collection of all local disks in the C evaluator.
        simple=deepcopy(self.authored)
        simple["from"]["windows.wmi.query"]["query"]=(
            'SELECT deviceid FROM win32_logicaldisk WHERE drivetype=3')
        with self.assertRaisesRegex(ValueError,"changes original"):
            lower_c_wmi_absence(simple,self.source)


if __name__=="__main__":
    unittest.main()
