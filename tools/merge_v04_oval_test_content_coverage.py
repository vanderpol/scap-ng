#!/usr/bin/env python3
"""Merge canonical 0.4.0 source-proven slices into the full OVAL Test Content ledger.

The pinned 167-Definition source universe must be immutable. Independent
validated slices may upgrade a disposition only with a source-hash-bound proof
and a genuinely passed canonical native schema check. Never promote historical
0.4-C research or the old v003 source-roundtrip as current 0.4 coverage.

Refs #248 #229 #232.
"""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

PIN = "e3538595c5083b9c34d937a81d319234df9bbfaa"
GOOD = "CURRENT_040_SOURCE_XML_AND_SCHEMA_VALIDATED_NOT_RUNTIME"


def combine(baseline, pilot, artifacts):
    source=baseline["summary"]
    if (source["source_revision"]!=PIN or source["definitions"]!=167 or
            source["source_xml_files"]!=144 or
            source["declared_oval_tests"]!=785 or
            source["current_040_validated_definitions_in_this_corpus"]!=0):
        raise ValueError("Complete baseline is not the pinned release gap census")
    if pilot["pin"]!=PIN or pilot["source_multitest_denominator"]!=44 or (
            pilot["schema_status"]!="PASS_ALL_EMITTED_NATIVE_040"):
        raise ValueError("Pilot missing complete source/accounting or schema pass")
    rows={}
    for entry in baseline["definitions"]:
        key=(entry["source_file"],entry["definition_id"])
        if key in rows:
            raise ValueError("Duplicated source Definition in full corpus")
        rows[key]=dict(entry)
    if len(rows)!=167:
        raise ValueError("Source Definition disappeared from complete universe")
    verified={}
    for entry in pilot["cases"]:
        if entry["status"]!=GOOD:
            continue
        key=(entry["file"],entry["definition_id"])
        if key in verified or key not in rows:
            raise ValueError("Duplicate or nonexistent OVAL Definition upgraded")
        original=rows[key]
        if (original["source_status"]!="OVAL_003_SOURCE_COMPATIBLE" or
                original["experimental_c_status"]!="SOURCE_COMPATIBLE_NOT_EXPERIMENTAL_C" or
                original["current_040_native_schema"]!="NOT_TESTED"):
            raise ValueError("Unsafe upgrade of Definition already blocked or proven")
        required=("assessment_json","assessment_yaml","proof_file")
        for field in required:
            if field not in entry:
                raise ValueError("Missing native 0.4 artifact: "+field)
        files={}
        for field in required:
            path=(artifacts/entry[field]).resolve()
            if artifacts.resolve() not in path.parents or not path.is_file():
                raise ValueError("Unsafe native 0.4 artifact path: "+field)
            files[field]=path
        actual=json.loads(files["assessment_json"].read_text())
        import yaml
        if yaml.safe_load(files["assessment_yaml"].read_text())!=actual:
            raise ValueError("Native 0.4 JSON and YAML differ")
        proof=json.loads(files["proof_file"].read_text())
        if (proof["source_definition_id"]!=entry["definition_id"] or
                proof["source_file"]!=entry["file"] or
                proof["source_file_sha256"]!=original["original_source_file_sha256"] or
                proof["native_schema_validation"]!="PASS" or
                proof["current_040_assessment_graph_sha256"]!=_digest(actual["assessment"]) or
                proof["scanner_result_equivalence"]!="NOT_PROVEN"):
            raise ValueError("OVAL source graph or schema proof inconsistent")
        if proof["source_test_count"]!=entry["source_tests"]:
            raise ValueError("OVAL Test closure count differs")
        original["current_040_native_schema"]="PASS"
        original["current_040_oval_xml_roundtrip"]="NOT_RUN"
        original["scanner_six_state_parity"]="NOT_PROVEN"
        original["current_040_artifact_json"]=entry["assessment_json"]
        original["current_040_artifact_yaml"]=entry["assessment_yaml"]
        original["current_040_proof"]=entry["proof_file"]
        verified[key]=entry
    if len(verified)!=pilot["native_040_schema_validated_definitions"]:
        raise ValueError("Missing or nonvalidated pilot Definition")
    if len(verified)<2:
        raise ValueError("No genuine incremental native 0.4 corpus coverage")
    statuses=Counter(r["source_status"] for r in rows.values())
    if statuses!={"OVAL_003_SOURCE_COMPATIBLE":162,
                   "OVAL_SOURCE_INVALID_OR_DEPRECATED":5}:
        raise ValueError("Original OVAL compatibility classification changed")
    result={
        "format":"scap-ng-0.4.0-original-oval-test-content-cumulative-readiness-1",
        "source_repository":"OVAL-Community/SCAP-Self-Assertion",
        "source_revision":PIN,
        "source_xml_files":144,
        "original_definitions":167,
        "declared_oval_tests":785,
        "v003_source_roundtrip_compatible":162,
        "original_source_invalid_or_deprecated":5,
        "current_040_schema_and_original_source_validated":len(verified),
        "current_040_original_xml_roundtrip_exported":0,
        "scanner_result_parity_proven":0,
        "remaining_v003_compatible_without_current_040_proof":162-len(verified),
        "historical_C_research_subsets_are_not_current_040_proofs":True,
        "records":[rows[k] for k in sorted(rows)],
    }
    return result


def _digest(value):
    return sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,
                             separators=(",",":")).encode()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--baseline",type=Path,required=True)
    p.add_argument("--native-pilot",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    baseline=json.loads(args.baseline.read_text())
    pilot=json.loads((args.native_pilot/"manifest.json").read_text())
    result=combine(baseline,pilot,args.native_pilot)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",
                           encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k!="records"},indent=2))


if __name__=="__main__":
    main()
