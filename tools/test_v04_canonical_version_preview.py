#!/usr/bin/env python3
"""Source-exact 0.4 Benchmark version preview and adversarial tests (#232)."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_v04_canonical_source_ir import sample
from v04_canonical_version_preview import preview, preview_pair


def blocked():
    docs = sample()
    docs["authoring/demo/benchmark.demo.json"]["benchmark"][
        "assessment_specifications"][0]["version"] = "0.3.0"
    return docs


class VersionPreviewTests(unittest.TestCase):
    def test_source_kept_candidate_changes_only_benchmark_spec(self):
        source = blocked()
        preserved = deepcopy(source)
        result = preview(source, validate_benchmark_schema=False)
        self.assertEqual(source, preserved)
        self.assertEqual(result["conflicts_before"], 1)
        self.assertEqual(result["conflicts_after"], 0)
        self.assertEqual(result["choice_links"], 1)
        self.assertTrue(result["approval_required"])
        self.assertEqual(len(result["changes"]), 1)
        row = result["changes"][0]
        self.assertEqual(row["existing_specs"][0]["version"], "0.3.0")
        self.assertEqual(row["reachable_automated_specs"][0]["version"], "0.4.0")
        before = {x["path"]: x["source_ast"] for x in result["source_ir"]["records"]}
        after = {x["path"]: x["source_ast"] for x in result["candidate_ir"]["records"]}
        for path in before:
            if "benchmark" not in before[path]:
                self.assertEqual(before[path], after[path])
        self.assertNotEqual(result["source_graph_sha256"], result["candidate_graph_sha256"])

    def test_already_consistent_source_is_not_migrated(self):
        out = preview(sample(), validate_benchmark_schema=False)
        self.assertEqual(out["status"], "VERSION_DECLARATIONS_ALREADY_COMPATIBLE")
        self.assertFalse(out["changes"])
        self.assertEqual(out["conflicts_before"], 0)

    def test_manual_choice_not_converted_to_automated(self):
        docs = blocked()
        docs["authoring/demo/assessments/manual.json"] = {"assessment": {
            "id": "manual", "mode": "manual"}}
        docs["authoring/demo/rules/r1.json"]["rule"]["assessment_choices"][
            "manual"] = {"assessment": "manual"}
        result = preview(docs, validate_benchmark_schema=False)
        self.assertEqual(result["conflicts_after"], 0)
        self.assertEqual(result["choice_links"], 2)
        after = {x["path"]: x["source_ast"] for x in result["candidate_ir"]["records"]}
        self.assertEqual(after["authoring/demo/assessments/manual.json"],
                         docs["authoring/demo/assessments/manual.json"])

    def test_bad_references_cannot_be_hidden_by_version_rewrite(self):
        docs = blocked()
        docs["authoring/demo/rules/r1.json"]["rule"]["assessment_choices"][
            "automated"]["assessment"] = "unresolved"
        with self.assertRaisesRegex(ValueError, "unresolved"):
            preview(docs, validate_benchmark_schema=False)

    def test_two_formats_have_identical_proposed_graph_and_provenance(self):
        docs = blocked()
        with tempfile.TemporaryDirectory() as root:
            json_path, yaml_path = Path(root) / "j.zip", Path(root) / "y.zip"
            for target, ext in ((json_path, "json"), (yaml_path, "yaml")):
                with zipfile.ZipFile(target, "w") as z:
                    for path, doc in docs.items():
                        z.writestr(path.removesuffix(".json") + "." + ext,
                                   json.dumps(doc) if ext == "json"
                                   else yaml.safe_dump(doc, sort_keys=False))
            report = preview_pair(json_path, yaml_path, validate_benchmark_schema=False)
            self.assertEqual(report["yaml_json_source_and_candidate_parity"], "PASS")
            self.assertEqual(report["benchmarks_changed"], 1)
            self.assertFalse(report["version_policy_approved"])
            self.assertFalse(report["executable_compiler_completed"])
            self.assertFalse(report["signed_bundle"])


if __name__ == "__main__":
    unittest.main()
