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
from migrate_v04_oval_proven_direct_filters import (
    index_provenance, migrate as migrate_source_proven_filter,
)
from migrate_v04_additional_source_filters import (
    index_source_proof, migrate as migrate_additional_filter,
)

from collections import Counter
from itertools import product
import json
from pathlib import Path

from build_v04_canonical_six_stigs import promote, reconcile_benchmark_specifications
from v04_field_requirement import PAIR_BY_NAME, FIELD_EXISTENCE, PRESENCE, validate_test
from v04_a_authoring_graph_index import read_authoring_archive
from v04_flat_object_authoring import load_catalog, flatten_document, restore_document
from oval_result_truth_tables import evaluate_collected_object_test
from research_english_first_04_six_state import (
    STATES, FLAGS, independent,
)

EXISTENCE = {
    "one_or_more": "at_least_one_exists",
    "none": "none_exist",
    "exactly_one": "only_one_exists",
    "may_be_absent": "any_exist",
}


def describe(requirement):
    validate_test({'require': requirement})
    existence = EXISTENCE[requirement['items_found']]
    if set(requirement) == {'items_found'}:
        return existence, 'all', False
    check = {'every': 'all', 'one_or_more': 'at least one',
             'exactly_one': 'only one', 'none': 'none satisfy'}[requirement['items_satisfying']]
    return existence, check, True


def source_axes(source_test):
    old = source_test.get('collected_items_require', source_test.get('require'))
    if source_test.get('states'):
        if old not in PAIR_BY_NAME:
            raise ValueError('source Test requires exceptional semantics')
        existence, match = PAIR_BY_NAME[old]
        found = FIELD_EXISTENCE[existence]
        original_existence = 'all_exist' if found == 'every' else EXISTENCE[found]
        check = {'all': 'all', 'one': 'only one', 'one_or_more': 'at least one',
                 'none': 'none satisfy'}[match]
        return original_existence, check, True
    if old in PRESENCE:
        return ('all_exist' if old == 'all_exist' else EXISTENCE[PRESENCE[old]]), 'all', False
    raise ValueError('source Test requires exceptional semantics')


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


def compare_original_to_canonical(original, canonical, *, filter_proof=None,
                                  additional_proof=None):
    if set(original) != set(canonical):
        raise ValueError("different original/canonical document path sets")
    # The reviewed Benchmark 0.3 -> 0.4 declaration update is the only
    # intentional source difference outside lossless Test/Object promotion.
    promoted = {}
    for path, doc in original.items():
        proposed, _ = promote(doc)
        if filter_proof is not None:
            proposed, _ = migrate_source_proven_filter(proposed, path, filter_proof)
        if additional_proof is not None:
            if filter_proof is None:
                raise ValueError("Second-pass Filter proof requires original first-pass proof")
            proposed, _ = migrate_additional_filter(proposed, path, additional_proof)
        promoted[path] = proposed
    if any("benchmark" in doc for doc in original.values()):
        promoted, _ = reconcile_benchmark_specifications(promoted)
    # The canonical six-STIG builder now applies the source-invertible,
    # approved flat-Object pass *after* the Test/Filter/version promotions.
    # Recreate it independently from the pinned input, rather than ignoring
    # Object differences or weakening the whole-document equality gate.
    catalog = load_catalog(Path(__file__).resolve().parents[1] /
                           "schema/v0.4.0/capability-mappings/supported")
    for path, staged in promoted.items():
        flattened, inverse = flatten_document(staged, catalog)
        if restore_document(flattened, inverse) != staged:
            raise ValueError(f"{path}: flat Object source inverse failed")
        promoted[path] = flattened
    counts = Counter()
    axes = set()
    by_capability = Counter()
    for path, doc in sorted(original.items()):
        if promoted[path] != canonical[path]:
            raise ValueError(f"{path}: canonical content differs from exact source promotion")
        old = doc.get("assessment")
        if not isinstance(old, dict) or old.get("mode") != "automated":
            continue
        next_tests = canonical[path]["assessment"].get("tests") or {}
        for tid, src in (old.get("tests") or {}).items():
            candidate = next_tests[tid]
            req = candidate.get("require")
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
    p.add_argument("--filter-proof", type=Path, default=None,
                   help="Original-OVAL source Filter classification; required for migrated 0.4 sources")
    p.add_argument("--additional-filter-proof",type=Path,default=None)
    a = p.parse_args()
    original = read_authoring_archive(a.original_json, "json")
    canonical = read_authoring_archive(a.canonical_json, "json")
    proof = (index_provenance(json.loads(a.filter_proof.read_text()), assert_six=True)
             if a.filter_proof else None)
    additional = (index_source_proof(json.loads(a.additional_filter_proof.read_text()),
                                      assert_six=True) if a.additional_filter_proof else None)
    result = compare_original_to_canonical(
        original, canonical, filter_proof=proof, additional_proof=additional)
    if a.assert_six and (
        result["documents"],
        result["test_population"].get("converted_presence"),
        result["test_population"].get("converted_all_items"),
        result["test_population"].get("exceptional_source_exact"),
    ) != (4012, 399, 991, None):
        raise ValueError("full six-STIG canonical requirement population changed")
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(json.dumps({key: value for key, value in result.items()
                      if key not in {"converted_by_capability", "mode_matrix"}},
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
