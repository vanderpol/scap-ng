#!/usr/bin/env python3
"""Generate six complete SCAP-NG 0.4.0 source-backed authoring sets.

Source: October 15 r3 pre-alpha archive, pinned by SHA-256 in workflow.
Only promote the two proven all-match requirement pairs to inline
`require.items` / `require.all_items_must`; leave exceptional pairs explicit.
Inherit inline Object capability only for identical Test/Object capability.
Preserve all other graph content and prove parsed-source exact recovery.

Refs #227 #232 #239 #246.
"""
from collections import Counter
from copy import deepcopy
import argparse
import hashlib
import json
from pathlib import Path
import zipfile
import yaml

PAIRS={"at_least_one_exists_and_all_match":"one_or_more",
       "may_be_absent_and_all_match":"may_be_absent"}
INVERSE={v:k for k,v in PAIRS.items()}

def promote(doc):
    new=deepcopy(doc)
    audit=Counter()
    a=new.get("assessment")
    if not isinstance(a,dict) or a.get("mode")!="automated":
        return new,audit
    for test in (a.get("tests") or {}).values():
        cap=test.get("capability")
        obj=test.get("object")
        if isinstance(obj,dict) and "capability" in obj:
            if obj["capability"]!=cap:
                raise ValueError("Inline Object capability conflicts with Test")
            del obj["capability"]
            audit["inline_capabilities_removed"]+=1
        old=test.get("collected_items_require",test.get("require"))
        if "collected_items_require" in test and "require" in test:
            raise ValueError("Mixed Test requirement dialect")
        states=test.get("states")
        if old in PAIRS and isinstance(states,list) and states:
            source_key="collected_items_require" if "collected_items_require" in test else "require"
            test.pop(source_key)
            test.pop("states")
            test["require"]={"items":PAIRS[old],"all_items_must":states}
            audit["all_items_must"]+=1
        elif "collected_items_require" in test:
            test["require"]=test.pop("collected_items_require")
            audit["explicit_fallback"]+=1
    return new,audit

def recover(candidate,original):
    restored=deepcopy(candidate)
    oa=original.get("assessment")
    if not isinstance(oa,dict) or oa.get("mode")!="automated":
        if restored!=original:
            raise ValueError("Non-automated source changed")
        return
    for id,test in restored["assessment"].get("tests",{}).items():
        orig=oa["tests"][id]
        if isinstance(test.get("object"),dict) and "capability" in orig.get("object",{}):
            if "capability" in test["object"]:
                raise ValueError("Redundant inline capability survived promotion")
            test["object"]["capability"]=orig["object"]["capability"]
        source_key="collected_items_require" if "collected_items_require" in orig else "require"
        req=test.get("require")
        if isinstance(req,dict):
            if set(req)!={"items","all_items_must"} or req["items"] not in INVERSE:
                raise ValueError("Unsupported new requirement structure")
            states=req["all_items_must"]
            if not isinstance(states,list) or not states:
                raise ValueError("Missing inline States")
            test.pop("require")
            test["states"]=states
            test[source_key]=INVERSE[req["items"]]
        elif source_key=="collected_items_require":
            test["collected_items_require"]=test.pop("require")
    if restored!=original:
        raise ValueError("Original authoring source differs after exact reverse translation")

def run(src,dest,manifest_path):
    if src.suffix!=".zip": raise ValueError("ZIP input required")
    is_yaml="six-stig-yaml" in src.name
    ext=".yaml" if is_yaml else ".json"
    counts=Counter()
    path_stats={}
    with zipfile.ZipFile(src) as z,zipfile.ZipFile(dest,"w",zipfile.ZIP_DEFLATED) as output:
        names=[x for x in z.namelist() if x.startswith("authoring/") and x.endswith(ext)]
        if len(names)!=4001: raise ValueError(f"Unexpected source count: {len(names)}")
        for name in sorted(names):
            old=yaml.safe_load(z.read(name)) if is_yaml else json.loads(z.read(name))
            new,stats=promote(old)
            recover(new,old)
            counts.update(stats)
            if stats: path_stats[name]=dict(stats)
            rendered=yaml.safe_dump(new,sort_keys=False,allow_unicode=True,width=110) if is_yaml else json.dumps(new,indent=2,ensure_ascii=False)+"\n"
            output.writestr(name,rendered)
        output.writestr("READ-ME-FIRST.txt",
            "SCAP-NG 0.4.0 six-benchmark authoring candidate. Source-exact inversion verified.\n"
            "Object capability inherits from Test; common all-match predicates live inside require.\n"
            "Remaining explicit require strings are original uncommon semantics, not inferred defaults.\n"
            "Do not interpret this authoring ZIP as a signed scanner bundle or runtime parity result.\n")
    if counts["all_items_must"]<1 or counts["inline_capabilities_removed"]<1:
        raise ValueError("Expected real migration did not happen")
    report={"source_sha256":hashlib.sha256(src.read_bytes()).hexdigest(),
            "output_sha256":hashlib.sha256(dest.read_bytes()).hexdigest(),
            "format":"yaml" if is_yaml else "json",
            "documents":len(names),"counts":dict(counts),
            "changed_documents":len(path_stats),
            "changed_paths":path_stats,
            "source_ast_recovered":True,
            "schema_validated":False,
            "scanner_equivalence_proven":False}
    manifest_path.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({k:v for k,v in report.items() if k!="changed_paths"},indent=2))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--manifest",type=Path,required=True)
    a=p.parse_args();run(a.source,a.out,a.manifest)
