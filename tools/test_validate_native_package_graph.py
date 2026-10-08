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

    def test_corpus_level_shared_assessment_reference(self):
        with tempfile.TemporaryDirectory() as td:
            corpus=Path(td)
            package=corpus/"pkg"
            self.build_valid(package)
            shared=corpus/"shared"/"assessments"/"shared.assessment.yaml"
            write(shared, {"assessment":{"id":"shared.auto"}})

            rule_path=package/"rules"/"R1.rule.yaml"
            rule=yaml.safe_load(rule_path.read_text())
            rule["rule"]["assessment_choices"]["default"]["assessment"]="../../shared/assessments/shared.assessment.yaml"
            write(rule_path,rule)

            rows=validate_package(package, reference_root=corpus)
            self.assertEqual(rows,[])

    def test_reference_escape_beyond_corpus_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            corpus=Path(td)/"corpus"
            package=corpus/"pkg"
            self.build_valid(package)
            outside=Path(td)/"outside.assessment.yaml"
            write(outside, {"assessment":{"id":"outside"}})

            rule_path=package/"rules"/"R1.rule.yaml"
            rule=yaml.safe_load(rule_path.read_text())
            rule["rule"]["assessment_choices"]["default"]["assessment"]="../../../outside.assessment.yaml"
            write(rule_path,rule)

            rows=validate_package(package, reference_root=corpus)
            self.assertIn("reference_escape",{r["code"] for r in rows})


    def test_native_logical_ids_resolve_without_author_paths(self):
        with tempfile.TemporaryDirectory() as td:
            corpus = Path(td)
            package = corpus / "pkg"
            self.build_valid(package)
            registry_path = package / "applicability.yaml"
            registry = yaml.safe_load(registry_path.read_text())
            registry["applicability"]["conditions"]["platform.rhel"]["assessment"] = "platform.rhel"
            write(registry_path, registry)
            rule_path = package / "rules/R1.rule.yaml"
            rule = yaml.safe_load(rule_path.read_text())
            rule["rule"]["assessment_choices"]["default"]["assessment"] = "R1.auto"
            write(rule_path, rule)
            self.assertEqual(validate_package(package, reference_root=corpus), [])
            original = package / "assessments/R1.assessment.yaml"
            original.rename(package / "assessments/moved.yaml")
            self.assertEqual(validate_package(package, reference_root=corpus), [])
            write(corpus / "shared/assessments/copy.yaml", {"assessment": {"id": "R1.auto"}})
            errors = validate_package(package, reference_root=corpus)
            self.assertIn("reference_ambiguous", {row["code"] for row in errors})

    def test_logical_id_wrong_type_and_version_are_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.build_valid(root)
            rule_path = root / "rules/R1.rule.yaml"
            rule = yaml.safe_load(rule_path.read_text())
            rule["rule"]["assessment_choices"]["default"] = {
                "assessment": "R1.auto", "expected_version": 8}
            write(rule_path, rule)
            errors = validate_package(root)
            self.assertIn("reference_missing", {row["code"] for row in errors})
            rule["rule"]["assessment_choices"]["default"] = {"assessment": "R1.auto"}
            write(rule_path, rule)
            write(root / "assessments/R1.assessment.yaml", {"rule": {"id": "R1.auto"}})
            errors = validate_package(root)
            self.assertIn("reference_wrong_type", {row["code"] for row in errors})

    def test_missing_assessment_reference(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); self.build_valid(root)
            (root/"assessments/R1.assessment.yaml").unlink()
            rows=validate_package(root)
            self.assertIn("reference_missing",{r["code"] for r in rows})

    def test_partial_group_coverage_is_valid(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); self.build_valid(root)
            benchmark=yaml.safe_load((root/"benchmark.yaml").read_text())
            benchmark["benchmark"]["groups"]=[]
            write(root/"benchmark.yaml",benchmark)
            self.assertEqual(validate_package(root),[])

    def test_duplicate_group_membership_is_detected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); self.build_valid(root)
            benchmark=yaml.safe_load((root/"benchmark.yaml").read_text())
            benchmark["benchmark"]["groups"]=[
                {"id":"g1","rules":["R1"],"groups":[]},
                {"id":"g2","rules":["R1"],"groups":[]},
            ]
            write(root/"benchmark.yaml",benchmark)
            rows=validate_package(root)
            self.assertIn("benchmark_group_membership_duplicate",{r["code"] for r in rows})

    def test_unknown_group_membership_is_detected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); self.build_valid(root)
            benchmark=yaml.safe_load((root/"benchmark.yaml").read_text())
            benchmark["benchmark"]["groups"]=[{"id":"g","rules":["R2"],"groups":[]}]
            write(root/"benchmark.yaml",benchmark)
            rows=validate_package(root)
            self.assertIn("benchmark_group_membership_unknown",{r["code"] for r in rows})

if __name__=="__main__":
    unittest.main()
