#!/usr/bin/env python3
"""Inventory OVAL 5.12.3 repeatable collected-Item fields for SCAP-NG v0.3.

Source backed: reports XSD maxOccurs for the exact mapped OVAL Item fields.
Does NOT assume repeatable collected fields are correctly serialized/evaluated.
"""
from __future__ import annotations
import argparse
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from audit_capability_state_item_parity import (
    direct_global, infer_sc_schema, infer_item_name, payload_fields
)


def audit(root: Path, mapping_dir: Path) -> dict:
    entries=[]
    failures=[]
    checked=0
    for file in sorted(mapping_dir.glob("*.json")):
        mapping=json.loads(file.read_text(encoding="utf-8"))
        cap=mapping.get("capability",file.stem)
        src=mapping.get("source") or {}
        if (mapping.get("native") or {}).get("fixed_result") is not None:
            continue
        defs=src.get("definitions_schema")
        if not defs:
            failures.append({"capability":cap,"reason":"missing OVAL source schema"})
            continue
        item_path=root / (src.get("system_characteristics_schema") or infer_sc_schema(defs))
        if not item_path.exists():
            failures.append({"capability":cap,"reason":f"missing {item_path}"})
            continue
        try:
            root_xsd=ET.parse(item_path).getroot()
            item_name=infer_item_name(mapping)
            el=direct_global(root_xsd,"element",item_name)
            if el is None:
                failures.append({"capability":cap,"reason":f"source Item {item_name} not found"})
                continue
            fields=payload_fields(el)
            checked+=1
            translated=(mapping.get("native") or {}).get("state_field_map") or {}
            for source_field,node in sorted(fields.items()):
                count=node.get("maxOccurs","1")
                if count=="1":
                    continue
                entries.append({
                    "capability":cap,
                    "source_item":item_name,
                    "source_field":source_field,
                    "native_state_field":translated.get(source_field),
                    "min_occurs":node.get("minOccurs","1"),
                    "max_occurs":count,
                    "source_schema":str(item_path.relative_to(root)),
                    "requires_item_cardinality_review":True,
                })
        except (ValueError,TypeError,ET.ParseError) as ex:
            failures.append({"capability":cap,"reason":str(ex)})
    return {"checked_source_items":checked,"repeatable_fields":entries,
            "repeatable_count":len(entries),"failures":failures}


def main():
    ap=argparse.ArgumentParser()
    root=Path(__file__).resolve().parents[1]
    ap.add_argument("--repo-root",type=Path,default=root)
    ap.add_argument("--mapping-dir",type=Path,default=Path("schema/v0.3.0/capability-mappings/supported"))
    ap.add_argument("--json",action="store_true")
    args=ap.parse_args()
    repo=args.repo_root.resolve()
    directory=args.mapping_dir if args.mapping_dir.is_absolute() else repo / args.mapping_dir
    result=audit(repo,directory)
    if args.json:
        print(json.dumps(result,indent=2,sort_keys=True))
    else:
        print(f"items={result['checked_source_items']} repeatable_fields={result['repeatable_count']} errors={len(result['failures'])}")
    if result["failures"]:
        raise SystemExit(1)


if __name__=="__main__":
    main()
