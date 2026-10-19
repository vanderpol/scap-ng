#!/usr/bin/env python3
"""Refs #245: ONE observational authoring surface for C derived values.

Bridge a user-authored inline or named *observation* and read_field into the
existing source-independent C derived-value -> A compiler. Object is ONLY the
A/OVAL-compatible internal IR name. No source OVAL evaluation or scanner parity
is asserted. Named observation references retain their original source Object
identity and may not be silently deduplicated.
"""
from __future__ import annotations
from copy import deepcopy
import re

from research_c_derived_values_compiler import compile_c_derived_values
from research_c_shared_engine import present_c_variable_steps

ID=re.compile(r"[a-z][a-z0-9_-]{0,127}\Z")
MAX=512
COLLECTOR_FIELDS=frozenset(("capability","collect","select","object_title",
                             "filesystem","traversal"))

def _id(value):
    if type(value) is not str or not ID.fullmatch(value):
        raise ValueError("meaningful lowercase observation identity required")
    return value

def _source_object_to_observation(obj):
    if not isinstance(obj,dict) or not set(obj)<=COLLECTOR_FIELDS:
        raise ValueError("unsupported source Object shape; retain typed compatibility IR")
    cap=obj.get("capability")
    if type(cap) is not str or not cap or (("collect" in obj)==("select" in obj)):
        raise ValueError("one explicit source collection or selector required")
    args={key:deepcopy(value) for key,value in obj.items()
          if key not in ("capability","object_title")}
    spec={"from":{cap:args}}
    if "object_title" in obj:
        spec["description"]=obj["object_title"]
    return spec

def _observation_to_source_object(spec):
    if not isinstance(spec,dict) or set(spec) not in (
        {"from"},{"from","description"}):
        raise ValueError("observation needs from and optional description")
    frm=spec["from"]
    if not isinstance(frm,dict) or len(frm)!=1:
        raise ValueError("from needs exactly one acquisition capability")
    cap,args=next(iter(frm.items()))
    if type(cap) is not str or not cap or not isinstance(args,dict):
        raise ValueError("invalid typed observation capability/selector")
    if not set(args)<=COLLECTOR_FIELDS-{"capability","object_title"} or (
        ("collect" in args)==("select" in args)):
        raise ValueError("observation must preserve one typed collection route")
    if not isinstance(args.get("collect",args.get("select")),dict):
        raise ValueError("observation collection parameters must be explicit")
    raw={"capability":cap,**deepcopy(args)}
    if "description" in spec:
        desc=spec["description"]
        if type(desc) is not str or not desc.strip():
            raise ValueError("observation description must be meaningful")
        raw["object_title"]=desc
    return raw

def _convert_expression(node, named, used, depth=0):
    if depth>64:
        raise ValueError("nested observation expression exceeds limit")
    if isinstance(node,list):
        return [_convert_expression(x,named,used,depth+1) for x in node]
    if not isinstance(node,dict):
        return deepcopy(node)
    if set(node)=={"read_field"}:
        field=node["read_field"]
        if not isinstance(field,dict) or set(field)!={"field","observation"}:
            raise ValueError("read_field must name one observation and field")
        which=field["observation"]
        if type(which) is str:
            if which not in named:
                raise ValueError("unresolved named observation")
            used.add(which)
            obj=named[which][0]
        elif isinstance(which,dict):
            if "source_object" in which:
                raise ValueError("private observation cannot claim named shared identity")
            obj=_observation_to_source_object(which)
        else:
            raise ValueError("observation must be one alias or one private descriptor")
        return {"read_field":{"field":field["field"],"object":deepcopy(obj)}}
    # Reject ambiguous or legacy internal Object spelling, even when nested.
    if set(node) in ({"object"},{"variable"},{"values"}):
        raise ValueError("source-only Object/Variable vocabulary is not C authoring")
    return {key:_convert_expression(value,named,used,depth+1)
            for key,value in node.items()}

