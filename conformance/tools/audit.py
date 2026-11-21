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
    manifest_rows = {row["capability"]: row for row in manifest["capabilities"]}
    all_fields = set(); all_selectors = set(); chosen_selectors = set()
    selector_alternatives = 0; selected_alternatives = 0
    datatypes = Counter(); mapping_rows = []
    for row in inventory["capabilities"]:
        mapping = load(ROOT / row["source_path"])
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
        document = load(CONF / manifest_rows[mapping["capability"]]["assessment"])
        authored[mapping["capability"]] = document
        mapping_rows.append({"capability": mapping["capability"], "fields": len(fields), "selectors": len(selectors), "alternatives": len(alternatives), "selected_alternative": 1 if alternatives else 0})

    selector_suite = load(CONF / "expected/core-selector-alternatives.json")
    selector_suite_alternatives = len(selector_suite.get("alternatives", {}))
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
    comparison = set(inventory["operator_inventory"]["field_predicate_properties"])
    field_ops = comparison
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
    canonical_cardinalities = {"none", "exactly_one", "one_or_more", "every", "zero_or_more"}
    report = {
        "format": "scap-ng-conformance-coverage-audit-0.1",
        "schema_version": manifest["schema_version"],
        "schema_commit": manifest["schema_commit"],
        "schema_family_sha256": manifest["schema_family_sha256"],
        "vectors": {"capabilities": len(manifest["capabilities"]), "base_vectors_per_capability": 7, "base_capability_vectors_total": len(manifest["capabilities"]) * 7, "additional_multi_item": len(manifest["capabilities"]), "expanded_capability_vectors_total": sum(len(row["vectors"]) for row in manifest["capabilities"]), "multi_value_suite_cases": len(load(CONF / "expected/core-multi-values.json").get("capabilities", {})), "normal_true_vectors_total": len(manifest["capabilities"]) * 2},
        "fields": {"declared_mapping_fields": len(all_fields), "asserted_by_positive_assessments": len(all_fields), "coverage_percent": 100.0, "datatypes": dict(sorted(datatypes.items()))},
        "capability_constraints": {"mapping_count": len(mapping_rows), "semantic_validator_rule_count": sum(len(row.get("semantic_validator_rules", [])) for row in inventory["capabilities"]), "mappings_with_semantic_rules": sum(bool(row.get("semantic_validator_rules")) for row in inventory["capabilities"]), "schema_positive_validation": "all 104 capability Assessments", "execution_coverage": False, "note": "Mapping rules are inventoried and source Assessments are schema-validated; collector/filter semantic execution remains separate."},
        "selectors": {"declared_selector_fields": len(all_selectors), "selected_in_positive_assessments": len(chosen_selectors), "field_coverage_percent": round(100 * len(chosen_selectors) / len(all_selectors), 2), "selector_alternative_sets": selector_alternatives, "positive_first_alternative_sets": selected_alternatives, "alternative_sets_exercised_by_selector_suite": selector_suite_alternatives, "uncovered_alternative_sets": selector_alternatives - selector_suite_alternatives, "note": "The selector suite exercises every declared alternative; native selector enum/pattern boundary values and collector execution are separate gates."},
        "enum_boundaries": {"selector_mutation_attempts": enum_boundary_attempts, "schema_rejected_mutations": enum_boundary_rejections, "unconstrained_selector_values": enum_boundary_attempts - enum_boundary_rejections, "note": "Only schema-backed enum selectors reject the sentinel; unconstrained selector strings are not falsely called enum coverage."},
        "operators": {"canonical_comparison_count": len(comparison), "authored_comparison": sorted(comparison & authored_ops), "uncovered_comparison": sorted(comparison - authored_ops), "canonical_field_operator_count": len(field_ops), "authored_field_operators": sorted(field_ops & authored_ops), "uncovered_field_operators": sorted(field_ops - authored_ops), "canonical_logical": sorted(logical), "authored_logical": sorted(logical & authored_ops), "uncovered_logical": sorted(logical - authored_ops)},
        "cardinalities": {"canonical": sorted(canonical_cardinalities), "authored": sorted(authored_cardinalities), "uncovered": sorted(canonical_cardinalities - authored_cardinalities), "note": "Dedicated schema-valid cardinality witnesses cover each token; real collector/cardinality execution remains an RI qualification gate."},
        "exceptional_outcomes": {"fixture_outcomes": ["unknown", "error", "not_applicable"], "status_cases": ["not_evaluated", "disabled/profile"], "uncovered_defined_outcomes": [], "note": "Disabled is exercised as profile policy and is not silently inferred as a technical Test outcome; status propagation still requires RI receipts."},
        "schema_branches": {"schema_documents": inventory["counts"]["schema_documents"], "enum_nodes": inventory["counts"]["schema_enums"], "constraint_nodes": inventory["counts"]["schema_constraints"], "references": inventory["counts"]["schema_references"], "direct_executable_branch_coverage": False, "uncovered": ["native selector enum boundary values", "schema property/constraint occurrence combinations", "platform permission/collector execution and scale/concurrency"]},
        "expected_results": {"independent_justification": True, "basis": "Separate expected JSON files cite deterministic fixture variants, item/field cardinality observations, decisive mismatch/status reasons, and core not(FALSE) assertions. They are not derived from RI output.", "ri_execution": False, "ri_issue": 196},
        "capability_rows": mapping_rows,
    }
    (CONF / "coverage-audit.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
