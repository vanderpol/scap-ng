#!/usr/bin/env python3
"""Refs #245: fully source-independent C hybrid authoring for Apache SV-214268.

Input is human-facing checks/must/from, named observations and derived_values.
The existing C observation/derived-values compiler constructs all 19 native
OVAL-compatible Variables. This adapter constructs all five Tests and their
Boolean AND expression from authored C, without reading the original A graph.
The A collector, State/Item model and 0.3 dataflow are reused unchanged.
No claim of OVAL scanner execution, six-state parity or normative syntax.
"""
from __future__ import annotations
from collections import Counter
from copy import deepcopy
import hashlib
import json
import re

from research_c_observation_values import (
    compile_c_observation_values, present_c_observation_values)
from v04_a_dataflow_index import index_assessment_dataflow

STAGE="C_RESEARCH_COMPLETE_APACHE_DERIVED_VALUES_AND_MUST_TO_0_3_IR"
ID=re.compile(r"[a-z][a-z0-9_-]{0,127}\Z")
MATCH={"all":"every","one_or_more":"some","only_one":"one",
       "none":"none"}
MATCH_BACK={v:k for k,v in MATCH.items()}
EXIST={"one_or_more":"one_or_more","optional":"optional",
       "none":"none","exactly_one":"exactly_one"}
OP={"pattern_match":"matches_regex","equals":"equals"}
OP_BACK={v:k for k,v in OP.items()}
META={"assessment_title","class","id","mode","purpose","specification","version"}
TOP=META|{"evaluate","shared_objects","tests","variables"}

def _no(message):
    raise ValueError("C Apache hybrid source contract: "+message)

def _hash(node):
    return hashlib.sha256(json.dumps(
        node,sort_keys=True,separators=(",",":"),ensure_ascii=False,
        allow_nan=False).encode("utf-8")).hexdigest()

def _text(value):
    if type(value) is not str or not value.strip():
        _no("required source description missing")
    return value

def _ref_expr(node,lookup,to_c,depth=0):
    """Only change exact variable/use *reference expressions*; not shell text."""
    if depth>64:_no("nested acquisition dependency limit")
    if isinstance(node,list):
        return [_ref_expr(x,lookup,to_c,depth+1) for x in node]
    if not isinstance(node,dict):return deepcopy(node)
    if len(node)==1:
        key,value=next(iter(node.items()))
        src_key="variable" if to_c else "use"
        if key==src_key:
            if type(value) is not str or value not in lookup:
                _no("unresolved derived command/acquisition dependency")
            return {("use" if to_c else "variable"):lookup[value]}
        if key in ("variable","use"):
            _no("ambiguous mixed A/C dependency expression")
    return {k:_ref_expr(v,lookup,to_c,depth+1) for k,v in node.items()}

def _field_to_c(state):
    if not isinstance(state,dict) or set(state)!={
        "existence","field","match","operation","value"}:
        _no("unsupported typed Item State, preserve original A route")
    ex=state["existence"];ma=state["match"];op=state["operation"]
    if ex not in EXIST or ma not in MATCH or op not in OP:
        _no("unproven field existence/matching/operation")
    field=_text(state["field"])
    if type(state["value"]) is not str:
        _no("unsupported field expected data type")
    return {"field":field,"exists":EXIST[ex],"matches":MATCH[ma],
            OP[op]:state["value"]}

def _field_to_a(state):
    if not isinstance(state,dict) or set(state) not in (
        {"field","exists","matches","matches_regex"},
        {"field","exists","matches","equals"}):
        _no("one typed C Item field expectation required")
    if state["exists"] not in EXIST or state["matches"] not in MATCH_BACK:
        _no("ambiguous field existence or match quantifier")
    if type(state["field"]) is not str or not state["field"] or type(
        state.get("matches_regex",state.get("equals"))) is not str:
        _no("field and string predicate required")
    op="matches_regex" if "matches_regex" in state else "equals"
    return {"existence":state["exists"],"field":state["field"],
            "match":MATCH_BACK[state["matches"]],"operation":OP_BACK[op],
            "value":state[op]}

