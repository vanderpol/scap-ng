#!/usr/bin/env python3
"""Refs #245: author-facing grouping of safe Apache value-only steps.

Audit is independent and source-based; only its proven single-consumer,
non-acquisition nodes may be nested as inline_derived_value. All 19 native
Variables remain individually rehydrated before the already-tested hybrid
C -> 0.3 graph compiler. Never inline a value that drives a collector.
This is exploratory *presentation* simplification, not runtime optimization.
"""
from __future__ import annotations
from copy import deepcopy

from research_c_apache_hybrid_authoring import (
    STAGE as BASE,compile_c_apache_hybrid,present_c_apache_hybrid,
    prove_c_apache_hybrid)
from research_c_variable_folding_safety import candidate_single_use_value_steps

STAGE="C_RESEARCH_GROUP_SAFE_SINGLE_USE_DERIVED_VALUES"
INLINE="inline_derived_value"
FIELDS={"name","source_id","title","kind","datatype","derive"}
COLLECTOR_NODES=frozenset(("observation","read_field","from","collect","select"))

def _fail(why):
    raise ValueError("grouped C derived-value source contract: "+why)

def _rewrite_once(node,name,into,collector=False):
    if isinstance(node,list):
        result=[];count=0
        for part in node:
            value,n=_rewrite_once(part,name,into,collector)
            result.append(value);count+=n
        return result,count
    if not isinstance(node,dict):
        return deepcopy(node),0
    if set(node)=={"use"} and node["use"]==name:
        if collector:_fail("cannot group a derived value consumed by acquisition")
        return {INLINE:deepcopy(into)},1
    out={};count=0
    for k,v in node.items():
        val,n=_rewrite_once(v,name,into,collector or k in COLLECTOR_NODES)
        out[k]=val;count+=n
    return out,count

def present_grouped_apache(source):
    original=present_c_apache_hybrid(source)
    audit=candidate_single_use_value_steps(source)
    if audit["named_variable_count"]!=19 or audit[
        "presentation_group_candidates"]!=4:
        _fail("Apache source grouping inventory changed")
    candidates=[v["display_name"] for v in audit["candidates"]
                if v["presentation_grouping_candidate"]]
    nodes={step["name"]:deepcopy(step) for step in original["derived_values"]}
    if len(nodes)!=19:_fail("source Step identities are not unique")
    for name in candidates:
        if name not in nodes:_fail("grouping source no longer present")
        candidate=nodes[name]
        found=0
        for other,step in nodes.items():
            if name==other:continue
            repl,n=_rewrite_once(step["derive"],name,candidate)
            step["derive"]=repl
            found+=n
        if found!=1:
            _fail("groupable source must have exactly one pure value consumer")
        del nodes[name]
    result=deepcopy(original)
    result["stage"]=STAGE
    result["derived_values"]=[nodes[step["name"]] for step in original[
        "derived_values"] if step["name"] in nodes]
    result["grouped_presentation_count"]=4
    result["source_total_derived_value_count"]=19
    return result

def _expand(node,acc,collector=False,depth=0):
    if depth>64:_fail("nested grouping too deep")
    if isinstance(node,list):
        return [_expand(v,acc,collector,depth+1) for v in node]
    if not isinstance(node,dict):return deepcopy(node)
    if set(node)=={INLINE}:
        if collector:_fail("inline value embedded inside dynamic acquisition")
        step=node[INLINE]
        if not isinstance(step,dict) or set(step)!=FIELDS:
            _fail("inline source step metadata incomplete")
        name=step["name"]
        if type(name) is not str or name in acc:
            _fail("duplicate hidden value name")
        # Each nested C step becomes the exact original native Variable.
        value=deepcopy(step)
        value["derive"]=_expand(step["derive"],acc,False,depth+1)
        acc[name]=value
        return {"use":name}
    if INLINE in node:_fail("ambiguous inline source declaration")
    return {k:_expand(v,acc,collector or k in COLLECTOR_NODES,depth+1)
            for k,v in node.items()}

def compile_grouped_apache(authoring):
    if (not isinstance(authoring,dict) or authoring.get("stage")!=STAGE or
        set(authoring)!={"stage","metadata","observations","derived_values",
             "expected_source_variables_sha256",
             "expected_source_shared_objects_sha256","checks","require",
             "source_assessment_sha256",
             "grouped_presentation_count","source_total_derived_value_count"}):
        _fail("unknown/ambiguous grouped source shape")
    if authoring["grouped_presentation_count"]!=4 or authoring[
        "source_total_derived_value_count"]!=19:
        _fail("unexpected source grouping inventory")
    steps=authoring["derived_values"]
    if not isinstance(steps,list) or len(steps)!=15:
        _fail("expected fifteen visible values; no silent disappearance")
    assembled={}
    for step in steps:
        if not isinstance(step,dict) or set(step)!=FIELDS:
            _fail("malformed visible derived step")
        if type(step["name"]) is not str or step["name"] in assembled:
            _fail("duplicate visible derived step")
        assembled[step["name"]]=None
    restored=[]
    for step in steps:
        new_step=deepcopy(step)
        inline={}
        new_step["derive"]=_expand(step["derive"],inline)
        for name,hidden in inline.items():
            if name in assembled or any(x["name"]==name for x in restored):
                _fail("duplicate nested or visible source identity")
            restored.append(hidden)
        restored.append(new_step)
    if len(restored)!=19 or len({x["name"] for x in restored})!=19:
        _fail("not all original values rehydrated exactly once")
    base=deepcopy(authoring)
    base["stage"]=BASE
    base["derived_values"]=restored
    base.pop("grouped_presentation_count")
    base.pop("source_total_derived_value_count")
    return compile_c_apache_hybrid(base)

def prove_grouped_apache(source,grouped):
    original=present_grouped_apache(source)
    # We need the separately authored grouped input to preserve the pinned
    # scope, not merely happen to compile to some source graph.
    if compile_grouped_apache(grouped)!=source:
        _fail("grouped authored source does not reproduce original A Assessment")
    if grouped!=original:
        _fail("grouped authoring changed pinned original DAG/meaning")
    proof=prove_c_apache_hybrid(source,present_c_apache_hybrid(source))
    return {**proof,"stage":STAGE,
            "author_visible_derived_value_steps":15,
            "nested_pure_value_steps":4,
            "native_A_variables_rehydrated":19,
            "scanner_runtime_parity_proven":False}
