#!/usr/bin/env python3
"""#232/#239: deterministic, fail-closed research authoring graph tests."""
from copy import deepcopy
import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from zipfile import ZipFile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from v04_a_authoring_graph_index import graph_index, read_authoring_archive


def docs():
    return {
        "authoring/assessments/home.json": {
            "assessment": {"id": "ng.example.home-nosuid", "mode": "automated",
                           "tests": {"home-test": {"capability": "linux.partition",
                             "require": "at_least_one_exists_and_all_match",
                             "states": [{"mount_options": {"equals": "nosuid",
                               "require": "at_least_one_exists_and_some_match"}}]}},
                           "evaluate": {"test": "home-test"}}},
        "authoring/rules/SV-test.json": {
            "rule": {"id": "SV-test", "default_assessment_choice": "automated",
                     "assessment_choices": {"automated": {
                         "assessment": "ng.example.home-nosuid"}}}},
        "authoring/benchmark.json": {
            "benchmark": {"id": "ng.example.rhel9", "assessment_specifications": [
                {"id": "scap-ng.pre-alpha.assessment", "version": "0.3.0"}]}},
    }


class ResearchGraphIndexTests(unittest.TestCase):
    def test_graph_is_order_and_filename_independent(self):
        base = docs()
        original = graph_index(base)
        moved = {k.replace("home.json", "renamed.json").replace(".json", ".yaml"): v
                 for k, v in reversed(list(base.items()))}
        self.assertEqual(original["graph_sha256"], graph_index(moved)["graph_sha256"])
        self.assertEqual(original["stage"], "parsed_source_only_not_compiled")
        self.assertEqual(len(original["nodes"]), 3)

    def test_data_mutation_changes_graph_digest(self):
        changed = deepcopy(docs())
        changed["authoring/assessments/home.json"]["assessment"]["tests"]["home-test"]["states"][0][
            "mount_options"]["equals"] = "nodev"
        self.assertNotEqual(graph_index(docs())["graph_sha256"],
                            graph_index(changed)["graph_sha256"])

    def test_duplicate_logical_ids_fail(self):
        changed = deepcopy(docs())
        changed["authoring/duplicate.json"] = deepcopy(changed["authoring/assessments/home.json"])
        with self.assertRaisesRegex(ValueError, "duplicate logical identity"):
            graph_index(changed)

    def test_dangling_rule_assessment_fails(self):
        changed = deepcopy(docs())
        changed["authoring/rules/SV-test.json"]["rule"]["assessment_choices"]["automated"][
            "assessment"] = "missing"
        with self.assertRaisesRegex(ValueError, "unresolved authoring graph"):
            graph_index(changed)

    def test_unregistered_roots_fail(self):
        changed = deepcopy(docs())
        changed["authoring/other.json"] = {"unknown": {"id": "x"}}
        with self.assertRaisesRegex(ValueError, "unsupported document kind"):
            graph_index(changed)

    def test_source_spec_version_is_not_silently_changed(self):
        result = graph_index(docs())
        b = next(n for n in result["nodes"] if n["kind"] == "benchmark")
        changed = deepcopy(docs())
        changed["authoring/benchmark.json"]["benchmark"]["assessment_specifications"][0]["version"] = "0.4.0"
        updated = graph_index(changed)
        changed_node = next(n for n in updated["nodes"] if n["kind"] == "benchmark")
        self.assertNotEqual(b["sha256"], changed_node["sha256"])

    def test_yaml_and_json_parsers_produce_same_canonical_graph(self):
        import yaml
        with TemporaryDirectory() as d:
            jsonzip, yamlzip = Path(d)/"json.zip", Path(d)/"yaml.zip"
            source = docs()
            with ZipFile(jsonzip, "w") as archive:
                for path, item in source.items():
                    archive.writestr(path, json.dumps(item, sort_keys=True))
            with ZipFile(yamlzip, "w") as archive:
                for path, item in source.items():
                    archive.writestr(path.replace(".json", ".yaml"),
                                     yaml.safe_dump(item, sort_keys=False))
            j = graph_index(read_authoring_archive(jsonzip, "json"))
            y = graph_index(read_authoring_archive(yamlzip, "yaml"))
            self.assertEqual(j["graph_sha256"], y["graph_sha256"])

    def test_duplicate_json_member_key_fails(self):
        with TemporaryDirectory() as d:
            path = Path(d)/"duplicate.zip"
            with ZipFile(path, "w") as archive:
                archive.writestr("authoring/a.json", '{"assessment":{"id":"a","id":"b"}}')
            with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                read_authoring_archive(path, "json")

    def test_duplicate_yaml_member_key_fails(self):
        with TemporaryDirectory() as d:
            path = Path(d)/"duplicate.zip"
            with ZipFile(path, "w") as archive:
                archive.writestr("authoring/a.yaml", "assessment:\n  id: a\n  id: b\n")
            with self.assertRaisesRegex(ValueError, "duplicate YAML key"):
                read_authoring_archive(path, "yaml")

    def test_implicitly_boolean_yaml_key_rejected_not_reinterpreted(self):
        with TemporaryDirectory() as d:
            path = Path(d)/"coercion.zip"
            with ZipFile(path, "w") as archive:
                archive.writestr("authoring/a.yaml", "assessment:\n  id: a\n  on: x\n")
            with self.assertRaisesRegex(ValueError, "nonstring/implicitly coerced"):
                read_authoring_archive(path, "yaml")

    def test_nonjson_yaml_date_not_coerced(self):
        with TemporaryDirectory() as d:
            path = Path(d)/"date.zip"
            with ZipFile(path, "w") as archive:
                archive.writestr("authoring/a.yaml", "assessment:\n  id: a\n  created: 2026-10-18\n")
            with self.assertRaisesRegex(ValueError, "not JSON serializable"):
                read_authoring_archive(path, "yaml")


if __name__ == "__main__":
    unittest.main()
