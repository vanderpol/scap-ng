#!/usr/bin/env python3
"""Measure current SCAP-NG evaluate-tree shapes in generated Assessment YAML."""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import yaml


OPS={"all","any","one","odd","not","if","then","else","test","assessment","not_applicable"}


def walk_expr(node: Any, depth: int=1):
    yield node,depth
    if not isinstance(node,dict):
        return
    if "test" in node or "assessment" in node or "not_applicable" in node:
        return
    if "not" in node:
        yield from walk_expr(node["not"],depth+1)
        return
    if "all" in node or "any" in node or "one" in node or "odd" in node:
        key=next(k for k in ("all","any","one","odd") if k in node)
        for child in node[key]:
            yield from walk_expr(child,depth+1)
        return
    if "if" in node:
        for key in ("if","then","else"):
            if key in node:
                yield from walk_expr(node[key],depth+1)


def expr_root(node: Any)->str:
    if not isinstance(node,dict) or len(node)!=1:
        return "other"
    return next(iter(node))


def leaf_refs(node: Any):
    tests=[]
    assessments=[]
    for part,_ in walk_expr(node):
        if isinstance(part,dict):
            if isinstance(part.get("test"),str):
                tests.append(part["test"])
            if isinstance(part.get("assessment"),str):
                assessments.append(part["assessment"])
    return tests,assessments


def is_flat_operator(node: Any)->bool:
    if not isinstance(node,dict) or len(node)!=1:
        return False
    key=next(iter(node))
    if key not in {"all","any","one","odd"}:
        return False
    vals=node[key]
    return isinstance(vals,list) and vals and all(
        isinstance(x,dict) and set(x)=={"test"} and isinstance(x["test"],str)
        for x in vals
    )


def analyze_assessment(path:Path,doc:dict)->dict:
    a=doc["assessment"]
    tests=a.get("tests") or {}
    evaluate=a.get("evaluate")
    test_refs,assessment_refs=leaf_refs(evaluate)
    max_depth=max((depth for _,depth in walk_expr(evaluate)),default=0)
    node_count=sum(1 for _ in walk_expr(evaluate))
    root=expr_root(evaluate)
    trivial_single=(
        len(tests)==1
        and isinstance(evaluate,dict)
        and set(evaluate)=={"test"}
        and evaluate.get("test") in tests
    )
    repeated_test_refs=sum(c-1 for c in Counter(test_refs).values() if c>1)
    unreferenced_tests=sorted(set(tests)-set(test_refs))
    return {
        "path":str(path),
        "assessment_id":a.get("id"),
        "test_count":len(tests),
        "evaluate_root":root,
        "evaluate_nodes":node_count,
        "evaluate_depth":max_depth,
        "test_leaf_refs":len(test_refs),
        "assessment_leaf_refs":len(assessment_refs),
        "trivial_single_test_evaluate":trivial_single,
        "flat_test_operator":is_flat_operator(evaluate),
        "repeated_test_ref_occurrences":repeated_test_refs,
        "unreferenced_tests":unreferenced_tests,
    }


def bucket_tests(n:int)->str:
    if n==0:return "0"
    if n==1:return "1"
    if n==2:return "2"
    if n<=5:return "3-5"
    return "6+"


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("root",type=Path)
    ap.add_argument("--label",required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()

    rows=[]
    for path in sorted(args.root.rglob("*.assessment.yaml")):
        try:
            doc=yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(doc,dict) or not isinstance(doc.get("assessment"),dict):
            continue
        a=doc["assessment"]
        if a.get("mode")!="automated" or "evaluate" not in a:
            continue
        aid=str(a.get("id") or "")
        # Focus on Rule Assessments; applicability/platform helpers are a
        # separate composition use case and can be measured later.
        if ".SV-" not in aid and not aid.startswith("SV-"):
            continue
        rows.append(analyze_assessment(path,doc))

    root_counts=Counter(r["evaluate_root"] for r in rows)
    test_buckets=Counter(bucket_tests(r["test_count"]) for r in rows)
    total=len(rows)
    trivial=sum(r["trivial_single_test_evaluate"] for r in rows)
    flat=sum(r["flat_test_operator"] for r in rows)
    nested=sum(r["evaluate_depth"]>2 for r in rows)
    repeated=sum(r["repeated_test_ref_occurrences"]>0 for r in rows)
    unreferenced=sum(bool(r["unreferenced_tests"]) for r in rows)

    report={
        "format":"scap-ng-evaluate-shape-census-0.1",
        "status":"research_only_not_accepted_design",
        "label":args.label,
        "summary":{
            "assessments":total,
            "evaluate_root_counts":dict(root_counts),
            "test_count_buckets":dict(test_buckets),
            "trivial_single_test_evaluate":trivial,
            "trivial_single_test_percent":round(100*trivial/total,1) if total else 0,
            "flat_test_operator":flat,
            "flat_test_operator_percent":round(100*flat/total,1) if total else 0,
            "nested_evaluate_depth_gt_2":nested,
            "nested_evaluate_percent":round(100*nested/total,1) if total else 0,
            "assessments_with_repeated_test_refs":repeated,
            "assessments_with_unreferenced_tests":unreferenced,
            "max_evaluate_depth":max((r["evaluate_depth"] for r in rows),default=0),
            "max_evaluate_nodes":max((r["evaluate_nodes"] for r in rows),default=0),
        },
        "assessments":rows,
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(report["summary"],indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
