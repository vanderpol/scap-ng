#!/usr/bin/env python3
"""Measure repeated Apache authoring nodes across converted Assessments."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml

NONSEMANTIC={"title","object_title","state_title","test_title","variable_title",
             "provenance","migration_provenance","source_id"}

def canonical_payload(value:Any)->Any:
    if isinstance(value,dict):
        return {
            k:canonical_payload(v)
            for k,v in sorted(value.items())
            if k not in NONSEMANTIC
        }
    if isinstance(value,list):
        return [canonical_payload(v) for v in value]
    return value

def digest(value:Any)->str:
    raw=json.dumps(canonical_payload(value),sort_keys=True,separators=(",",":"))
    return hashlib.sha256(raw.encode()).hexdigest()

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("root",type=Path)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()

    rows=[]
    by_kind_name=defaultdict(lambda: defaultdict(list))
    for path in sorted(args.root.rglob("*.assessment.yaml")):
        try:
            doc=yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        a=(doc or {}).get("assessment") or {}
        aid=str(a.get("id") or "")
        if a.get("mode")!="automated" or not a.get("tests"):
            continue
        rows.append({"path":str(path),"assessment_id":aid})
        for kind in ("objects","variables","states"):
            registry=a.get(kind) or {}
            if not isinstance(registry,dict):
                continue
            for name,payload in registry.items():
                if isinstance(payload,dict):
                    by_kind_name[kind][name].append({
                        "assessment_id":aid,
                        "hash":digest(payload),
                    })

    repeated={}
    for kind,names in by_kind_name.items():
        out=[]
        for name,uses in names.items():
            if len(uses)<2:
                continue
            hashes=sorted({u["hash"] for u in uses})
            out.append({
                "name":name,
                "assessments":len(uses),
                "distinct_payloads":len(hashes),
                "identical_across_uses":len(hashes)==1,
                "examples":[u["assessment_id"] for u in uses[:8]],
            })
        repeated[kind]=sorted(
            out,
            key=lambda x:(-x["assessments"],x["distinct_payloads"],x["name"])
        )

    identical_variables=[x for x in repeated.get("variables",[]) if x["identical_across_uses"]]
    identical_objects=[x for x in repeated.get("objects",[]) if x["identical_across_uses"]]
    report={
        "format":"scap-ng-apache-authoring-reuse-0.1",
        "status":"research_only_not_accepted_design",
        "automated_assessments":len(rows),
        "summary":{
            "repeated_identical_variable_names":len(identical_variables),
            "repeated_identical_object_names":len(identical_objects),
            "variable_occurrences_covered_by_identical_reuse":sum(x["assessments"] for x in identical_variables),
            "object_occurrences_covered_by_identical_reuse":sum(x["assessments"] for x in identical_objects),
        },
        "top_repeated":repeated,
        "assessments":rows,
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        "automated_assessments":len(rows),
        **report["summary"],
        "top_variables":identical_variables[:20],
        "top_objects":identical_objects[:15],
    },indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
