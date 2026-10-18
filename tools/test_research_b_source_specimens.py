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

    def test_picks_real_direct_nested_registry_state_all_specimen(self):
        nested=assessment("registry-nested","windows.registry")
        a=nested["assessment"]
        a["evaluate"]={"test":"t1"}
        t=a["tests"]["t1"]
        t["object"]={"capability":"windows.registry","object_title":None,
                     "select":{"hive":"local_machine",
                               "key":{"operation":"equals","value":"SOFTWARE\\Example"},
                               "name":{"operation":"equals","value":"Setting"}}}
        t["states"]=[{"all":[
            {"field":"type","operation":"equals","value":"dword",
             "existence":"one_or_more","match":"all"},
            {"field":"value","operation":"equals","value":1,
             "existence":"one_or_more","match":"all"},
        ]}]
        small=assessment("registry-small","windows.registry")
        long=assessment("registry-large","windows.registry")
        long["assessment"]["assessment_title"]="extended-source-specimen-"*600
        docs={
            "authoring/ms_windows_11/rules/small.yaml":rule("SV-101","registry-small"),
            "authoring/ms_windows_11/rules/nested.yaml":rule("SV-102","registry-nested"),
            "authoring/ms_windows_11/rules/large.yaml":rule("SV-103","registry-large"),
            "authoring/ms_windows_11/assessments/small.yaml":small,
            "authoring/ms_windows_11/assessments/nested.yaml":nested,
            "authoring/ms_windows_11/assessments/large.yaml":long,
        }
        report,capsules=import_corpus(docs,{k:digest(v) for k,v in docs.items()},
                                       expected_benchmarks=1)
        picks,_=choose(report,capsules)
        self.assertIn("registry-nested",picks)
        selected=picks["registry-nested"]
        self.assertTrue(selected["file"].startswith("windows-registry-state-all-"))
        self.assertIn("windows.registry/nested_state_all",selected["families"])
        self.assertIn("states:",selected["content"])

    def test_platform_specific_apache_and_dns_command_source_samples(self):
        docs={
            "authoring/apache_server_2-4_unix_server/rules/apache.yaml":
                rule("SV-701","apache-command"),
            "authoring/ms_windows_server_dns/rules/dns.yaml":
                rule("SV-702","dns-command"),
            "authoring/apache_server_2-4_unix_server/assessments/apache.yaml":
                assessment("apache-command","independent.shellcommand"),
            "authoring/ms_windows_server_dns/assessments/dns.yaml":
                assessment("dns-command","independent.shellcommand"),
        }
        report,capsules=import_corpus(docs,{k:digest(v) for k,v in docs.items()},
                                       expected_benchmarks=2)
        picks,_=choose(report,capsules)
        self.assertIn("apache-command",picks)
        self.assertIn("dns-command",picks)
        self.assertIn("independent.shellcommand/apache_small",
                      picks["apache-command"]["families"])
        self.assertIn("independent.shellcommand/dns_small",
                      picks["dns-command"]["families"])
        self.assertEqual(picks["apache-command"]["benchmarks"],
                         ["apache_server_2-4_unix_server"])
        self.assertEqual(picks["dns-command"]["benchmarks"],
                         ["ms_windows_server_dns"])

    def test_output_filenames_do_not_use_ids_as_unsafe_paths(self):
        report,capsules=self.fixtures()
        picks,_=choose(report,capsules)
        for v in picks.values():
            self.assertNotIn("/",v["file"])
            self.assertTrue(v["file"].endswith(".source.yaml"))

if __name__=="__main__":unittest.main()
