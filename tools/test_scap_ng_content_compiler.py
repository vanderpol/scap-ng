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
                "assessment":{"id":"example.R1.automated","version":1,"assessment_title":null,"mode":"automated","class":"compliance","purpose":"assessment","specification":{"id":"scap-ng.pre-alpha.assessment","version":"0.1.0"},"objects":{},"states":{},"tests":{},"evaluate":{}}
            })
            dump(b/"rules"/"R1.rule.yaml",{
                "rule":{
                    "id":"R1",
                    "assessment_choices":{"automated":{"assessment":"../assessments/automated/R1.automated.assessment.yaml"}},
                    "default_assessment_choice":"automated",
                }
            })
            benchmark,members,index=compile_benchmark(root,b)
            self.assertIn("example.R1.automated",index)
            rule_doc=json.loads(members["objects/rules/R1.json"])
            self.assertEqual(
                rule_doc["rule"]["assessment_choices"]["automated"]["assessment"],
                "example.R1.automated",
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

    def test_mapped_applicability_conditions_preserve_ids_and_resolve_assessments(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)/"corpus"
            b=root/"example"
            dump(b/"benchmark.yaml",{
                "benchmark":{
                    "id":"example",
                    "version":{"value":"1"},
                    "rules":["R1"],
                    "profiles":[],
                    "applicability_catalog":"applicability.yaml",
                }
            })
            dump(b/"assessments"/"automated"/"R1.automated.assessment.yaml",{
                "assessment":{"id":"example.R1.automated","version":1,"assessment_title":null,"mode":"automated","class":"compliance","purpose":"assessment","specification":{"id":"scap-ng.pre-alpha.assessment","version":"0.1.0"},"objects":{},"states":{},"tests":{},"evaluate":{}}
            })
            dump(b/"assessments"/"applicability"/"platform.assessment.yaml",{
                "assessment":{"id":"example.platform.assessment","version":1,"assessment_title":null,"mode":"automated","class":"inventory","purpose":"applicability","specification":{"id":"scap-ng.pre-alpha.assessment","version":"0.1.0"},
                              "objects":{},"states":{},"tests":{},"evaluate":{}}
            })
            dump(b/"rules"/"R1.rule.yaml",{
                "rule":{
                    "id":"R1",
                    "assessment_choices":{"automated":{"assessment":"../assessments/automated/R1.automated.assessment.yaml"}},
                    "default_assessment_choice":"automated",
                }
            })
            dump(b/"applicability.yaml",{
                "applicability":{
                    "id":"example.applicability",
                    "conditions":{
                        "platform.example":{
                            "assessment":"assessments/applicability/platform.assessment.yaml"
                        }
                    },
                }
            })
            benchmark,members,index=compile_benchmark(root,b)
            self.assertIn("example.platform.assessment",index)
            app=json.loads(members["objects/applicability.json"])
            self.assertEqual(
                app["applicability"]["conditions"]["platform.example"]["assessment"],
                "example.platform.assessment",
            )


if __name__=="__main__":
    unittest.main()
