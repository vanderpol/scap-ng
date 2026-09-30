#!/usr/bin/env python3
"""Audit OVAL 5.12.3 Test/Object/State type-reference consistency.

Checks exact qualified type identity (family namespace and stem), while
cataloging embedded per-Test Schematron type assertions separately.
This is an audit of source content, not a replacement for schema/Schematron
validation or a claim about scanner execution behavior.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys
from lxml import etree as ET

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
import scap14_rule_splitter as split

XSD = "http://www.w3.org/2001/XMLSchema"
SCH = "http://purl.oclc.org/dsdl/schematron"


def identity(node):
    uri, stem = ET.QName(node).namespace, ET.QName(node).localname
    return uri, stem.rsplit("_", 1)[0]


def audit_set_references(root, component_id=None):
    """Check the inherited same-Object-type constraint at every set depth.

    Unlike the upstream oval-def_setobjref Schematron pattern, which enumerates
    depths 1..3, this walk covers every nested set. It records source defects
    without rewriting or coercing any Object capability.
    """
    sections = {split.local(n.tag): n for n in root if isinstance(n.tag, str)}
    objects = {n.get("id"): n for n in sections.get("objects", [])
               if isinstance(n.tag, str) and n.get("id")}
    report = {"set_object_refs": 0, "mismatches": [], "missing_targets": []}
    for owner in objects.values():
        pending = [(n, 1) for n in owner if split.local(n.tag) == "set"]
        while pending:
            node, depth = pending.pop()
            for child in node:
                name = split.local(child.tag)
                if name == "set":
                    pending.append((child, depth + 1))
                elif name == "object_reference":
                    report["set_object_refs"] += 1
                    ref = (child.text or "").strip()
                    details = {"component": component_id, "object": owner.get("id"),
                               "reference": ref, "kind": "set_object",
                               "set_depth": depth}
                    target = objects.get(ref)
                    if target is None:
                        report["missing_targets"].append(details)
                    elif identity(target) != identity(owner):
                        report["mismatches"].append({
                            **details, "reason": "mismatched_type",
                            "expected_family": identity(owner)[0],
                            "expected_stem": identity(owner)[1],
                            "target_type": ET.QName(target).localname,
                            "target_family": ET.QName(target).namespace,
                        })
    return report


def audit_source(zip_file):
    _member, _data, stream = split.find_datastream(zip_file)
    components, _refs = split.embedded_components(stream)
    result = {
        "archive": str(zip_file),
        "oval_components": 0,
        "tests": 0,
        "object_refs": 0,
        "state_refs": 0,
        "set_object_refs": 0,
        "tests_without_object": [],
        "mismatches": [],
        "duplicate_id_components": [],
        "missing_targets": [],
    }
    for component_id, root in components.items():
        if split.component_kind(root) != "oval":
            continue
        result["oval_components"] += 1
        sections = {split.local(n.tag): n for n in root
                    if isinstance(n.tag, str)}
        index = {}
        for kind in ("tests", "objects", "states"):
            for element in sections.get(kind, []):
                if not isinstance(element.tag, str) or not element.get("id"):
                    continue
                key = element.get("id")
                if key in index:
                    result["duplicate_id_components"].append({
                        "component": component_id, "id": key})
                index[key] = (kind, element)
        set_audit = audit_set_references(root, component_id)
        result["set_object_refs"] += set_audit["set_object_refs"]
        result["mismatches"].extend(set_audit["mismatches"])
        result["missing_targets"].extend(set_audit["missing_targets"])
        for test in sections.get("tests", []):
            if not isinstance(test.tag, str):
                continue
            result["tests"] += 1
            test_name = ET.QName(test).localname
            if not test_name.endswith("_test"):
                result["mismatches"].append({
                    "component": component_id, "test": test.get("id"),
                    "reason": "non_test_type", "type": test_name})
                continue
            expected = identity(test)
            refs = []
            for child in test:
                if not isinstance(child.tag, str):
                    continue
                tag = ET.QName(child).localname
                if tag in ("object", "state"):
                    refs.append((tag, child.get(tag + "_ref")))
            if not any(kind == "object" for kind, _ in refs):
                result["tests_without_object"].append({
                    "component": component_id, "test": test.get("id"),
                    "test_type": test_name})
            for kind, ref in refs:
                result[kind + "_refs"] += 1
                target = index.get(ref)
                if target is None:
                    result["missing_targets"].append({
                        "component": component_id, "test": test.get("id"),
                        "reference": ref, "kind": kind})
                    continue
                actual_kind, element = target
                actual = identity(element)
                if actual_kind != kind + "s" or actual != expected:
                    result["mismatches"].append({
                        "component": component_id, "test": test.get("id"),
                        "test_type": test_name,
                        "kind": kind, "reference": ref,
                        "target_type": ET.QName(element).localname,
                        "target_family": ET.QName(element).namespace,
                        "expected_family": expected[0],
                        "expected_stem": expected[1],
                        "reason": ("wrong_section" if actual_kind != kind + "s"
                                   else "mismatched_type"),
                    })
    return result


def schema_constraints(schemas):
    test_types = []
    covered = []
    for path in sorted(Path(schemas).glob("*-definitions-schema.xsd")):
        root = ET.parse(str(path)).getroot()
        for element in root:
            if not isinstance(element.tag, str) or element.tag != "{" + XSD + "}element":
                continue
            name = element.get("name", "")
            if not name.endswith("_test"):
                continue
            assertions = []
            for rule in element.iter("{" + SCH + "}rule"):
                context = rule.get("context", "")
                if "/object" in context or ":object" in context or "/state" in context or ":state" in context:
                    assertions.extend([
                        {"context": context, "test": assertion.get("test"),
                         "message": " ".join("".join(assertion.itertext()).split())[:300]}
                        for assertion in rule.iter("{" + SCH + "}assert")
                    ])
            rec = {"schema": path.name, "test_type": name,
                   "has_typed_assertion": any(
                       "_object" in (a.get("test") or "")
                       or "_state" in (a.get("test") or "")
                       for a in assertions),
                   "assertion_count": len(assertions)}
            test_types.append(rec)
            if rec["has_typed_assertion"]:
                covered.append(rec)
    return {
        "test_type_count": len(test_types),
        "test_types_with_explicit_typed_schematron": len(covered),
        "tests_without_typed_schematron": [
            {"schema": t["schema"], "test_type": t["test_type"]}
            for t in test_types if not t["has_typed_assertion"]
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--schemas", required=True, type=Path)
    parser.add_argument("--source", required=True, type=Path, action="append")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--fail-on-mismatch", action="store_true")
    args = parser.parse_args()
    sources = [audit_source(p) for p in args.source]
    report = {
        "source_pin_required": True,
        "schema": schema_constraints(args.schemas),
        "sources": sources,
        "totals": {key: sum(row[key] for row in sources)
                   for key in ("oval_components", "tests",
                               "object_refs", "state_refs", "set_object_refs")},
        "issues": {
            "mismatched_type_references": sum(len(r["mismatches"]) for r in sources),
            "missing_targets": sum(len(r["missing_targets"]) for r in sources),
            "duplicate_ids": sum(len(r["duplicate_id_components"]) for r in sources),
            "tests_without_objects": sum(len(r["tests_without_object"]) for r in sources),
        },
        "scope": "Direct Test Object/State references and same-type Object references at every nested set depth. Filter typing, extended expressions and runtime evaluation remain separate conformance work.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "sources"},
                     indent=2))
    if args.fail_on_mismatch and any(report["issues"][k]
       for k in ("mismatched_type_references", "missing_targets", "duplicate_ids")):
        raise SystemExit("OVAL Test/Object/State typed references are inconsistent")


if __name__ == "__main__":
    main()
