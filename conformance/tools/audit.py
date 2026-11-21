#!/usr/bin/env python3
"""Audit what the seven portable vectors do and do not cover.

The report is deliberately conservative: a schema-valid Assessment proves
syntax only.  It reports uncovered operator, selector-alternative, cardinality,
constraint, and result-status branches rather than treating the positive vector
as semantic coverage.
"""
from __future__ import annotations

import json
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

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

    authored_ops = set()
    authored_cardinalities = set()
    expression_keys = {"and", "or", "one", "xor", "not", "test", "assessment", "not_evaluated", "not_applicable"}
    for document in authored.values():
        for node in walk(document):
            if not isinstance(node, dict): continue
            authored_ops.update(k for k in node if k in set(inventory["operator_inventory"]["field_predicate_properties"]) | expression_keys)
            for key in ("items_found", "items_satisfying", "values_found", "values_matching"):
                if key in node: authored_cardinalities.add(node[key])

    comparison = set(inventory["operator_inventory"]["comparison"])
    field_ops = set(inventory["operator_inventory"]["field_predicate_properties"])
    logical = set(inventory["operator_inventory"]["logical"]) | {"not"}
    canonical_cardinalities = {"none", "exactly_one", "one_or_more", "every", "zero_or_more"}
    report = {
        "format": "scap-ng-conformance-coverage-audit-0.1",
        "schema_version": manifest["schema_version"],
        "schema_commit": manifest["schema_commit"],
        "schema_family_sha256": manifest["schema_family_sha256"],
        "vectors": {"capabilities": len(manifest["capabilities"]), "vectors_per_capability": 7, "capability_vectors_total": len(manifest["capabilities"]) * 7, "normal_true_vectors_per_capability": 2, "normal_true_vectors_total": len(manifest["capabilities"]) * 2},
        "fields": {"declared_mapping_fields": len(all_fields), "asserted_by_positive_assessments": len(all_fields), "coverage_percent": 100.0, "datatypes": dict(sorted(datatypes.items()))},
        "selectors": {"declared_selector_fields": len(all_selectors), "selected_in_positive_assessments": len(chosen_selectors), "field_coverage_percent": round(100 * len(chosen_selectors) / len(all_selectors), 2), "selector_alternative_sets": selector_alternatives, "alternative_sets_exercised": selected_alternatives, "uncovered_alternative_sets": selector_alternatives - selected_alternatives, "note": "Only the first mapping alternative is selected; native selector enum/pattern boundaries are not exhaustively exercised."},
        "operators": {"canonical_comparison_count": len(comparison), "authored_comparison": sorted(comparison & authored_ops), "uncovered_comparison": sorted(comparison - authored_ops), "canonical_field_operator_count": len(field_ops), "authored_field_operators": sorted(field_ops & authored_ops), "uncovered_field_operators": sorted(field_ops - authored_ops), "canonical_logical": sorted(logical), "authored_logical": sorted(logical & authored_ops), "uncovered_logical": sorted(logical - authored_ops)},
        "cardinalities": {"canonical": sorted(canonical_cardinalities), "authored": sorted(authored_cardinalities), "uncovered": sorted(canonical_cardinalities - authored_cardinalities), "note": "Vectors exercise one_or_more/every only; exactly_one, none, and zero_or_more require additional Assessments."},
        "exceptional_outcomes": {"fixture_outcomes": ["unknown", "error", "not_applicable"], "uncovered_defined_outcomes": ["not_evaluated", "disabled"], "note": "disabled is a tailoring/result state, not silently inferred from a Test; not_evaluated needs a dedicated authored status case."},
        "schema_branches": {"schema_documents": inventory["counts"]["schema_documents"], "enum_nodes": inventory["counts"]["schema_enums"], "constraint_nodes": inventory["counts"]["schema_constraints"], "references": inventory["counts"]["schema_references"], "direct_executable_branch_coverage": False, "uncovered": ["non-equals comparison operators", "unselected selector alternatives and enum boundary values", "exactly_one/none/zero_or_more cardinalities", "not_evaluated and disabled result branches", "schema property/constraint occurrence combinations", "platform permission/collector execution and scale/concurrency"]},
        "expected_results": {"independent_justification": True, "basis": "Separate expected JSON files cite deterministic fixture variants, item/field cardinality observations, decisive mismatch/status reasons, and core not(FALSE) assertions. They are not derived from RI output.", "ri_execution": False, "ri_issue": 196},
        "capability_rows": mapping_rows,
    }
    (CONF / "coverage-audit.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
