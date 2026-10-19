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
    NotNativeCConvertible, reject, project_selection, project_fields, _entities, _same_source_semantics, OPS)
from research_c_require_language import _mapping
from research_c_unified_compiler import compile_c_unified

ID=re.compile(r"[^a-z0-9]+")
def alias_of(title, fields):
    """Prefer the actual State field over boilerplate OVAL Test descriptions.

    The original title remains in the source review/provenance; never cut
    a meaningful identifier halfway through. Ambiguous collisions reject.
    """
    if type(title) is not str or not title.strip():
        reject("SOURCE_TEST_DESCRIPTION_MISSING")
    if len(fields)==1:
        field=next(iter(fields))
        # Recognize only when the source title actually identifies the field,
        # not a fabricated assertion meaning or meaningless Test number.
        if (type(field) is str and re.fullmatch(r"[a-z][a-z0-9_]*",field)
                and re.search(r"(?<![a-z0-9_])"+re.escape(field)+r"(?![a-z0-9_])",
                              title.lower())):
            return field
    result=ID.sub("_",title.lower()).strip("_")
    if not result or not result[0].isalpha() or len(result)>90:
        reject("SOURCE_TEST_TITLE_UNSUITABLE_FOR_MEANINGFUL_ALIAS")
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
        fields=project_fields(st["state"],st["capability"])
        alias=alias_of(t.get("test_title"),fields)
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
        _same_source_semantics(tests[tid],generated,obj,native_states[alias],
                               source_singleton_objectless=True)
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


