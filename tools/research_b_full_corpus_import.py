#!/usr/bin/env python3
"""Research #235: 0.4-B full six-STIG Assessment SOURCE-ACCOUNTING importer.

Consumes the published immutable 0.3 six-STIG authoring ZIP. This is a corpus
ACCOUNTING and nonexecuting compatibility-capsule stage, NOT SCAP 1.4 XML
conversion, OVAL equivalence, a scanner, or normative 0.4-B release.

Every referenced Assessment must resolve exactly once. Import capsules retain
entire original parsed source documents, origin, source digest and a canonical
round-trip digest; no unproved replacement with a simplified native check is
allowed. Never report source-runtime parity simply because structure survives.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import zipfile
import yaml

FORMAT="requirements-first-B-source-capsules/0.1-research"
SOURCE_TAG="v0.3.0-six-stig-typed-operators-5796d016b12f"
BENCHMARKS=(
    "rhel_9",
    "oracle_linux_9",
    "ms_windows_11",
    "ms_windows_server_2025",
    "ms_windows_server_dns",
    "apache_server_2-4_unix_server",
)
MAX_DOCUMENT_BYTES=8_000_000

class StrictLoader(yaml.SafeLoader):pass

def _mapping(loader,node):
    doc={}
    for k,v in node.value:
        key=loader.construct_object(k)
        if key in doc:raise ValueError("duplicate YAML key "+str(key))
        doc[key]=loader.construct_object(v)
    return doc
StrictLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,_mapping)

def digest(doc):
    # Consistent typed parsed tree equality, not an OVAL runtime digest.
    return sha256(json.dumps(doc,sort_keys=True,ensure_ascii=False,
                             separators=(",",":"),default=str).encode()).hexdigest()

def _safe_zip_name(name):
    p=PurePosixPath(name)
    return (not name.startswith("/") and not name.endswith("/")
            and "\\" not in name and ".." not in p.parts
            and name==p.as_posix()
            and p.parts[:1]==("authoring",))

def read_source(archive):
    documents={}
    raw_sha={}
    with zipfile.ZipFile(archive) as z:
        for info in sorted(z.infolist(),key=lambda x:x.filename):
            name=info.filename
            if info.is_dir() or not name.endswith((".yaml",".yml")):
                continue  # Release README/metadata are not Assessment documents.
            if not _safe_zip_name(name):
                raise ValueError("unsafe source archive path: "+name)
            if name in documents:raise ValueError("duplicate archive path: "+name)
            if info.file_size>MAX_DOCUMENT_BYTES:
                raise ValueError("oversized source document: "+name)
            raw=z.read(info)
            doc=yaml.load(raw.decode("utf-8"),Loader=StrictLoader)
            if not isinstance(doc,dict):
                raise ValueError("document must be mapping: "+name)
            documents[name]=doc
            raw_sha[name]=sha256(raw).hexdigest()
    if not documents:raise ValueError("no source YAML documents")
    return documents,raw_sha

def discover_benchmarks(documents):
    names={PurePosixPath(p).parts[1] for p in documents
           if len(PurePosixPath(p).parts)>2
           and PurePosixPath(p).parts[1]!="shared"
           and "/rules/" in p}
    if not names:raise ValueError("no benchmark rule files")
    return sorted(names)

def verify_in_memory_capsule(capsule):
    # Reconstructing original parsed source MUST be exact and deterministic.
    if capsule["format"]!=FORMAT:raise ValueError("wrong capsule format")
    if digest(capsule["source_document"])!=capsule["source_parsed_sha256"]:
        raise ValueError("capsule parsed source mismatch: "+capsule["source_path"])
    if capsule["migration_status"]!="compatibility_execution_pending":
        raise ValueError("unproved compatibility capsule claims executable")
    return capsule["source_document"]

def import_corpus(documents,raw_sha,*,expected_benchmarks=6):
    benchmark_names=discover_benchmarks(documents)
    if expected_benchmarks is not None and len(benchmark_names)!=expected_benchmarks:
        raise ValueError(f"expected {expected_benchmarks} benchmark rule directories, found {benchmark_names}")
    by_assessment={}
    by_rule=defaultdict(list)
    collisions=[]
    for path,doc in sorted(documents.items()):
        assessment=doc.get("assessment")
        if isinstance(assessment,dict):
            aid=assessment.get("id")
            if not isinstance(aid,str) or not aid:raise ValueError("Assessment missing id: "+path)
            if aid in by_assessment:
                collisions.append((aid,by_assessment[aid][0],path))
            else:by_assessment[aid]=(path,doc)
        rule=doc.get("rule")
        if isinstance(rule,dict):
            parts=PurePosixPath(path).parts
            if len(parts)<4 or parts[1] not in benchmark_names or "/rules/" not in path:
                raise ValueError("Rule in unexpected location: "+path)
            rid=rule.get("id")
            if not isinstance(rid,str) or not rid:raise ValueError("Rule missing id: "+path)
            by_rule[parts[1]].append((path,rule))
    if collisions:
        raise ValueError("duplicate Assessment IDs: "+repr(collisions[:5]))

    capsules={}
    rows=[]
    totals=Counter()
    for benchmark in benchmark_names:
        rules=by_rule[benchmark]
        if not rules:raise ValueError("benchmark has zero Rules: "+benchmark)
        seen_rule=set()
        for path,rule in rules:
            rid=rule["id"]
            if rid in seen_rule:
                raise ValueError("duplicate Rule ID within benchmark: "+benchmark+" / "+rid)
            seen_rule.add(rid)
            choices=rule.get("assessment_choices")
            if not isinstance(choices,dict) or not choices:
                raise ValueError("Rule lacks choice definitions: "+rid)
            default=rule.get("default_assessment_choice")
            if default not in choices:
                raise ValueError("Rule default choice missing: "+rid)
            selections=[]
            for kind,payload in sorted(choices.items()):
                if not isinstance(payload,dict):
                    raise ValueError("invalid Rule Assessment choice: "+rid+" / "+kind)
                aid=payload.get("assessment")
                if not isinstance(aid,str) or not aid:
                    raise ValueError("choice has no Assessment ID: "+rid+" / "+kind)
                if aid not in by_assessment:
                    raise ValueError("unresolved Assessment reference: "+rid+" -> "+aid)
                source_path,source_document=by_assessment[aid]
                if aid not in capsules:
                    capsules[aid]={
                        "format":FORMAT,
                        "id":aid,
                        "migration_status":"compatibility_execution_pending",
                        "execution_verified":False,
                        "native_equivalent_verified":False,
                        "source_path":source_path,
                        "source_raw_sha256":raw_sha[source_path],
                        "source_parsed_sha256":digest(source_document),
                        "source_document":source_document,
                    }
                verify_in_memory_capsule(capsules[aid])
                selections.append({"choice":kind,"assessment_id":aid,"source_path":source_path,
                                   "default":kind==default})
                totals["assessment_choice_bindings"]+=1
                totals["choice:"+kind]+=1
            rows.append({"benchmark":benchmark,"rule_id":rid,"rule_path":path,
                         "rule_raw_sha256":raw_sha[path],
                         "rule_parsed_sha256":digest(documents[path]),
                         "default_assessment_choice":default,"choices":selections,
                         "migration_status":"reference_verified_execution_pending"})
            totals["rules"]+=1
            totals["benchmark:"+benchmark]+=1
            totals["default:"+default]+=1
    totals["unique_referenced_assessments"]=len(capsules)
    totals["benchmarks"]=len(benchmark_names)
    totals["source_yaml_files"]=len(documents)
    referenced={x["assessment_id"] for r in rows for x in r["choices"]}
    if referenced!=set(capsules):raise ValueError("assessment ledger inconsistent")
    output={
        "format":FORMAT,
        "source_tag":SOURCE_TAG,
        "status":"structural_only_not_executable",
        "source_benchmark_names":benchmark_names,
        "summary":dict(sorted(totals.items())),
        "rules":rows,
        "assessment_index":[{
            "id":aid,
            "source_path":v["source_path"],
            "source_raw_sha256":v["source_raw_sha256"],
            "source_parsed_sha256":v["source_parsed_sha256"],
            "migration_status":v["migration_status"],
            "mode":v["source_document"].get("assessment",{}).get("mode"),
            "tests":len(v["source_document"].get("assessment",{}).get("tests") or {}),
        } for aid,v in sorted(capsules.items())],
        "unsupported_references":[],
        "source_runtime_equivalence_verified":False,
        "six_state_execution_implemented":False,
    }
    return output,capsules

def render_markdown(report):
    c=report["summary"]
    lines=[
        "# Requirements-first B — six-STIG source-coverage importer",
        "",
        "**Structural import only. NOT a successful native translation, lossless source execution, or A/B bake-off.**",
        "Input is the published immutable **SCAP-NG 0.3 six-STIG authoring ZIP**,",
        "**not** a raw SCAP 1.4 XML datastream. Capsule documents retain exact parsed",
        "source YAML, ID, raw digest, original path and an independent normalized digest.",
        "Every referenced choice and Rule ID is checked; native and compatibility",
        "execution remain pending.",
        "",
        "| Source property | Verified value |",
        "|---|---:|",
        f"| Benchmark directories | {c['benchmarks']} |",
        f"| Rules with validated choice bindings | {c['rules']} |",
        f"| Unique referenced Assessments | {c['unique_referenced_assessments']} |",
        f"| Assessment-choice bindings | {c['assessment_choice_bindings']} |",
        f"| Source YAML files examined | {c['source_yaml_files']} |",
        "",
        "## Per benchmark",
        "",
        "| Benchmark | Rules |",
        "|---|---:|",
    ]
    for b in report["source_benchmark_names"]:
        lines.append(f"| {b} | {c['benchmark:'+b]} |")
    lines.extend(["","## What this does not prove","",
       "It does not prove semantic equivalence to SCAP 1.4, native rewrite coverage,",
       "manual handling quality, imported OVAL State/Variable behavior, applicability",
       "execution, six-state evaluation or a working scanner. The preserved source",
       "capsules are **nonexecutable** and marked compatibility_execution_pending.",
       "The original six-STIG 0.3 authoring ZIP is itself a converted source;",
       "raw SCAP 1.4 parity requires a separate importer using the existing",
       "oval_semantic_ir.py and scap14_benchmark_ir.py source parsers.",
       "",
       "Neither A nor B has been competitively scored here. This is B capability",
       "engineering pursuant to [the readiness gate](../CAPABILITY-READINESS-GATE.md).",
       ""])
    return "\n".join(lines)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--authoring-zip",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--markdown",type=Path)
    p.add_argument("--capsules-output",type=Path)
    p.add_argument("--expected-benchmarks",type=int,default=6)
    args=p.parse_args()
    docs,hashes=read_source(args.authoring_zip)
    report,capsules=import_corpus(docs,hashes,expected_benchmarks=args.expected_benchmarks)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    if args.markdown:
        args.markdown.parent.mkdir(parents=True,exist_ok=True)
        args.markdown.write_text(render_markdown(report))
    if args.capsules_output:
        args.capsules_output.parent.mkdir(parents=True,exist_ok=True)
        args.capsules_output.write_text(json.dumps({
            "format":FORMAT,"capsules":capsules},sort_keys=True,indent=2)+"\n")
    print(json.dumps(report["summary"],sort_keys=True,indent=2))
    return 0

if __name__=="__main__":raise SystemExit(main())
