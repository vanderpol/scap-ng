#!/usr/bin/env python3
"""#237: exact six-STIG source-shape blocker census for the B conversion work.

Structural feature labels, NOT proof of OVAL compatibility or native support.
Counts de-duplicate shared Assessments globally and track per-stream usage.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
import json
from pathlib import Path

from research_b_full_corpus_import import import_corpus,read_source
from research_b_six_stream_compiler import build_six_stream_report,READY_STATUS


def walk_keys(value):
    if isinstance(value,dict):
        for k,v in value.items():
            yield k
            yield from walk_keys(v)
    elif isinstance(value,list):
        for child in value:
            yield from walk_keys(child)


def describe_assessment(capsule):
    a=capsule["source_document"]["assessment"]
    tests=a.get("tests")
    if not isinstance(tests,dict):
        tests={}
    caps=sorted({t.get("capability","(missing)") for t in tests.values()
                 if isinstance(t,dict)})
    observed=set(walk_keys(a))
    flags={
        "multiple_tests":len(tests)>1,
        "states":"states" in observed,
        "variables":"variables" in observed or "variable" in observed,
        "shared_objects":"shared_objects" in observed,
        "for_each":"for_each" in observed,
        "set_or_filter":"filter" in observed or "set" in observed,
        "record":"record" in observed,
        "value_match":"value_match" in observed,
    }
    return caps,flags,len(tests)


def assess_backlog(report,capsules):
    index={a["assessment_id"]:a for a in report["assessments"]}
    if set(index)!=set(capsules):
        raise ValueError("source and conversion index disagree")
    rows=[]
    by_cap=Counter()
    by_stream_cap=defaultdict(Counter)
    by_features=Counter()
    for aid in sorted(capsules):
        doc=capsules[aid]["source_document"].get("assessment",{})
        if doc.get("mode")!="automated":
            continue
        ent=index[aid]
        if ent["conversion_status"]==READY_STATUS:
            continue
        caps,features,test_count=describe_assessment(capsules[aid])
        for cap in caps:
            by_cap[cap]+=1
            for stream in ent["benchmark_streams"]:
                by_stream_cap[stream][cap]+=1
        for k,v in features.items():
            if v:by_features[k]+=1
        rows.append({
            "assessment_id":aid,
            "source_path":ent["source_path"],
            "benchmark_streams":ent["benchmark_streams"],
            "test_count":test_count,
            "capabilities":caps,
            "source_features":features,
            "lowering_rejection":ent["reason"],
        })
    return {
        "format":"scap-ng-b-six-stream-blockers/0.1",
        "source_tag":report["source_tag"],
        "unsupported_automated_assessments":len(rows),
        "capability_assessment_counts":dict(sorted(by_cap.items())),
        "source_feature_assessment_counts":dict(sorted(by_features.items())),
        "by_stream_capability_counts":{s:dict(sorted(v.items()))
                                       for s,v in sorted(by_stream_cap.items())},
        "unsupported_assessment_index":rows,
        "limitations":(
            "Capability and marker counts are overlapping source-structure "
            "frequencies, not executable conversions or scanner parity."),
    }


def render_markdown(report):
    lines=[
        "# SCAP-NG 0.4-B six-STIG automated source blockers",
        "",
        "**Source-shape inventory only; 0.4-B is NOT yet a complete converter.**",
        "Counts below are distinct *unsupported automated Assessments* referencing",
        "each capability/feature; a multi-Test Assessment may appear in multiple rows.",
        "",
        f"**Unsupported automated Assessments: {report['unsupported_automated_assessments']}**.",
        "",
        "## Highest-volume capability families",
        "",
        "| Source Test capability | Unsupported Assessments containing it |",
        "| --- | ---: |",
    ]
    for key,count in sorted(report["capability_assessment_counts"].items(),
                            key=lambda kv:(-kv[1],kv[0])):
        lines.append(f"| {key} | {count} |")
    lines.extend(["", "## Complex-source feature markers", "",
                  "| Feature | Unsupported Assessments containing it |",
                  "| --- | ---: |"])
    for key,count in sorted(report["source_feature_assessment_counts"].items(),
                            key=lambda kv:(-kv[1],kv[0])):
        lines.append(f"| {key} | {count} |")
    lines.extend(["","## Per-stream capability matrix",""])
    for stream,counts in report["by_stream_capability_counts"].items():
        lines.append(f"### {stream}")
        lines.append("")
        lines.append("| Capability | Referenced unsupported Assessments |")
        lines.append("| --- | ---: |")
        for cap,count in sorted(counts.items(),key=lambda kv:(-kv[1],kv[0])):
            lines.append(f"| {cap} | {count} |")
        lines.append("")
    lines.extend([
        "This is a **development queue**, not a reason to discard infrequent OVAL",
        "semantics. B may use proven native lowering or a correct compiler-owned",
        "compatibility operation, but the resulting content must actually execute.",
        "Original SCAP 1.4 XML/source parity and six-state scanner semantics",
        "are independent gates, currently open.",
        "",
        "The [machine-readable per-Assessment blockers](conversion-blockers.json)",
        "retain source paths and IDs. Full census: [conversion-progress](conversion-progress.md).",
        "Tracking: [#237](https://github.com/vanderpol/scap-ng/issues/237).",
        "",
    ])
    return "\n".join(lines)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--authoring-zip",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    p.add_argument("--markdown",required=True,type=Path)
    args=p.parse_args()
    docs,raw=read_source(args.authoring_zip)
    source,caps=import_corpus(docs,raw,expected_benchmarks=6)
    converted,_=build_six_stream_report(source,caps)
    output=assess_backlog(converted,caps)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(output,sort_keys=True,indent=2)+"\n")
    args.markdown.parent.mkdir(parents=True,exist_ok=True)
    args.markdown.write_text(render_markdown(output))
    print(json.dumps({
        "unsupported_automated_assessments":output["unsupported_automated_assessments"],
        "top_capabilities":sorted(output["capability_assessment_counts"].items(),
                                  key=lambda x:(-x[1],x[0]))[:10]},indent=2))


if __name__=="__main__":
    main()
