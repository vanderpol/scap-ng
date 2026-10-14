#!/usr/bin/env python3
"""Author diagnostic plan for existing SCAP-NG 0.3 Variable chains.

This generates static, implementation-neutral debug metadata only. It does
not evaluate a Variable or invent runtime observations, status or test truth.
"""
from __future__ import annotations
from collections import Counter, defaultdict
import csv
from pathlib import Path
import argparse
import hashlib
import json
import zipfile

import yaml
from research_04_flow_patterns import analyze_assessment

TRACE_FIELDS = (
    "input_status", "input_item_count", "output_value_count",
    "status", "complete", "error_reason", "source_item_lineage",
    "sampled_values", "samples_truncated", "redaction_applied",
)

def build_plan(document, *, source_path=""):
    a=document["assessment"]
    nodes=analyze_assessment(document)
    lookup={node["name"]:node for node in nodes}
    order=[]
    visiting=set()
    visited=set()
    missing=set()
    def visit(name):
        if name not in lookup:
            missing.add(name)
            return
        if name in visiting:
            raise ValueError("Variable dependency cycle: "+name)
        if name in visited:
            return
        visiting.add(name)
        for dep in lookup[name]["dependencies"]:
            visit(dep)
        visiting.remove(name)
        visited.add(name)
        order.append(name)
    for name in lookup:
        visit(name)
    def check_undefined_refs(node):
        if isinstance(node,list):
            for item in node:
                check_undefined_refs(item)
        elif isinstance(node,dict):
            for key,value in node.items():
                if key=="variable" and isinstance(value,str) and value not in lookup:
                    missing.add(value)
                else:
                    check_undefined_refs(value)
    for payload in (a.get("variables") or {}).values():
        check_undefined_refs(payload)
    reverse=defaultdict(list)
    for n in nodes:
        for dep in n["dependencies"]:
            reverse[dep].append(n["name"])
    out=[]
    hazards=Counter()
    depths={}
    for idx,name in enumerate(order,1):
        n=lookup[name]
        ops=n["operations"]
        inputs=n["dependencies"]
        source=n["source_objects"]
        reasons=[]
        depths[name]=1+max((depths.get(dep,0) for dep in inputs),default=0)
        if ops.get("concat") and len(inputs)+len(source)>1:
            reasons.append("concat_multiple_dynamic_sources__check_cardinality_and_product")
        if ops.get("regex_capture"):
            reasons.append("regex_capture__no_match_and_invalid_input_must_be_visible")
        if ops.get("merge") or ops.get("unique"):
            reasons.append("merge_or_unique__track_input_output_counts_and_lineage")
        if ops.get("split") or ops.get("substring"):
            reasons.append("text_transformation__track_empty_and_error_outcomes")
        if len(reverse[name])>1:
            reasons.append("intermediate_reused_in_multiple_derivations")
        for reason in reasons:
            hazards[reason]+=1
        out.append({
            "sequence":idx,
            "variable_id":name,
            "upstream_dependency_depth":depths[name],
            "datatype":n["datatype"],
            "kind":n["kind"],
            "operations":ops,
            "input_variables":inputs,
            "input_objects":source,
            "downstream_variables":sorted(reverse[name]),
            "direct_consumers":n["consumer_paths"],
            "debug_focus":reasons,
            # This is the metadata a FUTURE scanner could populate on request.
            # No fabricated runtime result appears in this authoring-time plan.
            "suggested_runtime_fields":list(TRACE_FIELDS),
        })
    serialized=yaml.safe_dump(document,sort_keys=True,allow_unicode=True)
    return {
        "research_type":"scap-ng-variable-debug-plan",
        "not_runtime_evidence":True,
        "assessment_id":a["id"],
        "source_path":source_path,
        "source_structure_sha256":hashlib.sha256(serialized.encode()).hexdigest(),
        "stage_count":len(out),
        "longest_variable_chain":max(depths.values(),default=0),
        "stage_order_proven_acyclic":True,
        "unresolved_variable_refs":sorted(missing),
        "potential_debug_hazard_counts":dict(hazards),
        "stages":out,
    }

