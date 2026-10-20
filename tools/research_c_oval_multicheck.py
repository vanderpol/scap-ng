#!/usr/bin/env python3
"""Refs #245: source-compatible three-check OVAL -> one native C grammar.

Reuse unified C observations + checks + require, not a second dialect.
First real eligible feature family: source singleton/objectless provider
(linux.sestatus) with independent typed State checks and an OVAL AND tree.
No source Test may be omitted or silently rewritten. All other shapes fail.
"""
from __future__ import annotations
from copy import deepcopy
from collections import Counter
import re

from research_c_original_oval_to_authored_c import (
    NotNativeCConvertible, reject, project_selection, project_fields, _entities, _same_source_semantics, OPS, PAIR_CHECK, PRESENCE)
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

def source_test_field_must(test, fields):
    """Keep OVAL check=all/at least one/only one/none satisfy per source Test.

    Existence is a distinct axis. No advanced check_existence is inferred from
    the matching operation; unsupported pairs must remain compatibility data.
    """
    if test.get("check_existence") not in ("at_least_one_exists","all_exist","only_one_exists"):
        reject("SOURCE_TEST_ADVANCED_EXISTENCE_UNSUPPORTED")
    token=PAIR_CHECK.get(test.get("check"))
    modes={"all_match":"every_item","some_match":"any_item",
           "only_one_matches":"one_matching_item","none_match":"no_matching_item"}
    if token not in modes:
        reject("SOURCE_TEST_MATCHING_QUANTIFIER_UNSUPPORTED")
    if test["check_existence"]=="only_one_exists":
        if token!="all_match":
            reject("SOURCE_TEST_ONLY_ONE_MATCH_PAIR_NOT_REVIEWED")
        return {"exactly_one_item":fields}
    if test["check_existence"]=="all_exist":
        return {"items_exist":"all","items_match":{
            "all_match":"every","some_match":"some",
            "only_one_matches":"one","none_match":"none"}[token],
            "fields":fields}
    return {modes[token]:fields}


def source_boolean_tree_to_c(tree, source_to_alias, *, inventory_error):
    """Faithfully map original A/OVAL AND/OR, including nested groups.

    This is NOT a boolean rewrite: retain operand order, group boundaries,
    and one-to-one Test membership. Other source operations fail closed.
    """
    if (not isinstance(source_to_alias,dict) or not source_to_alias or
        len(set(source_to_alias.values()))!=len(source_to_alias)):
        reject("SOURCE_LOGIC_INVALID_TEST_CROSSWALK")
    encountered=[]
    def visit(node,depth=0):
        if depth>64 or not isinstance(node,dict) or len(node)!=1:
            reject("SOURCE_LOGIC_UNSUPPORTED_DEPTH_OR_NODE")
        op,value=next(iter(node.items()))
        if op=="test":
            if type(value) is not str or value not in source_to_alias:
                reject("SOURCE_LOGIC_UNKNOWN_TEST")
            encountered.append(value)
            return {"check":source_to_alias[value]}
        if op not in ("all","any") or not isinstance(value,list) or (
            not 1<=len(value)<=64
        ):
            reject("SOURCE_LOGIC_UNSUPPORTED_OPERATOR_OR_ARITY")
        return {("every" if op=="all" else "one_of"):
                [visit(child,depth+1) for child in value]}
    authored=visit(tree)
    if (set(encountered)!=set(source_to_alias) or
        len(encountered)!=len(source_to_alias)):
        reject(inventory_error)
    return authored


