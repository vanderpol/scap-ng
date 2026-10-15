#!/usr/bin/env python3
"""Export six source-backed 0.4 Assessment previews as parallel YAML/JSON authoring ZIPs.

Pre-alpha technical review only; no scanner and no normative schema promotion.
"""
import argparse,hashlib,json,zipfile
from pathlib import Path
from collections import Counter
from copy import deepcopy
from datetime import date,datetime
import yaml
import research_04_rhel9_compact_preview as corpus
from research_04_native_deep_content_census import SIX_ANCHORS,resolve_benchmark_dir,SUPPORTED_MAPPING_DATA
from research_04_one_grammar_proof import make_single,lower_single,normalize_inert_source_checks,check_no_parallel_comparison_or_cardinality_grammar
from research_04_scoped_state_require import compact,expand
from research_04_scoped_schema import validate,CANDIDATE_LANGUAGE
from migrate_v04_enum_selectors import migrate,restore

def digest(data):return hashlib.sha256(data).hexdigest()
def jsonable(node):
    if isinstance(node,dict):return {k:jsonable(v) for k,v in node.items()}
    if isinstance(node,list):return [jsonable(v) for v in node]
    if isinstance(node,(datetime,date)):return node.isoformat()
    if isinstance(node,(str,int,float,bool)) or node is None:return node
    raise TypeError("Unrepresentable JSON native scalar: "+repr(node))
def benchmark_content(z,benchmark):
    folders={n.split("/")[1] for n in z.namelist() if n.startswith("authoring/") and "/rules/" in n}
    old=corpus.SOURCE_PREFIX
    corpus.SOURCE_PREFIX="authoring/"+resolve_benchmark_dir(folders,benchmark)+"/"
    try:return corpus.archive_contents(z)
    finally:corpus.SOURCE_PREFIX=old
def migrate_assessment(doc,path,cache):
    source,_,notes=make_single(doc)
    check_no_parallel_comparison_or_cardinality_grammar(source)
    if lower_single(source)!=normalize_inert_source_checks(doc,notes):
        raise ValueError("Existing single grammar source inverse mismatch "+path)
    modern,migrations=migrate(source,SUPPORTED_MAPPING_DATA)
    if restore(modern,migrations)!=source:raise ValueError("Enum selector inverse mismatch "+path)
    scoped,stats=compact(modern)
    spec=scoped["assessment"].get("specification")
    if not isinstance(spec,dict) or spec.get("version")!="0.3.0":
        raise ValueError("Unexpected original specification at "+path)
    spec["version"]="0.4.0"
    expected=deepcopy(modern)
    expected["assessment"]["specification"]["version"]="0.4.0"
    if expand(scoped)!=expected or validate(scoped,cache)!=expected:
        raise ValueError("Scoped syntax expansion/schema/native mismatch "+path)
    return scoped,notes,migrations,stats

