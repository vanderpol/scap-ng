#!/usr/bin/env python3
import tempfile
import unittest
from pathlib import Path

import yaml

from normalize_0_3_review_surface import normalize_tree


class ReviewSurfaceNormalizationTests(unittest.TestCase):
    def test_vocab_and_naming(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            ap=root/"assessments"/"automated"
            rp=root/"rules"
            ap.mkdir(parents=True)
            rp.mkdir(parents=True)

            old_name="benchmark.rhel_9.SV-1.automated.assessment.yaml"
            (ap/old_name).write_text(yaml.safe_dump({
                "assessment":{
                    "id":"benchmark.rhel_9.SV-1.automated",
                    "mode":"automated",
                    "tests":{
                        "t":{
                            "check_existence":"some",
                            "check":"any",
                            "states_match":"any",
                            "object":{
                                "capability":"unix.file",
                                "select":{
                                    "path":{
                                        "value":"/x",
                                        "datatype":"string",
                                        "operation":"equal",
                                    }
                                },
                                "filesystem":"any",
                            },
                        }
                    },
                }
            },sort_keys=False),encoding="utf-8")
            (rp/"SV-1.rule.yaml").write_text(yaml.safe_dump({
                "rule":{
                    "id":"SV-1",
                    "assessment_choices":{
                        "automated":{
                            "assessment":f"../assessments/automated/{old_name}",
                            "expected_id":"benchmark.rhel_9.SV-1.automated",
                        }
                    },
                }
            },sort_keys=False),encoding="utf-8")

            report=normalize_tree(root)

            candidate=ap/"SV-1.automated.yaml"
            self.assertTrue(candidate.is_file())
            self.assertFalse((ap/old_name).exists())
            doc=yaml.safe_load(candidate.read_text())
            a=doc["assessment"]
            self.assertEqual(a["id"],"SV-1.automated")
            t=a["tests"]["t"]
            self.assertNotIn("check_existence",t)
            self.assertNotIn("check",t)
            self.assertEqual(t["existence"],"one_or_more")
            self.assertEqual(t["match"],"one_or_more")
            self.assertEqual(t["states_match"],"any")
            self.assertEqual(
                t["object"]["select"]["path"]["operation"],
                "equals",
            )
            self.assertEqual(t["object"]["filesystem"],"all")

            rule=yaml.safe_load((rp/"SV-1.rule.yaml").read_text())["rule"]
            choice=rule["assessment_choices"]["automated"]
            self.assertEqual(
                choice["assessment"],
                "../assessments/automated/SV-1.automated.yaml",
            )
            self.assertEqual(choice["expected_id"],"SV-1.automated")
            self.assertEqual(len(report["renames"]),1)

    def test_full_word_comparison_vocabulary(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            p=root/"sample.yaml"
            p.write_text(yaml.safe_dump({
                "x":{
                    "a":{"operation":"equal_ci"},
                    "b":{"operation":"greater_or_equal"},
                    "c":{"operation":"match"},
                    "d":{"operation":"subset"},
                }
            }),encoding="utf-8")
            normalize_tree(root)
            doc=yaml.safe_load(p.read_text())
            self.assertEqual(doc["x"]["a"]["operation"],"case_insensitive_equals")
            self.assertEqual(doc["x"]["b"]["operation"],"greater_than_or_equal")
            self.assertEqual(doc["x"]["c"]["operation"],"pattern_match")
            self.assertEqual(doc["x"]["d"]["operation"],"subset_of")


if __name__=="__main__":
    unittest.main()
