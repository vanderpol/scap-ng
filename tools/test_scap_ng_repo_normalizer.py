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
                "specification":{"id":"scap-ng.pre-alpha.assessment","version":"0.1.0"},
                "objects":{
                    "files":{
                        "object_title":"files",
                        "capability":"unix.file",
                        "select":{"path":{"operation":"equals","datatype":"string","value":literal}},
                    }
                },
                "states":{},
                "tests":{
                    "test-file":{
                        "test_title":"file",
                        "capability":"unix.file",
                        "object":"files",
                        "check_existence":"at_least_one_exists",
                        "check":"all",
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
            self.assertEqual(report["stats"]["format"],"scap-ng-normalizer-stats-0.1")
            self.assertEqual(report["stats"]["tool"],"scap_ng_repo_normalizer")
            self.assertEqual(report["stats"]["examined"]["referenced_assessment_instances"],3)
            self.assertEqual(report["stats"]["changed"]["exact_duplicate_groups_promoted"],1)
            self.assertEqual(report["stats"]["changed"]["duplicate_assessment_definitions_avoided"],1)
            self.assertGreaterEqual(report["stats"]["unchanged_or_review"]["near_duplicate_review_groups"],1)
            self.assertEqual(
                report["stats"]["reasons"]["automatic_change_exact_semantic_duplicate_groups"],1
            )
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
            self.assertIn("$.objects.files.select.path.value",diff_paths)
            shared=list((output/"shared"/"assessments").glob("*.yaml"))
            self.assertEqual(len(shared),1)
            self.assertEqual(shared[0].name, "file.assessment.yaml")
            shared_assessment=yaml.safe_load(shared[0].read_text())["assessment"]
            self.assertEqual(shared_assessment["id"], "ng.shared.file")
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


    def test_manual_duplicates_keep_manual_shared_filename(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)/"source"
            for name,rule_id in (("a","R1"),("b","R2")):
                b=root/name
                dump(b/"benchmark.yaml",{"benchmark":{"id":name,"rules":[rule_id],"profiles":[]}})
                dump(b/"assessments"/"manual"/f"{rule_id}.manual.assessment.yaml",{
                    "assessment":{
                        "id":f"{rule_id}.manual",
                        "version":1,
                        "assessment_title":"Manual check",
                        "mode":"manual",
                        "class":"compliance",
                        "purpose":"assessment",
                        "procedure":"Verify the setting manually.",
                        "response":{
                            "type":"compliance",
                            "choices":[
                                {"value":"pass","label":"Pass","outcome":"true"},
                                {"value":"fail","label":"Fail","outcome":"false"},
                            ],
                            "allow_comment":True,
                            "allow_evidence":True,
                        },
                    }
                })
                dump(b/"rules"/f"{rule_id}.rule.yaml",{
                    "rule":{
                        "id":rule_id,
                        "title":"Manual rule",
                        "assessment_choices":{
                            "default":{"assessment":f"../assessments/manual/{rule_id}.manual.assessment.yaml"},
                            "manual":{"assessment":f"../assessments/manual/{rule_id}.manual.assessment.yaml"},
                        },
                        "default_assessment_choice":"default",
                    }
                })

            output=Path(td)/"normalized"
            report=Path(td)/"report.json"
            old_argv=__import__("sys").argv
            try:
                __import__("sys").argv=[
                    "normalizer",str(root),"--rewrite","--output-root",str(output),
                    "--report",str(report),"--advisory","none",
                ]
                self.assertEqual(normalizer.main(),0)
            finally:
                __import__("sys").argv=old_argv

            shared=list((output/"shared"/"assessments").glob("*.yaml"))
            self.assertEqual(len(shared),1)
            self.assertEqual(shared[0].name, "manual-check.manual.assessment.yaml")
            doc=yaml.safe_load(shared[0].read_text())["assessment"]
            self.assertEqual(doc["id"], "ng.shared.manual-check")
            self.assertEqual(doc["mode"],"manual")
            self.assertIn("response",doc)


    def test_applicability_assessments_are_normalized_and_rewritten(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)/"source"
            self.benchmark(root,"a","R1","/etc/a")
            self.benchmark(root,"b","R2","/etc/b")
            for name in ("a","b"):
                b=root/name
                dump(b/"assessments"/"applicability"/"platform.assessment.yaml",{
                    "assessment":{
                        "id":f"{name}.platform",
                        "version":1,
                        "assessment_title":f"{name} platform",
                        "mode":"automated",
                        "class":"inventory",
                        "purpose":"applicability",
                        "specification":{"id":"scap-ng.pre-alpha.assessment","version":"0.1.0"},
                        "objects":{},
                        "states":{},
                        "tests":{},
                        "evaluate":{},
                    }
                })
                dump(b/"applicability.yaml",{
                    "applicability":{
                        "id":f"{name}.applicability",
                        "conditions":{
                            "platform":{
                                "assessment":"assessments/applicability/platform.assessment.yaml"
                            }
                        },
                    }
                })

            output=Path(td)/"normalized"
            report_path=Path(td)/"report.json"
            old_argv=__import__("sys").argv
            try:
                __import__("sys").argv=[
                    "normalizer",str(root),"--rewrite","--output-root",str(output),
                    "--report",str(report_path),"--advisory","none",
                ]
                self.assertEqual(normalizer.main(),0)
            finally:
                __import__("sys").argv=old_argv

            report=json.loads(report_path.read_text())
            self.assertEqual(report["summary"]["applicability_files_rewritten"],2)
            app_members=[
                group for group in report["exact_groups"]
                if any(
                    consumer.get("consumer_kind")=="applicability"
                    for member in group["members"]
                    for consumer in member["consumers"]
                )
            ]
            self.assertEqual(len(app_members),1)
            for name in ("a","b"):
                app=yaml.safe_load((output/name/"applicability.yaml").read_text())["applicability"]
                ref=app["conditions"]["platform"]["assessment"]
                self.assertIn("shared/assessments",ref)
                self.assertFalse(
                    (output/name/"assessments"/"applicability"/"platform.assessment.yaml").exists()
                )

    def test_missing_applicability_assessment_fails_repository_validation(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)/"source"
            self.benchmark(root,"a","R1","/etc/a")
            dump(root/"a"/"applicability.yaml",{
                "applicability":{
                    "id":"a.applicability",
                    "conditions":{
                        "platform":{
                            "assessment":"assessments/applicability/missing.assessment.yaml"
                        }
                    },
                }
            })
            with self.assertRaisesRegex(ValueError,"unresolved reference"):
                normalizer.validate_normalized_repository(root)


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


    def test_cross_benchmark_shared_name_is_platform_neutral(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)/"source"
            self.benchmark(root,"ms_windows_11","R1","/etc/example")
            self.benchmark(root,"ms_windows_server_2025","R2","/etc/example")
            for name,rule_id in (("ms_windows_11","R1"),("ms_windows_server_2025","R2")):
                p=root/name/"assessments"/"automated"/f"{rule_id}.automated.assessment.yaml"
                doc=yaml.safe_load(p.read_text())
                doc["assessment"]["tests"]["test-file"]["test_title"]="WN11-AU-000084 Windows 11 must be configured to audit registry failures"
                dump(p,doc)
            output=Path(td)/"normalized"
            report=Path(td)/"report.json"
            old_argv=__import__("sys").argv
            try:
                __import__("sys").argv=[
                    "normalizer",str(root),"--rewrite","--output-root",str(output),
                    "--report",str(report),"--advisory","none",
                ]
                self.assertEqual(normalizer.main(),0)
            finally:
                __import__("sys").argv=old_argv
            shared=list((output/"shared"/"assessments").glob("*.yaml"))
            self.assertEqual(len(shared),1)
            self.assertEqual(
                shared[0].name,
                "windows-must-be-configured-to-audit-registry-failures.assessment.yaml",
            )
            self.assertNotIn("wn11",shared[0].name)
            self.assertNotIn("windows-11",shared[0].name)

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
            self.assertEqual(report["mode"],"dry-run-exact-plan")
            self.assertEqual(report["advisory_mode"],"all")
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


    def test_failed_validation_does_not_replace_existing_destination(self):
        with tempfile.TemporaryDirectory() as td:
            source=Path(td)/"source"
            self.benchmark(source,"a","R1","/etc/example")
            rule_path=source/"a"/"rules"/"R1.rule.yaml"
            doc=yaml.safe_load(rule_path.read_text())
            doc["rule"]["assessment_choices"]["default"]["assessment"]="../assessments/automated/missing.assessment.yaml"
            doc["rule"]["assessment_choices"]["automated"]["assessment"]="../assessments/automated/missing.assessment.yaml"
            dump(rule_path,doc)

            destination=Path(td)/"normalized"
            destination.mkdir()
            sentinel=destination/"sentinel.txt"
            sentinel.write_text("original destination",encoding="utf-8")
            report=Path(td)/"report.json"
            old_argv=__import__("sys").argv
            try:
                __import__("sys").argv=[
                    "normalizer",str(source),"--rewrite","--output-root",str(destination),
                    "--report",str(report),
                ]
                with self.assertRaises(ValueError):
                    normalizer.main()
            finally:
                __import__("sys").argv=old_argv
            self.assertTrue(sentinel.exists())
            self.assertEqual(sentinel.read_text(encoding="utf-8"),"original destination")


    def test_exact_only_mode_skips_advisory_queues_without_changing_exact_groups(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)/"source"
            self.benchmark(root,"a","R1","/etc/example")
            self.benchmark(root,"b","R2","/etc/example")
            self.benchmark(root,"c","R3","/etc/other")
            report_all=Path(td)/"all.json"
            report_none=Path(td)/"none.json"
            old_argv=__import__("sys").argv
            try:
                __import__("sys").argv=[
                    "normalizer",str(root),"--report",str(report_all),
                    "--advisory","all",
                ]
                self.assertEqual(normalizer.main(),0)
                __import__("sys").argv=[
                    "normalizer",str(root),"--report",str(report_none),
                    "--advisory","none",
                ]
                self.assertEqual(normalizer.main(),0)
            finally:
                __import__("sys").argv=old_argv
            all_report=json.loads(report_all.read_text())
            none_report=json.loads(report_none.read_text())
            self.assertEqual(
                all_report["summary"]["exact_duplicate_groups"],
                none_report["summary"]["exact_duplicate_groups"],
            )
            self.assertEqual(
                all_report["summary"]["duplicate_assessment_definitions_avoided"],
                none_report["summary"]["duplicate_assessment_definitions_avoided"],
            )
            self.assertEqual(none_report["advisory_mode"],"none")
            self.assertEqual(none_report["near_duplicate_review_groups"],[])
            self.assertEqual(none_report["near_duplicate_rule_candidates"],[])


    def test_standalone_change_manifest_matches_report(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)/"source"
            self.benchmark(root,"a","R1","/etc/example")
            self.benchmark(root,"b","R2","/etc/example")
            report_path=Path(td)/"report.json"
            manifest_path=Path(td)/"changes.json"
            old_argv=__import__("sys").argv
            try:
                __import__("sys").argv=[
                    "normalizer",str(root),
                    "--report",str(report_path),
                    "--change-manifest",str(manifest_path),
                    "--advisory","none",
                ]
                self.assertEqual(normalizer.main(),0)
            finally:
                __import__("sys").argv=old_argv
            report=json.loads(report_path.read_text())
            manifest=json.loads(manifest_path.read_text())
            self.assertEqual(report["change_manifest"],manifest)
            self.assertEqual(len(manifest["shared_assessments"]),1)
            self.assertEqual(
                set(manifest["shared_assessments"][0]["sources_replaced"]),
                {
                    "a/assessments/automated/R1.automated.assessment.yaml",
                    "b/assessments/automated/R2.automated.assessment.yaml",
                },
            )


    def test_fingerprint_cache_reuses_unchanged_assessments(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)/"source"
            self.benchmark(root,"a","R1","/etc/example")
            self.benchmark(root,"b","R2","/etc/example")
            cache=Path(td)/"fingerprints.json"
            report1=Path(td)/"first.json"
            report2=Path(td)/"second.json"
            old_argv=__import__("sys").argv
            try:
                __import__("sys").argv=[
                    "normalizer",str(root),"--report",str(report1),
                    "--fingerprint-cache",str(cache),"--advisory","none",
                ]
                self.assertEqual(normalizer.main(),0)
                __import__("sys").argv=[
                    "normalizer",str(root),"--report",str(report2),
                    "--fingerprint-cache",str(cache),"--advisory","none",
                ]
                self.assertEqual(normalizer.main(),0)
            finally:
                __import__("sys").argv=old_argv
            first=json.loads(report1.read_text())
            second=json.loads(report2.read_text())
            self.assertEqual(first["summary"]["fingerprint_cache_hits"],0)
            self.assertEqual(first["summary"]["fingerprint_cache_misses"],2)
            self.assertEqual(second["summary"]["fingerprint_cache_hits"],2)
            self.assertEqual(second["summary"]["fingerprint_cache_misses"],0)
            self.assertEqual(
                first["summary"]["exact_duplicate_groups"],
                second["summary"]["exact_duplicate_groups"],
            )
            self.assertEqual(
                first["summary"]["duplicate_assessment_definitions_avoided"],
                second["summary"]["duplicate_assessment_definitions_avoided"],
            )


if __name__=="__main__":
    unittest.main()
