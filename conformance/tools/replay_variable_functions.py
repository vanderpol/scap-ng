#!/usr/bin/env python3
"""Replay the canonical Variable function suite and projection controls through RI."""
from __future__ import annotations

import argparse
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import subprocess

import yaml

from qualify_merge_fixture import require_equal
from runner import CONFORMANCE, ROOT, load, validator

ASSESSMENT = "cases/core/variable-functions.assessment.yaml"
EVIDENCE = "fixtures/core-variable-functions.json"
EXPECTED = "expected/core-variable-functions.json"
INTERACTION_ASSESSMENT = "cases/core/variable-interactions.assessment.yaml"
INTERACTION_EXPECTED = "expected/core-variable-interactions.json"
REPLAY = CONFORMANCE / "variable-function-replay"
PROJECTION = "function-values-test"
ORDERED_PROJECTION = "function-values-ordered-test"


def bind_collected_items(assessment, fixture, variable="collected-values-variable"):
    planned = assessment["variables"][variable]["expression"]["values"]
    object_ref = planned["object"]["object_ref"]
    field = planned["field"]
    capability = assessment["shared_objects"][object_ref]["capability"]
    items = []
    for row in fixture["populations"][object_ref]:
        require_equal(row["status"], "collected", row["id"])
        items.append({
            "id": row["id"], "capability": capability, "status": "exists",
            "provenance": {"source": "canonical variable-functions fixture"},
            "fields": {field: [{"datatype": "string", "status": "exists", "value": row[field]}]},
        })
    evidence = {object_ref: {
        "Collection": {"id": "projection-source-collection", "capability": capability,
                       "status": "complete", "logical_complete": True, "population_complete": True},
        "Items": items,
    }}
    return evidence, field


def projection_variant(baseline, field, name):
    if name == "absent":
        return {}
    variant = deepcopy(baseline)
    collection, = variant.values()
    items = collection["Items"]
    if name == "empty":
        items.clear()
    elif name == "incomplete":
        collection["Collection"]["population_complete"] = False
    elif name == "collection-error":
        collection["Collection"]["status"] = "error"
    elif name == "field-error":
        items[0]["fields"][field] = [{"datatype": "string", "status": "error"}]
    elif name == "field-empty":
        items[0]["fields"][field] = []
    elif name == "missing-field":
        del items[0]["fields"][field]
    elif name == "nonmatching":
        items[0]["fields"][field][0]["value"] = "/scap-ng-function-fixture/gamma"
    elif name == "reordered":
        items.reverse()
    elif name == "duplicate":
        duplicate = deepcopy(items[0])
        duplicate["id"] = "extra-" + duplicate["id"]
        items.append(duplicate)
    elif name == "one-item":
        items.pop()
    else:
        raise ValueError(f"Unknown collected projection variant {name!r}")
    return variant


def source_cases(assessment, evidence):
    cases = []
    for test in assessment["tests"]:
        case = {"name": test, "test": test}
        if test in {PROJECTION, ORDERED_PROJECTION}:
            case["evidence"] = evidence
        cases.append(case)
    return cases


def run(ri, go, document, fixture, schema_hash, cases):
    request = {"schema_family_sha256": schema_hash, "assessment_document": document, "bindings": {}}
    payload = {"request": request, "definitions": document["assessment"].get("inputs", {}),
               "inputs": fixture.get("bindings", {}), "cases": cases}
    process = subprocess.run([go, "run", str(REPLAY / "ri-replay.go")], cwd=ri,
                             input=json.dumps(payload), capture_output=True, text=True, timeout=120)
    if process.returncode != 0:
        raise ValueError(f"RI replay failed: {process.stderr}")
    observations = {}
    for case, observed in json.loads(process.stdout).items():
        decision = observed["decision"]
        if diagnostic := observed.get("diagnostic"):
            require_equal(decision["technical_outcome"], "", case)
            observations[case] = {"diagnostic": diagnostic["code"]}
            continue
        counts = decision["cardinality"]
        observations[case] = {"outcome": decision["technical_outcome"],
                              "values_found": counts["values_found"], "values_matching": counts["values_matching"]}
    require_equal(set(observations), {case["name"] for case in cases}, "replay cases")
    return observations


def positive_expectations(expected):
    outcomes = {}
    for function, row in expected["functions"].items():
        outcomes[f'function-{function.replace("_", "-")}-test'] = {
            "outcome": row["outcome"], "values_found": row["values_found"], "values_matching": row["values_found"],
        }
    for test, row in expected["ordered_population_checks"].items():
        outcomes[test] = {"outcome": row["outcome"], "values_found": 1, "values_matching": 1}
    return outcomes


