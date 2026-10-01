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
                    "normalizer",str(root),"--output-root",str(output),
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


if __name__=="__main__":
    unittest.main()
