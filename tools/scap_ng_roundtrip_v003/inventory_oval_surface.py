#!/usr/bin/env python3
"""Inventory behaviorally relevant OVAL constructs across a corpus."""
from __future__ import annotations
import argparse, collections, json
from pathlib import Path
from lxml import etree as E

OD="http://oval.mitre.org/XMLSchema/oval-definitions-5"

def qname(el):
    q=E.QName(el)
    ns=q.namespace or ""
    fam=ns.split("#")[-1] if "#" in ns else ("oval-def" if ns==OD else ns)
    return f"{fam}.{q.localname}"

def bump(counter,key):
    counter[key]+=1

def inventory_file(path):
    root=E.parse(str(path)).getroot()
    c=collections.Counter()
    vals={k:collections.Counter() for k in [
        "test_types","object_types","state_types","variable_types","functions",
        "operations","check","check_existence","state_operator","criteria_operator",
        "set_operator","filter_action","var_check","entity_check","datatypes",
        "behaviors","criteria_nodes",
    ]}
    for el in root.iter():
        if not isinstance(el.tag,str):
            continue
        local=E.QName(el).localname
        ns=E.QName(el).namespace or ""
        if local.endswith("_test") and ns!=OD:
            vals["test_types"][qname(el)]+=1
        elif local.endswith("_object") and ns!=OD:
            vals["object_types"][qname(el)]+=1
        elif local.endswith("_state") and ns!=OD:
            vals["state_types"][qname(el)]+=1
        elif local in {"constant_variable","external_variable","local_variable"} and ns==OD:
            vals["variable_types"][local]+=1
        elif local in {"arithmetic","begin","concat","end","escape_regex","split","substring",
                       "time_difference","regex_capture","unique","count","glob_to_regex","merge"} and ns==OD:
            vals["functions"][local]+=1
        elif local in {"criteria","criterion","extend_definition"} and ns==OD:
            vals["criteria_nodes"][local]+=1

        for a,bucket in [
            ("operation","operations"),("check","check"),("check_existence","check_existence"),
            ("state_operator","state_operator"),("set_operator","set_operator"),
            ("action","filter_action"),("var_check","var_check"),("entity_check","entity_check"),
            ("datatype","datatypes"),
        ]:
            if a in el.attrib:
                vals[bucket][el.attrib[a]]+=1
        if local=="criteria" and "operator" in el.attrib:
            vals["criteria_operator"][el.attrib["operator"]]+=1
        if local=="behaviors":
            for a,v in sorted(el.attrib.items()):
                vals["behaviors"][f"{qname(el)}@{a}={v}"]+=1
    return vals

def merge(dst,src):
    for k,v in src.items(): dst[k].update(v)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("root",type=Path)
    ap.add_argument("--glob",default="**/oval.xml")
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()

    files=sorted(args.root.glob(args.glob))
    total={k:collections.Counter() for k in [
        "test_types","object_types","state_types","variable_types","functions",
        "operations","check","check_existence","state_operator","criteria_operator",
        "set_operator","filter_action","var_check","entity_check","datatypes",
        "behaviors","criteria_nodes",
    ]}
    per_file=[]
    for p in files:
        inv=inventory_file(p); merge(total,inv)
        per_file.append({
            "path":p.relative_to(args.root).as_posix(),
            "constructs":{k:dict(sorted(v.items())) for k,v in inv.items() if v},
        })
    out={
        "format":"oval-corpus-surface-inventory-0.1",
        "file_count":len(files),
        "totals":{k:dict(sorted(v.items())) for k,v in total.items() if v},
        "files":per_file,
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"file_count":len(files),"totals":out["totals"]},indent=2,sort_keys=True))
if __name__=="__main__": main()
