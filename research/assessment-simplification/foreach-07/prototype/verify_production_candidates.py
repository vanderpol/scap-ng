#!/usr/bin/env python3
"""Verify foreach v1 lowering against analyzer-described faithful production graphs."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
DEFAULT_MAPPING_DIR = ROOT / "schema" / "v0.2.0" / "capability-mappings" / "supported"


HERE = Path(__file__).resolve().parent
LOWER_SPEC = importlib.util.spec_from_file_location(
    "lower_foreach_v1", HERE / "lower_foreach_v1.py"
)
LOWER = importlib.util.module_from_spec(LOWER_SPEC)
assert LOWER_SPEC.loader is not None
LOWER_SPEC.loader.exec_module(LOWER)


def authoring_from_candidate(candidate: dict, mappings: dict) -> tuple[str, dict]:
    proof = candidate.get("first_proof_class") or {}
    if not proof.get("eligible"):
        raise ValueError("candidate is not first-proof-class eligible")

    targets = candidate.get("targets", [])
    if len(targets) != 1:
        raise ValueError("v1 requires exactly one target")
    target = targets[0]

    variable_id = candidate["variable_id"]
    source = candidate["source"]
    binding = "item"

    # The simplified syntax deliberately omits equality/datatype because those
    # are intrinsic/inferred in v1. Production proof therefore refuses any
    # source whose faithful target selector does not use the proven equality
    # family.
    if target.get("operation") != "equals":
        raise ValueError(
            f"{variable_id}: target operation {target.get('operation')!r} "
            "is outside foreach v1"
        )
    if target.get("var_check") != "at least one":
        raise ValueError(
            f"{variable_id}: target var_check {target.get('var_check')!r} "
            "is outside foreach v1"
        )

    source_mapping = mappings.get(source["object_type"])
    target_mapping = mappings.get(target["object_type"])
    if source_mapping is None or target_mapping is None:
        raise ValueError(f"{variable_id}: capability mapping missing")

    source_field = native_source_field(source_mapping, source["item_field"])
    target_entity = native_target_selector(target_mapping, target["entity"])
    if not source_field or not target_entity:
        raise ValueError(f"{variable_id}: native field mapping missing")

    obj = {
        "for_each": {
            "item": binding,
            "in": source["object_id"],
        },
        "select": {
            target_entity: {
                "from": f"{binding}.{source_field}",
            }
        },
    }
    return target["object_id"], obj


def load_capability_mappings(mapping_dir: Path) -> dict:
    by_object_type = {}
    for path in sorted(mapping_dir.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        object_type = data.get("source", {}).get("object")
        if object_type:
            by_object_type[object_type] = data
    return by_object_type


def native_source_field(mapping: dict, oval_field: str) -> str | None:
    native = mapping.get("native", {})
    return (
        native.get("state_field_map", {}).get(oval_field)
        or native.get("selector_map", {}).get(oval_field)
    )


def native_target_selector(mapping: dict, oval_entity: str) -> str | None:
    return mapping.get("native", {}).get("selector_map", {}).get(oval_entity)


def datatype_compatibility(candidate: dict, mappings: dict) -> dict:
    source = candidate["source"]
    target = candidate["targets"][0]
    source_mapping = mappings.get(source["object_type"])
    target_mapping = mappings.get(target["object_type"])
    if source_mapping is None or target_mapping is None:
        return {
            "compatible": False,
            "reason": "capability_mapping_missing",
        }

    source_field = native_source_field(source_mapping, source["item_field"])
    target_field = native_target_selector(target_mapping, target["entity"])
    if not source_field or not target_field:
        return {
            "compatible": False,
            "reason": "field_mapping_missing",
            "source_native_field": source_field,
            "target_native_field": target_field,
        }

    source_types = set(
        source_mapping.get("native", {})
        .get("field_datatypes", {})
        .get(source_field, [])
    )
    target_types = set(
        target_mapping.get("native", {})
        .get("field_datatypes", {})
        .get(target_field, [])
    )
    compatible_types = sorted(source_types & target_types)

    faithful_oval_datatype = target.get("datatype")
    datatype_map = (
        target_mapping.get("migration_crosswalk", {})
        .get("datatype", {})
    )
    faithful_native_datatype = datatype_map.get(
        faithful_oval_datatype,
        "integer" if faithful_oval_datatype == "int" else faithful_oval_datatype,
    )
    faithful_type_compatible = faithful_native_datatype in compatible_types

    return {
        "compatible": bool(compatible_types) and faithful_type_compatible,
        "source_capability": source_mapping.get("capability"),
        "source_native_field": source_field,
        "source_datatypes": sorted(source_types),
        "target_capability": target_mapping.get("capability"),
        "target_native_field": target_field,
        "target_datatypes": sorted(target_types),
        "compatible_datatypes": compatible_types,
        "faithful_oval_datatype": faithful_oval_datatype,
        "faithful_native_datatype": faithful_native_datatype,
        "faithful_type_compatible": faithful_type_compatible,
    }


def compare_candidate(candidate: dict, mappings: dict) -> dict:
    target_id, authoring = authoring_from_candidate(candidate, mappings)
    lowered = LOWER.lower_foreach_v1(target_id, authoring)
    target = candidate["targets"][0]
    source = candidate["source"]

    datatype_proof = datatype_compatibility(candidate, mappings)
    native_source = datatype_proof.get("source_native_field")
    native_target = datatype_proof.get("target_native_field")

    checks = {
        "rewrite_id": (
            lowered["rewrite_id"]
            == "foreach.direct-object-component.at-least-one.v1"
        ),
        "source_object": lowered["source_object"] == source["object_id"],
        "projected_field": (
            lowered["synthetic_variable"]["expression"]["object_component"]["item_field"]
            == native_source
        ),
        "target_object": lowered["target_object"]["id"] == target["object_id"],
        "target_entity": native_target in lowered["target_object"]["select"],
        "target_operation": (
            lowered["target_object"]["select"][native_target]["operation"]
            == target["operation"]
        ),
        "target_var_check": (
            lowered["target_object"]["select"][native_target]["var_check"]
            == target["var_check"]
        ),
        "aggregation_boundary": (
            lowered["aggregation_boundary"] == "target_object_population"
        ),
        "collection_combination": lowered["collection_combination"] == "union",
    }

    # The research lowerer marks datatype as source-compatible because full
    # capability-schema type inference is not part of this bounded prototype.
    # Record the faithful datatype and require it to be concrete; a production
    # 0.3.0 compiler must prove compatibility from capability schemas.
    datatype = target.get("datatype")
    checks["capability_datatype_compatible"] = datatype_proof["compatible"]

    return {
        "variable_id": candidate["variable_id"],
        "source_object": source["object_id"],
        "source_object_type": source["object_type"],
        "source_item_field": source["item_field"],
        "native_source_field": native_source,
        "target_object": target["object_id"],
        "target_object_type": target["object_type"],
        "target_entity": target["entity"],
        "native_target_entity": native_target,
        "faithful_target_datatype": datatype,
        "datatype_proof": datatype_proof,
        "authoring": authoring,
        "checks": checks,
        "equivalent": all(checks.values()),
    }


def verify_report(report: dict, mappings: dict) -> dict:
    rows = []
    for file_row in report.get("files", []):
        for candidate in file_row.get("candidates", []):
            proof = candidate.get("first_proof_class") or {}
            if proof.get("eligible"):
                row = compare_candidate(candidate, mappings)
                row["source_document"] = file_row.get("path")
                rows.append(row)

    failures = [row for row in rows if not row["equivalent"]]
    return {
        "format": "scap-ng-foreach-v1-production-proof-0.1",
        "rewrite_id": "foreach.direct-object-component.at-least-one.v1",
        "eligible_candidates": len(rows),
        "equivalent_candidates": len(rows) - len(failures),
        "failed_candidates": len(failures),
        "all_equivalent": bool(rows) and not failures,
        "datatype_note": (
            "Source and target field compatibility is proven from maintained "
            "v0.2.0 capability mappings for this bounded research prototype."
        ),
        "candidates": rows,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--mapping-dir", type=Path, default=DEFAULT_MAPPING_DIR)
    args = parser.parse_args(argv)

    mappings = load_capability_mappings(args.mapping_dir)
    result = verify_report(
        json.loads(args.report.read_text(encoding="utf-8")),
        mappings,
    )
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
    else:
        print(encoded, end="")
    return 0 if result["all_equivalent"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
