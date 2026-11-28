#!/usr/bin/env python3
"""Run the shared RI report-side conditional reducer with independent leaf outcomes."""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess

from qualify_merge_fixture import require_equal
from runner import CONFORMANCE, load, schema_validator, validator

FIXTURE = CONFORMANCE / "conditional-replay"
MIXED = FIXTURE / "mixed-guards.assessment.yaml"
ORDERED = CONFORMANCE / "cases/supplemental/conditional-ordered.assessment.yaml"
ORDERED_EXPECTED = CONFORMANCE / "expected/conditional-ordered.json"
ORDERED_INPUTS = CONFORMANCE / "fixtures/conditional-ordered.json"


def select_entries(result):
    outer, = [row for row in result["entries"] if row["Path"] == "/evaluate"]
    nested = [row for row in result["entries"] if row["Operator"] == "if" and row["Path"] != "/evaluate"]
    terminals = [row["Path"] for row in result["entries"] if row["Operator"] in {"not_evaluated", "not_applicable"}]
    branch = outer["SelectedBranch"] or None
    index = outer["BranchIndex"] if outer["HasBranchIndex"] else None
    return outer, branch, index, nested, terminals


def trace_wire(assessment, entries, outcome, leaves):
    """Project the actual helper entries using RI's report-side field mapping."""
    invocation = "conformance-conditional-projection"
    trace = []
    for entry in entries:
        row = {"path": entry["Path"], "kind": "logical", "owner_invocation_ref": invocation,
               "outcome": entry["Outcome"], "reason": "operator:" + entry["Operator"]}
        if entry["Operator"] == "if":
            row.update(kind="conditional", condition_outcome=entry["ConditionOutcome"],
                       selected_branch=entry["SelectedBranch"] or None)
            if entry["HasBranchIndex"]:
                row["branch_index"] = entry["BranchIndex"]
            if entry["InputID"]:
                row["input"] = entry["InputID"]
        trace.append(row)
    return {"assessment": assessment, "invocation_ref": invocation, "outcome": outcome,
            "executed_tests": list(leaves), "trace": trace, "diagnostics": []}


def cases_for_replay(expected):
    mixed = load(MIXED)
    ordered = load(ORDERED)
    for document in (mixed, ordered):
        validator().validate(document)
    cases = {}
    mixed_body = mixed["assessment"]
    known = mixed_body["variables"]["known-value-variable"]["expression"]["literal"]
    bodies = {}
    for name in ("primary-body-test", "input-body-test"):
        operand = mixed_body["tests"][name]["require"]["fields"]["value"]["equals"]
        bodies[name] = str(known == operand).lower()
    for name, row in expected["mixed"].items():
        cases["mixed/" + name] = {
            "expression": mixed_body["evaluate"],
            "leaves": {**bodies, "initial-guard-test": row["first"], "secondary-guard-test": row["second"]},
            "presence": dict.fromkeys(row["supplied_inputs"], True),
        }
    outcomes = load(ORDERED_EXPECTED)["variants"]
    bindings = load(ORDERED_INPUTS)["input_variants"]
    require_equal(set(outcomes), set(expected["ordered"]), "ordered branch scenarios")
    for name, oracle in outcomes.items():
        cases["ordered/" + name] = {
            "expression": ordered["assessment"]["evaluate"],
            "leaves": oracle["test_outcomes"],
            "presence": dict.fromkeys(bindings[name], True),
        }
    return cases, outcomes, {"mixed": mixed_body["id"], "ordered": ordered["assessment"]["id"]}


def replay(ri, go):
    expected = load(FIXTURE / "expected.json")
    cases, outcomes, assessments = cases_for_replay(expected)
    run = subprocess.run([go, "run", str(FIXTURE / "ri-trace.go")], cwd=ri,
                         input=json.dumps(cases), capture_output=True, text=True, timeout=120)
    if run.returncode != 0:
        raise ValueError(f"RI conditional replay failed: {run.stderr}")
    reports = json.loads(run.stdout)
    require_equal(set(reports), set(cases), "RI conditional replay cases")
    schema = schema_validator("expression-invocation.schema.json")
    normalized = {}
    for case, report in reports.items():
        family, name = case.split("/", 1)
        oracle = expected[family][name]
        outcome = report["outcome"]
        outer, selected, index, nested, paths = select_entries(report)
        wanted = oracle.get("outcome") or outcomes[name]["assessment_outcome"]
        require_equal((selected, index), (oracle["selected"], oracle["branch_index"]), case)
        require_equal([row["SelectedBranch"] for row in nested], [oracle["nested"]] if "nested" in oracle else [], case)
        require_equal(paths, [oracle["terminal_path"]] if "terminal_path" in oracle else [], case)
        wire = trace_wire(assessments[family], report["entries"], outcome, cases[case]["leaves"])
        errors = list(schema.iter_errors(wire))
        status = "matched"
        if name in {"initial-not_evaluated", "initial-not_applicable"}:
            require_equal((outcome, outer["ConditionOutcome"]), ("unknown", "unknown"), case)
            status = "status-normalized"
        else:
            require_equal(outcome, wanted, case)
        if name in {"later-error", "later-unknown"}:
            require_equal(outer["ConditionOutcome"], "false", case)
            require_equal([(error.validator, error.message) for error in errors], [("const", "'else' was expected")], case)
            status = "wire-rejected"
        else:
            require_equal(errors, [], case)
        normalized[case] = {
            "expected_outcome": wanted, "observed_outcome": outcome, "status": status,
            "condition_outcome": outer["ConditionOutcome"], "selected": selected, "branch_index": index,
            "nested": [row["SelectedBranch"] for row in nested], "terminal_paths": paths,
            "wire_diagnostics": [error.message for error in errors],
        }
    return {
        "format": "scap-ng-ri-conditional-report-oracle-1",
        "schema_pin": expected["schema_pin"],
        "ri_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ri, text=True).strip(),
        "source_sha256": {source.relative_to(CONFORMANCE).as_posix(): sha256(source.read_bytes()).hexdigest()
                          for source in (MIXED, ORDERED, ORDERED_EXPECTED, ORDERED_INPUTS)},
        "cases": normalized,
        "scope": "Production report-side Evaluate reduction with supplied leaf outcomes and Input presence. No scheduling or collector claim.",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ri", type=Path, required=True)
    parser.add_argument("--go", default="go")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    output = json.dumps(replay(args.ri, args.go), indent=2, sort_keys=True) + "\n"
    if args.check and (FIXTURE / "ri-receipt.json").read_text(encoding="utf-8") != output:
        raise SystemExit("RI conditional receipt differs from the replay")
    print(output, end="")
