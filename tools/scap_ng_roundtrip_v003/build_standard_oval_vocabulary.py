#!/usr/bin/env python3
"""Generate a pinned standard OVAL Test/Object/State vocabulary manifest.

Input is an authoritative OVAL schema directory, normally an exact checkout of
OVAL-Community/OVAL tag v5.12.3. The output is intentionally small so offline
converters can distinguish standard OVAL vocabulary from local/publisher schema
extensions without carrying a second full schema tree.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import xml.etree.ElementTree as ET

XS="http://www.w3.org/2001/XMLSchema"

def local(tag):
    return tag.rsplit("}",1)[-1]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--schemas",type=Path,required=True)
    ap.add_argument("--version",default="5.12.3")
    ap.add_argument("--source",default="OVAL-Community/OVAL")
    ap.add_argument("--source-ref",default="v5.12.3")
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()

    rows=[]
    schema_files=[]
    for path in sorted(args.schemas.glob("*-definitions-schema.xsd")):
        root=ET.parse(path).getroot()
        target=root.get("targetNamespace") or ""
        schema_files.append(path.name)
        for child in list(root):
            if local(child.tag)!="element":
                continue
            name=child.get("name")
            if name and name.endswith(("_test","_object","_state")):
                rows.append({"namespace":target,"name":name})
    rows.sort(key=lambda x:(x["namespace"],x["name"]))
    doc={
        "format":"scap-ng-oval-standard-vocabulary-v1",
        "oval_version":args.version,
        "source_repository":args.source,
        "source_ref":args.source_ref,
        "schema_files":schema_files,
        "elements":rows,
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(doc,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"schemas":len(schema_files),"elements":len(rows)},indent=2))

if __name__=="__main__":
    main()