def run(zip_path,study):
    stats=json.loads((study/"STATS.json").read_text())
    summary=Counter()
    depth_by_benchmark=defaultdict(list)
    variable_assessments=Counter()
    with zipfile.ZipFile(zip_path) as z:
        scoped=set()
        with (study/"ALL-VARIABLES.csv").open(newline="",encoding="utf-8") as fd:
            for row in csv.DictReader(fd):
                scoped.add((row["benchmark"],row["source_path"]))
        for benchmark,path in sorted(scoped):
            doc=yaml.safe_load(z.read("authoring/"+path))
            plan=build_plan(doc,source_path=path)
            depth_by_benchmark[benchmark].append(plan["longest_variable_chain"])
            variable_assessments[benchmark]+=1
        for case in stats["examples"]:
            folder=study/case["folder"]
            doc=yaml.safe_load((folder/"current-0.3.assessment.yaml").read_text(encoding="utf8"))
            if not (doc["assessment"].get("variables") or {}):
                continue
            plan=build_plan(doc,source_path=case["folder"])
            (folder/"VARIABLE-DEBUG-PLAN.yaml").write_text(
                "# Research-only stage map, NOT observed scanner data or approved results schema.\n"
                +yaml.safe_dump(plan,sort_keys=False,allow_unicode=True))
            summary["paired_plans"]+=1
            summary["paired_stages"]+=plan["stage_count"]
            if case["benchmark"]=="apache_server_2-4_unix_server":
                summary["apache_paired_stages"]+=plan["stage_count"]
            summary["unresolved_refs"]+=len(plan["unresolved_variable_refs"])
            summary.update({"hazard_"+k:v for k,v in plan["potential_debug_hazard_counts"].items()})
    report={
        "status":"research_trace_planning_only",
        "paired_diagnostic_plans":summary["paired_plans"],
        "paired_stage_occurrences":summary["paired_stages"],
        "apache_paired_stage_occurrences":summary["apache_paired_stages"],
        "unresolved_references":summary["unresolved_refs"],
        "full_release_dependency_chains_by_benchmark":{
            key:{
                "assessments_with_variables":len(values),
                "max_dependency_chain":max(values,default=0),
                "median_dependency_chain":sorted(values)[len(values)//2],
                "assessments_with_chain_depth_4_or_more":sum(v>=4 for v in values),
            } for key,values in depth_by_benchmark.items()},
        "debug_hazard_occurrences":{k.removeprefix("hazard_"):v for k,v in summary.items()
                                   if k.startswith("hazard_")},
        "runtime_trace_data_observed":False,
        "no_change_to_scan_verdict":True,
        "recommendation":"Optional per-Variable diagnostic summary plus bounded redacted samples, preserving source Item lineage and completeness; opt-in outside normal minimal results.",
    }
    (study/"VARIABLE-DEBUG-STATS.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    (study/"VARIABLE-DEBUG-DESIGN.md").write_text(
        "# Variable debugging without changing assessment semantics\n\n"
        "**Research only**. Complex Variables are a dataflow and diagnostics problem, "
        "not merely an authoring-line-count problem.\n\n"
        "1. At build time, generate a deterministic ordered list of derived-value "
        "stages: input Objects, input Variables, operations, datatype, consumers.\n"
        "2. In *optional* scanner debug output, report the status and completeness "
        "of each stage plus input/output counts, bounded sample values, redaction, "
        "failure reason and source-Item lineage. Do not fabricate or assume zero/empty "
        "means success. Keep normal results compact.\n"
        "3. On a failed Rule, show the earliest relevant failed/incomplete producer, "
        "then the dependent operations and the final failed comparison. Multiple "
        "causes or incomplete evidence must not be flattened to a false single root cause.\n"
        "4. Preserve OVAL and SCAP-NG error, unknown, not-applicable and "
        "not-evaluated behavior; debugging SHALL NOT change the result.\n"
        "5. Support multi-valued streams and independent concatenation; show counts "
        "and lineage rather than interpreting a list as one scalar or assuming zipped "
        "pairing. The partial/interrupted collection path needs explicit diagnostics.\n"
        "6. Keep organizational inputs separate from scanner acquisition or the "
        "diagnostic request; redact values according to existing reported-elements "
        "and product security policies.\n\n"
        "Each source-paired case includes `VARIABLE-DEBUG-PLAN.yaml`. It contains "
        "no fabricated runtime values. Live scanner trace collection and differential "
        "truth testing remain unproven and outside this research prototype.\n")
    print(json.dumps(report,indent=2,sort_keys=True))
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--authoring-zip",type=Path,required=True)
    p.add_argument("--study",type=Path,required=True)
    a=p.parse_args()
    run(a.authoring_zip,a.study)

if __name__=="__main__":
    main()
