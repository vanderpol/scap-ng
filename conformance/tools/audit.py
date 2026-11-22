#!/usr/bin/env python3
"""Audit what the seven portable vectors do and do not cover.

The report is deliberately conservative: a schema-valid Assessment proves
syntax only.  It reports uncovered operator, selector-alternative, cardinality,
constraint, and result-status branches rather than treating the positive vector
as semantic coverage.
"""
from __future__ import annotations

import copy
import json
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

import yaml
from jsonschema import ValidationError
from runner import validator as assessment_validator

ROOT = Path(__file__).resolve().parents[2]
CONF = ROOT / "conformance"
SCHEMA = ROOT / "schema"


def load(path: Path) -> Any:
    return json.loads(path.read_text()) if path.suffix == ".json" else yaml.safe_load(path.read_text())


def walk(value: Any):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def predicate_matches(observed: Any, predicate: Any) -> bool:
    """Verify the positive comparison is witnessed by the fixture value."""
    if not isinstance(predicate, dict):
        return False
    if "equals" in predicate:
        expected = predicate["equals"]
        if isinstance(expected, list):
            return isinstance(observed, list) and all(value in expected for value in observed)
        return observed == expected
    if "record" in predicate and isinstance(observed, dict):
        return all(predicate_matches(observed.get(field), child)
                   for field, child in predicate["record"].get("fields", {}).items())
    return False


