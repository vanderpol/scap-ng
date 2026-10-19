#!/usr/bin/env python3
"""#245 Two real Windows STIG check inputs share ONE C authored Assessment.

The composite is new policy (two distinct original Rules), not a verified
native C scanner, source-faithful rewritten Rule or direct OVAL runtime test.
"""
from __future__ import annotations

from copy import deepcopy
from itertools import product
from pathlib import Path
import sys
import unittest
import yaml

sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_c_composed_assessment import (
    compile_c_composed_assessment,evaluate_c_composed_supplied_results)
from research_c_wmi_source_compat import evaluate_c_wmi_absence
from research_c_registry_boundary import lower_c_registry_exact
from research_b_source_registry_lowering import lower_source_registry_assessment
from research_b_source_registry_evaluator import evaluate_source_registry
from research_b_source_registry_snapshot import normalize as registry_normalize
from research_b_wmi_query_snapshot import normalize as wmi_normalize,PROVIDER as WMI
from v04_a_truth_plan_source_oracle import source_expected_outcome
from research_c_common_evaluation import SIX

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"research/assessment-simplification/compact-authoring-04"
SOURCE=ROOT/"research/requirements-first-language/contract-candidate/corpus/source-specimens"

class ComplexWindowsCombination(unittest.TestCase):
    def setUp(self):
        self.doc=yaml.safe_load((BASE/"c-two-windows-checks.research.yaml").read_text())
        self.wmi=yaml.safe_load((SOURCE/"windows-wmi-query-0-a5018a53e0f6.source.yaml").read_text())
        self.reg=yaml.safe_load((SOURCE/"windows-registry-state-all-0fef40d33c90.source.yaml").read_text())
        self.compiled=compile_c_composed_assessment(
            self.doc,source_documents={"non_ntfs_local_volumes":self.wmi})

    def test_both_collection_legs_and_the_shared_logic_are_structurally_pinned(self):
        self.assertEqual(set(self.compiled["checks"]),{"wdigest","non_ntfs_local_volumes"})
        self.assertEqual(self.compiled["checks"]["wdigest"]["kind"],"native_A_test_pieces")
        self.assertEqual(self.compiled["checks"]["wdigest"]["plan"]["test"]["require"],
                         "at_least_one_exists_and_all_match")
        wmi=self.compiled["checks"]["non_ntfs_local_volumes"]
        self.assertEqual(wmi["kind"],"source_compatibility")
        self.assertEqual(wmi["plan"]["compatibility"]["source_assessment_id"],
                         "SV-253265.automated")
        self.assertEqual(wmi["plan"]["compatibility"]["existence"],"none_exist")
        self.assertEqual(self.compiled["expression"]["source_tree"],
                         {"all":[{"test":"wdigest"},{"test":"non_ntfs_local_volumes"}]})
        self.assertFalse(self.compiled["scanner_executed"])

    def test_all_36_six_state_pairs_against_independent_source_expression_oracle(self):
        for one,two in product(sorted(SIX),repeat=2):
            values={"wdigest":one,"non_ntfs_local_volumes":two}
            with self.subTest(registry=one,wmi=two):
                actual=evaluate_c_composed_supplied_results(self.compiled,checks=values)
                expected=source_expected_outcome(
                    self.compiled["expression"]["source_tree"],values,{})
                self.assertEqual(actual["outcome"],expected)
                self.assertFalse(actual["scanner_executed"])

    def test_two_offline_source_collectors_are_reused_not_rebuilt(self):
        from research_b_source_registry_snapshot import PROVIDER as REG
        reg_ast=lower_source_registry_assessment(self.reg)
        self.assertEqual(reg_ast["source_test_id"],"wdigest-authentication-disabled-test")
        def reg_status(kind,value,status="complete"):
            views={}
            for view in ("32bit","64bit"):
                using={**reg_ast["using"],"view":view}
                row=[] if status!="complete" else [{"value_kind":kind,"raw_value":value}]
                views[view]=registry_normalize(
                    {"query":using,"status":status,"records":row},**using)
            return evaluate_source_registry(reg_ast,{REG:{"views":views}})[0].replace(" ","_")
        wmi=self.compiled["checks"]["non_ntfs_local_volumes"]["plan"]
        def wmi_status(rows=(),status="complete"):
            using=wmi["compatibility"]["using"]
            snapshot=wmi_normalize(
                {"using":using,"status":status,"rows":list(rows)},**using)
            return evaluate_c_wmi_absence(wmi,snapshot)
        scenarios=[
            ("REG_DWORD",0,[],"true"),
            ("REG_DWORD",1,[],"false"),
            ("REG_DWORD",0,[{"deviceid":"D:"}],"false"),
            ("REG_DWORD",1,[{"deviceid":"D:"}],"false"),
        ]
        for kind,value,rows,want in scenarios:
            with self.subTest(value=value,rows=rows):
                leaves={"wdigest":reg_status(kind,value),
                        "non_ntfs_local_volumes":wmi_status(rows)}
                self.assertEqual(
                    evaluate_c_composed_supplied_results(self.compiled,checks=leaves)["outcome"],want)
        leaves={"wdigest":"true","non_ntfs_local_volumes":wmi_status(status="incomplete")}
        self.assertEqual(
            evaluate_c_composed_supplied_results(self.compiled,checks=leaves)["outcome"],"unknown")
        leaves={"wdigest":"false","non_ntfs_local_volumes":wmi_status(status="error")}
        self.assertEqual(
            evaluate_c_composed_supplied_results(self.compiled,checks=leaves)["outcome"],"false")

    def test_fail_closed_on_unreferenced_checks_bad_source_or_undeclared_test(self):
        for altered in (
            lambda d:d["require"].update(every=[{"check":"wdigest"}]),
            lambda d:d["require"].update(every=[{"check":"wmi_nonsense"}]),
            lambda d:d["checks"]["non_ntfs_local_volumes"]["from"]["windows.wmi.query"].update(
                query="SELECT deviceid FROM win32_logicaldisk"),
            lambda d:d["checks"]["wdigest"]["must"]["every_item"].update(value="0"),
            lambda d:d["checks"].update(extra=deepcopy(d["checks"]["wdigest"])),
        ):
            doc=deepcopy(self.doc)
            altered(doc)
            with self.subTest(changed=doc):
                with self.assertRaises(ValueError):
                    compile_c_composed_assessment(
                        doc,source_documents={"non_ntfs_local_volumes":self.wmi})
        with self.assertRaises(ValueError):
            compile_c_composed_assessment(self.doc,source_documents={})
        with self.assertRaises(ValueError):
            evaluate_c_composed_supplied_results(self.compiled,checks={"wdigest":"true"})


if __name__=="__main__":
    unittest.main()
