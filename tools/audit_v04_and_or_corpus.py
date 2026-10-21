#!/usr/bin/env python3
"""Strict six-STIG official 0.4 AND/OR scope census and inverse guard.

Validates every automated Test and Test-result evaluate tree in the proven
canonical v0.4.0 JSON ZIP, without editing the archive. New shadow operators
are named AND/OR/ONE/XOR exclusively when a source property's *scope* is
logical, never because an unrelated field happens to say 'all' or 'any'.

Reversible projection != scanner execution parity. Refs #248 #239.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
from zipfile import ZipFile

from audit_v04_and_or_scope_projection import document_projection,document_inverse


def census(archive, *, source_sha256, expected_documents=4001):
    raw=archive.read_bytes()
    actual=sha256(raw).hexdigest()
    if actual!=source_sha256:
        raise ValueError("Canonical 0.4 corpus archive SHA-256 does not match trusted run")
    totals=Counter()
    cases=[]
    errors=[]
    with ZipFile(BytesIO(raw)) as z:
        names=[n for n in z.namelist() if n.endswith(".json") and
               n.startswith("authoring/")]
        if len(names)!=expected_documents:
            raise ValueError("Canonical 0.4 source document count changed: "+
                             str(len(names)))
        for name in names:
            data=json.loads(z.read(name))
            assessment=data.get("assessment")
            if not isinstance(assessment,dict) or assessment.get("mode")!="automated":
                continue
            try:
                shadow=document_projection(data)
                document_inverse(data,shadow)
                totals["automated_assessments"]+=1
                for test_id,ir in shadow["test_logic"].items():
                    totals["automated_tests"]+=1
                    totals["test_state_operator_"+str(ir["condition_operator"])]+=1
                    totals["source_layout_"+ir["source_layout"]]+=1
                    if ir["operator_explicit"]:
                        totals["source_explicit_states_match"]+=1
                        if ir["condition_operator"]=="or":
                            totals["original_state_any_kept_as_logical_or"]+=1
                    if ir["source_layout"]=="all_items_must":
                        totals["all_items_not_converted_to_or"]+=1
                    if ir["source_layout"]=="legacy_states":
                        totals["legacy_state_semantics_kept"]+=1
                def visits(value):
                    if isinstance(value,dict):
                        for key,node in value.items():
                            if key in ("and","or","one","xor") and isinstance(node,list):
                                totals["projected_evaluate_"+key]+=1
                            visits(node)
                    elif isinstance(value,list):
                        for node in value:visits(node)
                visits(shadow["evaluate_logic"])
                if any(ir["operator_explicit"] for ir in shadow["test_logic"].values()):
                    cases.append({"path":name,"assessment_id":shadow["assessment_id"],
                                  "test_state_operators":{k:v["condition_operator"]
                                      for k,v in shadow["test_logic"].items()
                                      if v["operator_explicit"]},
                                  "original_items_quantifiers":{k:v["items_exist"]
                                      for k,v in shadow["test_logic"].items()
                                      if v["operator_explicit"]}})
            except Exception as e:
                errors.append({"path":name,"error":str(e)})
    if totals["automated_tests"]<1300:
        errors.append({"error":"Lost a large portion of the source Test denominator"})
    return {"format":"v04-boolean-scopes-source-proof-1",
            "status":"PASS" if not errors else "FAIL",
            "source_authoring_sha256":actual,
            "automated_assessments":totals["automated_assessments"],
            "automated_tests":totals["automated_tests"],
            "counts":dict(sorted(totals.items())),
            "source_explicit_logical_operator_cases":cases,
            "errors":errors,
            "schema_changed":False,"scanner_six_state_execution":"NOT_RUN"}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--canonical-zip",type=Path,required=True)
    p.add_argument("--sha256",required=True)
    p.add_argument("--report",type=Path,required=True)
    args=p.parse_args()
    result=census(args.canonical_zip,source_sha256=args.sha256)
    args.report.parent.mkdir(exist_ok=True,parents=True)
    args.report.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:v for k,v in result.items()
                      if k not in ("source_explicit_logical_operator_cases","errors")},
                     indent=2,sort_keys=True))
    if result["errors"]:
        print(json.dumps(result["errors"][:12],indent=2))
    raise SystemExit(0 if result["status"]=="PASS" else 1)


if __name__=="__main__":
    main()