def _alias(source_id):
    if type(source_id) is not str or not source_id.endswith("-test"):
        _no("source Test identity not meaningfully named")
    name=source_id[:-5]
    if not ID.fullmatch(name):_no("source Test alias invalid")
    return name

def _eval_parts(node,reverse):
    if not isinstance(node,dict) or set(node)!={"all"} or not isinstance(
        node["all"],list) or not node["all"]:
        _no("only explicit original top-level AND supported")
    ans=[]
    for child in node["all"]:
        if not isinstance(child,dict) or set(child)!={"test"}:
            _no("nested criteria requires independent syntax proof")
        key=child["test"]
        if key not in reverse:_no("unresolved source Test in criteria")
        ans.append({"check":reverse[key]})
    if len(set(x["check"] for x in ans))!=len(ans):
        _no("duplicate Test in original requirements")
    return {"and":ans}

def present_c_apache_hybrid(source):
    if not isinstance(source,dict) or set(source)!=TOP or source["mode"]!="automated":
        _no("requires exact automated A source with provenance")
    if not isinstance(source["tests"],dict) or not 1<=len(source["tests"])<=128:
        _no("bounded original Apache Tests required")
    values=present_c_observation_values(source)
    id_to_alias={x["source_id"]:x["name"] for x in values["steps"]}
    checks={};reverse={}
    for source_id,raw in sorted(source["tests"].items()):
        if not isinstance(raw,dict) or set(raw) not in (
            {"capability","existence","match","object","reported_elements",
             "states","test_title"},
            {"capability","existence","match","object","reported_elements",
             "states","states_match","test_title"}):
            _no("unreviewed original Test attributes")
        if (raw["capability"]!="independent.shellcommand" or
            raw["reported_elements"]!="all" or
            raw["existence"] not in EXIST or raw["match"] not in MATCH):
            _no("unsupported source Test existence/collection")
        obj=raw["object"]
        if not isinstance(obj,dict) or set(obj)!={
            "capability","collect","object_title"} or (
            obj["capability"]!=raw["capability"]):
            _no("unreviewed private Test observation")
        states=raw["states"]
        if not isinstance(states,list) or not 1<=len(states)<=64:
            _no("unsupported source Item States")
        name=_alias(source_id)
        if name in checks:_no("duplicate check alias")
        must={"items_exist":EXIST[raw["existence"]],
              "items_match":MATCH[raw["match"]],
              "fields":[_field_to_c(s) for s in states]}
        if "states_match" in raw:
            if raw["states_match"]!="all" or len(states)<2:
                _no("unsupported composed State evaluation")
            must["fields_join"]="and"
        checks[name]={
            "source_id":source_id,
            "description":_text(raw["test_title"]),
            "from":{obj["capability"]:{
                "description":_text(obj["object_title"]),
                "collect":_ref_expr(obj["collect"],id_to_alias,True)}},
            "must":must,
        }
        reverse[source_id]=name
    requirement=_eval_parts(source["evaluate"],reverse)
    if Counter(x["check"] for x in requirement["and"])!=Counter(checks):
        _no("missing/duplicated source Test reference")
    return {
        "stage":STAGE,
        "metadata":{k:deepcopy(source[k]) for k in sorted(META)},
        "observations":deepcopy(values["observations"]),
        "derived_values":deepcopy(values["steps"]),
        "expected_source_variables_sha256":values["expected_source_variables_sha256"],
        "expected_source_shared_objects_sha256":values["expected_source_shared_objects_sha256"],
        "checks":checks,"require":requirement,
        "source_assessment_sha256":_hash(source),
    }

