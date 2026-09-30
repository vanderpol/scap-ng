#!/usr/bin/env python3
"""Conformance gate for SCAP-NG v003 OVAL lowering.

The preferred mode runs every XML document in the SCAP 1.4 Self-Assertion
OVAL_Test_Content tree. A small network-backed agnostic subset remains available
for local smoke testing when the corpus is not checked out.

This is a conversion gate, not a serialization-equivalence claim. It proves that
native SCAP-NG lowering either represents a definition cleanly or reports the
exact unsupported feature instead of silently dropping semantics.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import urllib.request
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from scap_upconvert_v003.build_rhel9_review_slice import (
    local,
    lower_definition,
    semantic_id,
    unsupported_definition_features,
)
from scap_upconvert_v003.cleanliness import assert_native_clean

BASE = (
    "https://raw.githubusercontent.com/OVAL-Community/SCAP-Self-Assertion/"
    "main/SCAP_1.4/OVAL_Test_Content/agnostic/"
)

SMOKE_FILES = [
    "ind-def_variable_test.xml",
    "oval-def_arithmetic_function.xml",
    "oval-def_begin_function.xml",
    "oval-def_concat_function.xml",
    "oval-def_constant_variable.xml",
    "oval-def_end_function.xml",
    "oval-def_escape_regex_function.xml",
    "oval-def_literal_component.xml",
    "oval-def_local_variable.xml",
    "oval-def_merge.xml",
    "oval-def_object_component.xml",
    "oval-def_regex_capture_function.xml",
    "oval-def_split_function.xml",
    "oval-def_substring_function.xml",
    "oval-def_time_difference_function.xml",
    "oval-def_variable_component.xml",
    "oval_check_enumeration_variable_values.xml",
]

def fetch_xml(name: str) -> ET.Element:
    request = urllib.request.Request(
        BASE + name,
        headers={"User-Agent": "scap-ng-v003-self-assertion"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return ET.fromstring(response.read())

def parse_xml(path: Path) -> ET.Element:
    return ET.parse(path).getroot()

def definition_nodes(root: ET.Element):
    return [
        node for node in root.iter()
        if local(node.tag) == "definition" and node.get("id")
    ]

def corpus_files(root: Path):
    return sorted(
        path for path in root.rglob("*.xml")
        if path.is_file()
    )

def known_ids(root: ET.Element):
    return {
        node.get("id")
        for node in root.iter()
        if node.get("id")
    }

def ref_targets(node: ET.Element, ids: set[str]):
    out = set()
    for item in node.iter():
        for value in item.attrib.values():
            if value in ids:
                out.add(value)
        text = (item.text or "").strip()
        if text in ids:
            out.add(text)
    return out

def dependency_depth(root: ET.Element, definition_id: str):
    by_id = {
        node.get("id"): node
        for node in root.iter()
        if node.get("id")
    }
    ids = set(by_id)
    graph = {
        node_id: ref_targets(node, ids) - {node_id}
        for node_id, node in by_id.items()
    }

    memo = {}
    visiting = set()

    def walk(node_id: str):
        if node_id in memo:
            return memo[node_id]
        if node_id in visiting:
            return (0, [node_id, "<cycle>"])
        visiting.add(node_id)
        best_depth = 0
        best_path = [node_id]
        for target in sorted(graph.get(node_id, ())):
            depth, path = walk(target)
            if 1 + depth > best_depth:
                best_depth = 1 + depth
                best_path = [node_id] + path
        visiting.remove(node_id)
        memo[node_id] = (best_depth, best_path)
        return memo[node_id]

    return walk(definition_id)

def run_document(label: str, root: ET.Element):
    failures = []
    converted = 0
    definitions = definition_nodes(root)
    max_depth = 0
    deepest_path = []

    for definition in definitions:
        definition_id = definition.get("id")
        depth, path = dependency_depth(root, definition_id)
        if depth > max_depth:
            max_depth = depth
            deepest_path = path

        unsupported = unsupported_definition_features(root, definition_id)
        assessment_id = "self-assertion." + semantic_id(definition_id, "definition")
        assessment, error = lower_definition(root, definition_id, assessment_id)

        problems = []
        if unsupported:
            problems.append({"unsupported_features": unsupported})
        if assessment is None:
            problems.append({"lowering_error": error})

        if assessment is not None:
            try:
                assert_native_clean(assessment)
            except Exception as exc:
                problems.append({"cleanliness_error": str(exc)})

        if problems:
            failures.append(
                {
                    "file": label,
                    "definition_id": definition_id,
                    "dependency_depth": depth,
                    "dependency_path": path,
                    "problems": problems,
                }
            )
        else:
            converted += 1

    return {
        "file": label,
        "definitions": len(definitions),
        "converted": converted,
        "failures": len(failures),
        "max_dependency_depth": max_depth,
        "deepest_dependency_path": deepest_path,
        "failure_details": failures,
    }

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--corpus",
        type=Path,
        help="Path to SCAP_1.4/OVAL_Test_Content; when omitted, run the network smoke subset.",
    )
    ap.add_argument("--output", type=Path)
    ap.add_argument(
        "--inventory-only",
        action="store_true",
        help="Always return success while still reporting every conversion failure.",
    )
    args = ap.parse_args()

    results = []
    parse_failures = []

    if args.corpus:
        files = corpus_files(args.corpus)
        for path in files:
            label = str(path.relative_to(args.corpus))
            try:
                root = parse_xml(path)
            except Exception as exc:
                parse_failures.append({"file": label, "error": str(exc)})
                continue
            results.append(run_document(label, root))
    else:
        for name in SMOKE_FILES:
            try:
                root = fetch_xml(name)
            except Exception as exc:
                parse_failures.append({"file": name, "error": str(exc)})
                continue
            results.append(run_document(name, root))

    failures = [
        failure
        for result in results
        for failure in result["failure_details"]
    ]
    converted = sum(result["converted"] for result in results)
    definitions = sum(result["definitions"] for result in results)
    deepest = max(results, key=lambda r: r["max_dependency_depth"], default=None)

    report = {
        "mode": "full-corpus" if args.corpus else "smoke-subset",
        "files": len(results),
        "parse_failures": parse_failures,
        "definitions": definitions,
        "definitions_converted": converted,
        "definition_failures": len(failures),
        "max_dependency_depth": deepest["max_dependency_depth"] if deepest else 0,
        "deepest_dependency_file": deepest["file"] if deepest else None,
        "deepest_dependency_path": deepest["deepest_dependency_path"] if deepest else [],
        "per_file": [
            {k: v for k, v in result.items() if k != "failure_details"}
            for result in results
        ],
        "failure_details": failures,
    }

    payload = json.dumps(report, indent=2, sort_keys=True)
    print(payload)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")

    if args.inventory_only:
        return 0
    if parse_failures or failures:
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
