#!/usr/bin/env python3
"""Refs #245. Original OVAL 5.12.3 Variable consumers, NOT native C coverage.

Account for every Variable and its source-compatible Object/State/derived-value
uses in the 68 independently verified native-C Variable-blocked Definitions.
A Variable can have more than one use/role: never infer exclusive categories
or silently convert a collector-binding Variable into an expected State.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path

CATEGORIES=(
    "runtime_derived",
    "constant_collection_binding",
    "constant_derived_dependency",
    "constant_single_state_expectation",
    "constant_shared_state_expectation",
    "constant_other",
)


def references(node, var_id, path=()):
    if isinstance(node, dict):
        if node == {"variable": var_id}:
            yield path
        for key, value in node.items():
            yield from references(value,var_id,path+(key,))
    elif isinstance(node,list):
        for i,value in enumerate(node):
            yield from references(value,var_id,path+(i,))


def classify(variable, paths):
    if variable.get("kind")=="local":
        return "runtime_derived"
    if variable.get("kind")!="constant":
        raise ValueError("unknown original OVAL Variable kind; do not infer")
    roles=Counter(path[0] for path in paths)
    if roles["objects"]:
        return "constant_collection_binding"
    if roles["variables"]:
        return "constant_derived_dependency"
    if roles["states"]:
        return ("constant_single_state_expectation" if
                len(paths)==1 else "constant_shared_state_expectation")
    return "constant_other"


def variable_census(review, manifest):
    if manifest.get("stage") != "SOURCE_BACKED_NATIVE_C_SUBSET_NOT_SCANNER_PARITY":
        raise ValueError("unverified C original-source disposition")
    blockers={(x["file"],x["definition_id"])
              for x in manifest["unsupported"] if x["reason"].startswith(
                  "VARIABLE_SOURCE_GRAPH_NEEDS_COMPATIBILITY")}
    if len(blockers)!=sum(1 for x in manifest["unsupported"] if x[
            "reason"].startswith("VARIABLE_SOURCE_GRAPH_NEEDS_COMPATIBILITY")):
        raise ValueError("repeated source Definition identity")
    found={}
    for f in Path(review).glob("*.review.json"):
        data=json.loads(f.read_text(encoding="utf-8"))
        origin=data.get("source",{})
        key=(origin.get("file"),origin.get("definition_id"))
        if key in blockers:
            if key in found:
                raise ValueError("duplicate original OVAL source review")
            found[key]=data["A_source_compatibility_fallback"]
    if set(found)!=blockers:
        raise ValueError("missing original OVAL Variable source review")
    totals=Counter()
    definitions=defaultdict(set)
    examples=defaultdict(list)
    shared_contexts=Counter()
    for key, a in sorted(found.items()):
        variables=a.get("variables")
        if not isinstance(variables,dict) or not variables:
            raise ValueError("source Variable blocker without a Variable graph")
        outside={k:v for k,v in a.items() if k!="variables"}
        for vid,v in sorted(variables.items()):
            if type(vid) is not str or not isinstance(v,dict):
                raise ValueError("invalid original Variable declaration")
            uses=list(references(outside,vid))
            dependencies=list(references(variables,vid,("variables",)))
            uses+=dependencies
            category=classify(v,uses)
            totals[category]+=1
            definitions[category].add(key)
            consumer_kinds=sorted(set(u[0] for u in uses))
            if len(consumer_kinds)>1:
                shared_contexts[",".join(consumer_kinds)]+=1
            if len(examples[category])<5:
                examples[category].append({
                    "source_file":key[0],"definition_id":key[1],
                    "source_variable":vid,"consumers":consumer_kinds,
                    "references":len(uses)})
    return {
        "stage":"ORIGINAL_SOURCE_VARIABLE_USAGE_NOT_SCANNER_OR_NATIVE_C_PARITY",
        "blocked_source_definitions":len(blockers),
        "variable_declarations":sum(totals.values()),
        "variable_roles":{k:totals[k] for k in CATEGORIES},
        "definition_membership_by_role":{
            k:len(definitions[k]) for k in CATEGORIES},
        "multi_context_variables":dict(sorted(shared_contexts.items())),
        "examples":{k:examples[k] for k in CATEGORIES},
        "authoring_optimization_not_automatically_safe":True,
        "new_native_C_conversions_proven":0,
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--review",type=Path,required=True)
    p.add_argument("--manifest",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    report=variable_census(a.review,json.loads(a.manifest.read_text(encoding="utf-8")))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n",
                     encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k!="examples"},sort_keys=True))


if __name__=="__main__":
    main()
