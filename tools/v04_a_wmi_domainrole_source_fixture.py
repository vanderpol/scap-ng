#!/usr/bin/env python3
"""#229/#232: source-exact Windows DomainRole WMI record reference fixture.

Reference simulation, not WMI execution. Accept only exact 0.4-A
source-record shapes observed in the six-STIG r3 authoring. Pinned OVAL
5.12.3 result charts handle complete/incomplete/error collection results.
Unsupported source expressions fail closed.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path

from oval_result_truth_tables import aggregate_operator, evaluate_collected_object_test
from v04_a_authoring_graph_index import canonical_json, read_authoring_archive

ANCHORS = {
    "SV-253495.automated": (
        "system-non-dc-domain-joined-windows-server-or-workstation-test",
        "system-standalone-windows-server-or-workstation-test",
    ),
    "SV-278001.automated": ("system-windows-domain-controller-test",),
}
EXPECTED_ROLES = {
    "system-non-dc-domain-joined-windows-server-or-workstation-test": ("1", "3"),
    "system-standalone-windows-server-or-workstation-test": ("0", "2"),
    "system-windows-domain-controller-test": ("4", "5"),
}
STAGE = "SOURCE_EXACT_WMI_DOMAINROLE_OVAL_REFERENCE_FIXTURE_NOT_SCANNER"


def compile_record_role_test(test_id, authored):
    if (not isinstance(authored, dict) or
            authored.get("capability") != "windows.wmi.query" or
            authored.get("states_match") != "any" or
            authored.get("require", authored.get("collected_items_require"))
            != "at_least_one_exists_and_all_match"):
        raise ValueError(f"{test_id}: unsupported WMI Test scope")
    states = authored.get("states")
    if not isinstance(states, list) or len(states) != 2:
        raise ValueError(f"{test_id}: expected exactly two source record States")
    expected = []
    for index, state in enumerate(states):
        try:
            record = state["result"]["record"]
            field = record["fields"]["domainrole"]
        except (TypeError, KeyError) as exc:
            raise ValueError(f"{test_id}: unrecognized record path {index}") from exc
        if (set(state) != {"result"} or set(state["result"]) != {"record"}
                or set(record) != {"fields", "require"} or
                set(record["fields"]) != {"domainrole"} or
                record["require"] != "at_least_one_exists_and_all_match" or
                set(field) != {"equals", "require"} or
                field["require"] != "at_least_one_exists_and_all_match" or
                type(field["equals"]) is not str):
            raise ValueError(f"{test_id}: unreviewed record or field semantics {index}")
        expected.append(field["equals"])
    if tuple(expected) != EXPECTED_ROLES.get(test_id):
        raise ValueError(f"{test_id}: source record values changed unexpectedly")
    return {
        "stage": STAGE, "test_id": test_id, "role_values": expected,
        "test_source_sha256": sha256(canonical_json(authored)).hexdigest(),
        "item_existence": "at_least_one_exists",
        "states_match": "any", "test_check": "all",
    }


def oracle_observed_record_test(compiled, observation):
    """Predict restricted Test outcome from pre-collected simulated Items.

    A missing/non-scalar DomainRole is a record-field error, not an absent
    Test Item. Collection flag remains separate from Item count.
    """
    if compiled.get("stage") != STAGE:
        raise ValueError("untrusted reference fixture")
    if not isinstance(observation, dict) or set(observation) != {"flag", "items"}:
        raise ValueError("expected explicit collected status flag and Items")
    flag, items = observation["flag"], observation["items"]
    if (flag not in ("complete", "incomplete", "error",
                     "not collected", "not applicable", "does not exist")
            or not isinstance(items, list)):
        raise ValueError("unsupported collected population status")
    results = []
    for item in items:
        if not isinstance(item, dict) or set(item) != {"result"}:
            results.append("error")
            continue
        record = item["result"]
        if (not isinstance(record, dict) or
                not isinstance(record.get("domainrole"), str) or
                set(record) != {"domainrole"}):
            results.append("error")
            continue
        field = record["domainrole"]
        state_results = [
            "true" if field == literal else "false"
            for literal in compiled["role_values"]
        ]
        results.append(aggregate_operator("OR", state_results))
    result = evaluate_collected_object_test(
        flag, existence=compiled["item_existence"],
        check=compiled["test_check"], has_state=True, exists=len(items),
        item_results=results,
    ).replace(" ", "_")
    return {
        "stage": STAGE, "test_id": compiled["test_id"],
        "result": result, "collection_flag": flag,
        "count": len(items), "per_item_state_results": results,
        "source_test_sha256": compiled["test_source_sha256"],
        "scanner_executed": False, "windows_wmi_queried": False,
    }


def source_fixtures(documents):
    found = {}
    for path, doc in sorted(documents.items()):
        a = doc.get("assessment")
        if not isinstance(a, dict) or a.get("id") not in ANCHORS:
            continue
        name = a["id"]
        if name in found:
            raise ValueError(f"duplicate source Assessment {name}")
        checks = []
        for test_id in ANCHORS[name]:
            t = (a.get("tests") or {}).get(test_id)
            if not isinstance(t, dict):
                raise ValueError(f"{name}: missing source WMI Test {test_id}")
            checks.append(compile_record_role_test(test_id, t))
        found[name] = {"assessment_id": name, "source_path": path,
                       "source_assessment_sha256": sha256(canonical_json(doc)).hexdigest(),
                       "compiled_restricted_test_fixtures": checks}
    if set(found) != set(ANCHORS):
        raise ValueError(f"missing real WMI source anchors {sorted(set(ANCHORS)-set(found))}")
    return [found[name] for name in sorted(found)]


def reference_scenarios(source_records):
    cases = []
    for assessment in source_records:
        for compiled in assessment["compiled_restricted_test_fixtures"]:
            for role in ("0", "1", "2", "3", "4", "5"):
                sample = {"flag": "complete",
                          "items": [{"result": {"domainrole": role}}]}
                value = oracle_observed_record_test(compiled, sample)
                expected = "true" if role in compiled["role_values"] else "false"
                if value["result"] != expected:
                    raise ValueError(f"source WMI fixture mismatch for {compiled['test_id']} role={role}")
                cases.append({"assessment_id": assessment["assessment_id"],
                              "test_id": compiled["test_id"], "role": role,
                              "expected": expected, "observed": value["result"]})
    return {
        "stage": STAGE,
        "anchored_assessments": len(source_records),
        "anchored_WMI_tests": sum(len(a["compiled_restricted_test_fixtures"])
                                  for a in source_records),
        "complete_single_record_role_cases": len(cases),
        "cases": cases,
        "not_proven": [
            "actual Windows WMI collector or registry/userright evaluation",
            "nested multi-field record cardinality or OVAL source scanner parity",
            "full seven-Test Assessment result, signed 0.4 bundle or scanner",
        ],
    }


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--json-archive", type=Path, required=True)
    p.add_argument("--report", type=Path)
    args = p.parse_args(argv)
    records = source_fixtures(read_authoring_archive(args.json_archive, "json"))
    report = reference_scenarios(records)
    rendered = json.dumps(report, sort_keys=True, indent=2) + "\n"
    print(rendered, end="")
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(rendered, encoding="utf-8")


if __name__ == "__main__":
    main()