def compile_c_apache_hybrid(authored):
    required={"stage","metadata","observations","derived_values",
              "expected_source_variables_sha256",
              "expected_source_shared_objects_sha256","checks","require",
              "source_assessment_sha256"}
    if not isinstance(authored,dict) or set(authored)!=required or authored[
        "stage"]!=STAGE:
        _no("unknown C Apache authoring grammar")
    metadata=authored["metadata"]
    if not isinstance(metadata,dict) or set(metadata)!=META or metadata[
        "mode"]!="automated" or not _text(metadata["id"]):
        _no("original identity and metadata required")
    steps=authored["derived_values"]
    if not isinstance(steps,list) or not 1<=len(steps)<=512:
        _no("bounded derived value graph required")
    sources={x["name"]:x["source_id"] for x in steps
             if isinstance(x,dict) and "name" in x and "source_id" in x}
    if len(sources)!=len(steps):_no("duplicate/invalid derived alias")
    value_input={"assessment_id":metadata["id"],
                 "observations":deepcopy(authored["observations"]),
                 "steps":deepcopy(steps),
                 "expected_source_variables_sha256":
                     authored["expected_source_variables_sha256"],
                 "expected_source_shared_objects_sha256":
                     authored["expected_source_shared_objects_sha256"]}
    compiled=compile_c_observation_values(value_input)
    checks=authored["checks"]
    if not isinstance(checks,dict) or not 1<=len(checks)<=128:
        _no("bounded authored must checks required")
    tests={};aliases={}
    for name,check in checks.items():
        if type(name) is not str or not ID.fullmatch(name) or (
            not isinstance(check,dict) or set(check)!={
                "source_id","description","from","must"}):
            _no("unexpected C check declaration")
        tid=check["source_id"]
        if _alias(tid)!=name or tid in tests:
            _no("original meaningful Test identity/alias mismatch")
        from_value=check["from"]
        if not isinstance(from_value,dict) or set(from_value)!={
            "independent.shellcommand"}:
            _no("typed local test observation required")
        acq=from_value["independent.shellcommand"]
        if not isinstance(acq,dict) or set(acq)!={"description","collect"}:
            _no("unknown collection attributes")
        obj={"capability":"independent.shellcommand",
             "object_title":_text(acq["description"]),
             "collect":_ref_expr(acq["collect"],sources,False)}
        must=check["must"]
        if not isinstance(must,dict) or set(must) not in (
            {"items_exist","items_match","fields"},
            {"items_exist","items_match","fields","fields_join"}):
            _no("explicit cardinality and Item field assertions required")
        if must["items_exist"] not in EXIST or must["items_match"] not in MATCH_BACK:
            _no("unproven Item cardinality")
        fields=must["fields"]
        if not isinstance(fields,list) or not 1<=len(fields)<=64:
            _no("one or more Item states required")
        test={"capability":"independent.shellcommand",
              "existence":must["items_exist"],
              "match":MATCH_BACK[must["items_match"]],
              "object":obj,"reported_elements":"all",
              "states":[_field_to_a(x) for x in fields],
              "test_title":_text(check["description"])}
        if "fields_join" in must:
            if must["fields_join"]!="and" or len(fields)<2:
                _no("unproved composition operator")
            test["states_match"]="all"
        tests[tid]=test;aliases[name]=tid
    require=authored["require"]
    if not isinstance(require,dict) or set(require)!={"and"} or (
        not isinstance(require["and"],list)):
        _no("only explicit source AND test evaluation proved")
    parts=[]
    for x in require["and"]:
        if not isinstance(x,dict) or set(x)!={"check"} or x["check"] not in aliases:
            _no("unknown authored check requirement")
        parts.append({"test":aliases[x["check"]]})
    if Counter(x["test"] for x in parts)!=Counter(tests):
        _no("source Test coverage incomplete or duplicated")
    restored={**deepcopy(metadata),"evaluate":{"all":parts},
              "shared_objects":compiled["shared_objects"],
              "tests":tests,"variables":compiled["variables"]}
    # Validate the SAME native dependency model used by existing converters.
    index_assessment_dataflow(restored)
    return restored

def prove_c_apache_hybrid(original,authored):
    native=compile_c_apache_hybrid(authored)
    if native!=original or authored["source_assessment_sha256"]!=_hash(original):
        _no("full source Test/acquisition/Variable graph differs from pinned original")
    return {
        "stage":STAGE,"exact_full_original_assessment_reconstructed":True,
        "source_test_count":len(native["tests"]),
        "source_variable_count":len(native["variables"]),
        "source_shared_acquisition_count":len(native["shared_objects"]),
        "authored_named_observations":len(authored["observations"]),
        "authored_derived_value_steps":len(authored["derived_values"]),
        "original_scanner_execution_proven":False,
        "six_state_runtime_parity_proven":False,
    }
