#!/usr/bin/env python3
"""#240: adversarial lossless 0.4-A IR source-envelope regression."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from jsonschema import Draft202012Validator
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_v04_a_end_to_end_base_authoring import input_documents
from v04_a_end_to_end_base_authoring import stage_and_package, _extract_docs
from v04_a_authoring_graph_index import canonical_json
from v04_a_lossless_ir import (
    IR_STATUS, decode_and_verify, normalize_documents,
)


def fixture():
    data, report = stage_and_package(input_documents(), validate_base=False)
    docs, manifest = _extract_docs(data)
    assert report["base_schema"] == "NOT_CHECKED_RESEARCH_FIXTURE"
    assert len(docs) == 4
    return docs


def automated(docs):
    return docs["authoring/shared/assessments/ng.shared.auto.json"]["assessment"]


class LosslessIrTests(unittest.TestCase):
    def setUp(self):
        self.docs = fixture()

    def test_draft_2020_12_research_ir_schema_accepts_lossless_envelope(self):
        path = (Path(__file__).resolve().parents[1] /
                "research/assessment-simplification/compact-authoring-04/"
                "lossless-ir-envelope.schema.json")
        schema = json.loads(path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        ir = normalize_documents(self.docs)
        Draft202012Validator(schema).validate(ir)
        invalid = deepcopy(ir)
        invalid["status"] = "COMPILER_READY"
        self.assertTrue(list(Draft202012Validator(schema).iter_errors(invalid)))

    def test_roundtrip_all_source_documents_and_manual_choice(self):
        original = deepcopy(self.docs)
        ir = normalize_documents(self.docs)
        restored = decode_and_verify(ir)
        self.assertEqual(restored, original)
        self.assertEqual(self.docs, original)
        self.assertEqual(ir["status"], IR_STATUS)
        self.assertEqual(ir["document_count"], 4)
        self.assertEqual(ir["automated_assessment_count"], 1)
        self.assertEqual(ir["automated_test_count"], 1)
        self.assertEqual(ir["rule_choice_link_count"], 2)
        self.assertFalse(any("executable" in x.lower() for x in ir if x != "not_proven"))
        self.assertEqual(len([r for r in ir["documents"] if r["kind"] == "rule"]), 1)
        manual = next(r for r in ir["documents"]
                      if r["kind"] == "assessment"
                      and r["assessment_index"]["mode"] == "manual")
        self.assertEqual(manual["assessment_index"]["tests"], [])

    def test_json_yaml_names_and_insertion_order_yield_same_bytes(self):
        a = normalize_documents(self.docs)
        yaml_docs = {key[:-5] + ".yaml": value for key, value in
                     reversed(list(self.docs.items()))}
        b = normalize_documents(yaml_docs)
        self.assertEqual(canonical_json(a), canonical_json(b))
        self.assertEqual(decode_and_verify(b), self.docs)

    def test_nested_evaluate_tree_is_not_flattened(self):
        auto = automated(self.docs)
        name = next(iter(auto["tests"]))
        auto["evaluate"] = {"all": [{"test": name}, {"not": {"test": name}}]}
        ir = normalize_documents(self.docs)
        self.assertEqual(next(r for r in ir["documents"] if r["id"] == auto["id"])
                         ["source_ast"]["assessment"]["evaluate"], auto["evaluate"])
        self.assertEqual(decode_and_verify(ir), self.docs)

    def test_variable_objects_foreach_sets_filters_and_windows_records_stay_in_ast(self):
        auto = automated(self.docs)
        test = next(iter(auto["tests"].values()))
        test["research_unexecuted"] = {
            "for_each": {"item": "user", "in": "existing"},
            "select": {"directory": {"from": "user.home_dir"}},
            "computed": {"variable": "loop-variable"},
            "records": [{"record": {"require": "only_one_exists",
                                   "fields": [{"sid": {"equals": "S-1-5-18",
                                                       "require": "all_exist_and_all_match"}}]}}],
            "set": {"union": [{"object": "existing"}, {"filter": {"equals": "x"}}]},
            "state": {"unknown": "unknown", "error": "error",
                      "not_applicable": "not_applicable"},
        }
        auto["variables"] = {"loop-variable": {"value": [1, 2]}}
        auto["shared_objects"] = {"existing": {"capability": "unix.file"}}
        ir = normalize_documents(self.docs)
        r = next(x for x in ir["documents"] if x["id"] == auto["id"])
        self.assertEqual(decode_and_verify(ir), self.docs)
        indexed = r["assessment_index"]["tests"][0]
        self.assertIn({"type": "variable",
                       "path": ["research_unexecuted", "computed", "variable"],
                       "target": "loop-variable"},
                      indexed["collection_reference_hints"])
        self.assertEqual(r["source_ast"]["assessment"]["tests"], auto["tests"])
        dataflow = r["assessment_index"]["source_dataflow"]
        self.assertTrue(any(e["role"] == "for_each_source" for e in dataflow["edges"]))
        self.assertEqual(dataflow["status"], "SOURCE_DATAFLOW_ONLY_NOT_EXECUTABLE")

    def test_preserves_provenance_and_valid_unrecognized_test_subtrees(self):
        auto = automated(self.docs)
        test = next(iter(auto["tests"].values()))
        test["new_capability_accepted_field"] = {"nested": [True, False, None]}
        auto["evidence"] = [{"source": "original-oval-id", "sha256": "a" * 64}]
        ir = normalize_documents(self.docs)
        self.assertEqual(decode_and_verify(ir), self.docs)

    def test_rejects_tampered_test_index_and_source_hash(self):
        ir = normalize_documents(self.docs)
        record = next(r for r in ir["documents"] if r["kind"] == "assessment"
                      and r["assessment_index"]["mode"] == "automated")
        bad = deepcopy(ir)
        target = next(r for r in bad["documents"] if r["id"] == record["id"])
        target["assessment_index"]["tests"][0]["item_requirement"] = "none_exist"
        with self.assertRaisesRegex(ValueError, "index|checksum"):
            decode_and_verify(bad)
        bad = deepcopy(ir)
        bad["documents"][0]["source_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "digest"):
            decode_and_verify(bad)

    def test_rejects_duplicate_logical_assessment_id_and_paths(self):
        duplicate = deepcopy(self.docs)
        duplicate["authoring/shared/assessments/duplicate.json"] = deepcopy(
            self.docs["authoring/shared/assessments/ng.shared.auto.json"])
        with self.assertRaisesRegex(ValueError, "duplicate"):
            normalize_documents(duplicate)
        duplicate = dict(self.docs)
        key = "authoring/shared/assessments/ng.shared.auto.json"
        duplicate[key[:-5] + ".yaml"] = deepcopy(duplicate[key])
        with self.assertRaisesRegex(ValueError, "duplicate normalized"):
            normalize_documents(duplicate)

    def test_rejects_unresolved_evaluate_reference(self):
        automated(self.docs)["evaluate"] = {"test": "no-such-test"}
        with self.assertRaisesRegex(ValueError, "unresolved"):
            normalize_documents(self.docs)

    def test_rejects_missing_requirement_no_hidden_defaults(self):
        test = next(iter(automated(self.docs)["tests"].values()))
        test.pop("require")
        with self.assertRaisesRegex(ValueError, "explicit Item require"):
            normalize_documents(self.docs)

    def test_rejects_missing_version_or_mixed_scoped_syntax(self):
        auto = automated(self.docs)
        auto["specification"].pop("version")
        with self.assertRaisesRegex(ValueError, "specification"):
            normalize_documents(self.docs)
        self.docs = fixture()
        test = next(iter(automated(self.docs)["tests"].values()))
        test["state_fields_require"] = "all_exist"
        with self.assertRaisesRegex(ValueError, "scoped-only"):
            normalize_documents(self.docs)

    def test_rejects_malformed_mode_or_tampered_status(self):
        automated(self.docs)["mode"] = "maybe"
        with self.assertRaisesRegex(ValueError, "mode"):
            normalize_documents(self.docs)
        ir = normalize_documents(fixture())
        ir["status"] = "EXECUTABLE"
        with self.assertRaisesRegex(ValueError, "research IR"):
            decode_and_verify(ir)

    def test_rejects_broken_rule_choice(self):
        rule = next(doc["rule"] for doc in self.docs.values() if "rule" in doc)
        rule["assessment_choices"]["automated"]["assessment"] = "missing"
        with self.assertRaisesRegex(ValueError, "unresolved"):
            normalize_documents(self.docs)

    def test_resolved_truth_dependency_is_distinct_from_collection_refs(self):
        auto = automated(self.docs)
        manual = next(doc["assessment"] for doc in self.docs.values()
                      if doc.get("assessment", {}).get("mode") == "manual")
        auto["version"], auto["purpose"] = 1, "assessment"
        manual["version"], manual["purpose"] = 1, "assessment"
        test_id = next(iter(auto["tests"]))
        auto["dependencies"] = {"other": {
            "assessment": manual["id"], "expected_version": 1,
            "purpose": "assessment"}}
        auto["evaluate"] = {"all": [{"test": test_id}, {"assessment": "other"}]}
        ir = normalize_documents(self.docs)
        index = next(d["assessment_index"] for d in ir["documents"]
                     if d["id"] == auto["id"])
        self.assertEqual(index["assessment_dependencies"][0]["target"], manual["id"])
        self.assertEqual(decode_and_verify(ir), self.docs)

    def test_missing_truth_dependency_target_fails_closed(self):
        auto = automated(self.docs)
        auto["dependencies"] = {"other": {
            "assessment": "does-not-exist", "expected_version": 1,
            "purpose": "assessment"}}
        with self.assertRaisesRegex(ValueError, "unresolved Assessment dependency"):
            normalize_documents(self.docs)

    def test_truth_dependency_exact_version_and_purpose_are_checked(self):
        auto = automated(self.docs)
        auto["version"], auto["purpose"] = 1, "assessment"
        auto["dependencies"] = {"self": {
            "assessment": auto["id"], "expected_version": 2,
            "purpose": "assessment"}}
        with self.assertRaisesRegex(ValueError, "version mismatch"):
            normalize_documents(self.docs)
        auto["dependencies"]["self"]["expected_version"] = 1
        auto["dependencies"]["self"]["purpose"] = "applicability"
        with self.assertRaisesRegex(ValueError, "purpose mismatch"):
            normalize_documents(self.docs)

    def test_truth_dependency_cycle_fails_closed(self):
        auto = automated(self.docs)
        auto["version"], auto["purpose"] = 1, "assessment"
        auto["dependencies"] = {"self": {
            "assessment": auto["id"], "expected_version": 1,
            "purpose": "assessment"}}
        with self.assertRaisesRegex(ValueError, "cyclic Assessment dependency"):
            normalize_documents(self.docs)

    def test_shared_assessment_cannot_depend_on_private_other_benchmark(self):
        auto = automated(self.docs)
        auto["version"], auto["purpose"] = 1, "assessment"
        private = deepcopy(self.docs["authoring/shared/assessments/ng.shared.auto.json"])
        private["assessment"]["id"] = "ng.private"
        self.docs["authoring/windows11/assessments/private.json"] = private
        auto["dependencies"] = {"private": {
            "assessment": "ng.private", "expected_version": 1,
            "purpose": "assessment"}}
        with self.assertRaisesRegex(ValueError, "cross-Benchmark private"):
            normalize_documents(self.docs)

    def test_changed_source_produces_distinct_digest(self):
        before = canonical_json(normalize_documents(self.docs))
        auto = automated(self.docs)
        test = next(iter(auto["tests"].values()))
        test["nonsemantic_documentation"] = "reviewed by human"
        after = canonical_json(normalize_documents(self.docs))
        self.assertNotEqual(sha256(before).digest(), sha256(after).digest())


if __name__ == "__main__":
    unittest.main()
