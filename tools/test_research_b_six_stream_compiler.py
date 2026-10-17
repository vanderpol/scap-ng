#!/usr/bin/env python3
"""#237 source-to-B conversion census, safety and deterministic packaging tests."""
from __future__ import annotations

import copy
from hashlib import sha256
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile
import yaml

sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_b_full_corpus_import import import_corpus, read_source
from research_b_six_stream_compiler import (
    READY_STATUS, STATUS, FORMAT, build_six_stream_report,
    render_markdown, write_research_zip, _lower_assessment,
)
from research_b_compiled_ir import decode, evaluate_json
from oval_result_truth_tables import TRUE, FALSE, UNKNOWN

SOURCE=(Path(__file__).resolve().parents[1] /
        "research/requirements-first-language/contract-candidate/corpus/"
        "source-specimens/independent-textfilecontent54-0-4c14428014be.source.yaml")


def rule(rid, aid, manual=None):
    choices={"automated":{"assessment":aid}}
    if manual:
        choices["manual"]={"assessment":manual}
    return {"rule":{
        "id":rid, "title":"fixture Rule "+rid,
        "assessment_choices":choices,
        "default_assessment_choice":"automated"}}


def manual(aid):
    return {"assessment":{"id":aid,"mode":"manual","procedure":"check manually"}}


def unsupported(aid):
    return {"assessment":{
        "id":aid, "mode":"automated",
        "tests":{"custom":{"capability":"windows.wmi.query"}},
        "evaluate":{"test":"custom"}}}


