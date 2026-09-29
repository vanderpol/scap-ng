#!/usr/bin/env python3
"""Promote proven exact cross-benchmark Assessment reuse into shared NG source.

This tool consumes:
  * the exact-reuse report from analyze_scapng_assessment_reuse.py; and
  * the canonical converted benchmarks used to build that report.

Only cross-benchmark groups whose complete normalized automated Assessment
semantics are identical are promoted automatically. Parameterization candidates
are intentionally excluded.

Each promoted group produces one shared *.assessment.yaml plus per-benchmark
binding files. Rule/policy identity remains benchmark-local. Selector identity
is preserved; only references to the duplicate automated Assessment are
rewritten to the shared Assessment ID.
"""
from __future__ import annotations

import argparse
import copy
import json
import re
import shutil
from pathlib import Path

import yaml


SPEC = "0.1-prototype"


def safe_id(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_") or "unnamed"


def benchmark_arg(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("benchmark must be LABEL=PATH")
    label, raw = value.split("=", 1)
    if not label:
        raise argparse.ArgumentTypeError("benchmark label may not be empty")
    return label, Path(raw)


def dump_yaml(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(value, sort_keys=False, allow_unicode=True, width=120),
        encoding="utf-8",
    )


def stripped_shared_assessment(
    assessment: dict,
    shared_id: str,
    fingerprint: str,
    members: list[dict],
) -> dict:
    out = copy.deepcopy(assessment)
    out["id"] = shared_id

    # Remove rule/source-specific provenance while retaining semantic content.
    migration = copy.deepcopy(out.get("migration") or {})
    migration.pop("source_rule", None)
    migration.pop("semantic_ir_sha256", None)
    migration["reuse_scope"] = "cross-benchmark-exact-semantic-equivalence"
    out["migration"] = migration

    out.pop("source_check_context", None)
    out.pop("source_check_logic", None)
    out.pop("semantic_fingerprint_sha256", None)

    out["exact_reuse_fingerprint_sha256"] = fingerprint
    out["reuse_provenance"] = [
        {
            "benchmark": m["benchmark"],
            "rule_id": m["rule_id"],
            "title": m.get("title"),
        }
        for m in members
    ]
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("reuse_report", type=Path)
    ap.add_argument(
        "benchmarks",
        nargs="+",
        type=benchmark_arg,
        help="LABEL=path/to/canonical-benchmark.json",
    )
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()

    report = json.loads(args.reuse_report.read_text(encoding="utf-8"))
    docs = {
        label: json.loads(path.read_text(encoding="utf-8"))
        for label, path in args.benchmarks
    }

    rule_index: dict[tuple[str, str], dict] = {}
    for label, doc in docs.items():
        for row in doc.get("rules", []):
            rid = (row.get("policy") or {}).get("id")
            if rid:
                rule_index[(label, rid)] = row

    out = args.output_dir
    if out.exists():
        shutil.rmtree(out)
    (out / "assessments").mkdir(parents=True)
    (out / "bindings").mkdir(parents=True)

    per_benchmark: dict[str, list[dict]] = {label: [] for label in docs}
    manifest_groups = []
    duplicate_instances_avoided = 0

    groups = report.get("cross_benchmark_exact_reuse_groups", [])
    for group in groups:
        members = group.get("instances", [])
        if len({m.get("benchmark") for m in members}) < 2:
            continue

        fingerprint = group["fingerprint"]
        shared_id = f"ng.shared.{fingerprint[:24]}"

        first = members[0]
        representative = rule_index[(first["benchmark"], first["rule_id"])]
        source_assessment = representative.get("assessment")
        if not source_assessment:
            raise ValueError(
                "exact-reuse representative lacks primary automated assessment: "
                f"{first['benchmark']} {first['rule_id']}"
            )

        shared = stripped_shared_assessment(
            source_assessment,
            shared_id,
            fingerprint,
            members,
        )
        dump_yaml(
            out / "assessments" / f"{safe_id(shared_id)}.assessment.yaml",
            {
                "scap_ng": SPEC,
                "prototype": True,
                "assessment": shared,
            },
        )

        group_members = []
        for member in members:
            label = member["benchmark"]
            rid = member["rule_id"]
            row = rule_index[(label, rid)]
            policy = row.get("policy") or {}
            original = row.get("assessment") or {}
            original_id = original.get("id")

            selectors = []
            for check in policy.get("checks", []) or []:
                rewritten = copy.deepcopy(check)
                if rewritten.get("assessment") == original_id:
                    rewritten["assessment"] = shared_id
                selectors.append(rewritten)

            binding = {
                "rule": rid,
                "shared_assessment": shared_id,
                "replaces_assessment": original_id,
                "checks": selectors,
                "reuse_evidence": "exact_semantic_equivalence",
                "exact_reuse_fingerprint_sha256": fingerprint,
            }
            if policy.get("default_check") is not None:
                binding["default_check"] = policy["default_check"]

            per_benchmark[label].append(binding)
            group_members.append({
                "benchmark": label,
                "rule_id": rid,
                "original_assessment": original_id,
            })

        duplicate_instances_avoided += len(members) - 1
        manifest_groups.append({
            "shared_assessment": shared_id,
            "fingerprint": fingerprint,
            "instance_count": len(members),
            "benchmarks": group.get("benchmarks", []),
            "members": group_members,
        })

    for label, rows in per_benchmark.items():
        dump_yaml(
            out / "bindings" / f"{safe_id(label)}.bindings.yaml",
            {
                "scap_ng": SPEC,
                "prototype": True,
                "benchmark": label,
                "bindings": sorted(rows, key=lambda x: x["rule"]),
            },
        )

    summary = {
        "format": "scap-ng-shared-assessment-catalog-0.1",
        "source_reuse_report_format": report.get("format"),
        "shared_assessment_count": len(manifest_groups),
        "cross_benchmark_rule_instances_rebound": sum(
            len(x["members"]) for x in manifest_groups
        ),
        "duplicate_assessment_definitions_avoided": duplicate_instances_avoided,
        "parameterization_candidates_promoted": 0,
        "promotion_rule": (
            "Only complete normalized automated Assessment semantic equivalence "
            "is promoted automatically."
        ),
    }

    (out / "manifest.json").write_text(
        json.dumps(
            {
                "summary": summary,
                "groups": manifest_groups,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    readme = [
        "# Shared SCAP-NG Assessments",
        "",
        "Generated from proven exact semantic equivalence across the four anchor STIGs.",
        "",
        f"- Shared Assessment definitions: **{summary['shared_assessment_count']}**",
        f"- Rule instances rebound to shared Assessments: **{summary['cross_benchmark_rule_instances_rebound']}**",
        f"- Duplicate Assessment definitions avoided: **{summary['duplicate_assessment_definitions_avoided']}**",
        "",
        "Only exact semantic matches are promoted automatically.",
        "Parameterization candidates remain unshared until separately reviewed and approved.",
        "",
        "Benchmark Rule/policy identity remains benchmark-local. The binding files preserve",
        "each Rule's selector identities while redirecting equivalent automated selectors",
        "to the shared Assessment definition.",
        "",
    ]
    (out / "README.md").write_text("\n".join(readme), encoding="utf-8")

    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
