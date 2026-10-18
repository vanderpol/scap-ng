#!/usr/bin/env python3
"""#237 compiler-owned source Variable DAG schedule (NO EVALUATION).

Normalizes dependency order for converted SCAP-NG 0.3 source local Variables,
retaining each original expression exactly. This is only a graph/planning
intermediate; it does NOT resolve values or establish OVAL variable semantics.
"""
from __future__ import annotations

import argparse
import copy
from hashlib import sha256
import json
from pathlib import Path
import yaml

from research_b_variable_dag_inventory import analyze_graph

FORMAT="scap-ng-b-source-variable-plan/0.1"
SOURCE_OPERATIONS={"concat","regex_capture","merge","unique",
                   "values","count","split","arithmetic","literal"}
MAX_VARS=512
MAX_EDGES=8192


def shared_object_references(value):
    """Collect named shared Object references without resolving acquisitions."""
    found=set()
    def walk(node):
        if isinstance(node,dict):
            for key,value in node.items():
                if key=="object" and type(value) is str:
                    found.add(value)
                walk(value)
        elif isinstance(node,list):
            for entry in node:walk(entry)
    walk(value)
    return found


def plan_source_variables(assessment):
    if not isinstance(assessment,dict) or type(assessment.get("id")) is not str:
        raise ValueError("source Assessment id required for Variable DAG plan")
    source=assessment.get("variables")
    if not isinstance(source,dict) or not source or len(source)>MAX_VARS:
        raise ValueError("source Variable schedule requires bounded local graph")
    shared=assessment.get("shared_objects",{})
    if not isinstance(shared,dict) or len(shared)>MAX_VARS:
        raise ValueError("source shared Object definitions must be bounded mapping")
    raw_object_refs=shared_object_references({
        "variables":source,"tests":assessment.get("tests",{})})
    missing=raw_object_refs-set(shared)
    if missing:
        raise ValueError("source Variable/Test references unresolved shared Objects: "+
                         repr(sorted(missing)))
    g=analyze_graph(assessment)
    if g["cycle_nodes"]:
        raise ValueError("cyclic source Variable references: "+repr(g["cycle_nodes"]))
    if g["external_dependencies"] or g["unbound_test_variables"]:
        raise ValueError("source Variable DAG has unresolved references")
    if g["malformed_expressions"] or g["max_variable_depth"]>64:
        raise ValueError("malformed or excessively deep source Variable graph")
    if sum(len(x) for x in g["dependencies"].values())>MAX_EDGES:
        raise ValueError("source Variable graph exceeds dependency edge cap")
    pending={key:set(deps) for key,deps in g["dependencies"].items()}
    result=[]
    while pending:
        available=sorted(key for key,deps in pending.items() if not deps)
        if not available:
            raise ValueError("source Variable scheduler encountered cycle")
        for key in available:
            raw=source[key]
            expression=raw["expression"]
            op=next(iter(expression))
            if op not in SOURCE_OPERATIONS:
                raise ValueError("unsupported source Variable operator "+str(op))
            result.append({
                "id":key,
                "operator":op,
                "depends_on":g["dependencies"][key],
                "source_expression":copy.deepcopy(expression),
                "source_datatype":raw.get("datatype"),
                "source_kind":raw.get("kind"),
            })
            del pending[key]
        for deps in pending.values():
            deps.difference_update(available)
    result_ids=[r["id"] for r in result]
    if len(result_ids)!=len(set(result_ids)) or set(result_ids)!=set(source):
        raise ValueError("source Variable graph coverage is incomplete")
    positions={name:i for i,name in enumerate(result_ids)}
    for item in result:
        if any(positions[dep]>=positions[item["id"]] for dep in item["depends_on"]):
            raise ValueError("variable source dependency ordered after consumer")
    fingerprint=sha256(json.dumps(source,sort_keys=True,separators=(",",":"),
                                 ensure_ascii=False).encode("utf-8")).hexdigest()
    return {
        "format":FORMAT,
        "source_assessment_id":assessment["id"],
        "original_source_parity_verified":False,
        "execution_supported":False,
        "note":"structural Variable dependency plan, no acquisition or evaluation",
        "source_variables_sha256":fingerprint,
        "referenced_shared_object_ids":sorted(raw_object_refs),
        "source_shared_objects":copy.deepcopy(shared),
        "source_shared_objects_sha256":sha256(
            json.dumps(shared,sort_keys=True,separators=(",",":"),
                       ensure_ascii=False).encode("utf-8")).hexdigest(),
        "test_variable_references":g["test_variables"],
        "max_variable_depth":g["max_variable_depth"],
        "nodes":result,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    args=p.parse_args()
    document=yaml.safe_load(args.source.read_text())
    plan=plan_source_variables(document["assessment"])
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(plan,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"assessment":plan["source_assessment_id"],
                      "variables":len(plan["nodes"]),
                      "depth":plan["max_variable_depth"],
                      "executable":False},sort_keys=True))


if __name__=="__main__":
    main()