def verify_compiled_source_boolean_tree(compiled, original, source_to_alias):
    """Require exact structural re-projection, never mere leaf-set parity."""
    projected=compiled.get("expression",{}).get("source_tree")
    reverse={alias:tid for tid,alias in source_to_alias.items()}
    def visit(node):
        if not isinstance(node,dict) or len(node)!=1:
            reject("COMPILED_SOURCE_LOGIC_SHAPE_DRIFT")
        op,value=next(iter(node.items()))
        if op=="test":
            if type(value) is not str or value not in reverse:
                reject("COMPILED_SOURCE_LOGIC_TEST_DRIFT")
            return {"test":reverse[value]}
        if op not in ("all","any") or not isinstance(value,list):
            reject("COMPILED_SOURCE_LOGIC_OPERATOR_DRIFT")
        return {op:[visit(child) for child in value]}
    if visit(projected)!=original:
        reject("COMPILED_SOURCE_LOGIC_TREE_DRIFT")


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
        if (t.get("check_existence") not in ("at_least_one_exists","all_exist")
                or t.get("check") not in PAIR_CHECK):
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
            "must":source_test_field_must(t,fields),
        }
    if used_states!=set(states):
        reject("UNUSED_SOURCE_STATE")
    original_logic=a.get("evaluate")
    source_to_alias={tid:alias for alias,tid in reverse.items()}
    c_logic=source_boolean_tree_to_c(original_logic,source_to_alias,
        inventory_error="DUPLICATE_OR_MISSING_SOURCE_TEST_IN_LOGIC")
    doc={
        "id":a["id"],
        "observations":{"system_status":{"from":{capability:{}}}},
        "checks":checks,
        "require":c_logic,
    }
    try:
        compiled=compile_c_unified(doc)
    except (ValueError,TypeError,KeyError) as exc:
        reject("UNIFIED_NATIVE_C_COMPILER_BLOCKER: "+str(exc))
    verify_compiled_source_boolean_tree(compiled,original_logic,source_to_alias)
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
        expected_requirement=(tests[tid]["check_existence"]+
            "_and_"+PAIR_CHECK[tests[tid]["check"]])
        if generated["capability"]!=capability or (
            generated.get("require")!=expected_requirement):
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
            t.get("check") not in PAIR_CHECK or
            t.get("check_existence") not in ("at_least_one_exists","all_exist")):
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
                       "must":source_test_field_must(t,fields)}
        reverse[tid]=alias
        entities[tid]=_entities(st["state"])
    if used_states!=set(states):
        reject("SHARED_SELECTED_UNUSED_SOURCE_STATES")
    original_logic=a.get("evaluate")
    source_to_alias=dict(reverse)
    c_logic=source_boolean_tree_to_c(original_logic,source_to_alias,
        inventory_error="SHARED_SELECTED_SOURCE_CHECK_INVENTORY_CHANGED")
    doc={"id":a["id"],
         "observations":{"original_collection":{
             "source_object":oid,"from":{cap:selectors}}},
         "checks":checks,
         "require":c_logic}
    try:
        compiled=compile_c_unified(doc)
    except (ValueError,KeyError,TypeError) as exc:
        reject("SHARED_SELECTED_UNIFIED_C_NOT_SUPPORTED: "+str(exc))
    verify_compiled_source_boolean_tree(compiled,original_logic,source_to_alias)
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


