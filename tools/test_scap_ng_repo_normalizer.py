#!/usr/bin/env python3
import json
import tempfile
import unittest
from pathlib import Path
import yaml

import scap_ng_repo_normalizer as normalizer


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(value, sort_keys=False), encoding="utf-8")


class RepoNormalizerTests(unittest.TestCase):
    def benchmark(self, root, name, rule_id, literal):
        b=root/name
        dump(b/"benchmark.yaml",{"benchmark":{"id":name,"rules":[rule_id],"profiles":[]}})
        assessment={
            "assessment":{
                "id":f"{rule_id}.automated",
                "version":1,
                "assessment_title":f"{rule_id} title",
                "mode":"automated",
                "class":"compliance",
                "purpose":"assessment",
                "collections":{
                    "files":{
                        "collection_title":"files",
                        "capability":"unix.file",
                        "select":{"path":{"operation":"equals","datatype":"string","value":literal}},
                    }
                },
                "tests":{
                    "test-file":{
                        "test_title":"file",
                        "capability":"unix.file",
                        "collection":"files",
                        "assertion":{"existence":"at_least_one_exists","item_quantifier":"all","state":None},
                    }
                },
                "evaluate":{"test":"test-file"},
            }
        }
        dump(b/"assessments"/"automated"/f"{rule_id}.automated.assessment.yaml",assessment)
        dump(b/"rules"/f"{rule_id}.rule.yaml",{
            "rule":{
                "id":rule_id,
                "title":f"Ensure {literal} is configured",
                "discussion":f"The file {literal} must be configured securely.",
                "assessment_choices":{
                    "default":{"assessment":f"../assessments/automated/{rule_id}.automated.assessment.yaml"},
                    "automated":{"assessment":f"../assessments/automated/{rule_id}.automated.assessment.yaml"},
                },
                "default_assessment_choice":"default",
            }
        })

    def test_exact_merge_and_near_duplicate_reporting(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)/"source"
            self.benchmark(root,"a","R1","/etc/example")
            self.benchmark(root,"b","R2","/etc/example")
            self.benchmark(root,"c","R3","/etc/other")
            output=Path(td)/"normalized"
            report_path=Path(td)/"report.json"
            old_argv=__import__("sys").argv
            try:
                __import__("sys").argv=[
                    "normalizer",str(root),"--rewrite","--output-root",str(output),
                    "--report",str(report_path),"--top-near","50",
                ]
                self.assertEqual(normalizer.main(),0)
            finally:
                __import__("sys").argv=old_argv
            report=json.loads(report_path.read_text())
            self.assertEqual(report["summary"]["exact_duplicate_groups"],1)
            self.assertEqual(report["summary"]["duplicate_assessment_definitions_avoided"],1)
            self.assertGreaterEqual(report["summary"]["near_duplicate_review_groups"],1)
            near=report["near_duplicate_review_groups"][0]
            self.assertTrue(near["variant_differences"])
            diff_paths={
                item["path"]
                for variant in near["variant_differences"]
                for item in variant["differences"]
            }
            self.assertIn("$.collections.files.select.path.value",diff_paths)
            shared=list((output/"shared"/"assessments").glob("*.yaml"))
            self.assertEqual(len(shared),1)
            shared_assessment=yaml.safe_load(shared[0].read_text())["assessment"]
            self.assertEqual(shared_assessment["version"],1)
            self.assertNotIn("reuse_provenance",shared_assessment)
            provenance=report["exact_groups"][0]["members"]
            self.assertEqual(len(provenance),2)
            self.assertEqual(
                {row["source_assessment"]["id"] for row in provenance},
                {"R1.automated","R2.automated"},
            )
            rule=yaml.safe_load((output/"a"/"rules"/"R1.rule.yaml").read_text())["rule"]
            self.assertIn("shared/assessments",rule["assessment_choices"]["automated"]["assessment"])
            # The literal-different third Assessment is advisory only, not removed.
            self.assertTrue((output/"c"/"assessments"/"automated"/"R3.automated.assessment.yaml").exists())


    def test_rule_overlap_queue_requires_strong_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            self.benchmark(root,"a","R1","/etc/ssh/sshd_config")
            self.benchmark(root,"b","R2","/etc/ssh/sshd_config")
            self.benchmark(root,"c","R3","/etc/unrelated")
            benches,_=normalizer.collect_corpus(root)
            candidates=normalizer.near_rule_candidates(benches)
            self.assertTrue(candidates)
            top=candidates[0]
            self.assertIn(top["confidence"],{"high","medium"})
            self.assertTrue(top["review_reasons"])
            # Generic STIG phrasing alone should not create an overlap candidate.
            self.assertFalse(any(
                {row["left"]["rule_id"],row["right"]["rule_id"]}=={"R1","R3"}
                for row in candidates
            ))


    def test_default_mode_is_dry_run(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)/"source"
            self.benchmark(root,"a","R1","/etc/example")
            self.benchmark(root,"b","R2","/etc/example")
            report_path=Path(td)/"report.json"
            old_argv=__import__("sys").argv
            try:
                __import__("sys").argv=[
                    "normalizer",str(root),"--report",str(report_path),
                ]
                self.assertEqual(normalizer.main(),0)
            finally:
                __import__("sys").argv=old_argv
            report=json.loads(report_path.read_text())
            self.assertEqual(report["mode"],"dry-run-exact-plan-plus-near-duplicate-review")
            self.assertFalse(report["planned_changes"]["rewrite_requested"])
            self.assertEqual(report["summary"]["rule_files_rewritten"],0)
            self.assertEqual(report["summary"]["local_assessment_files_removed"],0)
            self.assertEqual(report["summary"]["exact_duplicate_groups"],1)
            self.assertFalse((Path(td)/"normalized").exists())

    def test_rewrite_is_idempotent(self):
        with tempfile.TemporaryDirectory() as td:
            source=Path(td)/"source"
            self.benchmark(source,"a","R1","/etc/example")
            self.benchmark(source,"b","R2","/etc/example")
            first=Path(td)/"first"
            second=Path(td)/"second"
            report1=Path(td)/"report1.json"
            report2=Path(td)/"report2.json"
            old_argv=__import__("sys").argv
            try:
                __import__("sys").argv=[
                    "normalizer",str(source),"--rewrite","--output-root",str(first),
                    "--report",str(report1),
                ]
                self.assertEqual(normalizer.main(),0)
                __import__("sys").argv=[
                    "normalizer",str(first),"--rewrite","--output-root",str(second),
                    "--report",str(report2),
                ]
                self.assertEqual(normalizer.main(),0)
            finally:
                __import__("sys").argv=old_argv
            second_report=json.loads(report2.read_text())
            self.assertEqual(second_report["summary"]["exact_duplicate_groups"],0)
            self.assertEqual(second_report["summary"]["duplicate_assessment_definitions_avoided"],0)
            self.assertEqual(second_report["summary"]["rule_files_rewritten"],0)
            self.assertEqual(second_report["summary"]["local_assessment_files_removed"],0)

            def tree_bytes(root):
                return {
                    p.relative_to(root).as_posix(): p.read_bytes()
                    for p in sorted(root.rglob("*"))
                    if p.is_file()
                }
            self.assertEqual(tree_bytes(first),tree_bytes(second))


if __name__=="__main__":
    unittest.main()
