#!/usr/bin/env python3
"""#245 Compose several short C requirements into A evaluation IR, without OS collectors.

Registry native A capability mapping; source-exact WMI is compiler-owned
compatibility lowered via existing previously verified source fixture.
Assessment boolean logic is the already audited A six-state executor.
NOT a normative SCAP-NG grammar; these two *separate* Windows STIG rules form
a NEW demonstration policy, not a faithful reauthoring of an original Rule.
"""
from __future__ import annotations

from copy import deepcopy
from research_c_require_language import compile_c_requirement
from research_c_wmi_source_compat import lower_c_wmi_absence
from research_c_common_evaluation import lower_c_assessment_logic,evaluate_c_assessment_logic

def compile_c_composed_assessment(document, *, source_documents):
    if not isinstance(document,dict) or set(document)!={"id","checks","require"} or (
        not isinstance(document["id"],str) or not document["id"].strip()
    ):
        raise ValueError("C compound Assessment must explicitly declare id, checks, require")
    checks=document["checks"]
    if not isinstance(checks,dict) or not 1<=len(checks)<=50:
        raise ValueError("C compound Assessment requires 1..50 named checks")
    out={}
    for check_name,req in checks.items():
        if type(check_name) is not str or not check_name or (
            not isinstance(req,dict) or set(req)!={"from","must"}
        ):
            raise ValueError("each C check needs an identity and one from/must pair")
        frm=req["from"]
        if not isinstance(frm,dict) or len(frm)!=1:
            raise ValueError("each C check requires exactly one capability")
        capability=next(iter(frm))
        if capability=="windows.wmi.query":
            source=source_documents.get(check_name)
            if source is None:
                raise ValueError("WMI compatibility source must be pinned")
            lowered=lower_c_wmi_absence(req,source)
            out[check_name]={"kind":"source_compatibility","plan":lowered}
        else:
            if check_name in source_documents:
                raise ValueError("unnecessary or mismatched source compatibility input")
            native=compile_c_requirement(req)
            out[check_name]={"kind":"native_A_test_pieces","plan":native}
    if set(source_documents)-set(checks):
        raise ValueError("unreferenced compatibility source document")
    # Only test results reach the assessment six-state engine: no Item
    # outcomes, dependency scopes, or source Variable types are conflated.
    assessment={"id":document["id"],"mode":"automated",
                "tests":{name:{} for name in checks}}
    logical=lower_c_assessment_logic(document["require"],assessment)
    if set(logical["plan"]["requires"]["tests"])!=set(checks):
        raise ValueError("every named Test must be deliberately referenced")
    return {"stage":"C_RESEARCH_COMPOSED_SUPPLIED_RESULTS_NOT_SCANNER",
            "assessment_id":document["id"],"checks":out,
            "expression":logical,
            "source_oval_parity_verified":False,"scanner_executed":False}

def evaluate_c_composed_supplied_results(compiled, *, checks):
    if compiled.get("stage")!="C_RESEARCH_COMPOSED_SUPPLIED_RESULTS_NOT_SCANNER" or (
        compiled.get("source_oval_parity_verified") is not False
    ):
        raise ValueError("unrecognized C research compilation result")
    if set(checks)!=set(compiled["checks"]):
        raise ValueError("C supplied six-state Test identities differ")
    value=evaluate_c_assessment_logic(compiled["expression"],checks)
    return {"outcome":value["outcome"],"trace":deepcopy(value["trace"]),
            "scanner_executed":False,
            "source_oval_parity_verified":False}
