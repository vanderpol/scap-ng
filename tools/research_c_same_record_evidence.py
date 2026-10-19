#!/usr/bin/env python3
"""Refs #245: C synthetic same-record field-correlation evaluator.

Delegates cardinality/six-state aggregation to pinned A/OVAL table functions.
Only precollected typed record Items and scalar equals; NOT WMI collection,
general OVAL record conformance, nested record grammar or scanner parity.
"""
from __future__ import annotations

from oval_result_truth_tables import evaluate_record_entity, evaluate_record_field
from research_c_common_evaluation import population_outcome

MODES=frozenset(("any_item","every_item"))

def evaluate_same_record_requirement(required, observed, *, item_scope):
    if item_scope not in MODES or not isinstance(required,dict) or (
        not required or any(type(k) is not str or not k or
                            type(v) not in (str,int,bool) for k,v in required.items())
    ):
        raise ValueError("explicit scalar field predicates and Item scope required")
    if not isinstance(observed,dict) or set(observed)!={"status","items","capability"} or (
        observed["status"] not in ("complete","incomplete","error","not_collected","not_applicable")
        or type(observed["capability"]) is not str or not observed["capability"]
        or not isinstance(observed["items"],list)
    ):
        raise ValueError("typed recorded evidence with collection status required")
    if observed["status"] in ("error","not_collected","not_applicable") and observed["items"]:
        raise ValueError("terminal failure cannot claim trusted Items")
    items=[]
    seen=set()
    for entry in observed["items"]:
        if not isinstance(entry,dict) or set(entry)!={"id","record"} or (
            type(entry["id"]) is not str or not entry["id"] or
            entry["id"] in seen or not isinstance(entry["record"],dict)
        ):
            raise ValueError("duplicate/malformed parent Item or record")
        seen.add(entry["id"])
        outcomes=[]
        for field, expectation in required.items():
            values=entry["record"].get(field)
            if values is None:
                # A/OVAL record field absence is an Error, not a successful
                # absent Item or permission to borrow the field from a sibling.
                field_outcome=evaluate_record_field(field, [])
            elif not isinstance(values,list) or not values:
                field_outcome="error"
            else:
                compared=[
                    "true" if type(actual) is type(expectation)
                    and actual==expectation else "false"
                    for actual in values
                ]
                field_outcome=evaluate_record_field(
                    field, compared, entity_check="all")
            outcomes.append(field_outcome)
        items.append({"id":entry["id"],
                      "outcome":evaluate_record_entity(outcomes).replace(" ","_")})
    value=population_outcome(
        {"exists":"at_least_one_exists",
         "items_match":"every" if item_scope=="every_item" else "one_of",
         "has_state":True},
        {"capability":observed["capability"],
         "status":observed["status"],"items":items,
         "does_not_exist":0,"error":0,"not_collected":0})
    return {"result":value,"per_item_results":items,
            "all_fields_same_record":True,
            "missing_required_field_is_error":True,
            "synthetic_record_evidence_only":True,
            "scanner_executed":False}
