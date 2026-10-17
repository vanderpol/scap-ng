#!/usr/bin/env python3
"""#235: first source-shaped B Test consumes actual textfile collector Items.

Does NOT prove Python re equivalent to OVAL regex, item_creation, filesystem,
State processing, or the original raw SCAP 1.4 XML semantics.
"""
from __future__ import annotations
import copy
from pathlib import Path
import sys
import tempfile
import unittest
import yaml

sys.path.insert(0,str(Path(__file__).resolve().parent))
from oval_result_truth_tables import TRUE,FALSE,ERROR,UNKNOWN,NOT_APPLICABLE
from research_b_compiled_ir import encode,decode,evaluate_json
from research_b_source_textfile_lowering import lower_state_free_textfile_assessment
from research_native_contract_candidate import EXAMPLES,read
from research_provider_textfile_matches import collect,PROVIDER

SOURCE=(EXAMPLES.parent/"corpus/source-specimens"/
        "independent-textfilecontent54-0-4c14428014be.source.yaml")


class RawItemSourceBridgeTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/"chrony.conf"
        self.doc=yaml.safe_load(SOURCE.read_text())
        self.source=lower_state_free_textfile_assessment(self.doc)
        self.assertEqual(self.source["source_assessment_id"],
                         "ng.shared.etc-chrony-conf-cmdport-option-is-set-to-0")
        self.assertEqual(self.source["source_test_id"],
                         "etc-chrony-conf-cmdport-option-set-0-test")
        self.assertEqual(self.source["using"]["path"],"/etc/chrony.conf")
        self.assertEqual(self.source["provider"],PROVIDER)
        # Only fixture acquisition path is substituted. This is NOT claiming
        # a source converter can silently rewrite the original full_path.
        self.source=copy.deepcopy(self.source)
        self.source["using"]["path"]=str(self.path)
        native=read(EXAMPLES/"10-linux-chrony-cmdport.yaml")
        self.native=copy.deepcopy(native["ast"])
        self.native["using"]["path"]=str(self.path)

    def evidence(self,**limits):
        return collect(**self.source["using"],**limits)

    def result(self,evidence=None):
        if evidence is None:evidence=self.evidence()
        encoded=encode(self.source["source_assessment_id"],self.source)
        decoded=decode(encoded)
        self.assertEqual(decoded["source_kind"],"compiler-compatibility")
        return evaluate_json(encoded,{PROVIDER:evidence}).result

    def native_result(self,evidence):
        return evaluate_json(encode("native-chrony",self.native),
                             {PROVIDER:evidence}).result

    def test_real_complete_collected_items_drive_source_test_truth(self):
        self.path.write_text("cmdport 0\n")
        observed=self.evidence()
        self.assertEqual(observed["status"],"complete")
        self.assertEqual(len(observed["items"]),1)
        self.assertEqual(self.result(observed),TRUE)
        self.assertEqual(self.native_result(observed),TRUE)

        self.path.write_text("cmdport 1\n# cmdport 0\n")
        self.assertEqual(self.result(),FALSE)
        self.path.unlink()
        self.assertEqual(self.result(),FALSE)

    def test_partial_positive_evidence_exposes_real_native_source_semantic_difference(self):
        self.path.write_text("cmdport 0\ncmdport 0\n")
        observed=self.evidence(max_matches=1)
        self.assertEqual(observed["status"],"incomplete")
        self.assertEqual(len(observed["items"]),1)
        # Source generic OVAL Test flag=incomplete, has_state=False:
        # UNKNOWN even with one Item. Native existence has a decisive witness:
        # TRUE. Keep the imported Test a compatibility node until proven.
        self.assertEqual(self.result(observed),UNKNOWN)
        self.assertEqual(self.native_result(observed),TRUE)

    def test_read_error_and_unsupported_symlink_are_not_false_absence(self):
        self.path.write_text("cmdport 0\n")
        target=Path(self.temp.name)/"dest"
        target.write_text("cmdport 0\n")
        self.path.unlink()
        self.path.symlink_to(target)
        self.assertEqual(self.result(),UNKNOWN)
        self.assertEqual(self.result({"status":"error","using":self.source["using"],
                                      "items":[]}),ERROR)
        self.assertEqual(self.result({"status":"not applicable","using":self.source["using"],
                                      "items":[]}),NOT_APPLICABLE)

    def test_query_mismatch_malformed_items_and_duplicates_fail_closed(self):
        self.path.write_text("cmdport 0\n")
        original=self.evidence()
        wrong=copy.deepcopy(original)
        wrong["using"]["path"]="/etc/not-the-file"
        self.assertEqual(self.result(wrong),ERROR)
        wrong=copy.deepcopy(original)
        wrong["items"][0]["fields"]["full_path"]="/etc/different"
        self.assertEqual(self.result(wrong),ERROR)
        wrong=copy.deepcopy(original)
        wrong["items"].append(copy.deepcopy(wrong["items"][0]))
        self.assertEqual(self.result(wrong),ERROR)

    def test_unproven_source_constructs_are_rejected_instead_of_rewritten(self):
        cases=[]
        d=copy.deepcopy(self.doc)
        test=next(iter(d["assessment"]["tests"].values()))
        test["states"]=[{"field":"value","operation":"equals","value":0}]
        cases.append(d)
        d=copy.deepcopy(self.doc)
        next(iter(d["assessment"]["tests"].values()))["match"]="one"
        cases.append(d)
        d=copy.deepcopy(self.doc)
        next(iter(d["assessment"]["tests"].values()))["object"]["collect"]["item_creation"]="never"
        cases.append(d)
        d=copy.deepcopy(self.doc)
        next(iter(d["assessment"]["tests"].values()))["object"]["select"]["instance"]["value"]=2
        cases.append(d)
        d=copy.deepcopy(self.doc)
        d["assessment"]["evaluate"]={"all":[d["assessment"]["evaluate"]]}
        cases.append(d)
        for d in cases:
            with self.subTest(changed=d):
                with self.assertRaises(ValueError):
                    lower_state_free_textfile_assessment(d)

    def test_source_owned_node_is_not_an_authored_B_requirement(self):
        from research_native_contract_candidate import compile_doc
        author={"id":"forbidden","title":"forbidden",
                "require":{"compat_oval_provider_existence":self.source}}
        with self.assertRaises(ValueError):
            compile_doc(author)

if __name__=="__main__":
    unittest.main()
