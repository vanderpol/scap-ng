#!/usr/bin/env python3
"""#235: real temp-file tests for B textfile regex typed collection.

Only source STRUCTURAL alignment is checked: no SCAP 1.4 OVAL runtime,
not a proof of Python regex / OVAL pattern_match semantics.
"""
from __future__ import annotations
import copy
from pathlib import Path
import sys
import tempfile
import unittest
import yaml
sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_provider_textfile_matches import collect,PROVIDER,VERSION
from research_native_contract_candidate import EXAMPLES,read
from research_native_contract_evaluator import evaluate
from oval_result_truth_tables import TRUE,FALSE,ERROR,UNKNOWN

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"research/requirements-first-language/contract-candidate/corpus/source-specimens/independent-textfilecontent54-0-4c14428014be.source.yaml"

class TextfileFixtureTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/"chrony.conf"
        self.ast=read(EXAMPLES/"10-linux-chrony-cmdport.yaml")["ast"]
        self.using=dict(self.ast["using"],path=str(self.path))
        self.ast=dict(self.ast,using=self.using)
    def scan(self,**extra):
        return collect(**dict(self.using,**extra))
    def result(self,**extra):
        return evaluate(self.ast,{PROVIDER:self.scan(**extra)}).result
    def test_source_scoping_matches_first_class_acquisition_shapewise(self):
        source=yaml.safe_load(SOURCE.read_text())["assessment"]
        tests=list(source["tests"].values())
        self.assertEqual(len(tests),1)
        original=tests[0]
        self.assertEqual(original["capability"],"independent.textfilecontent54")
        self.assertEqual(original["existence"],"one_or_more")
        self.assertEqual(original["match"],"all")
        self.assertNotIn("states",original)
        collected=original["object"]["collect"]
        self.assertEqual((collected["ignore_case"],collected["multiline"],
                          collected["singleline"]),(False,True,False))
        selectors=original["object"]["select"]
        self.assertEqual(selectors["full_path"],{
            "operation":"equals","value":"/etc/chrony.conf"})
        self.assertEqual(selectors["instance"]["operation"],"greater_than_or_equal")
        self.assertEqual(selectors["instance"]["value"],1)
        self.assertEqual(selectors["pattern"]["value"],self.ast["using"]["pattern"])
        self.assertEqual(self.ast["mode"],"some")
        self.assertEqual(self.ast["predicates"],[])
        # Source collection statuses/item_creation etc still unverified.

    def test_one_matching_line_passes_and_provides_identity(self):
        self.path.write_text("# ignored\ncmdport 0\n")
        result=self.scan()
        self.assertEqual(result["status"],"complete")
        self.assertEqual((result["provider"],result["version"]),(PROVIDER,VERSION))
        self.assertEqual(len(result["items"]),1)
        self.assertEqual(result["items"][0]["fields"]["instance"],1)
        self.assertEqual(result["items"][0]["fields"]["match_text"],"cmdport 0")
        self.assertEqual(self.result(),TRUE)

    def test_nonmatching_lines_fail_on_complete_collection(self):
        self.path.write_text("cmdport 1\n# cmdport 0\ncmdport 0 # commentary\n")
        self.assertEqual(self.result(),FALSE)

    def test_multiple_matches_retain_distinct_instances(self):
        self.path.write_text("cmdport 0\n cmdport 0\n")
        observed=self.scan()
        self.assertEqual(observed["status"],"complete")
        self.assertEqual([x["fields"]["instance"] for x in observed["items"]],[1,2])
        self.assertEqual(len(set(x["id"] for x in observed["items"])),2)
        self.assertEqual(self.result(),TRUE)

    def test_missing_file_is_confirmed_empty_and_fails_required_witness(self):
        self.assertEqual(self.scan()["status"],"complete")
        self.assertEqual(self.result(),FALSE)

    def test_partial_file_does_not_pass_from_empty_selection(self):
        self.path.write_text("cmdport 0\n" * 1500)
        observed=self.scan(max_bytes=100)
        self.assertEqual(observed["status"],"incomplete")
        self.assertEqual(observed["items"],[])
        self.assertIn("file_byte_limit",{x["reason"] for x in observed["diagnostics"]})
        self.assertEqual(self.result(max_bytes=100),UNKNOWN)

    def test_match_count_cap_is_explicit_incomplete_even_with_witness(self):
        self.path.write_text("cmdport 0\ncmdport 0\n")
        evidence=self.scan(max_matches=1)
        self.assertEqual(evidence["status"],"incomplete")
        self.assertEqual(len(evidence["items"]),1)
        # Exists witnesses can be decisive even when later matches not collected.
        self.assertEqual(self.result(max_matches=1),TRUE)

    def test_symlink_is_not_silently_followed(self):
        target=Path(self.tmp.name)/"real.conf"
        target.write_text("cmdport 0\n")
        self.path.symlink_to(target)
        evidence=self.scan()
        self.assertEqual(evidence["status"],"incomplete")
        self.assertEqual(self.result(),UNKNOWN)

    def test_unsupported_file_encoding_fails_closed(self):
        self.path.write_bytes(b"cmdport 0\n\xff")
        self.assertEqual(self.scan()["status"],"incomplete")
        self.assertEqual(self.result(),UNKNOWN)

    def test_invalid_regex_and_input_types_rejected(self):
        with self.assertRaisesRegex(ValueError,"invalid acquisition regex"):
            collect(path=str(self.path),pattern="[")
        with self.assertRaisesRegex(ValueError,"must be Boolean"):
            collect(path=str(self.path),pattern="x",ignore_case="false")

    def test_provider_contract_version_and_fields_are_pinned(self):
        p=ROOT/"research/requirements-first-language/providers/linux.textfile_matches.v0.1.yaml"
        definition=yaml.safe_load(p.read_text())
        self.assertEqual((definition["provider"],definition["version"]),(PROVIDER,VERSION))
        self.path.write_text("cmdport 0\n")
        produced=self.scan()
        self.assertEqual(set(definition["collection"]["item_fields"]),
                         set(produced["items"][0]["fields"]))

if __name__=="__main__":unittest.main()
