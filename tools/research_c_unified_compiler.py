#!/usr/bin/env python3
"""Refs #245 C single-frontend-to-A research compiler for supported scalar checks.

The normalized ONE frontend grammar supports:
  - standalone inline C checks
  - named checks, each inline or referring to shared observations
  - source-compat WMI absence when original pinned source is supplied
  - named checks combined by audited A six-state logic
A Object / State / Test pieces from the existing C/A adapter remain primary.
This does NOT compile the full seven-check record example, execute collectors,
deduplicate runtime snapshots, or certify source 1.4 parity. Unsupported
record/Variable/Filter/scope constructs fail closed.
"""
from __future__ import annotations

from copy import deepcopy

from research_c_one_frontend import normalize_c_frontend
from research_c_require_language import compile_c_requirement
from research_c_common_evaluation import (
    lower_c_assessment_logic, evaluate_c_assessment_logic
)
from research_c_wmi_source_compat import lower_c_wmi_absence


def _c_logic(node):
    if node["op"] == "check":
        return {"check": node["id"]}
    if node["op"] == "not":
        return {"not": _c_logic(node["child"])}
    return {node["op"]: [_c_logic(child) for child in node["children"]]}


def _name(alias):
    return alias.replace("_", "-") + "-object"


def compile_c_unified(document, *, source_documents=None):
    normalized=normalize_c_frontend(document)
    source_documents={} if source_documents is None else source_documents
    if not isinstance(source_documents,dict) or (
        set(source_documents)-
        {c["id"] for c in normalized["checks"]}
    ):
        raise ValueError("unknown pinned source compatibility input")
    sources={}
    by_alias={}
    for alias, source in normalized["observations"].items():
        ident=source["source_object"] or _name(alias)
        if ident in sources:
            raise ValueError("ambiguous shared Object identity")
        by_alias[alias]=ident
    checks={}
    native_tests={}
    for check in normalized["checks"]:
        alias=check["id"]
        cap=check["from"]["capability"]
        requirement={
            "from":{cap:deepcopy(check["from"]["arguments"])},
            "must":deepcopy(check["must"]),
        }
        if cap=="windows.wmi.query" and requirement["must"]=="absent":
            if check["observation"] is not None:
                raise ValueError("shared WMI compatibility requires native capability proof")
            if alias not in source_documents:
                raise ValueError("pinned source required for WMI legacy absence")
            compat=lower_c_wmi_absence(requirement,source_documents[alias])
            checks[alias]={"kind":"legacy_source_compat","plan":compat}
            continue
        if alias in source_documents:
            raise ValueError("unexpected legacy source document for native check")
        compiled=compile_c_requirement(requirement)
        test=deepcopy(compiled["test"])
        ref=check["observation"]
        if ref is not None:
            identifier=by_alias[ref]
            collection=test["object"]
            if identifier not in sources:
                sources[identifier]=deepcopy(collection)
            elif sources[identifier]!=collection:
                raise ValueError("shared observation collection mismatch")
            test["object"]=identifier
        native_tests[alias]=test
        # The ONE native Test graph is authoritative. Do not publish a second
        # inline Object alongside its shared-Object reference: a later runtime
        # could accidentally recollect the same request or lose provenance.
        checks[alias]={"kind":"native_A_test_pieces",
                       "test":deepcopy(test),
                       "independent_collection_plan":False}
    if set(sources)!={by_alias[k] for k in by_alias}:
        raise ValueError("dangling shared observation cannot be discarded")
    logic=_c_logic(normalized["require"])
    assessment={"id":normalized["assessment_id"] or "internal-c-research",
                "mode":"automated",
                "tests":{c["id"]:{} for c in normalized["checks"]}}
    lowered=lower_c_assessment_logic(logic,assessment)
    # The expression compiler deduplicates leaf IDs; this is intentional
    # where a single check participates in two OR branches.
    expected={c["id"] for c in normalized["checks"]}
    actual=set(lowered["plan"]["requires"]["tests"])
    if actual!=expected:
        raise ValueError("C Test references missing from the executable expression")
    return {
        "stage":"C_RESEARCH_UNIFIED_A_COMPILER_NO_SCANNER",
        "assessment_id":normalized["assessment_id"],
        "shared_objects":sources,"tests":native_tests,
        "checks":checks,"expression":lowered,
        "authored_check_ids":sorted(expected),
        "source_compatibility_inputs":sorted(source_documents),
        "scanner_executed":False,
        "source_parity_verified":False,
        "runtime_acquisition_sharing_verified":False,
    }


def evaluate_c_unified_supplied_results(compiled, *, checks):
    if compiled.get("stage")!="C_RESEARCH_UNIFIED_A_COMPILER_NO_SCANNER" or (
        compiled.get("scanner_executed") is not False
    ):
        raise ValueError("not a trusted C research compilation")
    if set(checks)!=set(compiled["checks"]):
        raise ValueError("mismatched Test result IDs")
    result=evaluate_c_assessment_logic(compiled["expression"],checks)
    return {"outcome":result["outcome"],"scanner_executed":False}
