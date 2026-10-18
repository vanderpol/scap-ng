#!/usr/bin/env python3
"""#237: six-STIG source Variable DAG inventory, source-shape only.

Counts converted-0.3 Assessment Variable expressions, dependencies and cycles.
Source graph traversal is not conversion to executable IR nor OVAL parity.
"""
from __future__ import annotations

from collections import Counter
import argparse
import json
from pathlib import Path
from research_b_full_corpus_import import read_source,import_corpus


def variable_references(value):
    """Return all literal Variable references, including nested Object queries."""
    found=set()
    def walk(node):
        if isinstance(node,dict):
            for k,v in node.items():
                if k=="variable" and type(v) is str:
                    found.add(v)
                walk(v)
        elif isinstance(node,list):
            for x in node:walk(x)
    walk(value)
    return found


def analyze_graph(assessment):
    variables=assessment.get("variables",{})
    if not isinstance(variables,dict):
        raise ValueError("source Variable table must be a mapping")
    declared=set(variables)
    edges={key:variable_references(val) for key,val in variables.items()}
    external={key:sorted(refs-declared) for key,refs in edges.items()
              if refs-declared}
    test_refs=variable_references(assessment.get("tests",{}))
    unbound_test_refs=sorted(test_refs-declared)
    operator_counts=Counter()
    malformed=0
    for value in variables.values():
        expression=value.get("expression") if isinstance(value,dict) else None
        if isinstance(expression,dict) and len(expression)==1:
            op=next(iter(expression))
            operator_counts[str(op)]+=1
        else:
            malformed+=1
    visiting=set();done={};cycles=set()
    def depth(node):
        if node in done:return done[node]
        if node in visiting:
            cycles.add(node)
            return 0
        visiting.add(node)
        ds=[depth(ref) for ref in sorted(edges[node]&declared)]
        visiting.remove(node)
        done[node]=1+max(ds,default=0)
        return done[node]
    for name in sorted(declared):
        depth(name)
    return {
        "variable_count":len(declared),
        "variable_ids":sorted(declared),
        "operators":dict(sorted(operator_counts.items())),
        "dependencies":{key:sorted(value&declared) for key,value in sorted(edges.items())},
        "external_dependencies":external,
        "test_variables":sorted(test_refs),
        "unbound_test_variables":unbound_test_refs,
        "cycle_nodes":sorted(cycles),
        "max_variable_depth":max(done.values(),default=0),
        "malformed_expressions":malformed,
    }


def inventory(capsules):
    rows=[]
    operators=Counter(); by_stream=Counter()
    cycles=[];unknown=Counter();maxdepth=0
    for aid,cap in sorted(capsules.items()):
        a=cap["source_document"].get("assessment",{})
        if a.get("mode")!="automated" or not a.get("variables"):
            continue
        graph=analyze_graph(a)
        benchmark=sorted(cap.get("benchmarks",[]))
        # Import corpus capsules may not include a reverse Rule binding.
        # Record the source path, not a guessed stream, where absent.
        source=cap["source_path"]
        stream=source.split("/")[1] if source.startswith("authoring/") else "shared"
        by_stream[stream]+=1
        operators.update(graph["operators"])
        maxdepth=max(maxdepth,graph["max_variable_depth"])
        if graph["cycle_nodes"]:cycles.append(aid)
        if graph["external_dependencies"] or graph["unbound_test_variables"]:
            unknown["assessments_with_unresolved_refs"]+=1
        rows.append({"assessment_id":aid,"source_path":source,
                     "stream_source_directory":stream,**graph})
    return {
        "format":"scap-ng-b-source-variable-dag-census/0.1",
        "source":"converted_0.3_not_original_SCAP_1.4",
        "original_source_parity_verified":False,
        "assessments_with_variables":len(rows),
        "total_declared_variables":sum(r["variable_count"] for r in rows),
        "source_operator_counts":dict(sorted(operators.items())),
        "source_directory_counts":dict(sorted(by_stream.items())),
        "assessment_count_with_cycles":len(cycles),
        "cycle_assessment_ids":cycles,
        "assessment_count_with_external_refs":
            unknown["assessments_with_unresolved_refs"],
        "max_declared_variable_chain_depth":maxdepth,
        "assessment_graphs":rows,
    }


def markdown(report):
    lines=[
        "# B six-STIG converted-source Variable DAG census",
        "",
        "**Source 0.3 structural research only — not original SCAP 1.4 XML parity or executable content.**",
        "",
        f"**Assessments declaring Variables:** {report['assessments_with_variables']}",
        f"**Declared local Variables:** {report['total_declared_variables']}",
        f"**Largest observed declared dependency depth:** {report['max_declared_variable_chain_depth']}",
        f"**Assessments with cycles (structural analyzer):** {report['assessment_count_with_cycles']}",
        f"**Assessments with unresolved Variable references:** {report['assessment_count_with_external_refs']}",
        "",
        "## Variable expression operators",
        "",
        "| Operator | Declared Variables using it |",
        "| --- | ---: |",
    ]
    for op,count in sorted(report["source_operator_counts"].items(),
                           key=lambda pair:(-pair[1],pair[0])):
        lines.append(f"| {op} | {count} |")
    lines.extend([
        "","## Small and complex example graphs","","| Assessment | Variables | Depth | Operators |",
        "| --- | ---: | ---: | --- |",
    ])
    rows=report["assessment_graphs"]
    picks=sorted(rows,key=lambda r:(r["variable_count"],r["assessment_id"]))[:5]
    picks+=sorted(rows,key=lambda r:(-r["variable_count"],r["assessment_id"]))[:8]
    seen=set()
    for r in picks:
        if r["assessment_id"] in seen:continue
        seen.add(r["assessment_id"])
        o=", ".join(f"{k}({n})" for k,n in r["operators"].items())
        lines.append(f"| {r['assessment_id']} | {r['variable_count']} | {r['max_variable_depth']} | {o} |")
    lines.extend(["","[Complete per-Assessment DAGs](variable-dags.json).",
                  "",
                  "Graph references are inferred structurally from literal variable",
                  "references; source OVAL lexical cardinality, set semantics and",
                  "Object/State scope must still be proven separately. A cycle-free",
                  "source DAG is NOT necessarily executable by the current B pilot.",""])
    return "\n".join(lines)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--authoring-zip",required=True,type=Path)
    ap.add_argument("--output",required=True,type=Path)
    ap.add_argument("--markdown",required=True,type=Path)
    args=ap.parse_args()
    docs,raw=read_source(args.authoring_zip)
    _,caps=import_corpus(docs,raw,expected_benchmarks=6)
    data=inventory(caps)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(data,sort_keys=True,indent=2)+"\n")
    args.markdown.parent.mkdir(parents=True,exist_ok=True)
    args.markdown.write_text(markdown(data))
    print(json.dumps({key:data[key] for key in
        ("assessments_with_variables","total_declared_variables",
         "max_declared_variable_chain_depth",
         "assessment_count_with_cycles")},indent=2))


if __name__=="__main__":
    main()
