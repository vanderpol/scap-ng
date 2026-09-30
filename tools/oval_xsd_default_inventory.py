#!/usr/bin/env python3
"""Inventory XSD defaults and structural hazards without assuming runtime semantics.

Usage: python3 tools/oval_xsd_default_inventory.py path/to/schemas --output report.json
Reads local XSD files only. Does not resolve remote imports; flags them for review.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET

XSD = "{http://www.w3.org/2001/XMLSchema}"
ATTR_TAGS = {"attribute", "element"}
STRUCTURAL = {"restriction", "extension", "attributeGroup", "group", "any",
              "anyAttribute", "choice", "sequence", "all", "union", "list"}
FOCUS = ("check", "exist", "entity", "var_check", "behavior", "operator",
         "filter", "set", "datatype", "operation", "recurse", "filepath")

def local(tag):
    return tag.rsplit("}", 1)[-1]

def inventory(root: Path):
    files = sorted([root] if root.is_file() else root.rglob("*.xsd"))
    output = {"files": [], "declarations": [], "imports": [], "errors": []}
    for path in files:
        try:
            doc = ET.parse(path)
        except (ET.ParseError, OSError) as exc:
            output["errors"].append({"file": str(path), "error": str(exc)})
            continue
        root_node = doc.getroot()
        output["files"].append(str(path))
        target_ns = root_node.get("targetNamespace", "")
        def walk(node, ancestry):
            tag = local(node.tag)
            label = node.get("name") or node.get("ref") or node.get("base") or tag
            here = ancestry + [f"{tag}:{label}"]
            if tag in ("import", "include", "redefine", "override"):
                output["imports"].append({"file": str(path), "kind": tag,
                    "namespace": node.get("namespace"), "schemaLocation": node.get("schemaLocation")})
            if tag in ATTR_TAGS | STRUCTURAL:
                name = node.get("name", node.get("ref", ""))
                restrictions = []
                for child in node:
                    ct = local(child.tag)
                    if ct in ("enumeration", "pattern", "minInclusive",
                              "maxInclusive", "minLength", "maxLength", "length"):
                        restrictions.append({"kind": ct, "value": child.get("value")})
                documentation = [" ".join("".join(d.itertext()).split())
                    for d in node.iter() if d.tag == XSD + "documentation"]
                fields = {k: node.get(k) for k in ("default", "fixed", "use",
                    "minOccurs", "maxOccurs", "type", "ref", "base",
                    "substitutionGroup", "nillable") if node.get(k) is not None}
                flagged = any(word in (name + " " + label).lower() for word in FOCUS)
                if fields or restrictions or documentation or flagged:
                    output["declarations"].append({"file": str(path),
                        "targetNamespace": target_ns, "path": "/".join(here),
                        "kind": tag, "name": name, "attributes": fields,
                        "restrictions": restrictions,
                        "documentation": documentation,
                        "focus": flagged})
            for child in node:
                walk(child, here)
        walk(root_node, [])
    output["summary"] = {"parsed_files": len(output["files"]),
        "declarations": len(output["declarations"]),
        "explicit_defaults": sum("default" in x["attributes"] for x in output["declarations"]),
        "fixed_values": sum("fixed" in x["attributes"] for x in output["declarations"]),
        "import_links": len(output["imports"]),
        "errors": len(output["errors"])}
    return output

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("schema_root", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = inventory(args.schema_root)
    rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    if result["errors"]:
        raise SystemExit(2)

if __name__ == "__main__":
    main()
