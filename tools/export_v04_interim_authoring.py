#!/usr/bin/env python3
"""Review-only, current single-grammar 0.4 RHEL9 / Windows11 YAML previews."""
from __future__ import annotations
import argparse, hashlib, json, zipfile
from collections import Counter
from copy import deepcopy
from pathlib import Path
import yaml
import research_04_rhel9_compact_preview as corpus
from research_04_native_deep_content_census import (
    ROOT_ASSESSMENT_VALIDATOR, SUPPORTED, SUPPORTED_MAPPING_DATA,
    resolve_benchmark_dir, validator_for,
)
from research_04_one_grammar_proof import (
    check_no_parallel_comparison_or_cardinality_grammar,
    lower_single, make_single, normalize_inert_source_checks,
)
from migrate_v04_enum_selectors import migrate, restore

TARGETS=("rhel_9","windows_11")
def sha(data):
    return hashlib.sha256(data).hexdigest()

def build_one(source_zip,target,destination):
    with zipfile.ZipFile(source_zip) as z:
        if z.testzip() is not None:raise ValueError("Corrupted immutable source ZIP")
        folders={p.split("/")[1] for p in z.namelist()
                 if p.startswith("authoring/") and "/rules/" in p}
        prev=corpus.SOURCE_PREFIX
        corpus.SOURCE_PREFIX="authoring/"+resolve_benchmark_dir(folders,target)+"/"
        try: docs,raw=corpus.archive_contents(z)
        finally: corpus.SOURCE_PREFIX=prev
    rules=corpus.benchmark_rule_paths(docs)
    if not rules:raise ValueError("No source benchmark Rules")
    updated={}
    provenance=[]
    count=Counter()
    cache={}
    for path,original in sorted(docs.items()):
        assessment=original.get("assessment") if isinstance(original,dict) else None
        if not isinstance(assessment,dict) or assessment.get("mode")!="automated":continue
        compact,_,notes=make_single(original)
        check_no_parallel_comparison_or_cardinality_grammar(compact)
        if lower_single(compact)!=normalize_inert_source_checks(original,notes):
            raise ValueError(f"Source/0.4 inverse mismatch: {path}")
        transformed,migrations=migrate(compact,SUPPORTED_MAPPING_DATA)
        if restore(transformed,migrations)!=compact:
            raise ValueError(f"Reversible selector migration mismatch: {path}")
        transformed=deepcopy(transformed)
        spec=transformed["assessment"].get("specification")
        if not isinstance(spec,dict) or spec.get("version")!="0.3.0":
            raise ValueError(f"Unexpected source spec: {path} {spec}")
        spec["version"]="0.4.0"
        errors=list(ROOT_ASSESSMENT_VALIDATOR.iter_errors(transformed))
        if errors:
            e=errors[0]
            raise ValueError(f"0.4 Assessment {path} at {list(e.path)}: {e.message[:300]}")
        for tid,test in (transformed["assessment"].get("tests") or {}).items():
            if not isinstance(test,dict):continue
            cap=test.get("capability")
            if cap not in SUPPORTED:raise ValueError(f"Unknown capability {cap} at {path}")
            found=list(validator_for(cap,cache).iter_errors(test))
            if found:
                e=found[0]
                raise ValueError(f"Native Test {path}.{tid} at {list(e.path)}: {e.message[:300]}")
        encoded=yaml.safe_dump(
            transformed,sort_keys=False,allow_unicode=True,width=115
        ).encode("utf-8")
        if yaml.safe_load(encoded)!=transformed:
            raise ValueError(f"Serialized YAML mismatch: {path}")
        updated[path]=encoded
        count["automated_assessments"]+=1
        count["native_tests"]+=len(transformed["assessment"].get("tests") or {})
        count["exact_reconstructions"]+=int(not notes)
        count["state_free_model_normalizations"]+=int(bool(notes))
        count["enum_selector_migrations"]+=len(migrations)
        provenance.append({
            "path":path,"source_sha256":sha(raw[path]),"preview_sha256":sha(encoded),
            "equivalence":"source-exact" if not notes else "state-free-model-normalized",
            "state_free_normalization_notes":notes,"selector_migration_notes":migrations
        })
    if not updated:raise ValueError("No migrated Assessment YAML")
    count["unchanged_rules"]=len(rules)
    count["total_authoring_files"]=len(raw)
    description="\n".join([
        "# SCAP-NG 0.4 current single-grammar interim authoring preview",
        "",
        "**Research only. Not a published standard or scanning bundle.**",
        "",
        "This ZIP includes the real "+target+" Benchmark, Rules, manual Assessments",
        "and necessary shared Assessments from the published six-STIG 0.3 source.",
        "Automated/applicability Assessment YAML is converted to the CURRENT 0.4",
        "single human-readable authoring grammar and specification version.",
        "Every converted document passes the full 0.4 Assessment schema and",
        "its capability-specific native Test schemas and source inverse proof.",
        "",
        "Rule, Benchmark and manual files are byte-for-byte original context",
        "and may still contain 0.3 version markers. No 0.4 scanning bundle is",
        "implied. Provenance of original source and exceptions is in provenance.json.",
        "",
        "Tracking: https://github.com/vanderpol/scap-ng/issues/228",
        "",
        *[f"- {k}: {v}" for k,v in sorted(count.items())],"",
    ])
    data={
        "status":"interim research; NOT A SCANNING BUNDLE",
        "format":"scap-ng-0.4-authoring-preview/1",
        "source":"published immutable 0.3 six-STIG authoring ZIP",
        "source_zip_sha256":sha(source_zip.read_bytes()),
        "target":target,"summary":dict(count),"files":provenance,
    }
    with zipfile.ZipFile(destination,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=8) as z:
        for path,body in sorted(raw.items()):z.writestr(path,updated.get(path,body))
        z.writestr("REVIEW-FIRST.md",description)
        z.writestr("provenance.json",json.dumps(data,indent=2,sort_keys=True)+"\n")
    with zipfile.ZipFile(destination) as z:
        if z.testzip() is not None:raise AssertionError("Preview ZIP integrity failure")
        for path,raw_bytes in raw.items():
            blob=z.read(path)
            if path in updated:
                if blob!=updated[path]:raise AssertionError("Converted Assessment mutation")
                if yaml.safe_load(blob)["assessment"]["specification"]["version"]!="0.4.0":
                    raise AssertionError("Converted Assessment is not version 0.4")
            elif blob!=raw_bytes:raise AssertionError(f"Changed unchanged source: {path}")
    return {"benchmark":target,"zip":destination.name,"sha256":sha(destination.read_bytes()),
            "summary":dict(count)}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-zip",required=True,type=Path)
    p.add_argument("--output-dir",required=True,type=Path)
    args=p.parse_args()
    args.output_dir.mkdir(parents=True,exist_ok=True)
    result=[]
    for target in TARGETS:
        dest=args.output_dir/f"scap-ng-v0.4-{target}-single-grammar-authoring.zip"
        result.append(build_one(args.source_zip,target,dest))
    (args.output_dir/"PREVIEW-MANIFEST.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("V04_INTERIM_PREVIEWS",json.dumps(result,sort_keys=True),flush=True)

if __name__=="__main__":main()
