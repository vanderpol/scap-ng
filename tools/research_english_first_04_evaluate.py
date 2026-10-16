#!/usr/bin/env python3
"""One-grammar English-first named-Test composition research: exact inversion.

READABILITY/CANONICAL GRAPH PROOF ONLY. Nothing here claims that an OVAL
OR(AND(G,P),AND(NOT G,Q)) graph can be rewritten as procedural if/else.
"""
from copy import deepcopy
from pathlib import Path
import argparse
import json

import yaml

FIXTURES = {
    "rhel9_sv257889_user_file_graph":
        "focused-fixtures/source-backed/authoring/shared/assessments/linux/other/initialization-files-0740-less-permissive.assessment.yaml",
    "win11_sv253495_role_userright_graph":
        "focused-fixtures/source-backed/authoring/ms_windows_11/assessments/automated/SV-253495.automated.yaml",
    "windows_dns_sv259345_alternatives":
        "focused-fixtures/source-backed/authoring/ms_windows_server_dns/assessments/automated/SV-259345.automated.yaml",
    "apache_sv214228_config_checks":
        "focused-fixtures/source-backed/authoring/apache_server_2-4_unix_server/assessments/automated/SV-214228.automated.yaml",
}
TO_ENGLISH = {
    "all": "all_of", "any": "any_of", "one": "exactly_one_of",
    "odd": "odd_number_of", "not": "not",
}
TO_SOURCE = {value: key for key, value in TO_ENGLISH.items()}


def transform(node, mapping):
    if not isinstance(node, dict) or len(node) != 1:
        raise ValueError("evaluate node must have exactly one operation")
    ((key, value),) = node.items()
    if key == "test":
        if not isinstance(value, str) or not value:
            raise ValueError("named Test reference must be nonempty")
        return {"test": value}
    if key not in mapping:
        raise ValueError("unproven evaluate operator " + repr(key))
    if key == "not":
        return {mapping[key]: transform(value, mapping)}
    if not isinstance(value, list) or not value:
        raise ValueError("logical aggregator requires nonempty children")
    return {mapping[key]: [transform(sub, mapping) for sub in value]}


def stats(node):
    if "test" in node:
        return 0, 1
    key, value = next(iter(node.items()))
    children = [value] if key == "not" else value
    parts = [stats(v) for v in children]
    return 1 + sum(p[0] for p in parts), sum(p[1] for p in parts)


def reject_naive_wmi_alternative_merge():
    """OVAL-permitted repeated records make State-OR != per-record membership.

    Source Win11 SV-253495 has two independent WMI record States, each with
    domainrole field require one_or_more/all and record require one_or_more/all,
    with states_match any. OVAL wmi57_item.result is 0..unbounded.
    """
    from oval_result_truth_tables import TRUE, FALSE, aggregate_check
    checks = 0
    def original(values):
        state_1 = aggregate_check("all", [TRUE if v == "1" else FALSE for v in values])
        state_3 = aggregate_check("all", [TRUE if v == "3" else FALSE for v in values])
        return aggregate_check("at least one", [state_1, state_3])
    def tempting_but_wrong(values):
        return aggregate_check("all",
                               [TRUE if v in {"1", "3"} else FALSE for v in values])
    for values in (["1"], ["3"], ["0"], ["1", "1"], ["3", "3"], ["0", "1"]):
        if original(values) != tempting_but_wrong(values):
            raise AssertionError("Unexpected divergence in control input " + repr(values))
        checks += 1
    mixed = ["1", "3"]
    if original(mixed) != FALSE or tempting_but_wrong(mixed) != TRUE:
        raise AssertionError("WMI mixed-record counterexample disappeared")
    return {"control_populations": checks,
            "source": "Win11 SV-253495 WMI domainrole State alternatives",
            "typed_field": "windows.wmi57_item.result: 0..unbounded records",
            "counterexample_record_values": mixed,
            "source_state_alternatives": "false",
            "incorrect_per_record_one_of": "true",
            "conclusion": "Never lower alternative whole-States to membership on each record"}


def run(root):
    results = []
    for ident, path in FIXTURES.items():
        with (Path(root) / path).open(encoding="utf-8") as f:
            source = yaml.safe_load(f)["assessment"]
        graph = source["evaluate"]
        named = set(source["tests"])
        readable = transform(graph, TO_ENGLISH)
        reconstructed = transform(readable, TO_SOURCE)
        if reconstructed != graph:
            raise AssertionError("source evaluate graph changed: " + ident)
        def leaves(n):
            if "test" in n: return {n["test"]}
            key, value = next(iter(n.items()))
            values = [value] if key == "not" else value
            return set().union(*(leaves(v) for v in values))
        unresolved = leaves(graph) - named
        if unresolved:
            raise AssertionError("Test graph has unresolved references " + repr(unresolved))
        groups, references = stats(graph)
        results.append({"id": ident, "source": path, "logical_groups": groups,
                        "test_occurrences": references, "result": "exact evaluate graph inversion",
                        "readable_expression": readable})
    rejects = 0
    for graph in ({"if": {}}, {"and": []}, {"any": []},
                  {"any": [{"test": "A"}], "all": [{"test": "B"}]},
                  {"test": ""}, {"not": {"if": {}}}):
        try:
            transform(graph, TO_ENGLISH)
        except ValueError:
            rejects += 1
        else:
            raise AssertionError("unsupported/invalid graph was accepted " + repr(graph))
    return {"cases": results, "total_graphs": len(results),
            "wmi_alternative_merge_counterexample": reject_naive_wmi_alternative_merge(),
            "negative_inputs_rejected": rejects,
            "proof": "exact named-Test composition only, not scanner parity or rewritten conditional semantics"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixture-root", required=True)
    ap.add_argument("--report", default=None)
    a = ap.parse_args()
    report = run(a.fixture_root)
    output = json.dumps(report, indent=2, sort_keys=True) + "\n"
    print(json.dumps({"total_graphs": report["total_graphs"],
                      "negative_inputs_rejected": report["negative_inputs_rejected"],
                      "cases": [{k: x[k] for k in ("id", "logical_groups", "test_occurrences")}
                                for x in report["cases"]]}, indent=2))
    if a.report: Path(a.report).write_text(output, encoding="utf-8")


if __name__ == "__main__":
    main()