def convert_selected_shared_many(a):
    """Conservatively lower one genuine OVAL Object selected by 2+ Tests.

    C names the observation once, preserves its original Object identity,
    and uses the established unified compiler for each typed Test and AND.
    No source Variables, Sets, Filters, behaviors, shared States, unsupported
    existence/matching or hidden source attributes may be discarded.
    """
    if not isinstance(a,dict) or a.get("mode")!="automated":
        reject("SHARED_SELECTED_ASSESSMENT_NOT_AUTOMATED")
    if a.get("variables"):
        reject("VARIABLE_SOURCE_GRAPH_NEEDS_COMPATIBILITY")
    tests=a.get("tests") or {}
    objects=a.get("objects") or {}
    states=a.get("states") or {}
    if (not isinstance(tests,dict) or not 2<=len(tests)<=64 or
        not isinstance(objects,dict) or len(objects)!=1 or
        not isinstance(states,dict)):
        reject("SHARED_SELECTED_SOURCE_INVENTORY_UNSUPPORTED")
    oid,obj=next(iter(objects.items()))
    if (not isinstance(obj,dict) or
        set(obj)!={"capability","object_title","select"}):
        reject("SHARED_SELECTED_OBJECT_HAS_COMPLEX_COLLECTION")
    selectors=project_selection(obj)
    cap=obj["capability"]
    used_states=set()
    checks={}
    reverse={}
    entities={}
    for tid,t in sorted(tests.items()):
        if (not isinstance(t,dict) or set(t)-{
            "capability","check","check_existence","object",
            "states","reported_elements","test_title"}):
            reject("SHARED_SELECTED_TEST_HAS_EXTRA_SOURCE_FIELDS")
        if (t.get("object")!=oid or t.get("capability")!=cap or
            t.get("reported_elements")!="all" or
            t.get("check")!="all" or
            t.get("check_existence")!="at_least_one_exists"):
            reject("SHARED_SELECTED_TEST_HAS_DIFFERENT_SOURCE_SCOPE")
        refs=t.get("states")
        if not isinstance(refs,list) or len(refs)!=1 or refs[0] not in states:
            reject("SHARED_SELECTED_TEST_NEEDS_ONE_TYPED_STATE")
        sid=refs[0]
        if sid in used_states:
            reject("SHARED_SELECTED_STATE_REUSE_UNPROVEN")
        used_states.add(sid)
        st=states[sid]
        if (not isinstance(st,dict) or
            set(st)!={"capability","state_title","state"} or
            st["capability"]!=cap):
            reject("SHARED_SELECTED_STATE_METADATA_UNSUPPORTED")
        fields=project_fields(st["state"],st["capability"])
        alias=alias_of(t.get("test_title"),fields)
        if alias in checks:
            # Two source Tests may assert different values on the SAME
            # observed field. Do not collapse them to the same field alias.
            alias=ID.sub("_",t["test_title"].lower()).strip("_")
        if alias in checks or len(alias)>63 or not re.fullmatch(
            r"[a-z][a-z0-9_]*",alias):
            reject("SHARED_SELECTED_TEST_ALIAS_COLLISION_OR_TOO_LONG")
        checks[alias]={"observation":"original_collection",
                       "source_test":tid,
                       "must":{"every_item":fields}}
        reverse[tid]=alias
        entities[tid]=_entities(st["state"])
    if used_states!=set(states):
        reject("SHARED_SELECTED_UNUSED_SOURCE_STATES")
    evaluate=a.get("evaluate")
    if (not isinstance(evaluate,dict) or set(evaluate)!={"all"} or
        not isinstance(evaluate["all"],list)):
        reject("SHARED_SELECTED_SOURCE_AND_REQUIRED")
    ordered=[]
    for part in evaluate["all"]:
        if (not isinstance(part,dict) or set(part)!={"test"} or
            part["test"] not in reverse):
            reject("SHARED_SELECTED_UNRESOLVED_OR_NESTED_CRITERIA")
        ordered.append(reverse[part["test"]])
    if len(ordered)!=len(tests) or len(set(ordered))!=len(tests):
        reject("SHARED_SELECTED_SOURCE_CHECK_INVENTORY_CHANGED")
    doc={"id":a["id"],
         "observations":{"original_collection":{
             "source_object":oid,"from":{cap:selectors}}},
         "checks":checks,
         "require":{"every":[{"check":alias} for alias in ordered]}}
    try:
        compiled=compile_c_unified(doc)
    except (ValueError,KeyError,TypeError) as exc:
        reject("SHARED_SELECTED_UNIFIED_C_NOT_SUPPORTED: "+str(exc))
    if (set(compiled["tests"])!=set(checks) or
        set(compiled["shared_objects"])!={oid} or
        compiled.get("shared_singletons")):
        reject("SHARED_SELECTED_COMPILER_CHANGED_COLLECTION_IDENTITY")
    for tid,alias in reverse.items():
        output=deepcopy(compiled["tests"][alias])
        if output.get("object")!=oid:
            reject("SHARED_SELECTED_TEST_NO_LONGER_REFERENCES_ONE_OBJECT")
        output["object"]=deepcopy(compiled["shared_objects"][oid])
        _same_source_semantics(tests[tid],output,obj,entities[tid])
    return {"stage":"NATIVE_C_SHARED_SELECTED_MULTI_SOURCE_COMPATIBILITY_PROVED",
            "source_assessment_id":a["id"],
            "authored_c":doc,
            "source_test_crosswalk":{alias:tid for tid,alias in reverse.items()},
            "source_test_documentation":{
                alias:tests[tid]["test_title"] for tid,alias in reverse.items()},
            "native_c_compiled_tests":deepcopy(compiled["tests"]),
            "C_uses_one_shared_observation":True,
            "A_source_semantic_projection_passed":True,
            "OVAL_actual_scanner_parity_proven":False}