class SixStreamConversionTests(unittest.TestCase):
    def setUp(self):
        self.source=yaml.safe_load(SOURCE.read_text())
        self.aid=self.source["assessment"]["id"]
        self.docs={
            "authoring/rhel_9/rules/r1.yaml":rule("SV-1",self.aid,"manual-check"),
            "authoring/oracle_linux_9/rules/r2.yaml":rule("SV-2",self.aid),
            "authoring/ms_windows_11/rules/r3.yaml":rule("SV-3","unsupported-wmi"),
            "authoring/shared/assessments/source.yaml":self.source,
            "authoring/shared/assessments/manual.yaml":manual("manual-check"),
            "authoring/ms_windows_11/assessments/automated/wmi.yaml":unsupported("unsupported-wmi")
        }
        self.raw={k:sha256(yaml.safe_dump(v,sort_keys=True).encode()).hexdigest()
                  for k,v in self.docs.items()}
        self.corpus,self.capsules=import_corpus(
            self.docs,self.raw,expected_benchmarks=3)

    def test_all_choice_references_are_classified_not_overcounted(self):
        report,compiled=build_six_stream_report(self.corpus,self.capsules)
        self.assertEqual(report["format"],FORMAT)
        self.assertEqual(report["status"],STATUS)
        self.assertEqual(report["summary"]["rules"],3)
        self.assertEqual(report["summary"]["assessment_choice_bindings"],4)
        self.assertEqual(report["summary"]["referenced_assessments"],3)
        self.assertEqual(report["summary"]["fixture_ir_compiled"],1)
        self.assertEqual(report["summary"]["fully_executable_assessments"],0)
        self.assertEqual(report["summary"]["source_parity_verified_assessments"],0)
        self.assertEqual(report["summary"]["status_counts"][READY_STATUS],1)
        self.assertEqual(report["summary"]["status_counts"]["manual_contract_unimplemented"],1)
        self.assertEqual(report["summary"]["status_counts"]["unsupported_source_semantics"],1)
        self.assertEqual(report["by_stream"]["rhel_9"]["referenced_assessments"],2)
        self.assertEqual(report["by_stream"]["oracle_linux_9"]["referenced_assessments"],1)
        self.assertEqual(report["by_stream"]["ms_windows_11"]["referenced_assessments"],1)
        # Shared Assessment counted once across entire cohort, but once per
        # referencing benchmark. It is NOT 2 distinct "conversions".
        self.assertEqual(len(compiled),1)
        self.assertFalse(report["full_six_stream_conversion_complete"])

    def test_strictly_lowered_fixture_ir_roundtrip_not_scanner_proof(self):
        report,compiled=build_six_stream_report(self.corpus,self.capsules)
        member=next(iter(compiled))
        decoded=decode(compiled[member])
        self.assertEqual(decoded["assessment_id"],self.aid)
        self.assertEqual(decoded["source_kind"],"compiler-compatibility")
        self.assertEqual(decoded["root"]["source_test_id"],
                         "etc-chrony-conf-cmdport-option-set-0-test")
        row=next(a for a in report["assessments"] if a["assessment_id"]==self.aid)
        self.assertEqual(row["research_fixture_ir_member"],member)
        self.assertEqual(row["research_fixture_ir_sha256"],
                         sha256(compiled[member]).hexdigest())
        self.assertFalse(row["source_parity_verified"])
        self.assertFalse(row["scanner_runtime_verified"])

        using=decoded["root"]["using"]
        actual={
            "status":"complete","using":using,
            "items":[{"id":"chrony-1","fields":{
                "full_path":using["path"],"instance":1,"match_text":"cmdport 0"}}]}
        self.assertEqual(evaluate_json(compiled[member],
                {"linux.textfile_matches":actual}).result,TRUE)
        actual["status"]="incomplete"
        self.assertEqual(evaluate_json(compiled[member],
                {"linux.textfile_matches":actual}).result,UNKNOWN)
        actual["status"]="complete"
        actual["items"]=[]
        self.assertEqual(evaluate_json(compiled[member],
                {"linux.textfile_matches":actual}).result,FALSE)

    def test_manual_never_silently_lowered_to_automated(self):
        status,reason,payload=_lower_assessment(self.capsules["manual-check"])
        self.assertEqual(status,"manual_contract_unimplemented")
        self.assertIsNone(payload)

    def test_unsupported_semantics_never_sent_to_scanner(self):
        status,reason,payload=_lower_assessment(self.capsules["unsupported-wmi"])
        self.assertEqual(status,"unsupported_source_semantics")
        self.assertIsNone(payload)
        self.assertTrue(reason)

    def test_source_semantics_change_results_in_explicit_unsupported(self):
        source_capsule=copy.deepcopy(self.capsules[self.aid])
        original=source_capsule["source_document"]["assessment"]
        first=next(iter(original["tests"].values()))
        first["states"]=[{"field":"stdout_line","operation":"equals","value":"cmdport 0"}]
        state,reason,payload=_lower_assessment(source_capsule)
        self.assertEqual(state,"unsupported_source_semantics")
        self.assertIn("State/Variable",reason)
        self.assertIsNone(payload)

    def test_zip_is_repeatable_and_never_pretends_to_be_scapng(self):
        report,compiled=build_six_stream_report(self.corpus,self.capsules)
        with tempfile.TemporaryDirectory() as td:
            a=Path(td)/"first.zip"
            b=Path(td)/"second.zip"
            write_research_zip(a,report,compiled)
            write_research_zip(b,report,compiled)
            self.assertEqual(a.read_bytes(),b.read_bytes())
            with zipfile.ZipFile(a) as z:
                members=z.namelist()
                self.assertEqual(members[0],"RESEARCH-ONLY.txt")
                self.assertIn("conversion-progress.json",members)
                self.assertEqual(len([x for x in members if x.startswith("fixture-ir/")]),1)
                self.assertEqual(len([x for x in members if x.endswith(".yaml")]),0)
                published=json.loads(z.read("conversion-progress.json"))
                self.assertFalse(published["scanner_package"])
                self.assertFalse(published["full_six_stream_conversion_complete"])

    def test_all_ir_members_digest_match_index(self):
        report,compiled=build_six_stream_report(self.corpus,self.capsules)
        index={r["research_fixture_ir_member"]:r["research_fixture_ir_sha256"]
               for r in report["assessments"] if "research_fixture_ir_member" in r}
        self.assertEqual(set(index),set(compiled))
        for p,blob in compiled.items():
            self.assertEqual(sha256(blob).hexdigest(),index[p])

    def test_report_stable_and_never_claims_full_coverage(self):
        report,compiled=build_six_stream_report(self.corpus,self.capsules)
        self.assertEqual(
            json.dumps(report,sort_keys=True),
            json.dumps(build_six_stream_report(self.corpus,self.capsules)[0],
                       sort_keys=True))
        markdown=render_markdown(report)
        self.assertIn("NOT a completed conversion",markdown)
        self.assertIn("ms_windows_11",markdown)
        self.assertIn("Verified executable source-equivalent",markdown)

    def test_broken_rule_to_assessment_closure_fails_closed(self):
        altered=copy.deepcopy(self.corpus)
        altered["rules"][0]["choices"][0]["assessment_id"]="not-found"
        with self.assertRaisesRegex(ValueError,"closure violated"):
            build_six_stream_report(altered,self.capsules)

    def test_does_not_change_source_capsules_or_mark_them_executable(self):
        before=json.dumps(self.capsules,sort_keys=True)
        build_six_stream_report(self.corpus,self.capsules)
        self.assertEqual(json.dumps(self.capsules,sort_keys=True),before)
        self.assertTrue(all(x["migration_status"]=="compatibility_execution_pending"
                            for x in self.capsules.values()))


if __name__=="__main__":
    unittest.main()
