#!/usr/bin/env python3
"""Inventory OVAL definition complexity from a checked-out content tree.

This is a research heuristic, not an OVAL validator. It identifies candidate
definitions for manual review/prototyping by counting constructs that commonly
make migration or result explanation difficult.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET

FEATURES = {
    "set": {"set"},
    "filter": {"filter"},
    "local_variable": {"local_variable"},
    "external_variable": {"external_variable"},
    "object_component": {"object_component"},
    "arithmetic": {"arithmetic"},
    "regex_capture": {"regex_capture"},
    "concat": {"concat"},
    "substring": {"substring"},
    "split": {"split"},
    "time_difference": {"time_difference"},
    "extend_definition": {"extend_definition"},
}

ATTR_FEATURES = (
    "check",
    "check_existence",
    "var_check",
    "entity_check",
    "operator",
    "operation",
    "recurse_direction",
    "max_depth",
)


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def analyze(path: Path) -> dict:
    root = ET.parse(path).getroot()
    elems = list(root.iter())
    counts = {}

    for key, names in FEATURES.items():
        count = sum(1 for e in elems if local(e.tag) in names)
        if count:
            counts[key] = count

    criteria = [e for e in elems if local(e.tag) == "criteria"]
    criterion = [e for e in elems if local(e.tag) == "criterion"]

    attr_values = {}
    for attr in ATTR_FEATURES:
        values = {}
        for e in elems:
            if attr in e.attrib:
                value = e.attrib[attr]
                values[value] = values.get(value, 0) + 1
        if values:
            attr_values[attr] = values

    title = next(
        ((e.text or "").strip() for e in elems if local(e.tag) == "title"),
        "",
    )

    score = (
        len(criteria) * 2
        + len(criterion)
        + counts.get("set", 0) * 3
        + counts.get("filter", 0) * 2
        + counts.get("local_variable", 0) * 3
        + counts.get("external_variable", 0) * 4
        + counts.get("object_component", 0) * 4
        + counts.get("arithmetic", 0) * 4
        + counts.get("regex_capture", 0) * 3
        + counts.get("extend_definition", 0) * 3
    )

    if "OR" in attr_values.get("operator", {}):
        score += 5
    if "pattern match" in attr_values.get("operation", {}):
        score += 2
    if attr_values.get("check_existence"):
        score += 2
    if attr_values.get("var_check"):
        score += 3

    return {
        "path": str(path),
        "title": title,
        "bytes": path.stat().st_size,
        "score": score,
        "criteria": len(criteria),
        "criterion": len(criterion),
        "features": counts,
        "attributes": attr_values,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, help="Root of checked-out SCAP content tree")
    parser.add_argument("--top", type=int, default=100)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    paths = sorted(args.root.rglob("*-oval.xml"))
    rows = []
    for path in paths:
        try:
            rows.append(analyze(path))
        except ET.ParseError as exc:
            rows.append({"path": str(path), "parse_error": str(exc), "score": -1})

    rows.sort(key=lambda x: (x.get("score", -1), x.get("bytes", 0)), reverse=True)
    result = {
        "note": "Heuristic research inventory; high score means review first, not 'better' or 'worse' OVAL.",
        "files_scanned": len(paths),
        "results": rows[: args.top],
    }
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
