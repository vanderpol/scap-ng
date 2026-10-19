#!/usr/bin/env python3
"""Refs #245: source-compatible three-check OVAL -> one native C grammar.

Reuse unified C observations + checks + require, not a second dialect.
First real eligible feature family: source singleton/objectless provider
(linux.sestatus) with independent typed State checks and an OVAL AND tree.
No source Test may be omitted or silently rewritten. All other shapes fail.
"""
from __future__ import annotations
from copy import deepcopy
import re

from research_c_original_oval_to_authored_c import (
    NotNativeCConvertible, reject, project_fields, _entities, _same_source_semantics)
from research_c_require_language import _mapping
from research_c_unified_compiler import compile_c_unified

ID=re.compile(r"[^a-z0-9]+")
def alias_of(title):
    if type(title) is not str or not title.strip():
        reject("SOURCE_TEST_DESCRIPTION_MISSING")
    result=ID.sub("_",title.lower()).strip("_")[:63].rstrip("_")
    if not result or not result[0].isalpha():
        reject("SOURCE_TEST_TITLE_HAS_NO_SAFE_ALIAS")
    return result

def convert_objectless_many(a):
    if not isinstance(a,dict) or a.get("mode")!="automated":
        reject("ASSESSMENT_NOT_AUTOMATED")
    if a.get("variables"):
        reject("VARIABLE_SOURCE_GRAPH_NEEDS_COMPATIBILITY")
    tests=a.get("tests") or {}
    if not isinstance(tests,dict) or not 2<=len(tests)<=64:
        reject("NOT_A_BOUNDED_MULTI_TEST_DEFINITION")
    # A source singleton Object does not imply reusable acquired Items.
    # The versioned C mapping must explicitly designate an objectless test.
    objects=a.get("objects") or {}
    if not isinstance(objects,dict) or len(objects)!=1:
        reject("SOURCE_OBJECTS_NOT_SINGLETON")
    oid,obj=next(iter(objects.items()))
    if not isinstance(obj,dict) or set(obj)!={"capability","object_title"}:
        reject("SINGLETON_OBJECT_IS_NOT_OBJECTLESS")
    capability=obj["capability"]
    try:
        native=_mapping(capability)
    except Exception as exc:
        reject("CAPABILITY_MAPPING_MISSING: "+str(exc))
    if native.get("test_source",{}).get("kind")!="none":
        reject("CAPABILITY_NOT_PROVED_OBJECTLESS")
    states=a.get("states") or {}
    if not isinstance(states,dict):
        reject("UNKNOWN_STATE_MAP")
    checks={};reverse={};native_states={};used_states=set()
    for tid,t in sorted(tests.items()):
        if not isinstance(t,dict) or set(t)-{
            "capability","check","check_existence","object",
            "states","reported_elements","test_title"}:
            reject("UNREVIEWED_SOURCE_TEST_ATTRS")
        if (t.get("capability")!=capability or t.get("object")!=oid
                or t.get("reported_elements")!="all"):
            reject("TEST_SINGLETON_COLLECTION_IDENTITY_MISMATCH")
        if (t.get("check_existence")!="at_least_one_exists"
                or t.get("check")!="all"):
            reject("SOURCE_TEST_UNSUPPORTED_QUANTIFIER")
        refs=t.get("states") or []
        if len(refs)!=1 or refs[0] not in states:
            reject("STATE_LIST_NOT_ONE_NAMED_STATE")
        sid=refs[0]
        if sid in used_states:
            reject("SHARED_STATE_COMPLEX_SCOPE")
        used_states.add(sid)
        st=states[sid]
        if (not isinstance(st,dict) or set(st)!={"capability","state_title","state"}
                or st["capability"]!=capability):
            reject("STATE_UNREVIEWED_METADATA")
        fields=project_fields(st["state"])
        alias=alias_of(t.get("test_title"))
        if alias in reverse:
            reject("DUPLICATE_MEANINGFUL_TEST_TITLE")
        reverse[alias]=tid
        native_states[alias]=_entities(st["state"])
        checks[alias]={
            "observation":"system_status",
            "source_test":tid,
            "must":{"every_item":fields},
        }
    if used_states!=set(states):
        reject("UNUSED_SOURCE_STATE")
    source_expr=a.get("evaluate")
    if (not isinstance(source_expr,dict) or set(source_expr)!={"all"}
            or not isinstance(source_expr["all"],list)):
        reject("NOT_PROVEN_0_3_OVAL_AND_REQUIREMENT")
    ordered=[]
    for part in source_expr["all"]:
        if not isinstance(part,dict) or set(part)!={"test"}:
            reject("NESTED_SOURCE_EXPRESSION_REQUIRES_SEPARATE_PROOF")
        old=part["test"]
        matches=[alias for alias,tid in reverse.items() if tid==old]
        if len(matches)!=1 or matches[0] in ordered:
            reject("DUPLICATE_OR_MISSING_SOURCE_TEST_IN_AND")
        ordered.append(matches[0])
    if len(ordered)!=len(tests):
        reject("SOURCE_EVALUATE_LOST_TEST")
    doc={
        "id":a["id"],
        "observations":{"system_status":{"from":{capability:{}}}},
        "checks":checks,
        "require":{"every":[{"check":alias} for alias in ordered]},
    }
    try:
        compiled=compile_c_unified(doc)
    except (ValueError,TypeError,KeyError) as exc:
        reject("UNIFIED_NATIVE_C_COMPILER_BLOCKER: "+str(exc))
    if set(compiled["tests"])!=set(checks):
        reject("COMPILED_TEST_COVERAGE_MISMATCH")
    if (compiled.get("shared_objects") or
        set(compiled.get("shared_singletons",{}))!={"system_status"}):
        reject("COMPILER_FABRICATED_NATIVE_COLLECTION_OBJECT")
    consumers=compiled["shared_singletons"]["system_status"]["consumer_tests"]
    if set(consumers)!=set(checks) or len(consumers)!=len(checks):
        reject("SHARED_SINGLETON_CONSUMER_LOSS")
    for alias,tid in reverse.items():
        generated=compiled["tests"][alias]
        if generated.get("object") is not None:
            reject("OBJECTLESS_PROVIDER_INCORRECTLY_RECOLLECTED")
        if generated["capability"]!=capability or (
            generated.get("require")!="at_least_one_exists_and_all_match"):
            reject("C_TEST_SEMANTIC_DRIFT")
        expected=native_states[alias]
        if len(generated.get("states") or [])!=len(expected):
            reject("C_FIELDS_COUNT_DRIFT")
        for out,original in zip(generated["states"],expected):
            field=original["field"]
            op={"equals":"equals","pattern match":"matches_regex"}[original["operation"]]
            if out!={field:{"require":"at_least_one_exists_and_all_match",
                            op:original["value"]}}:
                reject("C_FIELDS_TYPED_CONTENT_DRIFT")
    # The C AND compiler shares the source OVAL six-state truth-table model;
    # this gate does NOT infer truth from source Item collection.
    result={"stage":"NATIVE_C_MULTICHECK_SOURCE_COMPATIBILITY_PROVED",
            "source_assessment_id":a["id"],
            "authored_c":doc,
            "source_test_crosswalk":deepcopy(reverse),
            "native_c_compiled_tests":deepcopy(compiled["tests"]),
            "C_uses_one_shared_observation":True,
            "A_source_semantic_projection_passed":True,
            "OVAL_actual_scanner_parity_proven":False}
    return result
