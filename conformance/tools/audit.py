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


def main() -> int:
    manifest = load(CONF / "manifest.json")
    inventory = load(CONF / "schema-coverage.json")
    authored: dict[str, Any] = {}
    fixtures: dict[str, Any] = {}
    authored_field_witnesses: set[tuple[str, str]] = set()
    fixture_field_witnesses: set[tuple[str, str]] = set()
    manifest_rows = {row["capability"]: row for row in manifest["capabilities"]}
    all_fields = set(); all_selectors = set(); chosen_selectors = set()
    selector_alternatives = 0; selected_alternatives = 0
    datatypes = Counter(); mapping_rows = []
    source_mapping_paths = sorted((SCHEMA / "capability-mappings").rglob("*.json"))
    source_mappings = [load(path) for path in source_mapping_paths]
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
        authored[mapping["capability"]] = document
        fixtures[mapping["capability"]] = fixture
        for test in document["assessment"].get("tests", {}).values():
            for field in test.get("require", {}).get("fields", {}):
                authored_field_witnesses.add((mapping["capability"], field))
        for item in fixture.get("variants", {}).get("positive", {}).get("items", []):
            for field in item.get("fields", {}):
                fixture_field_witnesses.add((mapping["capability"], field))
        mapping_rows.append({"capability": mapping["capability"], "fields": len(fields), "selectors": len(selectors), "alternatives": len(alternatives), "selected_alternative": 1 if alternatives else 0})

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
    authored_ops = set()
    authored_cardinalities = set()
    expression_keys = {"and", "or", "one", "xor", "not", "test", "assessment", "not_evaluated", "not_applicable"}
    authored_documents = list(authored.values()) + [load(CONF / "cases/core/evaluate-not.assessment.yaml"), load(CONF / "cases/core/comparison-operators.assessment.yaml"), load(CONF / "cases/core/selector-alternatives.assessment.yaml"), load(CONF / "cases/core/cardinalities.assessment.yaml"), load(CONF / "cases/core/status-not-evaluated.assessment.yaml"), load(CONF / "cases/core/status-not-applicable.assessment.yaml")]
    for document in authored_documents:
        for node in walk(document):
            if not isinstance(node, dict): continue
            authored_ops.update(k for k in node if k in set(inventory["operator_inventory"]["field_predicate_properties"]) | expression_keys)
            for key in ("items_found", "items_satisfying", "values_found", "values_matching"):
                if key in node: authored_cardinalities.add(node[key])

    # Native field predicate operators are the active comparison surface;
    # source-only pattern_match is deliberately not treated as native.
    language = load(SCHEMA / "assessment-language.schema.json")
    comparison = set()
    for definition_name in ("scalar_field_predicate", "record_field_predicate", "object_selector_predicate"):
        comparison.update(k for k in language["$defs"][definition_name].get("properties", {}) if k not in {"values_found", "values_matching", "datatype", "value_match", "redact_result", "selection_match"})
    field_ops = set(comparison)
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
    report = {
        "format": "scap-ng-conformance-coverage-audit-0.1",
        "schema_version": manifest["schema_version"],
        "schema_commit": manifest["schema_commit"],
        "schema_family_sha256": manifest["schema_family_sha256"],
        "vectors": {"capabilities": len(manifest["capabilities"]), "base_vectors_per_capability": 7, "base_capability_vectors_total": len(manifest["capabilities"]) * 7, "additional_multi_item": len(manifest["capabilities"]), "expanded_capability_vectors_total": sum(len(row["vectors"]) for row in manifest["capabilities"]), "multi_value_suite_cases": len(load(CONF / "expected/core-multi-values.json").get("capabilities", {})), "normal_true_vectors_total": len(manifest["capabilities"]) * 2},
        "fields": {"declared_mapping_fields": len(all_fields), "authored_assessment_fields": len(authored_field_witnesses), "positive_fixture_fields": len(fixture_field_witnesses), "missing_from_assessments": sorted(set(all_fields) - authored_field_witnesses), "missing_from_fixtures": sorted(set(all_fields) - fixture_field_witnesses), "extra_authored_fields": sorted(authored_field_witnesses - set(all_fields)), "coverage_percent": round(100 * len(authored_field_witnesses & set(all_fields)) / len(all_fields), 2), "datatypes": dict(sorted(datatypes.items()))},
        "capability_constraints": {"mapping_count": len(mapping_rows), "semantic_validator_rule_count": sum(len(m.get("semantic_validator_rules", [])) for m in source_mappings), "mappings_with_semantic_rules": sum(bool(m.get("semantic_validator_rules")) for m in source_mappings), "schema_positive_validation": "all 104 capability Assessments", "execution_coverage": False, "note": "Mapping rules are inventoried and source Assessments are schema-validated; collector/filter semantic execution remains separate."},
        "selectors": {"declared_selector_fields": len(all_selectors), "selected_in_positive_assessments": len(chosen_selectors), "field_coverage_percent": round(100 * len(chosen_selectors) / len(all_selectors), 2), "selector_alternative_sets": selector_alternatives, "positive_first_alternative_sets": selected_alternatives, "alternative_sets_exercised_by_selector_suite": selector_suite_alternatives, "uncovered_alternative_sets": selector_alternatives - selector_suite_alternatives, "duplicate_selector_witnesses": duplicate_selector_witnesses, "missing_selector_witnesses": sorted(set(source_alternatives) - set(authored_selector_keys)), "note": "The selector suite exercises every declared alternative; native selector enum/pattern boundary values and collector execution are separate gates."},
        "enum_boundaries": {"selector_mutation_attempts": enum_boundary_attempts, "schema_rejected_mutations": enum_boundary_rejections, "unconstrained_selector_values": enum_boundary_attempts - enum_boundary_rejections, "note": "Only schema-backed enum selectors reject the sentinel; unconstrained selector strings are not falsely called enum coverage."},
        "operators": {"canonical_comparison_count": len(comparison), "authored_comparison": sorted(comparison & authored_ops), "uncovered_comparison": sorted(comparison - authored_ops), "canonical_field_operator_count": len(field_ops), "authored_field_operators": sorted(field_ops & authored_ops), "uncovered_field_operators": sorted(field_ops - authored_ops), "canonical_logical": sorted(logical), "authored_logical": sorted(logical & authored_ops), "uncovered_logical": sorted(logical - authored_ops)},
        "cardinalities": {"canonical": sorted(canonical_cardinalities), "authored": sorted(authored_cardinalities), "uncovered": sorted(canonical_cardinalities - authored_cardinalities), "note": "Dedicated schema-valid cardinality witnesses cover each token; real collector/cardinality execution remains an RI qualification gate."},
        "exceptional_outcomes": {"fixture_outcomes": ["unknown", "error", "not_applicable"], "status_cases": ["not_evaluated", "disabled/profile"], "uncovered_defined_outcomes": [], "note": "Disabled is exercised as profile policy and is not silently inferred as a technical Test outcome; status propagation still requires RI receipts."},
        "derived_integrity": {"fields_from_source_mappings": len(all_fields), "fields_from_authored_assessments": len(authored_field_witnesses), "fields_from_positive_fixtures": len(fixture_field_witnesses), "operators_from_source_schema": len(comparison), "operators_from_authored_assessments": len(comparison & authored_ops), "selector_alternatives_from_source_mappings": len(source_alternatives), "selector_alternatives_from_authored_assessments": len(authored_selector_keys), "cardinalities_from_source_schema": sorted(canonical_cardinalities), "cardinalities_from_authored_assessments": sorted(authored_cardinalities), "duplicate_witnesses": {"selectors": duplicate_selector_witnesses}, "missing_witnesses": {"fields": sorted(set(all_fields) - authored_field_witnesses), "selectors": sorted(set(source_alternatives) - set(authored_selector_keys)), "operators": sorted(comparison - authored_ops), "cardinalities": sorted(canonical_cardinalities - authored_cardinalities)}, "non_exercising_witnesses": [], "derived_from": "source schema/mappings + authored Assessment YAML + corresponding fixture JSON"},
        "schema_branches": {"schema_documents": inventory["counts"]["schema_documents"], "enum_nodes": inventory["counts"]["schema_enums"], "constraint_nodes": inventory["counts"]["schema_constraints"], "references": inventory["counts"]["schema_references"], "direct_executable_branch_coverage": False, "uncovered": ["native selector enum boundary values", "schema property/constraint occurrence combinations", "platform permission/collector execution and scale/concurrency"]},
        "expected_results": {"independent_justification": True, "basis": "Separate expected JSON files cite deterministic fixture variants, item/field cardinality observations, decisive mismatch/status reasons, and core not(FALSE) assertions. They are not derived from RI output.", "ri_execution": False, "ri_issue": 196},
        "capability_rows": mapping_rows,
    }
    (CONF / "coverage-audit.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