def convert_distinct_selected_many(a):
    """Original OVAL AND with 2+ independent, explicitly selected Objects.

    Use ONE C frontend, not a second execution model. Fail closed unless
    every Object and State belongs to exactly one source Test, and there
    are no Variables, Sets, Filters, behavior side effects or hidden dataflow.
    """
    if not isinstance(a,dict) or a.get("mode")!="automated":
        reject("MULTI_DISTINCT_ASSESSMENT_UNSUPPORTED")
    if a.get("variables"):
        reject("VARIABLE_SOURCE_GRAPH_NEEDS_COMPATIBILITY")
    tests=a.get("tests") or {}
    objects=a.get("objects") or {}
    states=a.get("states") or {}
    if (not isinstance(tests,dict) or not 2<=len(tests)<=64 or
        not isinstance(objects,dict) or not isinstance(states,dict)):
        reject("MULTI_DISTINCT_BOUNDED_SOURCE_INVENTORY_REQUIRED")
    source_to_alias={}
    checks={}
    used_objects=set()
    used_states=set()
    comparisons={}
    for tid,t in sorted(tests.items()):
        if (not isinstance(t,dict) or set(t)-{
            "capability","check","check_existence","object","states",
            "reported_elements","test_title"} or
            t.get("check")!="all" or
            t.get("check_existence")!="at_least_one_exists" or
            t.get("reported_elements")!="all"):
            reject("MULTI_DISTINCT_TEST_QUANTIFIER_OR_ATTRS_UNSUPPORTED")
        oid=t.get("object")
        if oid not in objects or oid in used_objects:
            reject("MULTI_DISTINCT_OBJECT_MISSING_OR_SHARED")
        used_objects.add(oid)
        obj=objects[oid]
        if (not isinstance(obj,dict) or
            set(obj)!={"capability","object_title","select"} or
            obj["capability"]!=t.get("capability")):
            reject("MULTI_DISTINCT_OBJECT_SET_FILTER_OR_CAPABILITY_UNSUPPORTED")
        selectors=project_selection(obj)
        refs=t.get("states")
        if (not isinstance(refs,list) or len(refs)!=1 or
            refs[0] not in states or refs[0] in used_states):
            reject("MULTI_DISTINCT_STATE_REUSE_OR_MISSING")
        sid=refs[0]
        used_states.add(sid)
        state=states[sid]
        if (not isinstance(state,dict) or
            set(state)!={"capability","state_title","state"} or
            state["capability"]!=t["capability"]):
            reject("MULTI_DISTINCT_STATE_METADATA_UNSUPPORTED")
        fields=project_fields(state["state"],state["capability"])
        alias=alias_of(t.get("test_title"),fields)
        if alias in checks:
            # Same State field with a different source Test condition:
            # use the full source Test purpose, not an ambiguous field ID.
            alias=ID.sub("_",t["test_title"].lower()).strip("_")
        if (alias in checks or len(alias)>63 or
            not re.fullmatch(r"[a-z][a-z0-9_]*",alias)):
            reject("MULTI_DISTINCT_SOURCE_ALIAS_UNSAFE")
        checks[alias]={"source_test":tid,
                       "from":{t["capability"]:selectors},
                       "must":{"every_item":fields}}
        source_to_alias[tid]=alias
        comparisons[tid]=(obj,_entities(state["state"]))
    if used_objects!=set(objects) or used_states!=set(states):
        reject("MULTI_DISTINCT_EXTRA_SOURCE_OBJECT_OR_STATE")
    tree=a.get("evaluate")
    if (not isinstance(tree,dict) or set(tree)!={"all"} or
        not isinstance(tree["all"],list)):
        reject("MULTI_DISTINCT_REQUIRE_EXPLICIT_AND")
    ordered=[]
    for branch in tree["all"]:
        if (not isinstance(branch,dict) or set(branch)!={"test"} or
            branch["test"] not in source_to_alias):
            reject("MULTI_DISTINCT_UNPROVEN_NESTED_SOURCE_LOGIC")
        ordered.append(source_to_alias[branch["test"]])
    if len(ordered)!=len(tests) or len(set(ordered))!=len(tests):
        reject("MULTI_DISTINCT_SOURCE_TEST_COVERAGE_DRIFT")
    c={"id":a["id"],"checks":checks,
       "require":{"every":[{"check":alias} for alias in ordered]}}
    try:
        compiled=compile_c_unified(c)
    except (ValueError,TypeError,KeyError) as exc:
        reject("MULTI_DISTINCT_UNIFIED_COMPILER_REJECTED: "+str(exc))
    if (set(compiled["tests"])!=set(checks) or
        compiled.get("shared_objects") or compiled.get("shared_singletons")):
        reject("MULTI_DISTINCT_COMPILER_CONFLATED_SOURCE_OBJECTS")
    for tid,alias in source_to_alias.items():
        out=compiled["tests"][alias]
        obj,original_entities=comparisons[tid]
        _same_source_semantics(tests[tid],out,obj,original_entities)
    return {
        "stage":"NATIVE_C_DISTINCT_MULTI_SOURCE_COMPATIBILITY_PROVED",
        "source_assessment_id":a["id"],
        "authored_c":c,
        "source_test_crosswalk":{alias:tid for tid,alias in source_to_alias.items()},
        "source_test_documentation":{
            alias:tests[tid]["test_title"]
            for tid,alias in source_to_alias.items()},
        "native_c_compiled_tests":deepcopy(compiled["tests"]),
        "C_uses_independent_selected_objects":True,
        "A_source_semantic_projection_passed":True,
        "OVAL_actual_scanner_parity_proven":False,
    }
