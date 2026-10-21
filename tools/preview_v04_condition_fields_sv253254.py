#!/usr/bin/env python3
"""Source-reversible 0.4.0 condition/require/fields *naming pilot only*.

Narrow original OVAL source-backed Windows 11 SV-253254:
    State 1: type=string AND value=Enterprise
    State 2: type=string AND value=EnterpriseS
    Test:   OR across these complete States; all collected Items must match;
            at least one collected Item must exist.

Replace exactly one source-proven State group with a first-read candidate:
    - require: <shared field-existence + matching requirement>
      or:
        - fields: {type: ..., value: ...}
        - fields: {type: ..., value: ...}

This avoids 'state' and 'fields_require' entirely in author-facing syntax.
It is NOT current v0.4 schema; do not claim full OVAL roundtrip or scanner
equivalence from a single real registry Test. Refs #248 #239.
"""
from __future__ import annotations
from copy import deepcopy
import hashlib,json

SOURCE_TEST="editionid-enterprise-or-enterprises-test"
SOURCE_ASSESSMENT="SV-253254.automated"


def sha(v):
    return hashlib.sha256(json.dumps(v,sort_keys=True,
        separators=(",",":"),ensure_ascii=False).encode()).hexdigest()


def preview(doc):
    new=deepcopy(doc)
    a=new.get("assessment") if isinstance(new,dict) else None
    if (not isinstance(a,dict) or a.get("id")!=SOURCE_ASSESSMENT
            or a.get("specification",{}).get("version")!="0.4.0"):
        raise ValueError("Pinned SV-253254 0.4.0 Assessment is required")
    t=a["tests"]
    if set(t)!={SOURCE_TEST}:
        raise ValueError("Original single Windows registry Test identity changed")
    test=t[SOURCE_TEST]
    if test.get("capability")!="windows.registry" or "states_match" in test:
        raise ValueError("Expected first-pass complete-State OR normalization")
    field_require=test.get("state_fields_require")
    if field_require!="at_least_one_exists_and_all_match":
        raise ValueError("Source-preserved scalar field requirement missing")
    req=test.get("require")
    if not isinstance(req,dict) or set(req)!={"items","all_items_must"}:
        raise ValueError("Original Item-matching scope changed")
    if req["items"]!="one_or_more" or len(req["all_items_must"])!=1:
        raise ValueError("Original Item existence or State-level OR changed")
    group=req["all_items_must"][0]
    if set(group)!={"or"} or len(group["or"])!=2:
        raise ValueError("Expected OR of two separately proven complete States")
    conditions=[]
    for i,state in enumerate(group["or"]):
        if set(state)!={"and"} or len(state["and"])!=2:
            raise ValueError(f"OVAL State {i} does not have exact field-level AND")
        fields={}
        for entity in state["and"]:
            if not isinstance(entity,dict) or len(entity)!=1:
                raise ValueError("Invalid original field predicate")
            name,predicate=next(iter(entity.items()))
            if name in fields:
                raise ValueError("Cannot silently merge repeated OVAL field names")
            if not isinstance(predicate,dict) or not predicate:
                raise ValueError("Empty or invalid source field predicate")
            fields[name]=deepcopy(predicate)
        if set(fields)!={"type","value"}:
            raise ValueError("Original registry State field pair differs")
        if fields["type"]!={"equals":"string"}:
            raise ValueError("Original State type predicate differs")
        if fields["value"]!={"equals":("Enterprise","EnterpriseS")[i]}:
            raise ValueError("Original State value predicate differs")
        conditions.append({"fields":fields})
    old=sha(test)
    req["all_items_must"]=[{"require":field_require,"or":conditions}]
    test.pop("state_fields_require")
    ledger={"assessment_id":SOURCE_ASSESSMENT,"test_id":SOURCE_TEST,
            "old_test_sha256":old,"candidate_test_sha256":sha(test),
            "field_requirement":field_require,
            "complete_state_count":len(conditions),
            "source_item_existence":req["items"],
            "source_matching_items":"all",
            "source_original_oval_state_operator":"OR",
            "source_original_oval_field_operator":"AND"}
    return new,ledger


def restore(doc,ledger):
    old=deepcopy(doc)
    test=old["assessment"]["tests"][SOURCE_TEST]
    if sha(test)!=ledger["candidate_test_sha256"]:
        raise ValueError("Preview mutated since source proof")
    req=test["require"]
    groups=req.get("all_items_must")
    if not isinstance(groups,list) or len(groups)!=1:
        raise ValueError("Missing preview condition group")
    group=groups[0]
    if list(group)!=["require","or"] or group["require"]!=ledger["field_requirement"]:
        raise ValueError("Shared condition requirement changed")
    if not isinstance(group["or"],list) or len(group["or"])!=2:
        raise ValueError("Source whole-State OR alternatives changed")
    original=[]
    for entry in group["or"]:
        if set(entry)!={"fields"} or not isinstance(entry["fields"],dict):
            raise ValueError("Source-recoverable fields mapping missing")
        original.append({"and":[{key:deepcopy(value)}
                                for key,value in entry["fields"].items()]})
    req["all_items_must"]=[{"or":original}]
    test["state_fields_require"]=ledger["field_requirement"]
    if sha(test)!=ledger["old_test_sha256"]:
        raise ValueError("Condition/fields reformat lost original State fields")
    return old


def exact_inverse(source,candidate,ledger):
    if restore(candidate,ledger)!=source:
        raise ValueError("Original State structure not exactly recovered")
    repeat,reledger=preview(source)
    if repeat!=candidate or reledger!=ledger:
        raise ValueError("Condition naming rewrite not deterministic")
    return True
