#!/usr/bin/env python3
"""Source-backed six-state *generic* oracle for the 221 0.4 source exceptions.

This checks the existence and check-aggregation axes of the legacy source
requirements *without rewriting any Test*. It does NOT compare or interpret
States, alternative-state aggregation, record/cardinality semantics, capability
collection or native executable scanner behavior. Refs #229 #232.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

from v04_canonical_requirement_oracle import comparison_matrix

# OVAL 5.12.3 ExistenceEnumeration, CheckEnumeration pairs. No implied
# new 0.4.0 requirement keywords are introduced by this research-only table.
AXES = {
    "all_exist_and_all_match": ("all_exist", "all", True),
    "all_exist_and_none_match": ("all_exist", "none satisfy", True),
    "at_least_one_exists_and_all_match": ("at_least_one_exists", "all", True),
    "at_least_one_exists_and_only_one_matches": ("at_least_one_exists", "only one", True),
    "at_least_one_exists_and_some_match": ("at_least_one_exists", "at least one", True),
    "may_be_absent_and_none_match": ("any_exist", "none satisfy", True),
    "may_be_absent_and_all_match": ("any_exist", "all", True),
    "may_be_absent_and_some_match": ("any_exist", "at least one", True),
    "none_exist": ("none_exist", "all", True),
    "only_one_exists_and_matches": ("only_one_exists", "all", True),
    "only_one_exists_and_only_one_matches": ("only_one_exists", "only one", True),
}
BASELINE = {
    "all_exist_and_all_match": 75,
    "all_exist_and_none_match": 1,
    "at_least_one_exists_and_all_match": 42,
    "at_least_one_exists_and_only_one_matches": 21,
    "at_least_one_exists_and_some_match": 67,
    "may_be_absent_and_none_match": 3,
    "may_be_absent_and_all_match": 5,
    "may_be_absent_and_some_match": 1,
    "none_exist": 1,
    "only_one_exists_and_matches": 3,
    "only_one_exists_and_only_one_matches": 2,
}


def audit(ledger, *, assert_six=False):
    entries = ledger.get("entries")
    if not isinstance(entries, list):
        raise ValueError("missing exception source ledger")
    labels = Counter()
    seen = set()
    counts = Counter()
    for entry in entries:
        if not isinstance(entry, dict) or entry.get("require") not in AXES:
            raise ValueError("unknown source requirement; do not guess its OVAL check")
        test = entry.get("source_test")
        if not isinstance(test, dict) or test.get("require") != entry["require"]:
            raise ValueError("ledger not source-exact")
        if not isinstance(test.get("states"), list) or not test["states"]:
            raise ValueError("unconverted requirement lost its State source")
        key = (entry.get("path"), entry.get("assessment"), entry.get("test"))
        if key in seen or any(not isinstance(v, str) or not v for v in key):
            raise ValueError("duplicate/unnamed source Test exception")
        seen.add(key)
        labels[entry["require"]] += 1
        if "states_match" in test:
            counts["tests_with_state_aggregation_unverified"] += 1
        if "state_fields_require" in test:
            counts["tests_with_field_cardinality_unverified"] += 1
    if labels != Counter(ledger.get("by_requirement") or {}):
        raise ValueError("ledger family inventory does not match actual source Tests")
    if assert_six and (len(entries) != 221 or labels != Counter(BASELINE)):
        raise ValueError("six-STIG source exception distribution changed; review required")
    distinct = {AXES[label] for label in labels}
    matrix = {"/".join([axis[0], axis[1]]): comparison_matrix(axis)
              for axis in sorted(distinct)}
    return {
        "status": "GENERIC_EXCEPTION_SOURCE_AXES_VERIFIED_NOT_LOWERED",
        "source_exceptions": len(entries),
        "source_requirement_families": dict(sorted(labels.items())),
        "source_states_retained": len(entries),
        "generic_oval_scenarios_compared": sum(x["compared"] for x in matrix.values()),
        "undefined_empty_reference_scenarios": sum(
            x["unresolved_empty_aggregate"] for x in matrix.values()),
        "source_specific_unverified": dict(sorted(counts.items())),
        "all_match_source_exceptions_needing_state_record_review": (
            labels["at_least_one_exists_and_all_match"]
            + labels["may_be_absent_and_all_match"]),
        "mode_matrix": matrix,
        "native_compact_lowering_proved": False,
        "alternative_state_or_field_semantics_proved": False,
        "capability_specific_parity_proved": False,
        "scanner_parity": False,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--ledger", type=Path, required=True)
    p.add_argument("--report", type=Path, required=True)
    p.add_argument("--assert-six", action="store_true")
    a = p.parse_args()
    ledger = json.loads(a.ledger.read_text(encoding="utf-8"))
    report = audit(ledger, assert_six=a.assert_six)
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "mode_matrix"}, indent=2))


if __name__ == "__main__":
    main()
