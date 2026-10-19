#!/usr/bin/env python3
"""Refs #245 single authoring frontend compiles direct/shared C to same A core."""
from copy import deepcopy
from itertools import product
import json
from pathlib import Path
import sys
import unittest
import yaml
from jsonschema import Draft202012Validator

sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_c_require_language import parse_c_yaml
from research_c_unified_compiler import (
    compile_c_unified,evaluate_c_unified_supplied_results,
)
from v04_a_truth_plan_source_oracle import source_expected_outcome
from research_c_common_evaluation import SIX

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"research/assessment-simplification/compact-authoring-04"
SPECIMENS=ROOT/"research/requirements-first-language/contract-candidate/corpus/source-specimens"

def sample(name):
    return parse_c_yaml((BASE/name).read_text(encoding="utf-8"))

class CUnifiedCompilerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema=json.loads((ROOT/"schema/v0.4.0/assessment-language.schema.json").read_text())
        cls.validator=Draft202012Validator(cls.schema)

    def test_shared_registry_two_checks_compile_one_native_object(self):
        document=sample("c-shared-wdigest-two-checks.research.yaml")
        before=deepcopy(document)
        plan=compile_c_unified(document)
        self.assertEqual(document,before)
        self.assertEqual(plan["stage"],"C_RESEARCH_UNIFIED_A_COMPILER_NO_SCANNER")
        self.assertEqual(len(plan["shared_objects"]),1)
        self.assertEqual(len(plan["tests"]),2)
        self.assertEqual(plan["authored_check_ids"],["contains_dword","value_disabled"])
        self.assertFalse(plan["scanner_executed"])
        self.assertFalse(plan["runtime_acquisition_sharing_verified"])
        one=list(plan["shared_objects"])[0]
        self.assertTrue(one.endswith("-object"))
        self.assertEqual({t["object"] for t in plan["tests"].values()}, {one})
        self.assertEqual(plan["tests"]["value_disabled"]["require"],
                         "at_least_one_exists_and_all_match")
        self.assertEqual(plan["tests"]["contains_dword"]["require"],
                         "at_least_one_exists_and_some_match")
        self.validator.validate({"assessment":{"tests":plan["tests"]}})

    def test_inline_single_linux_and_dns_use_identical_compiler_boundary(self):
        for name,expected in (
            ("c-short-linux-home.research.yaml","linux.partition"),
            ("c-short-windows-dns-rrl.research.yaml","independent.shellcommand"),
            ("c-short-windows-wdigest.research.yaml","windows.registry"),
        ):
            with self.subTest(name=name):
                doc=sample(name)
                plan=compile_c_unified(doc)
                self.assertEqual(plan["shared_objects"],{})
                self.assertEqual(len(plan["tests"]),1)
                self.assertEqual(plan["tests"]["single_check"]["capability"],expected)
                self.validator.validate({"assessment":{"tests":plan["tests"]}})

    def test_previous_two_windows_check_fixture_compiles_with_pinned_WMI_fallback(self):
        src=yaml.safe_load((SPECIMENS/"windows-wmi-query-0-a5018a53e0f6.source.yaml").read_text())
        plan=compile_c_unified(sample("c-two-windows-checks.research.yaml"),
            source_documents={"non_ntfs_local_volumes":src})
        self.assertEqual(set(plan["checks"]),{"wdigest","non_ntfs_local_volumes"})
        self.assertEqual(plan["checks"]["wdigest"]["kind"],"native_A_test_pieces")
        self.assertEqual(plan["checks"]["non_ntfs_local_volumes"]["kind"],"legacy_source_compat")
        self.assertEqual(len(plan["tests"]),1)
        self.assertFalse(plan["source_parity_verified"])

    def test_focused_six_state_logic_uses_source_expression_table(self):
        plan=compile_c_unified(sample("c-shared-wdigest-two-checks.research.yaml"))
        expr={"all":[{"test":"value_disabled"},{"test":"contains_dword"}]}
        for first,second in product(sorted(SIX),repeat=2):
            leaves={"value_disabled":first,"contains_dword":second}
            expected=source_expected_outcome(expr,leaves,{})
            with self.subTest(pair=(first,second)):
                actual=evaluate_c_unified_supplied_results(plan,checks=leaves)
                self.assertEqual(actual["outcome"],expected)
                self.assertFalse(actual["scanner_executed"])

    def test_document_edits_do_not_mutate_compiler_input(self):
        d=sample("c-shared-wdigest-two-checks.research.yaml")
        before=deepcopy(d)
        compile_c_unified(d)
        self.assertEqual(d,before)

    def test_unknown_observation_and_extra_pinned_source_fail_closed(self):
        d=sample("c-shared-wdigest-two-checks.research.yaml")
        d["checks"]["contains_dword"]["observation"]="missing"
        with self.assertRaisesRegex(ValueError,"unresolved"):
            compile_c_unified(d)
        d=sample("c-shared-wdigest-two-checks.research.yaml")
        with self.assertRaisesRegex(ValueError,"unknown pinned source"):
            compile_c_unified(d,source_documents={"phantom":{}})

    def test_truncating_required_check_is_not_allowed(self):
        d=sample("c-shared-wdigest-two-checks.research.yaml")
        d["require"]["every"].pop()
        with self.assertRaisesRegex(ValueError,"all authored checks"):
            compile_c_unified(d)

    def test_source_mismatch_refused_and_typed_state_preserved(self):
        d=sample("c-shared-wdigest-two-checks.research.yaml")
        d["checks"]["value_disabled"]["must"]["every_item"]["value"]="0"
        with self.assertRaisesRegex(ValueError,"DWORD/QWORD"):
            compile_c_unified(d)
        d=sample("c-shared-wdigest-two-checks.research.yaml")
        d["observations"]["wdigest_setting"]["from"]["windows.registry"]["view"]="32bit"
        with self.assertRaisesRegex(ValueError,"selector fields"):
            compile_c_unified(d)

    def test_legacy_wmi_source_does_not_become_unverified_shared_collection(self):
        d=sample("c-two-windows-checks.research.yaml")
        src=yaml.safe_load((SPECIMENS/"windows-wmi-query-0-a5018a53e0f6.source.yaml").read_text())
        d["observations"]={"disks":{"from":d["checks"]["non_ntfs_local_volumes"].pop("from")}}
        d["checks"]["non_ntfs_local_volumes"]["observation"]="disks"
        with self.assertRaisesRegex(ValueError,"shared WMI compatibility"):
            compile_c_unified(d,source_documents={"non_ntfs_local_volumes":src})

    def test_cross_source_missing_value_not_silent_collection_success(self):
        d=sample("c-shared-wdigest-two-checks.research.yaml")
        d["checks"]["contains_dword"]["must"]={"every_item":{"nonexistent":0}}
        with self.assertRaises(ValueError):
            compile_c_unified(d)

if __name__=="__main__":
    unittest.main()