def descriptive_distinct_alias(title,fields,existing,*,selectors=None,capability=None):
    """Keep source-purpose names, including long distinct-Object Test titles.

    The repeated OVAL Self-Assertion boilerplate can be removed only if its
    recognized selector/operation words remain explicit. Never truncate text
    and risk merging two independently assessed source Tests.
    """
    try:
        candidate=alias_of(title,fields)
    except NotNativeCConvertible as exc:
        if str(exc)!="SOURCE_TEST_TITLE_UNSUITABLE_FOR_MEANINGFUL_ALIAS":
            raise
        candidate=None
    if (candidate and len(candidate)<=63 and candidate not in existing and
        re.fullmatch(r"[a-z][a-z0-9_]*",candidate)):
        return candidate
    if type(title) is not str:
        reject("MULTI_DISTINCT_SOURCE_ALIAS_UNSAFE")
    # A different Test over the same State field may still have a concise
    # complete purpose title; prefer that over inventing a shortened alias.
    full_purpose=ID.sub("_",title.lower()).strip("_")
    if (full_purpose not in existing and len(full_purpose)<=63 and
        re.fullmatch(r"[a-z][a-z0-9_]*",full_purpose)):
        return full_purpose
    # A long original OVAL Test title may begin with an imperative
    # "Ensure ". Drop only that non-technical command word to form a
    # bounded, complete descriptive ID. Do not truncate the technical
    # subject, expected state, negation, or original provenance title.
    if full_purpose.startswith("ensure_"):
        concise=full_purpose[len("ensure_"):]
        if (concise not in existing and len(concise)<=63 and
            re.fullmatch(r"[a-z][a-z0-9_]*",concise)):
            return concise
    match=re.fullmatch(
        r"Test that the ([a-z][a-z0-9_]*)_object is supported with the "
        r"([a-z][a-z0-9_]*) entity "
        r"(equal to some value|not equal to some value|matching some regular expression)\.",
        title.strip(),re.I)
    if match is None:
        # This is a controlled subset of original OVAL Self-Assertion
        # purpose names, not a heuristic truncating arbitrary English.
        if capability=="unix.sysctl":
            m=re.fullmatch(
                r"Test that the sysctl test is supported with the name entity "
                r"with operation of '(equals|not equal|pattern match|"
                r"case insensitive equals|case insensitive not equal)'\\.",
                title.strip(),re.I)
            if m:
                op={"equals":"equals","not equal":"not_equal",
                    "pattern match":"matches_regex",
                    "case insensitive equals":"case_insensitive_equals",
                    "case insensitive not equal":"case_insensitive_not_equal"}[
                    m.group(1).lower()]
                candidate="name_"+op
                if candidate not in existing and len(candidate)<=63:
                    return candidate
        if capability=="linux.systemdunitproperty":
            # OVAL Test comments for this fixture repeat, and some claim
            # "not equal" when the actual Object predicate is equals.
            # Base the C ID on the real native Object selector, not an
            # inaccurate comment or opaque numeric source Test ID.
            if (re.match(r"^Test that systemdunitproperty test is supported",
                         title.strip(),re.I) and isinstance(selectors,dict) and
                set(selectors)=={"unit","property"}):
                pieces=[]
                for field in ("unit","property"):
                    sel=selectors[field]
                    if isinstance(sel,str):
                        op,value="equals",sel
                    elif isinstance(sel,dict) and len(sel)==1:
                        op,value=next(iter(sel.items()))
                    else:
                        break
                    if op not in ("equals","not_equal","matches_regex",
                                  "case_insensitive_equals",
                                  "case_insensitive_not_equal") or type(value) is not str:
                        break
                    slug=ID.sub("_",value.lower()).strip("_")
                    if not slug:
                        break
                    pieces.append((field,slug,{
                        "equals":"eq","not_equal":"ne",
                        "matches_regex":"re",
                        "case_insensitive_equals":"eq_ci",
                        "case_insensitive_not_equal":"ne_ci"}[op]))
                if len(pieces)==2:
                    candidate=("_".join((pieces[0][0],pieces[0][1],pieces[0][2],
                                          pieces[1][0],pieces[1][1],pieces[1][2])))
                    if (candidate not in existing and len(candidate)<=63 and
                        re.fullmatch(r"[a-z][a-z0-9_]*",candidate)):
                        return candidate
        reject("MULTI_DISTINCT_SOURCE_ALIAS_UNSAFE")
    _,selected_field,operation=match.groups()
    operation={"equal to some value":"equals",
               "not equal to some value":"not_equals",
               "matching some regular expression":"matches_regex"}[operation.lower()]
    compact=f"{selected_field}_{operation}"
    if (len(compact)>63 or compact in existing or
        not re.fullmatch(r"[a-z][a-z0-9_]*",compact)):
        reject("MULTI_DISTINCT_SOURCE_ALIAS_UNSAFE")
    return compact


