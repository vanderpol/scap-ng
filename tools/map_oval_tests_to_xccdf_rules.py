#!/usr/bin/env python3
import argparse, json, zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

def local(tag):
    return tag.split("}",1)[-1] if isinstance(tag,str) else ""

def iter_xml(zip_path):
    with zipfile.ZipFile(zip_path) as z:
        for name in z.namelist():
            if name.lower().endswith(".xml"):
                try:
                    yield name, ET.fromstring(z.read(name))
                except ET.ParseError:
                    pass

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("package", type=Path)
    ap.add_argument("--test", action="append", default=[])
    ap.add_argument("--output", type=Path, required=True)
    args=ap.parse_args()

    defs_by_test={}
    parent_defs={}
    rules=[]
    for name,root in iter_xml(args.package):
        for node in root.iter():
            if local(node.tag)=="definition" and node.get("id"):
                did=node.get("id")
                for child in node.iter():
                    if local(child.tag)=="criterion" and child.get("test_ref"):
                        defs_by_test.setdefault(child.get("test_ref"),set()).add(did)
                    elif local(child.tag)=="extend_definition" and child.get("definition_ref"):
                        parent_defs.setdefault(child.get("definition_ref"),set()).add(did)
            elif local(node.tag)=="Rule":
                rid=node.get("id")
                title=next(((x.text or "").strip() for x in node if local(x.tag)=="title"),"")
                refs=[]
                for check in node:
                    if local(check.tag)!="check": continue
                    for ref in check:
                        if local(ref.tag)=="check-content-ref" and ref.get("name"):
                            refs.append(ref.get("name"))
                rules.append({"id":rid,"title":title,"definition_refs":refs})

    out=[]
    for test in args.test:
        direct=set(defs_by_test.get(test,set()))
        reachable=set(direct)
        queue=list(direct)
        while queue:
            child=queue.pop()
            for parent in parent_defs.get(child,set()):
                if parent not in reachable:
                    reachable.add(parent)
                    queue.append(parent)
        defs=sorted(reachable)
        matched=[r for r in rules if any(d in r["definition_refs"] for d in reachable)]
        out.append({
            "test_id":test,
            "direct_definitions":sorted(direct),
            "definitions":defs,
            "rules":matched,
        })
    args.output.write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps(out,indent=2))

if __name__=="__main__":
    main()
