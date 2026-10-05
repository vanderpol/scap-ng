#!/usr/bin/env python3
"""Draft schema, callback execution and real package integration regressions."""
import copy
import itertools
import json
from pathlib import Path
import tempfile
import unittest

import yaml
from assessment_expression import AssessmentExpressionEvaluator, ContentError, OUTCOMES, load_assessments
from conditional_conformance import ConditionalModel
from scap_ng_content_compiler import compile_benchmark, write_bundle, verify_bundle
from validate_native_json_schemas import build_validators, document_errors, schema_store, validator

ROOT = Path(__file__).resolve().parents[1]
SUITE = ROOT / "tests/conditional-0.2.0"


class ConditionalIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = load_assessments(SUITE / "content")
        cls.validators = build_validators(ROOT / "schema/v0.2.0")
        cls.result_validator = validator(ROOT / "schema/v0.2.0", "expression-result.schema.json", schema_store(ROOT / "schema/v0.2.0"))

    def draft(self, assessment):
        doc = {"assessment": copy.deepcopy(assessment)}
        doc["assessment"]["specification"] = {"id": "scap-ng.pre-alpha.assessment", "version": "0.2.0"}
        for test in doc["assessment"].get("tests", {}).values():
            test["reported_elements"] = "all"
            if "existence" in test and "check_existence" not in test:
                test["check_existence"] = test.pop("existence")
            if "match" in test and "check" not in test:
                test["check"] = test.pop("match")
        return doc

    def schema_errors(self, doc):
        return list(document_errors(self.validators["assessment.schema.json"], doc))

    def tree(self, root, entry="conditional.dependent", change=None):
        bench = root / "bench"
        def dump(path, doc):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")
        dump(bench / "benchmark.yaml", {"benchmark": {"id": "conditional.benchmark", "version": {"value": "1"}, "rules": ["R1"], "profiles": []}})
        entry_file = None
        for path in (SUITE / "content").glob("*.assessment.yaml"):
            doc = self.draft(yaml.safe_load(path.read_text())["assessment"])
            if change:
                change(doc["assessment"])
            if doc["assessment"]["id"] == entry:
                entry_file = path.name
            dump(bench / "assessments" / path.name, doc)
        dump(bench / "rules/R1.rule.yaml", {"rule": {
            "id": "R1", "assessment_choices": {"automated": {"assessment": "../assessments/" + entry_file}},
            "default_assessment_choice": "automated"}})
        return bench

    def test_all_fourteen_sources_validate_in_versioned_draft(self):
        self.assertEqual(len(self.sources), 14)
        for assessment in self.sources.values():
            with self.subTest(assessment=assessment["id"]):
                self.assertFalse(self.schema_errors(self.draft(assessment)))

    def test_schema_rejects_incomplete_conditional_and_empty_na_reason(self):
        doc = self.draft(self.sources["conditional.local"])
        for expr in [{"if": {"test": "test-guard"}, "then": {"test": "test-then"}},
                     {"not_applicable": {"reason": "  "}}, {"all": []}, {"if": {}, "then": {}, "else": {}}]:
            doc["assessment"]["evaluate"] = expr
            self.assertTrue(self.schema_errors(doc))

    def test_callback_runtime_complete_guard_matrix(self):
        oracle = json.loads((SUITE / "guard-table.json").read_text())
        engine = AssessmentExpressionEvaluator(self.sources)
        for guard, then, otherwise in itertools.product(OUTCOMES, repeat=3):
            calls = []
            def provider(identity, name, context):
                calls.append(name)
                return {"test-guard": guard, "test-then": then, "test-else": otherwise}[name]
            actual = engine.run("conditional.local", provider)
            self.result_validator.validate(actual)
            selected = oracle[guard]["selected_branch"]
            self.assertEqual(actual["outcome"], {"then": then, "else": otherwise}.get(selected, oracle[guard]["outcome"]))
            self.assertEqual(calls, ["test-guard"] + (["test-" + selected] if selected else []))

    def test_actual_constant_boolean_tests_are_lazy(self):
        sources = copy.deepcopy(self.sources)
        sources["conditional.local"]["variables"]["guard"]["value"] = False
        sources["conditional.local"]["variables"]["else"]["value"] = False
        calls = []
        def provider(identity, name, context):
            # Bounded actual-content adapter, not controlled terminal outcomes.
            calls.append(name)
            self.assertNotEqual(name, "test-then")
            assessment = sources[identity]
            test = assessment["tests"][name]
            observed = assessment["variables"][test["variable"]]["value"]
            expected = assessment["states"][test["states"][0]]["state"]["value"]
            return "true" if observed == expected else "false"
        result = AssessmentExpressionEvaluator(sources).run("conditional.local", provider)
        self.assertEqual(result["outcome"], "false")
        self.assertEqual(calls, ["test-guard", "test-else"])

    def test_runtime_result_does_not_disclose_binding_values(self):
        seen = []
        def provider(identity, name, context):
            seen.append(context["bindings"]["secret"])
            context["bindings"]["secret"] = "provider-mutation"
            return "true"
        bindings = {"secret": "private-binding-value"}
        result = AssessmentExpressionEvaluator(self.sources).run("conditional.dependent", provider, bindings=bindings)
        self.assertNotIn("private-binding-value", json.dumps(result))
        self.assertEqual(bindings["secret"], "private-binding-value")
        self.assertTrue(all(v == "private-binding-value" for v in seen))

    def test_one_and_odd_keep_six_state_aggregation(self):
        sources = copy.deepcopy(self.sources)
        engine = None
        for operator, expected in [("one", "false"), ("odd", "false")]:
            sources["conditional.local"]["evaluate"] = {operator: [{"test": "test-guard"}, {"test": "test-then"}]}
            self.assertFalse(self.schema_errors(self.draft(sources["conditional.local"])))
            engine = AssessmentExpressionEvaluator(sources)
            self.assertEqual(engine.run("conditional.local", lambda *args: "true")["outcome"], expected)
            self.assertEqual(engine.run("conditional.local", lambda *args: "error")["outcome"], "error")

    def test_manual_dependency_preserves_normalized_six_state_results(self):
        sources = copy.deepcopy(self.sources)
        sources["conditional.role"] = {"id": "conditional.role", "version": 1, "mode": "manual"}
        engine = AssessmentExpressionEvaluator(sources)
        for outcome in OUTCOMES:
            result = engine.run("conditional.dependent", lambda *args: "true", evaluate_manual=lambda *args: outcome)
            expected = "true" if outcome in ("true", "false") else outcome
            self.assertEqual(result["outcome"], expected)
        with self.assertRaisesRegex(ContentError, "missing_manual_provider"):
            engine.run("conditional.dependent", lambda *args: "true")

    def test_compiler_packages_dependency_closure_and_preserves_expression(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            benchmark, members, index = compile_benchmark(root, self.tree(root))
            self.assertIn("conditional.role", index)
            doc = json.loads(members[index["conditional.dependent"]["path"]])["assessment"]
            self.assertEqual(doc["dependencies"]["role"]["assessment"], "conditional.role")
            self.assertEqual(doc["dependencies"]["role"]["expected_version"], 1)
            self.assertEqual(doc["evaluate"], self.sources["conditional.dependent"]["evaluate"])
            package = root / "conditional.scapng"
            write_bundle(package, benchmark, members, index, sign_self_signed=False, provenance={})
            self.assertEqual(verify_bundle(package)["benchmark_id"], "conditional.benchmark")
            graph = {identity: json.loads(members[row["path"]])["assessment"]
                     for identity, row in index.items() if row["type"] == "assessment"}
            result = AssessmentExpressionEvaluator(graph).run("conditional.dependent", lambda *args: "true")
            self.result_validator.validate(result)
            self.assertEqual(result["outcome"], "true")

    def test_compiler_rejects_missing_reference_in_unselected_branch(self):
        def change(a):
            if a["id"] == "conditional.local":
                a["evaluate"]["else"] = {"test": "not-declared"}
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with self.assertRaisesRegex(ContentError, "missing_test"):
                compile_benchmark(root, self.tree(root, "conditional.local", change))

    def test_compiler_rejects_dependency_cycle_even_when_unused(self):
        def change(a):
            if a["id"] == "conditional.role":
                a["dependencies"] = {"back": {"assessment": "dependent.assessment.yaml", "expected_id": "conditional.dependent", "expected_version": 1}}
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with self.assertRaisesRegex(ValueError, "dependency cycle"):
                compile_benchmark(root, self.tree(root, change=change))

    def test_compiler_rejects_dependency_version_mismatch(self):
        def change(a):
            if a["id"] == "conditional.dependent":
                a["dependencies"]["role"]["expected_version"] = 2
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with self.assertRaisesRegex(ValueError, "expected_version mismatch"):
                compile_benchmark(root, self.tree(root, change=change))

    def test_unused_dependencies_are_packaged_and_pinned(self):
        def change(a):
            if a["id"] == "conditional.local":
                a["dependencies"] = {"unused": {"assessment": "role.assessment.yaml", "expected_id": "conditional.role", "expected_version": 1, "purpose": "applicability"}}
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, members, index = compile_benchmark(root, self.tree(root, "conditional.local", change))
            self.assertIn("conditional.role", index)
            compiled = json.loads(members[index["conditional.local"]["path"]])["assessment"]
            self.assertEqual(compiled["dependencies"]["unused"]["expected_id"], "conditional.role")

    def test_shared_nested_dependency_keeps_compiled_bindings(self):
        def change(a):
            if a["id"] == "conditional.dependent":
                a["dependencies"]["role-again"] = copy.deepcopy(a["dependencies"]["role"])
            if a["id"] == "conditional.role":
                a["dependencies"] = {"nested": {"assessment": "local.assessment.yaml", "expected_id": "conditional.local", "expected_version": 1, "purpose": "assessment"}}
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            benchmark, members, index = compile_benchmark(root, self.tree(root, change=change))
            role = json.loads(members[index["conditional.role"]["path"]])["assessment"]
            self.assertEqual(role["dependencies"]["nested"]["assessment"], "conditional.local")
            write_bundle(root / "shared.scapng", benchmark, members, index, sign_self_signed=False, provenance={})

    def test_unused_dependency_missing_source_and_identity_mismatch(self):
        for dependency, error in [
            ({"assessment": "missing.assessment.yaml", "expected_id": "conditional.missing", "expected_version": 1, "purpose": "assessment"}, "unresolved Assessment reference"),
            ({"assessment": "role.assessment.yaml", "expected_id": "wrong-id", "expected_version": 1, "purpose": "applicability"}, "expected_id mismatch"),
        ]:
            def change(a):
                if a["id"] == "conditional.local":
                    a["dependencies"] = {"unused": dependency}
            with tempfile.TemporaryDirectory() as td:
                root = Path(td)
                with self.assertRaisesRegex(ValueError, error):
                    compile_benchmark(root, self.tree(root, "conditional.local", change))

    def test_result_schema_rejects_inconsistent_guard_selection(self):
        from jsonschema import ValidationError
        result = AssessmentExpressionEvaluator(self.sources).run("conditional.local", lambda *args: "error")
        branch = next(n for n in result["trace"] if n["kind"] == "conditional")
        branch["selected_branch"] = "else"
        with self.assertRaises(ValidationError):
            self.result_validator.validate(result)

    def test_bundle_verifier_rejects_unresolved_dependency_with_valid_hashes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            benchmark, members, index = compile_benchmark(root, self.tree(root))
            # Rebuild a structurally/integrity-valid bundle with a semantic defect.
            row = index["conditional.dependent"]
            doc = json.loads(members[row["path"]])
            doc["assessment"]["dependencies"]["role"]["assessment"] = "absent"
            from scap_ng_content_compiler import canonical_json
            import hashlib
            members[row["path"]] = canonical_json(doc)
            row["size"] = len(members[row["path"]])
            row["sha256"] = hashlib.sha256(members[row["path"]]).hexdigest()
            with self.assertRaisesRegex(ValueError, "does not resolve"):
                write_bundle(root / "invalid.scapng", benchmark, members, index, sign_self_signed=False, provenance={})


if __name__ == "__main__":
    unittest.main()