def convert_distinct_selected_many(a):
    """Original OVAL AND with 2+ independent, explicitly selected Objects.

    Use ONE C frontend, not a second execution model. Fail closed unless
    every Object belongs to a known source Test; reused immutable source States
    retain exact identity/provenance. No Variables, Sets, Filters or hidden dataflow.
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
    if any(not isinstance(t,dict) or type(t.get("object")) is not str
           for t in tests.values()):
        reject("MULTI_DISTINCT_TEST_OBJECT_ID_REQUIRED")
    usage=Counter(t["object"] for t in tests.values())
    state_usage=Counter(
        sid for t in tests.values() if isinstance(t,dict)
        and isinstance(t.get("states"),list)
        for sid in t["states"] if type(sid) is str)
    reused={oid:"reused_collection_"+str(i+1)
            for i,oid in enumerate(sorted(o for o,n in usage.items() if n>1))}
    observations={}
    for tid,t in sorted(tests.items()):
        if (not isinstance(t,dict) or set(t)-{
            "capability","check","check_existence","object","states",
            "reported_elements","test_title"} or
            t.get("reported_elements")!="all"):
            reject("MULTI_DISTINCT_TEST_QUANTIFIER_OR_ATTRS_UNSUPPORTED")
        oid=t.get("object")
        if oid not in objects:
            reject("MULTI_DISTINCT_OBJECT_MISSING_OR_SHARED")
        used_objects.add(oid)
        obj=objects[oid]
        if (not isinstance(obj,dict) or
            set(obj)!={"capability","object_title","select"} or
            obj["capability"]!=t.get("capability")):
            reject("MULTI_DISTINCT_OBJECT_SET_FILTER_OR_CAPABILITY_UNSUPPORTED")
        selectors=project_selection(obj)
        refs=t.get("states")
        if not isinstance(refs,list) or len(refs)>1:
            reject("MULTI_DISTINCT_STATE_REUSE_OR_MISSING")
        if refs:
            sid=refs[0]
            if sid not in states:
                reject("MULTI_DISTINCT_STATE_REUSE_OR_MISSING")
            used_states.add(sid)
            state=states[sid]
            if (not isinstance(state,dict) or
                set(state)!={"capability","state_title","state"} or
                state["capability"]!=t["capability"]):
                reject("MULTI_DISTINCT_STATE_METADATA_UNSUPPORTED")
            fields=project_fields(state["state"],state["capability"])
            must=source_test_field_must(t,fields)
            original_entities=_entities(state["state"])
        else:
            # A State-free original Test evaluates collection existence only.
            # Its check aggregation is irrelevant only in the reviewed
            # check=all source shape; do not fabricate a matching State.
            if (t.get("check")!="all" or
                t.get("check_existence") not in PRESENCE):
                reject("MULTI_DISTINCT_STATE_FREE_PRESENCE_UNSUPPORTED")
            fields={}
            must=PRESENCE[t["check_existence"]]
            original_entities=[]
        alias=descriptive_distinct_alias(t.get("test_title"),fields,checks,
                                         selectors=selectors,capability=t["capability"])
        repeated_state=(sid if refs and state_usage[sid]>1 else None)
        source={"from":{t["capability"]:selectors}}
        if oid in reused:
            collection_alias=reused[oid]
            if collection_alias not in observations:
                observations[collection_alias]={
                    "source_object":oid,"from":deepcopy(source["from"])}
            elif observations[collection_alias]["from"]!=source["from"]:
                reject("MULTI_DISTINCT_REUSED_OBJECT_SELECTOR_DRIFT")
            checks[alias]={"source_test":tid,
                           "observation":collection_alias,
                           "must":must}
        else:
            checks[alias]={"source_test":tid,**source,"must":must}
        if repeated_state is not None:
            checks[alias]["source_state"]=repeated_state
        source_to_alias[tid]=alias
        comparisons[tid]=(obj,original_entities)
    if used_objects!=set(objects) or used_states!=set(states):
        reject("MULTI_DISTINCT_EXTRA_SOURCE_OBJECT_OR_STATE")
    original_logic=a.get("evaluate")
    c_logic=source_boolean_tree_to_c(original_logic,source_to_alias,
        inventory_error="MULTI_DISTINCT_SOURCE_TEST_COVERAGE_DRIFT")
    c={"id":a["id"],"checks":checks,
       "require":c_logic}
    if observations:
        c["observations"]=observations
    try:
        compiled=compile_c_unified(c)
    except (ValueError,TypeError,KeyError) as exc:
        reject("MULTI_DISTINCT_UNIFIED_COMPILER_REJECTED: "+str(exc))
    verify_compiled_source_boolean_tree(compiled,original_logic,source_to_alias)
    source_state_crosswalk={
        alias:check["source_state"] for alias,check in checks.items()
        if "source_state" in check}
    if compiled.get("source_state_provenance")!=source_state_crosswalk:
        reject("MULTI_DISTINCT_REUSED_SOURCE_STATE_IDENTITY_DRIFT")
    if (set(compiled["tests"])!=set(checks) or
        set(compiled.get("shared_objects",{}))!=set(reused) or
        compiled.get("shared_singletons")):
        reject("MULTI_DISTINCT_COMPILER_CONFLATED_SOURCE_OBJECTS")
    for tid,alias in source_to_alias.items():
        out=deepcopy(compiled["tests"][alias])
        oid=tests[tid]["object"]
        if oid in reused:
            if out.get("object")!=oid:
                reject("MULTI_DISTINCT_REUSED_OBJECT_REFERENCE_DRIFT")
            out["object"]=deepcopy(compiled["shared_objects"][oid])
        elif not isinstance(out.get("object"),dict):
            reject("MULTI_DISTINCT_UNSHARED_OBJECT_REFERENCE_DRIFT")
        obj,original_entities=comparisons[tid]
        _same_source_semantics(tests[tid],out,obj,original_entities)
    return {
        "stage":"NATIVE_C_DISTINCT_MULTI_SOURCE_COMPATIBILITY_PROVED",
        "source_assessment_id":a["id"],
        "authored_c":c,
        "source_test_crosswalk":{alias:tid for tid,alias in source_to_alias.items()},
        "source_state_crosswalk":source_state_crosswalk,
        "source_test_documentation":{
            alias:tests[tid]["test_title"]
            for tid,alias in source_to_alias.items()},
        "native_c_compiled_tests":deepcopy(compiled["tests"]),
        "C_uses_independent_selected_objects":not bool(reused),
        "C_preserves_mixed_original_object_reuse":bool(reused),
        "A_source_semantic_projection_passed":True,
        "OVAL_actual_scanner_parity_proven":False,
    }
