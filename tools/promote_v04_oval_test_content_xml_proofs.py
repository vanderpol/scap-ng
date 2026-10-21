#!/usr/bin/env python3
"""Promote independently proved XML↔canonical 0.4 cases in the pinned 167 ledger.

Requires actual regenerated OVAL XML, pinned 5.12.3 XSD result, hashes,
complete source-independent semantic equality, and existing native-schema
evidence; rejects partial/missing/tampered evidence.
Refs #248 #229 #232.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path

PIN="e3538595c5083b9c34d937a81d319234df9bbfaa"


def checked(base, rel, digest):
    if not isinstance(rel,str) or not rel or Path(rel).is_absolute():
        raise ValueError("Absolute/missing proof path")
    resolved=(base/rel).resolve()
    if not resolved.is_relative_to(base.resolve()) or not resolved.is_file():
        raise ValueError("Proof artifact escapes source directory")
    if sha256(resolved.read_bytes()).hexdigest()!=digest:
        raise ValueError("Evidence SHA-256 differs from manifest")
    return resolved


def upgrade(original, manifest, audit, base):
    if (original.get("source_revision")!=PIN or
            original.get("original_definitions")!=167 or
            original.get("declared_oval_tests")!=785 or
            original.get("current_040_schema_and_original_source_validated")!=2):
        raise ValueError("Original complete OVAL source ledger invalid")
    if (manifest.get("format")!="scap-ng-v04-oval-xml-roundtrip-1" or
            manifest.get("profile")!="0.4.0" or
            audit.get("status")!="PASS" or
            audit.get("source_case_count")!=2 or
            audit.get("outcome_counts")!={"EQUAL":2}):
        raise ValueError("Incomplete original-OVAL XML semantic gate")
    original_records={(r["source_file"],r["definition_id"]):r
                      for r in original["records"]}
    if len(original_records)!=167 or len(manifest["cases"])!=2:
        raise ValueError("Incomplete original source corpus/manifest")
    outcomes={r["case_id"]:r for r in audit.get("cases",[])}
    if len(outcomes)!=2 or any(r.get("status")!="EQUAL" or
                              r.get("semantic_equal") is not True
                              for r in outcomes.values()):
        raise ValueError("Independent XML semantic comparison not proven")
    seen=set()
    new=json.loads(json.dumps(original))
    index={(r["source_file"],r["definition_id"]):r for r in new["records"]}
    for row in manifest["cases"]:
        case_id=row["case_id"]
        key=(case_id,row["source_definition"])
        if key in seen or key not in original_records or
                case_id not in outcomes:
            raise ValueError("Duplicate/unknown source Definition in XML comparison")
        seen.add(key)
        source=index[key]
        if (source.get("current_040_native_schema")!="PASS" or
                source.get("current_040_oval_xml_roundtrip")!="NOT_RUN" or
                row.get("forward_profile")!="0.4.0" or
                row.get("reverse_profile")!="0.4.0"):
            raise ValueError("Unproven original source/native 0.4.0 conversion")
        outcome=outcomes[case_id]
        if (outcome.get("source_definition")!=row["source_definition"] or
                outcome.get("regenerated_definition")!=row["regenerated_definition"] or
                outcome.get("source_sha256")!=row["original_sha256"] or
                outcome.get("native_sha256")!=row["native_assessment_sha256"] or
                outcome.get("regenerated_sha256")!=row["regenerated_sha256"]):
            raise ValueError("OVAL source/output identity not preserved")
        source_file=checked(base,row["original"],row["original_sha256"])
        native_file=checked(base,row["native_assessment"],row["native_assessment_sha256"])
        emitted=checked(base,row["regenerated"],row["regenerated_sha256"])
        if (row["original_sha256"]!=source["original_source_file_sha256"] or
                native_file.relative_to(base).as_posix()!=source["current_040_artifact_json"]):
            raise ValueError("OVAL original file/native identity drift")
        plat=case_id.split("/",1)[0]
        if plat not in ("ios","iosxe"):
            raise ValueError("Unexpected semantic pilot platform")
        report_file=emitted.parent/"xsd-proof.json"
        proof=json.loads(report_file.read_text())
        if (proof.get("status")!="PASS" or
                proof.get("oval_schema_version")!="5.12.3" or
                proof.get("oval_platform_schema")!=plat or
                proof.get("xml_sha256")!=row["regenerated_sha256"] or
                proof.get("diagnostics")):
            raise ValueError("5.12.3 native platform XSD check missing or invalid")
        negative=emitted.parent/"negative-mutation-proof.json"
        mutated=json.loads(negative.read_text())
        if (mutated.get("mutated_differs") is not True or
                mutated.get("source_consulted_by_exporter") is not False):
            raise ValueError("No adverse semantic selector mutation evidence")
        source["current_040_oval_xml_roundtrip"]="PASS_INDEPENDENT_OVAL_5123_SEMANTIC_AND_XSD"
        source["current_040_oval_xml_proof"]=(emitted.parent/"oval-semantic-proof.json").relative_to(base).as_posix()
        source["current_040_regenerated_oval"]=emitted.relative_to(base).as_posix()
    if len(seen)!=2:
        raise ValueError("Missing source-valid OVAL parity case")
    new["current_040_original_xml_roundtrip_exported"]=2
    new["current_040_oval_roundtrip_kind"]="INDEPENDENT_XML_EXPORT_SEMANTIC_GRAPH_AND_XSD"
    new["scanner_result_parity_proven"]=0
    return new


def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--cumulative-ledger",type=Path,required=True)
    cli.add_argument("--roundtrip-root",type=Path,required=True)
    cli.add_argument("--output",type=Path,required=True)
    args=cli.parse_args()
    base=args.roundtrip_root
    audit_root=base/"independent-oval-roundtrip"
    ledger=json.loads(args.cumulative_ledger.read_text())
    manifest=json.loads((audit_root/"manifest.json").read_text())
    proof=json.loads((audit_root/"complete-semantic-proof.json").read_text())
    upgraded=upgrade(ledger,manifest,proof,base)
    args.output.write_text(json.dumps(upgraded,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps({k:v for k,v in upgraded.items() if k!="records"},indent=2))


if __name__=="__main__":
    main()
