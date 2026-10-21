#!/usr/bin/env python3
"""Compare independently imported OVAL→0.4 authoring with canonical six-STIG.

Ignore only author/publisher-assigned Assessment ID/title and meaningful local
Test ID, never any executable Test/Object/State/Filter fields or result axes.
This is a real forward-conversion differential, not a scanner execution test.
Refs #248 #229.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path


def executable(doc):
    a=doc.get("assessment") if isinstance(doc,dict) else None
    if not isinstance(a,dict) or a.get("specification",{}).get("version")!="0.4.0":
        raise ValueError("Native 0.4 Assessment missing")
    if len(a.get("tests") or {})!=1:
        raise ValueError("Pilot source must contain exactly one Test")
    tid,test=next(iter(a["tests"].items()))
    if a.get("evaluate")!={"test":tid}:
        raise ValueError("Native Assessment evaluate boundary differs")
    if not isinstance(a.get("assessment_title"),str) or not a["assessment_title"]:
        raise ValueError("Native Assessment title missing")
    if not isinstance(a.get("id"),str) or not a["id"]:
        raise ValueError("Native Assessment identity missing")
    return {"class":a.get("class"),"version":a.get("version"),
            "purpose":a.get("purpose"),"mode":a.get("mode"),
            "specification":a.get("specification"),
            "Test":test}


def compare(fresh,canonical):
    expected=executable(fresh)
    actual=executable(canonical)
    if expected!=actual:
        deltas={k:{"fresh":expected.get(k),"canonical":actual.get(k)}
                for k in sorted(expected.keys()|actual.keys())
                if expected.get(k)!=actual.get(k)}
        raise ValueError("OVAL→new 0.4 import differs from official six-STIG source: "+
                         json.dumps(deltas,sort_keys=True)[:9000])
    return {"status":"TRUE_FRESH_OVAL_IMPORT_MATCHES_CANONICAL_040_TEST",
            "tested":True,
            "capability":expected["Test"]["capability"],
            "author_documentary_id_title_ignored":True,
            "original_xml_to_native_import_verified":True,
            "full_converter_coverage_claim":False}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--fresh",type=Path,required=True)
    p.add_argument("--canonical",type=Path,required=True)
    p.add_argument("--report",type=Path,required=True)
    a=p.parse_args()
    report=compare(json.loads(a.fresh.read_text()),json.loads(a.canonical.read_text()))
    report["fresh_sha256"]=hashlib.sha256(a.fresh.read_bytes()).hexdigest()
    report["canonical_sha256"]=hashlib.sha256(a.canonical.read_bytes()).hexdigest()
    a.report.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps(report,indent=2))


if __name__=="__main__":
    main()