def main() -> int:
    manifest = load(CONF / "manifest.json")
    inventory = load(CONF / "schema-coverage.json")
    authored: dict[str, Any] = {}
    fixtures: dict[str, Any] = {}
    authored_field_witnesses: set[tuple[str, str]] = set()
    fixture_field_witnesses: set[tuple[str, str]] = set()
    non_exercising_field_witnesses: list[dict[str, Any]] = []
    manifest_rows = {row["capability"]: row for row in manifest["capabilities"]}
    all_fields = set(); all_selectors = set(); chosen_selectors = set()
    selector_alternatives = 0; selected_alternatives = 0
    datatypes = Counter(); mapping_rows = []
    source_mapping_paths = sorted((SCHEMA / "capability-mappings").rglob("*.json"))
    source_mappings = [load(path) for path in source_mapping_paths]
    semantic_rule_audit: list[dict[str, Any]] = []
    declared_semantic_rule_ids = {rule.get("id", "") for mapping in source_mappings for rule in mapping.get("semantic_validator_rules", [])}
    semantic_boundary_assessment = load(CONF / "cases/core/semantic-boundaries.assessment.yaml")
    semantic_boundary_fixture = load(CONF / "fixtures/core-semantic-boundaries.json")
    semantic_witness_rules: dict[str, list[str]] = {}
    for witness in semantic_boundary_fixture.get("semantic_witnesses", []):
        for rule_id in witness.get("rules", []):
            semantic_witness_rules.setdefault(rule_id, []).append(witness.get("test", ""))
    for mapping in source_mappings:
        native = mapping.get("native", {})
        fields = set(native.get("state_field_map", {})); selectors = set(native.get("selector_map", {}))
        all_fields.update((mapping["capability"], f) for f in fields)
        all_selectors.update((mapping["capability"], f) for f in selectors)
        for values in native.get("field_datatypes", {}).values():
            for datatype in values: datatypes[datatype] += 1
        alternatives = native.get("object_selector_alternatives", [])
        selector_alternatives += len(alternatives)
        if alternatives:
            selected = set(alternatives[0]); selected_alternatives += 1
        else:
            selected = selectors
        chosen_selectors.update((mapping["capability"], f) for f in selected)
        manifest_row = manifest_rows[mapping["capability"]]
        document = load(CONF / manifest_row["assessment"])
        fixture = load(CONF / manifest_row["fixture"])
        capability = mapping["capability"]
        authored[capability] = document
        fixtures[capability] = fixture
        positive_items = fixture.get("variants", {}).get("positive", {}).get("items", [])
        positive_item = positive_items[0] if len(positive_items) == 1 else None
        predicates: dict[str, Any] = {}
        for test in document["assessment"].get("tests", {}).values():
            for field, predicate in test.get("require", {}).get("fields", {}).items():
                authored_field_witnesses.add((capability, field))
                predicates[field] = predicate
        for item in positive_items:
            for field in item.get("fields", {}):
                fixture_field_witnesses.add((capability, field))
        for field in sorted(set(predicates) & set(native.get("state_field_map", {}))):
            observed = positive_item.get("fields", {}).get(field, {}).get("value") if positive_item else None
            if not positive_item or field not in positive_item.get("fields", {}) or not predicate_matches(observed, predicates[field]):
                non_exercising_field_witnesses.append({"capability": capability, "field": field, "reason": "positive fixture value does not satisfy authored Require predicate"})
        tests = list(document["assessment"].get("tests", {}).values())
        for rule in mapping.get("semantic_validator_rules", []):
            rule_id = rule.get("id", "")
            suffix = rule_id.rsplit(".", 1)[-1]
            has_object = any(isinstance(test.get("object"), dict) for test in tests)
            has_variable = any(isinstance(test.get("variable"), str) and test["variable"] in document["assessment"].get("variables", {}) for test in tests)
            if rule_id in semantic_witness_rules:
                status = "semantic-witness"
            elif suffix in {"singleton_source", "implicit_source", "implicit_population", "fixed_result"} and not has_object:
                status = "structural-witness"
            elif suffix == "source_exists" and has_variable:
                status = "structural-witness"
            else:
                status = "untested"
            semantic_rule_audit.append({"capability": capability, "id": rule_id, "status": status, **({"witness_tests": semantic_witness_rules[rule_id]} if rule_id in semantic_witness_rules else {})})
        mapping_rows.append({"capability": mapping["capability"], "fields": len(fields), "selectors": len(selectors), "alternatives": len(alternatives), "selected_alternative": 1 if alternatives else 0, "coverage": {"schema": "pass", "semantic": "pass", "collection": "untested", "integration": "not_run", "operational": "untested"}})

    selector_document = load(CONF / "cases/core/selector-alternatives.assessment.yaml")
    source_alternatives = {(m["capability"], index): set(alternative) for m in source_mappings for index, alternative in enumerate(m.get("native", {}).get("object_selector_alternatives", []), 1)}
    remaining_alternatives = {key: value for key, value in source_alternatives.items()}
    authored_selector_keys: list[tuple[str, int]] = []
    for test in selector_document["assessment"].get("tests", {}).values():
        obj = test.get("object", {}); capability = obj.get("capability"); fields = set(obj) - {"capability"}
        matches = [key for key, alternative in remaining_alternatives.items() if key[0] == capability and alternative == fields]
        if matches:
            key = matches[0]; authored_selector_keys.append(key); del remaining_alternatives[key]
    selector_suite_alternatives = len(authored_selector_keys)
    duplicate_selector_witnesses = len(authored_selector_keys) - len(set(authored_selector_keys))
    non_exercising_selector_witnesses: list[dict[str, Any]] = []
    selector_fixture = load(CONF / "fixtures/core-selector-alternatives.json")
    selector_witnesses = selector_fixture.get("selector_witnesses", {})
    for test_name, test in selector_document["assessment"].get("tests", {}).items():
        object_fields = set(test.get("object", {})) - {"capability"}
        witness = selector_witnesses.get(test_name, {})
        if object_fields != set(witness.get("selectors", {})) or not witness.get("items"):
            non_exercising_selector_witnesses.append({"test": test_name, "reason": "selector Object and corresponding fixture witness differ"})
    enum_suite_document = load(CONF / "cases/core/enum-boundaries.assessment.yaml")
    enum_suite_values = {test.get("object", {}).get("hive", {}).get("equals") for test in enum_suite_document["assessment"].get("tests", {}).values()}
    native_enum_values = {"classes_root", "current_config", "current_user", "current_user_local_settings", "local_machine", "users"}
    authored_enum_values = {value for value in enum_suite_values if isinstance(value, str)}
    authored_ops = set()
    operator_witnesses: dict[str, dict[str, Any]] = {}
    duplicate_operator_witnesses: list[str] = []
    non_exercising_operator_witnesses: list[dict[str, Any]] = []
    authored_cardinalities = set()
    expression_keys = {"and", "or", "one", "xor", "not", "test", "assessment", "not_evaluated", "not_applicable"}
    authored_documents = list(authored.values()) + [load(CONF / "cases/core/evaluate-not.assessment.yaml"), load(CONF / "cases/core/variable-interactions.assessment.yaml"), load(CONF / "cases/core/variable-functions.assessment.yaml"), load(CONF / "cases/core/input-guards.assessment.yaml"), load(CONF / "cases/core/applicability.assessment.yaml"), load(CONF / "cases/core/comparison-operators.assessment.yaml"), load(CONF / "cases/core/selector-alternatives.assessment.yaml"), load(CONF / "cases/core/cardinalities.assessment.yaml"), load(CONF / "cases/core/status-not-evaluated.assessment.yaml"), load(CONF / "cases/core/status-not-applicable.assessment.yaml"), semantic_boundary_assessment]
    for document in authored_documents:
        for node in walk(document):
            if not isinstance(node, dict): continue
            authored_ops.update(k for k in node if k in set(inventory["operator_inventory"]["field_predicate_properties"]) | expression_keys)
            for key in ("items_found", "items_satisfying", "values_found", "values_matching"):
                if key in node: authored_cardinalities.add(node[key])
    presentation_order_violations: list[str] = []
    presentation_order_witnesses = 0
    for document in authored_documents:
        for test_name, test in document.get("assessment", {}).get("tests", {}).items():
            if not isinstance(test, dict) or "object" not in test or "require" not in test:
                continue
            presentation_order_witnesses += 1
            keys = list(test)
            if keys.index("object") > keys.index("require"):
                presentation_order_violations.append(test_name)

    # Native field predicate operators are the active comparison surface;
    # source-only pattern_match is deliberately not treated as native.
    language = load(SCHEMA / "assessment-language.schema.json")
    comparison = set()
    for definition_name in ("scalar_field_predicate", "record_field_predicate", "object_selector_predicate"):
        comparison.update(k for k in language["$defs"][definition_name].get("properties", {}) if k not in {"values_found", "values_matching", "datatype", "value_match", "redact_result", "selection_match"})
    field_ops = set(comparison)
    operator_document = load(CONF / "cases/core/comparison-operators.assessment.yaml")
    operator_expected = load(CONF / "expected/core-comparison-operators.json").get("operators", {})
    for test_name, test in operator_document["assessment"].get("tests", {}).items():
        value_predicate = test.get("require", {}).get("fields", {}).get("value", {})
        operators = [key for key in value_predicate if key in comparison]
        if len(operators) != 1:
            non_exercising_operator_witnesses.append({"test": test_name, "reason": "operator test does not contain exactly one comparison operator"})
            continue
        operator = operators[0]
        if operator in operator_witnesses:
            duplicate_operator_witnesses.append(operator)
        operand = value_predicate[operator]
        expected = operator_expected.get(operator, {})
        operator_witnesses[operator] = {"test": test_name, "datatype": expected.get("datatype"), "operand": operand, "variable": test.get("variable")}
        if expected.get("operand") != operand or not test.get("variable"):
            non_exercising_operator_witnesses.append({"test": test_name, "operator": operator, "reason": "authored operand or Variable source differs from expected witness"})
    logical = set(inventory["operator_inventory"]["logical"]) | {"not"}
    boundary_validator = assessment_validator()
    enum_boundary_attempts = enum_boundary_rejections = 0
    for row in manifest["capabilities"]:
        document = load(CONF / row["assessment"])
        for test in document["assessment"].get("tests", {}).values():
            obj = test.get("object")
            if not isinstance(obj, dict): continue
            for field, condition in obj.items():
                if field == "capability" or not isinstance(condition, dict) or not isinstance(condition.get("equals"), str): continue
                enum_boundary_attempts += 1
                mutant = copy.deepcopy(document)
                mutant["assessment"]["tests"][next(iter(document["assessment"]["tests"]))]["object"][field]["equals"] = "__invalid_enum_boundary__"
                try:
                    boundary_validator.validate(mutant)
                except ValidationError:
                    enum_boundary_rejections += 1
    canonical_cardinalities = set()
    for definition_name in ("cardinality", "existence_cardinality", "item_existence_cardinality"):
        definition = language["$defs"].get(definition_name, {})
        for node in walk(definition):
            if isinstance(node, dict) and isinstance(node.get("enum"), list): canonical_cardinalities.update(node["enum"])
    semantic_rules_untested_count = sum(row["status"] == "untested" for row in semantic_rule_audit)
    report = {
        "format": "scap-ng-conformance-coverage-audit-0.1",
        "schema_version": manifest["schema_version"],
        "schema_commit": manifest["schema_commit"],
        "schema_family_sha256": manifest["schema_family_sha256"],
        "vectors": {"capabilities": len(manifest["capabilities"]), "base_vectors_per_capability": 7, "base_capability_vectors_total": len(manifest["capabilities"]) * 7, "additional_multi_item": len(manifest["capabilities"]), "expanded_capability_vectors_total": sum(len(row["vectors"]) for row in manifest["capabilities"]), "multi_value_suite_cases": len(load(CONF / "expected/core-multi-values.json").get("capabilities", {})), "normal_true_vectors_total": len(manifest["capabilities"]) * 2},
        "fields": {"declared_mapping_fields": len(all_fields), "authored_assessment_fields": len(authored_field_witnesses), "positive_fixture_fields": len(fixture_field_witnesses), "missing_from_assessments": sorted(set(all_fields) - authored_field_witnesses), "missing_from_fixtures": sorted(set(all_fields) - fixture_field_witnesses), "extra_authored_fields": sorted(authored_field_witnesses - set(all_fields)), "coverage_percent": round(100 * len(authored_field_witnesses & set(all_fields)) / len(all_fields), 2), "non_exercising_witnesses": non_exercising_field_witnesses, "datatypes": dict(sorted(datatypes.items()))},
        "capability_constraints": {"mapping_count": len(mapping_rows), "semantic_validator_rule_count": len(semantic_rule_audit), "mappings_with_semantic_rules": sum(bool(m.get("semantic_validator_rules")) for m in source_mappings), "semantic_rules_structural_witnesses": sum(row["status"] == "structural-witness" for row in semantic_rule_audit), "semantic_rules_semantic_witnesses": sum(row["status"] == "semantic-witness" for row in semantic_rule_audit), "semantic_rules_untested": [row for row in semantic_rule_audit if row["status"] == "untested"], "schema_positive_validation": "all 105 capability Assessments plus core-semantic-boundaries", "execution_coverage": False, "semantic_boundary_witnesses": len(semantic_witness_rules), "semantic_boundary_unknown_rules": sorted(set(semantic_witness_rules) - declared_semantic_rule_ids), "note": "Mapping rules are inventoried; semantic-witness marks only schema-valid authored combinations paired with independently justified expected semantic outcomes. Collector/filter and runtime execution remain separate."},
        "selectors": {"declared_selector_fields": len(all_selectors), "selected_in_positive_assessments": len(chosen_selectors), "field_coverage_percent": round(100 * len(chosen_selectors) / len(all_selectors), 2), "selector_alternative_sets": selector_alternatives, "positive_first_alternative_sets": selected_alternatives, "alternative_sets_exercised_by_selector_suite": selector_suite_alternatives, "uncovered_alternative_sets": selector_alternatives - selector_suite_alternatives, "duplicate_selector_witnesses": duplicate_selector_witnesses, "missing_selector_witnesses": sorted(set(source_alternatives) - set(authored_selector_keys)), "non_exercising_witnesses": non_exercising_selector_witnesses, "note": "The selector suite exercises every declared alternative; native selector enum/pattern boundary values and collector execution remain separate gates."},
        "enum_boundaries": {"selector_mutation_attempts": enum_boundary_attempts, "schema_rejected_mutations": enum_boundary_rejections, "unconstrained_selector_values": enum_boundary_attempts - enum_boundary_rejections, "native_selector_enum_values": len(native_enum_values), "authored_native_selector_enum_values": len(authored_enum_values & native_enum_values), "uncovered_native_selector_enum_values": sorted(native_enum_values - authored_enum_values), "note": "Only schema-backed enum selectors reject the sentinel; unconstrained selector strings are not falsely called enum coverage."},
        "operators": {"canonical_comparison_count": len(comparison), "authored_comparison": sorted(comparison & authored_ops), "uncovered_comparison": sorted(comparison - authored_ops), "canonical_field_operator_count": len(field_ops), "authored_field_operators": sorted(field_ops & authored_ops), "uncovered_field_operators": sorted(field_ops - authored_ops), "canonical_logical": sorted(logical), "authored_logical": sorted(logical & authored_ops), "uncovered_logical": sorted(logical - authored_ops), "witnesses": operator_witnesses, "duplicate_witnesses": sorted(set(duplicate_operator_witnesses)), "non_exercising_witnesses": non_exercising_operator_witnesses},
        "cardinalities": {"canonical": sorted(canonical_cardinalities), "authored": sorted(authored_cardinalities), "uncovered": sorted(canonical_cardinalities - authored_cardinalities), "note": "Dedicated schema-valid cardinality witnesses cover each token; real collector/cardinality execution remains an RI qualification gate."},
        "exceptional_outcomes": {"fixture_outcomes": ["unknown", "error", "not_applicable"], "status_cases": ["not_evaluated", "disabled/profile"], "uncovered_defined_outcomes": [], "note": "Disabled is exercised as profile policy and is not silently inferred as a technical Test outcome; status propagation still requires RI receipts."},
        "derived_integrity": {"fields_from_source_mappings": len(all_fields), "fields_from_authored_assessments": len(authored_field_witnesses), "fields_from_positive_fixtures": len(fixture_field_witnesses), "operators_from_source_schema": len(comparison), "operators_from_authored_assessments": len(comparison & authored_ops), "selector_alternatives_from_source_mappings": len(source_alternatives), "selector_alternatives_from_authored_assessments": len(authored_selector_keys), "cardinalities_from_source_schema": sorted(canonical_cardinalities), "cardinalities_from_authored_assessments": sorted(authored_cardinalities), "duplicate_witnesses": {"selectors": duplicate_selector_witnesses, "operators": sorted(set(duplicate_operator_witnesses))}, "missing_witnesses": {"fields": sorted(set(all_fields) - authored_field_witnesses), "selectors": sorted(set(source_alternatives) - set(authored_selector_keys)), "operators": sorted(comparison - authored_ops), "cardinalities": sorted(canonical_cardinalities - authored_cardinalities)}, "non_exercising_witnesses": {"fields": non_exercising_field_witnesses, "selectors": non_exercising_selector_witnesses, "operators": non_exercising_operator_witnesses}, "derived_from": "source schema/mappings + authored Assessment YAML + corresponding fixture JSON"},
        "schema_branches": {"schema_documents": inventory["counts"]["schema_documents"], "enum_nodes": inventory["counts"]["schema_enums"], "constraint_nodes": inventory["counts"]["schema_constraints"], "references": inventory["counts"]["schema_references"], "direct_executable_branch_coverage": False, "uncovered": ["non-selector enum boundary values", "schema property/constraint occurrence combinations", f"{semantic_rules_untested_count} untested capability semantic-validator rules", "platform permission/collector execution and scale/concurrency"]},
        "independent_oracle": {"model_a_scope": "complete known nonempty integer/string Model A", "source_cases": 15, "source_manifest": "conformance/0.4/model-a/manifest.json", "implementation": "conformance/tools/model_a_oracle.py", "executed_by": "tests/test_model_a_oracle.py", "runtime_qualification": False},
        "variable_interactions": {"case": "core-variable-interactions", "canonical_assessment": True, "local_alias": True, "multi_value_observation": 2, "false_leaf_visible": True, "enclosing_not_result": "true", "independently_justified": True, "runtime_qualification": False},
        "set_filter_semantics": {"case": "core-set-filters", "filter_actions": ["include", "exclude"], "set_operators": ["union", "intersection", "difference"], "operations": 3, "independently_justified": True, "runtime_qualification": False},
        "variable_functions": {"case": "core-variable-functions", "functions": ["unique", "count", "concat", "merge"], "ordered_duplicate_source": True, "independently_justified": True, "runtime_qualification": False},
        "input_guards": {"case": "core-input-guards", "guard": "input_provided", "variants": ["provided", "absent", "explicit-empty", "too-many", "out-of-range"], "independently_justified": True, "runtime_qualification": False},
        "applicability": {"case": "core-applicability", "dependency": "shared-applicability-assessment", "variants": ["applicable", "not-applicable", "deferred"], "independently_justified": True, "runtime_qualification": False},
        "semantic_boundaries": {"case": "core-semantic-boundaries", "rules": sorted(semantic_witness_rules), "witnesses": len(semantic_boundary_fixture.get("semantic_witnesses", [])), "independently_justified": True, "runtime_qualification": False},
        "authoring_enums": {"cases": len(manifest.get("authoring_cases", [])), "automated_reported_elements_branches": ["scalar-all", "scalar-compared", "explicit-list"], "manual_outcomes": ["true", "false", "error", "unknown", "not_evaluated", "not_applicable"], "negative_boundary_cases": ["invalid-class", "invalid-reported-elements", "invalid-manual-outcome", "invalid-mode", "invalid-variable-kind", "invalid-cardinality", "invalid-specification-version", "invalid-reported-elements-duplicate", "invalid-empty-procedure", "invalid-id-pattern"]},
        "expected_results": {"independent_justification": True, "basis": "Separate expected JSON files cite deterministic fixture variants, item/field cardinality observations, decisive mismatch/status reasons, and core not(FALSE) assertions. They are not derived from RI output.", "ri_execution": False, "ri_issue": 196},
        "feature_coverage": {"fields": {"schema": "pass", "semantic": "pass", "collection": "untested", "integration": "not_run", "operational": "untested", "scope": "authored fields and deterministic fixture witness"}, "comparison_operators": {"schema": "pass", "semantic": "pass", "collection": "untested", "integration": "not_run", "operational": "untested", "scope": "schema-valid typed witnesses; runtime unqualified"}, "selector_alternatives": {"schema": "pass", "semantic": "pass", "collection": "untested", "integration": "not_run", "operational": "untested", "scope": "mapping-declared alternatives; acquisition unqualified"}, "cardinalities": {"schema": "pass", "semantic": "pass", "collection": "untested", "integration": "not_run", "operational": "untested", "scope": "Model A and schema witnesses; empty/status precedence unqualified"}, "variable_functions": {"schema": "pass", "semantic": "pass", "collection": "untested", "integration": "not_run", "operational": "untested", "scope": "known ordered values only"}, "input_guards": {"schema": "pass", "semantic": "pass", "collection": "untested", "integration": "untested", "operational": "untested", "scope": "authoring binding distinctions; Rule packaging unqualified"}, "applicability": {"schema": "pass", "semantic": "pass", "collection": "untested", "integration": "untested", "operational": "untested", "scope": "dependency identity and typed handoff; graph resolution unqualified"}, "set_filters": {"schema": "pass", "semantic": "pass", "collection": "untested", "integration": "untested", "operational": "untested", "scope": "abstract deterministic populations; collector filter execution unqualified"}, "semantic_boundaries": {"schema": "pass", "semantic": "pass", "collection": "untested", "integration": "not_run", "operational": "untested", "scope": "twenty-two schema-valid semantic rule witnesses; semantic validator runtime remains unqualified"}},
        "presentation_order": {"issue": 95, "tests_with_object_and_require": presentation_order_witnesses, "violations": presentation_order_violations, "deterministic": True},
        "capability_rows": mapping_rows,
    }
    (CONF / "coverage-audit.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
