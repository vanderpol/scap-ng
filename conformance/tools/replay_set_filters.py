#!/usr/bin/env python3
"""Replay canonical Set/Filter expressions through current RI memory and streaming paths."""
from __future__ import annotations

import argparse
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import subprocess

from qualify_merge_fixture import require_equal
from runner import CONFORMANCE, load, validator

FIXTURE = CONFORMANCE / "set-replay"
ASSESSMENT = CONFORMANCE / "cases/core/set-filters.assessment.yaml"
SOURCE_ITEMS = CONFORMANCE / "fixtures/core-set-filters.json"
EXPECTED = CONFORMANCE / "expected/core-set-filters.json"


def authored_cases(assessment, evidence):
    populations = {}
    for source, rows in evidence["populations"].items():
        ref = f"{source}-object"
        cap = assessment["shared_objects"][ref]["capability"]
        items = []
        for entry in rows:
            require_equal(entry["status"], "collected", entry["id"])
            fields = {key: [{"datatype": "string", "status": "exists", "value": entry[key]}]
                      for key in ("name", "arch")}
            items.append({"id": entry["id"], "capability": cap, "status": "exists",
                          "fields": fields, "provenance": {"scope": "supplied canonical fixture"}})
        populations[ref] = {"complete": True, "items": items}
    return {name: {"expression": test["object"]["set"], "populations": populations}
            for name, test in assessment["tests"].items()}


def control_case(difference, name):
    case = deepcopy(difference)
    populations = case["populations"]
    if name == "incomplete-right":
        populations["right-object"]["complete"] = False
    elif name == "duplicate-within":
        rows = populations["left-object"]["items"]
        rows.append(deepcopy(rows[0]))
    elif name == "field-error":
        populations["left-object"]["items"][0]["fields"]["arch"] = [{"datatype": "string", "status": "error"}]
    elif name == "cancelled":
        case["cancelled"] = True
    else:
        raise ValueError(f"Unknown Set replay control {name!r}")
    return case


def replay(ri, go):
    document = load(ASSESSMENT)
    validator().validate(document)
    controls = load(FIXTURE / "controls.json")
    expected = load(EXPECTED)["operations"]
    cases = authored_cases(document["assessment"], load(SOURCE_ITEMS))
    desired = {name: {"ids": expected[name.removeprefix("set-").removesuffix("-test")]["values"], "complete": True}
               for name in cases}
    for name, details in controls["controls"].items():
        cases[name] = control_case(cases["set-difference-test"], name)
        desired[name] = {"ids": details.get("observed_partial_ids", []), "complete": details["complete"]}
        if "diagnostic" in details:
            desired[name]["diagnostic"] = details["diagnostic"]
    run = subprocess.run([go, "run", str(FIXTURE / "ri-set.go")], cwd=ri,
                         input=json.dumps(cases), capture_output=True, text=True, timeout=120)
    if run.returncode != 0:
        raise ValueError(f"RI Set replay failed: {run.stderr}")
    observed = json.loads(run.stdout)
    require_equal(set(observed), set(desired), "RI Set replay cases")
    for name, output in observed.items():
        require_equal(output, {"memory": desired[name], "stream": desired[name]}, name)

    return {
        "format": "scap-ng-set-compiled-filter-ri-receipt-1",
        "schema_pin": controls["schema_pin"],
        "ri_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ri, text=True).strip(),
        "sha256": {path.relative_to(CONFORMANCE).as_posix(): sha256(path.read_bytes()).hexdigest()
                   for path in (ASSESSMENT, SOURCE_ITEMS, EXPECTED)},
        "scope": "RI filter compilation plus in-memory and streaming Set membership over supplied Items.",
        "observed": observed,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ri", type=Path, required=True)
    parser.add_argument("--go", default="go")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    output = json.dumps(replay(args.ri, args.go), indent=2, sort_keys=True) + "\n"
    if args.check and (FIXTURE / "ri-receipt.json").read_text(encoding="utf-8") != output:
        raise SystemExit("RI Set receipt differs from the replay")
    print(output, end="")
