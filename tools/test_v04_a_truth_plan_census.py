#!/usr/bin/env python3
"""#232/#229: independent verified-source expression plan census tests."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_v04_a_lossless_ir import fixture, automated
from v04_a_lossless_ir import normalize_documents
from v04_a_truth_plan_census import (MANIFEST_STAGE, build_manifest, verify_manifest)


class ExpressionManifestTests(unittest.TestCase):
    def setUp(self):
        self.docs = fixture()

    def test_full_source_roundtrip_and_six_input_classes(self):
        source = normalize_documents(self.docs)
        manifest = build_manifest(source)
        self.assertEqual(manifest["stage"], MANIFEST_STAGE)
        self.assertEqual(manifest["counts"]["automated_assessments_seen"], 1)
        self.assertEqual(manifest["counts"]["assessments_with_compiled_evaluate"], 1)
        self.assertEqual(manifest["counts"]["synthetic_expression_executions"], 6)
        self.assertEqual(len(manifest["plans"]), 1)
        self.assertEqual(manifest["unapproved_expression_blockers"], [])
        self.assertEqual(manifest["plans"][0][
            "synthetic_result_scenarios_not_collections"], {
            "true": "true", "false": "false", "error": "error",
            "unknown": "unknown", "not_evaluated": "not_evaluated",
            "not_applicable": "not_applicable"})
        self.assertTrue(verify_manifest(source, manifest))

    def test_detect_tampered_source_path_hash_and_result_scenario(self):
        source = normalize_documents(self.docs)
        manifest = build_manifest(source)
        for action in ("path", "hash", "scenario"):
            mutated = deepcopy(manifest)
            if action == "path":
                mutated["plans"][0]["source_path"] = "authoring/made-up.json"
            if action == "hash":
                mutated["plans"][0]["source_sha256"] = "0" * 64
            if action == "scenario":
                mutated["plans"][0]["synthetic_result_scenarios_not_collections"][
                    "error"] = "true"
            with self.subTest(action=action):
                with self.assertRaisesRegex(ValueError, "tampered"):
                    verify_manifest(source, mutated)

    def test_conditional_is_reported_not_executed_or_rewritten(self):
        a = automated(self.docs)
        name = next(iter(a["tests"]))
        a["evaluate"] = {
            "if": {"test": name},
            "then": {"test": name},
            "else": {"not_applicable": {"reason": "not applicable"}},
        }
        source = normalize_documents(self.docs)
        manifest = build_manifest(source)
        self.assertEqual(manifest["counts"]["automated_assessments_seen"], 1)
        self.assertEqual(manifest["counts"].get("assessments_with_compiled_evaluate", 0), 0)
        self.assertEqual(len(manifest["unapproved_expression_blockers"]), 1)
        self.assertEqual(manifest["unapproved_expression_blockers"][0]["field"], "evaluate")
        self.assertEqual(manifest["plans"], [])
        self.assertTrue(verify_manifest(source, manifest))

    def test_applicability_is_compiled_as_distinct_expression(self):
        a = automated(self.docs)
        name = next(iter(a["tests"]))
        a["applicability"] = {"test": name}
        ir = normalize_documents(self.docs)
        manifest = build_manifest(ir)
        self.assertEqual(manifest["counts"]["compiled_applicability_roots"], 1)
        self.assertEqual(manifest["counts"]["compiled_expression_roots"], 2)
        self.assertEqual(manifest["counts"]["synthetic_expression_executions"], 12)
        self.assertEqual({x["expression_field"] for x in manifest["plans"]},
                         {"evaluate", "applicability"})

    def test_order_and_format_normalization_stable(self):
        expected = build_manifest(normalize_documents(self.docs))
        other = {k.replace(".json", ".yaml"): v for k, v in
                 reversed(list(self.docs.items()))}
        self.assertEqual(expected, build_manifest(normalize_documents(other)))


if __name__ == "__main__":
    unittest.main()
