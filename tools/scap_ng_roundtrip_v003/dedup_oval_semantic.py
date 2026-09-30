#!/usr/bin/env python3
"""Semantically deduplicate an aggregate OVAL document.

Definitions remain distinct. Tests, objects, states and variables are collapsed
only when the ID-independent semantic comparator says they are equivalent.
All references are rewritten to the retained canonical IDs.
"""
from __future__ import annotations
import argparse, collections, json
from pathlib import Path
import xml.etree.ElementTree as ET

from compare_oval_semantics import Model, OD, split

def q(name):
    return f"{{{OD}}}{name}"

def section_map(root,section):
    node=root.find(q(section))
    if node is None:
        return None,{}
    return node,{child.get("id"):child for child in node if child.get("id")}

def semantic_groups(model,kind,ids):
    fn={
        "test":model.test,
        "object":model.obj,
        "state":model.state,
        "variable":model.variable,
    }[kind]
    groups=collections.defaultdict(list)
    for item_id in ids:
        groups[repr(fn(item_id))].append(item_id)
    return groups

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("source",type=Path)
    ap.add_argument("-o","--output",type=Path,required=True)
    ap.add_argument("--report",type=Path,required=True)
    args=ap.parse_args()

    model=Model(args.source)
    tree=ET.parse(args.source)
    root=tree.getroot()

    config=[
        ("test","tests",model.tests),
        ("object","objects",model.objects),
        ("state","states",model.states),
        ("variable","variables",model.vars),
    ]
    remap={}
    detail={}
    before={}
    after={}

    for kind,section_name,index in config:
        before[kind]=len(index)
        groups=semantic_groups(model,kind,index.keys())
        duplicate_groups=[]
        for members in groups.values():
            if len(members)<2:
                continue
            canonical=sorted(members)[0]
            for duplicate in members:
                if duplicate!=canonical:
                    remap[duplicate]=canonical
            duplicate_groups.append({
                "canonical":canonical,
                "duplicates":sorted(x for x in members if x!=canonical),
            })
        detail[kind]=duplicate_groups
        after[kind]=before[kind]-sum(len(x["duplicates"]) for x in duplicate_groups)

    # Rewrite all exact OVAL-ID references before deleting duplicate nodes.
    for node in root.iter():
        for attr,value in list(node.attrib.items()):
            if value in remap:
                node.set(attr,remap[value])
        if node.text:
            stripped=node.text.strip()
            if stripped in remap and stripped==node.text.strip():
                node.text=remap[stripped]

    for kind,section_name,index in config:
        section=root.find(q(section_name))
        if section is None:
            continue
        for child in list(section):
            cid=child.get("id")
            if cid in remap:
                section.remove(child)

    ET.indent(tree,space="  ")
    args.output.parent.mkdir(parents=True,exist_ok=True)
    tree.write(args.output,encoding="utf-8",xml_declaration=True)

    report={
        "before":before,
        "after":after,
        "removed":{k:before[k]-after[k] for k in before},
        "total_removed":sum(before[k]-after[k] for k in before),
        "duplicate_groups":detail,
    }
    args.report.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k!="duplicate_groups"},indent=2,sort_keys=True))

if __name__=="__main__":
    main()
