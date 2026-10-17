#!/usr/bin/env python3
"""#235: 0.4-B full six-stream *source-feature inventory*, NOT conversion.

Reads the already verified 0.3 six-stream authoring archive via the structural
B importer. Reports EVERY referenced Assessment and every Rule choice,
representative structural keys, and test capability names. This is a lossless
accounting aid, not an OVAL source runtime or an A/B bake-off scorecard.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
import json
from pathlib import Path
from research_b_full_corpus_import import (
    SOURCE_TAG,read_source,import_corpus,digest
)

FORMAT="requirements-first-B-feature-inventory/0.1-research"
# These are presence markers in *parsed source YAML keys*, not proven source
# semantic operators. Do not read 'variable' markers as OVAL variable count.
MARKERS=(
    "foreach","for_each","if","elseif","else","then",
    "union","intersection","intersect","difference","filter",
    "record","records","states","state","fields","field",
    "objects","object","variables","variable",
    "source","sources","using","evaluate",
    "manual","evidence","organization_input","organizational_input",
    "regex","matches_regex","exactly_one","one_or_more","all_exist",
    "not_applicable","exists","existence","check",
)
MARKER_SET=set(MARKERS)

def walk_keys(obj):
    """Yield source mapping keys recursively; never inspect description text."""
    if isinstance(obj,dict):
        for key,val in obj.items():
            if isinstance(key,str):
                yield key
            yield from walk_keys(val)
    elif isinstance(obj,(tuple,list)):
        for val in obj:
            yield from walk_keys(val)

def test_summary(assessment):
    tests=assessment.get("tests")
    if tests is None:
        return 0, [],"tests_absent"
    if isinstance(tests,dict):
        values=list(tests.values())
    elif isinstance(tests,list):
        values=tests
    else:
        return 0, [],"tests_shape_unsupported"
    cap=[]
    unknown=0
    for v in values:
        if not isinstance(v,dict):
            unknown+=1
            continue
        c=v.get("capability")
        if isinstance(c,str) and c:
            cap.append(c)
        else:
            unknown+=1
    if unknown:
        return len(values),cap,"capability_missing_or_nested"
    return len(values),cap,"recognized"

def feature_inventory(report,capsules):
    """Compile per-benchmark source feature presence and typed choice closure.

    Capsule verification is done by caller importer. A feature inventory MUST
    account for all referenced Assessment IDs per source Rule, even shared.
    """
    lookup={x["assessment_id"]:capsules[x["assessment_id"]]
            for rule in report["rules"] for x in rule["choices"]}
    if lookup.keys()!=capsules.keys():
        raise ValueError("source Assessment closure mismatches importer")
    per_benchmark={}
    all_seen={}
    for benchmark in report["source_benchmark_names"]:
        rules=[r for r in report["rules"] if r["benchmark"]==benchmark]
        bound=defaultdict(set)
        mode_counts=Counter()
        source_keys=Counter()
        capabilities=Counter()
        status=Counter()
        marker_assessments=defaultdict(list)
        test_count=0
        for rule in rules:
            if not rule["choices"]:
                raise ValueError("unbound source Rule: "+rule["rule_id"])
            for choice in rule["choices"]:
                bound[choice["assessment_id"]].add(rule["rule_id"])
        for aid in sorted(bound):
            source=capsules[aid]["source_document"]
            original=source.get("assessment")
            if not isinstance(original,dict):
                raise ValueError("referenced Assessment has no assessment mapping: "+aid)
            if original.get("id")!=aid:
                raise ValueError("capsule assessment ID mismatch: "+aid)
            n,cap,condition=test_summary(original)
            test_count+=n
            status[condition]+=1
            capabilities.update(cap)
            mode_counts[str(original.get("mode","missing"))]+=1
            present={k.lower() for k in walk_keys(source)}
            for key in sorted(present&MARKER_SET):
                source_keys[key]+=1
                if len(marker_assessments[key])<5:
                    marker_assessments[key].append(aid)
            all_seen[aid]=capsules[aid]["source_parsed_sha256"]
        per_benchmark[benchmark]={
            "rules":len(rules),
            "referenced_unique_assessments":len(bound),
            "referenced_test_nodes_not_deduplicated_across_benchmarks":test_count,
            "assessment_modes":dict(sorted(mode_counts.items())),
            "test_structure_status":dict(sorted(status.items())),
            "capability_counts":dict(sorted(capabilities.items())),
            "assessment_key_presence":dict(sorted(source_keys.items())),
            "marker_example_ids":dict(sorted(marker_assessments.items())),
            "source_unresolved_references":0,
        }
    if len(all_seen)!=len(capsules):
        raise ValueError("full six-stream feature inventory did not include every Assessment")
    actual_benchmarks=len(per_benchmark)
    return {
        "format":FORMAT,
        "source_tag":SOURCE_TAG,
        "source_basis":"previously converted SCAP-NG 0.3 authoring ZIP, not raw SCAP 1.4 XML",
        "status":"source_inventory_only_NO_native_or_compatibility_runtime",
        "benchmarks":per_benchmark,
        "total_unique_assessments":len(all_seen),
        "total_rules":len(report["rules"]),
        "total_assessment_choice_bindings":sum(len(r["choices"]) for r in report["rules"]),
        "total_tests_in_unique_assessments":sum(
            test_summary(c["source_document"]["assessment"])[0]
            for c in capsules.values()),
        "native_verified_execution_count":0,
        "compatibility_verified_execution_count":0,
        "source_equivalence_verified":False,
        "all_assessment_source_sha256":digest(all_seen),
        "marker_legend":"presence of parsed YAML mapping key per Assessment, not OVAL operation equivalence",
    }

def markdown(doc):
    lines=["# 0.4-B six-STIG feature coverage inventory","",
           "**Research-only corpus profile. Not native translation, not source-equivalent",
           "execution, and not an A/B comparison.** Input: published SCAP-NG 0.3",
           "six-STIG authoring archive, *not* raw SCAP 1.4 XML.","",
           "| Stream | Rules | Referenced Assessments | Test nodes |",
           "| --- | ---: | ---: | ---: |"]
    for name,row in sorted(doc["benchmarks"].items()):
        lines.append("| "+name+" | "+str(row["rules"])+" | "+
                     str(row["referenced_unique_assessments"])+" | "+
                     str(row["referenced_test_nodes_not_deduplicated_across_benchmarks"])+" |")
    lines.extend(["",
      "**"+str(doc["total_unique_assessments"])+" distinct Assessment IDs** are",
      "covered across six source streams; shared Assessments are counted once",
      "globally but can appear in more than one stream's row.","",
      "## Capability names and structural markers by stream","",
      "Values below count **referenced Assessments with a marker key**, not",
      "execution paths or runtime equivalence. Complete details, all discovered",
      "capability names, source digests and representative IDs are in",
      "[feature-inventory.json](feature-inventory.json).",""])
    for name,row in sorted(doc["benchmarks"].items()):
        lines.extend(["### "+name,"",
             "Test capability names: "+
             (", ".join(k+" ("+str(v)+")" for k,v in
                       sorted(row["capability_counts"].items(),
                              key=lambda kv:(-kv[1],kv[0]))[:12])
              or "(no directly declared capability names)"),
             "",
             "Key-presence markers: "+
             (", ".join(k+" ("+str(v)+")" for k,v in
                        sorted(row["assessment_key_presence"].items(),
                               key=lambda kv:(-kv[1],kv[0]))[:18])
              or "(none of predefined keys detected)"),""])
    lines.extend(["## Hard boundary","",
      "No assessed source here is marked native-converted or executable.",
      "No source Test/State/Object/Variable semantic parity is asserted.",
      "This inventory is a B development input: next implement the features",
      "and compatibility IR families against pinned source fixtures before",
      "claiming B's six-content-stream capability readiness.",
      "The A/B bake-off remains postponed.",""])
    return "\n".join(lines)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--authoring-zip",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--markdown",type=Path)
    args=p.parse_args()
    source,sha=read_source(args.authoring_zip)
    report,capsules=import_corpus(source,sha)
    result=feature_inventory(report,capsules)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    if args.markdown:
        args.markdown.parent.mkdir(parents=True,exist_ok=True)
        args.markdown.write_text(markdown(result))
    print(json.dumps({"source_benchmarks":len(result["benchmarks"]),
                      "unique_assessments":result["total_unique_assessments"],
                      "source_tests":result["total_tests_in_unique_assessments"],
                      "verified_native":0},sort_keys=True))
if __name__=="__main__":main()
