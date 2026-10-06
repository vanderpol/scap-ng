#!/usr/bin/env python3
"""Research-only census of recurring residual Assessment complexity patterns.

The goal is not to label features "bad". It clusters real automated Assessments
by semantic shape after removing IDs, titles, provenance and literal values so
we can see whether the complex remainder is a small set of recurring patterns.

This tool is descriptive only; it performs no rewrite.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import yaml

FUNCTION_KEYS={
    "arithmetic","begin","concat","count","end","escape_regex","glob_to_regex",
    "merge","object_component","object_values","regex_capture","split","substring",
    "time_difference","unique","values","variable_component",
}
BOOL_KEYS={"all","any","not","one","odd","if","then","else"}
NONSEMANTIC_KEYS={
    "id","version","assessment_title","test_title","object_title","state_title",
    "variable_title","title","provenance","migration_provenance","reuse_provenance",
    "source_id","source_definition_id","source_test_id","source_object_id",
    "source_state_id","source_variable_id",
}

def load(path:Path):
    value=yaml.safe_load(path.read_text(encoding="utf-8"))
    return value if isinstance(value,dict) else None

def walk(value:Any):
    yield value
    if isinstance(value,dict):
        for child in value.values():
            yield from walk(child)
    elif isinstance(value,list):
        for child in value:
            yield from walk(child)

def count_key(value:Any,key:str)->int:
    return sum(isinstance(x,dict) and key in x for x in walk(value))

def collect_registry_ids(a:dict):
    registries={
        "tests":("T",a.get("tests") or a.get("checks") or {}),
        "objects":("O",a.get("objects") or {}),
        "states":("S",a.get("states") or {}),
        "variables":("V",a.get("variables") or {}),
    }
    mapping={}
    for _,(prefix,rows) in registries.items():
        if isinstance(rows,dict):
            for i,name in enumerate(sorted(rows),1):
                mapping[name]=f"{prefix}{i}"
    return mapping

def normalize_shape(value:Any, ids:dict[str,str], parent:str|None=None)->Any:
    if isinstance(value,dict):
        out={}
        for key,child in value.items():
            if key in NONSEMANTIC_KEYS:
                continue
            if key=="specification":
                continue
            if key in {"value","pattern","command"}:
                # Keep references/structured expressions, abstract ordinary literals.
                if isinstance(child,(dict,list)):
                    out[key]=normalize_shape(child,ids,key)
                else:
                    out[key]="<LITERAL>"
            else:
                out[key]=normalize_shape(child,ids,key)
        return out
    if isinstance(value,list):
        return [normalize_shape(x,ids,parent) for x in value]
    if isinstance(value,str) and value in ids:
        return ids[value]
    return value

def fingerprint(value:Any)->str:
    raw=json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False)
    return hashlib.sha256(raw.encode()).hexdigest()

def expression_variable_kind(variable:dict)->str:
    expr=variable.get("expression")
    if not isinstance(expr,dict):
        return "missing_expression"
    keys=set(expr)
    if keys=={"values"}:
        v=expr["values"]
        if isinstance(v,dict) and set(v)=={"object","field"}:
            return "direct_object_projection"
    if keys=={"object_values"}:
        ov=expr["object_values"]
        if isinstance(ov,dict) and set(ov)>={"collect","field"}:
            return "direct_embedded_object_projection"
    found=[]
    for node in walk(expr):
        if isinstance(node,dict):
            for key in node:
                if key in FUNCTION_KEYS:
                    found.append(key)
    return "+".join(sorted(set(found))) or "other_expression"

def max_eval_depth(node:Any,depth=0)->int:
    if not isinstance(node,dict):
        return depth
    keys=set(node)
    here=depth+1 if keys & BOOL_KEYS else depth
    children=[]
    for v in node.values():
        if isinstance(v,list): children.extend(v)
        elif isinstance(v,dict): children.append(v)
    return max([here]+[max_eval_depth(x,here) for x in children])

def leaf_ref(node):
    if not isinstance(node,dict) or len(node)!=1:
        return None
    key=next(iter(node))
    if key in {"test","check"} and isinstance(node[key],str):
        return (key,node[key])
    return None

def exact_complement_branch(node)->bool:
    if not isinstance(node,dict) or set(node)!={"any"}:
        return False
    branches=node["any"]
    if not isinstance(branches,list) or len(branches)!=2:
        return False
    if not all(isinstance(b,dict) and set(b)=={"all"} and isinstance(b["all"],list) for b in branches):
        return False
    left,right=branches[0]["all"],branches[1]["all"]
    pairs=0
    for l in left:
        for r in right:
            if isinstance(r,dict) and set(r)=={"not"} and r["not"]==l:
                pairs+=1
            if isinstance(l,dict) and set(l)=={"not"} and l["not"]==r:
                pairs+=1
    return pairs==1

def eval_contains_exact_complement(node)->bool:
    if exact_complement_branch(node):
        return True
    if isinstance(node,dict):
        return any(eval_contains_exact_complement(v) for v in node.values())
    if isinstance(node,list):
        return any(eval_contains_exact_complement(v) for v in node)
    return False

def analyze(path:Path,doc:dict):
    a=doc.get("assessment") or {}
    mode=a.get("mode")
    tests=a.get("tests") or a.get("checks") or {}
    if mode!="automated" or not isinstance(tests,dict) or not tests:
        return None

    variables=a.get("variables") or {}
    var_kinds=Counter()
    if isinstance(variables,dict):
        for row in variables.values():
            if isinstance(row,dict):
                var_kinds[expression_variable_kind(row)]+=1

    funcs=Counter()
    for node in walk(variables):
        if isinstance(node,dict):
            for key in node:
                if key in FUNCTION_KEYS:
                    funcs[key]+=1

    sets=count_key(a,"set")
    filters=count_key(a,"filters")+count_key(a,"filter")
    eval_node=a.get("evaluate")
    eval_depth=max_eval_depth(eval_node)
    exact_cond=eval_contains_exact_complement(eval_node)

    capabilities=Counter()
    for node in walk(a):
        if isinstance(node,dict) and isinstance(node.get("capability"),str):
            capabilities[node["capability"]]+=1

    direct_vars=var_kinds["direct_object_projection"]+var_kinds["direct_embedded_object_projection"]
    non_direct_vars=sum(var_kinds.values())-direct_vars

    reasons=[]
    if non_direct_vars: reasons.append("non_direct_variable_dataflow")
    if sets: reasons.append("sets")
    if filters: reasons.append("filters")
    if eval_depth>=2 and not exact_cond: reasons.append("nested_evaluation_not_exact_complement")
    if len(tests)>1 and eval_depth>=1: reasons.append("multi_test_composition")
    if any(k in funcs for k in ("concat","merge","regex_capture","split","unique","count","arithmetic","substring","time_difference")):
        reasons.append("variable_functions")

    # A conservative research definition: known direct-projection variables and
    # exact complementary conditionals do not by themselves make the remainder
    # "residual complex".
    residual=bool(set(reasons)-{"multi_test_composition"}) or (
        "multi_test_composition" in reasons and eval_depth>=2 and not exact_cond
    )

    ids=collect_registry_ids(a)
    shape=normalize_shape(a,ids)
    return {
        "path":str(path),
        "assessment_id":a.get("id"),
        "tests":len(tests),
        "variables":len(variables) if isinstance(variables,dict) else 0,
        "variable_kinds":dict(var_kinds),
        "function_counts":dict(funcs),
        "sets":sets,
        "filters":filters,
        "evaluate_depth":eval_depth,
        "exact_complement_conditional_shape":exact_cond,
        "capabilities":dict(capabilities),
        "residual_complex":residual,
        "residual_reasons":sorted(set(reasons)),
        "shape_fingerprint":fingerprint(shape),
        "shape":shape,
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("root",type=Path)
    ap.add_argument("--label",required=True)
    ap.add_argument("--output",type=Path,required=True)
    ap.add_argument("--top",type=int,default=30)
    args=ap.parse_args()

    rows=[]
    for path in sorted(args.root.rglob("*.assessment.yaml")):
        try: doc=load(path)
        except Exception: continue
        if not doc: continue
        row=analyze(path,doc)
        if row: rows.append(row)

    residual=[r for r in rows if r["residual_complex"]]
    clusters=defaultdict(list)
    for row in residual:
        clusters[row["shape_fingerprint"]].append(row)

    ranked=sorted(clusters.items(),key=lambda kv:(-len(kv[1]),kv[0]))
    reason_counts=Counter()
    function_counts=Counter()
    variable_kind_counts=Counter()
    for row in residual:
        reason_counts.update(row["residual_reasons"])
        function_counts.update(row["function_counts"])
        variable_kind_counts.update(row["variable_kinds"])

    top=[]
    for fp,members in ranked[:args.top]:
        exemplar=members[0]
        top.append({
            "shape_fingerprint":fp,
            "count":len(members),
            "percent_of_residual":round(100*len(members)/len(residual),2) if residual else 0.0,
            "residual_reasons":exemplar["residual_reasons"],
            "variable_kinds":exemplar["variable_kinds"],
            "function_counts":exemplar["function_counts"],
            "sets":exemplar["sets"],
            "filters":exemplar["filters"],
            "evaluate_depth":exemplar["evaluate_depth"],
            "capabilities":exemplar["capabilities"],
            "examples":[m["assessment_id"] for m in members[:10]],
        })

    report={
        "format":"scap-ng-residual-complexity-pattern-census-0.1",
        "status":"research_only_not_accepted_design",
        "label":args.label,
        "automated_assessments":len(rows),
        "residual_complex_assessments":len(residual),
        "residual_complex_percent":round(100*len(residual)/len(rows),2) if rows else 0.0,
        "known_pattern_signals":{
            "assessments_with_direct_projection_variables":sum(
                (r["variable_kinds"].get("direct_object_projection",0)+r["variable_kinds"].get("direct_embedded_object_projection",0))>0
                for r in rows
            ),
            "assessments_with_exact_complement_conditional_shape":sum(r["exact_complement_conditional_shape"] for r in rows),
        },
        "residual_reason_counts":dict(reason_counts),
        "variable_kind_counts":dict(variable_kind_counts),
        "variable_function_counts":dict(function_counts),
        "unique_residual_shapes":len(clusters),
        "top_residual_shapes":top,
        "all_residual_rows":[{
            k:v for k,v in row.items() if k!="shape"
        } for row in residual],
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        "label":args.label,
        "automated_assessments":len(rows),
        "residual_complex_assessments":len(residual),
        "residual_complex_percent":report["residual_complex_percent"],
        "unique_residual_shapes":len(clusters),
        "top_shapes":[{"count":x["count"],"reasons":x["residual_reasons"],"examples":x["examples"][:3]} for x in top[:10]],
    },indent=2))

if __name__=="__main__":
    main()
