#!/usr/bin/env python3
"""#237 B: preserve publisher-authored Manual Assessments as compiled procedures.

Manual method belongs to SCAP-NG policy/assessment packaging, not the OVAL
successor's automated auditor authoring language. No automatic verdict from
unstructured check text. Rich unrecognized manual contracts fail closed.
"""
from __future__ import annotations

OUTCOMES={"true","false","error","unknown","not_evaluated","not_applicable"}
SOURCE_KEYS={"id","version","assessment_title","mode","class","purpose",
             "procedure","response","references","evidence_guidance",
             "inputs","evidence"}


def lower_manual_assessment(source):
    if not isinstance(source,dict) or set(source)!={"assessment"}:
        raise ValueError("manual source requires single Assessment document")
    a=source["assessment"]
    if not isinstance(a,dict) or a.get("mode")!="manual":
        raise ValueError("source is not a Manual Assessment")
    if set(a)-SOURCE_KEYS:
        raise ValueError("unsupported publisher-authored manual fields: "+
                         repr(sorted(set(a)-SOURCE_KEYS)))
    aid=a.get("id")
    proc=a.get("procedure")
    version=a.get("version")
    if not isinstance(aid,str) or not aid or not isinstance(proc,str) or not proc:
        raise ValueError("manual source requires id and exact nonempty procedure")
    if (type(version) is not int and type(version) is not str) or not str(version):
        raise ValueError("source Manual Assessment version required")
    for field in ("inputs","evidence"):
        if a.get(field) not in (None,[],{}):
            raise ValueError("unsupported nonempty manual "+field+" contract")
    response=a.get("response")
    if response is not None:
        if not isinstance(response,dict) or set(response)!={
                "type","choices","allow_comment","allow_evidence"}:
            raise ValueError("unsupported richer manual response contract")
        if not isinstance(response["type"],str) or not response["type"]:
            raise ValueError("response vocabulary identifier required")
        if (type(response["allow_comment"]) is not bool or
                type(response["allow_evidence"]) is not bool):
            raise ValueError("response flags must be Boolean")
        if not isinstance(response["choices"],list) or not response["choices"]:
            raise ValueError("manual choices must be nonempty")
        seen=set()
        for choice in response["choices"]:
            if not isinstance(choice,dict) or not {"value","outcome"}<=set(choice) or (
                    set(choice)-{"value","label","outcome"}):
                raise ValueError("malformed source response choice")
            if not isinstance(choice["value"],str) or not choice["value"] or (
                    choice["value"] in seen):
                raise ValueError("duplicate or empty response choice")
            seen.add(choice["value"])
            if not isinstance(choice["outcome"],str) or choice["outcome"] not in OUTCOMES:
                raise ValueError("unrecognized normalized manual outcome")
            if "label" in choice and choice["label"] is not None and not isinstance(choice["label"],str):
                raise ValueError("manual choice label must be string/null")
    title=a.get("assessment_title")
    if title is not None and not isinstance(title,str):
        raise ValueError("manual title must be string or null")
    if a.get("purpose") not in {"assessment","applicability"} or (
            a.get("class") not in {"compliance","vulnerability","patch",
                                    "inventory","miscellaneous"}):
        raise ValueError("unknown manual Assessment purpose/class")
    if a.get("references") not in (None,[]) or (
            a.get("evidence_guidance") is not None and
            not isinstance(a["evidence_guidance"],str)):
        raise ValueError("unsupported manual references or evidence guidance")
    return {
        "kind":"manual_procedure",
        "source_assessment_id":aid,
        "version":version,
        "title":title,
        "class":a["class"],
        "purpose":a["purpose"],
        "procedure":proc,
        "response":response,
        "evidence_guidance":a.get("evidence_guidance"),
    }
