#!/usr/bin/env python3
"""#238/#232: read-only Linux mount Test -> generic 0.4-A truth-plan bridge.

One *pinned* 0.4-A /home nosuid Assessment only. Reuses the deliberately
restricted Linux mountinfo pilot to observe/verify an Item/Test result, then
feeds that result to the separately implemented six-state expression plan.
NOT a general scanner, OVAL linux.partition parity or signed .scapng.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path

from prototype_a_linux_mount_scan import compile_assessment, evaluate
from research_provider_linux_mounts import (
    collect_current_linux_mounts, parse_mountinfo_text,
)
from v04_a_authoring_graph_index import canonical_json
from v04_a_truth_plan import compile_expression, execute_supplied_results

STAGE = "RESEARCH_PINNED_LINUX_TEST_TO_EXPRESSION_BRIDGE_NOT_SCANNER"


def bridge(document, observation, *, fixture_mode=False):
    """Wire one proven pilot Test to its authored direct-Test evaluation root."""
    compiled = compile_assessment(document)  # Strictly pinned, no defaults.
    assessment = document["assessment"]
    plan = compile_expression(assessment)
    if (plan["requires"]["tests"] != [compiled["test_id"]]
            or plan["requires"]["dependencies"]
            or plan["expression_field"] != "evaluate"):
        raise ValueError("unimplemented Linux Test/Assessment expression binding")
    if plan["instructions"] != [
            {"op": "read_test", "id": compiled["test_id"], "path": ["evaluate"]}]:
        raise ValueError("only the source-pinned direct-Test binding is implemented")
    test = evaluate(compiled, observation, fixture_mode=fixture_mode)
    if (test["assessment_id"] != plan["assessment_id"]
            or test["test_id"] != compiled["test_id"]):
        raise ValueError("Test identity/provenance mismatch")
    evaluated = execute_supplied_results(plan, {compiled["test_id"]: test["result"]})
    if evaluated["outcome"] != test["result"]:
        raise ValueError("unexpected source Test to expression result mismatch")
    return {
        "stage": STAGE,
        "assessment_id": compiled["assessment_id"],
        "assessment_version": compiled["version"],
        "source_assessment_sha256": sha256(canonical_json(document)).hexdigest(),
        "expression_sha256": plan["expression_sha256"],
        "test_id": compiled["test_id"],
        "test_result": test,
        "assessment_expression": evaluated,
        "result": evaluated["outcome"],
        "fixture_mode": bool(fixture_mode),
        "scanner_executed": False,
        "not_proven": [
            "OVAL linux.partition effective mount option equivalence",
            "full 0.4 Test/State/Variable or Set/Filter evaluator",
            "Benchmark/Rule aggregation, tailoring or signed .scapng bundle",
            "multiple-Test or conditional assessment execution",
        ],
    }


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--assessment", required=True, type=Path)
    modes = p.add_mutually_exclusive_group(required=True)
    modes.add_argument("--fixture-mountinfo", type=Path)
    modes.add_argument("--live", action="store_true",
                       help="read current Linux mountinfo namespace, not an external host")
    args = p.parse_args(argv)
    doc = json.loads(args.assessment.read_text(encoding="utf-8"))
    if args.live:
        observed = collect_current_linux_mounts()
    else:
        observed = parse_mountinfo_text(
            args.fixture_mountinfo.read_text(encoding="utf-8"), "mnt:[fixture]")
    report = bridge(doc, observed, fixture_mode=not args.live)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["result"] in ("true", "false") else 3


if __name__ == "__main__":
    raise SystemExit(main())
