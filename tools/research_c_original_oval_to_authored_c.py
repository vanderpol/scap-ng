#!/usr/bin/env python3
"""Refs #245: bounded ORIGINAL OVAL -> independently compiled native C from/must.

Input is the pinned full OVAL v003 *semantic-equal* report + source A review
output. A Test can be claimed converted only if:
  1. the original OVAL Definition already passed semantic v003 roundtrip;
  2. the authoring AST is generated from its exact source A graph;
  3. the established source-independent C compiler accepts the AST;
  4. both source and compiled typed Test meanings are compared exhaustively
     for this declared, narrow subset.
All other OVAL constructs are explicit unsupported rows; never drop semantics.
This is original-OVAL SOURCE/IR parity, NOT independently executed scanner
result parity or approval of normative 0.4-C language.
"""
from __future__ import annotations
from collections import Counter
from copy import deepcopy
import argparse
import json
from pathlib import Path
import re
import yaml

from research_c_require_language import compile_c_requirement

OPS={"equals":"equals","pattern match":"matches_regex"}
PAIR_CHECK={"all":"all_match","at least one":"some_match",
            "only one":"only_one_matches","none satisfy":"none_match"}
PRESENCE={"at_least_one_exists":"present","none_exist":"absent",
          "only_one_exists":"one_item_exists"}
BASIC_TYPES={"string":str,"integer":int,"boolean":bool}
MAX_FIELDS=64

class NotNativeCConvertible(ValueError):
    pass

def reject(reason):
    raise NotNativeCConvertible(reason)

def value_is_type(value,datatype):
    typ=BASIC_TYPES.get(datatype)
    return typ is not None and type(value) is typ

def project_selection(obj):
    if not isinstance(obj,dict) or set(obj)!={"capability","object_title","select"}:
        reject("OBJECT_ADVANCED_OR_UNREVIEWED_METADATA")
    select=obj["select"]
    if not isinstance(select,dict) or not 1<=len(select)<=MAX_FIELDS:
        reject("SELECTOR_EMPTY_OR_COMPLEX")
    out={}
    for field,entity in select.items():
        if not isinstance(entity,dict) or set(entity)!={"datatype","operation","value"}:
            reject("SELECTOR_ENTITY_EXPLICIT_TYPE_OR_NIL_REQUIRED")
        if entity["operation"] not in OPS or not value_is_type(entity["value"],entity["datatype"]):
            reject("SELECTOR_OPERATOR_OR_TYPE_UNSUPPORTED")
        # Explicit field mapping is enforced again by the C/A compiler.
        value=deepcopy(entity["value"])
        op=OPS[entity["operation"]]
        out[field]=value if op=="equals" else {"matches_regex":value}
    return out

def _entities(state):
    if isinstance(state,dict) and set(state)=={"all"}:
        group=state["all"]
        if not isinstance(group,list):
            reject("STATE_COMPLEX_GROUP")
        return group
    return [state]

def project_fields(state):
    entities=_entities(state)
    if not 1<=len(entities)<=MAX_FIELDS:
        reject("STATE_EMPTY_OR_TOO_LARGE")
    out={}
    for entity in entities:
        if not isinstance(entity,dict) or set(entity)!={
            "datatype","entity_check","entity_existence","field","operation","value"}:
            reject("STATE_HAS_UNPROVEN_SOURCE_SEMANTICS")
        if (entity["entity_check"]!="all" or
            entity["entity_existence"]!="at_least_one_exists"):
            reject("STATE_FIELD_CARDINALITY_COMPLEX")
        field=entity["field"]
        if type(field) is not str or not field or field in out:
            reject("STATE_FIELD_REPEATED_OR_MISSING")
        if entity["operation"] not in OPS or not value_is_type(entity["value"],entity["datatype"]):
            reject("STATE_FIELD_SPECIALIZED_COMPARISON")
        value=deepcopy(entity["value"])
        op=OPS[entity["operation"]]
        out[field]=value if op=="equals" else {"matches_regex":value}
    return out

