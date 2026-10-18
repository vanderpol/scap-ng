#!/usr/bin/env python3
"""#235: deterministic, bounded six-STIG SOURCE specimens for B development.

Select one small and one complex Assessment in each widespread source
capability family from the pinned published 0.3 six-STIG corpus. Publish
source excerpts on GitHub main to develop actual converters without relying
on inaccessible short-lived Actions artifacts. These ARE NOT native B
translations, executable Assessments, source-OVAL originals or parity proofs.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path
import re
import yaml
from research_b_full_corpus_import import read_source,import_corpus,digest

FAMILIES=(
  "independent.textfilecontent54",
  "windows.registry",
  "windows.userright",
  "independent.shellcommand",
  "linux.partition",
  "windows.wmi.query",
)
MAX_BYTES=50000
FORMAT="requirements-first-B-source-specimens/0.1-research"

def choose(report,capsules):
    """Use referencing rules as proof that specimens are live in the cohort."""
    binding=defaultdict(set)
    for row in report["rules"]:
        for c in row["choices"]:
            binding[c["assessment_id"]].add(row["benchmark"])
    if len(binding)!=len(capsules):
        raise ValueError("source Assessment closure is not complete")
    candidates=defaultdict(list)
    for aid,cap in sorted(capsules.items()):
        assessment=cap["source_document"].get("assessment")
        if not isinstance(assessment,dict):
            raise ValueError("source Assessment malformed: "+aid)
        tests=assessment.get("tests",{})
        if not isinstance(tests,dict):
            continue
        named=set()
        for value in tests.values():
            if isinstance(value,dict) and isinstance(value.get("capability"),str):
                named.add(value["capability"])
        if not named:continue
        body=yaml.safe_dump(cap["source_document"],sort_keys=True,allow_unicode=True)
        size=len(body.encode("utf-8"))
        if size>MAX_BYTES:
            continue
        for fam in named&set(FAMILIES):
            complexity=(len(tests),len(body),
                        len(cap["source_document"].get("metadata",{}).get("variables",{})))
            candidates[fam].append((size,complexity,aid,cap,body))
    selected={}
    warnings=[]
    for fam in FAMILIES:
        possible=sorted(candidates[fam],key=lambda t:(t[0],t[2]))
        if not possible:
            warnings.append("No bounded source specimen for "+fam)
            continue
        picks=[possible[0]]
        # Pick the largest still bounded specimen, to exercise advanced
        # structures without dumping multi-megabyte source documents.
        if len(possible)>1 and possible[-1][2]!=possible[0][2]:
            picks.append(possible[-1])
        for rank,(size,complexity,aid,cap,body) in enumerate(picks):
            if aid in selected:
                selected[aid]["families"].append(fam)
                continue
            suffix=sha256(aid.encode()).hexdigest()[:12]
            filename=fam.replace(".","-")+"-"+str(rank)+"-"+suffix+".source.yaml"
            selected[aid]={
                "id":aid,
                "source_path":cap["source_path"],
                "source_raw_sha256":cap["source_raw_sha256"],
                "source_parsed_sha256":cap["source_parsed_sha256"],
                "specimen_dump_sha256":sha256(body.encode()).hexdigest(),
                "families":[fam],
                "benchmarks":sorted(binding[aid]),
                "byte_count":size,
                "test_count":complexity[0],
                "file":filename,
                "content":body,
            }
    # The dominant source registry cohort is not the existing shortest/longest
    # sample: 135 / 190 registry Tests use a nested all State. Publish one
    # independently accounted, small, direct source Assessment of that form.
    # It is NOT a compiled B conversion or a verified original XML mapping.
    nested=[]
    for aid,cap in sorted(capsules.items()):
        if aid in selected:
            continue
        a=cap["source_document"].get("assessment",{})
        tests=a.get("tests",{})
        if a.get("mode")!="automated" or not isinstance(tests,dict) or len(tests)!=1:
            continue
        tid,t=next(iter(tests.items()))
        if (not isinstance(t,dict) or t.get("capability")!="windows.registry" or
            a.get("evaluate")!={"test":tid} or
            bool(a.get("variables")) or bool(a.get("shared_objects"))):
            continue
        states=t.get("states")
        if not isinstance(states,list) or len(states)!=1 or not isinstance(states[0],dict):
            continue
        conjunct=states[0].get("all")
        if not isinstance(conjunct,list) or len(conjunct)<2:
            continue
        obj=t.get("object")
        if not isinstance(obj,dict) or obj.get("capability")!="windows.registry":
            continue
        sel=obj.get("select")
        if not isinstance(sel,dict) or set(sel)!={"hive","key","name"}:
            continue
        body=yaml.safe_dump(cap["source_document"],sort_keys=True,allow_unicode=True)
        size=len(body.encode("utf-8"))
        if size>MAX_BYTES:
            continue
        nested.append((size,aid,cap,body))
    if nested:
        size,aid,cap,body=min(nested,key=lambda row:(row[0],row[1]))
        suffix=sha256(aid.encode()).hexdigest()[:12]
        selected[aid]={
            "id":aid,
            "source_path":cap["source_path"],
            "source_raw_sha256":cap["source_raw_sha256"],
            "source_parsed_sha256":cap["source_parsed_sha256"],
            "specimen_dump_sha256":sha256(body.encode()).hexdigest(),
            "families":["windows.registry/nested_state_all"],
            "benchmarks":sorted(binding[aid]),
            "byte_count":size,
            "test_count":1,
            "file":"windows-registry-state-all-"+suffix+".source.yaml",
            "content":body,
        }
    elif "No bounded nested registry State all source specimen" not in warnings:
        warnings.append("No bounded nested registry State all source specimen")
    # Platform breadth: the single smallest shellcommand family specimen is
    # Linux and the largest happens to be Apache. Publish a distinct smallest
    # *per-stream* source specimen for the two streams still at zero automated
    # fixture conversions. Do not infer the command can safely run.
    for stream,label in (("apache_server_2-4_unix_server","apache"),
                         ("ms_windows_server_dns","dns")):
        possible=[]
        for aid,cap in sorted(capsules.items()):
            if stream not in binding.get(aid,set()):
                continue
            assessment=cap["source_document"].get("assessment",{})
            tests=assessment.get("tests",{})
            if not isinstance(tests,dict) or not any(
                isinstance(test,dict) and
                test.get("capability")=="independent.shellcommand"
                for test in tests.values()):
                continue
            body=yaml.safe_dump(cap["source_document"],sort_keys=True,allow_unicode=True)
            size=len(body.encode("utf-8"))
            if size<=MAX_BYTES:
                possible.append((size,aid,cap,body,len(tests)))
        if not possible:
            continue
        size,aid,cap,body,test_count=min(possible,key=lambda row:(row[0],row[1]))
        if aid in selected:
            selected[aid]["families"].append("independent.shellcommand/"+label+"_small")
            continue
        suffix=sha256(aid.encode()).hexdigest()[:12]
        selected[aid]={
            "id":aid,
            "source_path":cap["source_path"],
            "source_raw_sha256":cap["source_raw_sha256"],
            "source_parsed_sha256":cap["source_parsed_sha256"],
            "specimen_dump_sha256":sha256(body.encode()).hexdigest(),
            "families":["independent.shellcommand/"+label+"_small"],
            "benchmarks":sorted(binding[aid]),
            "byte_count":size,
            "test_count":test_count,
            "file":"independent-shellcommand-"+label+"-small-"+suffix+".source.yaml",
            "content":body,
        }
    return selected,warnings

def build_manifest(picks,warnings):
    return {
      "format":FORMAT,
      "source_basis":"0.3 published authoring ZIP, not raw SCAP 1.4 XML",
      "conversion_status":"source_specimens_ONLY_no_native_conversion",
      "warnings":warnings,
      "families":list(FAMILIES),
      "specimens":[{
          k:v for k,v in x.items() if k!="content"
      } for _,x in sorted(picks.items())],
      "source_runtime_equivalence_verified":False,
    }

def write(picks,manifest,out_dir):
    out_dir=Path(out_dir)
    out_dir.mkdir(parents=True,exist_ok=True)
    for specimen in picks.values():
        (out_dir/specimen["file"]).write_text(specimen["content"])
    (out_dir/"manifest.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    parts=[
        "# B source specimens — six-stream capability implementation",
        "",
        "**Unmodified source semantics have NOT been proven. These are preserved",
        "parsed YAML research specimens from the earlier published 0.3",
        "authoring archive, not source SCAP 1.4 XML and not executable 0.4-B.**",
        "",
        "Specimens span common families from the complete six-stream corpus;",
        "small and larger documents exercise different conversion complexity.",
        "",
        "| Family | Source Assessment | Referencing streams | Tests | Source specimen |",
        "| --- | --- | --- | ---: | --- |",
    ]
    for a in manifest["specimens"]:
        parts.append("| "+", ".join(a["families"])+" | "+a["id"]+
          " | "+", ".join(a["benchmarks"])+" | "+str(a["test_count"])+" | "+
          "["+a["file"]+"]("+a["file"]+") |")
    parts.extend(["",
     "**Source limitations:** the original OVAL Test/State/Object/Variable",
     "semantics, shared source references, provider statuses and scanner",
     "results are not established by preserving a YAML document.",
     "This B-only specimen set enables implementation research; it is",
     "not an A/B bake-off or a claim of any native conversion rate.",
     ""])
    if manifest["warnings"]:
        parts+=["Missing bounded families: "+", ".join(manifest["warnings"])]
    (out_dir/"README.md").write_text("\n".join(parts)+"\n")
    return manifest

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--authoring-zip",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    args=p.parse_args()
    docs,sha=read_source(args.authoring_zip)
    report,capsules=import_corpus(docs,sha)
    picks,warnings=choose(report,capsules)
    manifest=write(picks,build_manifest(picks,warnings),args.output_dir)
    print(json.dumps({"specimens":len(picks),"families":len(FAMILIES),
                      "missing_families":len(warnings)},sort_keys=True))
    if warnings:
        raise SystemExit("incomplete source family set: "+str(warnings))

if __name__=="__main__":main()