def create(source_zip,out_dir):
    raws={};ydocs={};jdocs={};prior_sha={}
    by_stig={};provenance=[];cache={};examples={}
    with zipfile.ZipFile(source_zip) as z:
        if z.testzip() is not None:raise ValueError("Corrupt original ZIP")
        for bench in SIX_ANCHORS:
            docs,raw=benchmark_content(z,bench)
            rules=corpus.benchmark_rule_paths(docs)
            if not rules:raise ValueError("No Rules in "+bench)
            counts=Counter()
            for path,source_bytes in sorted(raw.items()):
                if path in prior_sha and prior_sha[path]!=digest(source_bytes):
                    raise ValueError("Shared authoring source collision: "+path)
                prior_sha[path]=digest(source_bytes)
                if path.endswith((".yaml",".yml")):
                    doc=docs[path]
                    a=doc.get("assessment") if isinstance(doc,dict) else None
                    if isinstance(a,dict) and a.get("mode")=="automated":
                        doc,notes,migrations,metrics=migrate_assessment(doc,path,cache)
                        counts.update(metrics)
                        counts["assessments"]+=1
                        counts["tests"]+=len(doc["assessment"].get("tests") or {})
                        counts["source_exact"]+=int(not notes)
                        counts["source_model_equivalent"]+=int(bool(notes))
                        counts["enum_migrations"]+=len(migrations)
                        rec={"benchmark":bench,"path":path,"source_sha256":digest(source_bytes),
                             "source_class":"EXACT" if not notes else "STATE_FREE_MODEL_EQUIVALENT",
                             "notes":notes,"selector_migrations":migrations}
                        provenance.append(rec)
                        if "SV-253254.automated" in path or "SV-253274.automated" in path:
                            examples[path]=doc
                        ybody=yaml.safe_dump(doc,sort_keys=False,allow_unicode=True,width=112).encode()
                        if yaml.safe_load(ybody)!=doc:raise ValueError("YAML roundtrip "+path)
                    else:ybody=source_bytes
                    jbody=(json.dumps(jsonable(doc),ensure_ascii=False,indent=2,allow_nan=False)+"\n").encode()
                    if jsonable(yaml.safe_load(ybody))!=json.loads(jbody):
                        raise ValueError("YAML/JSON content mismatch "+path)
                    jpath=path.rsplit(".",1)[0]+".json"
                    if path in ydocs and ydocs[path]!=ybody:raise ValueError("Shared YAML conflict "+path)
                    if jpath in jdocs and jdocs[jpath]!=jbody:raise ValueError("Shared JSON conflict "+jpath)
                    ydocs[path]=ybody;jdocs[jpath]=jbody
                    counts["yaml_source_files"]+=1
                else:
                    if path in ydocs and ydocs[path]!=source_bytes:raise ValueError("NonYAML collision")
                    ydocs[path]=source_bytes
                    jdocs[path]=source_bytes
            counts["rules"]=len(rules)
            by_stig[bench]=dict(counts)
            print("SIX_STIG",bench,json.dumps(dict(counts),sort_keys=True),flush=True)
    totals=Counter()
    for vals in by_stig.values():
        for key,val in vals.items():totals[key]+=val
    for key,expected in {"assessments":1396,"tests":2144,"fields":2550,"saved":1106,"source_model_equivalent":12}.items():
        if totals[key]!=expected:raise ValueError(f"Six-STIG {key}: {totals[key]} != {expected}")
    index=[
        "# SCAP-NG 0.4 pre-alpha: Joval meeting review",
        "",
        "This discussion packet contains all six converted authoring benchmarks in YAML and JSON.",
        "This is NOT a normative schema release or executable scanner bundle.",
        "",
        "The proposed language uses actual field names, comparator verbs, explicit",
        "Test requirements, and/or State logic, and explicit inherited requirements",
        "from Test to State group to individual field. Native Windows record fields",
        "and the Test's collected-item requirement remain independent.",
        "",
        "JSON and YAML files contain the same parsed content; their internal",
        "path references are retained from published YAML for traceability.",
        "JSON paths end in .json, so those references are not yet independent",
        "buildable JSON-package paths. Original Rule/Benchmark/manual source files",
        "are preserved as YAML and semantically mirrored as JSON; original 0.3",
        "metadata may remain in contextual files. Only automated Assessments",
        "identify specification version 0.4.0.",
        "",
        "All automated Assessments pass current 0.4 source reconstruction,",
        "the scoped-candidate research schema, expansion to the strict 0.4 base",
        "schema and all native capability Test schemas. This is syntax and",
        "source-preservation verification, NOT scanner-runtime result parity.",
        "",
        "| STIG | Assessments | Native Tests | Redundant field declarations saved |",
        "| --- | ---: | ---: | ---: |",
    ]
    labels={"rhel_9":"RHEL 9","oracle_linux_9":"Oracle Linux 9",
            "windows_11":"Windows 11","windows_server_2025":"Windows Server 2025",
            "windows_server_dns":"Windows Server DNS","apache_2_4_unix":"Apache 2.4 UNIX"}
    for key,v in by_stig.items():
        index.append(f"| {labels.get(key,key)} | {v['assessments']} | {v['tests']} | {v['saved']} |")
    index+= [
        f"| **Total** | **{totals['assessments']}** | **{totals['tests']}** | **{totals['saved']}** |",
        "",
        "Suggested Windows 11 sample files to open: SV-253254.automated",
        "(Enterprise versus EnterpriseS; explicit group AND and State OR),",
        "and SV-253274.automated (shellcommand stderr_line must be absent).",
        "",
        "Pending decisions: unusual cardinality phrase naming; scoped",
        "inheritance accepted grammar versus research syntax; runtime",
        "absence/error/unknown/incomplete semantics; compiled package support.",
        "",
        "Source, scripts and review: https://github.com/vanderpol/scap-ng/issues/227",
        "https://github.com/vanderpol/scap-ng/issues/228",
        "https://github.com/vanderpol/scap-ng/blob/main/research/assessment-simplification/compact-authoring-04/SCOPED-FIELD-REQUIRE-REVIEW.md",
        "",
        "Reproduction source: published release",
        "v0.3.0-six-stig-typed-operators-5796d016b12f",
        "SHA-256 of original six-STIG authoring ZIP: "+digest(source_zip.read_bytes()),
        "",
    ]
    readme=("\n".join(index)).encode()
    manifest={"status":"REVIEW ONLY: 0.4 PRE-ALPHA, NOT APPROVED OR SCANNABLE",
              "source_zip_sha256":digest(source_zip.read_bytes()),
              "benchmarks":by_stig,"totals":dict(totals),"provenance":provenance,
              "review_examples":sorted(examples)}
    supplementary={
        "MEETING-START-HERE.md":readme,
        "PROVENANCE.json":(json.dumps(manifest,indent=2,sort_keys=True)+"\n").encode(),
        "SCOPED-LANGUAGE-RESEARCH-SCHEMA.json":(json.dumps(CANDIDATE_LANGUAGE,indent=2,sort_keys=True)+"\n").encode(),
    }
    archives=[]
    for ext,contents in (("yaml",ydocs),("json",jdocs)):
        dest=out_dir/f"scap-ng-v0.4-joval-six-stig-{ext}.zip"
        with zipfile.ZipFile(dest,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=8) as z:
            for path,blob in sorted({**contents,**supplementary}.items()):
                z.writestr(path,blob)
        with zipfile.ZipFile(dest) as z:
            if z.testzip() is not None:raise ValueError("ZIP CRC error "+str(dest))
            if sum(p.startswith("authoring/") for p in z.namelist())!=len(contents):
                raise ValueError("ZIP member count error")
        archives.append({"file":dest.name,"sha256":digest(dest.read_bytes()),
                         "bytes":dest.stat().st_size,"authoring_files":len(contents)})
    (out_dir/"MEETING-START-HERE.md").write_bytes(readme)
    (out_dir/"REVIEW-MANIFEST.json").write_text(
        json.dumps({"status":manifest["status"],"totals":manifest["totals"],
                    "benchmarks":by_stig,"archives":archives},indent=2,sort_keys=True)+"\n")
    print("SIX_STIG_JOVAL_PREVIEW",json.dumps(archives,sort_keys=True),flush=True)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-zip",required=True,type=Path)
    parser.add_argument("--output-dir",required=True,type=Path)
    args=parser.parse_args()
    args.output_dir.mkdir(parents=True,exist_ok=True)
    create(args.source_zip,args.output_dir)

if __name__=="__main__":main()
