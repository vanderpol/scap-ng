#!/usr/bin/env python3
"""Join independent original-OVAL semantic diff and XSD reports by SHA-256.

An XSD pass about a different output XML must never be counted toward
current-v0.4 roundtrip evidence. Each passed Definition needs both proofs.
This remains a pilot/source-structure gate, not full OVAL or scanner parity.
Refs #248 #229.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path


def combine(semantic,schemas):
    if semantic.get("format")!="scap-ng-v04-oval-xml-roundtrip-report-1":
        raise ValueError("Unknown semantic roundtrip report")
    if semantic.get("status")!="PASS":
        raise ValueError("Semantic XML comparison failed")
    cases=semantic.get("cases")
    if not isinstance(cases,list) or not cases:
        raise ValueError("Missing source Definition comparison evidence")
    by_sha={}
    for xsd in schemas:
        if (xsd.get("status")!="PASS" or xsd.get("oval_schema_version")!="5.12.3"
                or xsd.get("diagnostics")):
            raise ValueError("XML export is not strictly valid against OVAL 5.12.3")
        hashval=xsd.get("xml_sha256")
        if not isinstance(hashval,str) or len(hashval)!=64 or hashval in by_sha:
            raise ValueError("Duplicate or invalid independently schema-validated XML hash")
        by_sha[hashval]=xsd
    if len(by_sha)!=len(cases):
        raise ValueError("Schema evidence count differs from original-OVAL case count")
    joined=[]
    for case in cases:
        if case.get("status")!="EQUAL" or case.get("semantic_equal") is not True:
            raise ValueError("Definition not semantically equal to source OVAL")
        ident=case.get("regenerated_sha256")
        if ident not in by_sha:
            raise ValueError("Schema check not bound to semantic output XML hash")
        joined.append({"case_id":case["case_id"],"original_definition":case["source_definition"],
                       "exported_definition":case["regenerated_definition"],
                       "semantic_equal":True,"xsd_valid_5123":True,
                       "original_xml_sha256":case["source_sha256"],
                       "native_040_sha256":case["native_sha256"],
                       "regenerated_oval_sha256":ident})
    return {"status":"PASS_LIMITED_040_NATIVE_ROUNDTRIP_PILOT",
            "case_count":len(joined),"cases":joined,
            "semantic_comparison":"PASS",
            "oval_5123_xsd_validation":"PASS",
            "source_xml_to_ng":"PINNED_SIX_STIG_GENERATED_AUTHORING",
            "exporter":"INDEPENDENT_STRICT_SUBSET_040",
            "full_oval_self_assertion":"NOT_RUN",
            "schematron":"NOT_RUN",
            "scanner_execution":"NOT_RUN",
            "full_oval_xml_roundtrip_conformance":False}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--semantic",type=Path,required=True)
    p.add_argument("--xsd",type=Path,action="append",required=True)
    p.add_argument("--report",type=Path,required=True)
    a=p.parse_args()
    result=combine(json.loads(a.semantic.read_text()),
                   [json.loads(path.read_text()) for path in a.xsd])
    a.report.parent.mkdir(exist_ok=True,parents=True)
    a.report.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k!="cases"},indent=2))


if __name__=="__main__":
    main()
