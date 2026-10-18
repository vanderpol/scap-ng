#!/usr/bin/env python3
"""#232/#239: per-Benchmark Rule->Assessment 0.4-A source version closure.

This is an archive structural compatibility gate, not an executable 0.4
compiler. Never infer version compatibility from the union of all Benchmarks'
declarations. Keep all source documents and versions unchanged.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import PurePosixPath

from v04_a_authoring_graph_index import read_authoring_archive
from v04_a_specification_version_gate import _identity


def _folder(path):
    parts = PurePosixPath(path).parts
    if len(parts) < 3 or parts[0] != "authoring" or parts[1] in {"", ".", ".."}:
        raise ValueError(f"unsupported authoring namespace: {path}")
    return parts[1]


def inspect_edges(documents):
    """Inspect every declared Rule choice in its Benchmark's own namespace.

    No source mutation; manual alternatives are referenced but not presumed
    to have an automated Assessment specification. Shared documents can be
    referenced by any Benchmark. Reject cross-Benchmark local references.
    """
    benchmarks, assessments, rules = {}, {}, []
    for path, doc in sorted(documents.items()):
        folder = _folder(path)
        if not isinstance(doc, dict) or len(doc) != 1:
            raise ValueError(f"{path}: not a single-root document")
        kind, payload = next(iter(doc.items()))
        if not isinstance(payload, dict):
            raise ValueError(f"{path}: invalid {kind} value")
        if kind == "benchmark":
            if folder == "shared":
                raise ValueError(f"{path}: shared Benchmark is unsupported")
            if folder in benchmarks:
                raise ValueError(f"{path}: duplicate Benchmark for folder {folder}")
            declared = payload.get("assessment_specifications")
            if not isinstance(declared, list) or not declared:
                raise ValueError(f"{path}: missing declared Assessment specifications")
            specs = [_identity(x, path) for x in declared]
            if len(set(specs)) != len(specs):
                raise ValueError(f"{path}: duplicate declared Assessment specification")
            ident = payload.get("id")
            if not isinstance(ident, str) or not ident:
                raise ValueError(f"{path}: missing Benchmark id")
            benchmarks[folder] = {"id": ident, "path": path, "specifications": set(specs)}
        elif kind == "assessment":
            ident = payload.get("id")
            if not isinstance(ident, str) or not ident:
                raise ValueError(f"{path}: missing Assessment id")
            if ident in assessments:
                raise ValueError(f"{path}: duplicate Assessment id {ident}")
            mode = payload.get("mode")
            if mode not in {"manual", "automated"}:
                raise ValueError(f"{path}: unknown Assessment mode {mode!r}")
            specification = None
            if mode == "automated":
                specification = _identity(payload.get("specification"), path)
            assessments[ident] = {"path": path, "folder": folder, "mode": mode,
                                  "specification": specification}
        elif kind == "rule":
            if folder == "shared":
                raise ValueError(f"{path}: shared Rule is unsupported")
            if not isinstance(payload.get("id"), str) or not payload.get("id"):
                raise ValueError(f"{path}: missing Rule id")
            rules.append((path, folder, payload))
        elif kind != "applicability":
            raise ValueError(f"{path}: unrecognized native document type {kind!r}")

    if not benchmarks or not rules:
        raise ValueError("missing Benchmark or Rule documents")
    totals = Counter()
    by_benchmark = defaultdict(Counter)
    incompatible = []
    for path, folder, rule in rules:
        benchmark = benchmarks.get(folder)
        if benchmark is None:
            raise ValueError(f"{path}: no Benchmark in its own authoring namespace")
        choices = rule.get("assessment_choices")
        if not isinstance(choices, dict) or not choices:
            raise ValueError(f"{path}: no Assessment choices")
        if rule.get("default_assessment_choice") not in choices:
            raise ValueError(f"{path}: undeclared default Assessment choice")
        totals["rules"] += 1
        by_benchmark[folder]["rules"] += 1
        for label, choice in sorted(choices.items()):
            if not isinstance(choice, dict) or not isinstance(choice.get("assessment"), str):
                raise ValueError(f"{path}: invalid Assessment choice {label!r}")
            ident = choice["assessment"]
            assessment = assessments.get(ident)
            if assessment is None:
                raise ValueError(f"{path}: unresolved Assessment choice {label!r}: {ident}")
            if assessment["folder"] not in ("shared", folder):
                raise ValueError(f"{path}: cross-Benchmark private Assessment reference {ident} "
                                 f"from {assessment['folder']}")
            totals["choice_links"] += 1
            by_benchmark[folder]["choice_links"] += 1
            mode = assessment["mode"]
            totals[mode + "_choice_links"] += 1
            by_benchmark[folder][mode + "_choice_links"] += 1
            if label == rule["default_assessment_choice"]:
                totals[mode + "_default_choices"] += 1
                by_benchmark[folder][mode + "_default_choices"] += 1
            if mode == "automated" and assessment["specification"] not in benchmark["specifications"]:
                totals["incompatible_automated_choice_links"] += 1
                by_benchmark[folder]["incompatible_automated_choice_links"] += 1
                incompatible.append({
                    "benchmark": benchmark["id"], "rule": rule["id"],
                    "choice": label, "assessment": ident,
                    "assessment_specification": {
                        "id": assessment["specification"][0],
                        "version": assessment["specification"][1],
                    },
                })

    rows = []
    for folder, bench in sorted(benchmarks.items()):
        rows.append({
            "folder": folder, "benchmark_id": bench["id"],
            "declared_assessment_specifications": [
                {"id": sid, "version": version} for sid, version in sorted(bench["specifications"])
            ],
            "counts": dict(sorted(by_benchmark[folder].items())),
        })
    status = ("BLOCKED_PER_BENCHMARK_SPECIFICATION" if incompatible
              else "EDGE_DECLARATIONS_CONSISTENT_NOT_COMPILED")
    return {
        "status": status,
        "stage": "per_benchmark_rule_choice_specifications_not_compiled",
        "benchmarks": rows,
        "counts": dict(sorted(totals.items())),
        "incompatible_edge_samples": incompatible[:20],
        "incompatible_edge_count": len(incompatible),
        "allowed_to_compile": False,
        "notes": [
            "every Rule is bound to a Benchmark by its authoring/ namespace",
            "shared Assessments are allowed, cross-Benchmark private Assessments are rejected",
            "manual choices are accounted for but not assigned an automated specification",
            "this validates declaration edges only; no schema migration, capability execution or bundle output",
        ],
    }


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--json-archive", required=True)
    p.add_argument("--yaml-archive")
    p.add_argument("--report-json")
    p.add_argument("--expect-blocked", action="store_true",
                   help="research regression only: assert native compilation would be blocked")
    args = p.parse_args(argv)
    result = inspect_edges(read_authoring_archive(args.json_archive, "json"))
    if args.yaml_archive:
        from_yaml = inspect_edges(read_authoring_archive(args.yaml_archive, "yaml"))
        if from_yaml != result:
            raise ValueError("independent YAML and JSON Benchmark edge results differ")
        result["yaml_json_agree"] = True
    report = json.dumps(result, indent=2, sort_keys=True) + "\n"
    print(report, end="")
    if args.report_json:
        from pathlib import Path
        Path(args.report_json).write_text(report, encoding="utf-8")
    blocked = result["status"].startswith("BLOCKED")
    return (0 if blocked else 2) if args.expect_blocked else (2 if blocked else 0)


if __name__ == "__main__":
    raise SystemExit(main())
