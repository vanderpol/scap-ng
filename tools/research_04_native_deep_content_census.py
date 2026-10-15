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
from copy import deepcopy
import json
from pathlib import Path
import zipfile

from jsonschema import Draft202012Validator
from referencing import Registry, Resource
import research_04_rhel9_compact_preview as corpus
from research_04_three_benchmark_quantifier import BENCHMARKS
from research_04_one_grammar_proof import make_single,benchmark_dir
from generate_capability_schema_v04 import generate
from migrate_v04_enum_selectors import migrate,restore

SIX_ANCHORS=(*BENCHMARKS,"oracle_linux_9","windows_server_dns","apache_2_4_unix")


def resolve_benchmark_dir(folders,benchmark):
    if benchmark in BENCHMARKS:
        return benchmark_dir(folders,benchmark)
    names={
        "oracle_linux_9":lambda n:"oracle" in n.lower() and "9" in n,
        "windows_server_dns":lambda n:"windows" in n.lower() and "dns" in n.lower(),
        "apache_2_4_unix":lambda n:"apache" in n.lower(),
    }
    match=[n for n in folders if names[benchmark](n)]
    if len(match)!=1:
        raise ValueError(
            f"Cannot uniquely locate {benchmark}: matched={match}; available={sorted(folders)}"
        )
    return match[0]

ROOT=Path(__file__).resolve().parents[1]
MAPPINGS=ROOT/"schema"/"v0.4.0"/"capability-mappings"/"supported"
SUPPORTED={p.stem:p for p in MAPPINGS.glob("*.json")}
SUPPORTED_MAPPING_DATA={name:json.loads(path.read_text(encoding="utf-8")) for name,path in SUPPORTED.items()}
SHARED={
    s["$id"]:s for p in (ROOT/"schema"/"v0.4.0").glob("*.schema.json")
    if (s:=json.loads(p.read_text(encoding="utf-8")))
}
ROOT_ASSESSMENT_SCHEMA=SHARED["https://scap-ng.dev/schema/v0.4.0/assessment.schema.json"]
ROOT_ASSESSMENT_REGISTRY=Registry().with_resources(
    (uri,Resource.from_contents(schema)) for uri,schema in SHARED.items()
)
ROOT_ASSESSMENT_VALIDATOR=Draft202012Validator(
    ROOT_ASSESSMENT_SCHEMA,registry=ROOT_ASSESSMENT_REGISTRY
)


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


def _variable_refs(node):
    if isinstance(node,dict):
        if isinstance(node.get("variable"),str):
            yield node
        for child in node.values():
            yield from _variable_refs(child)
    elif isinstance(node,list):
        for child in node:
            yield from _variable_refs(child)


