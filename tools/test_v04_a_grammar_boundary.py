#!/usr/bin/env python3
"""#239: preserve the 0.4-A base/research grammar distinction without freezing it."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parent))
from v04_a_grammar_boundary import (
    GrammarBoundaryError, boundary_schema_report, validate_draft_boundaries,
)

ROOT = Path(__file__).resolve().parents[1]
REAL_SOURCE = (ROOT / "research/assessment-simplification/compact-authoring-04/"
               "runtime-slice/home-nosuid.assessment.json")


def example():
    return {"assessment": {"id": "ng.example.synthetic", "tests": {
        "example-test": {
            "capability": "linux.partition",
            "require": "at_least_one_exists_and_all_match",
            "states": [{"mount_options": {
                "equals": "nosuid",
                "require": "at_least_one_exists_and_some_match",
            }}],
        },
    }, "evaluate": {"test": "example-test"}}}


def test_node(doc):
    return doc["assessment"]["tests"]["example-test"]


class BoundaryTests(unittest.TestCase):
    def test_base_schema_and_research_boundary_are_distinct(self):
        report = boundary_schema_report()
        self.assertEqual(report["status"], "DRAFT_BOUNDARY_INTACT")
        self.assertEqual(report["draft_test_key"], "require")
        self.assertEqual(report["unapproved_research_test_key"], "collected_items_require")
        self.assertTrue(report["base_test_additional_properties"])
        self.assertIn("native 0.4 compilation", report["not_proven"])

    def test_accepts_canonical_source_shape_without_scanner_claim(self):
        self.assertEqual(validate_draft_boundaries(example())["tested"], 1)

    def test_accepts_pinned_real_a_example(self):
        report = validate_draft_boundaries(json.loads(REAL_SOURCE.read_text(encoding="utf-8")))
        self.assertEqual(report["status"], "DRAFT_BOUNDARY_PASS")

    def test_requires_explicit_test_population_contract(self):
        doc = example()
        test_node(doc).pop("require")
        with self.assertRaisesRegex(GrammarBoundaryError, "Test 'require' missing"):
            validate_draft_boundaries(doc)

    def test_rejects_mixed_base_and_r3_research_test_keys(self):
        doc = example()
        test_node(doc)["collected_items_require"] = test_node(doc)["require"]
        with self.assertRaisesRegex(GrammarBoundaryError, "collected_items_require"):
            validate_draft_boundaries(doc)

    def test_rejects_r3_research_field_scope_in_base(self):
        doc = example()
        test_node(doc)["state_fields_require"] = "at_least_one_exists_and_all_match"
        with self.assertRaisesRegex(GrammarBoundaryError, "state_fields_require"):
            validate_draft_boundaries(doc)

    def test_rejects_field_scope_in_nested_group(self):
        doc = example()
        test_node(doc)["states"] = [{"all": [{"mount_options": {
            "require": "at_least_one_exists_and_some_match", "equals": "nosuid"}}],
            "state_fields_require": "at_least_one_exists_and_all_match"}]
        with self.assertRaisesRegex(GrammarBoundaryError, "state_fields_require"):
            validate_draft_boundaries(doc)

    def test_rejects_unapproved_and_or_list_groups(self):
        for op in ("and", "or"):
            with self.subTest(op=op):
                doc = example()
                original = test_node(doc)["states"][0]
                test_node(doc)["states"] = [{op: [original]}]
                with self.assertRaisesRegex(GrammarBoundaryError, "research-only logical group"):
                    validate_draft_boundaries(doc)

    def test_literal_fields_named_and_or_are_not_logic_groups(self):
        for field in ("and", "or"):
            with self.subTest(field=field):
                doc = example()
                test_node(doc)["states"] = [{field: {
                    "require": "at_least_one_exists_and_all_match", "equals": "literal"}}]
                self.assertEqual(validate_draft_boundaries(doc)["tested"], 1)

    def test_missing_field_cardinality_does_not_infer_test_default(self):
        doc = example()
        test_node(doc)["states"][0]["mount_options"].pop("require")
        with self.assertRaisesRegex(GrammarBoundaryError, "scalar field requires explicit"):
            validate_draft_boundaries(doc)

    def test_legacy_comparison_wrapper_not_promoted(self):
        doc = example()
        test_node(doc)["states"] = [{"mount_options": {
            "require": "at_least_one_exists_and_all_match",
            "operation": "equals", "value": "nosuid"}}]
        with self.assertRaisesRegex(GrammarBoundaryError, "legacy comparator wrapper"):
            validate_draft_boundaries(doc)

    def test_legacy_cardinality_pair_not_promoted(self):
        doc = example()
        test_node(doc)["states"][0]["mount_options"].update(
            {"existence": "one_or_more", "match": "all"})
        with self.assertRaisesRegex(GrammarBoundaryError, "legacy cardinality pair"):
            validate_draft_boundaries(doc)

    def test_draft_group_composition_kept(self):
        doc = example()
        field = deepcopy(test_node(doc)["states"][0])
        test_node(doc)["states"] = [{"all": [field, field]}]
        self.assertEqual(validate_draft_boundaries(doc)["tested"], 1)

    def test_record_scope_does_not_inherit_scalar_field_req(self):
        doc = example()
        test_node(doc)["states"] = [{"setting": {"record": {
            "require": "at_least_one_exists_and_all_match",
            "fields": {"key": {"equals": "v",
                               "require": "at_least_one_exists_and_all_match"}}}}}]
        # This is a syntax boundary check, not a validation of record schema.
        self.assertEqual(validate_draft_boundaries(doc)["tested"], 1)


if __name__ == "__main__":
    unittest.main()
