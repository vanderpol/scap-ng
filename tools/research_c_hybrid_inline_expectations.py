#!/usr/bin/env python3
"""Refs #245: C hybrid expected-value authoring without constant Variables.

Works over source-compatible original OVAL typed graph, not new evaluator.
Move simple scalar/path States and single-consumer string constant Variables
into author-facing expected values. Lower independent C values back to the
EXACT original typed OVAL State + constant Variable representation, including
explicit original variable_check quantifier. Unproven shapes fail closed.
"""
from __future__ import annotations
from copy import deepcopy
from collections import Counter

from research_c_hybrid_must_overlay import (
    STAGE, present_hybrid_must, compile_hybrid_must,
    prove_original_hybrid, reject)

INLINE_STAGE="C_HYBRID_AUTHOR_VALUES_INLINE_OVAL_EXECUTION_IR_RESTORED"
FIELD_SET={"datatype","entity_check","entity_existence","field","operation","value"}

def _count_refs(node,key):
    if isinstance(node,dict):
        count=sum(1 for k,v in node.items()
                  if k=="variable" and v==key)
        return count+sum(_count_refs(v,key) for v in node.values())
    if isinstance(node,list):
        return sum(_count_refs(v,key) for v in node)
    return 0

def present_inline_expectations(source):
    doc=present_hybrid_must(source)
    original=doc["compatibility"]
    states=original["states"]
    variables=original["variables"]
    if not states or len(states)>128 or len(variables)>128:
        reject("bounded nonempty source expected States and Variables required")
    original_refs=set()
    authored_states={}
    for sid,raw in sorted(states.items()):
        if not isinstance(raw,dict) or set(raw)!={
            "capability","state_title","state"}:
            reject("source State metadata unproven")
        field=raw["state"]
        if (not isinstance(field,dict) or not FIELD_SET<=set(field) or
            set(field)-FIELD_SET-{"variable_check"} or
            raw["capability"]!="unix.file" or
            field["datatype"]!="string" or
            field["entity_check"]!="all" or
            field["entity_existence"]!="at_least_one_exists" or
            field["field"]!="path" or field["operation"]!="equals"):
            reject("unsupported original typed State field")
        value=field["value"]
        entry={"description":raw["state_title"],"field":"path"}
        if type(value) is str and "variable_check" not in field:
            entry["equals"]=value
        elif isinstance(value,dict) and set(value)=={"variable"}:
            vid=value["variable"]
            if vid in original_refs:
                reject("shared constant Variable needs explicit reuse plan")
            original_refs.add(vid)
            var=variables.get(vid)
            if (not isinstance(var,dict) or set(var)!={
                "datatype","expression","kind","title"} or
                var["kind"]!="constant" or var["datatype"]!="string" or
                not isinstance(var["expression"],dict) or
                set(var["expression"])!={"literal"} or
                not isinstance(var["expression"]["literal"],list) or
                not 1<=len(var["expression"]["literal"])<=128 or
                any(type(x) is not str for x in var["expression"]["literal"]) or
                field.get("variable_check")!="only one"):
                reject("unsupported constant Variable type or source quantifier")
            # A Variable may not feed Objects, other Variables, filters, or
            # additional States. Such source sharing must not be erased.
            if _count_refs(source,vid)!=1:
                reject("original constant Variable has other consumers")
            entry["equals"]=deepcopy(var["expression"]["literal"])
            entry["value_match"]="one"
            entry["source_constant"]={"id":vid,"description":var["title"]}
        else:
            reject("unsupported original literal/value reference")
        authored_states[sid]=entry
    if set(variables)!=original_refs:
        reject("not all source Variables are safe single-use literal constants")
    # AUTHORING: fixed values live at expected-value consumers, not in
    # Variable declarations; typed A fields recreated by lowering.
    doc["compatibility"]["variables"]={}
    doc["compatibility"]["states"]={}
    doc["expected_values"]=authored_states
    doc["stage"]=INLINE_STAGE
    return doc

def compile_inline_expectations(authored):
    if (not isinstance(authored,dict) or
        set(authored)!={"stage","compatibility","checks","require",
                        "source_ir_sha256","expected_values"} or
        authored["stage"]!=INLINE_STAGE):
        reject("unsupported C inline-value authoring form")
    out=deepcopy(authored)
    out["stage"]=STAGE
    expectations=out.pop("expected_values")
    if (not isinstance(expectations,dict) or
        not 1<=len(expectations)<=128 or
        out["compatibility"]["states"] or
        out["compatibility"]["variables"]):
        reject("typed source States/Variables must be synthesized, not duplicated")
    states={};variables={}
    for sid,entry in expectations.items():
        if (type(sid) is not str or not sid or
            not isinstance(entry,dict) or
            set(entry) not in (
                {"description","field","equals"},
                {"description","field","equals","value_match","source_constant"})):
            reject("invalid expected-value authoring")
        if (entry["field"]!="path" or
            type(entry["description"]) is not str or
            not entry["description"].strip()):
            reject("expected source field/documentation unsupported")
        expected=entry["equals"]
        raw={"datatype":"string","entity_check":"all",
             "entity_existence":"at_least_one_exists",
             "field":"path","operation":"equals"}
        if type(expected) is str and len(entry)==3:
            raw["value"]=expected
        elif (isinstance(expected,list) and 1<=len(expected)<=128 and
              all(type(x) is str for x in expected) and
              entry.get("value_match")=="one"):
            provenance=entry.get("source_constant")
            if not isinstance(provenance,dict) or set(provenance)!={
                "id","description"}:
                reject("constant source provenance required")
            vid=provenance["id"]
            if type(vid) is not str or not vid or vid in variables:
                reject("duplicate or missing constant provenance")
            if type(provenance["description"]) is not str or not provenance[
                "description"].strip():
                reject("constant Variable source title required")
            variables[vid]={"datatype":"string",
                            "expression":{"literal":deepcopy(expected)},
                            "kind":"constant","title":provenance["description"]}
            raw["value"]={"variable":vid}
            raw["variable_check"]="only one"
        else:
            reject("unsupported scalar/array original value quantifier")
        states[sid]={"capability":"unix.file",
                     "state_title":entry["description"],"state":raw}
    out["compatibility"]["states"]=states
    out["compatibility"]["variables"]=variables
    # Existing hybrid compiler is the single source of truth for the
    # authored must/AND and typed graph; no alternate Set/Filter evaluator.
    return compile_hybrid_must(out)

def prove_inline_original(source,authored):
    rebuilt=compile_inline_expectations(authored)
    if rebuilt!=source:
        reject("authored expected values changed source OVAL typed graph")
    underlying=deepcopy(authored)
    underlying["stage"]=STAGE
    underlying.pop("expected_values")
    underlying["compatibility"]["states"]=deepcopy(source["states"])
    underlying["compatibility"]["variables"]=deepcopy(source["variables"])
    proof=prove_original_hybrid(source,underlying)
    return {**proof,
            "stage":INLINE_STAGE,
            "authored_constant_variable_declarations":0,
            "authored_named_expected_values":len(authored["expected_values"]),
            "compiler_rehydrated_source_variables":len(rebuilt["variables"]),
            "OVAL_runtime_parity_proven":False}
