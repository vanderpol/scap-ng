#!/usr/bin/env python3
"""Render measured exact SCAP-NG assessment reuse in all three candidate styles.

Input is the cross-benchmark reuse report produced by
analyze_scapng_assessment_reuse.py plus the same canonical benchmark files used
to produce that report.

Only proven exact semantic-reuse groups are rendered automatically.
Parameterization candidates remain report-only until reviewed.
"""
from __future__ import annotations

import argparse
import copy
import json
import re
from pathlib import Path

import yaml

from render_ansible_inspired_benchmark import transform_assessment


SPEC = "0.1-prototype"


def safe_id(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_") or "unnamed"


def parse_benchmark_arg(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("benchmark must be LABEL=PATH")
    label, raw = value.split("=", 1)
    return label, Path(raw)


def dump_yaml(path: Path, value) -> int:
    text = yaml.safe_dump(value, sort_keys=False, allow_unicode=True, width=120)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return len(text.encode("utf-8"))


def stripped_shared_assessment(assessment: dict, shared_id: str, members: list[dict]) -> dict:
    out = copy.deepcopy(assessment)
    out["id"] = shared_id
    migration = copy.deepcopy(out.get("migration") or {})
    migration.pop("source_rule", None)
    migration.pop("semantic_ir_sha256", None)
    migration["reuse_scope"] = "cross-benchmark-exact-semantic-equivalence"
    out["migration"] = migration
    out.pop("semantic_fingerprint_sha256", None)
    if members:
        out["exact_reuse_fingerprint_sha256"] = members[0]["exact_fingerprint"]
    out.pop("source_check_context", None)
    out.pop("source_check_logic", None)
    out["reuse_provenance"] = [
        {
            "benchmark": x["benchmark"],
            "rule_id": x["rule_id"],
            "title": x.get("title"),
            "exact_fingerprint": x["exact_fingerprint"],
        }
        for x in members
    ]
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("reuse_report", type=Path)
    ap.add_argument(
        "benchmarks",
        nargs="+",
        type=parse_benchmark_arg,
        help="LABEL=path/to/canonical-benchmark.json",
    )
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument(
        "--include-rule",
        action="append",
        default=[],
        help="Render only exact-reuse groups containing this rule ID. Repeatable.",
    )
    args = ap.parse_args()

    report = json.loads(args.reuse_report.read_text(encoding="utf-8"))
    index = {}
    for label, path in args.benchmarks:
        doc = json.loads(path.read_text(encoding="utf-8"))
        for row in doc.get("rules", []):
            rid = (row.get("policy") or {}).get("id")
            if rid:
                index[(label, rid)] = row

    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)

    groups = report.get("cross_benchmark_exact_reuse_groups", [])
    if args.include_rule:
        wanted=set(args.include_rule)
        groups=[
            group for group in groups
            if any(x.get("rule_id") in wanted for x in group.get("instances",[]))
        ]
        missing=wanted-{
            x.get("rule_id")
            for group in groups
            for x in group.get("instances",[])
        }
        if missing:
            raise ValueError(
                "requested rule IDs were not found in exact cross-benchmark reuse groups: "
                + ", ".join(sorted(missing))
            )
    metrics = []
    manifest_groups = []

    for ordinal, group in enumerate(groups, 1):
        members = group["instances"]
        first = members[0]
        representative = index[(first["benchmark"], first["rule_id"])]
        assessment = representative.get("assessment")
        if not assessment:
            raise ValueError(
                f"reuse group representative has no assessment: "
                f"{first['benchmark']} {first['rule_id']}"
            )

        group_id = f"exact-{ordinal:03d}-{group['fingerprint'][:12]}"
        shared_id = f"ng.shared.{group['fingerprint'][:24]}"
        shared = stripped_shared_assessment(assessment, shared_id, members)
        group_root = out / "groups" / group_id

        split_assessment_bytes = dump_yaml(
            group_root / "split-policy-assessment-binding" / "shared-assessment.yaml",
            {
                "scap_ng": SPEC,
                "prototype": True,
                "model": "split-policy-assessment-binding",
                "assessment": shared,
            },
        )
        split_bindings = [
            {
                "benchmark": member["benchmark"],
                "rule": member["rule_id"],
                "assessment": shared_id,
                "assessment_version": shared.get("version", 1),
                "reuse_evidence": "equivalent_oval_semantics",
            }
            for member in members
        ]
        split_binding_bytes = dump_yaml(
            group_root / "split-policy-assessment-binding" / "bindings.yaml",
            {
                "scap_ng": SPEC,
                "prototype": True,
                "model": "split-policy-assessment-binding",
                "bindings": split_bindings,
            },
        )

        ansible_assessment = transform_assessment(shared)
        ansible_assessment_bytes = dump_yaml(
            group_root / "ansible-inspired" / "shared-assessment.yaml",
            {
                "scap_ng": SPEC,
                "prototype": True,
                "authoring_style": "ansible-inspired",
                "runtime_dependency": "none",
                "assessment": ansible_assessment,
            },
        )
        ansible_bindings = [
            {
                "benchmark": m["benchmark"],
                "rule": m["rule_id"],
                "assessment": shared_id,
                "assessment_version": shared.get("version", 1),
                "reuse_evidence": "equivalent_oval_semantics",
            }
            for m in members
        ]
        ansible_binding_bytes = dump_yaml(
            group_root / "ansible-inspired" / "bindings.yaml",
            {
                "scap_ng": SPEC,
                "prototype": True,
                "authoring_style": "ansible-inspired",
                "runtime_dependency": "none",
                "bindings": ansible_bindings,
            },
        )

        combined_base_bytes = dump_yaml(
            group_root / "combined-rule" / "shared-rule-base.yaml",
            {
                "scap_ng": SPEC,
                "prototype": True,
                "model": "combined-rule",
                "shared_rule_base": {
                    "id": shared_id,
                    "assessment": shared,
                    "reuse_evidence": "equivalent_oval_semantics",
                    "overlay_contract": (
                        "Policy identity/content may vary per overlay; assessment "
                        "semantics are immutable."
                    ),
                },
            },
        )
        combined_overlay_bytes = 0
        for member in members:
            row = index[(member["benchmark"], member["rule_id"])]
            policy = copy.deepcopy(row.get("policy") or {})
            combined_overlay_bytes += dump_yaml(
                group_root
                / "combined-rule"
                / "overlays"
                / safe_id(member["benchmark"])
                / f"{safe_id(member['rule_id'])}.yaml",
                {
                    "scap_ng": SPEC,
                    "prototype": True,
                    "model": "combined-rule",
                    "overlay": {
                        "extends_shared_rule": shared_id,
                        "benchmark": member["benchmark"],
                        "policy": policy,
                        "reuse_evidence": "equivalent_oval_semantics",
                    },
                },
            )

        canonical_assessment_yaml_bytes = sum(
            len(
                yaml.safe_dump(
                    index[(m["benchmark"], m["rule_id"])]["assessment"],
                    sort_keys=False,
                    allow_unicode=True,
                    width=120,
                ).encode("utf-8")
            )
            for m in members
        )
        ansible_duplicated_yaml_bytes = sum(
            len(
                yaml.safe_dump(
                    transform_assessment(
                        index[(m["benchmark"], m["rule_id"])]["assessment"]
                    ),
                    sort_keys=False,
                    allow_unicode=True,
                    width=120,
                ).encode("utf-8")
            )
            for m in members
        )

        metric = {
            "group_id": group_id,
            "fingerprint": group["fingerprint"],
            "instances": len(members),
            "benchmarks": group["benchmarks"],
            "duplicate_assessment_definitions_avoided": len(members) - 1,
            "baseline": {
                "canonical_duplicated_assessment_yaml_bytes": canonical_assessment_yaml_bytes,
                "ansible_duplicated_assessment_yaml_bytes": ansible_duplicated_yaml_bytes,
            },
            "combined_rule": {
                "shared_base_bytes": combined_base_bytes,
                "overlay_bytes_including_policy_content": combined_overlay_bytes,
                "illustrative_source_bytes": combined_base_bytes + combined_overlay_bytes,
            },
            "split_policy_assessment_binding": {
                "shared_assessment_bytes": split_assessment_bytes,
                "binding_bytes": split_binding_bytes,
                "illustrative_automation_bytes_excluding_policy_files": split_assessment_bytes + split_binding_bytes,
            },
            "ansible_inspired": {
                "shared_assessment_bytes": ansible_assessment_bytes,
                "binding_bytes": ansible_binding_bytes,
                "illustrative_automation_bytes_excluding_policy_files": ansible_assessment_bytes + ansible_binding_bytes,
            },
        }
        metrics.append(metric)
        manifest_groups.append({
            "group_id": group_id,
            "fingerprint": group["fingerprint"],
            "shared_assessment_id": shared_id,
            "instance_count": len(members),
            "benchmarks": group["benchmarks"],
            "members": [
                {
                    "benchmark": m["benchmark"],
                    "rule_id": m["rule_id"],
                    "title": m.get("title"),
                }
                for m in members
            ],
        })

    total_instances = sum(x["instances"] for x in metrics)
    duplicates_avoided = sum(x["duplicate_assessment_definitions_avoided"] for x in metrics)
    summary = {
        "format": "scap-ng-exact-reuse-views-0.1",
        "exact_cross_benchmark_groups": len(metrics),
        "assessment_instances_in_reuse_groups": total_instances,
        "shared_assessments_required": len(metrics),
        "duplicate_assessment_definitions_avoided": duplicates_avoided,
        "reuse_group_definition_reduction_pct": (
            round(100.0 * duplicates_avoided / total_instances, 2)
            if total_instances else 0.0
        ),
        "important_scope_note": (
            "This directory is an illustrative subset of exact reuse groups selected "
            "for review. Corpus-wide reduction is reported separately by the reuse "
            "analyzer."
        ),
    }

    (out / "reuse-view-manifest.json").write_text(
        json.dumps(
            {
                "summary": summary,
                "groups": manifest_groups,
                "metrics_scope_note": (
                    "Byte counts are descriptive, not a direct total-source-size comparison: "
                    "combined overlays include policy content while split/Ansible policy files "
                    "are external to these reuse views."
                ),
                "metrics": metrics,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    readme = [
        "# Exact assessment reuse rendered three ways",
        "",
        "Generated only from cross-benchmark groups whose complete normalized OVAL semantics are equivalent.",
        "",
        "The same measured reuse groups are represented as:",
        "",
        "- combined-rule: one shared technical rule base plus policy overlays;",
        "- split policy/assessment/binding: one shared assessment plus explicit bindings;",
        "- Ansible-inspired: one shared Ansible-like assessment plus explicit bindings/vars surface.",
        "",
        "Parameterization candidates are intentionally excluded until reviewed.",
        "",
        "## Summary",
        "",
        f"- Exact cross-benchmark reuse groups: **{summary['exact_cross_benchmark_groups']}**",
        f"- Assessment instances in those groups: **{summary['assessment_instances_in_reuse_groups']}**",
        f"- Shared assessments required: **{summary['shared_assessments_required']}**",
        f"- Duplicate assessment definitions avoided: **{summary['duplicate_assessment_definitions_avoided']}**",
        f"- Definition reduction within exact-reuse groups: **{summary['reuse_group_definition_reduction_pct']}%**",
        "",
        "See reuse-view-manifest.json for per-group source-size and mapping metrics.",
        "",
    ]
    (out / "README.md").write_text("\n".join(readme), encoding="utf-8")

    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
