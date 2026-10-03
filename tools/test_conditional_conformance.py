"""Known-result and adversarial tests for the experimental conditional contract."""
import copy
import itertools
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from conditional_conformance import ConditionalModel, ContentError, OUTCOMES, load_assessments, run_suite
from oval_result_truth_tables import aggregate_operator
from generate_capability_schema import generate
from validate_generated_capability_semantics import validate_assessment_capability_semantics

ROOT = Path(__file__).resolve().parents[1]
SUITE = ROOT / "tests/conditional-0.2.0"


class ConditionalConformanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = load_assessments(SUITE / "content")
        cls.model = ConditionalModel(cls.sources)

    def test_curated_content_and_complete_local_dependency_matrices(self):
        report = run_suite(SUITE)
        self.assertEqual(report["failed"], [])
        self.assertEqual(report["cases_checked"], 465)

    def test_intrinsic_applicability_complete_matrix(self):
        # Independent expected staging: applicability precedes every normal
        # guard/branch and false applicability has its established N/A meaning.
        for applicable, guard, then, otherwise in itertools.product(OUTCOMES, repeat=4):
            supplied = {f"conditional.applicability:test-{name}": value for name, value in
                        (("applicable", applicable), ("guard", guard), ("then", then), ("else", otherwise))}
            if applicable == "true":
                expected = then if guard == "true" else otherwise if guard == "false" else guard
            else:
                expected = "not_applicable" if applicable == "false" else applicable
            result = self.model.run("conditional.applicability", supplied)
            self.assertEqual(result["outcome"], expected)
            if applicable != "true":
                self.assertEqual(result["executed_tests"], ["conditional.applicability:test-applicable"])

    def test_explicit_na_preserves_non_boolean_conditions_and_branch_errors(self):
        for guard, branch in itertools.product(OUTCOMES, repeat=2):
            result = self.model.run("conditional.explicit-na", {
                "conditional.explicit-na:test-guard": guard, "conditional.explicit-na:test-then": branch})
            expected = branch if guard == "true" else "not_applicable" if guard == "false" else guard
            self.assertEqual(result["outcome"], expected)
            terminals = [n for n in result["trace"] if n["kind"] == "terminal"]
            self.assertEqual(len(terminals), int(guard == "false"))
            if terminals:
                self.assertIn("component is absent", terminals[0]["reason"])

    def test_shared_test_not_falsely_marked_unexecuted(self):
        result = self.model.run("conditional.shared", {
            "conditional.shared:test-guard": "true", "conditional.shared:test-then": "true"})
        guard_uses = [n for n in result["trace"] if n.get("test") == "test-guard"]
        self.assertEqual([n["reused"] for n in guard_uses], [False, True])
        self.assertTrue(all(n["outcome"] == "true" for n in guard_uses))
        skipped = [n for n in result["trace"] if n.get("reason") == "conditional_branch_not_selected"]
        self.assertEqual([n["path"] for n in skipped], ["conditional.shared/evaluate/else"])

    def test_dependency_reuse_preserves_invocation_identity(self):
        sources = copy.deepcopy(self.sources)
        sources["conditional.dependent"]["evaluate"]["then"] = {"assessment": "role"}
        model = ConditionalModel(sources)
        result = model.run("conditional.dependent", {"conditional.role:test-role": "true"},
                           target="server-a", bindings={"threshold": 7})
        self.assertEqual(result["executed_tests"], ["conditional.role:test-role"])
        uses = [n for n in result["trace"] if n["kind"] == "dependency"]
        self.assertEqual([n["reused"] for n in uses], [False, True])
        self.assertEqual(uses[0]["context"], uses[1]["context"])

    def test_target_and_binding_contexts_do_not_share_results(self):
        for target, binding, outcome in (("a", 1, "true"), ("b", 1, "false"), ("a", 2, "unknown")):
            result = self.model.run("conditional.dependent", {"conditional.role:test-role": outcome,
                         "conditional.dependent:test-then": "true", "conditional.dependent:test-else": "false"},
                         target=target, bindings={"threshold": binding})
            self.assertEqual(result["outcome"], outcome)
            self.assertEqual(result["context"], {"target": target, "bindings": {"threshold": binding}})
            self.assertFalse([n for n in result["trace"] if n["kind"] == "dependency"][0]["reused"])

    def test_missing_guard_result_is_error_and_never_else(self):
        result = self.model.run("conditional.local", {"conditional.local:test-else": "true"})
        self.assertEqual(result["outcome"], "error")
        self.assertEqual(result["diagnostics"][0]["code"], "missing_test_result")
        self.assertEqual(result["executed_tests"], ["conditional.local:test-guard"])

    def test_missing_selected_result_is_error_but_unselected_missing_is_allowed(self):
        result = self.model.run("conditional.local", {"conditional.local:test-guard": "true"})
        self.assertEqual(result["outcome"], "error")
        self.assertEqual(len(result["diagnostics"]), 1)
        result = self.model.run("conditional.local", {"conditional.local:test-guard": "false", "conditional.local:test-else": "true"})
        self.assertEqual(result["outcome"], "true")
        self.assertEqual(result["diagnostics"], [])

    def test_missing_test_in_unselected_branch_is_static_error(self):
        sources = copy.deepcopy(self.sources)
        sources["conditional.local"]["evaluate"]["else"] = {"test": "test-missing"}
        with self.assertRaisesRegex(ContentError, "missing_test"):
            ConditionalModel(sources)

    def test_undeclared_dependency_and_missing_dependency_fail(self):
        sources = copy.deepcopy(self.sources)
        sources["conditional.local"]["evaluate"]["else"] = {"assessment": "unsigned"}
        with self.assertRaisesRegex(ContentError, "undeclared_dependency"):
            ConditionalModel(sources)
        sources = copy.deepcopy(self.sources)
        del sources["conditional.role"]
        with self.assertRaisesRegex(ContentError, "missing_dependency"):
            ConditionalModel(sources)

    def test_cycles_in_unused_dependencies_are_rejected(self):
        sources = copy.deepcopy(self.sources)
        sources["conditional.role"]["dependencies"] = {"cycle": {
            "expected_id": "conditional.dependent", "expected_version": 1}}
        with self.assertRaisesRegex(ContentError, "dependency_cycle"):
            ConditionalModel(sources)

    def test_dependency_version_mismatch_is_rejected(self):
        sources = copy.deepcopy(self.sources)
        sources["conditional.dependent"]["dependencies"]["role"]["expected_version"] = 2
        with self.assertRaisesRegex(ContentError, "dependency_version"):
            ConditionalModel(sources)

    def test_mapping_order_does_not_change_results(self):
        reversed_sources = dict(reversed(list(self.sources.items())))
        result = ConditionalModel(reversed_sources).run("conditional.dependent", {
            "conditional.role:test-role": "false", "conditional.dependent:test-else": "true"})
        self.assertEqual(result["outcome"], "true")

    def test_invalid_shapes_and_missing_else_never_implicitly_pass(self):
        for node in ({"if": {"test": "test-guard"}, "then": {"test": "test-then"}},
                     {"all": []}, {"any": []}, {"if": True, "then": {}, "else": {}},
                     {"test": "test-guard", "command": "injected"}, {"input": "branch-name"},
                     {"not_applicable": {"reason": " "}}):
            sources = copy.deepcopy(self.sources)
            sources["conditional.local"]["evaluate"] = node
            with self.assertRaises(ContentError):
                ConditionalModel(sources)

    def test_invalid_fixture_outcome_is_not_coerced(self):
        for outcome in (True, False, None, {}, [], "pass"):
            if outcome is None:  # Absence of a terminal transport result is an explicit error.
                continue
            with self.assertRaisesRegex(ContentError, "invalid_fixture_outcome"):
                self.model.run("conditional.local", {"conditional.local:test-guard": outcome})

    def test_depth_budget_is_resource_limit_not_three_layer_language_restriction(self):
        sources = copy.deepcopy(self.sources)
        node = {"test": "test-guard"}
        for _ in range(20):
            node = {"not": node}
        sources["conditional.local"]["evaluate"] = node
        result = ConditionalModel(sources, max_depth=30).run("conditional.local", {"conditional.local:test-guard": "true"})
        self.assertEqual(result["outcome"], "true")
        with self.assertRaisesRegex(ContentError, "resource_limit"):
            ConditionalModel(sources, max_depth=10)

    def test_experimental_expression_schema_and_model_agree_on_curated_content(self):
        schema = json.loads((SUITE / "expression.schema.json").read_text())
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema)
        for assessment in self.sources.values():
            validator.validate(assessment["evaluate"])
            if "applicability" in assessment:
                validator.validate(assessment["applicability"])
        for node in ({"if": {}, "then": {}, "else": {}}, {"all": []}, {"input": "selector"},
                     {"not_applicable": {"reason": " "}}):
            self.assertFalse(validator.is_valid(node))

    def test_illustrative_test_state_sources_use_current_capability_contracts(self):
        mapping = json.loads((ROOT / "schema/v0.1.0/capability-mappings/variable.value.json").read_text())
        generated = generate(mapping, ROOT)
        common = json.loads((ROOT / "schema/v0.1.0/capability-common.schema.json").read_text())
        registry = Registry().with_resource(common["$id"], Resource.from_contents(common))
        validators = {k: Draft202012Validator(generated["$defs"][k], registry=registry) for k in ("test", "state")}
        for assessment in self.sources.values():
            self.assertEqual(validate_assessment_capability_semantics({"assessment": assessment}), [])
            for test in assessment["tests"].values():
                validators["test"].validate(test)
            for state in assessment["states"].values():
                validators["state"].validate(state)

    def test_normalizer_boolean_shape_has_six_state_counterexample(self):
        # Source expression: (G AND T) OR (NOT G AND E). G=error,
        # T=false, E=false produces false under inherited aggregation.
        left = aggregate_operator("AND", ["error", "false"])
        right = aggregate_operator("AND", ["error", "false"])
        original = aggregate_operator("OR", [left, right])
        candidate = self.model.run("conditional.local", {
            "conditional.local:test-guard": "error", "conditional.local:test-then": "false",
            "conditional.local:test-else": "false"})["outcome"]
        self.assertEqual(original, "false")
        self.assertEqual(candidate, "error")
        self.assertNotEqual(original, candidate)


if __name__ == "__main__":
    unittest.main()
