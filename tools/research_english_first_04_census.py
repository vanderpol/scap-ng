#!/usr/bin/env python3
"""Conservative full-corpus English-first exact-lowering eligibility census.

No converter changes. Supports exactly the three research templates already
proven individually by source inversion; every other shape stays unsupported.
Report distinct source files and named Test nodes, not runtime result parity.
"""
from collections import Counter, defaultdict
from copy import deepcopy
from pathlib import Path
import argparse
import json
import sys
import zipfile

import yaml
from research_english_first_04 import lower, source_test


def try_candidate(original):
    if not isinstance(original, dict):
        return None, "not_a_mapping"
    cap = original.get("capability")
    obj = original.get("object")
    if not isinstance(obj, dict):
        return None, "unsupported_object_shape"
    where = obj.get("select")
    title = original.get("test_title")
    if not isinstance(title, str) or not title or not isinstance(where, dict):
        return None, "missing_local_selector_or_title"
    states = original.get("states")
    if cap == "linux.partition":
        if not isinstance(states, list) or len(states) != 1:
            return None, "linux_complex_states"
        field = states[0].get("mount_options") if isinstance(states[0], dict) else None
        if not isinstance(field, dict) or set(field) != {"equals", "require"}:
            return None, "linux_complex_mount_field"
        if field["require"] != "at_least_one_exists_and_some_match":
            return None, "linux_field_cardinality"
        if set(where) != {"mount_point"}:
            return None, "linux_complex_selector"
        return {"check": title, "inspect": cap, "where": where,
                "require": {"mount_options": {"includes_value": field["equals"]}}}, None
    if cap == "windows.userright":
        if not isinstance(states, list) or len(states) != 1:
            return None, "userright_complex_states"
        field = states[0].get("trustee_name") if isinstance(states[0], dict) else None
        if not isinstance(field, dict) or set(field) != {"case_insensitive_equals", "require"}:
            return None, "userright_complex_trustee"
        if field["require"] != "at_least_one_exists_and_all_match":
            return None, "userright_field_cardinality"
        if set(where) != {"userright"}:
            return None, "userright_complex_selector"
        return {"check": title, "inspect": cap, "where": where,
                "require": {"trustee_name": {
                    "includes_ignoring_case": field["case_insensitive_equals"]}}}, None
    if cap == "windows.registry":
        if not isinstance(states, list) or len(states) != 2:
            return None, "registry_not_two_alternatives"
        parts = []
        for group in states:
            if not isinstance(group, dict) or set(group) != {"and"} or not isinstance(group["and"], list) or len(group["and"]) != 2:
                return None, "registry_complex_state_group"
            typed, value = group["and"]
            if typed != {"type": {"equals": "string"}}:
                return None, "registry_type_condition"
            if not isinstance(value, dict) or set(value) != {"value"} or not isinstance(value["value"], dict) or set(value["value"]) != {"equals"}:
                return None, "registry_value_condition"
            parts.append({"all_of": [
                {"type": {"equals": "string"}},
                {"value": {"all_values_equal": value["value"]["equals"]}},
            ]})
        if set(where) != {"hive", "key", "name"}:
            return None, "registry_complex_selector"
        return {"check": title, "inspect": cap, "where": where,
                "require": {"at_least_one_item_exists": True,
                            "every_collected_item": {"any_of": parts}}}, None
    return None, "capability_or_structure_unsupported"


def audit(archive):
    by_category = Counter()
    cap_counter = Counter()
    admitted, rejected = [], []
    unique_docs, named_tests = 0, 0
    archive_sha = Path(archive).name
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None:
            raise ValueError("Corrupt pinned source ZIP")
        paths = [p for p in z.namelist()
                 if p.startswith("authoring/") and "/assessments/" in p and p.endswith(".yaml")]
        for path in sorted(paths):
            document = yaml.safe_load(z.read(path))
            ass = (document or {}).get("assessment") or {}
            if ass.get("mode") != "automated" or not ass.get("tests"):
                continue
            unique_docs += 1
            for test_name, original_test in ass["tests"].items():
                named_tests += 1
                cap = original_test.get("capability", "<missing>")
                cap_counter[cap] += 1
                try:
                    original = source_test(document, test_name)
                except (ValueError, KeyError, TypeError) as e:
                    category = "unresolvable_original_object"
                    by_category[category] += 1
                    if len(rejected) < 30:
                        rejected.append({"path": path, "test": test_name, "reason": category, "detail": str(e)[:130]})
                    continue
                candidate, category = try_candidate(original)
                if candidate is None:
                    by_category[category] += 1
                    if len(rejected) < 30:
                        rejected.append({"path": path, "test": test_name, "reason": category})
                    continue
                try:
                    lowered = lower(candidate)
                except (ValueError, KeyError, TypeError) as e:
                    category = "typed_compiler_rejected"
                    by_category[category] += 1
                    if len(rejected) < 30:
                        rejected.append({"path": path, "test": test_name, "reason": category, "detail": str(e)[:130]})
                    continue
                if lowered != original:
                    category = "not_source_identical"
                    by_category[category] += 1
                    if len(rejected) < 30:
                        rejected.append({"path": path, "test": test_name, "reason": category})
                    continue
                by_category["exact_source_inversion"] += 1
                admitted.append({"path": path, "test": test_name,
                                 "capability": cap, "source_equivalence": "exact Test node only"})
    if named_tests == 0:
        raise ValueError("No automated Assessment Tests found in the archive")
    if sum(by_category.values()) != named_tests:
        raise AssertionError("Every Test must receive an exact or rejected classification")
    return {
        "source_archive_name": archive_sha,
        "scope": "distinct automated Assessment files (shared counted once), all their named Tests",
        "documents": unique_docs,
        "named_tests": named_tests,
        "counts": dict(by_category.most_common()),
        "capabilities": dict(cap_counter.most_common()),
        "admitted": admitted,
        "rejected_samples": rejected,
        "evidence": "typed Test-source inversion (NOT independent runtime or full Assessment equivalence)",
        "warning": "everything not source-identical is fail-closed/unsupported; no fallback conversions",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--archive", required=True)
    ap.add_argument("--output", default=None)
    args = ap.parse_args()
    result = audit(args.archive)
    output = json.dumps(result, indent=2, sort_keys=True) + "\n"
    print(json.dumps({
        "documents": result["documents"], "named_tests": result["named_tests"],
        "counts": result["counts"], "n_admitted": len(result["admitted"]),
        "first_admitted": result["admitted"][:8],
    }, indent=2))
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")


if __name__ == "__main__":
    main()
