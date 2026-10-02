#!/usr/bin/env python3
"""Audit reviewed capability mappings for OVAL Object/State/Item parity.

Invariant:
  Object fields MUST be a subset of State fields.
  State fields MUST align 1:1 with collected Item fields.

This reflects OVAL Set-filter semantics: any State may be used as a filter, so
anything a capability can collect must remain addressable by a State.

The audit is intentionally source-backed. It reads the pinned OVAL definitions
and system-characteristics schemas named by each capability mapping. Missing
source families are reported as hard failures rather than inferred.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET

XSD = "{http://www.w3.org/2001/XMLSchema}"

DTYPE_MAP = {
    "int": "integer",
    "ipv4_address": "ipv4",
    "ipv6_address": "ipv6",
    "evr_string": "rpm_evr",
    "debian_evr_string": "debian_evr",
}

KNOWN_TYPED_SUFFIXES = {
    "StringType": {"string"},
    "IntType": {"integer"},
    "BoolType": {"boolean"},
    "FloatType": {"float"},
    "VersionType": {"version"},
    "IPAddressStringType": {"string"},
    "BinaryType": {"binary"},
    "RecordType": {"record"},
}


def direct_global(root, kind, name):
    for child in root:
        if child.tag == XSD + kind and child.get("name") == name:
            return child
    return None


def restriction_values(node):
    values = []
    for child in node.iter():
        if child.tag == XSD + "enumeration" and child.get("value") is not None:
            values.append(child.get("value"))
    return values


def field_datatypes(element):
    typed = (element.get("type") or "").split(":")[-1]
    for suffix, values in KNOWN_TYPED_SUFFIXES.items():
        if typed.endswith(suffix):
            return set(values)

    for attr in element.iter():
        if attr.tag == XSD + "attribute" and attr.get("name") == "datatype":
            vals = restriction_values(attr)
            if vals:
                return {DTYPE_MAP.get(v, v) for v in vals}
            default = attr.get("default")
            if default:
                return {DTYPE_MAP.get(default, default)}

    # Unknown specialized entity types are compared by exact XSD type name
    # instead of silently treating them as strings.
    if typed:
        return {"xsd-type:" + typed}
    return {"unknown"}


def payload_fields(global_element):
    if global_element is None:
        return {}
    fields = {}
    for node in global_element.iter():
        if node.tag != XSD + "element" or not node.get("name"):
            continue
        name = node.get("name")
        # Skip the root global element itself.
        if node is global_element:
            continue
        fields.setdefault(name, node)
    return fields


def infer_sc_schema(definitions_schema: str) -> str:
    if "-definitions-schema.xsd" not in definitions_schema:
        raise ValueError(f"cannot infer system-characteristics schema from {definitions_schema}")
    return definitions_schema.replace(
        "-definitions-schema.xsd", "-system-characteristics-schema.xsd"
    )


def infer_item_name(mapping):
    source = mapping["source"]
    if source.get("item"):
        return source["item"]
    state = source.get("state")
    if not state or not state.endswith("_state"):
        raise ValueError(
            f"{mapping['capability']}: source.item required when source.state does not end in _state"
        )
    return state[:-6] + "_item"


def audit_mapping(mapping_path: Path, repo_root: Path):
    mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
    source = mapping.get("source", {})
    capability = mapping.get("capability", mapping_path.stem)

    definitions_rel = source.get("definitions_schema")
    if not definitions_rel:
        return {
            "capability": capability,
            "mapping": str(mapping_path.relative_to(repo_root)),
            "ok": False,
            "errors": ["missing source.definitions_schema"],
        }

    definitions_path = repo_root / definitions_rel
    sc_rel = source.get("system_characteristics_schema") or infer_sc_schema(definitions_rel)
    sc_path = repo_root / sc_rel

    errors = []
    details = {}

    if not definitions_path.exists():
        errors.append(f"missing definitions schema: {definitions_rel}")
        return {"capability": capability, "mapping": str(mapping_path.relative_to(repo_root)), "ok": False, "errors": errors}
    if not sc_path.exists():
        errors.append(f"missing system-characteristics schema: {sc_rel}")
        return {"capability": capability, "mapping": str(mapping_path.relative_to(repo_root)), "ok": False, "errors": errors}

    def_root = ET.parse(definitions_path).getroot()
    sc_root = ET.parse(sc_path).getroot()

    state_name = source.get("state")
    object_name = source.get("object")
    try:
        item_name = infer_item_name(mapping)
    except ValueError as exc:
        errors.append(str(exc))
        item_name = None

    state_el = direct_global(def_root, "element", state_name) if state_name else None
    object_el = direct_global(def_root, "element", object_name) if object_name else None
    item_el = direct_global(sc_root, "element", item_name) if item_name else None

    if state_name and state_el is None:
        errors.append(f"missing source State {state_name!r} in {definitions_rel}")
    if object_name and object_el is None:
        errors.append(f"missing source Object {object_name!r} in {definitions_rel}")
    if item_name and item_el is None:
        errors.append(f"missing source Item {item_name!r} in {sc_rel}")

    if state_el is None or item_el is None:
        return {
            "capability": capability,
            "mapping": str(mapping_path.relative_to(repo_root)),
            "ok": False,
            "errors": errors,
            "details": details,
        }

    state_fields = payload_fields(state_el)
    item_fields = payload_fields(item_el)
    object_fields = payload_fields(object_el) if object_el is not None else {}

    state_names = set(state_fields)
    item_names = set(item_fields)
    object_names = set(object_fields)

    only_state = sorted(state_names - item_names)
    only_item = sorted(item_names - state_names)
    object_not_state = sorted(object_names - state_names)

    if only_state:
        errors.append("State-only fields: " + ", ".join(only_state))
    if only_item:
        errors.append("Item-only fields: " + ", ".join(only_item))
    if object_not_state:
        errors.append("Object fields absent from State: " + ", ".join(object_not_state))

    datatype_mismatches = []
    for name in sorted(state_names & item_names):
        sdt = field_datatypes(state_fields[name])
        idt = field_datatypes(item_fields[name])
        if sdt != idt:
            datatype_mismatches.append({
                "field": name,
                "state": sorted(sdt),
                "item": sorted(idt),
            })

    if datatype_mismatches:
        errors.append(
            "State/Item datatype mismatches: "
            + ", ".join(row["field"] for row in datatype_mismatches)
        )

    details.update({
        "definitions_schema": definitions_rel,
        "system_characteristics_schema": sc_rel,
        "object": object_name,
        "state": state_name,
        "item": item_name,
        "object_fields": sorted(object_names),
        "state_fields": sorted(state_names),
        "item_fields": sorted(item_names),
        "datatype_mismatches": datatype_mismatches,
    })

    return {
        "capability": capability,
        "mapping": str(mapping_path.relative_to(repo_root)),
        "ok": not errors,
        "errors": errors,
        "details": details,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mapping-dir",
        type=Path,
        default=Path("schema/v0.1.0/capability-mappings"),
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = args.repo_root.resolve()
    mapping_dir = args.mapping_dir
    if not mapping_dir.is_absolute():
        mapping_dir = root / mapping_dir

    results = []
    for path in sorted(mapping_dir.glob("*.json")):
        results.append(audit_mapping(path, root))

    failures = [row for row in results if not row["ok"]]

    if args.json:
        print(json.dumps({
            "invariant": "Object fields subset State fields; State fields equal Item fields",
            "checked": len(results),
            "failures": len(failures),
            "results": results,
        }, indent=2, sort_keys=True))
    else:
        for row in results:
            status = "PASS" if row["ok"] else "FAIL"
            print(f"{status} {row['capability']}")
            for error in row["errors"]:
                print(f"  - {error}")
        print(f"checked={len(results)} failures={len(failures)}")

    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
