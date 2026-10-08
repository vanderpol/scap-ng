#!/usr/bin/env python3
import json
import tempfile
import unittest
from pathlib import Path
import yaml

from scap_ng_content_compiler import compile_benchmark, readable_member_name, write_bundle, verify_bundle


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(value, sort_keys=False), encoding="utf-8")


class ContentCompilerTests(unittest.TestCase):
    def test_readable_bundle_member_layout_and_path_limit(self):
        self.assertEqual(
            readable_member_name(
                Path("bench/assessments/automated/SV-123.automated.assessment.yaml"),
                "SV-123.automated",
                "assessment",
            ),
            "assessments/automated/SV-123.automated.assessment.json",
        )
        self.assertEqual(
            readable_member_name(
                Path("bench/assessments/manual/SV-123.manual.assessment.yaml"),
                "SV-123.manual",
                "assessment",
            ),
            "assessments/manual/SV-123.manual.assessment.json",
        )
        self.assertEqual(
            readable_member_name(Path("bench/rules/SV-123.rule.yaml"),"SV-123","rule"),
            "rules/SV-123.rule.json",
        )

        long_name="SV-" + ("1234567890" * 30) + ".automated.assessment.yaml"
        shortened=readable_member_name(
            Path("bench/assessments/automated")/long_name,
            "very.long.logical.assessment.id",
            "assessment",
        )
        self.assertLessEqual(len(shortened),160)
        self.assertTrue(shortened.startswith("assessments/automated/"))
        self.assertTrue(shortened.endswith(".json"))


    def test_current_rule_path_compiles_to_logical_assessment_id(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)/"corpus"
            b=root/"example"
            dump(b/"benchmark.yaml",{"benchmark":{"id":"example","version":{"value":"1"},"rules":["R1"],"profiles":[]}})
            dump(b/"assessments"/"automated"/"R1.automated.assessment.yaml",{
                "assessment":{"id":"example.R1.automated","version":1,"assessment_title":None,"mode":"automated","class":"compliance","purpose":"assessment","specification":{"id":"scap-ng.pre-alpha.assessment","version":"0.1.0"},"objects":{},"states":{},"tests":{},"evaluate":{}}
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
            rule_member=index["R1"]["path"]
            rule_doc=json.loads(members[rule_member])
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
                "assessment":{"id":"example.R1.automated","version":1,"assessment_title":None,"mode":"automated","class":"compliance","purpose":"assessment","specification":{"id":"scap-ng.pre-alpha.assessment","version":"0.1.0"},"objects":{},"states":{},"tests":{},"evaluate":{}}
            })
            dump(b/"assessments"/"applicability"/"platform.assessment.yaml",{
                "assessment":{"id":"example.platform.assessment","version":1,"assessment_title":None,"mode":"automated","class":"inventory","purpose":"applicability","specification":{"id":"scap-ng.pre-alpha.assessment","version":"0.1.0"},
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
            app_member=index["example.applicability"]["path"]
            app=json.loads(members[app_member])
            self.assertEqual(
                app["applicability"]["conditions"]["platform.example"]["assessment"],
                "example.platform.assessment",
            )

    def test_logical_id_reference_and_relocated_assessment(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "corpus"
            bench = root / "sample"
            dump(bench / "benchmark.yaml", {"benchmark": {
                "id": "sample", "version": {"value": "1"}, "rules": ["R1"], "profiles": []}})
            assessment = {"assessment": {
                "id": "sample.R1", "version": 1, "assessment_title": None,
                "mode": "automated", "class": "compliance", "purpose": "assessment",
                "specification": {"id": "scap-ng.pre-alpha.assessment", "version": "0.1.0"},
                "objects": {}, "states": {}, "tests": {}, "evaluate": {}}}
            path = bench / "assessments" / "automated" / "original.yaml"
            dump(path, assessment)
            rule = {"rule": {"id": "R1",
                     "assessment_choices": {"automated": {"assessment": "sample.R1"}},
                     "default_assessment_choice": "automated"}}
            dump(bench / "rules" / "R1.rule.yaml", rule)
            _, members, index = compile_benchmark(root, bench)
            r1 = json.loads(members[index["R1"]["path"]])["rule"]
            self.assertEqual(r1["assessment_choices"]["automated"]["assessment"], "sample.R1")
            moved = bench / "assessments" / "automated" / "renamed.yaml"
            path.rename(moved)
            _, members2, index2 = compile_benchmark(root, bench)
            r2 = json.loads(members2[index2["R1"]["path"]])["rule"]
            self.assertEqual(r1, r2)
            dump(root / "shared" / "assessments" / "duplicate.yaml", assessment)
            with self.assertRaisesRegex(ValueError, "ambiguous Assessment identity"):
                compile_benchmark(root, bench)
            rule["rule"]["assessment_choices"]["automated"]["assessment"] = "missing.id"
            dump(bench / "rules" / "R1.rule.yaml", rule)
            with self.assertRaisesRegex(ValueError, "unresolved Assessment identity"):
                compile_benchmark(root, bench)

    def test_benchmark_rule_paths_become_logical_ids(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "corpus"
            bench = root / "example"
            dump(bench / "benchmark.yaml", {"benchmark": {
                "id": "example", "version": {"value": "1"},
                "rules": ["rules/R1.rule.yaml"], "profiles": []}})
            dump(bench / "rules" / "R1.rule.yaml", {"rule": {
                "id": "R1", "assessment_choices": {}, "default_assessment_choice": None}})
            _, members, index = compile_benchmark(root, bench)
            compiled = json.loads(members[index["example"]["path"]])["benchmark"]
            self.assertEqual(compiled["rules"], ["R1"])
            record = {"benchmark": {"id": "example", "version": {"value": "1"},
                                    "rules": ["rules/missing.yaml"], "profiles": []}}
            dump(bench / "benchmark.yaml", record)
            with self.assertRaisesRegex(ValueError, "unresolved Rule source reference"):
                compile_benchmark(root, bench)

    def test_applicability_catalog_logical_identity_and_no_silent_fallback(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "corpus"
            bench = root / "example"
            catalog = {"applicability": {"id": "example.platform", "conditions": {}}}
            dump(bench / "benchmark.yaml", {"benchmark": {
                "id": "example", "version": {"value": "1"},
                "rules": [], "profiles": [],
                "applicability_catalog": "example.platform"}})
            dump(bench / "applicability.yaml", catalog)
            _, members, index = compile_benchmark(root, bench)
            compiled = json.loads(members[index["example"]["path"]])["benchmark"]
            self.assertEqual(compiled["applicability_catalog"], "example.platform")
            dump(bench / "benchmark.yaml", {"benchmark": {
                "id": "example", "version": {"value": "1"},
                "rules": [], "profiles": [], "applicability_catalog": "wrong.id"}})
            with self.assertRaisesRegex(ValueError, "does not resolve to catalog identity"):
                compile_benchmark(root, bench)
            (bench / "applicability.yaml").unlink()
            with self.assertRaisesRegex(ValueError, "unresolved applicability_catalog"):
                compile_benchmark(root, bench)

    def test_runtime_manifest_omits_authoring_source_paths_and_verifies_graph(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)/"corpus"
            b=root/"example"
            dump(b/"benchmark.yaml",{"benchmark":{"id":"example","version":{"value":"1"},"rules":["R1"],"profiles":[]}})
            dump(b/"assessments"/"automated"/"R1.assessment.yaml",{
                "assessment":{"id":"example.R1","version":1,"assessment_title":None,"mode":"automated","class":"compliance","purpose":"assessment","specification":{"id":"scap-ng.pre-alpha.assessment","version":"0.1.0"},"objects":{},"states":{},"tests":{},"evaluate":{}}
            })
            dump(b/"rules"/"R1.rule.yaml",{"rule":{"id":"R1","assessment_choices":{"default":{"assessment":"../assessments/automated/R1.assessment.yaml"}},"default_assessment_choice":"default"}})
            benchmark,members,index=compile_benchmark(root,b)
            out=Path(td)/"example.scapng"
            write_bundle(out,benchmark,members,index,sign_self_signed=False,provenance={"generated_fresh_for_this_run":True})
            result=verify_bundle(out)
            self.assertEqual(result["benchmark_id"],"example")
            import zipfile
            with zipfile.ZipFile(out) as zf:
                manifest=json.loads(zf.read("META-INF/manifest.json"))
            self.assertTrue(all("source" not in row for row in manifest["objects"].values()))
            self.assertTrue(all(len(row["path"]) < 80 for row in manifest["objects"].values()))

    def test_verifier_rejects_unexpected_member(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)/"corpus"
            b=root/"example"
            dump(b/"benchmark.yaml",{"benchmark":{"id":"example","version":{"value":"1"},"rules":[],"profiles":[]}})
            benchmark,members,index=compile_benchmark(root,b)
            out=Path(td)/"example.scapng"
            write_bundle(out,benchmark,members,index,sign_self_signed=False,provenance={"generated_fresh_for_this_run":True})
            import zipfile
            with zipfile.ZipFile(out,"a") as zf:
                info=zipfile.ZipInfo("extra.txt",date_time=(1980,1,1,0,0,0))
                info.compress_type=zipfile.ZIP_DEFLATED
                info.external_attr=0o100644 << 16
                zf.writestr(info,b"x")
            with self.assertRaisesRegex(ValueError,"unexpected ZIP members"):
                verify_bundle(out)


if __name__=="__main__":
    unittest.main()
