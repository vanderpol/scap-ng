#!/usr/bin/env python3
"""Independent YAML/JSON source Filter inverse gate regression fixtures (#248)."""
from copy import deepcopy
import unittest

from guard_v04_additional_source_filters import compare
from migrate_v04_additional_source_filters import migrate
from test_migrate_v04_additional_source_filters import doc, row


class SourceFilterInverseGateTests(unittest.TestCase):
    def setup_documents(self):
        prior={}
        current={}
        proof={}
        for i in range(19):
            path=f"authoring/ms_windows_11/assessments/automated/SV-{250000+i}.json"
            src=doc()
            provenance=row()
            provenance["path"]=path
            proof[(path,"bluetooth-installation-test")]=provenance
            candidate,_=migrate(src,path,proof)
            prior[path]=src
            current[path.removesuffix(".json")+".yaml"]=candidate
        return prior,current,proof

    def test_all_19_exactly_reversed_across_both_formats(self):
        prior,current,proof=self.setup_documents()
        result=compare(prior,current,proof)
        self.assertEqual(result["status"],"PASS")
        self.assertEqual(result["changed_documents"],19)
        self.assertEqual(result["source_test_linked_filter_rewrites"],19)
        self.assertFalse(result["scanner_runtime_parity"])

    def test_any_filter_predicate_loss_is_a_ci_failure(self):
        prior,current,proof=self.setup_documents()
        path=sorted(current)[0]
        item=current[path]["assessment"]["tests"]["bluetooth-installation-test"]["object"]
        item["filters"][0]["include"]["stdout_line"]["case_insensitive_equals"]="WiFi"
        with self.assertRaisesRegex(ValueError,"unexpected Filter rewrite"):
            compare(prior,current,proof)

    def test_duplicate_logical_path_cross_format_is_rejected(self):
        prior,current,proof=self.setup_documents()
        path=sorted(prior)[0]
        prior[path.removesuffix(".json")+".yaml"]=deepcopy(prior[path])
        with self.assertRaisesRegex(ValueError,"Duplicate logical"):
            compare(prior,current,proof)


if __name__=="__main__":
    unittest.main()
