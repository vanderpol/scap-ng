#!/usr/bin/env python3
"""Refs #245: reversible C requirement authoring over existing typed OVAL IR.

Research-only hybrid: Sets/Filters/Variables/collections remain exactly in
the tested v003/0.4-A graph, while Test existence, matching and criteria
become readable C must/and/or. This does NOT create a second runtime or prove
scanner parity. Every Test is accounted for, unknown shapes reject.
"""
from __future__ import annotations
from collections import Counter
from copy import deepcopy
import hashlib
import json
import re

STAGE="C_HYBRID_MUST_OVER_OVAL_TYPED_DATAFLOW_RESEARCH"
NATIVE={"assessment_title","class","evaluate","id","mode","objects",
        "purpose","specification","states","tests","variables","version"}
EXISTS={"at_least_one_exists":"one_or_more","only_one_exists":"exactly_one",
        "none_exist":"none","all_exist":"all"}
MATCH={"all":"every","at least one":"some","only one":"one","none satisfy":"none"}
ALIAS=re.compile(r"^[a-z][a-z0-9_]{0,89}$")

def reject(message):
    raise ValueError("C hybrid source contract: "+message)

def _pin(source):
    raw=json.dumps(source,sort_keys=True,separators=(",",":"),ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def _alias(t):
    title=t.get("test_title")
    if type(title) is not str or not title.strip():
        reject("original Test documentation missing")
    s=title.lower()
    for token,name in [
        ("three levels","three_level_sets"),
        ("two levels","two_level_sets"),
        ("one level","one_level_sets"),
        ("filter element","exclude_filter"),
        ("intersection","intersection"),
        ("complement","complement"),
        ("union","union"),
    ]:
        if token in s:return name
    name=re.sub("[^a-z0-9_]+","_",s).strip("_")
    if not ALIAS.fullmatch(name):
        reject("Test title needs a meaningful, unambiguous alias")
    return name

def _tree(node,keys,forward=True,depth=0):
    if depth>64 or not isinstance(node,dict) or len(node)!=1:
        reject("unsupported or recursive criteria")
    op,val=next(iter(node.items()))
    if op==("test" if forward else "check"):
        if val not in keys:reject("unresolved Test in criteria")
        return {("check" if forward else "test"):keys[val]}
    opmap=({"all":"and","any":"or"} if forward else
           {"and":"all","or":"any"})
    if op not in opmap or not isinstance(val,list) or not val:
        reject("only explicit AND/OR criteria supported")
    return {opmap[op]:[_tree(x,keys,forward,depth+1) for x in val]}

def _refs(node):
    if "test" in node:yield node["test"]
    else:
        for group in node.values():
            for part in group:yield from _refs(part)

def present_hybrid_must(source):
    if (not isinstance(source,dict) or set(source)!=NATIVE or
        source["mode"]!="automated" or not isinstance(source["tests"],dict)
        or not 1<=len(source["tests"])<=128):
        reject("bounded native automated A Assessment required")
    checks={};reverse={}
    for test_id,t in sorted(source["tests"].items()):
        if not isinstance(t,dict) or set(t)-{
            "capability","check","check_existence","object","reported_elements",
            "states","test_title"}:
            reject("unknown original Test fields")
        if not {"capability","check","check_existence","object",
                "reported_elements","test_title"}<=set(t):
            reject("missing original Test fields")
        if t["reported_elements"]!="all":reject("unproven reporting semantics")
        exist=EXISTS.get(t["check_existence"])
        match=MATCH.get(t["check"])
        if exist is None or match is None:reject("unproven Test quantifier")
        refs=t.get("states",[])
        if not isinstance(refs,list) or len(refs)!=len(set(refs)):
            reject("duplicate or non-list source State refs")
        alias=_alias(t)
        if alias in checks:reject("colliding source Test display aliases")
        must={"items_exist":exist,"items_match":match}
        if refs:must["states"]=deepcopy(refs)
        checks[alias]={"source_id":test_id,"description":t["test_title"],
                       "observation":t["object"],"capability":t["capability"],
                       "must":must}
        reverse[test_id]=alias
    requirement=_tree(source["evaluate"],reverse)
    compat={k:deepcopy(v) for k,v in source.items() if k not in ("tests","evaluate")}
    doc={"stage":STAGE,"compatibility":compat,"checks":checks,
         "require":requirement,"source_ir_sha256":_pin(source)}
    if Counter(_refs(_tree(requirement,
        {k:v["source_id"] for k,v in checks.items()},False)))!=Counter(source["tests"].keys()):
        reject("original Tests not all referenced exactly once")
    return doc

def compile_hybrid_must(authored):
    if (not isinstance(authored,dict) or
        set(authored)!={"stage","compatibility","checks","require",
                        "source_ir_sha256"} or authored["stage"]!=STAGE):
        reject("wrong authored hybrid document")
    compat=authored["compatibility"]
    if not isinstance(compat,dict) or set(compat)!=NATIVE-{"tests","evaluate"}:
        reject("typed native compatibility graph missing")
    if any(not isinstance(compat[k],dict) for k in ("objects","states","variables")):
        reject("typed source Object/State/Variable graph missing")
    checks=authored["checks"]
    if not isinstance(checks,dict) or not 1<=len(checks)<=128:
        reject("bounded authored check set required")
    tests={};test_ids={}
    xexist={v:k for k,v in EXISTS.items()};xmatch={v:k for k,v in MATCH.items()}
    for alias,check in checks.items():
        if type(alias) is not str or not ALIAS.fullmatch(alias) or (
            not isinstance(check,dict) or
            set(check)!={"source_id","description","observation",
                         "capability","must"}):
            reject("invalid authored check shape")
        must=check["must"]
        if not isinstance(must,dict) or set(must) not in (
            {"items_exist","items_match"},{"items_exist","items_match","states"}):
            reject("explicit must existence and matching required")
        existence=xexist.get(must["items_exist"])
        matching=xmatch.get(must["items_match"])
        if existence is None or matching is None:reject("unsupported matching/existence")
        test_id=check["source_id"];obj_id=check["observation"]
        if (type(test_id) is not str or not test_id or test_id in tests or
            obj_id not in compat["objects"] or
            check["capability"]!=compat["objects"][obj_id].get("capability")):
            reject("duplicate Test identity or missing/mismatched observation")
        title=check["description"]
        if type(title) is not str or not title.strip():
            reject("original Test documentation cannot disappear")
        test={"capability":check["capability"],"check":matching,
              "check_existence":existence,"object":obj_id,
              "reported_elements":"all","test_title":title}
        if "states" in must:
            refs=must["states"]
            if (not isinstance(refs,list) or not refs or
                len(refs)!=len(set(refs)) or
                any(ref not in compat["states"] for ref in refs)):
                reject("duplicate/missing State reference")
            test["states"]=deepcopy(refs)
        tests[test_id]=test;test_ids[alias]=test_id
    evaluate=_tree(authored["require"],test_ids,False)
    if Counter(_refs(evaluate))!=Counter(tests.keys()):
        reject("require must reference each Test exactly once")
    result={**deepcopy(compat),"tests":tests,"evaluate":evaluate}
    if set(result)!=NATIVE:reject("source A contract missing fields")
    return result

def prove_original_hybrid(source,authored):
    compiled=compile_hybrid_must(authored)
    if compiled!=source or authored["source_ir_sha256"]!=_pin(source):
        reject("authored requirement or typed graph differs from pinned original")
    return {"stage":STAGE,"native_A_graph_recreated":True,
            "source_test_count":len(source["tests"]),
            "source_object_count":len(source["objects"]),
            "source_set_count":sum("set" in o for o in source["objects"].values()),
            "source_variable_count":len(source["variables"]),
            "source_state_count":len(source["states"]),
            "OVAL_runtime_parity_proven":False}
