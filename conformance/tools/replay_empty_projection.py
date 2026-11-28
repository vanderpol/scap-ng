#!/usr/bin/env python3
"""Compare authoritative empty, absent and invalid file projections in two RI revisions."""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess

from qualify_merge_fixture import require_equal
from replay_variable_functions import bind_collected_items, projection_variant, run
from runner import CONFORMANCE, load, validator

FIXTURE = CONFORMANCE / "empty-projection"
COUNT = "count-empty-test"
EXISTS = "projection-has-values-test"


def replay(current_ri, prior_ri, go):
    expected = load(FIXTURE / "expected.json")
    source = FIXTURE / expected["artifact"]
    fixture = CONFORMANCE / expected["source_evidence"]
    document = load(source)
    validator().validate(document)
    observed_source = load(fixture)
    assessment = document["assessment"]
    source_items, field = bind_collected_items(assessment, observed_source, "observed-values-variable")

    cases = []
    current_expected = {}
    prior_expected = {}
    for name, oracle in expected["cases"].items():
        evidence = source_items if name == "complete" else projection_variant(source_items, field, name)
        if "known_values" in oracle:
            collection, = evidence.values()
            values = [row["fields"][field][0]["value"] for row in collection["Items"]]
            require_equal(values, oracle["known_values"], name)
            require_equal(len(values), oracle["independent_count"], name)
        for test in assessment["tests"]:
            key = f"{name}/{test}"
            cases.append({"name": key, "test": test, "evidence": evidence})
            if "diagnostic" in oracle:
                observation = {"diagnostic": oracle["diagnostic"]}
            else:
                observation = oracle["count_outcome" if test == COUNT else "existence_outcome"]
            current_expected[key] = observation
            prior_expected[key] = {"diagnostic": oracle["prior_diagnostic"]} if "prior_diagnostic" in oracle else observation

    observed = {}
    for scope, ri, oracle in (("prior", prior_ri, prior_expected), ("current", current_ri, current_expected)):
        results = run(ri, go, document, {}, expected["assessment_closure_sha256"], cases)
        require_equal(results, oracle, f"{scope} projection observations")
        observed[scope] = {
            "ri_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ri, text=True).strip(),
            "cases": results,
        }
    return {
        "format": "scap-ng-collected-empty-projection-ri-receipt-1",
        "schema_pin": expected["schema_pin"],
        "sha256": {path.relative_to(CONFORMANCE).as_posix(): sha256(path.read_bytes()).hexdigest()
                   for path in (source, fixture)},
        "observed": observed,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--current-ri", type=Path, required=True)
    parser.add_argument("--prior-ri", type=Path, required=True)
    parser.add_argument("--go", default="go")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    output = json.dumps(replay(args.current_ri, args.prior_ri, args.go), indent=2, sort_keys=True) + "\n"
    if args.check and (FIXTURE / "ri-receipt.json").read_text(encoding="utf-8") != output:
        raise SystemExit("RI collected empty projection receipt differs from the replay")
    print(output, end="")
