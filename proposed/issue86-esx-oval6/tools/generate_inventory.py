#!/usr/bin/env python3
"""Derive the OVAL 6.0 ESX family inventory from the pinned XSD bytes.

This is design-only tooling. It does not infer native capability behavior or
claim that an RI can collect any field. The source XSDs are vendored next to
this script with their upstream commit and hashes recorded in the receipt.
"""
from __future__ import annotations

import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source"
OUT = ROOT / "schema-inventory.json"
CROSSWALK = ROOT / "capability-crosswalk.json"
XS = "http://www.w3.org/2001/XMLSchema"
Q = "{" + XS + "}"


def text(node: ET.Element | None) -> str:
    return " ".join("".join(node.itertext()).split()) if node is not None else ""


def documentation(node: ET.Element) -> str:
    return text(node.find(f"{Q}annotation/{Q}documentation") if node is not None else None)


def child_fields(root: ET.Element, element_name: str) -> list[dict[str, Any]]:
    element = next(e for e in root.findall(f"{Q}element") if e.get("name") == element_name)
    sequence = element.find(f"{Q}complexType/{Q}complexContent/{Q}extension/{Q}sequence")
    if sequence is None:
        return []
    fields = []
    for child in sequence.findall(f"{Q}element"):
        field: dict[str, Any] = {
            "name": child.get("name") or child.get("ref"),
            "ref": child.get("ref"),
            "type": child.get("type"),
            "min_occurs": child.get("minOccurs", "1"),
            "max_occurs": child.get("maxOccurs", "1"),
            "documentation": documentation(child),
        }
        fields.append(field)
    return fields


def enums(root: ET.Element) -> list[dict[str, Any]]:
    result = []
    for owner in root.iter(f"{Q}complexType"):
        for restriction in owner.iter(f"{Q}restriction"):
            values = [e.get("value") for e in restriction.findall(f"{Q}enumeration")]
            if values:
                result.append({"name": owner.get("name"), "base": restriction.get("base"), "values": values, "documentation": documentation(owner)})
    return result

def constraints(root: ET.Element) -> list[dict[str, Any]]:
    result = []
    for owner in root.iter(f"{Q}complexType"):
        for restriction in owner.iter(f"{Q}restriction"):
            for child in restriction:
                if child.tag != f"{Q}enumeration":
                    result.append({"simple_type": owner.get("name"), "kind": child.tag.rsplit("}", 1)[-1], "value": dict(child.attrib)})
    return result

def main() -> None:
    defs_path = SOURCE / "esx-definitions-schema.xsd"
    chars_path = SOURCE / "esx-system-characteristics-schema.xsd"
    defs = ET.parse(defs_path).getroot()
    chars = ET.parse(chars_path).getroot()
    tests = {e.get("name")[:-5]: e.get("name") for e in defs.findall(f"{Q}element") if (e.get("name") or "").endswith("_test")}
    families = []
    for stem, test_name in sorted(tests.items()):
        object_name, state_name, item_name = f"{stem}_object", f"{stem}_state", f"{stem}_item"
        test = next(e for e in defs.findall(f"{Q}element") if e.get("name") == test_name)
        families.append({
            "family": stem,
            "test": {"name": test_name, "substitution_group": test.get("substitutionGroup"), "documentation": documentation(test), "fields": child_fields(defs, test_name)},
            "object": {"name": object_name, "fields": child_fields(defs, object_name)},
            "state": {"name": state_name, "fields": child_fields(defs, state_name)},
            "item": {"name": item_name, "fields": child_fields(chars, item_name)},
        })
    all_enums = [{"schema": "esx-definitions-schema.xsd", **e} for e in enums(defs)] + [{"schema": "esx-system-characteristics-schema.xsd", **e} for e in enums(chars)]
    all_constraints = [{"schema": "esx-definitions-schema.xsd", **c} for c in constraints(defs)] + [{"schema": "esx-system-characteristics-schema.xsd", **c} for c in constraints(chars)]
    for family in families:
        for component in ("test", "object", "state", "item"):
            for field in family[component]["fields"]:
                all_constraints.extend([
                    {"schema": "esx-definitions-schema.xsd" if component != "item" else "esx-system-characteristics-schema.xsd", "family": family["family"], "component": component, "field": field["name"], "kind": "minOccurs", "value": field["min_occurs"]},
                    {"schema": "esx-definitions-schema.xsd" if component != "item" else "esx-system-characteristics-schema.xsd", "family": family["family"], "component": component, "field": field["name"], "kind": "maxOccurs", "value": field["max_occurs"]},
                ])
    hashes = {}
    for path in (defs_path, chars_path):
        hashes[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    result = {
        "format": "scap-ng-proposed-oval6-esx-inventory-0.1",
        "issue": 86,
        "status": "proposed-0.5.0",
        "source": {"repository": "OVAL-Community/OVAL", "release_tag": "v6.0", "commit": "5afcf590fb5d334687bfdc47f98716424cdb7f3d", "definitions_namespace": defs.get("targetNamespace"), "system_characteristics_namespace": chars.get("targetNamespace"), "schema_files_sha256": hashes},
        "families": families,
        "enumerations": all_enums,
        "constraints": all_constraints,
        "counts": {"test_families": len(families), "test_elements": len(families), "object_elements": len(families), "state_elements": len(families), "item_elements": len(families), "object_fields": sum(len(f["object"]["fields"]) for f in families), "state_fields": sum(len(f["state"]["fields"]) for f in families), "item_fields": sum(len(f["item"]["fields"]) for f in families), "enumerations": len(all_enums), "constraints": len(all_constraints)},
        "coverage_policy": "Every source-defined ESX Test/Object/State/Item family is listed. Mapping, collection, evaluation, and STIG applicability remain separate decisions.",
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    crosswalk = {
        "format": "scap-ng-proposed-oval6-esx-crosswalk-0.1",
        "issue": 86,
        "status": "proposed-0.5.0",
        "source": result["source"],
        "mapping_policy": "Capability names are generic XSD-derived families; no PowerCLI or STIG identifier is part of capability behavior.",
        "families": [
            {
                "capability": f"esx.{family['family']}",
                "source": {"test": family["test"]["name"], "object": family["object"]["name"], "state": family["state"]["name"], "item": family["item"]["name"]},
                "assessment": {"test": "assessment.tests.<id>", "object": "assessment.tests.<id>.object", "require": "assessment.tests.<id>.require.fields", "item": "evidence.items[].fields"},
                "object_fields": [f for f in family["object"]["fields"] if f["name"] != "oval-def:filter"],
                "state_fields": family["state"]["fields"],
                "item_fields": family["item"]["fields"],
                "converter": "gap", "ri": "govmomi-design-only", "editor": "proposed-schema-only", "qualification": "untested"
            } for family in families
        ],
        "deprecated_5_12_3_esx_families": ["patch56_test", "patch_test", "version_test", "visdkmanagedobject_test"],
        "deprecated_policy": "Reject as deprecated_source_construct; never alias or version-spoof into a 6.0 capability.",
    }
    CROSSWALK.write_text(json.dumps(crosswalk, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["counts"], indent=2))


if __name__ == "__main__":
    main()
