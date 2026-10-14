#!/usr/bin/env python3
"""SCAP-NG 0.4 real-source dataflow-pattern and graph readability study.

Strictly observational: consumes the immutable 0.3 release ZIP; does not rewrite
Variable execution, OVAL semantics, result status, or source content.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from pathlib import Path
import argparse
import csv
import hashlib
import json
import re
import zipfile

import yaml
from research_04_self_contained_inline import refs, analyze_chain

NONSEMANTIC = frozenset({
    "id", "title", "description", "provenance", "migration_provenance",
    "source_id", "source_variable_id", "source_object_id",
    "source_definition_id", "comments",
})
OPS = frozenset({
    "concat","regex_capture","split","unique","merge","count","substring",
    "begin","end","escape_regex","glob_to_regex","arithmetic","values",
    "object_component","object_values","variable_component","time_difference",
})

def clean(node):
    if isinstance(node, list):
        return [clean(x) for x in node]
    if isinstance(node, dict):
        return {k: clean(v) for k,v in node.items() if k not in NONSEMANTIC}
    return node

def fingerprint(node):
    return hashlib.sha256(json.dumps(clean(node),sort_keys=True,
        ensure_ascii=False,default=str,separators=(",",":")).encode()).hexdigest()

def sources(node):
    objs=set()
    external=set()
    ops=Counter()
    def walk(x):
        if isinstance(x,list):
            for v in x: walk(v)
        if isinstance(x,dict):
            for k,v in x.items():
                if k == "object" and isinstance(v,str): objs.add(v)
                if k in ("input","observation") and isinstance(v,str):
                    external.add(v)
                if k in OPS: ops[k]+=1
                walk(v)
    walk(node)
    return sorted(objs),sorted(external),dict(ops)

def analyze_assessment(doc):
    a=doc["assessment"]
    reg=a.get("variables") or {}
    all_other={k:v for k,v in a.items() if k!="variables"}
    rows=[]
    dependencies=defaultdict(list)
    consumers=defaultdict(list)
    for variable,payload in reg.items():
        outer=list(refs(all_other,"variable",variable))
        for other, body in reg.items():
            if other==variable:continue
            for loc in refs(body,"variable",variable):
                outer.append(("variables",other)+loc)
                dependencies[other].append(variable)
        consumers[variable].extend(outer)
    def trace(id_, seen=()):
        if id_ in seen:return ["[CYCLE]"]
        result=[]
        for dep in sorted(set(dependencies[id_])):
            result.extend(trace(dep,seen+(id_,)))
        return result+[id_]
    for name,payload in reg.items():
        objs,inputs,ops=sources(payload.get("expression"))
        rows.append(dict(
            name=name, datatype=payload.get("datatype"),kind=payload.get("kind"),
            operations=ops, source_objects=objs, external_sources=inputs,
            dependencies=sorted(set(dependencies[name])),
            consumer_count=len(consumers[name]),
            consumer_paths=["/".join(str(t) for t in p) for p in consumers[name]],
            expression_fingerprint=fingerprint({
                "kind":payload.get("kind"),
                "datatype":payload.get("datatype"),
                "expression":payload.get("expression")}),
            exact_payload_fingerprint=fingerprint(payload),
            longest_path_nodes=len(trace(name)),
        ))
    return rows

def resolved_graph_fingerprint(variable_id, assessment):
    """Closed authoring dependency fingerprint; refuse missing references/cycles.

    This checks equality of stored derivation and collector shape. It does NOT
    imply target-dependent collection/evidence can be safely cached or shared.
    """
    registry=assessment.get("variables") or {}
    objects={**(assessment.get("objects") or {}), **(assessment.get("shared_objects") or {})}
    missing=set()
    def walk(node, var_stack=(), obj_stack=()):
        if isinstance(node,list):
            return [walk(x,var_stack,obj_stack) for x in node]
        if isinstance(node,dict):
            if set(node)=={"variable"} and isinstance(node["variable"],str):
                name=node["variable"]
                if name in var_stack:
                    missing.add("variable-cycle:"+name)
                    return {"variable_cycle":name}
                if name not in registry:
                    missing.add("variable-missing:"+name)
                    return {"variable_missing":name}
                return {"resolved_variable":walk(
                    clean(registry[name]),var_stack+(name,),obj_stack)}
            # Object references are alternate serializations in the accepted
            # 0.3 Assessment language; preserve the marker and source identity.
            if set(node)=={"object"} and isinstance(node["object"],str):
                name=node["object"]
                if name in obj_stack:
                    missing.add("object-cycle:"+name)
                    return {"object_cycle":name}
                if name not in objects:
                    missing.add("object-missing:"+name)
                    return {"object_missing":name}
                return {"resolved_object":walk(
                    clean(objects[name]),var_stack,obj_stack+(name,))}
            return {k:walk(v,var_stack,obj_stack) for k,v in node.items()
                    if k not in NONSEMANTIC}
        return node
    if variable_id not in registry:
        raise ValueError("unknown Variable")
    closure=walk(clean(registry[variable_id]),(variable_id,),())
    return fingerprint(closure),sorted(missing)

def friendly(text):
    return str(text).replace("|","\\|").replace("\n"," ").replace("`","'")

def graph_markdown(assessment, rid, key):
    nodes=analyze_assessment(assessment)
    byid={r["name"]:r for r in nodes}
    out=[
        "# " + rid + " — derived-value dependency map",
        "",
        "**Source:** adjacent released 0.3 Assessment; original standalone OVAL is also in this directory.",
        "**Status:** automatically generated explanatory view, NOT authoring syntax or scanner execution proof.",
        "",
        f"**{len(nodes)} named Variables** in this Assessment. Outputs lead to the original Tests/Objects/States.",
        "",
        "| Variable / value | Depends on | Calculation | Used by |",
        "|---|---|---|---|",
    ]
    for r in nodes[:35]:
        deps = ", ".join(r["dependencies"] or r["source_objects"]) or "literal / external"
        ops = ", ".join(k for k,v in r["operations"].items() for _ in range(v)) or "direct value"
        use = ", ".join(dict.fromkeys(path.split("/")[0] for path in r["consumer_paths"])) or "unreferenced"
        out.append(f"| `{friendly(r['name'])}` | {friendly(deps)} | {friendly(ops)} | {friendly(use)} |")
    if len(nodes)>35:out.append(f"\n{len(nodes)-35} additional named Variables omitted from this short view; no source file is omitted.")
    out += ["", "### How to read this",
        "",
        "Start with the collected source Objects, follow the named calculations,",
        "and finish at the Object selector or expected State that consumes the value.",
        "The source Variable definitions remain unchanged; OVAL empty/multiple/error",
        "semantics, ordering, correlation, and completeness are NOT inferred from",
        "this graph. Names are not proof of semantics.",
        "",
        "See `current-0.3.assessment.yaml` and `original-1.4.oval.xml` for exact logic.",
    ]
    return "\n".join(out)+"\n"

def run(source_zip, study):
    with zipfile.ZipFile(source_zip) as z:
        names=[n for n in z.namelist() if n.endswith(".yaml") and n.startswith("authoring/")]
        docs={}
        for name in names:
            obj=yaml.safe_load(z.read(name))
            if isinstance(obj,dict) and isinstance(obj.get("assessment"),dict):
                a=obj["assessment"]
                if a.get("mode")=="automated" and a.get("variables"):
                    docs[name.removeprefix("authoring/")]=obj
    variable_csv={}
    with (study/"ALL-VARIABLES.csv").open(newline="",encoding="utf8") as fd:
        for row in csv.DictReader(fd):
            variable_csv[(row["benchmark"],row["source_path"],row["variable_id"])]=row
    stats=json.loads((study/"STATS.json").read_text())
    apache = {path:d for path,d in docs.items() if path.startswith("apache_server_2-4_unix_server/")}
    shared = {path:d for path,d in docs.items() if path.startswith("shared/")}
    # Only count in-scope Apache rule assessments from the actual rule-bound census.
    paths=sorted({key[1] for key in variable_csv if key[0]=="apache_server_2-4_unix_server"})
    occurrence=defaultdict(list)
    expression_groups=defaultdict(list)
    chain_graph_counts=Counter()
    named_chain_consumers=Counter()
    closure_occurrences=defaultdict(list)
    incomplete_closure=Counter()
    for path in paths:
        a=docs[path]["assessment"]
        graph=analyze_assessment(docs[path])
        variables=a.get("variables") or {}
        chain_graph_counts.update({path:len([r for r in graph if any(
            item.startswith("variables/") for item in r["consumer_paths"])])})
        for row in graph:
            closure, missing=resolved_graph_fingerprint(row["name"],a)
            if missing:
                incomplete_closure.update(missing)
            else:
                closure_occurrences[closure].append((path,row["name"]))
            occurrence[(row["name"], row["exact_payload_fingerprint"])].append(path)
            expression_groups[row["expression_fingerprint"]].append((path,row["name"]))
            for p in row["consumer_paths"]:
                if p.startswith("variables/"):
                    named_chain_consumers[p.split("/")[1]]+=1
    repeated_named=[dict(name=key[0],assessments=len(paths),fingerprint=key[1],
        sample=paths[:3]) for key,paths in occurrence.items() if len(set(paths))>=2]
    repeated_named.sort(key=lambda x:(-x["assessments"],x["name"]))
    repeated_expr=[dict(fingerprint=k,occurrences=len(v),
        different_assessments=len({p for p,n in v}),
        sample=[dict(assessment=p,variable=n) for p,n in v[:3]])
        for k,v in expression_groups.items() if len({p for p,n in v})>=2]
    repeated_expr.sort(key=lambda x:(-x["different_assessments"],-x["occurrences"]))
    closed_groups=[dict(fingerprint=k, occurrences=len(v),
        assessments=len({path for path,name in v}),
        sample=[dict(assessment=path,variable=name) for path,name in v[:3]])
        for k,v in closure_occurrences.items() if len({path for path,name in v})>=2]
    closed_groups.sort(key=lambda g:(-g["assessments"],-g["occurrences"]))
    # A candidate for reuse is an identical named/expression definition across
    # assessment boundaries, NOT proof that it can be made a runtime provider.
    report={
        "status":"research_only_no_semantic_merge_claim",
        "apache_assessments_with_variable_dataflow":len(paths),
        "apache_variable_occurrences":sum(len((docs[p]["assessment"].get("variables") or {})) for p in paths),
        "apache_exact_named_payload_duplicate_groups":len(repeated_named),
        "apache_exact_named_payload_duplicate_occurrences":sum(x["assessments"] for x in repeated_named),
        "apache_expression_duplicate_groups":len(repeated_expr),
        "apache_expression_duplicate_occurrences":sum(x["occurrences"] for x in repeated_expr),
        "apache_complete_closed_graph_duplicate_groups":len(closed_groups),
        "apache_complete_closed_graph_duplicate_occurrences":sum(g["occurrences"] for g in closed_groups),
        "apache_incomplete_closed_graph_reasons":dict(incomplete_closure),
        "largest_complete_closed_graph_groups":closed_groups[:18],
        "largest_named_duplicate_groups":repeated_named[:24],
        "largest_expression_duplicate_groups":repeated_expr[:20],
        "apache_chain_consumer_nodes":len(named_chain_consumers),
        "notes":[
            "Source names and expression fingerprints are observational only.",
            "Identical source-time expressions are not automatically reusable runtime observation providers.",
            "Collection cardinality, error behavior, provenance, input targeting and scanner scheduling require separate proof.",
        ],
    }
    (study/"APACHE-DATAFLOW-PATTERNS.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    for case in stats.get("examples",[]):
        folder=study/case["folder"]
        current=folder/"current-0.3.assessment.yaml"
        if current.exists():
            doc=yaml.safe_load(current.read_text())
            if doc["assessment"].get("variables"):
                (folder/"VARIABLE-FLOW.md").write_text(graph_markdown(doc,case["rule_id"],case["benchmark"]))
    return report

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--authoring-zip",required=True,type=Path)
    ap.add_argument("--study",required=True,type=Path)
    a=ap.parse_args()
    print(json.dumps(run(a.authoring_zip,a.study),indent=2,sort_keys=True))

if __name__=="__main__":main()
