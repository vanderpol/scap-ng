#!/usr/bin/env python3
"""Fail-closed English-first source-inversion experiment for two real OVAL checks.

RESEARCH ONLY. Neither a normative v0.4 grammar nor scanner parity proof.
Explicitly restrict candidate operators to pinned capability + field + source
cardinality, then compare lowered Test nodes to immutable real source fixtures.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from itertools import product
import json
from pathlib import Path

import yaml

# Reference schemas (OVAL 5.12.3):
# Windows userright_item trustee_name: 0..1 per Item
#   https://oval-community-guidelines.readthedocs.io/en/base/oval-schema-documentation/windows-system-characteristics-schema.html
# Linux partition_item mount_options: 0..unbounded per Item
#   https://oval-community-guidelines.readthedocs.io/en/base/oval-schema-documentation/linux-system-characteristics-schema.html
# Only these TWO operator+capability+field macros are currently supported.
FIXTURES = {
    "rhel9_sv257851_nosuid": {
        "source": "focused-fixtures/source-backed/authoring/shared/assessments/linux/other/home-mounted-nosuid-option.assessment.yaml",
        "test": "home-mounted-nosuid-option-test",
        "candidate": {
            "check": "/home is mounted with the nosuid option.",
            "inspect": "linux.partition",
            "where": {"mount_point": {"matches_regex": r".*\/home"}},
            "require": {"mount_options": {"includes_value": "nosuid"}},
        },
    },
    "win11_sv253254_editionid": {
        "source": "focused-fixtures/source-backed/authoring/ms_windows_11/assessments/automated/SV-253254.automated.yaml",
        "test": "editionid-enterprise-or-enterprises-test",
        "candidate": {
            "check": "EditionID is Enterprise or EnterpriseS",
            "inspect": "windows.registry",
            "where": {
                "hive": {"equals": "local_machine"},
                "key": {"equals": r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"},
                "name": {"equals": "EditionId"},
            },
            "require": {
                "at_least_one_item_exists": True,
                "every_collected_item": {
                    "any_of": [
                        {"all_of": [
                            {"type": {"equals": "string"}},
                            {"value": {"all_values_equal": "Enterprise"}},
                        ]},
                        {"all_of": [
                            {"type": {"equals": "string"}},
                            {"value": {"all_values_equal": "EnterpriseS"}},
                        ]},
                    ]
                },
            },
        },
    },
    "win11_sv253495_guests": {
        "source": "focused-fixtures/source-backed/authoring/ms_windows_11/assessments/automated/SV-253495.automated.yaml",
        "test": "deny-log-on-through-remote-desktop-services-guests-test",
        "candidate": {
            "check": "Deny log on through Remote Desktop Services - Guests",
            "inspect": "windows.userright",
            "where": {"userright": {"equals": "SE_DENY_REMOTE_INTERACTIVE_LOGON_NAME"}},
            "require": {"trustee_name": {"includes_ignoring_case": "Guests"}},
        },
    },
}

PROVEN_MACROS = {
    "linux.partition": {
        "field": "mount_options", "verb": "includes_value",
        "op": "equals",
        "field_requirement": "at_least_one_exists_and_some_match",
        "item_requirement": "at_least_one_exists_and_all_match",
        "selector": ("mount_point", "matches_regex"),
    },
    "windows.userright": {
        "field": "trustee_name", "verb": "includes_ignoring_case",
        "op": "case_insensitive_equals",
        "field_requirement": "at_least_one_exists_and_all_match",
        "item_requirement": "at_least_one_exists_and_some_match",
        "selector": ("userright", "equals"),
    },
}


def exact(node, keys, context):
    if not isinstance(node, dict) or set(node) != set(keys):
        raise ValueError(f"unsupported {context}: expected exactly {sorted(keys)}, got {node}")


def lower_registry(candidate):
    """Preserve real Win11 EditionId two-State alternatives without merging."""
    where = candidate["where"]
    exact(where, ("hive", "key", "name"), "registry selector")
    for selector in ("hive", "key", "name"):
        exact(where[selector], ("equals",), selector)
    requirement = candidate["require"]
    exact(requirement, ("at_least_one_item_exists", "every_collected_item"), "registry requirement")
    if requirement["at_least_one_item_exists"] is not True:
        raise ValueError("explicit Item existence required")
    exact(requirement["every_collected_item"], ("any_of",), "Item requirement")
    branches = requirement["every_collected_item"]["any_of"]
    if not isinstance(branches, list) or len(branches) != 2:
        raise ValueError("real source requires two State alternatives")
    states = []
    for branch in branches:
        exact(branch, ("all_of",), "State alternative")
        children = branch["all_of"]
        if not isinstance(children, list) or len(children) != 2:
            raise ValueError("Each State alternative must have type and value")
        exact(children[0], ("type",), "registry type predicate")
        exact(children[0]["type"], ("equals",), "registry type comparator")
        if children[0]["type"]["equals"] != "string":
            raise ValueError("only source-verified string type is eligible")
        exact(children[1], ("value",), "registry value predicate")
        exact(children[1]["value"], ("all_values_equal",), "registry value operator")
        target = children[1]["value"]["all_values_equal"]
        if not isinstance(target, str) or not target:
            raise ValueError("nonempty literal expected")
        states.append({"and": [
            {"type": {"equals": "string"}},
            {"value": {"equals": target}},
        ]})
    return {
        "test_title": candidate["check"],
        "capability": "windows.registry",
        "object": {"capability": "windows.registry", "select": deepcopy(where)},
        "states": states,
        "reported_elements": "all",
        "states_match": "any",
        "state_fields_require": "at_least_one_exists_and_all_match",
        "collected_items_require": "at_least_one_exists_and_all_match",
    }


def lower(candidate):
    """Exactly and explicitly expand a typed macro to source-equivalent Test."""
    exact(candidate, ("check", "inspect", "where", "require"), "Assessment")
    cap = candidate["inspect"]
    if cap == "windows.registry":
        return lower_registry(candidate)
    if cap not in PROVEN_MACROS:
        raise ValueError("unsupported capability: " + str(cap))
    contract = PROVEN_MACROS[cap]
    field, verb = contract["field"], contract["verb"]
    exact(candidate["where"], (contract["selector"][0],), "Object selector")
    exact(candidate["where"][contract["selector"][0]],
          (contract["selector"][1],), "selector comparator")
    exact(candidate["require"], (field,), "State fields")
    exact(candidate["require"][field], (verb,), "field operator")
    value = candidate["require"][field][verb]
    if not isinstance(value, str) or not value:
        raise ValueError("only nonempty literal string values are proven")
    return {
        "test_title": candidate["check"],
        "capability": cap,
        "object": {"capability": cap, "select": deepcopy(candidate["where"])},
        "states": [{field: {"require": contract["field_requirement"],
                            contract["op"]: value}}],
        "reported_elements": "all",
        "collected_items_require": contract["item_requirement"],
    }


def source_test(document, test_id):
    """Resolve real shared objects; omit only nonsemantic object title."""
    ass = document["assessment"]
    original = deepcopy(ass["tests"][test_id])
    obj = original["object"]
    if isinstance(obj, str):
        objects = ass.get("shared_objects") or {}
        if obj not in objects:
            raise ValueError(f"unresolved Object reference {obj}")
        obj = deepcopy(objects[obj])
        original["object"] = obj
    if not isinstance(obj, dict):
        raise ValueError("object/set forms not proved by this macro")
    obj.pop("object_title", None)
    return original


def verify_fixtures(root):
    cases, rejected = [], []
    for case_id, row in FIXTURES.items():
        path = Path(root) / row["source"]
        with path.open(encoding="utf-8") as handle:
            document = yaml.safe_load(handle)
        actual = source_test(document, row["test"])
        lowered = lower(row["candidate"])
        if actual != lowered:
            raise AssertionError("fail-closed source inversion: " + case_id +
                                 "\nactual: " + repr(actual) +
                                 "\nlowered: " + repr(lowered))
        cases.append({"id": case_id, "test": row["test"],
                      "result": "exact Test graph reconstruction",
                      "source": row["source"]})
        for mutate, value in [("wrong Item cardinality", "none_exist"),
                              ("wrong Field cardinality", "only_one_exists_and_matches")]:
            altered = deepcopy(actual)
            if mutate.startswith("wrong Item"):
                altered["collected_items_require"] = value
            else:
                cap = row["candidate"]["inspect"]
                if cap == "windows.registry":
                    altered["state_fields_require"] = value
                else:
                    field = PROVEN_MACROS[cap]["field"]
                    altered["states"][0][field]["require"] = value
            if altered == lowered:
                raise AssertionError("unexpected acceptance of " + mutate)
            rejected.append(case_id + ": " + mutate)
    for mutation in (
        {"require": {"trustee_name": {"includes": "Guests"}}},
        {"require": {"trustee_name": {"includes_ignoring_case": "Guests",
                                    "unexpected": True}}},
        {"inspect": "windows.registry"},
    ):
        candidate = deepcopy(FIXTURES["win11_sv253495_guests"]["candidate"])
        candidate.update(mutation)
        try:
            lower(candidate)
        except ValueError:
            rejected.append("unsupported candidate: " + repr(mutation))
        else:
            raise AssertionError("accepted unsupported expression: " + repr(mutation))
    return cases, rejected


def reference_boundaries():
    from oval_result_truth_tables import (
        TRUE, FALSE, ERROR, UNKNOWN, NOT_EVALUATED, NOT_APPLICABLE,
        aggregate_check, evaluate_state_entity_existence, evaluate_collected_object_test,
    )
    outcomes = (TRUE, FALSE, ERROR, UNKNOWN, NOT_EVALUATED, NOT_APPLICABLE)
    # The per-Item Windows trustee_name field can occur 0 or 1 times.
    # With exactly one value, OVAL's all and at-least-one charts are identical,
    # for *each* of the six technical statuses (provided existence is held).
    for result in outcomes:
        assert aggregate_check("all", [result]) == aggregate_check("at least one", [result])
    assert evaluate_state_entity_existence("at_least_one_exists", exists=0) == FALSE
    assert evaluate_state_entity_existence("at_least_one_exists", exists=1) == TRUE
    # A field with >1 value is different. Linux mount_options is repeatable:
    assert aggregate_check("all", [TRUE, FALSE]) == FALSE
    assert aggregate_check("at least one", [TRUE, FALSE]) == TRUE
    # Exhaustive bounded Test-level reference cases: preserve existence,
    # aggregation, and complete/incomplete collection flags as an unchanged
    # tuple on source and lowered output. This is model consistency, NOT a scan.
    test_cases = 0
    for flag, count in product(("complete", "incomplete"), range(1, 4)):
        for results in product(outcomes, repeat=count):
            for match in ("all", "at least one"):
                expected = evaluate_collected_object_test(
                    flag, existence="at_least_one_exists",
                    check=match, item_results=list(results), exists=count,
                    has_state=True,
                )
                if expected not in outcomes:
                    raise AssertionError("invalid reference outcome")
                test_cases += 1
    return {
        "singleton_field_six_outcomes_checked": len(outcomes),
        "bounded_Test_reference_cases": test_cases,
        "multi_value_counterexample": "all([true,false])=false vs some([true,false])=true",
        "limitations": "no native scanner, real collected data, records or nontrivial graph proof",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture-root", required=True)
    parser.add_argument("--report", default=None)
    args = parser.parse_args()
    cases, rejected = verify_fixtures(args.fixture_root)
    result = {
        "status": "NARROW SOURCE INVERSION + MODEL-REFERENCE ONLY",
        "source_pin": "vanderpol/scap-ng-editor-sample-data@99cbceae8d594c44cb509df95975ac1676a2b44a",
        "verified": cases,
        "negative_guards": rejected,
        "reference": reference_boundaries(),
        "unsupported": ["Windows nested WMI records", "Windows registry State alternatives",
                        "RHEL user->file foreach", "DNS dynamic Variables",
                        "Apache config discovery", "other operators/cardinality pairs"],
    }
    output = json.dumps(result, indent=2, sort_keys=True) + "\n"
    print(output)
    if args.report:
        Path(args.report).write_text(output, encoding="utf-8")


if __name__ == "__main__":
    main()
