#!/usr/bin/env python3
"""#229/#232: source-backed native 0.4-A Test/result fixture selection inventory.

Read exact immutable six-STIG JSON authoring; list the real Test/State/Object
shapes of selected complex Assessments. No OVAL evaluation, source mutation,
new grammar or runtime Test outcome is claimed.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

from v04_a_authoring_graph_index import canonical_json, read_authoring_archive

KNOWN_TARGETS = (
    "SV-253260.automated", # nested Windows 11 all/any/not
    "SV-278001.automated", # Server 2025 role/branch OVAL-derived Boolean expression
    "SV-258236.automated", # RHEL 9 multi-Test
    "SV-253495.automated", # Windows 11 record/WMI anchors
)


def _walk(node):
    stack = [node]
    while stack:
        current = stack.pop()
        if isinstance(current, dict):
            yield current
            stack.extend(current.values())
        elif isinstance(current, list):
            stack.extend(current)


def source_profile(documents, ids=KNOWN_TARGETS):
    targets = set(ids)
    if len(targets) != len(ids) or not targets:
        raise ValueError("duplicate or empty source target IDs")
    found = {}
    for source_path, document in sorted(documents.items()):
        assessment = document.get("assessment")
        if not isinstance(assessment, dict) or assessment.get("id") not in targets:
            continue
        aid = assessment["id"]
        if aid in found:
            raise ValueError(f"duplicate Assessment source ID: {aid}")
        tests = assessment.get("tests", {})
        if not isinstance(tests, dict) or not tests:
            raise ValueError(f"selected Assessment has no Tests: {aid}")
        records = []
        for name, test in sorted(tests.items()):
            if not isinstance(test, dict):
                raise ValueError(f"{aid}: invalid Test {name}")
            observed_keys = Counter()
            for node in _walk(test):
                observed_keys.update(str(k) for k in node)
            records.append({
                "test_id": name,
                "capability": test.get("capability"),
                "require": test.get("require", test.get("collected_items_require")),
                "has_state": bool(test.get("states")),
                "state_count": len(test.get("states") or []),
                "states_match": test.get("states_match"),
                "has_inline_object": isinstance(test.get("object"), dict),
                "shared_object_reference": test.get("object") if isinstance(
                    test.get("object"), str) else None,
                "record_nodes": observed_keys["record"],
                "set_nodes": observed_keys["set"],
                "filters_nodes": observed_keys["filters"],
                "foreach_nodes": observed_keys["for_each"],
                "variable_references": observed_keys["variable"],
                "wmi_record_state_source": test.get("states") if test.get("capability") == "windows.wmi.query" else None,
                "wmi_object_source": test.get("object") if test.get("capability") == "windows.wmi.query" else None,
                "test_source_sha256": sha256(canonical_json(test)).hexdigest(),
            })
        counts = Counter()
        for n in _walk(assessment.get("evaluate", {})):
            counts.update(n.keys())
        found[aid] = {
            "assessment_id": aid,
            "source_path": source_path,
            "source_document_sha256": sha256(canonical_json(document)).hexdigest(),
            "mode": assessment.get("mode"),
            "source_specification": assessment.get("specification"),
            "evaluate_operators": dict(sorted(counts.items())),
            "named_variables": len(assessment.get("variables") or {}),
            "shared_objects": len(assessment.get("shared_objects") or {}),
            "tests": records,
        }
    if set(found) != targets:
        raise ValueError(f"missing source Assessment anchors: {sorted(targets-set(found))}")
    return {
        "stage": "SOURCE_FACTS_ONLY_NOT_EXECUTION",
        "checked_source_assessment_count": len(found),
        "selected_source_assessments": [found[k] for k in sorted(found)],
        "not_proven": [
            "collected system Items and completeness",
            "Test/State/record result equivalence to original OVAL",
            "approved conditional or executable scanner semantics",
        ],
    }


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--json-archive", type=Path, required=True)
    p.add_argument("--output", type=Path)
    args = p.parse_args(argv)
    report = source_profile(read_authoring_archive(args.json_archive, "json"))
    data = json.dumps(report, sort_keys=True, indent=2) + "\n"
    print(data, end="")
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(data, encoding="utf-8")


if __name__ == "__main__":
    main()
