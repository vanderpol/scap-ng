#!/usr/bin/env python3
"""Adversarial source-coverage fixture tests for 0.4-B research import.

These are synthetic authoring ZIPs, not source SCAP 1.4 conversion tests.
"""
from __future__ import annotations
import io
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile
import yaml
sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_b_full_corpus_import import read_source,import_corpus,digest,verify_in_memory_capsule

def rule(rule_id,aid,manual=None):
    selections={"automated":{"assessment":aid}}
    if manual:
        selections["manual"]={"assessment":manual}
    return {"rule":{"id":rule_id,"title":"fixture "+rule_id,
                    "default_assessment_choice":"automated",
                    "assessment_choices":selections}}

def assessment(aid,mode="automated"):
    return {"assessment":{"id":aid,"mode":mode,
                          "tests":{"known_test":{"capability":"linux.partition",
                                                  "existence":"one_or_more","match":"all"}}}}
class SourceCoverageTests(unittest.TestCase):
    def make_archive(self,entries):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        file=Path(self.tmp.name)/"six.zip"
        with zipfile.ZipFile(file,"w") as z:
            for name,value in entries:
                z.writestr(name,value if isinstance(value,str) else yaml.safe_dump(value,sort_keys=True))
        return file

    def standard(self):
        return [
            ("authoring/rhel_9/rules/one.yaml",rule("SV-1","shared-id","manual-1")),
            ("authoring/rhel_9/rules/two.yaml",rule("SV-2","shared-id")),
            ("authoring/oracle_linux_9/rules/three.yaml",rule("SV-3","shared-id")),
            ("authoring/shared/assessments/shared-id.yaml",assessment("shared-id")),
            ("authoring/rhel_9/assessments/manual/manual-1.yaml",assessment("manual-1","manual")),
        ]

    def test_full_rule_choice_closure_and_shared_identity(self):
        zipfile_path=self.make_archive(self.standard())
        docs,hashes=read_source(zipfile_path)
        manifest,capsules=import_corpus(docs,hashes,expected_benchmarks=2)
        self.assertEqual(manifest["summary"]["rules"],3)
        self.assertEqual(manifest["summary"]["unique_referenced_assessments"],2)
        self.assertEqual(manifest["summary"]["assessment_choice_bindings"],4)
        self.assertEqual(manifest["summary"]["choice:manual"],1)
        self.assertEqual(len(capsules),2)
        self.assertEqual(set(manifest["source_benchmark_names"]),
                         {"rhel_9","oracle_linux_9"})
        self.assertFalse(manifest["source_runtime_equivalence_verified"])
        for capsule in capsules.values():
            self.assertEqual(capsule["source_document"],verify_in_memory_capsule(capsule))
            self.assertFalse(capsule["execution_verified"])
            self.assertFalse(capsule["native_equivalent_verified"])

    def test_missing_shared_assessment_fails_closed(self):
        z=self.make_archive([x for x in self.standard() if "shared-id.yaml" not in x[0]])
        docs,hashes=read_source(z)
        with self.assertRaisesRegex(ValueError,"unresolved Assessment reference"):
            import_corpus(docs,hashes,expected_benchmarks=2)

    def test_duplicate_assessment_id_fails_closed(self):
        rows=self.standard()+[
            ("authoring/oracle_linux_9/assessments/duplicate.yaml",assessment("shared-id"))]
        z=self.make_archive(rows)
        docs,hashes=read_source(z)
        with self.assertRaisesRegex(ValueError,"duplicate Assessment IDs"):
            import_corpus(docs,hashes,expected_benchmarks=2)

    def test_duplicate_rule_within_benchmark_fails_closed(self):
        rows=self.standard()+[("authoring/rhel_9/rules/dup.yaml",rule("SV-1","shared-id"))]
        z=self.make_archive(rows)
        docs,hashes=read_source(z)
        with self.assertRaisesRegex(ValueError,"duplicate Rule ID"):
            import_corpus(docs,hashes,expected_benchmarks=2)

    def test_nonexistent_default_choice_fails_closed(self):
        rows=self.standard()
        rows[0][1]["rule"]["default_assessment_choice"]="unavailable"
        z=self.make_archive(rows)
        docs,hashes=read_source(z)
        with self.assertRaisesRegex(ValueError,"default choice missing"):
            import_corpus(docs,hashes,expected_benchmarks=2)

    def test_misleading_claim_of_executable_capsule_fails_closed(self):
        z=self.make_archive(self.standard())
        docs,hashes=read_source(z)
        _,capsules=import_corpus(docs,hashes,expected_benchmarks=2)
        c=dict(capsules["shared-id"],migration_status="source_equivalent_executable")
        with self.assertRaisesRegex(ValueError,"claims executable"):
            verify_in_memory_capsule(c)

    def test_tampering_with_source_after_import_is_detected(self):
        z=self.make_archive(self.standard())
        docs,hashes=read_source(z)
        _,capsules=import_corpus(docs,hashes,expected_benchmarks=2)
        c=dict(capsules["shared-id"])
        c["source_document"]=assessment("shared-id","manual")
        with self.assertRaisesRegex(ValueError,"parsed source mismatch"):
            verify_in_memory_capsule(c)

    def test_missing_expected_benchmark_gate_fails_closed(self):
        z=self.make_archive(self.standard())
        docs,hashes=read_source(z)
        with self.assertRaisesRegex(ValueError,"expected 6"):
            import_corpus(docs,hashes)

    def test_unsafe_archive_parent_path_rejected(self):
        rows=self.standard()+[("authoring/../../evil.yaml","test: 1\n")]
        z=self.make_archive(rows)
        with self.assertRaisesRegex(ValueError,"unsafe source archive path"):
            read_source(z)

    def test_duplicate_yaml_keys_rejected(self):
        rows=self.standard()+[
            ("authoring/rhel_9/assessments/dup-keys.yaml",
             "assessment:\n  id: other\n  id: overwritten\n  mode: automated\n")]
        z=self.make_archive(rows)
        with self.assertRaisesRegex(ValueError,"duplicate YAML key"):
            read_source(z)

    def test_duplicate_zip_filename_rejected(self):
        rows=self.standard()
        rows.append(rows[0])
        z=self.make_archive(rows)
        with self.assertRaisesRegex(ValueError,"duplicate archive path"):
            read_source(z)

    def test_unreferenced_assessment_does_not_claim_executable(self):
        rows=self.standard()+[
            ("authoring/shared/assessments/unreferenced.yaml",assessment("unused"))]
        z=self.make_archive(rows)
        docs,hashes=read_source(z)
        manifest,capsules=import_corpus(docs,hashes,expected_benchmarks=2)
        self.assertEqual(len(capsules),2)
        self.assertEqual(manifest["summary"]["unique_referenced_assessments"],2)
        self.assertEqual(manifest["summary"]["source_yaml_files"],6)

if __name__=="__main__":unittest.main()