def _same_source_semantics(original,compiled,obj,states):
    if original["capability"]!=compiled["capability"]:
        reject("SOURCE_COMPILER_CAPABILITY_DRIFT")
    if (not isinstance(compiled.get("object"),dict) or
        compiled["object"].get("capability")!=obj["capability"]):
        reject("SOURCE_COMPILER_ACQUISITION_DRIFT")
    original_select=obj["select"]
    emitted_select=compiled["object"].get("select")
    if not isinstance(emitted_select,dict) or set(emitted_select)!=set(original_select):
        reject("SOURCE_COMPILER_SELECTOR_DRIFT")
    for field,ent in original_select.items():
        expected={"equals":ent["value"]} if ent["operation"]=="equals" else {
            "matches_regex":ent["value"]}
        if emitted_select[field]!=expected:
            reject("SOURCE_COMPILER_SELECTOR_VALUE_DRIFT")
    if not states:
        expected_token=PRESENCE.get(original["check_existence"])
        if expected_token is None:
            reject("SOURCE_PRESENCE_NOT_PROVEN")
        expected_token={"present":"at_least_one_exists",
                        "absent":"none_exist",
                        "one_item_exists":"only_one_exists"}[expected_token]
        if compiled["require"]!=expected_token or "states" in compiled:
            reject("SOURCE_COMPILER_PRESENCE_DRIFT")
        return
    if original["check_existence"]!="at_least_one_exists":
        reject("SOURCE_EXISTENCE_NOT_PROVEN")
    match=PAIR_CHECK.get(original["check"])
    if match is None or compiled["require"]!="at_least_one_exists_and_"+match:
        reject("SOURCE_COMPILER_MATCH_DRIFT")
    native_states=compiled.get("states")
    if not isinstance(native_states,list) or len(native_states)!=len(states):
        reject("SOURCE_COMPILER_STATE_COUNT_DRIFT")
    if len(states)>1 and compiled.get("states_match")!="all":
        reject("SOURCE_COMPILER_STATE_COMPOSITION_DRIFT")
    for actual,original_entity in zip(native_states,states):
        field=original_entity["field"]
        comparison=actual.get(field) if isinstance(actual,dict) else None
        operation=OPS[original_entity["operation"]]
        if comparison!={"require":"at_least_one_exists_and_all_match",
                       operation:original_entity["value"]}:
            reject("SOURCE_COMPILER_STATE_VALUE_DRIFT")

def compile_one_original_definition(original_assessment):
    """Independently compile ONE OVAL-imported Definition to original C grammar.

    Not a blanket translator; fail-closed on complex Set/Filter/Variable/etc.
    """
    a=original_assessment
    if not isinstance(a,dict) or a.get("mode")!="automated":
        reject("ASSESSMENT_NOT_AUTOMATED")
    if a.get("variables"):
        reject("VARIABLE_SOURCE_GRAPH_NEEDS_COMPATIBILITY")
    tests=a.get("tests") or {}
    if not isinstance(tests,dict) or len(tests)!=1:
        reject("MULTI_TEST_REQUIREMENT_TREE_PENDING")
    tid,old=next(iter(tests.items()))
    if a.get("evaluate")!={"test":tid}:
        reject("DEFINITION_LOGIC_NOT_SIMPLE")
    if not isinstance(old,dict) or set(old)-{
        "capability","check","check_existence","object","reported_elements",
        "states","test_title"}:
        reject("TEST_UNREVIEWED_SOURCE_ATTRIBUTES")
    if old.get("reported_elements")!="all":
        reject("SOURCE_REPORTING_MISMATCH")
    if (type(old.get("test_title")) is not str or not old["test_title"].strip()):
        reject("SOURCE_TEST_DESCRIPTION_MISSING")
    objects=a.get("objects") or {}
    if type(old.get("object")) is not str or set(objects)!={old["object"]}:
        reject("OBJECTLESS_OR_SHARED_SOURCE_SCOPE")
    obj=objects[old["object"]]
    if not isinstance(obj,dict) or obj.get("capability")!=old.get("capability"):
        reject("OBJECT_CAPABILITY_MISMATCH")
    selectors=project_selection(obj)
    states=a.get("states") or {}
    refs=old.get("states",[])
    if not isinstance(refs,list) or len(refs)>1 or set(states)!=set(refs):
        reject("STATE_SHARED_OR_MULTIPLE")
    if refs:
        state=states[refs[0]]
        if (not isinstance(state,dict) or
            set(state)!={"capability","state","state_title"} or
            state["capability"]!=old["capability"]):
            reject("STATE_CAPABILITY_OR_UNREVIEWED_FIELDS")
        entities=_entities(state["state"])
        fields=project_fields(state["state"])
        if old.get("check_existence")!="at_least_one_exists":
            reject("TEST_ADVANCED_EXISTENCE")
        token=PAIR_CHECK.get(old.get("check"))
        if token is None:
            reject("TEST_UNKNOWN_MATCHING")
        # This is the established single C from/must grammar, not a new one.
        must={("every_item" if token=="all_match" else
               "any_item" if token=="some_match" else
               "one_matching_item" if token=="only_one_matches" else
               "no_matching_item"):fields}
    else:
        if old.get("check_existence") not in PRESENCE:
            reject("TEST_UNSUPPORTED_PRESENCE")
        entities=[]
        must=PRESENCE[old["check_existence"]]
    c={"from":{old["capability"]:selectors},"must":must}
    try:
        compiled=compile_c_requirement(c)
    except (KeyError,ValueError,TypeError) as exc:
        reject("C_COMPILER_NOT_SUPPORTED: "+str(exc))
    _same_source_semantics(old,compiled["test"],obj,entities)
    return {"stage":"NATIVE_C_FROM_MUST_SOURCE_COMPATIBILITY_PROVED",
            "authored_c":c,
            "source_assessment_id":a["id"],
            "source_test_id":tid,
            "source_test_title":old["test_title"],
            "native_c_compiled_test":compiled["test"],
            "A_source_semantic_projection_passed":True,
            "OVAL_actual_scanner_parity_proven":False}

