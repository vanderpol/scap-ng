#!/usr/bin/env python3
"""Fail-closed 0.4.0 Filter-preservation and synthetic-Set regression gate.

Compare regenerated canonical authoring with the SHA-pinned accepted baseline.
Allow existing singleton-Union wrappers to remain unchanged, or to become
exact local Object filters, but only without changing their source-selected
Object, predicates, actions, ordering or effective inline capability.

A structural match is NOT proof that original OVAL contained no Set. Genuine
Sets, new/ambiguous shapes, and non-equivalent rewrites require source review.
The pinned original-OVAL provenance audit is a separate mandatory gate.

Refs #248.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path

from audit_v04_synthetic_filter_unions import candidate
from v04_a_authoring_graph_index import read_authoring_archive


def logical_path(path):
    if not path.startswith("authoring/") or not path.endswith((".json", ".yaml")):
        raise ValueError("Unexpected authoring document path: " + path)
    return path.rsplit(".", 1)[0]


def _entry_key(path, route):
    return (logical_path(path), tuple(route))


def audit_documents(documents):
    """Index filtered-Union shapes and all author-visible Filter predicates."""
    wrappers = {}
    filters = Counter()
    for path, doc in sorted(documents.items()):
        assessment = doc.get("assessment") if isinstance(doc, dict) else None
        if not isinstance(assessment, dict) or assessment.get("mode") != "automated":
            continue
        source = logical_path(path)
        assessment_id = assessment.get("id")
        if not isinstance(assessment_id, str):
            raise ValueError(f"{path}: Assessment ID missing")
        def walk(node, route):
            if isinstance(node, dict):
                shape = candidate(node)
                if shape is not None:
                    key = _entry_key(path, route)
                    if key in wrappers:
                        raise ValueError(f"{source}: duplicate wrapper site {route}")
                    wrappers[key] = {
                        "object": deepcopy(node),
                        "inner": deepcopy(shape["object"]),
                        "filters": deepcopy(shape["filters"]),
                        "assessment_id": assessment_id,
                    }
                if "filters" in node:
                    entries = node["filters"]
                    if not isinstance(entries, list):
                        raise ValueError(f"{source}: non-list filters at {route}")
                    for filt in entries:
                        if not isinstance(filt, dict) or set(filt) not in ({"include"}, {"exclude"}):
                            raise ValueError(f"{source}: ambiguous Filter at {route}")
                        # Include the parent Assessment so a Filter cannot silently
                        # disappear from one Assessment and reappear in another.
                        filters[(source, json.dumps(filt, sort_keys=True,
                                                    separators=(",", ":")))] += 1
                for key, value in node.items():
                    walk(value, route + (key,))
            elif isinstance(node, list):
                for index, value in enumerate(node):
                    walk(value, route + (index,))
        walk(assessment, ("assessment",))
    return wrappers, filters


def _at_path(documents, key):
    path, route = key
    candidates = [doc for name, doc in documents.items() if logical_path(name) == path]
    if len(candidates) != 1:
        return None
    value = candidates[0]
    try:
        for part in route:
            value = value[part]
    except (KeyError, IndexError, TypeError):
        return None
    return value


def _direct_equivalent(old, actual, key, target_docs):
    expected = deepcopy(old["inner"])
    if not isinstance(actual, dict):
        return False
    # Canonical inline Object capability is inherited from its Test, not
    # duplicated in the human source. Do not erase differing capabilities.
    route = key[1]
    if (len(route) == 4 and route[:2] == ("assessment", "tests")
            and route[3] == "object" and "capability" in expected):
        test = _at_path(target_docs, (key[0], route[:3]))
        if not isinstance(test, dict) or test.get("capability") != expected["capability"]:
            return False
        expected.pop("capability")
    expected["filters"] = deepcopy(old["filters"])
    return actual == expected


def compare(baseline_docs, target_docs, *, expected_baseline_candidates=None):
    old_wrappers, old_filters = audit_documents(baseline_docs)
    new_wrappers, new_filters = audit_documents(target_docs)
    if expected_baseline_candidates is not None and len(old_wrappers) != expected_baseline_candidates:
        raise ValueError(
            f"Pinned 0.4.0 baseline changed: expected {expected_baseline_candidates}"
            f" wrappers, got {len(old_wrappers)}"
        )
    errors = []
    retained = migrated = 0
    for key, old in sorted(old_wrappers.items()):
        actual = _at_path(target_docs, key)
        if actual == old["object"]:
            retained += 1
        elif _direct_equivalent(old, actual, key, target_docs):
            migrated += 1
        else:
            errors.append(f"{key[0]} {list(key[1])}: Filter/Set content missing or changed")
    for key in sorted(new_wrappers.keys() - old_wrappers.keys()):
        errors.append(f"{key[0]} {list(key[1])}: new singleton filtered-Union")
    if old_filters != new_filters:
        for key, count in sorted((old_filters - new_filters).items()):
            errors.append(f"{key[0]}: lost/changed Filter {key[1]} ({count})")
        for key, count in sorted((new_filters - old_filters).items()):
            errors.append(f"{key[0]}: added/changed Filter {key[1]} ({count})")
    report = {
        "status": "PASS" if not errors else "FAIL",
        "baseline_wrapper_sites": len(old_wrappers),
        "current_wrapper_sites": len(new_wrappers),
        "unchanged_wrapper_sites": retained,
        "exact_direct_filter_migrations": migrated,
        "baseline_filter_occurrences": sum(old_filters.values()),
        "current_filter_occurrences": sum(new_filters.values()),
        "errors": errors,
        "original_oval_semantics_proven": False,
        "scanner_result_parity_proven": False,
    }
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--baseline-archive", type=Path, required=True)
    p.add_argument("--archive", type=Path, required=True)
    p.add_argument("--expected-baseline-candidates", type=int, default=None)
    p.add_argument("--report", type=Path, required=True)
    args = p.parse_args()
    old = read_authoring_archive(args.baseline_archive, "json")
    fmt = "yaml" if args.archive.name.endswith(".yaml.zip") else "json"
    new = read_authoring_archive(args.archive, fmt)
    report = compare(old, new, expected_baseline_candidates=args.expected_baseline_candidates)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    if report["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
