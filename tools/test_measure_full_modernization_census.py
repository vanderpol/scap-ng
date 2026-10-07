#!/usr/bin/env python3
import tempfile
import unittest
from pathlib import Path

import yaml

from measure_full_modernization_census import build_report


class FullModernizationCensusTests(unittest.TestCase):
    def write_assessment(self,root,name,assessment):
        path=Path(root)/"assessments"/"automated"/f"{name}.assessment.yaml"
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(yaml.safe_dump({"assessment":assessment},sort_keys=False),encoding="utf-8")
        return path

    def test_single_local_test_becomes_local_simple(self):
        with tempfile.TemporaryDirectory() as td:
            self.write_assessment(td,"one",{
                "id":"benchmark.test.SV-1.automated",
                "version":1,
                "mode":"automated",
                "purpose":"assessment",
                "class":"compliance",
                "objects":{
                    "obj":{"capability":"unix.file","select":{"path":"/tmp/example"}}
                },
                "states":{
                    "state":{"capability":"unix.file","expect":{"owner":"root"}}
                },
                "tests":{
                    "test":{"capability":"unix.file","object":"obj","states":["state"]}
                },
                "evaluate":{"test":"test"},
            })
            report=build_report(Path(td),label="synthetic")
            s=report["summary"]
            self.assertEqual(s["automated_assessments"],1)
            self.assertEqual(s["classification_counts"],{"local_simple":1})
            self.assertEqual(s["modernized_objects"],0)
            self.assertEqual(s["modernized_states"],0)
            self.assertEqual(s["single_test_explicit_root_authoring_opportunities"],1)

    def test_shared_acquisition_is_retained_and_classified_complex(self):
        with tempfile.TemporaryDirectory() as td:
            self.write_assessment(td,"shared",{
                "id":"benchmark.test.SV-2.automated",
                "version":1,
                "mode":"automated",
                "purpose":"assessment",
                "class":"compliance",
                "objects":{
                    "shared":{"capability":"unix.file","select":{"path":"/tmp/example"}}
                },
                "tests":{
                    "one":{"capability":"unix.file","object":"shared"},
                    "two":{"capability":"unix.file","object":"shared"},
                },
                "evaluate":{"all":[{"test":"one"},{"test":"two"}]},
            })
            report=build_report(Path(td),label="synthetic")
            row=report["assessments"][0]
            self.assertEqual(row["classification"],"meaningfully_complex")
            self.assertIn("shared_acquisition",row["residual_reasons"])
            self.assertEqual(row["after"]["objects"],1)


if __name__=="__main__":
    unittest.main()
