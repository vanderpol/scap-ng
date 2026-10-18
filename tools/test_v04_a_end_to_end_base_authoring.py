#!/usr/bin/env python3
"""#232/#239: integrated, fail-closed A research package path tests."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_v04_a_benchmark_choice_version_closure import pack
from test_v04_a_lower_scoped_to_base import scoped, base
from v04_a_end_to_end_base_authoring import stage_and_package, _extract_docs
from v04_a_deterministic_research_container import verify_research_container


def input_documents():
    docs = pack()
    assessment = scoped(base())
    assessment["assessment"]["id"] = "ng.shared.auto"
    docs["authoring/shared/assessments/ng.shared.auto.json"] = assessment
    return docs


class IntegratedPipelineTests(unittest.TestCase):
    def test_end_to_end_content_contains_base_not_scoped(self):
        docs = input_documents()
        original = deepcopy(docs)
        data, report = stage_and_package(docs, validate_base=False)
        packaged, manifest = _extract_docs(data)
        self.assertEqual(docs, original)
        self.assertEqual(report["source_document_count"], 4)
        self.assertEqual(report["assessment_counts"]["lowered_automated_assessments"], 1)
        self.assertEqual(report["rule_choice_links"], 2)
        self.assertEqual(report["base_schema"], "NOT_CHECKED_RESEARCH_FIXTURE")
        self.assertFalse(report["owner_approved"])
        self.assertFalse(report["allowed_to_scan"])
        self.assertFalse(report["native_0_4_compiler_complete"])
        document = packaged["authoring/shared/assessments/ng.shared.auto.json"]["assessment"]
        test = document["tests"]["test"]
        self.assertEqual(test["require"], "at_least_one_exists_and_all_match")
        self.assertNotIn("collected_items_require", test)
        self.assertNotIn("state_fields_require", test)
        self.assertEqual(test["states"][0]["all"][2]["c"]["require"], "none_exist")
        self.assertEqual(packaged["authoring/rhel_9/benchmark.rhel_9.json"]["benchmark"][
            "assessment_specifications"], [{"id": "scap-ng.pre-alpha.assessment", "version": "0.4.0"}])
        self.assertEqual(packaged["authoring/shared/assessments/ng.shared.manual.json"],
                         docs["authoring/shared/assessments/ng.shared.manual.json"])
        self.assertEqual(verify_research_container(data)["member_count"], 4)

    def test_format_name_does_not_change_archive_bytes(self):
        original = input_documents()
        yaml_names = {name.replace(".json", ".yaml"): value
                      for name, value in original.items()}
        a, ar = stage_and_package(original, validate_base=False)
        b, br = stage_and_package(yaml_names, validate_base=False)
        self.assertEqual(a, b)
        self.assertEqual(ar["archive_sha256"], br["archive_sha256"])

    def test_input_order_does_not_change_archive_bytes(self):
        original = input_documents()
        a, _ = stage_and_package(original, validate_base=False)
        b, _ = stage_and_package(dict(reversed(list(original.items()))), validate_base=False)
        self.assertEqual(a, b)

    def test_state_value_change_changes_complete_archive_digest(self):
        docs = input_documents()
        a, _ = stage_and_package(docs, validate_base=False)
        docs = deepcopy(docs)
        test = docs["authoring/shared/assessments/ng.shared.auto.json"]["assessment"]["tests"]["test"]
        fields = test["states"][0]["and"]
        fields[-1]["c"]["equals"] = 999
        b, _ = stage_and_package(docs, validate_base=False)
        self.assertNotEqual(sha256(a).hexdigest(), sha256(b).hexdigest())

    def test_mixed_test_require_syntax_is_rejected(self):
        docs = input_documents()
        docs["authoring/shared/assessments/ng.shared.auto.json"]["assessment"]["tests"]["test"][
            "require"] = "at_least_one_exists_and_all_match"
        with self.assertRaisesRegex(ValueError, "mixed or missing"):
            stage_and_package(docs, validate_base=False)

    def test_unsupported_missing_cardinality_is_rejected(self):
        docs = input_documents()
        docs["authoring/shared/assessments/ng.shared.auto.json"]["assessment"]["tests"]["test"][
            "collected_items_require"] = None
        with self.assertRaisesRegex(ValueError, "invalid collected_items_require"):
            stage_and_package(docs, validate_base=False)

    def test_dangling_rule_choice_is_not_silently_dropped(self):
        docs = input_documents()
        docs["authoring/rhel_9/rules/SV-TEST.rule.json"]["rule"]["assessment_choices"][
            "automated"]["assessment"] = "missing"
        with self.assertRaisesRegex(ValueError, "unresolved"):
            stage_and_package(docs, validate_base=False)

    def test_duplicate_assessment_id_fails_closed(self):
        docs = input_documents()
        docs["authoring/rhel_9/assessments/duplicate.json"] = deepcopy(
            docs["authoring/shared/assessments/ng.shared.auto.json"])
        with self.assertRaisesRegex(ValueError, "duplicate"):
            stage_and_package(docs, validate_base=False)

    def test_invalid_semantic_source_not_claimed_as_schema_valid(self):
        docs = input_documents()
        data, result = stage_and_package(docs, validate_base=False)
        self.assertEqual(result["base_schema"], "NOT_CHECKED_RESEARCH_FIXTURE")
        self.assertEqual(result["status"], "VERIFIED_BASE_AUTHORING_RESEARCH_ONLY")
        self.assertEqual(result["source_preservation"], "PASS")
        self.assertEqual(json.loads(json.dumps(result))["signed_bundle"], False)


if __name__ == "__main__":
    unittest.main()
