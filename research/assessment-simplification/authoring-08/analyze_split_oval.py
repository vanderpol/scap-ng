#!/usr/bin/env python3
"""Quantify raw OVAL feature use in per-Rule splitter output.

Input is one scap14_rule_splitter.py output directory. Each rules/<id>/oval.xml
is already the reachable OVAL closure for that XCCDF Rule, so percentages are
Rule-weighted rather than global-document element counts.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import xml.etree.ElementTree as ET


FUNCTIONS = {
    "arithmetic",
    "begin",
    "concat",
    "count",
    "end",
    "escape_regex",
    "glob_to_regex",
    "merge",
    "regex_capture",
    "split",
    "substring",
    "time_difference",
    "unique",
}
COMPONENTS = FUNCTIONS | {"object_component", "variable_component", "literal_component"}


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def family(tag: str) -> str:
    if "}" not in tag:
        return "core"
    uri = tag.split("}", 1)[0].strip("{")
    return uri.split("#")[-1].split("/")[-1]


def criteria_depth(node) -> int:
    children = [x for x in node if local(x.tag) == "criteria"]
    if not children:
        return 1
    return 1 + max(criteria_depth(x) for x in children)


def scan_rule(path: Path) -> dict:
    root = ET.parse(path).getroot()
    counts = Counter()
    tests = Counter()
    variable_kinds = Counter()
    functions = Counter()
    checks = Counter()
    existence = Counter()
    criteria_ops = Counter()
    var_checks = Counter()
    entity_checks = Counter()
    state_entity_existence = Counter()
    criteria_max_depth = 0

    for node in root.iter():
        name = local(node.tag)

        if name == "definition":
            counts["definitions"] += 1
        elif name.endswith("_test"):
            counts["tests"] += 1
            tests[f"{family(node.tag)}.{name[:-5]}"] += 1
            checks[node.get("check") or "<missing>"] += 1
            existence[node.get("check_existence") or "<default>"] += 1
        elif name.endswith("_object"):
            counts["objects"] += 1
        elif name.endswith("_state"):
            counts["states"] += 1
        elif name.endswith("_variable"):
            counts["variables"] += 1
            variable_kinds[name] += 1

        if name == "set":
            counts["sets"] += 1
        elif name == "filter":
            counts["filters"] += 1
        elif name in FUNCTIONS:
            functions[name] += 1
        elif name == "object_component":
            counts["object_component"] += 1
        elif name == "variable_component":
            counts["variable_component"] += 1
        elif name == "literal_component":
            counts["literal_component"] += 1

        if name == "criteria":
            counts["criteria_nodes"] += 1
            criteria_ops[(node.get("operator") or "AND").upper()] += 1
            criteria_max_depth = max(criteria_max_depth, criteria_depth(node))

        if node.get("var_ref"):
            counts["entity_var_ref"] += 1
            var_checks[node.get("var_check") or "all"] += 1
        if node.get("entity_check") is not None:
            entity_checks[node.get("entity_check")] += 1
        if node.get("check_existence") is not None and not name.endswith("_test"):
            state_entity_existence[node.get("check_existence")] += 1

    flags = {
        "has_variables": counts["variables"] > 0,
        "has_functions": bool(functions),
        "has_sets": counts["sets"] > 0,
        "has_filters": counts["filters"] > 0,
        "has_object_component": counts["object_component"] > 0,
        "has_variable_component": counts["variable_component"] > 0,
        "has_entity_var_ref": counts["entity_var_ref"] > 0,
        "multiple_tests": counts["tests"] > 1,
        "multiple_objects": counts["objects"] > 1,
        "multiple_states": counts["states"] > 1,
        "multiple_variables": counts["variables"] > 1,
        "criteria_depth_gt_2": criteria_max_depth > 2,
        "shellcommand_test": any(key.endswith(".shellcommand") for key in tests),
    }
    return {
        "rule": path.parent.name,
        "counts": dict(counts),
        "flags": flags,
        "test_types": dict(tests),
        "variable_kinds": dict(variable_kinds),
        "functions": dict(functions),
        "test_check": dict(checks),
        "test_check_existence": dict(existence),
        "criteria_operators": dict(criteria_ops),
        "criteria_max_depth": criteria_max_depth,
        "var_check": dict(var_checks),
        "entity_check": dict(entity_checks),
        "state_entity_existence": dict(state_entity_existence),
    }


def aggregate(rows: list[dict], label: str) -> dict:
    feature_counts = Counter()
    totals = Counter()
    test_types = Counter()
    variable_kinds = Counter()
    functions = Counter()
    checks = Counter()
    existence = Counter()
    criteria_ops = Counter()
    var_checks = Counter()
    entity_checks = Counter()
    state_existence = Counter()
    depth = Counter()

    for row in rows:
        for key, value in row["flags"].items():
            if value:
                feature_counts[key] += 1
        totals.update(row["counts"])
        test_types.update(row["test_types"])
        variable_kinds.update(row["variable_kinds"])
        functions.update(row["functions"])
        checks.update(row["test_check"])
        existence.update(row["test_check_existence"])
        criteria_ops.update(row["criteria_operators"])
        var_checks.update(row["var_check"])
        entity_checks.update(row["entity_check"])
        state_existence.update(row["state_entity_existence"])
        depth[row["criteria_max_depth"]] += 1

    n = len(rows)
    return {
        "label": label,
        "rules_with_oval": n,
        "feature_rule_counts": dict(feature_counts),
        "feature_rule_pct": {
            key: round(100.0 * value / n, 2) if n else 0.0
            for key, value in sorted(feature_counts.items())
        },
        "closure_element_totals": dict(totals),
        "test_types": dict(test_types.most_common()),
        "variable_kinds": dict(variable_kinds),
        "function_occurrences": dict(functions),
        "test_check": dict(checks),
        "test_check_existence": dict(existence),
        "criteria_operators": dict(criteria_ops),
        "criteria_depth_rule_counts": {str(k): v for k, v in sorted(depth.items())},
        "var_check": dict(var_checks),
        "entity_check": dict(entity_checks),
        "state_entity_existence": dict(state_existence),
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("split_root", type=Path)
    p.add_argument("--label", required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--include-rules", action="store_true")
    args = p.parse_args(argv)

    paths = sorted((args.split_root / "rules").glob("*/oval.xml"))
    rows = [scan_rule(path) for path in paths]
    report = {
        "format": "scap-ng-authoring-oval-feature-census-0.1",
        "summary": aggregate(rows, args.label),
    }
    if args.include_rules:
        report["rules"] = rows
    args.output.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
