#!/usr/bin/env python3
"""Audit canonical 0.4.0 six-state expression compilation on pinned authoring.

Only six-state composition of caller-supplied Test/Assessment results is
implemented. A successful report is NOT native collector/Test evaluation,
IF/ELSE execution, scanner parity, or a signed executable .scapng bundle.
Refs #232 #229.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path

from v04_a_authoring_graph_index import read_authoring_archive, canonical_json
from v04_a_truth_plan import UnsupportedExpression
from v04_canonical_result_plan import census_authoring, compile_canonical_result_plan, STAGE


def audit(path):
    docs = read_authoring_archive(path, "json")
    report = census_authoring(docs)
    report["total_canonical_documents"] = len(docs)
    report["json_authoring_archive"] = path.name
    report["coverage_interpretation"] = (
        "Boolean and owner-approved ordered branches with externally supplied six-state leaves. "
        "No primitive collector execution or scanner conformance is established."
    )
    return report


def export_plans(documents, *, source_archive_sha256):
    """Materialize deterministic 0.4 result instructions with AST provenance.

    No executable Test source or host collection primitives are generated.
    """
    entries, uncompiled = [], []
    for path, doc in sorted(documents.items()):
        a = doc.get("assessment")
        if not isinstance(a, dict) or a.get("mode") != "automated":
            continue
        try:
            plan = compile_canonical_result_plan(a)
        except UnsupportedExpression as error:
            uncompiled.append({"path": path, "reason": str(error)})
            continue
        entries.append({
            "path": path,
            "assessment_id": a["id"],
            "result_source_sha256": plan["source_sha256"],
            "plan": plan,
        })
    return {
        "format": "scap-ng-0.4.0-supplied-result-plan-source-map/0.1",
        "stage": STAGE,
        "source_archive_sha256": source_archive_sha256,
        "compiled_plan_count": len(entries),
        "compiled_instruction_count": sum(e["plan"]["instruction_count"] for e in entries),
        "compiled_plan_sha256": sha256(canonical_json(entries)).hexdigest(),
        "entries": entries,
        "uncompiled": uncompiled,
        "scanner_executed": False,
        "test_collectors_compiled": False,
        "native_executable_bundle": False,
    }


def verify_export(documents, manifest):
    """Reject altered instructions, missing Assessments and untracked source."""
    reference = export_plans(
        documents, source_archive_sha256=manifest.get("source_archive_sha256"))
    if canonical_json(reference) != canonical_json(manifest):
        raise ValueError("compiled result-plan manifest differs from canonical source")
    return True


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--json-archive", required=True, type=Path)
    cli.add_argument("--report", required=True, type=Path)
    cli.add_argument("--assert-six-stigs", action="store_true")
    cli.add_argument("--plans", type=Path, help="write source-pinned result instructions (NOT executable)")
    args = cli.parse_args()
    report = audit(args.json_archive)
    totals = report["counts"]
    if args.assert_six_stigs:
        if report["total_canonical_documents"] != 4012:
            raise ValueError("unexpected original canonical authoring population")
        if totals.get("automated_assessments") != 883:
            raise ValueError("unexpected automated Assessment population")
        if (totals.get("compiled_supplied_result_plans", 0) +
                totals.get("unsupported_result_expressions", 0)
                != totals["automated_assessments"]):
            raise ValueError("unaccounted 0.4.0 authored result expression")
    if args.plans is not None:
        docs = read_authoring_archive(args.json_archive, "json")
        manifest = export_plans(
            docs, source_archive_sha256=sha256(args.json_archive.read_bytes()).hexdigest())
        verify_export(docs, manifest)
        if (manifest["compiled_plan_count"] != totals.get("compiled_supplied_result_plans", 0)
                or manifest["compiled_instruction_count"] != totals.get("compiled_result_instructions", 0)):
            raise ValueError("result-plan output does not match complete census")
        args.plans.parent.mkdir(parents=True, exist_ok=True)
        args.plans.write_bytes(canonical_json(manifest) + b"\n")
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n")
    print(json.dumps({"counts": totals,
                     "total_documents": report["total_canonical_documents"],
                     "source_not_executable": True}, sort_keys=True))


if __name__ == "__main__":
    main()