def batch_convert_review_folder(review,output):
    review=Path(review);output=Path(output)
    output.mkdir(parents=True,exist_ok=True)
    native=[];unsupported=[]
    for path in sorted(review.glob("*.review.json")):
        source=json.loads(path.read_text(encoding="utf-8"))
        if source.get("status")!="C_READ_ONLY_SOURCE_REVIEW_A_COMPATIBILITY_FALLBACK":
            raise ValueError("unverified OVAL source compatibility review")
        if source["C_read_only_view"].get("C_source_independent_compilation_proven") is not False:
            raise ValueError("untrusted source review assertion")
        ident=source["source"]["definition_id"]
        rel=source["source"]["file"]
        try:
            c=compile_one_original_definition(source["A_source_compatibility_fallback"])
        except NotNativeCConvertible as exc:
            if str(exc)!="MULTI_TEST_REQUIREMENT_TREE_PENDING":
                unsupported.append({"definition_id":ident,"file":rel,"reason":str(exc)})
                continue
            # Bounded multi-Test conversion uses the SAME unified C
            # observations/checks/require frontend. It may legally reject
            # a source Definition, but unexpected exceptions are fatal.
            from research_c_oval_multicheck import convert_objectless_many
            try:
                c=convert_objectless_many(source["A_source_compatibility_fallback"])
            except ValueError as multi:
                if multi.__class__.__name__!="NotNativeCConvertible":
                    raise
                unsupported.append({"definition_id":ident,"file":rel,
                                    "reason":"MULTI_TEST: "+str(multi)})
                continue
        src_path=path.stem.replace(".review","")
        file=src_path+".c.research.yaml"
        # Header carries source Test documentation that the tiny standalone C
        # from/must syntax cannot currently embed in its grammar.
        title=(c["source_test_title"] if "source_test_title" in c
               else source["source"].get("definition_title") or
               source["A_source_compatibility_fallback"]["id"]).replace("\n"," ")
        yaml_txt=("# 0.4-C research only. Exact A Test projection, NOT scanner parity.\n"
                  +"# Original source: "+rel+"\n"
                  +"# Test: "+title+"\n"
                  +yaml.safe_dump(c["authored_c"],sort_keys=False,allow_unicode=True))
        (output/file).write_text(yaml_txt,encoding="utf-8")
        native.append({"definition_id":ident,"file":rel,"c_source":file,
                       "C_compilation_stage":c["stage"],
                       "C_source_test_count":len(c.get("source_test_crosswalk",{})) or 1,
                       "native_C_compilation_passed":True,
                       "A_projection_equivalence_checked":True})
    summary={"stage":"SOURCE_BACKED_NATIVE_C_SUBSET_NOT_SCANNER_PARITY",
             "A_compatible_Definitions_seen":len(native)+len(unsupported),
             "native_C_Definitions":len(native),
             "source_compatible_not_yet_native_C":len(unsupported),
             "native_C_converted":native,"unsupported":unsupported}
    (output/"conversion-manifest.json").write_text(
        json.dumps(summary,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return summary

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--a-review",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args(argv)
    r=batch_convert_review_folder(args.a_review,args.output)
    counts=Counter(x["reason"].split(":")[0] for x in r["unsupported"])
    print(json.dumps({"A_compatible_Definitions_seen":r["A_compatible_Definitions_seen"],
          "native_C_Definitions":r["native_C_Definitions"],
          "source_compatible_not_yet_native_C":r["source_compatible_not_yet_native_C"],
          "reason_counts":dict(counts)},indent=2,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
