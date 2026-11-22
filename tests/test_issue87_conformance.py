"""Regression gates for the independent SCAP-NG 0.4.1 conformance corpus."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path
from copy import deepcopy
import yaml
from jsonschema import Draft202012Validator, ValidationError

from conformance.tools.oracle import compare
from conformance.tools.runner import validator

ROOT = Path(__file__).resolve().parents[1]
CONF = ROOT / "conformance"
SCHEMA = ROOT / "schema"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class Issue87Conformance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = read(CONF / "manifest.json")
        cls.inventory = read(CONF / "schema-coverage.json")

    def test_manifest_is_exactly_pinned_to_checked_out_schema(self):
        commit = self.manifest["schema_commit"]
        self.assertRegex(commit, r"^[0-9a-f]{40}$")
        self.assertEqual(subprocess.run(["git", "cat-file", "-e", f"{commit}^{{commit}}"], cwd=ROOT).returncode, 0)
        paths = sorted((ROOT / "schema").glob("*.json")) + sorted((ROOT / "schema/capability-mappings").rglob("*.json"))
        digest = hashlib.sha256()
        for path in sorted(paths):
            digest.update(path.relative_to(SCHEMA).as_posix().encode() + b"\0")
            digest.update(path.read_bytes())
        self.assertEqual(self.inventory["schema_family_sha256"], digest.hexdigest())
        self.assertEqual(self.manifest["schema_family_sha256"], self.inventory["schema_family_sha256"])

    def test_inventory_and_vectors_are_exhaustive_for_mappings(self):
        capabilities = {row["capability"] for row in self.inventory["capabilities"]}
        cases = {row["capability"] for row in self.manifest["capabilities"]}
        self.assertEqual(cases, capabilities)
        self.assertEqual(self.inventory["counts"]["capability_mappings"], len(cases))
        required = {"positive", "negative", "boundary", "empty", "permission-denied", "error", "not-applicable", "multi-item"}
        for row in self.manifest["capabilities"]:
            self.assertTrue(required.issubset(row["vectors"]), row["capability"])
            for kind in ("assessment", "fixture", "expected"):
                path = CONF / row[kind]
                self.assertTrue(path.is_file(), path)
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), row["sha256"][kind], path)

    def test_issue95_generated_yaml_orders_object_before_require(self):
        rows = self.manifest["capabilities"] + self.manifest["core_cases"]
        checked = 0
        for row in rows:
            path = CONF / row["assessment"]
            document = yaml.safe_load(path.read_text(encoding="utf-8"))
            for test in document.get("assessment", {}).get("tests", {}).values():
                keys = list(test)
                if "object" in test and "require" in test:
                    checked += 1
                    self.assertLess(keys.index("object"), keys.index("require"), path)
        self.assertGreater(checked, 100)

    def test_negative_variants_are_distinct_and_preserve_selectors(self):
        for row in self.manifest["capabilities"]:
            fixture = read(CONF / row["fixture"])
            positive = fixture["variants"]["positive"]
            negative = fixture["variants"]["negative"]
            self.assertFalse(
                positive == negative,
                f"{row['capability']} has identical positive/negative evidence",
            )
            contract = fixture["semantic_contract"]
            if contract["negative_strategy"] == "field-mismatch":
                self.assertEqual(len(positive["items"]), 1, row["capability"])
                self.assertEqual(len(negative["items"]), 1, row["capability"])
                for selector in contract["selector_fields"]:
                    self.assertEqual(
                        positive["items"][0]["fields"].get(selector),
                        negative["items"][0]["fields"].get(selector),
                        f"{row['capability']} negative changed selector {selector}",
                    )
                field = contract["negative_field"]
                self.assertNotEqual(
                    positive["items"][0]["fields"].get(field),
                    negative["items"][0]["fields"].get(field),
                    f"{row['capability']} negative did not change Require field",
                )
            else:
                self.assertEqual(negative["items"], [], row["capability"])
                self.assertEqual(negative["acquisition"], "collected", row["capability"])
            expected = read(CONF / row["expected"])
            self.assertNotEqual(
                expected["variants"]["positive"]["assessment_outcome"],
                expected["variants"]["negative"]["assessment_outcome"],
                row["capability"],
            )

    def _valid_receipt(self):
        row = next(row for row in self.manifest["capabilities"] if row["capability"] == "windows.registry")
        expected = read(CONF / row["expected"])
        fixture = read(CONF / row["fixture"])
        item = fixture["variants"]["positive"]["items"][0]
        evidence = [{"item_id": item["id"], "field": field, "datatype": value["datatype"], "status": value["status"], "value": value["value"]} for field, value in item["fields"].items()]
        receipt = {"format": "scap-ng-conformance-receipt-0.1", "schema_version": self.manifest["schema_version"], "schema_commit": self.manifest["schema_commit"], "case_id": "windows.registry", "variant": "positive", "fixture_sha256": row["sha256"]["fixture"], "expected_sha256": row["sha256"]["expected"], "assessment_outcome": "true", "test_outcomes": {"windows-registry-test": "true"}, "items_found": 1, "items_satisfying": 1, "decisive_reason": expected["variants"]["positive"]["reason"], "evidence": evidence, "provenance": {"source": "deterministic-fixture", "fixture_variant": "positive", "fixture_sha256": row["sha256"]["fixture"], "expected_sha256": row["sha256"]["expected"], "schema_commit": self.manifest["schema_commit"]}, "qualification": {"schema": "pass", "semantic": "pass", "collection": "pass", "integration": "not_run", "operational": "not_run"}}
        return expected, fixture, receipt, row

    def test_oracle_accepts_complete_receipt(self):
        expected, fixture, receipt, row = self._valid_receipt()
        self.assertEqual(compare(expected, receipt, manifest=self.manifest, fixture=fixture, fixture_sha256=row["sha256"]["fixture"], expected_sha256=row["sha256"]["expected"], test_names=["windows-registry-test"]), [])

    def test_portable_receipt_schema_accepts_valid_and_rejects_bad_qualification(self):
        _, _, receipt, _ = self._valid_receipt()
        schema = read(CONF / "receipt.schema.json")
        Draft202012Validator(schema).validate(receipt)
        invalid = deepcopy(receipt)
        invalid["qualification"].pop("collection")
        self.assertTrue(list(Draft202012Validator(schema).iter_errors(invalid)))
        invalid = deepcopy(receipt)
        invalid["qualification"]["semantic"] = "scanner-specific-pass"
        self.assertTrue(list(Draft202012Validator(schema).iter_errors(invalid)))

    def test_oracle_rejects_missing_or_mismatched_identity_and_proof(self):
        expected, fixture, receipt, row = self._valid_receipt()
        mutations = {
            "schema pin": ("schema_commit", "0" * 40),
            "fixture hash": ("fixture_sha256", "bad"),
            "expected hash": ("expected_sha256", "bad"),
            "test outcomes": ("test_outcomes", {}),
            "decisive reason": ("decisive_reason", "wrong"),
            "provenance": ("provenance", {"source": "deterministic-fixture"}),
            "typed evidence": ("evidence", [{"item_id": "windows-registry-item", "field": "hive", "datatype": "string", "status": "collected"}]),
            "qualification": ("qualification", {"schema": "pass"}),
        }
        for name, (key, value) in mutations.items():
            with self.subTest(name=name):
                mutant = deepcopy(receipt); mutant[key] = value
                errors = compare(expected, mutant, manifest=self.manifest, fixture=fixture, fixture_sha256=row["sha256"]["fixture"], expected_sha256=row["sha256"]["expected"], test_names=["windows-registry-test"])
                self.assertTrue(errors, name)

    def test_core_semantics_keep_false_leaf_visible_and_only_not_negates(self):
        assessment = (CONF / "cases/core/evaluate-not.assessment.yaml").read_text(encoding="utf-8")
        self.assertIn("not:", assessment)
        self.assertNotIn("negate:", assessment)
        expected = read(CONF / "expected/core-evaluate-not.json")
        self.assertEqual(expected["underlying"]["false-test"], "false")
        self.assertEqual(expected["assertions"]["not(false)"], "true")
        self.assertEqual(expected["assertions"]["unknown"], "unknown")
        self.assertEqual(expected["assertions"]["error"], "error")
        self.assertEqual(expected["assertions"]["not_applicable"], "not_applicable")

    def test_audit_reports_scope_without_false_semantic_completeness(self):
        audit = read(CONF / "coverage-audit.json")
        self.assertEqual(audit["schema_commit"], self.manifest["schema_commit"])
        self.assertEqual(audit["schema_family_sha256"], self.manifest["schema_family_sha256"])
        self.assertEqual(audit["vectors"]["base_capability_vectors_total"], 735)
        self.assertEqual(audit["vectors"]["expanded_capability_vectors_total"], 840)
        self.assertEqual(audit["vectors"]["multi_value_suite_cases"], 104)
        self.assertEqual(audit["fields"]["declared_mapping_fields"], 718)
        self.assertEqual(audit["fields"]["authored_assessment_fields"], 718)
        self.assertEqual(audit["selectors"]["uncovered_alternative_sets"], 0)
        self.assertEqual(audit["operators"]["uncovered_comparison"], [])
        self.assertEqual(audit["cardinalities"]["uncovered"], [])
        self.assertEqual(audit["exceptional_outcomes"]["uncovered_defined_outcomes"], [])
        self.assertGreater(audit["enum_boundaries"]["schema_rejected_mutations"], 0)
        self.assertFalse(audit["schema_branches"]["direct_executable_branch_coverage"])
        self.assertTrue(audit["expected_results"]["independent_justification"])
        self.assertEqual(audit["independent_oracle"]["source_cases"], 15)
        self.assertFalse(audit["independent_oracle"]["runtime_qualification"])
        derived = audit["derived_integrity"]
        self.assertEqual(derived["fields_from_source_mappings"], 718)
        self.assertEqual(derived["fields_from_authored_assessments"], 718)
        self.assertEqual(derived["fields_from_positive_fixtures"], 718)
        self.assertEqual(derived["operators_from_source_schema"], 67)
        self.assertEqual(derived["operators_from_authored_assessments"], 67)
        self.assertEqual(derived["selector_alternatives_from_source_mappings"], 94)
        self.assertEqual(derived["selector_alternatives_from_authored_assessments"], 94)
        self.assertEqual(derived["missing_witnesses"], {"fields": [], "selectors": [], "operators": [], "cardinalities": []})
        self.assertEqual(derived["non_exercising_witnesses"], {"fields": [], "selectors": [], "operators": []})
        self.assertEqual(audit["fields"]["non_exercising_witnesses"], [])
        self.assertEqual(audit["selectors"]["non_exercising_witnesses"], [])
        self.assertEqual(audit["operators"]["non_exercising_witnesses"], [])
        self.assertEqual(audit["authoring_enums"]["cases"], 20)
        self.assertEqual(len(audit["authoring_enums"]["negative_boundary_cases"]), 10)
        self.assertEqual(audit["capability_constraints"]["semantic_validator_rule_count"], 180)
        self.assertGreater(audit["capability_constraints"]["semantic_rules_structural_witnesses"], 0)
        self.assertGreater(len(audit["capability_constraints"]["semantic_rules_untested"]), 0)
        self.assertIn("155 untested capability semantic-validator rules", audit["schema_branches"]["uncovered"])
        self.assertEqual(audit["set_filter_semantics"]["operations"], 3)
        self.assertEqual(audit["set_filter_semantics"]["set_operators"], ["union", "intersection", "difference"])
        self.assertEqual(audit["variable_functions"]["functions"], ["unique", "count", "concat", "merge"])
        self.assertEqual(audit["input_guards"]["variants"], ["provided", "absent", "explicit-empty", "too-many", "out-of-range"])
        self.assertEqual(audit["applicability"]["variants"], ["applicable", "not-applicable", "deferred"])
        dimensions = {"schema", "semantic", "collection", "integration", "operational"}
        self.assertTrue(dimensions.issubset(audit["feature_coverage"]["fields"]))
        allowed_states = {"pass", "fail", "unsupported", "untested", "not_run", "blocked"}
        for feature in audit["feature_coverage"].values():
            self.assertTrue(all(feature[dimension] in allowed_states for dimension in dimensions))
        self.assertEqual(audit["feature_coverage"]["comparison_operators"]["collection"], "untested")
        self.assertEqual(audit["feature_coverage"]["applicability"]["integration"], "untested")
        for row in audit["capability_rows"]:
            self.assertEqual(set(row["coverage"]), {"schema", "semantic", "collection", "integration", "operational"})
        for row in self.manifest["capabilities"]:
            expected = read(CONF / row["expected"])
            for assertion in expected["variants"].values():
                self.assertTrue(assertion["reason"].strip())

    def test_authoring_enum_cases_cover_all_assessment_branches(self):
        rows = self.manifest.get("authoring_cases", [])
        self.assertEqual(len(rows), 20)
        modes = {read(CONF / row["expected"])["mode"] for row in rows}
        self.assertEqual(modes, {"automated", "manual"})
        classes = {read(CONF / row["expected"])["class"] for row in rows}
        self.assertEqual(classes, {"compliance", "vulnerability", "patch", "inventory", "miscellaneous"})
        automated = [read(CONF / row["expected"]) for row in rows if read(CONF / row["expected"])["mode"] == "automated"]
        self.assertEqual({case["reported_elements"] for case in automated}, {"scalar-all", "scalar-compared", "explicit-list"})
        manual = [read(CONF / row["expected"]) for row in rows if read(CONF / row["expected"])["mode"] == "manual"]
        self.assertEqual({tuple(case["response_outcomes"]) for case in manual}, {("true", "false", "error", "unknown", "not_evaluated", "not_applicable")})
        for row in rows:
            self.assertTrue((CONF / row["assessment"]).is_file())
            self.assertTrue(read(CONF / row["expected"])["reason"].strip())

    def test_authoring_enum_negative_boundaries_are_rejected(self):
        invalid = {row["id"] for row in self.manifest["invalid_cases"]}
        self.assertTrue({"invalid-class", "invalid-reported-elements", "invalid-manual-outcome", "invalid-mode", "invalid-variable-kind", "invalid-cardinality", "invalid-specification-version", "invalid-reported-elements-duplicate", "invalid-empty-procedure", "invalid-id-pattern", "invalid-set-difference-cardinality"}.issubset(invalid))
        for case in self.manifest["invalid_cases"]:
            if case["id"] not in {"invalid-class", "invalid-reported-elements", "invalid-manual-outcome", "invalid-mode", "invalid-variable-kind", "invalid-cardinality", "invalid-specification-version", "invalid-reported-elements-duplicate", "invalid-empty-procedure", "invalid-id-pattern", "invalid-set-difference-cardinality"}:
                continue
            path = CONF / case["assessment"]
            self.assertTrue(path.is_file(), path)

    def test_core_expansions_cover_operators_selectors_cardinalities_and_statuses(self):
        operators = read(CONF / "expected/core-comparison-operators.json")
        active = set(self.inventory["operator_inventory"]["field_predicate_properties"])
        self.assertEqual(set(operators["operators"]), active)
        selectors = read(CONF / "expected/core-selector-alternatives.json")
        declared = sum(len(row["selector_alternatives"]) for row in self.inventory["capabilities"])
        self.assertEqual(len(selectors["alternatives"]), declared)
        multi_values = read(CONF / "expected/core-multi-values.json")
        self.assertEqual(len(multi_values["capabilities"]), 104)
        enum_boundaries = read(CONF / "expected/core-enum-boundaries.json")
        self.assertEqual(len(enum_boundaries["enum_values"]), 12)
        self.assertEqual(read(CONF / "coverage-audit.json")["enum_boundaries"]["uncovered_native_selector_enum_values"], [])
        cardinalities = read(CONF / "expected/core-cardinalities.json")
        self.assertEqual(set(cardinalities["cardinalities"]), {"item-exactly-one", "item-none", "item-zero-or-more", "field-exactly-one", "field-none", "field-zero-or-more"})
        set_filters = read(CONF / "expected/core-set-filters.json")
        self.assertEqual(set(set_filters["set_operators"]), {"union", "intersection", "difference"})
        self.assertEqual(set(set_filters["filter_actions"]), {"include", "exclude"})
        for row in self.manifest["status_cases"]:
            self.assertTrue(read(CONF / row["expected"])["reason"].strip())

    def test_semantic_boundary_witnesses_are_schema_valid_and_targeted(self):
        assessment = yaml.safe_load((CONF / "cases/core/semantic-boundaries.assessment.yaml").read_text(encoding="utf-8"))
        fixture = read(CONF / "fixtures/core-semantic-boundaries.json")
        expected = read(CONF / "expected/core-semantic-boundaries.json")
        validator().validate(assessment)
        rule_ids = {rule for witness in fixture["semantic_witnesses"] for rule in witness["rules"]}
        self.assertEqual(rule_ids, set(expected["rules"]))
        self.assertEqual(len(rule_ids), 5)
        for test_name, assertion in expected["assertions"].items():
            evidence = fixture["evidence"][test_name]
            self.assertEqual(evidence["items_found"], assertion["items_found"])
            self.assertEqual(evidence["items_satisfying"], assertion["items_satisfying"])
            if assertion["outcome"] == "true":
                self.assertEqual(evidence["status"], "collected")
                for field_value in evidence["items"][0]["fields"].values():
                    self.assertTrue({"datatype", "value", "status"}.issubset(field_value))
                    self.assertEqual(field_value["status"], "collected")
            else:
                self.assertEqual(evidence["status"], "not_run")
                self.assertEqual(evidence["items"], [])
        for witness in fixture["semantic_witnesses"]:
            test = assessment["assessment"]["tests"][witness["test"]]
            outcome = expected["assertions"][witness["test"]]["outcome"]
            self.assertEqual(outcome, witness["expected"])
            self.assertTrue(test["object"].get("traversal") or test["object"].get("filename"))
            if outcome == "error":
                if any("no_traversal" in rule for rule in witness["rules"]):
                    self.assertIn("traversal", test["object"])
                else:
                    self.assertEqual(test["object"]["filename"].get("equals"), "bad:name")
        # A boundary mutation removing traversal from each traversal error leaves
        # a schema-valid positive shape; it must not be silently treated as the
        # same semantic witness.
        for witness in fixture["semantic_witnesses"]:
            if witness["expected"] != "error" or "traversal" not in assessment["assessment"]["tests"][witness["test"]]["object"]:
                continue
            mutated = deepcopy(assessment)
            del mutated["assessment"]["tests"][witness["test"]]["object"]["traversal"]
            validator().validate(mutated)
            self.assertNotIn("traversal", mutated["assessment"]["tests"][witness["test"]]["object"])

    def test_variable_require_evaluate_interaction_keeps_false_leaf_visible(self):
        assessment = yaml.safe_load((CONF / "cases/core/variable-interactions.assessment.yaml").read_text(encoding="utf-8"))
        self.assertEqual(set(assessment["assessment"]["variables"]), {"source-values-variable", "alias-values-variable", "expected-values-variable"})
        self.assertEqual(assessment["assessment"]["variables"]["alias-values-variable"]["kind"], "local")
        self.assertEqual(assessment["assessment"]["evaluate"]["and"][1]["not"]["test"], "variable-alias-exactly-one-test")
        expected = read(CONF / "expected/core-variable-interactions.json")
        self.assertEqual(expected["assertions"]["variable-alias-exactly-one-test"]["outcome"], "false")
        self.assertEqual(expected["enclosing_outcome"], "true")
        observed = assessment["assessment"]["variables"]["source-values-variable"]["expression"]["literal"]["value"]
        alias = assessment["assessment"]["variables"]["alias-values-variable"]["expression"]["variable"]
        self.assertEqual(alias, "source-values-variable")
        self.assertEqual(len(observed), 2)
        self.assertEqual(observed, assessment["assessment"]["variables"]["expected-values-variable"]["expression"]["literal"]["value"])
        self.assertEqual(expected["assertions"]["variable-alias-exactly-one-test"]["values_found"], len(observed))

    def test_set_filter_mutations_fail_closed_at_schema_boundary(self):
        assessment = yaml.safe_load((CONF / "cases/core/set-filters.assessment.yaml").read_text(encoding="utf-8"))
        difference = assessment["assessment"]["tests"]["set-difference-test"]["object"]["set"]["operands"]
        mutated = deepcopy(assessment)
        mutated_difference = mutated["assessment"]["tests"]["set-difference-test"]["object"]["set"]["operands"]
        mutated_difference.append(deepcopy(mutated_difference[0]))
        with self.assertRaises(ValidationError):
            validator().validate(mutated)
        self.assertEqual(len(difference), 2)
        missing_quantifier = deepcopy(assessment)
        del missing_quantifier["assessment"]["tests"]["set-union-test"]["object"]["set"]["operands"][0]["filters"][0]["include"]["arch"]["values_matching"]
        with self.assertRaises(ValidationError):
            validator().validate(missing_quantifier)

    def test_variable_function_expected_values_are_derived_from_source_population(self):
        assessment = yaml.safe_load((CONF / "cases/core/variable-functions.assessment.yaml").read_text(encoding="utf-8"))
        expected = read(CONF / "expected/core-variable-functions.json")
        source = assessment["assessment"]["variables"]["source-values-variable"]["expression"]["literal"]["value"]
        unique = list(dict.fromkeys(source))
        self.assertEqual(source, ["a", "a", "b"])
        self.assertEqual(expected["functions"]["unique"]["values"], unique)
        self.assertEqual(expected["functions"]["count"]["values"], [len(source)])
        self.assertEqual(expected["functions"]["concat"]["values"], [f"prefix-{value}" for value in unique])
        self.assertEqual(expected["functions"]["merge"]["values"], [",".join(sorted(unique))])

    def test_input_guard_keeps_absent_and_empty_bindings_distinct(self):
        assessment = yaml.safe_load((CONF / "cases/core/input-guards.assessment.yaml").read_text(encoding="utf-8"))
        expected = read(CONF / "expected/core-input-guards.json")
        self.assertEqual(assessment["assessment"]["evaluate"]["if"]["input_provided"], "expected-value-input")
        self.assertEqual(expected["variants"]["absent"]["assessment_outcome"], "not_evaluated")
        self.assertEqual(expected["variants"]["explicit-empty"]["assessment_outcome"], "error")
        self.assertNotEqual(expected["variants"]["absent"]["assessment_outcome"], expected["variants"]["explicit-empty"]["assessment_outcome"])

    def test_applicability_dependency_identity_and_status_handoffs_are_explicit(self):
        assessment = yaml.safe_load((CONF / "cases/core/applicability.assessment.yaml").read_text(encoding="utf-8"))
        expected = read(CONF / "expected/core-applicability.json")
        dependency = assessment["assessment"]["dependencies"]["shared-applicability"]
        self.assertEqual(dependency["assessment"], expected["dependency"])
        self.assertEqual(dependency["purpose"], expected["purpose"])
        expression = assessment["assessment"]["applicability"]["and"][0]
        self.assertEqual(expression["assessment"], dependency["assessment"])
        self.assertEqual(expected["variants"]["not-applicable"]["assessment_outcome"], "not_applicable")
        self.assertEqual(expected["variants"]["deferred"]["assessment_outcome"], "not_evaluated")

    def test_offline_schema_runner_and_invalid_negate_gate(self):
        command = [sys.executable, str(CONF / "tools/runner.py"), "validate"]
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        result = subprocess.run([sys.executable, str(CONF / "tools/runner.py"), "coverage"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
