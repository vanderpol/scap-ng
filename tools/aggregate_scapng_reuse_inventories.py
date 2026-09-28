#!/usr/bin/env python3
"""Aggregate compact SCAP-NG reuse inventories across a benchmark corpus."""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


def pct(n: int, d: int) -> float:
    return round(100.0 * n / d, 2) if d else 0.0


def group_rows(rows: list[dict], key: str) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        value = row.get(key)
        if value:
            out[value].append(row)
    return out


def summarize_group(fp: str, rows: list[dict]) -> dict:
    benchmarks = sorted({x["benchmark_key"] for x in rows})
    return {
        "fingerprint": fp,
        "instance_count": len(rows),
        "benchmark_count": len(benchmarks),
        "benchmarks": benchmarks,
        "instances": [
            {
                "benchmark": x["benchmark_key"],
                "rule_id": x.get("rule_id"),
                "title": x.get("title"),
            }
            for x in sorted(
                rows,
                key=lambda x: (
                    x["benchmark_key"],
                    x.get("rule_id") or "",
                ),
            )
        ],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("inventories", nargs="+", type=Path)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    benchmark_rows = []
    policy_rows = []
    automated_rows = []
    blocked_rows = []
    manual_count = 0
    source_rule_count = 0

    for path in args.inventories:
        doc = json.loads(path.read_text(encoding="utf-8"))
        bench = doc.get("benchmark") or {}
        key = path.stem
        benchmark_rows.append({
            "benchmark_key": key,
            "id": bench.get("id"),
            "title": bench.get("title"),
            "version": bench.get("version"),
            "artifact": bench.get("artifact"),
            "summary": doc.get("summary"),
        })
        source_rule_count += (doc.get("summary") or {}).get("source_rules", 0)
        manual_count += (doc.get("summary") or {}).get("manual_or_external_rules", 0)

        for rule in doc.get("rules", []):
            common = {
                "benchmark_key": key,
                "rule_id": rule.get("rule_id"),
                "title": rule.get("title"),
                "check_text_fingerprint": rule.get("check_text_fingerprint"),
            }
            policy_rows.append(common)
            if rule.get("status") == "automated":
                automated_rows.append({
                    **common,
                    "exact_fingerprint": rule.get("exact_fingerprint"),
                    "shape_fingerprint": rule.get("shape_fingerprint"),
                })
            elif rule.get("status") == "unsupported":
                blocked_rows.append({
                    **common,
                    "migration": rule.get("migration"),
                    "qualified_test_types": rule.get("qualified_test_types", []),
                })

    by_exact = group_rows(automated_rows, "exact_fingerprint")
    by_shape = group_rows(automated_rows, "shape_fingerprint")
    by_check = group_rows(policy_rows, "check_text_fingerprint")

    exact_reuse_groups = {
        fp: rows for fp, rows in by_exact.items() if len(rows) > 1
    }
    cross_exact_groups = {
        fp: rows
        for fp, rows in exact_reuse_groups.items()
        if len({x["benchmark_key"] for x in rows}) > 1
    }
    check_alignment_groups = {
        fp: rows
        for fp, rows in by_check.items()
        if len(rows) > 1
        and len({x["benchmark_key"] for x in rows}) > 1
    }
    parameterization_candidates = {
        fp: rows
        for fp, rows in by_shape.items()
        if len(rows) > 1
        and len({x.get("exact_fingerprint") for x in rows}) > 1
    }

    total_automated = len(automated_rows)
    exact_unique = len(by_exact)
    exact_avoided = total_automated - exact_unique
    shape_unique = len(by_shape)
    shape_avoided = total_automated - shape_unique

    cross_instances = sum(len(rows) for rows in cross_exact_groups.values())
    cross_duplicate_units = sum(
        len(rows) - 1 for rows in cross_exact_groups.values()
    )

    blocker_types: Counter[str] = Counter()
    blocker_by_benchmark: dict[str, Counter[str]] = defaultdict(Counter)
    blocked_rule_count_by_benchmark: Counter[str] = Counter()
    for row in blocked_rows:
        benchmark_key=row["benchmark_key"]
        blocked_rule_count_by_benchmark[benchmark_key] += 1
        migration = row.get("migration") or {}
        for item in migration.get("deprecated_tests", []) or []:
            qtype=item.get("qualified_type") or "<unknown>"
            blocker_types[qtype] += 1
            blocker_by_benchmark[benchmark_key][qtype] += 1

    fanout_by_benchmark_count = Counter()
    fanout_by_instance_count = Counter()
    for rows in cross_exact_groups.values():
        fanout_by_benchmark_count[
            len({x["benchmark_key"] for x in rows})
        ] += 1
        fanout_by_instance_count[len(rows)] += 1

    exact_group_summaries = [
        summarize_group(fp, rows)
        for fp, rows in cross_exact_groups.items()
    ]
    exact_group_summaries.sort(
        key=lambda x: (
            -x["benchmark_count"],
            -x["instance_count"],
            x["fingerprint"],
        )
    )

    check_group_summaries = [
        summarize_group(fp, rows)
        for fp, rows in check_alignment_groups.items()
    ]
    check_group_summaries.sort(
        key=lambda x: (
            -x["benchmark_count"],
            -x["instance_count"],
            x["fingerprint"],
        )
    )

    result = {
        "format": "scap-ng-corpus-reuse-analysis-0.1",
        "benchmarks": benchmark_rows,
        "summary": {
            "benchmarks": len(benchmark_rows),
            "source_rules": source_rule_count,
            "supported_automated_assessments": total_automated,
            "manual_or_external_rules": manual_count,
            "blocked_automated_rules": len(blocked_rows),
            "exact_unique_assessments": exact_unique,
            "exact_duplicate_assessment_units_avoided": exact_avoided,
            "exact_maintenance_unit_reduction_pct": pct(
                exact_avoided, total_automated
            ),
            "exact_reuse_groups": len(exact_reuse_groups),
            "cross_benchmark_exact_reuse_groups": len(cross_exact_groups),
            "cross_benchmark_exact_reuse_instances": cross_instances,
            "cross_benchmark_duplicate_units_avoided": cross_duplicate_units,
            "check_text_alignment_groups": len(check_alignment_groups),
            "shape_unique_assessments": shape_unique,
            "parameterization_candidate_units_avoided_upper_bound": shape_avoided,
            "parameterization_candidate_reduction_pct_upper_bound": pct(
                shape_avoided, total_automated
            ),
            "parameterization_candidate_groups": len(parameterization_candidates),
        },
        "fanout": {
            "exact_groups_by_benchmark_count": {
                str(k): v for k, v in sorted(fanout_by_benchmark_count.items())
            },
            "exact_groups_by_instance_count": {
                str(k): v for k, v in sorted(fanout_by_instance_count.items())
            },
        },
        "source_remediation_blockers": {
            "rules": len(blocked_rows),
            "by_effectively_deprecated_test": dict(blocker_types.most_common()),
            "by_benchmark": [
                {
                    "benchmark": benchmark,
                    "blocked_rules": blocked_rule_count_by_benchmark[benchmark],
                    "deprecated_test_references": dict(
                        blocker_by_benchmark[benchmark].most_common()
                    ),
                }
                for benchmark in sorted(
                    blocked_rule_count_by_benchmark,
                    key=lambda x:(
                        -blocked_rule_count_by_benchmark[x],
                        x,
                    ),
                )
            ],
        },
        "maintenance_cost_model": {
            "duplicate_assessment_units_avoided": exact_avoided,
            "formulas": {
                "full_review_cycle_hours_avoided": (
                    "duplicate_assessment_units_avoided "
                    "* average_hours_per_assessment_review"
                ),
                "annual_maintenance_hours_avoided": (
                    "duplicate_assessment_units_avoided "
                    "* average_change_events_per_year "
                    "* average_hours_per_change_review_and_test"
                ),
                "annual_labor_cost_avoided": (
                    "annual_maintenance_hours_avoided * loaded_hourly_labor_rate"
                ),
            },
            "note": (
                "Labor/time/rate assumptions are intentionally not embedded. "
                "Apply organization-specific observed values."
            ),
        },
        "largest_cross_benchmark_exact_reuse_groups": exact_group_summaries[:100],
        "largest_check_text_alignment_groups": check_group_summaries[:100],
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
