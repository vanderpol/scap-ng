#!/usr/bin/env python3
"""Audit canonical 0.4.0 six-state expression compilation on pinned authoring.

Only six-state composition of caller-supplied Test/Assessment results is
implemented. A successful report is NOT native collector/Test evaluation,
IF/ELSE execution, scanner parity, or a signed executable .scapng bundle.
Refs #232 #229.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
import sys

from v04_a_authoring_graph_index import read_authoring_archive
from v04_canonical_result_plan import census_authoring


def audit(path):
    docs = read_authoring_archive(path, "json")
    report = census_authoring(docs)
    report["total_canonical_documents"] = len(docs)
    report["json_authoring_archive"] = path.name
    report["coverage_interpretation"] = (
        "Only Boolean result composition with externally supplied six-state leaves. "
        "Unsupported IF/ELSE and missing primitive collector semantics remain open."
    )
    return report


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--json-archive", required=True, type=Path)
    cli.add_argument("--report", required=True, type=Path)
    cli.add_argument("--assert-six-stigs", action="store_true")
    args = cli.parse_args()
    report = audit(args.json_archive)
    totals = report["counts"]
    if args.assert_six_stigs:
        if report["total_canonical_documents"] != 4001:
            raise ValueError("unexpected original canonical authoring population")
        if totals.get("automated_assessments") != 872:
            raise ValueError("unexpected automated Assessment population")
        if (totals.get("compiled_supplied_result_plans", 0) +
                totals.get("unsupported_result_expressions", 0)
                != totals["automated_assessments"]):
            raise ValueError("unaccounted 0.4.0 authored result expression")
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n")
    print(json.dumps({"counts": totals,
                     "total_documents": report["total_canonical_documents"],
                     "source_not_executable": True}, sort_keys=True))


if __name__ == "__main__":
    main()
