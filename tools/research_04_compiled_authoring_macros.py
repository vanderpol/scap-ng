#!/usr/bin/env python3
"""Mechanical 0.4 research-only authoring macros that re-expand to original parsed 0.3.

NO canonical specification changes or inference of an omitted property.
"""
import argparse
from collections import Counter,defaultdict
from copy import deepcopy
import json
from pathlib import Path
import zipfile
import yaml

OPS={"equals":"equals","pattern_match":"matches_regex"}
REV={v:k for k,v in OPS.items()}


def scalar(value):
    return type(value) in (str,int,float,bool)


def simplify_predicate(d):
    if not isinstance(d,dict) or "value" not in d:
        return d,False
    op=d.get("operation")
    if op not in OPS or not scalar(d["value"]) or OPS[op] in d:
        return d,False
    new=deepcopy(d)
    value=new.pop("value")
    del new["operation"]
    new[OPS[op]]=value
    return new,True


def expand_predicate(d):
    if not isinstance(d,dict):
        return d
    present=[k for k in REV if k in d]
    if not present:
        return d
    if len(present)!=1 or "operation" in d or "value" in d:
        raise ValueError("Ambiguous or mixed predicate shorthand and canonical form")
    new=deepcopy(d)
    k=present[0]
    v=new.pop(k)
    if not scalar(v):
        raise ValueError("Shorthand predicate value not scalar")
    new["value"]=v
    new["operation"]=REV[k]
    return new


def simplify_doc(doc):
    out=deepcopy(doc)
    a=out["assessment"]
    counts=Counter()
    tests=a.get("tests") or {}
    if len(tests)==1:
        test_name=next(iter(tests))
        if a.get("evaluate")=={"test":test_name}:
            a["evaluate"]="sole_test"  # explicit instruction, never inferred
            counts["sole_test_evaluate"]+=1
    for test_name,t in tests.items():
        if not isinstance(t,dict):
            continue
        if isinstance(t.get("object"),dict):
            obj=t["object"]
            if (isinstance(t.get("capability"),str)
                and obj.get("capability")==t["capability"]):
                # Explicit parent typing rather than an invisible schema default.
                obj["capability"]="from_test"
                counts["private_object_capability_from_test"]+=1
            sel=obj.get("select") or {}
            for field,p in list(sel.items()):
                new,changed=simplify_predicate(p)
                if changed:
                    sel[field]=new
                    counts["selector_comparison"]+=1
        states=t.get("states")
        if isinstance(states,list):
            for state in states:
                if not isinstance(state,dict) or not ("field" in state and "value" in state):
                    continue
                new,changed=simplify_predicate(state)
                if changed:
                    state.clear()
                    state.update(new)
                    counts["state_comparison"]+=1
            if len(states)==1 and isinstance(states[0],dict) and "expect" not in t:
                t["expect"]=t.pop("states")[0]
                counts["sole_state_expect"]+=1
    return out,counts


def expand_doc(source):
    doc=deepcopy(source)
    a=doc["assessment"]
    tests=a.get("tests") or {}
    if a.get("evaluate")=="sole_test":
        if len(tests)!=1:
            raise ValueError("sole_test requires exactly one Test")
        a["evaluate"]={"test":next(iter(tests))}
    for test_name,t in tests.items():
        if not isinstance(t,dict):
            continue
        ob=t.get("object")
        if isinstance(ob,dict):
            if ob.get("capability")=="from_test":
                if not isinstance(t.get("capability"),str):
                    raise ValueError("private Object cannot inherit absent Test capability")
                ob["capability"]=t["capability"]
            for k,val in list((ob.get("select") or {}).items()):
                ob["select"][k]=expand_predicate(val)
        if "expect" in t:
            if "states" in t or not isinstance(t["expect"],dict):
                raise ValueError("expect must be exactly one State with no states sibling")
            t["states"]=[t.pop("expect")]
        if isinstance(t.get("states"),list):
            t["states"]=[expand_predicate(s) for s in t["states"]]
    return doc


def census(zipfile_path):
    counters=Counter()
    per_benchmark=defaultdict(Counter)
    examples=[]
    with zipfile.ZipFile(zipfile_path) as z:
        if z.testzip() is not None:
            raise ValueError("Bad archive")
        for filename in sorted(z.namelist()):
            if not (filename.startswith("authoring/") and filename.endswith(".automated.yaml")):
                continue
            original=yaml.safe_load(z.read(filename))
            if not isinstance(original,dict) or (original.get("assessment") or {}).get("mode")!="automated":
                continue
            transformed,local=simplify_doc(original)
            expanded=expand_doc(transformed)
            if expanded!=original:
                raise AssertionError(f"Macro expansion changed parsed 0.3 for {filename}")
            counters["exact_assessment_round_trips"]+=1
            counters.update(local)
            key=filename.split("/")[1]
            per_benchmark[key]["exact_assessment_round_trips"]+=1
            per_benchmark[key].update(local)
            if local and len(examples)<8:
                examples.append({"file":filename,"macros_applied":dict(local)})
    return {
        "status":"research_only_compiles_exact_original_parsed_0_3",
        "source":zipfile_path.name,
        "counts":dict(counters),
        "per_benchmark":{k:dict(v) for k,v in sorted(per_benchmark.items())},
        "samples":examples,
        "limitations":[
            "This proves parsed source equivalence for supported transformations, not runtime scanner conformance.",
            "Scalar-only comparison macros preserve original typed YAML values and exact regex strings.",
            "A private Object's from_test typing is explicitly requested; it is not a schema default.",
            "The macros can overlap; counts cannot be summed as independent lines saved.",
            "All macros compile to canonical explicit 0.3 before validation and vendor scanning.",
        ]
    }


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--authoring-zip",type=Path,required=True)
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    output=json.dumps(census(args.authoring_zip),indent=2,sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(output+"\n")
    print(output)
