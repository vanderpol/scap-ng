#!/usr/bin/env python3
"""Refs #245: a SINGLE static C authoring shape for inline/shared observations.

Accept simple from/must, named direct checks, or checks referencing named
observations; normalize all into ONE typed authoring AST without changing
collection selectors, States or six-state meaning. This is a research syntax
normalizer, NOT a compiler/evaluator/scanner or migration tool.
"""
from __future__ import annotations

from copy import deepcopy
import re

ALIASES=frozenset(("every","one_of","exactly_one","odd_count","not"))
ID=re.compile(r"[a-z][a-z0-9_]{0,63}\Z")

def _named(value,name):
    if type(value) is not str or not ID.fullmatch(value):
        raise ValueError(name+" must be a stable lowercase C identifier")
    return value

def _from(value):
    if not isinstance(value,dict) or len(value)!=1:
        raise ValueError("from requires exactly one pinned capability")
    cap,args=next(iter(value.items()))
    if type(cap) is not str or not cap or not isinstance(args,dict):
        raise ValueError("capability and explicit selector/collection mapping are required")
    return {"capability":cap,"arguments":deepcopy(args)}

def _logic(node,valid):
    referenced=[]
    def walk(expr,depth=0):
        if depth>128 or not isinstance(expr,dict) or len(expr)!=1:
            raise ValueError("nonempty single-operator logic tree required")
        operator,payload=next(iter(expr.items()))
        if operator=="check":
            if type(payload) is not str or payload not in valid:
                raise ValueError("unknown named check reference")
            referenced.append(payload)
            return {"op":"check","id":payload}
        if operator=="not":
            return {"op":"not","child":walk(payload,depth+1)}
        if operator not in ALIASES or not isinstance(payload,list) or (
            not 1<=len(payload)<=100
        ):
            raise ValueError("unsupported or empty C composition")
        return {"op":operator,"children":[walk(v,depth+1) for v in payload]}
    tree=walk(node)
    if set(referenced)!=set(valid):
        raise ValueError("all authored checks must be deliberately referenced")
    return tree,referenced

def normalize_c_frontend(document):
    if not isinstance(document,dict):
        raise ValueError("C Assessment must be a mapping")
    if set(document)=={"from","must"}:
        # No implicit authoring ID; this single check alias is internal-only.
        check_name="single_check"
        checks={check_name:{"from":document["from"],"must":document["must"]}}
        observations={}
        require={"check":check_name}
        assessment_id=None
        generated_alias=True
    elif set(document)=={"id","checks","require"}:
        assessment_id=document["id"]
        checks=document["checks"]
        observations={}
        require=document["require"]
        generated_alias=False
    elif set(document)=={"observations","checks","require"} or (
        set(document)=={"id","observations","checks","require"}
    ):
        assessment_id=document.get("id")
        checks=document["checks"]
        observations=document["observations"]
        require=document["require"]
        generated_alias=False
    else:
        raise ValueError("unsupported C document shape; no guessed defaults")
    if assessment_id is not None and (
        type(assessment_id) is not str or not assessment_id.strip()
    ):
        raise ValueError("Assessment ID must be explicit when present")
    if not isinstance(checks,dict) or not 1<=len(checks)<=100 or (
        not isinstance(observations,dict)
    ):
        raise ValueError("bounded named checks and observations required")
    sources={}
    source_object_ids=set()
    for key,source in observations.items():
        _named(key,"observation")
        if not isinstance(source,dict) or set(source) not in (
            {"from"},{"from","source_object"}
        ):
            raise ValueError("named observation requires from and optional source identity")
        ident=source.get("source_object")
        if ident is not None and (type(ident) is not str or not ident):
            raise ValueError("source Object provenance identity must be nonempty")
        if ident is not None:
            if ident in source_object_ids:
                raise ValueError("duplicate source Object provenance identity")
            source_object_ids.add(ident)
        sources[key]={"from":_from(source["from"]),"source_object":ident}
    normalized=[]
    used_obs=set()
    source_test_ids=set()
    for check_name,check in checks.items():
        _named(check_name,"check")
        if not isinstance(check,dict) or "must" not in check or (
            not isinstance(check["must"],dict) and type(check["must"]) is not str
        ):
            raise ValueError("check requires an explicit Item requirement")
        if "from" in check:
            if set(check) not in ({"from","must"},{"from","must","source_test"}):
                raise ValueError("direct check cannot also reference observation")
            source=_from(check["from"])
            observed=None
        elif "observation" in check:
            if set(check) not in (
                {"observation","must"},{"observation","must","source_test"}
            ):
                raise ValueError("shared check cannot have two acquisition routes")
            observed=check["observation"]
            if type(observed) is not str or observed not in sources:
                raise ValueError("unresolved shared observation")
            used_obs.add(observed)
            source=deepcopy(sources[observed]["from"])
        else:
            raise ValueError("check requires either from or named observation")
        source_test=check.get("source_test")
        if source_test is not None and (
            type(source_test) is not str or not source_test
        ):
            raise ValueError("source Test provenance must be explicit string")
        if source_test is not None:
            if source_test in source_test_ids:
                raise ValueError("duplicate source Test provenance identity")
            source_test_ids.add(source_test)
        normalized.append({
            "id":check_name,"source_test":source_test,
            "from":source,"observation":observed,
            "must":deepcopy(check["must"]),
        })
    if used_obs!=set(sources):
        raise ValueError("unused shared observations are not silently omitted")
    logic,referenced=_logic(require,set(checks))
    return {
        "stage":"C_RESEARCH_SINGLE_FRONTEND_SHAPE_NOT_COMPILER",
        "assessment_id":assessment_id,
        "generated_internal_single_check_alias":generated_alias,
        "observations":deepcopy(sources),
        "checks":normalized,"require":logic,
        "check_references_in_order":referenced,
        "source_semantics_validated":False,"scanner_executed":False,
    }
