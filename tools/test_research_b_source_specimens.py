#!/usr/bin/env python3
"""Research #235: protect bounded source specimens from false B conversion."""
import json
from pathlib import Path
import tempfile
import unittest
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_b_full_corpus_import import import_corpus,digest
from research_b_source_specimens import choose,build_manifest,write,FORMAT,MAX_BYTES

def rule(id,assessment):
    return {"rule":{"id":id,"assessment_choices":{
        "automated":{"assessment":assessment}},"default_assessment_choice":"automated"}}

def assessment(id,cap,extra=None):
    doc={"assessment":{"id":id,"mode":"automated",
                        "tests":{"t1":{"capability":cap,
                                       "existence":"one_or_more",
                                       "match":"all"}}}}
    if extra:doc.update(extra)
    return doc

class BSpecimensTests(unittest.TestCase):
    def fixtures(self):
        docs={
        "authoring/rhel_9/rules/r1.yaml":rule("SV-1","linux-source"),
        "authoring/rhel_9/rules/r2.yaml":rule("SV-2","linux-source"),
        "authoring/ms_windows_11/rules/w1.yaml":rule("SV-3","registry-source"),
        "authoring/shared/assessments/linux.yaml":assessment("linux-source","independent.textfilecontent54"),
        "authoring/ms_windows_11/assessments/win.yaml":assessment("registry-source","windows.registry")}
        return import_corpus(docs,{k:digest(v) for k,v in docs.items()},expected_benchmarks=2)

    def test_selected_from_accounted_source_and_bounded(self):
        report,capsules=self.fixtures()
        picks,warnings=choose(report,capsules)
        self.assertEqual(set(picks),{"linux-source","registry-source"})
        for v in picks.values():
            self.assertLessEqual(v["byte_count"],MAX_BYTES)
            self.assertTrue(v["source_raw_sha256"])
            self.assertTrue(v["source_parsed_sha256"])
            self.assertEqual(v["test_count"],1)
        self.assertTrue(warnings)  # remaining families unavailable in toy corpus

    def test_manifest_does_not_claim_converted_content(self):
        report,capsules=self.fixtures()
        picks,warnings=choose(report,capsules)
        manifest=build_manifest(picks,warnings)
        self.assertEqual(manifest["format"],FORMAT)
        self.assertFalse(manifest["source_runtime_equivalence_verified"])
        self.assertEqual(manifest["conversion_status"],"source_specimens_ONLY_no_native_conversion")
        self.assertEqual(len(manifest["specimens"]),2)
        with tempfile.TemporaryDirectory() as path:
            write(picks,manifest,path)
            doc=json.loads((Path(path)/"manifest.json").read_text())
            self.assertEqual(doc["conversion_status"],manifest["conversion_status"])
            text=(Path(path)/"README.md").read_text()
            self.assertIn("not executable 0.4-B",text)
            for v in picks.values():
                self.assertTrue((Path(path)/v["file"]).exists())

    def test_output_filenames_do_not_use_ids_as_unsafe_paths(self):
        report,capsules=self.fixtures()
        picks,_=choose(report,capsules)
        for v in picks.values():
            self.assertNotIn("/",v["file"])
            self.assertTrue(v["file"].endswith(".source.yaml"))

if __name__=="__main__":unittest.main()
