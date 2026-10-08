#!/usr/bin/env python3
"""Inventory type-ambiguous v0.3 capability fields; flag for semantic review.

This is a TRIAGE report, not proof that a field is incorrect. Runtime type
identity, Item encoding, and conditional field constraints need separate tests.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path


def audit(mapping_dir: Path) -> dict:
    results=[]
    errors=[]
    seen=set()
    for path in sorted(mapping_dir.glob("*.json")):
        mapping=json.loads(path.read_text(encoding="utf-8"))
        cap=mapping.get("capability")
        if not isinstance(cap,str) or not cap:
            errors.append({"mapping":str(path),"reason":"missing capability identity"})
            continue
        if cap in seen:
            errors.append({"mapping":str(path),"reason":f"duplicate capability {cap}"})
        seen.add(cap)
        native=mapping.get("native") or {}
        fields=native.get("state_field_map") or {}
        datatypes=native.get("field_datatypes") or {}
        enum_fields=native.get("state_value_enums") or {}
        for source,named in sorted(fields.items()):
            if not isinstance(named,str) or not named:
                errors.append({"capability":cap,"field":source,"reason":"invalid native state field"})
                continue
            options=datatypes.get(named)
            if not isinstance(options,list) or not options or not all(isinstance(x,str) for x in options):
                errors.append({"capability":cap,"field":named,"reason":"native state field lacks datatype list"})
                continue
            if len(set(options))!=len(options):
                errors.append({"capability":cap,"field":named,"reason":"duplicate datatype enumerations"})
            if len(options)>1:
                results.append({"capability":cap,"field":named,"datatypes":options,
                                "has_value_enum":named in enum_fields,
                                "needs_semantic_review":True})
        for field in sorted(set(datatypes)-set(fields.values())):
            # Some collection-only fields can be justified; identify, don't error.
            results.append({"capability":cap,"field":field,"datatypes":datatypes[field],
                            "collection_only_or_unmapped":True,
                            "needs_semantic_review":True})
    return {"mapping_count":len(seen),"polymorphic_and_unmapped_fields":results,
            "review_count":len(results),"structural_errors":errors}


def main():
    root=Path(__file__).resolve().parents[1]
    ap=argparse.ArgumentParser()
    ap.add_argument("--mapping-dir",type=Path,default=root/"schema/v0.3.0/capability-mappings/supported")
    ap.add_argument("--json",action="store_true")
    args=ap.parse_args()
    output=audit(args.mapping_dir)
    if args.json:
        print(json.dumps(output,sort_keys=True,indent=2))
    else:
        print(f"mappings={output['mapping_count']} flagged_fields={output['review_count']} errors={len(output['structural_errors'])}")
        for x in output["polymorphic_and_unmapped_fields"]:
            print(x["capability"],x["field"],x["datatypes"])
    if output["structural_errors"]:
        raise SystemExit(1)


if __name__=="__main__":
    main()
