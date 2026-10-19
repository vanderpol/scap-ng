#!/usr/bin/env python3
"""Refs #245: source-independent experimental C derived-value -> A Variable compiler.

A derived value may own a private acquisition, but the compiler preserves
every original named Variable and acquisition edge in A's typed source graph.
This is RESEARCH, not a normative new syntax, scanner or OVAL parity.
"""
from __future__ import annotations
from copy import deepcopy
from hashlib import sha256
import json
import re
from v04_a_dataflow_index import index_assessment_dataflow

ID = re.compile(r"[a-z][a-z0-9_-]{0,127}\Z")
OPERATORS = frozenset(("use","constant","read_field","extract","combine","distinct","merge_values"))
MAX_DEPTH = 64
MAX_STEPS = 512

def _hash(obj):
    return sha256(json.dumps(obj,sort_keys=True,ensure_ascii=False,
            separators=(",",":"),allow_nan=False).encode("utf-8")).hexdigest()

def _name(x):
    if type(x) is not str or not ID.fullmatch(x):
        raise ValueError("explicit meaningful lowercase value/source identity required")
    return x

def _restore_refs(node,aliases,depth=0):
    if depth>MAX_DEPTH:
        raise ValueError("deep nested acquisition reference")
    if isinstance(node,dict):
        if set(node)=={"use"}:
            if type(node["use"]) is not str or node["use"] not in aliases:
                raise ValueError("unresolved acquisition dependent value")
            return {"variable":aliases[node["use"]]}
        return {k:_restore_refs(v,aliases,depth+1) for k,v in node.items()}
    if isinstance(node,list):
        return [_restore_refs(x,aliases,depth+1) for x in node]
    return deepcopy(node)

def _inline_value(node,aliases,depth=0):
    if depth>MAX_DEPTH or not isinstance(node,dict) or len(node)!=1:
        raise ValueError("bounded single-operator derived expression required")
    op,arg=next(iter(node.items()))
    if op not in OPERATORS:
        raise ValueError("unsupported C derived value operation: "+str(op))
    if op=="use":
        if type(arg) is not str or arg not in aliases:
            raise ValueError("unknown derived-value reference")
        return {"variable":aliases[arg]}
    if op=="constant":
        if not isinstance(arg,dict) or set(arg)!={"datatype","value"} or (
            arg["datatype"]!="string" or type(arg["value"]) is not str):
            raise ValueError("explicit typed string literal required")
        return {"literal":deepcopy(arg)}
    if op=="read_field":
        if not isinstance(arg,dict) or set(arg)!={"field","object"} or (
            type(arg["field"]) is not str or not arg["field"]):
            raise ValueError("read_field needs field and source Object")
        obj=arg["object"]
        if type(obj) is str:
            _name(obj)
        elif isinstance(obj,dict):
            if type(obj.get("capability")) is not str or not obj["capability"] or (
                ("collect" in obj)==("select" in obj)):
                raise ValueError("private Object must preserve exactly one A acquisition route")
            # Pass the entire exact, typed collection contract through unchanged.
            if not set(obj)<={"capability","collect","select","object_title","filesystem","traversal"}:
                raise ValueError("complex private Object needs explicit compatibility path")
            if not isinstance(obj.get("collect",obj.get("select")),dict):
                raise ValueError("invalid private Object acquisition")
        else:
            raise ValueError("Object source must be named or typed private descriptor")
        return {"values":{"field":arg["field"],
                          "object":_restore_refs(obj,aliases,depth+1)}}
    if op=="extract":
        if not isinstance(arg,dict) or set(arg)!={"pattern","value"} or (
            type(arg["pattern"]) is not str or not arg["pattern"]):
            raise ValueError("regex capture requires explicit pattern and value")
        return {"regex_capture":{"pattern":arg["pattern"],
                "value":_inline_value(arg["value"],aliases,depth+1)}}
    if op=="combine":
        if not isinstance(arg,list) or not 2<=len(arg)<=64:
            raise ValueError("combine requires bounded ordered value list")
        return {"concat":[_inline_value(x,aliases,depth+1) for x in arg]}
    if op=="distinct":
        return {"unique":_inline_value(arg,aliases,depth+1)}
    if op=="merge_values":
        if not isinstance(arg,dict) or set(arg)!={"delimiter","sort","order","values"} or (
            type(arg["delimiter"]) is not str or
            arg["sort"] not in ("document","lexicographic","numeric") or
            arg["order"] not in ("ascending","descending")):
            raise ValueError("merge requires explicit source ordering semantics")
        return {"merge":{"delimiter":arg["delimiter"],"sort":arg["sort"],
                         "order":arg["order"],
                         "values":_inline_value(arg["values"],aliases,depth+1)}}
    raise AssertionError(op)

def compile_c_derived_values(document):
    """Compile authored C steps to A Variables WITHOUT original source Variables.

    A source digest is an optional reconstruction assertion, not runtime proof.
    The graph is checked by A's shared versioned dataflow indexer.
    """
    if not isinstance(document,dict) or set(document) not in (
        {"assessment_id","steps","shared_objects"},
        {"assessment_id","steps","shared_objects","expected_source_variables_sha256"},
    ):
        raise ValueError("one explicit C derived-value authoring shape required")
    assessment_id=document["assessment_id"]
    if type(assessment_id) is not str or not assessment_id:
        raise ValueError("assessment identity required")
    steps=document["steps"]
    shared=document["shared_objects"]
    if not isinstance(steps,list) or not 1<=len(steps)<=MAX_STEPS or (
        not isinstance(shared,dict)):
        raise ValueError("bounded C value steps and shared Objects required")
    aliases={}
    seen=set()
    for step in steps:
        if not isinstance(step,dict) or set(step)!={
            "name","source_id","title","kind","datatype","derive"}:
            raise ValueError("C value step requires source metadata, ID and expression")
        alias=_name(step["name"]); source_id=_name(step["source_id"])
        if alias in aliases or source_id in seen:
            raise ValueError("duplicate C alias or canonical Variable identity")
        aliases[alias]=source_id
        seen.add(source_id)
    variables={}
    for step in steps:
        if (type(step["title"]) is not str or not step["title"].strip() or
            step["kind"]!="local" or step["datatype"]!="string"):
            raise ValueError("description and explicit typed local string required")
        variables[step["source_id"]]={
            "title":step["title"],"kind":step["kind"],"datatype":step["datatype"],
            "expression":_inline_value(step["derive"],aliases)}
    probe={"id":assessment_id,"mode":"automated","shared_objects":deepcopy(shared),
           "variables":variables,"tests":{}}
    graph=index_assessment_dataflow(probe)
    actual=_hash(variables)
    expected=document.get("expected_source_variables_sha256")
    if expected is not None and (type(expected) is not str or expected!=actual):
        raise ValueError("C value lowering does not reproduce pinned source Variable graph")
    return {"stage":"C_RESEARCH_DERIVED_VALUES_TO_A_VARIABLES_NOT_SCANNER",
            "assessment_id":assessment_id,"variables":variables,
            "shared_objects":deepcopy(shared),"variable_aliases":aliases,
            "source_variables_sha256":actual,
            "dependency_first_source_order":graph["dependency_first_source_order"],
            "source_graph_sha256":_hash(graph),
            "original_source_reconstructed_if_pinned":expected is not None,
            "collector_executed":False,"oval_execution_parity_proven":False,
            "native_c_language_accepted":False}
