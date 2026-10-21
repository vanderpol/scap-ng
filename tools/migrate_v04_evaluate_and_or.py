#!/usr/bin/env python3
"""Reversible AND/OR/ONE/XOR spelling for Test-result evaluate expressions.

Scope is only assessment.evaluate, NEVER Test.require.items,
Test.require.all_items_must, matching cardinality, State field/group logic,
Objects, Filters, or Variable operand value_match.

The released v0.4.0 expression schema currently expects all/any/one/odd.
This tool creates an opt-in candidate; promotion requires full versioned
schema migration. Refs #248 #239.
"""
from __future__ import annotations
from copy import deepcopy
import hashlib
import json

from audit_v04_and_or_scope_projection import evaluate_projection,evaluate_inverse


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,
             ensure_ascii=False,separators=(",",":")).encode()).hexdigest()


def changed_sites(value,prefix=()):
    out=[]
    if isinstance(value,dict):
        if len(value)==1:
            key,child=next(iter(value.items()))
            if key in ("all","any","odd"):
                out.append({"site":list(prefix),"from":key,
                            "to":{"all":"and","any":"or","odd":"xor"}[key]})
        for k,v in value.items():
            out.extend(changed_sites(v,prefix+(k,)))
    elif isinstance(value,list):
        for i,v in enumerate(value):
            out.extend(changed_sites(v,prefix+(i,)))
    return out


def migrate(document):
    result=deepcopy(document)
    a=result.get("assessment") if isinstance(result,dict) else None
    if not isinstance(a,dict) or a.get("mode")!="automated":
        return result,[]
    old=a.get("evaluate")
    if old is None:
        raise ValueError("Source automated Test evaluation is missing")
    new=evaluate_projection(old)
    changes=changed_sites(old)
    if changes:
        a["evaluate"]=new
        row={"assessment_id":a["id"],
             "source_evaluate_sha256":digest(old),
             "candidate_evaluate_sha256":digest(new),
             "replaced_operators":changes}
        return result,[row]
    if new!=old:
        raise ValueError("Unexpected Test-evaluation normalization")
    return result,[]


def restore(candidate,ledger):
    recovered=deepcopy(candidate)
    a=recovered.get("assessment") if isinstance(recovered,dict) else None
    if not ledger:
        return recovered
    if not isinstance(a,dict) or len(ledger)!=1 or a.get("id")!=ledger[0]["assessment_id"]:
        raise ValueError("Wrong Test-result evaluation inversion identity")
    if digest(a.get("evaluate"))!=ledger[0]["candidate_evaluate_sha256"]:
        raise ValueError("Changed normalized Test-result logical expression")
    a["evaluate"]=evaluate_inverse(a["evaluate"])
    if digest(a["evaluate"])!=ledger[0]["source_evaluate_sha256"]:
        raise ValueError("Inverse lost original Test-result operators")
    if changed_sites(a["evaluate"])!=ledger[0]["replaced_operators"]:
        raise ValueError("Lossy Test-result operand conversion")
    return recovered


def assert_inverse(original,new,ledger):
    if restore(new,ledger)!=original:
        raise ValueError("evaluate-only AND/OR migration changed source Assessment")
    probe,copies=migrate(original)
    if probe!=new or copies!=ledger:
        raise ValueError("Test-result AND/OR migration is nondeterministic")
    return True
