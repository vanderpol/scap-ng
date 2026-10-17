#!/usr/bin/env python3
"""#235: B-only source-profile accounting and explicit no-parity guardrails."""
from __future__ import annotations
import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_b_full_corpus_import import import_corpus,digest
from research_b_full_corpus_features import feature_inventory,markdown,test_summary,walk_keys,FORMAT

def rule(rid,aid):
    return {"rule":{"id":rid,"assessment_choices":{
        "automated":{"assessment":aid}},"default_assessment_choice":"automated"}}

def assessment(aid,cap,mode="automated",extras=None):
    tree={"assessment":{"id":aid,"mode":mode,
        "tests":{"check1":{"capability":cap,"existence":"one_or_more",
                           "match":"all","fields":{"flag":{"equals":True}}}}}}
    if extras:
        tree["assessment"].update(extras)
    return tree

def fixtures():
    docs={
     "authoring/rhel_9/rules/r1.yaml":rule("SV-1","shared"),
     "authoring/rhel_9/rules/r2.yaml":rule("SV-2","rhel-only"),
     "authoring/oracle_linux_9/rules/o1.yaml":rule("SV-3","shared"),
     "authoring/shared/assessments/shared.yaml":assessment("shared","linux.partition"),
     "authoring/rhel_9/assessments/only.yaml":assessment("rhel-only","unix.file",
          extras={"evaluate":{"or":[{"test":"check1"}]},"sources":{"users":{"union":[]}}}),
    }
    return docs,{p:digest(d) for p,d in docs.items()}

class InventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        doc,raw=fixtures()
        cls.report,cls.capsules=import_corpus(doc,raw,expected_benchmarks=2)

    def test_every_referenced_assessment_is_accounted_for(self):
        result=feature_inventory(self.report,self.capsules)
        self.assertEqual(result["format"],FORMAT)
        self.assertEqual(result["total_unique_assessments"],2)
        self.assertEqual(result["total_rules"],3)
        self.assertEqual(result["total_assessment_choice_bindings"],3)
        self.assertEqual(result["total_tests_in_unique_assessments"],2)
        self.assertEqual(result["native_verified_execution_count"],0)
        self.assertEqual(result["compatibility_verified_execution_count"],0)
        self.assertFalse(result["source_equivalence_verified"])

    def test_shared_assessment_counts_once_globally_but_again_by_use(self):
        result=feature_inventory(self.report,self.capsules)
        rhel=result["benchmarks"]["rhel_9"]
        oracle=result["benchmarks"]["oracle_linux_9"]
        self.assertEqual(rhel["referenced_unique_assessments"],2)
        self.assertEqual(oracle["referenced_unique_assessments"],1)
        self.assertEqual(rhel["capability_counts"]["linux.partition"],1)
        self.assertEqual(oracle["capability_counts"]["linux.partition"],1)
        self.assertEqual(rhel["capability_counts"]["unix.file"],1)

    def test_only_mapping_keys_contribute_markers_not_descriptions(self):
        self.assertNotIn("union",set(walk_keys({"title":"contains union"})))
        result=feature_inventory(self.report,self.capsules)
        row=result["benchmarks"]["rhel_9"]
        self.assertEqual(row["assessment_key_presence"]["union"],1)
        self.assertEqual(row["assessment_key_presence"]["sources"],1)
        self.assertEqual(row["assessment_key_presence"]["evaluate"],1)
        self.assertEqual(row["marker_example_ids"]["union"],["rhel-only"])

    def test_unknown_test_shape_never_misrepresented_as_verified(self):
        n,cap,status=test_summary({"tests":[{"capability":"a"}, {"nested_test":"b"}]})
        self.assertEqual((n,cap,status),(2,["a"],"capability_missing_or_nested"))
        self.assertEqual(test_summary({"tests":"unparseable"})[2],"tests_shape_unsupported")

    def test_missing_assessment_capsule_rejected(self):
        malformed=dict(self.capsules)
        del malformed["shared"]
        with self.assertRaises(KeyError):
            feature_inventory(self.report,malformed)

    def test_report_does_not_claim_native_conversion(self):
        result=feature_inventory(self.report,self.capsules)
        text=markdown(result)
        self.assertIn("not an A/B comparison",text)
        self.assertIn("No assessed source here is marked native-converted",text)
        self.assertIn("The A/B bake-off remains postponed",text)

if __name__=="__main__":unittest.main()
