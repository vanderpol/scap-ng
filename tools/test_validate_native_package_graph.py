#!/usr/bin/env python3
import tempfile
import unittest
from pathlib import Path
import yaml

from validate_native_package_graph import validate_package


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(value, sort_keys=False), encoding="utf-8")


class NativePackageGraphValidationTests(unittest.TestCase):
    def build_valid(self, root: Path):
        write(root/"benchmark.yaml", {"benchmark":{
            "id":"b","rules":["R1"],"applicability_catalog":"applicability.yaml",
            "platform":{"applicability":{"conditions":["platform.rhel"]}},
            "groups":[{"id":"g","rules":["R1"],"groups":[]}],
        }})
        write(root/"applicability.yaml", {"applicability":{
            "id":"b.applicability",
            "conditions":{"platform.rhel":{"assessment":"assessments/platform.assessment.yaml"}}
        }})
        write(root/"assessments/platform.assessment.yaml", {"assessment":{"id":"platform.rhel"}})
        write(root/"rules/R1.rule.yaml", {"rule":{
            "id":"R1","requires":[],"conflicts":[],"applicability":["platform.rhel"],
            "assessment_choices":{"default":{"assessment":"../assessments/R1.assessment.yaml"}},
            "default_assessment_choice":"default"
        }})
        write(root/"assessments/R1.assessment.yaml", {"assessment":{"id":"R1.auto"}})

    def test_valid_package(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); self.build_valid(root)
            self.assertEqual(validate_package(root),[])

    def test_missing_assessment_reference(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); self.build_valid(root)
            (root/"assessments/R1.assessment.yaml").unlink()
            rows=validate_package(root)
            self.assertIn("reference_missing",{r["code"] for r in rows})

    def test_normalization_broken_group_membership_is_detected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); self.build_valid(root)
            write(root/"benchmark.yaml", {"benchmark":{
                "id":"b","rules":["R1"],"applicability_catalog":"applicability.yaml",
                "platform":{"applicability":{"conditions":["platform.rhel"]}},
                "groups":[{"id":"g","rules":[],"groups":[]}],
            }})
            rows=validate_package(root)
            self.assertIn("benchmark_group_membership_mismatch",{r["code"] for r in rows})

if __name__=="__main__":
    unittest.main()
