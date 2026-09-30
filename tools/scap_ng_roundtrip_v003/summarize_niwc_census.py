#!/usr/bin/env python3
"""Aggregate the pinned NIWC Current OVAL per-package round-trip reports.

The semantic_equal counter describes the repository's XML semantic comparator,
not independent execution-equivalence proof on assessed hosts.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def summarize(folder: Path, expected_sources: list[str]) -> dict:
    paths = sorted(folder.rglob("*-summary.json"))
    rows = [json.loads(path.read_text(encoding="utf-8")) for path in paths]
    by_source = {}
    duplicates = []
    for row in rows:
        name = row.get("source")
        if name in by_source:
            duplicates.append(name)
        by_source[name] = row
    expected = set(expected_sources)
    actual = set(by_source)
    totals = Counter()
    extensions = set()
    for row in by_source.values():
        for field in ("definitions", "semantic_equal", "deprecated_blockers",
                      "publisher_extension_blockers", "unexpected_failures"):
            totals[field] += int(row.get(field, 0))
        extensions.update(row.get("publisher_extension_elements") or [])
    total = totals["definitions"]
    return {
        "comparison_scope": "ID-independent OVAL XML semantic comparator; not differential evaluator execution",
        "expected_packages": len(expected_sources),
        "reported_packages": len(paths),
        "unique_reported_packages": len(actual),
        "missing_sources": sorted(expected - actual),
        "unexpected_sources": sorted(actual - expected),
        "duplicate_sources": sorted(duplicates),
        "totals": dict(sorted(totals.items())),
        "semantic_equal_percent_of_all_definitions": (
            round(100 * totals["semantic_equal"] / total, 4) if total else None
        ),
        "publisher_extension_elements": sorted(extensions),
        "per_package": sorted(rows, key=lambda x: str(x.get("source"))),
    }


def render_markdown(report: dict) -> str:
    totals = report["totals"]
    lines = [
        "# NIWC Current OVAL SCAP 1.4 → SCAP-NG → OVAL census",
        "",
        "All results use the pinned NIWC corpus and the workflow commit.",
        "**Caution:** semantic_equal means equivalence under the repository's",
        "ID-independent OVAL comparator; it is not a live-host evaluator test.",
        "",
        f"- Expected packages: {report['expected_packages']}",
        f"- Packages reported: {report['unique_reported_packages']}",
        f"- Definitions: {totals.get('definitions', 0)}",
        f"- Comparator-equivalent definitions: {totals.get('semantic_equal', 0)}",
        f"- Comparator-equivalent percentage: {report['semantic_equal_percent_of_all_definitions']}",
        f"- Deprecated-test blockers: {totals.get('deprecated_blockers', 0)}",
        f"- Publisher-extension blockers: {totals.get('publisher_extension_blockers', 0)}",
        f"- Unexpected failures: {totals.get('unexpected_failures', 0)}",
        f"- Missing packages: {len(report['missing_sources'])}",
        f"- Duplicate reports: {len(report['duplicate_sources'])}",
        "",
        "| Package | Definitions | Comparator equivalent | Deprecated | Extensions | Unexpected |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in report["per_package"]:
        lines.append(
            "| `{}` | {} | {} | {} | {} | {} |".format(
                str(row.get("source", "")).replace("|", "/"),
                row.get("definitions", 0), row.get("semantic_equal", 0),
                row.get("deprecated_blockers", 0),
                row.get("publisher_extension_blockers", 0),
                row.get("unexpected_failures", 0),
            )
        )
    for key in ("missing_sources", "duplicate_sources", "unexpected_sources"):
        if report[key]:
            lines.extend(["", f"## {key}", ""])
            lines.extend(f"- `{value}`" for value in report[key])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--expected-matrix", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    expected_rows = json.loads(args.expected_matrix.read_text(encoding="utf-8"))
    expected_sources = [row["source"] for row in expected_rows]
    report = summarize(args.directory, expected_sources)
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "summary.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (args.output / "README.md").write_text(render_markdown(report), encoding="utf-8")
    print(render_markdown(report))
    if (report["missing_sources"] or report["duplicate_sources"]
            or report["unexpected_sources"] or report["totals"].get("unexpected_failures", 0)):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
