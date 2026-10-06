#!/usr/bin/env python3
"""Research-only census of Variable/dataflow shapes in converted RHEL 9 assessments."""
from __future__ import annotations
import argparse, json
from collections import Counter
from pathlib import Path
import yaml

EXPR_KEYS={
    "object_values","object_component","variable_component","concat","split",
    "count","unique","arithmetic","substring","begin","end","merge",
    "regex_capture","escape_regex","glob_to_regex","time_difference","literal",
}

def walk(x):
    if isinstance(x,dict):
        yield x
        for v in x.values(): yield from walk(v)
    elif isinstance(x,list):
        for v in x: yield from walk(v)

def variable_refs(x):
    refs=[]
    for n in walk(x):
        if isinstance(n,dict):
            if set(n)=={"variable"} and isinstance(n["variable"],str):
                refs.append(n["variable"])
            if "variable_component" in n:
                vc=n["variable_component"]
                if isinstance(vc,dict):
                    ref=vc.get("variable") or vc.get("var_ref")
                    if isinstance(ref,str): refs.append(ref)
    return refs

def classify_var(var):
    expr=var.get("expression")
    if not isinstance(expr,dict):
        return {"kind":"unknown","top":[],"refs":[]}
    top=[k for k in expr if k in EXPR_KEYS]
    refs=variable_refs(expr)
    if set(expr)=={"object_values"}:
        kind="field_projection"
    elif set(expr)=={"concat"}:
        kind="concat"
    elif set(expr)=={"split"}:
        kind="split"
    elif set(expr)=={"count"}:
        kind="count"
    elif set(expr)=={"unique"}:
        kind="unique"
    elif set(expr)=={"arithmetic"}:
        kind="arithmetic"
    elif set(expr)=={"variable_component"}:
        kind="variable_component"
    elif len(top)==1:
        kind=top[0]
    else:
        kind="mixed_or_unknown"
    return {"kind":kind,"top":top,"refs":sorted(set(refs))}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("root",type=Path)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()

    rows=[]; rule_counts=Counter(); variable_counts=Counter(); combos=Counter()
    for path in sorted((args.root/"assessments"/"automated").glob("*.yaml")):
        doc=yaml.safe_load(path.read_text()) or {}
        a=doc.get("assessment") or {}
        variables=a.get("variables") or {}
        if not variables: continue

        vars_out={}
        kinds=[]
        for vid,var in variables.items():
            info=classify_var(var)
            vars_out[vid]=info
            kinds.append(info["kind"])
            variable_counts[info["kind"]]+=1

        kindset=tuple(sorted(set(kinds)))
        combos[" + ".join(kindset)] += 1
        for k in set(kinds): rule_counts[k]+=1

        chain_edges=[]
        for vid,info in vars_out.items():
            for ref in info["refs"]:
                if ref in variables:
                    chain_edges.append([vid,ref])

        rows.append({
            "assessment":a.get("id"),
            "path":path.as_posix(),
            "variable_count":len(variables),
            "kinds":sorted(set(kinds)),
            "variables":vars_out,
            "variable_chain_edges":chain_edges,
        })

    total=len(rows)
    summary={
        "status":"research_only_not_accepted_design",
        "rules_with_variables":total,
        "variable_instances":sum(variable_counts.values()),
        "rule_counts_by_variable_kind":dict(rule_counts),
        "variable_instance_counts_by_kind":dict(variable_counts),
        "rule_kind_combinations":dict(combos),
        "rules_with_variable_chains":sum(bool(r["variable_chain_edges"]) for r in rows),
        "rules_with_single_variable":sum(r["variable_count"]==1 for r in rows),
        "rules_with_multiple_variables":sum(r["variable_count"]>1 for r in rows),
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps({"summary":summary,"rules":rows},indent=2,sort_keys=True)+"\n")
    print(json.dumps(summary,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
