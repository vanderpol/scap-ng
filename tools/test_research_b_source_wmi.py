#!/usr/bin/env python3
"""#237: real Win11 WMI Test source shape over offline typed query rows.

These test a fixture evaluator and do NOT execute CIM or certify SCAP 1.4
OVAL WMI item flag/field semantics or source WQL implementation.
"""
from __future__ import annotations

from pathlib import Path
import copy
import sys
import unittest
import yaml

sys.path.insert(0,str(Path(__file__).resolve().parent))
from oval_result_truth_tables import TRUE,FALSE,UNKNOWN,ERROR,NOT_APPLICABLE
from research_b_source_wmi_lowering import lower_state_free_wmi_assessment
from research_b_wmi_query_snapshot import normalize,PROVIDER
from research_b_compiled_ir import encode,decode,evaluate_json

SOURCE=(Path(__file__).resolve().parents[1]/
        "research/requirements-first-language/contract-candidate/corpus/"
        "source-specimens/windows-wmi-query-0-a5018a53e0f6.source.yaml")


class WmiSourceTests(unittest.TestCase):
    def setUp(self):
        self.doc=yaml.safe_load(SOURCE.read_text())
        self.ast=lower_state_free_wmi_assessment(self.doc)
        self.binary=encode(self.doc["assessment"]["id"],self.ast)
        self.using=self.ast["using"]

    def evidence(self,status="complete",rows=None,using=None):
        snapshot={"using":self.using if using is None else using,
                  "status":status,"rows":[] if rows is None else rows}
        return normalize(snapshot,**self.using)

    def verdict(self,evidence):
        return evaluate_json(self.binary,{PROVIDER:evidence}).result

    def test_real_w11_ntfs_source_structure_and_compiled_ir(self):
        a=self.doc["assessment"]
        self.assertEqual(a["id"],"SV-253265.automated")
        self.assertEqual(self.ast["source_test_id"],"local-volumes-use-ntfs-test")
        self.assertEqual(self.ast["existence"],"none_exist")
        self.assertEqual(self.using["namespace"],r"root\cimv2")
        self.assertIn('filesystem!="NTFS"',self.using["query"])
        compiled=decode(self.binary)
        self.assertEqual(compiled["source_kind"],"compiler-compatibility")
        self.assertEqual(compiled["root"],self.ast)

    def test_no_non_ntfs_local_disks_is_true_and_any_bad_disk_is_false(self):
        self.assertEqual(self.verdict(self.evidence()),TRUE)
        self.assertEqual(self.verdict(self.evidence(rows=[{"deviceid":"D:"}])),FALSE)
        self.assertEqual(self.verdict(self.evidence(rows=[
            {"deviceid":"D:"},{"deviceid":"E:"}])),FALSE)

    def test_incomplete_query_cannot_prove_clean_but_a_bad_disk_is_decisive(self):
        self.assertEqual(self.verdict(self.evidence(status="incomplete")),UNKNOWN)
        self.assertEqual(self.verdict(self.evidence(status="incomplete",
                     rows=[{"deviceid":"E:"}])),FALSE)

    def test_query_errors_and_not_applicable_are_preserved(self):
        for status,expected in [("error",ERROR),
                                ("not collected",UNKNOWN),
                                ("not applicable",NOT_APPLICABLE)]:
            with self.subTest(status=status):
                self.assertEqual(self.verdict(self.evidence(status=status)),expected)

    def test_wrong_query_cannot_prove_absence(self):
        other=dict(self.using,query="SELECT deviceid FROM win32_logicaldisk")
        broken=self.evidence(using=other)
        self.assertEqual(broken["status"],"error")
        self.assertEqual(self.verdict(broken),ERROR)
        self.assertEqual(self.verdict({"status":"complete","items":[]}),ERROR)

    def test_unsafe_or_unsupported_source_shapes_rejected(self):
        mutations=[
            lambda a: a["tests"]["local-volumes-use-ntfs-test"].update(
                states=[{"field":"filesystem","operation":"equals","value":"NTFS"}]),
            lambda a: a["tests"]["local-volumes-use-ntfs-test"].update(
                existence="one"),
            lambda a: a["tests"]["local-volumes-use-ntfs-test"]["object"]["collect"].update(
                query="DELETE FROM win32_logicaldisk"),
            lambda a: a["tests"]["local-volumes-use-ntfs-test"]["object"]["collect"].update(
                namespace=r"root\other"),
            lambda a: a.update(variables={"dynamic":{"id":"test"}}),
        ]
        for change in mutations:
            c=copy.deepcopy(self.doc)
            change(c["assessment"])
            if c["assessment"]["tests"]["local-volumes-use-ntfs-test"]["object"]["collect"]["namespace"]!=self.using["namespace"]:
                # A syntactically valid different query identity is allowed
                # in this research; semantics depend on exact acquisition.
                self.assertNotEqual(
                    lower_state_free_wmi_assessment(c)["using"],self.using)
                continue
            with self.subTest(description=c["assessment"].get("variables","other")):
                with self.assertRaises(ValueError):
                    lower_state_free_wmi_assessment(c)

    def test_status_with_items_and_duplicate_ids_are_not_accepted(self):
        rejected=self.evidence(status="error",rows=[{"deviceid":"D:"}])
        self.assertEqual(rejected["status"],"error")
        self.assertEqual(rejected["items"],[])
        evidence=self.evidence(rows=[{"deviceid":"D:"}])
        evidence["items"].append(copy.deepcopy(evidence["items"][0]))
        self.assertEqual(self.verdict(evidence),ERROR)

    def test_malformed_rows_fail_closed(self):
        for row in ({"deviceid":None},{},{"deviceid":[]},{"":1}):
            with self.subTest(row=row):
                self.assertEqual(self.evidence(rows=[row])["status"],"error")


if __name__=="__main__":
    unittest.main()
