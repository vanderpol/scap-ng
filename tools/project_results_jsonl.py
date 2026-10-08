#!/usr/bin/env python3
"""Deterministic SCAP-NG canonical-result -> JSONL/SIEM projection.

The projection is deliberately derived and denormalized. It does not define or
modify canonical result semantics.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable


def _target_index(scan: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {t["id"]: t for t in scan.get("targets", [])}


def project_scan(
    scan_document: dict[str, Any],
    benchmark_documents: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    scan = scan_document["scan_result"]
    targets = _target_index(scan)

    events: list[dict[str, Any]] = [{
        "event_type": "scan_summary",
        "result_schema_version": scan["result_schema_version"],
        "run_id": scan["run_id"],
        "started_at": scan["started_at"],
        "completed_at": scan.get("completed_at"),
        "scanner": scan.get("scanner", {}),
        "targets": scan.get("targets", []),
        "benchmark_results": scan.get("benchmark_results", []),
        "signature_status": scan.get("signature_status"),
    }]

    for entry in scan.get("benchmark_results", []):
        ref = entry["benchmark_result_ref"]
        if ref not in benchmark_documents:
            raise KeyError(f"missing Benchmark Result for {ref}")
        benchmark_doc = benchmark_documents[ref]["benchmark_result"]

        if benchmark_doc.get("run_id") != scan.get("run_id"):
            raise ValueError(
                f"run_id mismatch for {ref}: "
                f"{benchmark_doc.get('run_id')!r} != {scan.get('run_id')!r}"
            )

        target_ref = entry["target_ref"]
        target = targets.get(target_ref)
        if target is None:
            raise KeyError(f"unknown target_ref {target_ref!r} for {ref}")

        canonical_benchmark = benchmark_doc.get("benchmark", {})
        if canonical_benchmark.get("id") != entry.get("benchmark_id"):
            raise ValueError(
                f"benchmark id mismatch for {ref}: "
                f"{canonical_benchmark.get('id')!r} != {entry.get('benchmark_id')!r}"
            )

        effective_policy = benchmark_doc.get("effective_policy", {})
        shared = {
            "result_schema_version": scan["result_schema_version"],
            "run_id": scan["run_id"],
            "started_at": benchmark_doc.get("started_at", scan.get("started_at")),
            "completed_at": benchmark_doc.get("completed_at", scan.get("completed_at")),
            "scanner": scan.get("scanner", {}),
            "target_ref": target_ref,
            "target": target,
            "benchmark": canonical_benchmark,
            "profile_id": entry.get("profile_id", effective_policy.get("profile")),
            "tailoring_id": entry.get("tailoring_id"),
            "source_benchmark_result_ref": ref,
            "source_signature_status": scan.get("signature_status"),
        }

        for rule in benchmark_doc.get("rule_results", []):
            event = {
                "event_type": "rule_result",
                **shared,
                "rule_id": rule["rule_id"],
                "title": rule.get("title"),
                "severity": rule.get("severity"),
                "weight": rule.get("weight"),
                "check_selector": rule.get(
                    "check_selector",
                    effective_policy.get("check_selectors", {}).get(rule["rule_id"]),
                ),
                "parameters": rule.get("parameters", effective_policy.get("parameters", {})),
                "applicability": rule.get("applicability"),
                "outcome": rule["outcome"],
                "message": rule.get("message"),
                "reason": rule.get("reason"),
                "assessment": rule.get("assessment"),
                "instances": rule.get("instances", []),
                "evidence_refs": rule.get("evidence_refs", []),
            }
            # Preserve 0.1/0.2 frozen projections; new 0.3 fields are
            # copied only when present in the authoritative Benchmark Result.
            if "findings" in rule:
                event["findings"] = rule["findings"]
            if "finding_counts" in rule:
                event["finding_counts"] = rule["finding_counts"]
            events.append(event)

    return events


def jsonl_lines(events: Iterable[dict[str, Any]]) -> list[str]:
    return [
        json.dumps(event, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        for event in events
    ]


def _parse_benchmark_arg(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError(
            "--benchmark-result must be REF=PATH, where REF matches "
            "scan_result.benchmark_results[].benchmark_result_ref"
        )
    ref, raw_path = value.split("=", 1)
    if not ref or not raw_path:
        raise argparse.ArgumentTypeError("--benchmark-result requires non-empty REF and PATH")
    return ref, Path(raw_path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scan-result", required=True, type=Path)
    parser.add_argument(
        "--benchmark-result",
        action="append",
        default=[],
        type=_parse_benchmark_arg,
        metavar="REF=PATH",
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    scan = json.loads(args.scan_result.read_text(encoding="utf-8"))
    benchmarks = {
        ref: json.loads(path.read_text(encoding="utf-8"))
        for ref, path in args.benchmark_result
    }
    lines = jsonl_lines(project_scan(scan, benchmarks))
    payload = "\n".join(lines) + ("\n" if lines else "")

    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
