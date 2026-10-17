#!/usr/bin/env python3
"""#237 B research: authenticated manual-result fixture contract.

This does not establish real user authentication; scanner/UI must verify the
claimed evaluator identity and secure evidence. It demonstrates the portable
minimum provenance semantics without inferring answers from procedure text.
"""
from __future__ import annotations
from datetime import datetime

from oval_result_truth_tables import (
    TRUE,FALSE,ERROR,UNKNOWN,NOT_APPLICABLE,NOT_EVALUATED)
from research_b_compiled_ir import decode


DEFAULT_CHOICES={"pass":TRUE,"fail":FALSE,"not_applicable":NOT_APPLICABLE}
COMPLETED={TRUE,FALSE,ERROR,UNKNOWN,NOT_APPLICABLE}


def complete_manual_response(compiled_ir, response):
    doc=decode(compiled_ir)
    if doc["source_kind"]!="manual" or doc["root"]["kind"]!="manual_procedure":
        raise ValueError("human response must reference a compiled Manual Assessment")
    node=doc["root"]
    if not isinstance(response,dict) or set(response)!={
            "assessment_id","assessment_version","execution_id","answer",
            "completed_at","evaluator","response_source","comment","evidence"}:
        raise ValueError("complete manual response/provenance contract required")
    if (response["assessment_id"]!=node["source_assessment_id"] or
            response["assessment_version"]!=node["version"]):
        raise ValueError("manual answer Assessment identity or version mismatch")
    if not isinstance(response["execution_id"],str) or not response["execution_id"]:
        raise ValueError("missing Assessment execution identity")
    who=response["evaluator"]
    if not isinstance(who,dict) or set(who)!={"scheme","value"} or not all(
            isinstance(v,str) and v.strip() for v in who.values()):
        raise ValueError("authenticated stable evaluator scheme/value required")
    if response["response_source"] not in {"direct","authorized_import"}:
        raise ValueError("unsupported manual response source")
    timestamp=response["completed_at"]
    if not isinstance(timestamp,str):
        raise ValueError("completed_at must be an offset-aware timestamp")
    try:
        finished=datetime.fromisoformat(timestamp)
    except ValueError as exc:
        raise ValueError("invalid manual completion timestamp") from exc
    if finished.utcoffset() is None:
        raise ValueError("manual completed_at must include timezone offset")
    if not isinstance(response["answer"],str) or not response["answer"]:
        raise ValueError("manual response answer must be a defined string choice")
    if node["response"] is None:
        choices=DEFAULT_CHOICES
        allow_comment=True
        allow_evidence=True
    else:
        contract=node["response"]
        choices={c["value"]:c["outcome"].replace("_"," ") for c in contract["choices"]}
        allow_comment=contract["allow_comment"]
        allow_evidence=contract["allow_evidence"]
    selected=choices.get(response["answer"])
    if selected not in COMPLETED:
        raise ValueError("unknown or unfinished manual choice")
    comment=response["comment"]
    evidence=response["evidence"]
    if comment is not None and not isinstance(comment,str):
        raise ValueError("manual comment must be string or null")
    if comment and not allow_comment:
        raise ValueError("publisher disallows manual comments")
    if not isinstance(evidence,list) or not all(
            isinstance(item,dict) and set(item)=={"ref"} and
            isinstance(item["ref"],str) and bool(item["ref"]) for item in evidence):
        raise ValueError("manual evidence must be explicit reference records")
    if evidence and not allow_evidence:
        raise ValueError("publisher disallows manual evidence")
    return {
        "assessment_id":node["source_assessment_id"],
        "assessment_version":node["version"],
        "execution_id":response["execution_id"],
        "mode":"manual",
        "technical_result":selected,
        "answer":response["answer"],
        "completed_at":timestamp,
        "evaluator":who,
        "response_source":response["response_source"],
        "comment":comment,
        "evidence_references":evidence,
        "source_procedure_preserved":True,
    }
