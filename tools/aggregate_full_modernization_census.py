#!/usr/bin/env python3
"""Aggregate the 65-package SCAP-NG 0.3 modernization research census."""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

EXPECTED_BLOCKERS = {
    "U_MS_SQL_Server_2016_Database_V3R4_STIG_SCAP_1-4_Benchmark-enhancedV13-signed.zip":
        "nonstandard source capability independent.sqlext",
    "U_MS_SQL_Server_2016_Instance_V3R6_STIG_SCAP_1-4_Benchmark-enhancedV14-signed.zip":
        "nonstandard source capability independent.sqlext",
    "U_MS_SQL_Server_2022_Database_V1R2_STIG_SCAP_1-4_Benchmark-enhancedV8-signed.zip":
        "nonstandard source capability independent.sqlext",
    "U_MS_SQL_Server_2022_Instance_V1R3_STIG_SCAP_1-4_Benchmark-enhancedV8-signed.zip":
        "nonstandard source capability independent.sqlext",
}


def add_counts(target: Counter, value: dict) -> None:
    for key, count in value.items():
        target[key] += int(count or 0)


def pct(n: int, d: int) -> float:
    return round(100.0 * n / d, 2) if d else 0.0


def reduction(before: int, after: int) -> float:
    return round(100.0 * (before - after) / before, 2) if before else 0.0


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("root", type=Path)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--markdown", type=Path, required=True)
    p.add_argument("--niwc-revision", required=True)
    args = p.parse_args()

    statuses = [
        json.loads(x.read_text(encoding="utf-8"))
        for x in sorted(args.root.rglob("status/*.json"))
    ]
    reports = [
        json.loads(x.read_text(encoding="utf-8"))
        for x in sorted(args.root.rglob("reports/*.json"))
    ]

    if len(statuses) != 65:
        raise SystemExit(f"expected 65 package status records, found {len(statuses)}")
    artifacts = [x["artifact"] for x in statuses]
    if len(set(artifacts)) != 65:
        raise SystemExit("duplicate package status records")

    blocked = [x for x in statuses if x["status"] != "generated"]
    unexpected = []
    for row in blocked:
        marker = EXPECTED_BLOCKERS.get(row["artifact"])
        if row["status"] != "blocked" or not marker or marker not in row.get("log_tail", ""):
            unexpected.append(row)
    for artifact in EXPECTED_BLOCKERS:
        row = next((x for x in statuses if x["artifact"] == artifact), None)
        if row is None or row["status"] != "blocked":
            unexpected.append({
                "artifact": artifact,
                "status": "missing" if row is None else row["status"],
                "reason": "expected sqlext blocker disappeared; review baseline",
            })

    generated = [x for x in statuses if x["status"] == "generated"]
    if len(generated) != 61 or len(blocked) != 4 or unexpected:
        raise SystemExit(
            f"expected 61 generated + 4 known blockers; got generated={len(generated)} "
            f"blocked={len(blocked)} unexpected={len(unexpected)}"
        )

    by_artifact = {r.get("source_artifact"): r for r in reports}
    missing = [x["artifact"] for x in generated if x["artifact"] not in by_artifact]
    extra = [k for k in by_artifact if k not in set(artifacts)]
    if len(reports) != 61 or missing or extra:
        raise SystemExit(
            f"expected 61 census reports; got {len(reports)} "
            f"missing={missing} extra={extra}"
        )

    numeric = Counter()
    classes = Counter()
    residuals = Counter()
    foreach_reasons = Counter()
    observation_consumers = Counter()
    observation_exports = Counter()
    classes_by_kind = defaultdict(Counter)
    residuals_by_kind = defaultdict(Counter)
    packages_with_observation = 0
    package_rows = []

    for report in reports:
        s = report["summary"]
        for key, value in s.items():
            if (
                isinstance(value, (int, float))
                and not isinstance(value, bool)
                and not key.endswith("_pct")
            ):
                numeric[key] += value

        add_counts(classes, s.get("classification_counts") or {})
        add_counts(residuals, s.get("residual_reason_counts") or {})
        add_counts(foreach_reasons, s.get("foreach_review_reason_counts") or {})
        add_counts(observation_consumers, s.get("observation_consumer_counts") or {})
        add_counts(observation_exports, s.get("observation_export_reference_counts") or {})

        for kind, counts in (s.get("classification_counts_by_kind") or {}).items():
            add_counts(classes_by_kind[kind], counts)
        for kind, counts in (s.get("residual_reason_counts_by_kind") or {}).items():
            add_counts(residuals_by_kind[kind], counts)

        if int(s.get("observation_artifacts", 0) or 0) > 0:
            packages_with_observation += 1

        package_rows.append({
            "source_artifact": report["source_artifact"],
            "label": report["label"],
            "automated_assessments": s.get("automated_assessments", 0),
            "rule_assessments": s.get("rule_assessments", 0),
            "applicability_assessments": s.get("applicability_assessments", 0),
            "classifications": s.get("classification_counts", {}),
            "rule_classifications": (
                s.get("classification_counts_by_kind") or {}
            ).get("rule", {}),
            "observation_artifacts": s.get("observation_artifacts", 0),
            "foreach_rewrites": s.get("foreach_rewrites_applied", 0),
            "object_scope_reduction_pct": s.get("object_scope_reduction_pct", 0),
            "state_scope_reduction_pct": s.get("state_scope_reduction_pct", 0),
            "variable_reduction_pct": s.get("variable_reduction_pct", 0),
        })

    summary = dict(numeric)
    summary.update({
        "source_packages": 65,
        "generated_packages": 61,
        "known_blocked_packages": 4,
        "unexpected_blocked_packages": 0,
        "packages_with_observation_artifacts": packages_with_observation,
        "classification_counts": dict(classes),
        "classification_counts_by_kind": {
            kind: dict(counts) for kind, counts in sorted(classes_by_kind.items())
        },
        "residual_reason_counts": dict(residuals),
        "residual_reason_counts_by_kind": {
            kind: dict(counts) for kind, counts in sorted(residuals_by_kind.items())
        },
        "foreach_review_reason_counts": dict(foreach_reasons),
        "observation_consumer_counts": dict(observation_consumers),
        "observation_export_reference_counts": dict(observation_exports),
        "object_scope_reduction_pct": reduction(
            numeric["baseline_objects"], numeric["modernized_objects"]
        ),
        "state_scope_reduction_pct": reduction(
            numeric["baseline_states"], numeric["modernized_states"]
        ),
        "variable_reduction_pct": reduction(
            numeric["baseline_variables"], numeric["modernized_variables"]
        ),
        "named_reference_reduction_pct": reduction(
            numeric["baseline_named_component_cross_references"],
            numeric["modernized_named_component_cross_references"],
        ),
        "normalized_line_reduction_pct": reduction(
            numeric["baseline_normalized_lines"],
            numeric["modernized_normalized_lines"],
        ),
        "normalized_byte_reduction_pct": reduction(
            numeric["baseline_normalized_bytes"],
            numeric["modernized_normalized_bytes"],
        ),
    })

    rule_classes = classes_by_kind.get("rule", Counter())
    rule_total = sum(rule_classes.values())
    summary["rule_assessment_classification_pct"] = {
        key: pct(value, rule_total) for key, value in sorted(rule_classes.items())
    }

    out = {
        "format": "scap-ng-full-modernization-census-0.1",
        "status": "research_only_not_accepted_design",
        "niwc_revision": args.niwc_revision,
        "scope": {
            "faithful_source": "fresh same-run current conversion",
            "applied_exact": [
                "consumer-local Object/State presentation",
                "private Set-operand locality",
                "Variable-local Object locality",
                "foreach.direct-object-component.at-least-one.v1",
                "proven shared Observation extraction shapes",
            ],
            "measured_not_applied": [
                "single-Test explicit evaluate-root authoring ceremony"
            ],
            "intentionally_not_rewritten": [
                "conditional/case native authoring",
                "linux.fstab typed native capability",
                "violation-query positive spelling",
                "general concat/multi-source foreach",
                "domain-specific semantic changes",
            ],
        },
        "summary": summary,
        "known_blockers": blocked,
        "packages": sorted(package_rows, key=lambda x: x["source_artifact"]),
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    rc = summary.get("classification_counts_by_kind", {}).get("rule", {})
    rp = summary.get("rule_assessment_classification_pct", {})
    rule_residuals = (
        summary.get("residual_reason_counts_by_kind", {}).get("rule", {})
    )

    lines = [
        "# Full 65-package SCAP-NG 0.3 modernization census",
        "",
        "**Status:** research checkpoint only; no schema change or design acceptance.",
        "",
        f"- NIWC revision: `{args.niwc_revision}`",
        "- Source packages: **65**; generated: **61**; known `independent.sqlext` blockers: **4**; unexpected blockers: **0**.",
        f"- Automated Assessments measured: **{summary.get('automated_assessments', 0)}** "
        f"(Rules **{summary.get('rule_assessments', 0)}**, applicability "
        f"**{summary.get('applicability_assessments', 0)}**).",
        "",
        "## Exact modernization effects",
        "",
        f"- top-level Objects: **{summary.get('baseline_objects', 0)} -> "
        f"{summary.get('modernized_objects', 0)}** "
        f"({summary['object_scope_reduction_pct']}% reduction)",
        f"- top-level States: **{summary.get('baseline_states', 0)} -> "
        f"{summary.get('modernized_states', 0)}** "
        f"({summary['state_scope_reduction_pct']}% reduction)",
        f"- named Variables: **{summary.get('baseline_variables', 0)} -> "
        f"{summary.get('modernized_variables', 0)}** "
        f"({summary['variable_reduction_pct']}% reduction)",
        f"- named component references: "
        f"**{summary.get('baseline_named_component_cross_references', 0)} -> "
        f"{summary.get('modernized_named_component_cross_references', 0)}** "
        f"({summary['named_reference_reduction_pct']}% reduction)",
        f"- foreach v1 rewrites: **{summary.get('foreach_rewrites_applied', 0)}** "
        f"across **{summary.get('foreach_rewritten_assessments', 0)}** Assessments",
        f"- Observation artifacts: **{summary.get('observation_artifacts', 0)}** "
        f"across **{summary.get('packages_with_observation_artifacts', 0)}** packages; "
        f"consumer Assessments: **{summary.get('observation_consumer_assessments', 0)}**",
        "",
        "## Rule Assessment outcome after proven exact simplifications",
        "",
        f"- local/simple: **{rc.get('local_simple', 0)}** "
        f"({rp.get('local_simple', 0)}%)",
        f"- bounded dataflow: **{rc.get('bounded_dataflow', 0)}** "
        f"({rp.get('bounded_dataflow', 0)}%)",
        f"- shared Observation consumer: "
        f"**{rc.get('shared_observation_consumer', 0)}** "
        f"({rp.get('shared_observation_consumer', 0)}%)",
        f"- meaningfully complex: **{rc.get('meaningfully_complex', 0)}** "
        f"({rp.get('meaningfully_complex', 0)}%)",
        "",
        "## Residual complexity",
        "",
    ]
    for reason, count in sorted(
        rule_residuals.items(), key=lambda kv: (-kv[1], kv[0])
    ):
        lines.append(f"- {reason}: **{count}**")

    lines += [
        "",
        "The four source blockers remain outside the Assessment classification denominator.",
        "Conditional/case authoring, `linux.fstab`, and other intentionally semantic",
        "native modernizations were not applied merely to make this census look smaller.",
        "",
    ]

    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
