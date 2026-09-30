#!/usr/bin/env python3
"""Round-trip one complete OVAL document through native SCAP-NG assessments.

Every source Definition is lowered independently (matching split SCAP-NG
assessment architecture), regenerated with its full dependency closure, assigned
globally unique OVAL IDs, and merged into one OVAL document. Each source root is
then compared semantically against its regenerated root in the aggregate output.

This intentionally does not deduplicate closures yet. Aggregate dedup/reuse is a
separate gate so unrelated native-local identifiers cannot collide.
"""
from __future__ import annotations

import argparse, json, re, sys
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
TOOLS=ROOT/"tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0,str(TOOLS))

from scap_upconvert_v003.build_rhel9_review_slice import (
    local, lower_definition, semantic_id, unsupported_definition_features,
)
from scap_upconvert_v003.cleanliness import assert_native_clean
from scap_ng_roundtrip_v003.native_assessment_to_oval import build as reverse_build, OD, OC, q
from scap_ng_roundtrip_v003.compare_oval_semantics import compare

ID_RE=re.compile(r"^oval:[A-Za-z0-9_.-]+:(?:def|tst|obj|ste|var):[A-Za-z0-9_.-]+$")

def definitions(root):
    return [n for n in root.iter() if local(n.tag)=="definition" and n.get("id")]

def remap_document(tree,index):
    root=tree.getroot()
    mapping={}
    serial={"def":0,"tst":0,"obj":0,"ste":0,"var":0}
    for node in root.iter():
        old=node.get("id")
        if not old or not ID_RE.match(old):
            continue
        kind=old.rsplit(":",2)[-2]
        serial[kind]+=1
        mapping[old]=f"oval:scap-ng.aggregate.{index}:{kind}:{serial[kind]}"

    for node in root.iter():
        for key,value in list(node.attrib.items()):
            if value in mapping:
                node.set(key,mapping[value])
        if node.text:
            value=node.text.strip()
            if value in mapping and node.text.strip()==value:
                node.text=mapping[value]
    return mapping

def ensure_sections(root):
    sections={}
    for name in ("definitions","tests","objects","states","variables"):
        node=ET.SubElement(root,q(OD,name))
        sections[name]=node
    return sections

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("source",type=Path)
    ap.add_argument("-o","--output",type=Path,required=True)
    ap.add_argument("--report",type=Path,required=True)
    ap.add_argument("--native-dir",type=Path)
    ap.add_argument("--inventory-only",action="store_true")
    args=ap.parse_args()

    source_root=ET.parse(args.source).getroot()
    aggregate=ET.Element(q(OD,"oval_definitions"))
    gen=ET.SubElement(aggregate,q(OD,"generator"))
    ET.SubElement(gen,q(OC,"product_name")).text="SCAP-NG aggregate round-trip generator"
    ET.SubElement(gen,q(OC,"schema_version")).text="5.12.3"
    ET.SubElement(gen,q(OC,"timestamp")).text="2026-09-30T00:00:00Z"
    sections=ensure_sections(aggregate)

    rows=[]
    root_map={}
    if args.native_dir:
        args.native_dir.mkdir(parents=True,exist_ok=True)

    for index,definition in enumerate(definitions(source_root),1):
        did=definition.get("id")
        row={"definition_id":did}
        unsupported=unsupported_definition_features(source_root,did)
        if unsupported:
            row.update(stage="lower",unsupported_features=unsupported)
            rows.append(row); continue
        native,error=lower_definition(
            source_root,did,
            "aggregate."+semantic_id(did,f"definition-{index}")
        )
        if native is None:
            row.update(stage="lower",error=error); rows.append(row); continue
        try:
            assert_native_clean(native)
            tree,regen_root=reverse_build(native)
        except Exception as exc:
            row.update(stage="reverse",error=str(exc)); rows.append(row); continue

        if args.native_dir:
            (args.native_dir/f"{index:04d}.json").write_text(
                json.dumps(native,indent=2,sort_keys=True)+"\n",encoding="utf-8"
            )

        mapping=remap_document(tree,index)
        regen_root=mapping[regen_root]
        root_map[did]=regen_root
        rroot=tree.getroot()
        for section_name in sections:
            source_section=rroot.find(q(OD,section_name))
            if source_section is not None:
                for child in list(source_section):
                    sections[section_name].append(child)
        row.update(stage="merged",regenerated_definition_id=regen_root)
        rows.append(row)

    for name,node in list(sections.items()):
        if len(node)==0:
            aggregate.remove(node)

    tree=ET.ElementTree(aggregate)
    ET.indent(tree,space="  ")
    args.output.parent.mkdir(parents=True,exist_ok=True)
    tree.write(args.output,encoding="utf-8",xml_declaration=True)

    equal=0
    for row in rows:
        did=row["definition_id"]
        rid=root_map.get(did)
        if not rid:
            continue
        try:
            result=compare(
                args.source,args.output,
                source_root=did,regenerated_root=rid,root_only=True
            )
        except Exception as exc:
            row.update(stage="compare",error=str(exc)); continue
        row["equal"]=bool(result["equal"])
        row["stage"]="equal" if result["equal"] else "semantic-diff"
        if result["equal"]:
            equal+=1
        else:
            row["source_definition"]=result.get("source_definition")
            row["regenerated_definition"]=result.get("regenerated_definition")

    failures=[r for r in rows if not r.get("equal")]
    by_stage={}
    for row in failures:
        by_stage[row.get("stage","unknown")]=by_stage.get(row.get("stage","unknown"),0)+1

    report={
        "source":str(args.source),
        "definitions":len(rows),
        "semantic_equal":equal,
        "failures":len(failures),
        "failures_by_stage":dict(sorted(by_stage.items())),
        "regenerated_counts":{
            name:len(aggregate.find(q(OD,name)) or [])
            for name in ("definitions","tests","objects","states","variables")
        },
        "results":rows,
    }
    args.report.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    summary={k:v for k,v in report.items() if k!="results"}
    if failures:
        summary["failure_details"]=failures
    print(json.dumps(summary,indent=2,sort_keys=True))
    return 0 if args.inventory_only or not failures else 1

if __name__=="__main__":
    raise SystemExit(main())
