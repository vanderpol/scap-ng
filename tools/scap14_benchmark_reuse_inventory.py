#!/usr/bin/env python3
"""Build a compact benchmark-level reuse inventory from split SCAP 1.4 content.

This tool is intended for corpus-scale reuse measurement. It reuses the same
OVAL semantic importer, effective-deprecation gate, generic SCAP-NG assessment
compiler, and semantic fingerprinting used by the four-anchor demonstration,
but does not render full YAML source trees.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import scap14_benchmark_ir as benchmark_ir
import scap14_rule_splitter as split
import oval_semantic_ir
import scap14_to_scapng as converter
from analyze_scapng_assessment_reuse import (
    assessment_fingerprints,
    digest,
    normalize_check_text,
)


def rule_check_text(rule: dict) -> str | None:
    for check in rule.get("checks", []):
        text = check.get("inline_content")
        if text:
            return normalize_check_text(text)
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("source_zip", type=Path)
    ap.add_argument("--split-root", type=Path, required=True)
    ap.add_argument("--schema-catalog", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    catalog = converter.load_catalog(args.schema_catalog)
    manifest = json.loads(
        (args.split_root / "manifest.json").read_text(encoding="utf-8")
    )
    manifest_rules = {
        row.get("rule_id"): row
        for row in manifest.get("rules", [])
        if row.get("rule_id")
    }

    _, _, ds_root = split.find_datastream(args.source_zip)
    components, _ = split.embedded_components(ds_root)
    benchmarks = [
        (cid, root)
        for cid, root in components.items()
        if split.component_kind(root) == "xccdf"
    ]
    if len(benchmarks) != 1:
        raise ValueError(
            f"expected one XCCDF benchmark in {args.source_zip}, found {len(benchmarks)}"
        )

    component_id, benchmark = benchmarks[0]
    rules = list(benchmark_ir.walk_rules(benchmark))
    output_rules = []
    missing_manifest = []

    summary = {
        "source_rules": len(rules),
        "supported_automated_assessments": 0,
        "manual_or_external_rules": 0,
        "blocked_automated_rules": 0,
        "missing_manifest_rules": 0,
        "rules_with_check_text": 0,
    }

    for rule in rules:
        rid = rule.get("id")
        check_text = rule_check_text(rule)
        if check_text:
            summary["rules_with_check_text"] += 1

        base = {
            "rule_id": rid,
            "title": rule.get("title"),
            "check_text": check_text,
            "check_text_fingerprint": digest(check_text) if check_text else None,
        }

        diag = manifest_rules.get(rid)
        if diag is None:
            missing_manifest.append(rid)
            output_rules.append({
                **base,
                "status": "missing_manifest",
            })
            continue

        if diag.get("status") != "split_valid":
            summary["manual_or_external_rules"] += 1
            output_rules.append({
                **base,
                "status": "manual_or_external",
                "split_status": diag.get("status"),
            })
            continue

        oval_path = args.split_root / diag["path"]
        provenance_path = oval_path.parent / "provenance.json"
        ir = oval_semantic_ir.parse(oval_path, provenance_path)
        if ir.get("unresolved_references"):
            raise ValueError(
                f"{rid}: unresolved OVAL references: "
                + ", ".join(ir["unresolved_references"][:10])
            )

        assessment, migration = converter.compile_oval_assessment(
            {
                "id": rid,
                "title": rule.get("title"),
                "check_model": None,
            },
            ir,
            catalog,
        )

        if migration.get("status") == "unsupported":
            summary["blocked_automated_rules"] += 1
            output_rules.append({
                **base,
                "status": "unsupported",
                "migration": migration,
                "qualified_test_types": sorted({
                    f'{test.get("namespace","")}#{test.get("type","")}'
                    for test in ir.get("tests", [])
                }),
            })
            continue

        exact, shape = assessment_fingerprints(assessment)
        summary["supported_automated_assessments"] += 1
        output_rules.append({
            **base,
            "status": "automated",
            "migration_status": migration.get("status"),
            "exact_fingerprint": exact,
            "shape_fingerprint": shape,
            "qualified_test_types": sorted({
                f'{test.get("namespace","")}#{test.get("type","")}'
                for test in ir.get("tests", [])
            }),
        })

    if missing_manifest:
        summary["missing_manifest_rules"] = len(missing_manifest)
        raise ValueError(
            f"{len(missing_manifest)} XCCDF rules missing from split manifest: "
            + ", ".join(missing_manifest[:10])
        )

    result = {
        "format": "scap-ng-benchmark-reuse-inventory-0.1",
        "source": manifest.get("source"),
        "benchmark": {
            "component_id": component_id,
            "id": benchmark.get("id"),
            "title": benchmark_ir.child_text(benchmark, "title"),
            "version": benchmark_ir.child_text(benchmark, "version"),
            "artifact": args.source_zip.name,
        },
        "summary": summary,
        "rules": output_rules,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "benchmark": result["benchmark"],
        "summary": summary,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
