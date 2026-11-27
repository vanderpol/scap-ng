"""Independent semantic oracle for the proposed native Object for_each contract."""
import json
import re
from pathlib import Path
import unittest

import yaml
from jsonschema import Draft202012Validator

from test_draft202012_and_examples import UniqueYaml, load, schema_registry

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = ROOT / "conformance/expected/core-foreach-semantic-vectors.json"
TRUTH = ROOT / "conformance/0.4/foreach/truth-tables.json"
ASSESSMENT = ROOT / "conformance/cases/core/foreach-semantic-vectors.assessment.yaml"


def reduce_iterations(source, reducer, outcomes):
    """Independent reducer; it intentionally does not inspect RI code."""
    if reducer == "every":
        if "false" in outcomes:
            return "false"
        if source == "cancelled":
            return "not_evaluated"
        if source != "complete_nonempty":
            return "unknown"
        if not outcomes:
            return "unknown"
        if "error" in outcomes:
            return "error"
        if "unknown" in outcomes:
            return "unknown"
        if "not_evaluated" in outcomes:
            return "not_evaluated"
        return "true"
    if reducer == "one_or_more":
        if "true" in outcomes:
            return "true"
        if source == "cancelled":
            return "not_evaluated"
        if source == "complete_empty":
            return "false"
        if source != "complete_nonempty":
            return "unknown"
        if "error" in outcomes:
            return "error"
        if "unknown" in outcomes:
            return "unknown"
        if "not_evaluated" in outcomes:
            return "not_evaluated"
        return "false"
    if reducer == "exactly_one":
        if outcomes.count("true") >= 2:
            return "false"
        if source == "cancelled":
            return "not_evaluated"
        if source != "complete_nonempty":
            return "false" if source == "complete_empty" else "unknown"
        if "error" in outcomes:
            return "error"
        if "unknown" in outcomes:
            return "unknown"
        if "not_evaluated" in outcomes:
            return "not_evaluated"
        return "true" if outcomes.count("true") == 1 else "false"
    if reducer == "none":
        if "true" in outcomes:
            return "false"
        if source == "cancelled":
            return "not_evaluated"
        if source == "complete_empty":
            return "true"
        if source != "complete_nonempty":
            return "unknown"
        if "error" in outcomes:
            return "error"
        if "unknown" in outcomes:
            return "unknown"
        if "not_evaluated" in outcomes:
            return "not_evaluated"
        return "true"
    raise AssertionError(reducer)


class ForeachSemanticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.expected = json.loads(EXPECTED.read_text())
        cls.truth = json.loads(TRUTH.read_text())
        cls.validator = Draft202012Validator(
            load(ROOT / "schema/assessment.schema.json"), registry=schema_registry()
        )

    def test_independent_truth_vectors(self):
        for name, vector in self.expected["vectors"].items():
            with self.subTest(vector=name):
                if name == "conditional-branch-suppression":
                    # Conditional selection happens before collection and is
                    # not a reducer input.
                    self.assertEqual(vector["outcome"], "not_evaluated")
                    continue
                actual = reduce_iterations(
                    vector["source"], vector["reduce"], vector["iterations"]
                )
                self.assertEqual(actual, vector["outcome"])

    def test_missing_dependent_item_cannot_disappear(self):
        vector = self.expected["vectors"]["missing-dependent-cannot-disappear"]
        self.assertEqual(reduce_iterations("complete_nonempty", "every", ["false", "true"]), "false")
        # Mutation: flattening away the empty dependent iteration changes the
        # result. The test makes that dangerous implementation visibly fail.
        self.assertNotEqual(
            reduce_iterations("complete_nonempty", "every", ["true"]), vector["outcome"]
        )

    def test_incomplete_population_never_becomes_empty(self):
        self.assertEqual(
            reduce_iterations("partial", "every", ["true"]), "unknown"
        )
        self.assertEqual(
            reduce_iterations("partial", "one_or_more", []), "unknown"
        )

    def test_decisive_result_survives_cancellation_without_claiming_complete(self):
        self.assertEqual(
            reduce_iterations("cancelled", "every", ["false"]), "false"
        )
        self.assertEqual(
            reduce_iterations("cancelled", "every", ["true"]), "not_evaluated"
        )

    def test_truth_table_invariants_are_present(self):
        self.assertEqual(self.truth["status"], "owner-review-draft")
        self.assertEqual(set(self.truth["reducers"]), {"every", "one_or_more", "exactly_one", "none"})
        self.assertIn("zero_dependent_items_are_explicit", self.truth["invariants"])
        self.assertIn("suppressed_branches_do_not_collect", self.truth["invariants"])

    def test_native_yaml_witness_is_schema_valid_and_separate_from_oracle(self):
        document = yaml.load(ASSESSMENT.read_text(), Loader=UniqueYaml)
        self.assertEqual(list(self.validator.iter_errors(document)), [])
        evaluate = document["assessment"]["evaluate"]
        self.assertIn("else_if", evaluate)
        self.assertEqual(
            self.expected["vectors"]["conditional-branch-suppression"]["outcome"],
            "not_evaluated",
        )
        self.assertEqual(
            json.loads((ROOT / "conformance/fixtures/core-foreach-semantic-vectors.json").read_text())[
                "branch_events"
            ][-1]["status"],
            "selected",
        )

    def test_binding_scope_vectors_reject_bad_lexical_forms(self):
        pattern = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]*\.[A-Za-z_][A-Za-z0-9_-]*$")
        vectors = self.expected["binding_vectors"]
        self.assertEqual(
            [v["name"] for v in vectors if v["expected"] == "reject"],
            ["unknown-alias", "unknown-field", "sibling-alias"],
        )
        for vector in vectors:
            self.assertTrue(pattern.fullmatch(vector["binding"]))
        # Shape-valid is not scope-valid: the compiler must resolve these
        # names against source Item contracts and visible aliases.
        self.assertTrue(pattern.fullmatch("missing.full_path"))
        self.assertTrue(pattern.fullmatch("sibling.full_path"))


if __name__ == "__main__":
    unittest.main()
