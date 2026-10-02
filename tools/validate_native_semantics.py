#!/usr/bin/env python3
"""Validate cross-reference and capability semantics in native SCAP-NG Assessments.

JSON Schema validates local document shape. This pass validates graph semantics
that require resolving Object/State/Test/Variable references within an authored
Assessment and capability-specific cross-field rules.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

from validate_generated_capability_semantics import (
    validate_assessment_capability_semantics,
)


def load_yaml(path: Path):
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected mapping")
    return value


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("corpus_root", type=Path)
    ap.add_argument("--report", type=Path)
    args = ap.parse_args()

    results = []
    files = sorted(args.corpus_root.rglob("*.assessment.yaml"))
    for path in files:
        doc = load_yaml(path)
        # Manual assessments have no Object/State/Test graph. They still count
        # in the census but semantic graph validation is not applicable.
        assessment = doc.get("assessment", doc)
        graph_applicable = any(
            key in assessment for key in ("objects", "states", "tests", "variables")
        )
        diagnostics = (
            validate_assessment_capability_semantics(doc)
            if graph_applicable
            else []
        )
        results.append({
            "path": path.relative_to(args.corpus_root).as_posix(),
            "graph_applicable": graph_applicable,
            "valid": not diagnostics,
            "diagnostics": diagnostics,
        })

    summary = {
        "assessment_documents_checked": len(results),
        "graph_assessments_checked": sum(x["graph_applicable"] for x in results),
        "non_graph_assessments": sum(not x["graph_applicable"] for x in results),
        "valid": sum(x["valid"] for x in results),
        "invalid": sum(not x["valid"] for x in results),
        "results": results,
    }
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(json.dumps({k: v for k, v in summary.items() if k != "results"}, indent=2))
    return 1 if summary["invalid"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
