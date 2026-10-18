#!/usr/bin/env python3
"""#232/#239: evidence-only A Benchmark spec declaration migration tests."""
from copy import deepcopy
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from zipfile import ZipFile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_v04_a_benchmark_choice_version_closure import pack, SPEC
from v04_a_benchmark_spec_migration_preview import build_preview, main
from v04_a_benchmark_choice_version_closure import inspect_edges
from v04_a_authoring_graph_index import graph_index


class PreviewTests(unittest.TestCase):
    def test_migrates_only_benchmark_declarations(self):
        docs = pack()
        original = deepcopy(docs)
        report, stage = build_preview(docs)
        self.assertEqual(docs, original, "source documents changed")
        self.assertEqual(report["status"], "RESEARCH_CANDIDATE_NOT_APPROVED")
        self.assertTrue(report["normative_approval_required"])
        self.assertFalse(report["allowed_to_compile"])
        self.assertEqual(report["source_incompatible_edges"], 1)
        self.assertEqual(report["candidate_incompatible_edges"], 0)
        self.assertEqual(len(report["benchmark_changes"]), 1)
        change = report["benchmark_changes"][0]
        self.assertEqual(change["existing_specs"], [{"id": SPEC, "version": "0.3.0"}])
        self.assertEqual(change["reachable_automated_specs"], [{"id": SPEC, "version": "0.4.0"}])
        self.assertEqual(len(change["add_specs"]), 1)
        self.assertEqual(len(change["drop_specs"]), 1)
        bench_path = change["path"]
        self.assertEqual(stage[bench_path]["benchmark"]["assessment_specifications"], [
            {"id": SPEC, "version": "0.4.0"}])
        for path in original:
            if path != bench_path:
                self.assertEqual(stage[path], original[path])
        self.assertEqual(report["source_rule_choice_counts"]["choice_links"], 2)
        self.assertEqual(report["proposed_rule_choice_counts"]["choice_links"], 2)

    def test_existing_compatible_source_is_noop(self):
        report, stage = build_preview(pack(old_benchmark=False))
        self.assertEqual(report["source_incompatible_edges"], 0)
        self.assertEqual(report["candidate_incompatible_edges"], 0)
        self.assertEqual(report["source_graph_sha256"], report["proposed_graph_sha256"])
        self.assertEqual(report["benchmark_changes"][0]["add_specs"], [])
        self.assertEqual(report["benchmark_changes"][0]["drop_specs"], [])

    def test_two_benchmarks_do_not_conflate_specs(self):
        report, stage = build_preview(pack(two_benchmarks=True))
        rows = {row["benchmark_id"]: row for row in report["benchmark_changes"]}
        self.assertEqual(len(rows), 2)
        self.assertEqual(len(rows["ng.rhel_9"]["add_specs"]), 1)
        self.assertEqual(len(rows["ng.win11"]["add_specs"]), 0)
        self.assertEqual(inspect_edges(stage)["counts"]["choice_links"], 4)

    def test_changed_rule_choice_does_not_become_a_valid_proposal(self):
        d = pack()
        d["authoring/rhel_9/rules/SV-TEST.rule.json"]["rule"][
            "assessment_choices"]["automated"]["assessment"] = "missing"
        with self.assertRaisesRegex(ValueError, "unresolved Assessment"):
            build_preview(d)

    def test_no_auto_rule_choices_blocks_unjustified_migration(self):
        d = pack()
        d["authoring/rhel_9/rules/SV-TEST.rule.json"]["rule"][
            "assessment_choices"] = {"manual": {"assessment": "ng.shared.manual"}}
        d["authoring/rhel_9/rules/SV-TEST.rule.json"]["rule"][
            "default_assessment_choice"] = "manual"
        with self.assertRaisesRegex(ValueError, "no automated Assessment choices"):
            build_preview(d)

    def test_reject_duplicate_identity(self):
        d = pack()
        d["authoring/extra/assessments/duplicate.json"] = deepcopy(
            d["authoring/shared/assessments/ng.shared.auto.json"])
        with self.assertRaisesRegex(ValueError, "duplicate Assessment"):
            build_preview(d)

    def test_manual_choices_remain_independent_of_external_spec(self):
        report, staged = build_preview(pack())
        self.assertEqual(report["proposed_rule_choice_counts"]["manual_choice_links"], 1)
        self.assertEqual(staged["authoring/shared/assessments/ng.shared.manual.json"]["assessment"]["mode"],
                         "manual")
        self.assertNotIn("specification", staged["authoring/shared/assessments/ng.shared.manual.json"]["assessment"])

    def test_no_unrecorded_changes_on_complex_benchmark(self):
        d = pack()
        d["authoring/rhel_9/benchmark.rhel_9.json"]["benchmark"]["metadata"] = {
            "source": "preserve", "author": "source-owner", "version": 29}
        report, staged = build_preview(d)
        old = d["authoring/rhel_9/benchmark.rhel_9.json"]["benchmark"]
        new = staged["authoring/rhel_9/benchmark.rhel_9.json"]["benchmark"]
        for name in old:
            if name != "assessment_specifications":
                self.assertEqual(old[name], new[name])

    def test_graph_digest_changes_if_versions_change(self):
        d = pack()
        report, stage = build_preview(d)
        self.assertNotEqual(report["source_graph_sha256"], report["proposed_graph_sha256"])
        self.assertEqual(report["proposed_graph_sha256"], graph_index(stage)["graph_sha256"])

    def test_cli_compare_yaml_json_and_report(self):
        import yaml
        with TemporaryDirectory() as folder:
            jpath, ypath = (Path(folder) / (x+".zip") for x in ("json", "yaml"))
            original = pack()
            with ZipFile(jpath, "w") as z:
                for path, doc in original.items():
                    z.writestr(path, json.dumps(doc))
            with ZipFile(ypath, "w") as z:
                for path, doc in original.items():
                    z.writestr(path.replace(".json", ".yaml"), yaml.safe_dump(doc))
            buf = io.StringIO()
            with redirect_stdout(buf):
                main(["--json-archive",str(jpath),"--yaml-archive",str(ypath)])
            report = json.loads(buf.getvalue())
            self.assertTrue(report["yaml_json_agree"])
            self.assertEqual(report["candidate_incompatible_edges"], 0)

    def test_unknown_format_or_unsupported_modes_refused(self):
        d = pack()
        d["authoring/shared/assessments/ng.shared.auto.json"]["assessment"]["mode"] = "unknown"
        with self.assertRaisesRegex(ValueError, "unknown Assessment mode"):
            build_preview(d)


if __name__ == "__main__":
    unittest.main()
