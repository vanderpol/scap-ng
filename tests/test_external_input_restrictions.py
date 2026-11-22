"""Canonical 0.4.1 external Input restriction conformance vectors."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import unittest

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
from test_draft202012_and_examples import load, schema_registry  # noqa: E402


class ExternalInputRestrictionSchema(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = schema_registry()
        cls.language = load(ROOT / "schema" / "assessment-language.schema.json")
        cls.vectors = json.loads((ROOT / "tests/fixtures/external-input-restriction-vectors.json").read_text())
        cls.expression_validator = Draft202012Validator(
            {"$ref": cls.language["$id"] + "#/$defs/value_constraint_expression"},
            registry=cls.registry,
        )
        cls.assessment = __import__("yaml").safe_load(
            (ROOT / "examples/windows-optional-organizational-input.assessment.yaml").read_text()
        )
        cls.assessment_validator = Draft202012Validator(
            load(ROOT / "schema/assessment.schema.json"), registry=cls.registry
        )

    def test_all_generic_boolean_and_comparison_vectors_are_schema_valid(self):
        for vector in self.vectors["schema_valid"]:
            with self.subTest(vector=vector["id"]):
                self.expression_validator.validate(vector["predicate"])

    def test_malformed_and_resource_bound_vectors_are_rejected(self):
        for vector in self.vectors["schema_invalid"]:
            with self.subTest(vector=vector["id"]):
                if vector["id"] == "too-many-branches":
                    predicate = {"or": [{"equals": i} for i in range(65)]}
                elif vector["id"] == "overlong-pattern":
                    predicate = {"matches_regex": "x" * 4097}
                else:
                    predicate = vector["predicate"]
                self.assertTrue(list(self.expression_validator.iter_errors(predicate)))

    def test_expression_resource_limits_are_explicit_and_enforced_by_contract(self):
        limits = self.language["$defs"]["value_constraint_expression"]["x-scap-ng-resource-limits"]
        self.assertEqual(limits["max_expression_depth"], 32)
        self.assertEqual(limits["max_expression_nodes"], 256)

        def nested(depth):
            value = {"equals": 1}
            for _ in range(depth - 1):
                value = {"and": [value]}
            return value

        def size_and_depth(value, depth=1):
            if "and" in value or "or" in value or "one" in value or "xor" in value:
                key = next(k for k in ("and", "or", "one", "xor") if k in value)
                children = [size_and_depth(child, depth + 1) for child in value[key]]
                return 1 + sum(row[0] for row in children), max([depth] + [row[1] for row in children])
            return 1, depth

        nodes, depth = size_and_depth(nested(limits["max_expression_depth"] + 1))
        self.assertGreater(depth, limits["max_expression_depth"])
        self.assertLessEqual(nodes, limits["max_expression_nodes"])
        nodes, depth = size_and_depth({"or": [{"equals": i} for i in range(limits["max_expression_nodes"] + 1)]})
        self.assertGreater(nodes, limits["max_expression_nodes"])
        self.assertLessEqual(depth, limits["max_expression_depth"])

    def test_input_constraint_is_admitted_without_oval_specific_keys(self):
        document = copy.deepcopy(self.assessment)
        document["assessment"]["inputs"]["slideshow-value-input"]["constraints"] = {
            "predicate": {"and": [{"greater_than_or_equal": 1}, {"less_than_or_equal": 10}]}
        }
        self.assessment_validator.validate(document)
        constraints = document["assessment"]["inputs"]["slideshow-value-input"]["constraints"]
        self.assertNotIn("possible_restriction", constraints)
        self.assertNotIn("restriction_groups", constraints)

    def test_binding_vectors_preserve_missing_empty_and_cardinality_distinctions(self):
        outcomes = {row["id"]: row["outcome"] for row in self.vectors["binding_semantics"]}
        self.assertEqual(outcomes["missing-required"], "not_evaluated")
        self.assertEqual(outcomes["optional-guarded"], "not_evaluated")
        self.assertEqual(outcomes["optional-unguarded"], "error")
        self.assertEqual(outcomes["explicit-empty-valid"], "accepted")
        self.assertEqual(outcomes["empty-cardinality-invalid"], "error")
        self.assertEqual(outcomes["multivalue-cardinality-invalid"], "error")
        self.assertIsNone(next(row for row in self.vectors["binding_semantics"] if row["id"] == "missing-required")["supplied"])
        self.assertEqual(next(row for row in self.vectors["binding_semantics"] if row["id"] == "explicit-empty-valid")["supplied"], [])


if __name__ == "__main__":
    unittest.main()
