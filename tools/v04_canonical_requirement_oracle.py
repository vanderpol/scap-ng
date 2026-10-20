#!/usr/bin/env python3
"""Pinned OVAL 5.12.3 generic result cross-check for real canonical 0.4 Tests.

Connects actual six-STIG source Test declarations to the source-reversible
presence and all-match authoring grammar. Compares a pinned OVAL reference
combiner with a separately implemented six-state model under complete,
incomplete, error, and absent collection flags. This does not evaluate
capability fields, nested record values, or scan a real target. Exceptional
legacy matching families are inventoried, NOT asserted equivalent.
"""
from __future__ import annotations

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path

from build_v04_canonical_six_stigs import promote, PAIRS, PRESENCE
from v04_a_authoring_graph_index import read_authoring_archive
from oval_result_truth_tables import evaluate_collected_object_test
from research_english_first_04_six_state import (
    STATES, FLAGS, independent,
)

EXISTENCE = {
    "one_or_more": "at_least_one_exists",
    "none": "none_exist",
    "exactly_one": "only_one_exists",
    "all": "all_exist",
    "may_be_absent": "any_exist",
}


def describe(requirement):
    if not isinstance(requirement, dict):
        raise ValueError("expected structured canonical Test requirement")
    if set(requirement) == {"items"}:
        return EXISTENCE[requirement["items"]], "all", False
    if set(requirement) == {"items", "all_items_must"}:
        if requirement["items"] not in PAIRS.values() or not requirement["all_items_must"]:
            raise ValueError("invalid structured all-match requirement")
        return EXISTENCE[requirement["items"]], "all", True
    raise ValueError("unknown structured requirement")


def source_axes(source_test):
    old = source_test.get("collected_items_require", source_test.get("require"))
    if old in PRESENCE:
        if source_test.get("states") or "states_match" in source_test:
            raise ValueError("source State-free Test unexpectedly has States")
        return EXISTENCE[PRESENCE[old]], "all", False
    if old in PAIRS:
        if not source_test.get("states"):
            raise ValueError("source all-match Test lacks States")
        return EXISTENCE[PAIRS[old]], "all", True
    raise ValueError("source Test requires exceptional semantics")


def comparison_matrix(axis):
    existence, check, with_state = axis
    tested = unresolved = 0
    for n in range(4):
        valuesets = product(STATES, repeat=n) if with_state else [()]
        for values in valuesets:
            for absent, err, nc in product((0, 1), repeat=3):
                for flag in FLAGS:
                    kwargs = {
                        "existence": existence, "check": check,
                        "has_state": with_state,
                        "item_results": list(values) if with_state else None,
                        "exists": n, "does_not_exist": absent,
                        "error": err, "not_collected": nc,
                    }
                    try:
                        expected = evaluate_collected_object_test(flag, **kwargs)
                    except (ValueError, AssertionError) as exc:
                        # An empty State aggregate has no OVAL reference result.
                        # Do not quietly invent a result for that boundary.
                        if n != 0 or not with_state or flag != "complete":
                            raise
                        if not (isinstance(exc, AssertionError)
                                or "requires at least one input" in str(exc)):
                            raise
                        unresolved += 1
                        continue
                    actual = independent(flag, existence, check, values, with_state,
                                         n, absent, err, nc)
                    if actual != expected:
                        raise AssertionError({
                            "axis": axis, "flag": flag, "observed_items": values,
                            "absent": absent, "error": err, "not_collected": nc,
                            "reference": expected, "independent": actual,
                        })
                    tested += 1
    return {"compared": tested, "unresolved_empty_aggregate": unresolved}


def compare_original_to_canonical(original, canonical):
    if set(original) != set(canonical):
        raise ValueError("different original/canonical document path sets")
    counts = Counter()
    axes = set()
    by_capability = Counter()
    for path, doc in sorted(original.items()):
        promoted, _ = promote(doc)
        if promoted != canonical[path]:
            raise ValueError(f"{path}: canonical content differs from exact source promotion")
        old = doc.get("assessment")
        if not isinstance(old, dict) or old.get("mode") != "automated":
            continue
        next_tests = canonical[path]["assessment"].get("tests") or {}
        for tid, src in (old.get("tests") or {}).items():
            candidate = next_tests[tid]
            req = candidate.get("require")
            if isinstance(req, str):
                counts["exceptional_source_exact"] += 1
                continue
            expected = source_axes(src)
            actual = describe(req)
            if actual != expected:
                raise AssertionError(f"{path}/{tid}: canonical existence/check does not match source")
            axes.add(actual)
            counts["converted_all_items" if actual[2] else "converted_presence"] += 1
            by_capability[candidate["capability"]] += 1
    if not axes:
        raise ValueError("no converted Test examples")
    matrix = {"/".join([axis[0], axis[1], str(axis[2])]): comparison_matrix(axis)
              for axis in sorted(axes)}
    return {
        "status": "SOURCE_AXES_AND_PINNED_OVAL_RESULT_ORACLE_PASS",
        "documents": len(original),
        "test_population": dict(sorted(counts.items())),
        "converted_by_capability": dict(sorted(by_capability.items())),
        "generic_scenarios": sum(v["compared"] for v in matrix.values()),
        "unresolved_empty_aggregates": sum(
            v["unresolved_empty_aggregate"] for v in matrix.values()),
        "mode_matrix": matrix,
        "source_exact_promotion": "PASS",
        "ovals_5_12_3_generic_result_oracle": "PASS",
        "source_exception_matching_equivalence_proved": False,
        "capability_field_semantics_proved": False,
        "scanner_parity": False,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--original-json", type=Path, required=True)
    p.add_argument("--canonical-json", type=Path, required=True)
    p.add_argument("--report", type=Path, required=True)
    p.add_argument("--assert-six", action="store_true")
    a = p.parse_args()
    original = read_authoring_archive(a.original_json, "json")
    canonical = read_authoring_archive(a.canonical_json, "json")
    result = compare_original_to_canonical(original, canonical)
    if a.assert_six and (
        result["documents"],
        result["test_population"].get("converted_presence"),
        result["test_population"].get("converted_all_items"),
        result["test_population"].get("exceptional_source_exact"),
    ) != (4001, 387, 816, 172):
        raise ValueError("full six-STIG canonical requirement population changed")
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(json.dumps({key: value for key, value in result.items()
                      if key not in {"converted_by_capability", "mode_matrix"}},
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
