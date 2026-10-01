#!/usr/bin/env python3
import json
import tempfile
import unittest
from pathlib import Path
import yaml

from scap_ng_content_compiler import compile_benchmark, write_bundle


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(value, sort_keys=False), encoding="utf-8")


class ContentCompilerTests(unittest.TestCase):
    def test_current_rule_path_compiles_to_logical_assessment_id(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)/"corpus"
            b=root/"example"
            dump(b/"benchmark.yaml",{"benchmark":{"id":"example","version":{"value":"1"},"rules":["R1"],"profiles":[]}})
            dump(b/"assessments"/"automated"/"R1.automated.assessment.yaml",{
                "assessment":{"id":"R1.automated","mode":"automated","collections":{},"tests":{},"evaluate":None}
            })
            dump(b/"rules"/"R1.rule.yaml",{
                "rule":{
                    "id":"R1",
                    "assessment_choices":{"automated":{"assessment":"../assessments/automated/R1.automated.assessment.yaml"}},
                    "default_assessment_choice":"automated",
                }
            })
            benchmark,members,index=compile_benchmark(root,b)
            self.assertIn("R1.automated",index)
            rule_doc=json.loads(members["objects/rules/R1.json"])
            self.assertEqual(
                rule_doc["rule"]["assessment_choices"]["automated"]["assessment"],
                "R1.automated",
            )
            out=Path(td)/"example.scapng"
            metrics=write_bundle(
                out,benchmark,members,index,
                sign_self_signed=False,
                provenance={
                    "niwc_source_revision":"test",
                    "scap_ng_revision":"test",
                    "generated_fresh_for_this_run":True,
                },
            )
            self.assertTrue(out.exists())
            self.assertFalse(metrics["signed"])


if __name__=="__main__":
    unittest.main()
