#!/usr/bin/env python3
"""Verify foreach v1 lowering against analyzer-described faithful production graphs."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
LOWER_SPEC = importlib.util.spec_from_file_location(
    "lower_foreach_v1", HERE / "lower_foreach_v1.py"
)
LOWER = importlib.util.module_from_spec(LOWER_SPEC)
assert LOWER_SPEC.loader is not None
LOWER_SPEC.loader.exec_module(LOWER)


def authoring_from_candidate(candidate: dict) -> tuple[str, dict]:
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

    obj = {
        "for_each": {
            "item": binding,
            "in": source["object_id"],
        },
        "select": {
            target["entity"]: {
                "from": f"{binding}.{source['item_field']}",
            }
        },
    }
    return target["object_id"], obj


def compare_candidate(candidate: dict) -> dict:
    target_id, authoring = authoring_from_candidate(candidate)
    lowered = LOWER.lower_foreach_v1(target_id, authoring)
    target = candidate["targets"][0]
    source = candidate["source"]

    checks = {
        "rewrite_id": (
            lowered["rewrite_id"]
            == "foreach.direct-object-component.at-least-one.v1"
        ),
        "source_object": lowered["source_object"] == source["object_id"],
        "projected_field": (
            lowered["synthetic_variable"]["expression"]["object_component"]["item_field"]
            == source["item_field"]
        ),
        "target_object": lowered["target_object"]["id"] == target["object_id"],
        "target_entity": target["entity"] in lowered["target_object"]["select"],
        "target_operation": (
            lowered["target_object"]["select"][target["entity"]]["operation"]
            == target["operation"]
        ),
        "target_var_check": (
            lowered["target_object"]["select"][target["entity"]]["var_check"]
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
    checks["faithful_target_datatype_present"] = bool(datatype)

    return {
        "variable_id": candidate["variable_id"],
        "source_object": source["object_id"],
        "source_object_type": source["object_type"],
        "item_field": source["item_field"],
        "target_object": target["object_id"],
        "target_object_type": target["object_type"],
        "target_entity": target["entity"],
        "faithful_target_datatype": datatype,
        "authoring": authoring,
        "checks": checks,
        "equivalent": all(checks.values()),
    }


def verify_report(report: dict) -> dict:
    rows = []
    for file_row in report.get("files", []):
        for candidate in file_row.get("candidates", []):
            proof = candidate.get("first_proof_class") or {}
            if proof.get("eligible"):
                row = compare_candidate(candidate)
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
            "Prototype records faithful target datatype but defers capability-"
            "schema source/target compatibility inference to production compiler."
        ),
        "candidates": rows,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    result = verify_report(json.loads(args.report.read_text(encoding="utf-8")))
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
    else:
        print(encoded, end="")
    return 0 if result["all_equivalent"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
