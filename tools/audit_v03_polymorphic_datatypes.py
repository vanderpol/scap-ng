#!/usr/bin/env python3
"""Inventory v0.3 fields whose collected Item types need extra semantic review.

Datatype resolution MUST follow generate_capability_schema.py: reviewed
field_datatypes overrides, otherwise the pinned OVAL 5.12.3 collected Item XSD.
An absent optional override is not a missing datatype.
"""
from __future__ import annotations

import argparse
import json
import xml.etree.ElementTree as ET
from pathlib import Path

from audit_capability_state_item_parity import (
    direct_global, infer_item_name, infer_sc_schema, payload_fields,
)
from generate_capability_schema import source_datatypes


def audit(mapping_dir: Path, *, repo_root: Path | None = None) -> dict:
    root = repo_root or Path(__file__).resolve().parents[1]
    results = []
    errors = []
    seen = set()
    cache = {}

    for path in sorted(mapping_dir.glob("*.json")):
        mapping = json.loads(path.read_text(encoding="utf-8"))
        cap = mapping.get("capability")
        if not isinstance(cap, str) or not cap:
            errors.append({"mapping": str(path), "reason": "missing capability identity"})
            continue
        if cap in seen:
            errors.append({"mapping": str(path), "reason": f"duplicate capability {cap}"})
        seen.add(cap)
        native = mapping.get("native") or {}
        fields = native.get("state_field_map") or {}
        overrides = native.get("field_datatypes") or {}
        enum_fields = native.get("state_value_enums") or {}
        if native.get("fixed_result") is not None:
            continue

        source = mapping.get("source") or {}
        try:
            sc_rel = source.get("system_characteristics_schema") or infer_sc_schema(
                source["definitions_schema"]
            )
            item_name = infer_item_name(mapping)
            key = (sc_rel, item_name)
            if key not in cache:
                xsd = ET.parse(root / sc_rel).getroot()
                item = direct_global(xsd, "element", item_name)
                if item is None:
                    raise ValueError(f"collected Item {item_name!r} missing from {sc_rel}")
                cache[key] = payload_fields(item)
            item_fields = cache[key]
        except (KeyError, ValueError, OSError, ET.ParseError) as exc:
            errors.append({"capability": cap, "reason": f"source Item unavailable: {exc}"})
            continue

        for source_field, native_field in sorted(fields.items()):
            if not isinstance(native_field, str) or not native_field:
                errors.append({"capability": cap, "field": source_field,
                               "reason": "invalid native State field mapping"})
                continue
            if source_field not in item_fields:
                errors.append({"capability": cap, "field": source_field,
                               "reason": "State mapping has no pinned collected Item field"})
                continue
            origin = "reviewed_override" if native_field in overrides else "oval_item_xsd"
            options = overrides.get(native_field)
            if options is None:
                options = source_datatypes(item_fields[source_field])
            if not isinstance(options, list) or not options or not all(
                isinstance(x, str) and x for x in options
            ):
                errors.append({"capability": cap, "field": native_field,
                               "reason": f"unresolved Item datatype from {origin}"})
                continue
            if len(set(options)) != len(options):
                errors.append({"capability": cap, "field": native_field,
                               "reason": "duplicate datatype entries"})
            if len(options) > 1:
                results.append({
                    "capability": cap, "field": native_field, "datatypes": options,
                    "datatype_source": origin, "source_item_field": source_field,
                    "has_value_enum": native_field in enum_fields,
                    "needs_semantic_review": True,
                })

        for field in sorted(set(overrides) - set(fields.values())):
            # Native-added fields are reviewed separately, not invented defaults.
            results.append({
                "capability": cap, "field": field, "datatypes": overrides[field],
                "collection_only_or_native_added": True, "needs_semantic_review": True,
            })

    return {
        "mapping_count": len(seen),
        "polymorphic_and_unmapped_fields": results,
        "review_count": len(results),
        "structural_errors": errors,
    }


def main():
    root = Path(__file__).resolve().parents[1]
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--mapping-dir", type=Path,
        default=root / "schema/v0.3.0/capability-mappings/supported",
    )
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    output = audit(args.mapping_dir, repo_root=root)
    if args.json:
        print(json.dumps(output, sort_keys=True, indent=2))
    else:
        print(
            f"mappings={output['mapping_count']} "
            f"flagged_fields={output['review_count']} "
            f"errors={len(output['structural_errors'])}"
        )
        for row in output["polymorphic_and_unmapped_fields"]:
            print(row["capability"], row["field"], row["datatypes"])
    if output["structural_errors"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
