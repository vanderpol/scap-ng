#!/usr/bin/env python3
"""Research audit: how much REAL 0.4 source passes native capability schemas?

Uses immutable 0.3 six-STIG authoring, the proven exact/source-model lowering
to the proposed one-grammar 0.4 representation, and the *generated 0.4 native*
Test schema per capability. Records precise failures; default is audit-only.
It never calls or claims a scanner and never downgrades native checks.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import zipfile

from jsonschema import Draft202012Validator
from referencing import Registry, Resource
import research_04_rhel9_compact_preview as corpus
from research_04_three_benchmark_quantifier import BENCHMARKS
from research_04_one_grammar_proof import make_single,benchmark_dir
from generate_capability_schema_v04 import generate

ROOT=Path(__file__).resolve().parents[1]
MAPPINGS=ROOT/"schema"/"v0.4.0"/"capability-mappings"/"supported"
SUPPORTED={p.stem:p for p in MAPPINGS.glob("*.json")}
SHARED={
    s["$id"]:s for p in (ROOT/"schema"/"v0.4.0").glob("*.schema.json")
    if (s:=json.loads(p.read_text(encoding="utf-8")))
}


def validator_for(capability,cache):
    if capability in cache:return cache[capability]
    mapping=json.loads(SUPPORTED[capability].read_text(encoding="utf-8"))
    schema=generate(mapping,ROOT)
    # Draft 2020-12 local references (for instance within filesystem
    # traversal and native collector schemas) need their own resource scope.
    # Legacy RefResolver can resolve them against the wrong external root in
    # unevaluatedProperties; use the official version-local Registry instead.
    registry=Registry().with_resources(
        (uri,Resource.from_contents(document))
        for uri,document in {**SHARED,schema["$id"]:schema}.items()
    )
    v=Draft202012Validator(
        {"$id":schema["$id"],"$defs":schema["$defs"],"$ref":"#/$defs/test"},
        registry=registry
    )
    cache[capability]=v
    return v


def audit(zip_path):
    reports={}
    cache={}
    with zipfile.ZipFile(zip_path) as z:
        folders={p.split("/")[1] for p in z.namelist()
                 if p.startswith("authoring/") and "/rules/" in p}
        for benchmark in BENCHMARKS:
            oldprefix=corpus.SOURCE_PREFIX
            corpus.SOURCE_PREFIX="authoring/"+benchmark_dir(folders,benchmark)+"/"
            try:
                docs,_=corpus.archive_contents(z)
            finally:
                corpus.SOURCE_PREFIX=oldprefix
            counts=Counter()
            by_capability=Counter()
            issue_types=Counter()
            samples=[]
            for path,original in sorted(docs.items()):
                a=(original or {}).get("assessment") if isinstance(original,dict) else None
                if not isinstance(a,dict) or a.get("mode")!="automated":continue
                source,_,normalizations=make_single(original)
                counts["assessments"]+=1
                if normalizations:counts["assessments_with_model_normalizations"]+=1
                all_valid=True
                for test_name,test in (source["assessment"].get("tests") or {}).items():
                    if not isinstance(test,dict):continue
                    counts["test_occurrences"]+=1
                    cap=test.get("capability")
                    if not isinstance(cap,str) or cap not in SUPPORTED:
                        counts["unsupported_capability_test"]+=1
                        by_capability[f"UNSUPPORTED {cap}"]+=1
                        all_valid=False
                        continue
                    v=validator_for(cap,cache)
                    found=list(v.iter_errors(test))
                    if not found:
                        counts["native_test_pass"]+=1
                        by_capability[f"PASS {cap}"]+=1
                    else:
                        counts["native_test_fail"]+=1
                        by_capability[f"FAIL {cap}"]+=1
                        all_valid=False
                        for err in found[:3]:
                            path_bits=".".join(map(str,err.absolute_path)) or "<root>"
                            label=f"{cap} | {path_bits} | {err.validator}"
                            issue_types[label]+=1
                            if len(samples)<90:
                                samples.append({
                                    "benchmark":benchmark,"file":path,
                                    "test":test_name,"capability":cap,
                                    "instance_path":list(map(str,err.absolute_path)),
                                    "schema_path":list(map(str,err.absolute_schema_path)),
                                    "message":err.message[:750],
                                    "suberrors":[{
                                        "path":list(map(str,child.path)),
                                        "message":child.message[:320],
                                    } for child in err.context[:6]],
                                    "require":test.get("require"),
                                    "object_excerpt":str(test.get("object"))[:1000],
                                })
                if all_valid:counts["assessments_all_native_tests_pass"]+=1
            reports[benchmark]={
                "counts":dict(counts),
                "test_status_by_capability":dict(by_capability),
                "top_error_kinds":[{"kind":k,"count":n} for k,n in issue_types.most_common(40)],
                "failure_samples":samples,
            }
    return {"status":"research only; 0.4 deep schema audit, not scanner parity",
            "source":"immutable 0.3 six-STIG authoring ZIP",
            "capabilities_compiled":len(cache),
            "benchmarks":reports,
            "limitations":[
                "Generic 0.4 authoring lowering is previously source-exact or separately reference-model-equivalent; generated deep schemas must be audited independently.",
                "No live SCAP-NG scanner is available or required in pre-alpha.",
                "Unknown or unmapped native Test types remain explicitly counted, not replaced by shell commands/manual.",
            ]}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-zip",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--strict",action="store_true",
                   help="Fail on any generated native Test mismatch (release gate, not initial research)")
    args=p.parse_args()
    result=audit(args.source_zip)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    bad=0
    for b,r in result["benchmarks"].items():
        print("DEEP_NATIVE_04",b,json.dumps(r["counts"],sort_keys=True),flush=True)
        print("DEEP_NATIVE_04_ERRORS",b,json.dumps(r["top_error_kinds"][:15]),flush=True)
        shown=set()
        for example in r["failure_samples"]:
            group=(example["capability"],str(example["instance_path"]))
            if group in shown:continue
            shown.add(group)
            if len(shown)>9:break
            print("DEEP_NATIVE_04_SAMPLE",b,json.dumps(example,sort_keys=True),flush=True)
        bad+=r["counts"].get("native_test_fail",0)+r["counts"].get("unsupported_capability_test",0)
    if bad and args.strict:raise SystemExit(f"{bad} unresolved deep native Test validation failures")


if __name__=="__main__":
    main()
