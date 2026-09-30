#!/usr/bin/env python3
"""Extract every embedded OVAL Definitions component from a SCAP source ZIP."""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path
from lxml import etree

ROOT=Path(__file__).resolve().parents[2]
TOOLS=ROOT/"tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0,str(TOOLS))

from scap14_rule_splitter import find_datastream, embedded_components, component_kind

def safe(value):
    return re.sub(r"[^A-Za-z0-9_.-]+","_",value).strip("_") or "oval"

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("source_zip",type=Path)
    ap.add_argument("--output-dir",type=Path,required=True)
    ap.add_argument("--manifest",type=Path)
    args=ap.parse_args()

    member,data,root=find_datastream(args.source_zip)
    components,_=embedded_components(root)
    args.output_dir.mkdir(parents=True,exist_ok=True)
    rows=[]
    for cid,component in sorted(components.items()):
        if component_kind(component)!="oval":
            continue
        path=args.output_dir/(safe(cid)+".xml")
        path.write_bytes(etree.tostring(
            component,xml_declaration=True,encoding="UTF-8",pretty_print=True
        ))
        definitions=sum(
            1 for n in component.iter()
            if etree.QName(n.tag).localname=="definition"
        )
        rows.append({"component_id":cid,"path":path.as_posix(),"definitions":definitions})

    manifest={
        "source_zip":args.source_zip.as_posix(),
        "datastream_member":member,
        "oval_components":rows,
        "component_count":len(rows),
        "definition_count":sum(x["definitions"] for x in rows),
    }
    if args.manifest:
        args.manifest.parent.mkdir(parents=True,exist_ok=True)
        args.manifest.write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(manifest,indent=2,sort_keys=True))
    return 1 if not rows else 0

if __name__=="__main__":
    raise SystemExit(main())
