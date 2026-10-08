#!/usr/bin/env python3
"""Reject deprecated OVAL entities still selected by a supported 0.3 mapping.

The XSD remains a historical reference. A deprecated source State or Item
entity SHALL NOT be emitted as a native SCAP-NG 0.3 mapping.
"""
from __future__ import annotations

import argparse
import json
import xml.etree.ElementTree as ET
from pathlib import Path

from audit_capability_state_item_parity import (
    infer_sc_schema, infer_item_name, is_deprecated,
)
from generate_capability_schema import direct_global, immediate_payload_elements


def audit(root: Path, mapping_dir: Path) -> dict:
    checked = 0
    mapped_fields = 0
    violations = []
    cache = {}

    def get_fields(path: Path, name: str):
        key = (path, name)
        if key not in cache:
            xsd = ET.parse(path).getroot()
            global_item = direct_global(xsd, "element", name)
            cache[key] = immediate_payload_elements(global_item)
        return cache[key]

    for path in sorted(mapping_dir.glob("*.json")):
        mapping = json.loads(path.read_text(encoding="utf-8"))
        capability = mapping.get("capability", path.stem)
        native = mapping.get("native", {})
        source = mapping.get("source", {})
        checked += 1
        if native.get("fixed_result") is not None:
            continue

        try:
            defs = root / source["definitions_schema"]
            items = root / (source.get("system_characteristics_schema") or
                            infer_sc_schema(source["definitions_schema"]))
            state_fields = get_fields(defs, source["state"])
            item_fields = get_fields(items, infer_item_name(mapping))
        except (ET.ParseError, OSError, KeyError, ValueError) as exc:
            violations.append({"capability": capability, "reason": f"cannot audit source: {exc}"})
            continue

        for source_field, native_field in sorted(native.get("state_field_map", {}).items()):
            mapped_fields += 1
            state = state_fields.get(source_field)
            item = item_fields.get(source_field)
            for origin, node in (("State", state), ("Item", item)):
                if node is None:
                    violations.append({
                        "capability": capability, "field": source_field,
                        "reason": f"mapped field missing from OVAL {origin}",
                    })
                elif is_deprecated(node):
                    violations.append({
                        "capability": capability, "field": source_field,
                        "native_field": native_field,
                        "reason": f"mapped deprecated OVAL {origin} field",
                    })

    return {"mappings": checked, "mapped_fields": mapped_fields,
            "violations": violations, "failure_count": len(violations)}


def main():
    root = Path(__file__).resolve().parents[1]
    p = argparse.ArgumentParser()
    p.add_argument("--mapping-dir", type=Path, default=
                   root / "schema/v0.3.0/capability-mappings/supported")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    out = audit(root, args.mapping_dir)
    if args.json:
        print(json.dumps(out, indent=2, sort_keys=True))
    else:
        print(f"mappings={out['mappings']} mapped_fields={out['mapped_fields']} violations={out['failure_count']}")
        for issue in out["violations"]:
            print(issue)
    if out["violations"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
