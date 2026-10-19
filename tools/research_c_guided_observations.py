#!/usr/bin/env python3
"""Refs #245: compiler-backed research C Guided view for shared observations.

Read-only semantic projection, not editor UI. No scanner outcome, source
formatting, general-purpose C grammar, or automatic semantic migration.
"""
from __future__ import annotations
from copy import deepcopy

from research_c_windows_shared_native import compile_native_c_windows

def project_c_shared_guided(document):
    compiled=compile_native_c_windows(document)
    observation_cards=[]
    for name,original in document["observations"].items():
        from_capability,selector=next(iter(original["from"].items()))
        consumers=[check_name for check_name,check in document["checks"].items()
                   if check["observation"]==name]
        if not consumers:
            raise ValueError("orphan observation cannot be hidden in Guided")
        observation_cards.append({
            "id":name,
            "source_object":original["source_object"],
            "capability":from_capability,
            "selector_or_collection":deepcopy(selector),
            "used_by":consumers,
            "execution_provenance_required":True,
        })
    cards=[]
    for key,check in document["checks"].items():
        m=check["must"]
        source_test=check["source_test"]
        c=compiled["tests"][source_test]
        scope=m["items"]
        if scope=="every_item":
            values=m["any_record_state_every_value_equals"]
            caption=("One or more collected Items must exist. Every Item must "
                     "contain a result record, with domainrole values that "
                     "all equal either one whole-state alternative.")
            advanced={
                "record":m["record"],"record_requirement":m["record_requirement"],
                "field":m["field"],"field_requirement":m["field_requirement"],
                "whole_record_state_alternatives":deepcopy(values),
                "not_equivalent_to_some_value_in_set":True,
            }
        elif scope=="any_item":
            op,value=next(iter(m["predicate"].items()))
            caption=("One or more Items must exist; one Item must satisfy the "
                     "trustee_name predicate. Do not combine fields from Items.")
            advanced={
                "same_item_field":m["same_item_field"],
                "field_requirement":m["field_values"],
                "operation":op,"expected":value,
                "regex_dialect_verified":False if op=="pattern_match" else None,
            }
        else:
            raise ValueError("unrecognized explicit Item scope")
        cards.append({
            "id":key,"source_test":source_test,
            "using_observation":check["observation"],
            "item_scope":scope,"plain_english_scope":caption,
            "record_or_field_details":advanced,
            "source_compatible_test_requirement":c["require"],
            "complex_record_requires_expert_disclosure":scope=="every_item",
            "results_scanner_verified":False,
        })

    def convert(node,depth=0):
        if depth>128 or not isinstance(node,dict) or len(node)!=1:
            raise ValueError("unsupported C logic node")
        kind,value=next(iter(node.items()))
        if kind=="check":
            if value not in document["checks"]:
                raise ValueError("unknown check in required logic")
            return {"kind":"check","check_id":value}
        if kind not in ("every","one_of","exactly_one","odd_count") or (
            not isinstance(value,list) or not value
        ):
            raise ValueError("unsupported Item-vs-Assessment logic")
        return {"kind":kind,"children":[convert(n,depth+1) for n in value]}

    tree=convert(document["require"])
    return {
        "stage":"C_RESEARCH_GUIDED_OBSERVATIONS_NOT_EDITOR",
        "native_specification":"0.4.0",
        "observations":observation_cards,"checks":cards,
        "requirement_tree":tree,
        "distinct_observations":len(observation_cards),
        "distinct_checks":len(cards),
        "source_yaml_mutated":False,
        "scanner_verification":"NOT_SCANNER_VERIFIED",
        "not_proven":["live collection","OVAL source oracle","source-preserving editor"],
    }