def compile_c_observation_values(authored):
    """Compile without reading any source Assessment or original A Variables."""
    if not isinstance(authored,dict) or set(authored) not in (
        {"assessment_id","observations","steps"},
        {"assessment_id","observations","steps","expected_source_variables_sha256"}):
        raise ValueError("one C observation/value authoring form required")
    entries=authored["observations"]
    steps=authored["steps"]
    if not isinstance(entries,dict) or len(entries)>MAX or (
        not isinstance(steps,list) or not 1<=len(steps)<=MAX):
        raise ValueError("bounded named observations and derived value steps required")
    named={}; shared={}; ids=set()
    for alias,entry in entries.items():
        _id(alias)
        if not isinstance(entry,dict) or set(entry) not in (
            {"source_object","from"},{"source_object","from","description"}):
            raise ValueError("named observation requires source Object provenance and from")
        source=_id(entry["source_object"])
        if source in ids:
            raise ValueError("two named observations claim one source Object identity")
        ids.add(source)
        obj=_observation_to_source_object({
            key:deepcopy(val) for key,val in entry.items()
            if key!="source_object"})
        named[alias]=(source,obj)
        shared[source]=obj
    # Crucially, named references lower to existing named source IDs rather
    # than accidentally recollecting a similar but distinct private Object.
    used=set()
    translated=deepcopy(authored)
    translated["shared_objects"]=shared
    translated.pop("observations")
    translated["steps"]=[]
    for step in steps:
        if not isinstance(step,dict):
            raise ValueError("derived value step required")
        change=deepcopy(step)
        change["derive"]=_convert_expression(step.get("derive"),named,used)
        translated["steps"].append(change)
    if used!=set(named):
        raise ValueError("unused observation cannot silently disappear")
    result=compile_c_derived_values(translated)
    if result["shared_objects"]!=shared:
        raise ValueError("named observation graph unexpectedly changed")
    result["stage"]="C_RESEARCH_OBSERVATIONS_TO_A_SOURCE_GRAPH_NO_SCANNER"
    result["observation_source_ids"]={
        alias:source for alias,(source,_) in named.items()}
    result["authored_private_observation_count"]=sum(
        1 for step in steps for _ in _private_observations(step.get("derive")))
    result["authored_named_observation_count"]=len(named)
    return result

def _private_observations(node):
    if isinstance(node,dict):
        if set(node)=={"read_field"} and isinstance(node["read_field"],dict):
            value=node["read_field"].get("observation")
            if isinstance(value,dict):
                yield value
        for x in node.values():
            yield from _private_observations(x)
    elif isinstance(node,list):
        for x in node:
            yield from _private_observations(x)

def present_c_observation_values(source):
    """Source-backed initial view; output is editable but still non-normative."""
    shared=source.get("shared_objects",{})
    if not isinstance(shared,dict):
        raise ValueError("source shared Objects require mapping")
    view=present_c_variable_steps(source)
    # Keep an exact source-identity mapping, not a guessed alias.
    names={}
    observations={}
    for obj_id,obj in sorted(shared.items()):
        _id(obj_id)
        alias=obj_id
        if alias in observations:
            raise ValueError("ambiguous source Object identity")
        names[obj_id]=alias
        observations[alias]={"source_object":obj_id,
                            **_source_object_to_observation(obj)}
    def converted(node):
        if isinstance(node,dict):
            if set(node)=={"read_field"}:
                data=node["read_field"]
                if not isinstance(data,dict) or set(data)!={"field","object"}:
                    raise ValueError("unsupported source field extraction")
                obj=data["object"]
                if type(obj) is str:
                    if obj not in names:
                        raise ValueError("unresolved source shared observation")
                    val=names[obj]
                elif isinstance(obj,dict):
                    val=_source_object_to_observation(obj)
                else:
                    raise ValueError("invalid source Object")
                return {"read_field":{"field":data["field"],"observation":val}}
            return {key:converted(value) for key,value in node.items()}
        if isinstance(node,list):
            return [converted(x) for x in node]
        return deepcopy(node)
    return {"assessment_id":source["id"],"observations":observations,
            "steps":[{**deepcopy(step),"derive":converted(step["derive"])}
                     for step in view["steps"]],
            "expected_source_variables_sha256":view["source_variables_sha256"]}
