#!/usr/bin/env python3
"""Research-only census of recurring native Assessment complexity motifs.

This examines faithful converted SCAP-NG authoring and groups repeated graph
shapes that may justify future modernization. It does not modify content and
does not imply that any detected motif is safe to rewrite.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import yaml


FUNCTION_KEYS={
    "arithmetic","begin","concat","count","end","escape_regex","glob_to_regex",
    "merge","regex_capture","split","substring","time_difference","unique",
}


def load(path: Path) -> dict | None:
    try:
        doc=yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return doc if isinstance(doc,dict) else None


def walk(value: Any, path=()):
    yield path,value
    if isinstance(value,dict):
        for k,v in value.items():
            yield from walk(v,path+(k,))
    elif isinstance(value,list):
        for i,v in enumerate(value):
            yield from walk(v,path+(i,))


def variable_refs(value: Any):
    for path,node in walk(value):
        if isinstance(node,dict) and set(node)=={"variable"} and isinstance(node.get("variable"),str):
            yield node["variable"],path


def expression_ops(expr: Any) -> Counter:
    out=Counter()
    for _,node in walk(expr):
        if not isinstance(node,dict):
            continue
        keys=set(node)
        if keys=={"values"}:
            values=node.get("values")
            if isinstance(values,dict) and set(values)=={"object","field"}:
                out["object_component"]+=1
            else:
                out["values"]+=1
        for key in FUNCTION_KEYS:
            if key in node:
                out[key]+=1
    return out


def has_key(value: Any, key: str) -> bool:
    return any(isinstance(node,dict) and key in node for _,node in walk(value))


def destination(path):
    if not path:
        return "other"
    first=path[0]
    if first=="objects":
        return "object"
    if first=="states":
        return "state"
    if first=="tests":
        return "test"
    if first=="variables":
        return "variable"
    if first=="evaluate":
        return "evaluate"
    return str(first)


def assessment_row(path: Path, doc: dict):
    a=doc.get("assessment")
    if not isinstance(a,dict) or a.get("mode")!="automated":
        return None
    variables=a.get("variables") or {}
    objects=a.get("objects") or {}
    states=a.get("states") or {}
    tests=a.get("tests") or {}
    if not isinstance(variables,dict):
        variables={}
    if not isinstance(objects,dict):
        objects={}
    if not isinstance(states,dict):
        states={}
    if not isinstance(tests,dict):
        tests={}

    surface={
        "objects":objects,
        "states":states,
        "tests":tests,
        "evaluate":a.get("evaluate"),
        "variables":variables,
    }
    refs=defaultdict(list)
    for var,pathref in variable_refs(surface):
        refs[var].append(pathref)

    motifs=set()
    ops=Counter()
    direct_projection_vars=[]
    variable_chain_vars=[]
    single_consumer_derived=[]
    shared_derived=[]
    multi_var_consumers=defaultdict(set)
    command_fed=set()
    state_fed=set()

    for vid,var in variables.items():
        expr=var.get("expression") if isinstance(var,dict) else None
        vops=expression_ops(expr)
        ops.update(vops)
        if vops.get("object_component")==1 and sum(vops.values())==1:
            direct_projection_vars.append(vid)
        if any(destination(p)=="variable" for p in refs.get(vid,[])):
            variable_chain_vars.append(vid)
        external=[p for p in refs.get(vid,[]) if not (p and p[0]=="variables" and len(p)>1 and p[1]==vid)]
        if len(external)==1:
            single_consumer_derived.append(vid)
        elif len(external)>1:
            shared_derived.append(vid)
        for p in external:
            dest=destination(p)
            if dest=="state":
                state_fed.add(vid)
            if dest=="object":
                # Command Variables are still Object consumers; identify path context.
                if any(str(x) in {"command","shellcommand"} for x in p):
                    command_fed.add(vid)

    for oid,obj in objects.items():
        vars_here={v for v,_ in variable_refs(obj)}
        if len(vars_here)>1:
            multi_var_consumers[f"object:{oid}"].update(vars_here)
        cap=str(obj.get("capability") or "") if isinstance(obj,dict) else ""
        if "shellcommand" in cap:
            command_fed.update(vars_here)
    for sid,state in states.items():
        vars_here={v for v,_ in variable_refs(state)}
        if len(vars_here)>1:
            multi_var_consumers[f"state:{sid}"].update(vars_here)
        state_fed.update(vars_here)

    sets=sum(1 for _,node in walk(objects) if isinstance(node,dict) and "set" in node)
    filters=sum(1 for _,node in walk(objects) if isinstance(node,dict) and "filter" in node)

    if direct_projection_vars:
        motifs.add("direct_object_component_projection")
    if single_consumer_derived:
        motifs.add("single_consumer_derived_value")
    if shared_derived:
        motifs.add("shared_derived_value")
    if variable_chain_vars:
        motifs.add("variable_chain")
    if multi_var_consumers:
        motifs.add("multi_variable_consumer")
    if command_fed:
        motifs.add("variable_feeds_command")
    if state_fed:
        motifs.add("variable_feeds_state")
    if sets and not variables:
        motifs.add("set_filter_without_variables")
    elif sets:
        motifs.add("set_with_variables")
    if filters and not variables:
        motifs.add("filter_without_variables")
    elif filters:
        motifs.add("filter_with_variables")
    for op in ops:
        motifs.add("function:"+op)

    advanced=bool(variables or sets or filters or len(tests)>1)
    if not advanced:
        return None

    # Try to recover the STIG rule id from Assessment id/filename for examples.
    aid=str(a.get("id") or "")
    rid=None
    for token in (aid,path.name):
        import re
        m=re.search(r"SV-\d+",token)
        if m:
            rid=m.group(0)
            break

    return {
        "path":str(path),
        "assessment_id":aid,
        "rule_id":rid,
        "tests":len(tests),
        "objects":len(objects),
        "states":len(states),
        "variables":len(variables),
        "sets":sets,
        "filters":filters,
        "motifs":sorted(motifs),
        "function_counts":dict(ops),
        "direct_projection_variables":direct_projection_vars,
        "single_consumer_derived_variables":single_consumer_derived,
        "shared_derived_variables":shared_derived,
        "variable_chain_variables":variable_chain_vars,
        "multi_variable_consumers":{k:sorted(v) for k,v in multi_var_consumers.items()},
        "command_fed_variables":sorted(command_fed),
        "state_fed_variables":sorted(state_fed),
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("root",type=Path)
    ap.add_argument("--label",required=True)
    ap.add_argument("--output",type=Path,required=True)
    ap.add_argument("--examples-per-motif",type=int,default=8)
    args=ap.parse_args()

    rows=[]
    files=0
    for path in sorted(args.root.rglob("*.yaml")):
        doc=load(path)
        if doc is None:
            continue
        files+=1
        row=assessment_row(path,doc)
        if row is not None:
            rows.append(row)

    motif_counts=Counter()
    function_counts=Counter()
    examples=defaultdict(list)
    for row in rows:
        motif_counts.update(row["motifs"])
        function_counts.update(row["function_counts"])
        for motif in row["motifs"]:
            if len(examples[motif])<args.examples_per_motif:
                examples[motif].append({
                    "rule_id":row["rule_id"],
                    "assessment_id":row["assessment_id"],
                    "path":row["path"],
                })

    total=len(rows)
    pct=lambda n: round(100*n/total,1) if total else 0.0
    report={
        "format":"scap-ng-residual-complexity-pattern-census-0.1",
        "status":"research_only_not_accepted_design",
        "label":args.label,
        "yaml_files_examined":files,
        "advanced_assessments":total,
        "motif_counts":dict(sorted(motif_counts.items(), key=lambda x:(-x[1],x[0]))),
        "motif_percent_of_advanced":{
            k:pct(v) for k,v in sorted(motif_counts.items(),key=lambda x:(-x[1],x[0]))
        },
        "function_counts":dict(sorted(function_counts.items(),key=lambda x:(-x[1],x[0]))),
        "examples":dict(examples),
        "assessments":rows,
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        "label":args.label,
        "advanced_assessments":total,
        "top_motifs":report["motif_counts"],
    },indent=2))


if __name__=="__main__":
    main()