def audit(zip_path,benchmarks=BENCHMARKS):
    reports={}
    cache={}
    with zipfile.ZipFile(zip_path) as z:
        folders={p.split("/")[1] for p in z.namelist()
                 if p.startswith("authoring/") and "/rules/" in p}
        for benchmark in benchmarks:
            oldprefix=corpus.SOURCE_PREFIX
            corpus.SOURCE_PREFIX="authoring/"+resolve_benchmark_dir(folders,benchmark)+"/"
            try:
                docs,_=corpus.archive_contents(z)
            finally:
                corpus.SOURCE_PREFIX=oldprefix
            counts=Counter()
            by_capability=Counter()
            issue_types=Counter()
            samples=[]
            root_failures=[]
            for path,original in sorted(docs.items()):
                a=(original or {}).get("assessment") if isinstance(original,dict) else None
                if not isinstance(a,dict) or a.get("mode")!="automated":continue
                source,_,normalizations=make_single(original)
                authored,migrations=migrate(source,SUPPORTED_MAPPING_DATA)
                if restore(authored,migrations)!=source:
                    raise ValueError(f"Enum-selector migration broke original source: {path}")
                counts["enum_selector_occurrences_explicitly_migrated"]+=len(migrations)
                for entry in migrations:
                    counts["enum_migration_"+entry.get(
                        "classification","unclassified"
                    )]+=1
                if migrations:counts["assessments_with_enum_migration"]+=1
                counts["assessments"]+=1
                if normalizations:counts["assessments_with_model_normalizations"]+=1
                # Confirm the complete authored Assessment, not merely its
                # separately generated native Test fragments, obeys the
                # independent v0.4.0 grammar. Version promotion is explicit;
                # do not rewrite the immutable 0.3 source input.
                promoted=deepcopy(authored)
                spec=(promoted["assessment"].get("specification") or {})
                if spec.get("version")!="0.3.0":
                    raise ValueError(f"Unexpected source spec for 0.4 migration: {path}: {spec}")
                spec["version"]="0.4.0"
                issues=list(ROOT_ASSESSMENT_VALIDATOR.iter_errors(promoted))
                if issues:
                    counts["full_assessment_schema_fail"]+=1
                    for issue in issues[:3]:
                        if len(root_failures)<90:
                            root_failures.append({
                                "benchmark":benchmark,"file":path,
                                "instance_path":list(map(str,issue.absolute_path)),
                                "schema_path":list(map(str,issue.absolute_schema_path)),
                                "validator":issue.validator,
                                "message":issue.message[:650],
                                "suberrors":[{"path":list(map(str,e.path)),
                                              "message":e.message[:250]}
                                             for e in issue.context[:4]],
                            })
                else:
                    counts["full_assessment_schema_pass"]+=1
                all_valid=True
                for test_name,test in (authored["assessment"].get("tests") or {}).items():
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
                                    # Diagnose source selector semantics before
                                    # choosing a 0.4 Variable syntax/quantifier.
                                    "variable_source_definitions": {
                                        name: (a.get("variables") or {}).get(name)
                                        for name in sorted({
                                            v.get("variable")
                                            for v in _variable_refs(test.get("object"))
                                            if isinstance(v.get("variable"),str)
                                        })
                                    } if cap=="windows.userright" else {},
                                })
                if all_valid:counts["assessments_all_native_tests_pass"]+=1
            reports[benchmark]={
                "counts":dict(counts),
                "test_status_by_capability":dict(by_capability),
                "top_error_kinds":[{"kind":k,"count":n} for k,n in issue_types.most_common(40)],
                "failure_samples":samples,
                "full_assessment_failure_samples":root_failures,
            }
    return {"status":"research only; 0.4 deep schema audit, not scanner parity",
            "source":"immutable 0.3 six-STIG authoring ZIP",
            "capabilities_compiled":len(cache),
            "benchmarks":reports,
            "limitations":[
                "Generic 0.4 authoring lowering is previously source-exact or separately reference-model-equivalent; generated deep schemas must be audited independently.",
                "No live SCAP-NG scanner is available or required in pre-alpha.",
                "Certified constant-full-enum Variable selections are structurally reversible, but their OVAL object value-check and exceptional-state equivalence still need independently sourced proof; do not count them as scanner parity.",
                "Unknown or unmapped native Test types remain explicitly counted, not replaced by shell commands/manual.",
            ]}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-zip",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--strict",action="store_true",
                   help="Fail on any generated native Test mismatch (release gate, not initial research)")
    p.add_argument("--six-anchor",action="store_true",
                   help="Audit all six published 0.3 anchors, not just the proven initial three")
    args=p.parse_args()
    result=audit(args.source_zip,SIX_ANCHORS if args.six_anchor else BENCHMARKS)
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
            if example.get("variable_source_definitions"):
                print("DEEP_NATIVE_04_VARIABLE_SOURCE",b,json.dumps(
                    example["variable_source_definitions"],sort_keys=True
                )[:5000],flush=True)
        for issue in r.get("full_assessment_failure_samples",[])[:7]:
            print("DEEP_NATIVE_04_FULL_DOCUMENT_ERROR",b,json.dumps(issue,sort_keys=True),flush=True)
        bad+=(r["counts"].get("native_test_fail",0)
              +r["counts"].get("unsupported_capability_test",0)
              +r["counts"].get("full_assessment_schema_fail",0))
    if bad and args.strict:raise SystemExit(f"{bad} unresolved deep native Test validation failures")


if __name__=="__main__":
    main()
