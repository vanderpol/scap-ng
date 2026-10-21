#!/usr/bin/env python3
"""Promote one original family constant Variable proof into the 167-source ledger.

Requires previous independent two-Definition OVAL XML parity evidence and the
new source-checked family-variable 0.4 native schema, original XML semantic,
5.12.3 XSD, source SHA and mutation evidence. Not scanner parity.
Refs #248 #229 #232.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import yaml
from v04_flat_object_authoring import digest

PIN="e3538595c5083b9c34d937a81d319234df9bbfaa"
PATH="agnostic/ind-def_family_test.xml"
DID="oval:org.mitre.oval.test:def:95"
FILES=("family.assessment.json","family.assessment.yaml","original-oval.xml",
       "regenerated-oval.xml","forward-proof.json","regenerated-xsd-report.json",
       "semantic-roundtrip-report.json","negative-tests.json")


def promote(previous,folder):
    source=previous
    if (source.get("source_revision")!=PIN or
        source.get("original_definitions")!=167 or
        source.get("declared_oval_tests")!=785 or
        source.get("original_source_invalid_or_deprecated")!=5 or
        source.get("current_040_schema_and_original_source_validated")!=2 or
        source.get("current_040_original_xml_roundtrip_exported")!=2 or
        source.get("scanner_result_parity_proven")!=0):
        raise ValueError("Previous complete 167-Definition accepted baseline missing")
    entries={(r["source_file"],r["definition_id"]):r
             for r in source["records"]}
    if len(entries)!=167 or (PATH,DID) not in entries:
        raise ValueError("Original pinned family Definition missing from 167 ledger")
    entry=entries[(PATH,DID)]
    if (entry.get("source_status")!="OVAL_003_SOURCE_COMPATIBLE" or
        entry.get("current_040_native_schema")!="NOT_TESTED" or
        entry.get("current_040_oval_xml_roundtrip")!="NOT_TESTED"):
        raise ValueError("Original family Definition was not untested source compatible")
    base=Path(folder).resolve()
    paths={}
    for file in FILES:
        path=(base/file).resolve()
        if not path.is_file() or not path.is_relative_to(base):
            raise ValueError("Missing/outside proof artifact: "+file)
        paths[file]=path
    proof=json.loads(paths["forward-proof.json"].read_text())
    xsd=json.loads(paths["regenerated-xsd-report.json"].read_text())
    comparison=json.loads(paths["semantic-roundtrip-report.json"].read_text())
    negative=json.loads(paths["negative-tests.json"].read_text())
    xml_sha=sha256(paths["original-oval.xml"].read_bytes()).hexdigest()
    export_sha=sha256(paths["regenerated-oval.xml"].read_bytes()).hexdigest()
    doc=json.loads(paths["family.assessment.json"].read_text())
    if yaml.safe_load(paths["family.assessment.yaml"].read_text())!=doc:
        raise ValueError("Authoring YAML/JSON graph not identical")
    assessment=doc.get("assessment",{})
    if (proof.get("source_revision")!=PIN or
        proof.get("original_definition_id")!=DID or
        proof.get("source_path")!=PATH or
        proof.get("original_xml_sha256")!=xml_sha or
        entry.get("original_source_file_sha256")!=xml_sha or
        proof.get("scap_ng_assessment_sha256")!=digest(assessment) or
        proof.get("native_040_schema")!="PASS" or
        proof.get("independent_oval_5123_xml_semantics")!="PASS"):
        raise ValueError("Current family source hash/native schema acceptance not proven")
    if (xsd.get("status")!="PASS" or
        xsd.get("oval_schema_version")!="5.12.3" or
        xsd.get("oval_platform_schema")!="independent" or
        xsd.get("xml_sha256")!=export_sha or
        xsd.get("diagnostics")):
        raise ValueError("Source-independent OVAL XML 5.12.3 XSD acceptance unproven")
    if comparison.get("equal") is not True:
        raise ValueError("Independent original OVAL Definition semantic graph differs")
    if negative != {
        "altered_literal_rejected_by_semantic_diff":True,
        "altered_ng_variable_match_rejected":True,
        "altered_source_xml_var_check_rejected":True
    }:
        raise ValueError("Required semantic source/variable mutation regression not passed")
    updated=json.loads(json.dumps(source))
    rows={(r["source_file"],r["definition_id"]):r for r in updated["records"]}
    row=rows[(PATH,DID)]
    row["current_040_native_schema"]="PASS"
    row["current_040_oval_xml_roundtrip"]="PASS_INDEPENDENT_OVAL_5123_SEMANTIC_AND_XSD"
    row["scanner_six_state_parity"]="NOT_PROVEN"
    row["current_040_artifact_json"]="family.assessment.json"
    row["current_040_artifact_yaml"]="family.assessment.yaml"
    row["current_040_proof"]="forward-proof.json"
    row["current_040_regenerated_oval"]="regenerated-oval.xml"
    row["current_040_oval_xml_proof"]="semantic-roundtrip-report.json"
    row["current_040_artifact_source"]="0.4.0 OVAL family constant Variable GitHub Actions artifact"
    updated["current_040_schema_and_original_source_validated"]=3
    updated["current_040_original_xml_roundtrip_exported"]=3
    updated["remaining_v003_compatible_without_current_040_proof"]=159
    updated["scanner_result_parity_proven"]=0
    if sum(r.get("current_040_oval_xml_roundtrip","").startswith("PASS_")
           for r in updated["records"])!=3:
        raise ValueError("OVAL XML accepted source total not exactly three")
    return updated


def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--previous-ledger",type=Path,required=True)
    cli.add_argument("--family-artifacts",type=Path,required=True)
    cli.add_argument("--output",type=Path,required=True)
    args=cli.parse_args()
    prior=json.loads(args.previous_ledger.read_text())
    now=promote(prior,args.family_artifacts)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(now,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps({k:v for k,v in now.items() if k!="records"},indent=2))

if __name__=="__main__":
    main()