def variant_expectation(oracle, test):
    if "diagnostic" in oracle:
        return {"diagnostic": oracle["diagnostic"]}
    if test == PROJECTION:
        return {"outcome": oracle["membership_outcome"], "values_found": oracle["values_found"],
                "values_matching": oracle["values_matching"]}
    return {"outcome": oracle["ordered_outcome"], "values_found": 1, "values_matching": 0}


def replay(ri, go):
    control = load(REPLAY / "controls.json")
    require_equal(load(CONFORMANCE / "manifest.json")["schema_commit"], control["schema_pin"], "schema pin")
    schema_hash = control["assessment_closure_sha256"]
    document = load(CONFORMANCE / ASSESSMENT)
    validator().validate(document)
    fixture = load(CONFORMANCE / EVIDENCE)
    expected = load(CONFORMANCE / EXPECTED)
    evidence, field = bind_collected_items(document["assessment"], fixture)
    cases = source_cases(document["assessment"], evidence)
    for name in control["projection_variants"]:
        variant = projection_variant(evidence, field, name)
        for test in (PROJECTION, ORDERED_PROJECTION):
            cases.append({"name": f"{name}/{test}", "test": test, "evidence": variant})

    observed = run(ri, go, document, fixture, schema_hash, cases)
    positives = {name: observed.pop(name) for name in document["assessment"]["tests"]}
    require_equal(positives, positive_expectations(expected), "core function positive observations")
    for name, variant in control["projection_variants"].items():
        for test in (PROJECTION, ORDERED_PROJECTION):
            require_equal(observed[f"{name}/{test}"], variant_expectation(variant, test), name)

    baseline_raw = subprocess.check_output(
        ["git", "show", f'{control["prior_commit"]}:conformance/{ASSESSMENT}'], cwd=ROOT
    )
    baseline = yaml.safe_load(baseline_raw)
    baseline_fixture_raw = subprocess.check_output(
        ["git", "show", f'{control["prior_commit"]}:conformance/{EVIDENCE}'], cwd=ROOT
    )
    baseline_fixture = json.loads(baseline_fixture_raw)
    baseline_evidence, _ = bind_collected_items(baseline["assessment"], baseline_fixture)
    previous = run(ri, go, baseline, baseline_fixture, schema_hash,
                   source_cases(baseline["assessment"], baseline_evidence))
    prior_false = sorted(name for name, row in previous.items() if row.get("outcome") == "false")
    require_equal(prior_false, control["prior_false"], "original core function contradictions")
    require_equal(sum(row.get("outcome") == "true" for row in previous.values()) + len(prior_false),
                  len(previous), "original executable Test leaves")
    alias_document = load(CONFORMANCE / INTERACTION_ASSESSMENT)
    validator().validate(alias_document)
    alias_cases = source_cases(alias_document["assessment"], {})
    alias_expectations = load(CONFORMANCE / INTERACTION_EXPECTED)["assertions"]
    alias_now = run(ri, go, alias_document, {}, schema_hash, alias_cases)
    for test, oracle in alias_expectations.items():
        require_equal(alias_now[test], {key: oracle[key] for key in ("outcome", "values_found", "values_matching")},
                      test)
    alias_prior_raw = subprocess.check_output(
        ["git", "show", f'{control["prior_commit"]}:conformance/{INTERACTION_ASSESSMENT}'], cwd=ROOT
    )
    alias_prior = run(ri, go, yaml.safe_load(alias_prior_raw), {}, schema_hash, alias_cases)
    for test, oracle in control["prior_alias"].items():
        require_equal(alias_prior[test], oracle, test)

    return {
        "format": "scap-ng-core-variable-function-ri-receipt-1",
        "schema_pin": control["schema_pin"], "assessment_closure_sha256": schema_hash,
        "ri_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ri, text=True).strip(),
        "sha256": {path: sha256((CONFORMANCE / path).read_bytes()).hexdigest() for path in (ASSESSMENT, EVIDENCE, EXPECTED, INTERACTION_ASSESSMENT, INTERACTION_EXPECTED)},
        "prior_commit": control["prior_commit"], "prior_assessment_sha256": sha256(baseline_raw).hexdigest(),
        "prior_observations": previous, "positive_observations": positives, "projection_controls": observed,
        "alias_interaction": {"baseline_assessment_sha256": sha256(alias_prior_raw).hexdigest(),
                              "baseline": alias_prior, "current": alias_now},
        "scope": "Direct RI Test evaluation against canonical authored Variables and explicitly supplied evidence.",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ri", type=Path, required=True)
    parser.add_argument("--go", default="go")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(replay(args.ri, args.go), indent=2, sort_keys=True) + "\n"
    if args.check and (REPLAY / "ri-receipt.json").read_text(encoding="utf-8") != rendered:
        raise SystemExit("core Variable function receipt differs from the replay")
    print(rendered, end="")
