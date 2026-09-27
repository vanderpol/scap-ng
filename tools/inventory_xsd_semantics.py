#!/usr/bin/env python3
"""Inventory XSD constructs for SCAP-NG migration research.

This tool does not attempt to convert XSD into the future SCAP-NG schema.
It creates a machine-readable inventory of schema constructs that must be
understood during migration research, with special attention to deprecation.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET

XSD = "{http://www.w3.org/2001/XMLSchema}"


def text_content(node: ET.Element) -> str:
    return " ".join(" ".join(node.itertext()).split())


def inventory_file(path: Path) -> dict:
    root = ET.parse(path).getroot()

    result = {
        "path": str(path),
        "target_namespace": root.get("targetNamespace"),
        "elements": [],
        "complex_types": [],
        "simple_types": [],
        "imports": [],
        "includes": [],
        "deprecated_annotations": [],
    }

    for node in root.iter():
        local = node.tag.rsplit("}", 1)[-1]

        if local == "element" and node.get("name"):
            result["elements"].append(
                {
                    "name": node.get("name"),
                    "type": node.get("type"),
                    "abstract": node.get("abstract"),
                    "substitution_group": node.get("substitutionGroup"),
                }
            )
        elif local == "complexType" and node.get("name"):
            result["complex_types"].append(node.get("name"))
        elif local == "simpleType" and node.get("name"):
            result["simple_types"].append(node.get("name"))
        elif local == "import":
            result["imports"].append(
                {
                    "namespace": node.get("namespace"),
                    "schema_location": node.get("schemaLocation"),
                }
            )
        elif local == "include":
            result["includes"].append(node.get("schemaLocation"))
        elif local in {"documentation", "appinfo"}:
            text = text_content(node)
            if "deprecat" in text.lower():
                result["deprecated_annotations"].append(text)

    result["counts"] = {
        "elements": len(result["elements"]),
        "complex_types": len(result["complex_types"]),
        "simple_types": len(result["simple_types"]),
        "deprecated_annotations": len(result["deprecated_annotations"]),
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("schema_root", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args()

    paths = sorted(args.schema_root.rglob("*.xsd"))
    files = []

    for path in paths:
        try:
            files.append(inventory_file(path))
        except ET.ParseError as exc:
            files.append({"path": str(path), "parse_error": str(exc)})

    report = {
        "schema_root": str(args.schema_root),
        "xsd_file_count": len(paths),
        "files": files,
        "totals": {
            "elements": sum(f.get("counts", {}).get("elements", 0) for f in files),
            "complex_types": sum(f.get("counts", {}).get("complex_types", 0) for f in files),
            "simple_types": sum(f.get("counts", {}).get("simple_types", 0) for f in files),
            "deprecated_annotations": sum(
                f.get("counts", {}).get("deprecated_annotations", 0) for f in files
            ),
        },
    }

    rendered = json.dumps(report, indent=2, sort_keys=True)

    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
