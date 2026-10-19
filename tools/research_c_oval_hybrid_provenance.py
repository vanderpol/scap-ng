#!/usr/bin/env python3
"""Refs #245: external source-provenance for real OVAL 5.12.3 Set C authoring.

Second source family for C author-only vs typed-source metadata separation.
Bounded exactly to original A graph shapes accepted by the existing hybrid
must and inline constant compilers. C names observations, expected values,
checks, must and nested Set references; sidecar keeps original Object/State/
Test/constant-Variable IDs and typed source metadata. Source OVAL sets,
filters and evaluation are NOT reimplemented here.

No scanner parity claim; aliases are presentation names not execution IDs.
"""
from __future__ import annotations
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import json
import re

from research_c_hybrid_inline_expectations import (
    INLINE_STAGE,present_inline_expectations,compile_inline_expectations,
    prove_inline_original)
from research_c_hybrid_must_overlay import reject, NATIVE

STAGE="C_RESEARCH_OVAL_TYPED_SET_AUTHORING_WITH_PROVENANCE_SIDECAR"
PROV_STAGE="C_RESEARCH_OVAL_OBJECT_STATE_TEST_VARIABLE_SOURCE_BINDINGS"

def _digest(node):
    return sha256(json.dumps(node,sort_keys=True,separators=(",",":"),
                     ensure_ascii=False,allow_nan=False).encode()).hexdigest()

def _slug(value):
    if type(value) is not str or not value:
        reject("source identity cannot yield an authored display name")
    name=re.sub(r"[^a-z0-9]+","_",value.lower()).strip("_")
    return name[:64].strip("_") or "source"

def _unique(base,used):
    name=base;counter=2
    while name in used:
        name=base+"_"+str(counter)
        counter+=1
    used.add(name)
    return name

def _aliases(objects,checks,expected):
    # A named Check's purpose is the best available name for its Object.
    # Non-Test leaf Objects receive a path-derived acquisition name.
    owner={}
    used=set()
    for check,definition in checks.items():
        original=definition["observation"]
        if original in owner:continue  # shared evidence has ONE identity
        owner[original]=_unique("observation_"+_slug(check),used)
    for original,obj in objects.items():
        if original in owner:continue
        if not isinstance(obj,dict) or "select" not in obj:
            reject("unnamed nested Set with no source Test requires explicit alias")
        path=obj["select"].get("path",{})
        if not isinstance(path,dict) or type(path.get("value")) is not str:
            reject("nonliteral leaf Object requires author naming study")
        beh=obj.get("behaviors",{})
        suffix=str(beh.get("recurse_direction","none"))
        owner[original]=_unique("files_"+_slug(path["value"]+"_"+suffix),used)
    if set(owner)!=set(objects):
        reject("incomplete source Object aliasing")
    names={}
    used=set()
    for sid,state in expected.items():
        values=state["equals"]
        if type(values) is str:values=[values]
        if not isinstance(values,list) or not values or any(type(x) is not str
                                                           for x in values):
            reject("complex expected values need their own authoring contract")
        # Preserve distinct expectations with bounded meaningful names.
        first=values[0].rsplit("/",1)[-1] or "root"
        last=values[-1].rsplit("/",1)[-1] or "root"
        key="expected_"+_slug(first if len(values)==1 else first+"_or_"+last)
        names[sid]=_unique(key,used)
    return owner,names

def _translate_refs(node,objects,states,*,reverse=False,depth=0):
    if depth>128:reject("nested OVAL Set authoring too deep")
    if isinstance(node,list):
        return [_translate_refs(x,objects,states,reverse=reverse,depth=depth+1)
                for x in node]
    if not isinstance(node,dict):
        return deepcopy(node)
    if len(node)==1:
        k,v=next(iter(node.items()))
        if k in ("object","state"):
            table=objects if k=="object" else states
            if type(v) is not str or v not in table:
                reject("unresolved OVAL Object/Filter State reference")
            return {k:table[v]}
    return {key:_translate_refs(value,objects,states,reverse=reverse,depth=depth+1)
            for key,value in node.items()}

def present_oval_set_provenance(source):
    authored=present_inline_expectations(source)
    compat=authored["compatibility"]
    obj_ids,state_ids=_aliases(
        compat["objects"],authored["checks"],authored["expected_values"])
    descriptions={name:deepcopy(obj) for name,obj in compat["objects"].items()}
    named_observations={
        obj_ids[name]:_translate_refs(obj,obj_ids,state_ids)
        for name,obj in descriptions.items()
    }
    named_expected={}
    constants={}
    for source_id,entry in authored["expected_values"].items():
        label=state_ids[source_id]
        readable={k:deepcopy(v) for k,v in entry.items()
                  if k!="source_constant"}
        named_expected[label]=readable
        if "source_constant" in entry:
            constants[label]=deepcopy(entry["source_constant"])
    checks={}
    for alias,check in authored["checks"].items():
        writable={k:deepcopy(v) for k,v in check.items()
                  if k!="source_id"}
        old_obj=writable["observation"]
        if old_obj not in obj_ids:reject("unresolved source Test Object")
        writable["observation"]=obj_ids[old_obj]
        if "states" in writable["must"]:
            writable["must"]["states"]=[
                state_ids[ref] for ref in writable["must"]["states"]]
        checks[alias]=writable
    result={
        "stage":STAGE,
        "assessment":{"id":compat["id"],"title":compat["assessment_title"]},
        "observations":named_observations,
        "expected_values":named_expected,
        "checks":checks,
        "require":deepcopy(authored["require"]),
    }
    sidecar={
        "stage":PROV_STAGE,
        "original_source_sha256":authored["source_ir_sha256"],
        "original_authored_sha256":_digest(result),
        "native_metadata":{
            k:deepcopy(v) for k,v in compat.items()
            if k not in ("id","assessment_title","objects","states","variables")},
        "object_source_ids":{alias:source_id for source_id,alias in obj_ids.items()},
        "state_source_ids":{alias:source_id for source_id,alias in state_ids.items()},
        "test_source_ids":{name:info["source_id"]
                           for name,info in authored["checks"].items()},
        "constant_sources":constants,
    }
    if (len(sidecar["object_source_ids"])!=len(compat["objects"]) or
        len(sidecar["state_source_ids"])!=len(authored["expected_values"]) or
        len(sidecar["test_source_ids"])!=len(authored["checks"])):
        reject("missing source provenance")
    return result,sidecar

def compile_oval_set_provenance(author,sidecar):
    if (not isinstance(author,dict) or
        set(author)!={"stage","assessment","observations",
                     "expected_values","checks","require"} or
        author["stage"]!=STAGE):
        reject("bounded OVAL source C authoring required")
    if (not isinstance(sidecar,dict) or
        set(sidecar)!={"stage","original_source_sha256",
                       "original_authored_sha256","native_metadata",
                       "object_source_ids","state_source_ids",
                       "test_source_ids","constant_sources"} or
        sidecar["stage"]!=PROV_STAGE):
        reject("separate complete source provenance required")
    obj_map=sidecar["object_source_ids"]
    st_map=sidecar["state_source_ids"]
    tests_map=sidecar["test_source_ids"]
    constants=sidecar["constant_sources"]
    for writable,source_ids,label in (
        (author["observations"],obj_map,"observations"),
        (author["expected_values"],st_map,"expected values"),
        (author["checks"],tests_map,"checks")):
        if (not isinstance(writable,dict) or
            not isinstance(source_ids,dict) or
            set(writable)!=set(source_ids) or
            len(set(source_ids.values()))!=len(source_ids)):
            reject("source identity bindings missing or duplicated: "+label)
    if not isinstance(constants,dict) or not set(constants)<=set(st_map):
        reject("constant provenance source bindings invalid")
    back_objects={alias:source for alias,source in obj_map.items()}
    back_states={alias:source for alias,source in st_map.items()}
    native_objects={}
    for alias,data in author["observations"].items():
        native_objects[back_objects[alias]]=_translate_refs(
            data,back_objects,back_states,reverse=True)
    native_expected={}
    for alias,entry in author["expected_values"].items():
        if not isinstance(entry,dict) or set(entry) not in (
            {"description","field","equals"},
            {"description","field","equals","value_match"}):
            reject("unsupported source expected-value field")
        value=deepcopy(entry)
        if alias in constants:
            metadata=constants[alias]
            if not isinstance(metadata,dict) or set(metadata)!={"id","description"}:
                reject("constant source identity and documentation required")
            value["source_constant"]=deepcopy(metadata)
        native_expected[back_states[alias]]=value
    checks={}
    for alias,entry in author["checks"].items():
        if not isinstance(entry,dict) or set(entry)!={
            "description","observation","capability","must"}:
            reject("source checks need description, acquisition and must")
        if entry["observation"] not in back_objects:
            reject("unbound source observation")
        must=deepcopy(entry["must"])
        if not isinstance(must,dict):
            reject("typed must requirement needed")
        if "states" in must:
            refs=must["states"]
            if not isinstance(refs,list):
                reject("expected State reference list required")
            try:must["states"]=[back_states[x] for x in refs]
            except KeyError:reject("unknown expected State reference")
        checks[alias]={
            "source_id":tests_map[alias],
            "description":entry["description"],
            "observation":back_objects[entry["observation"]],
            "capability":entry["capability"],
            "must":must,
        }
    assessment=author["assessment"]
    if (not isinstance(assessment,dict) or
        set(assessment)!={"id","title"} or
        type(assessment["id"]) is not str or
        type(assessment["title"]) is not str):
        reject("source Assessment metadata missing")
    compat={**deepcopy(sidecar["native_metadata"]),
            "id":assessment["id"],"assessment_title":assessment["title"],
            "objects":native_objects,"states":{},"variables":{}}
    if set(compat)!=NATIVE-{"tests","evaluate"}:
        reject("incomplete typed OVAL execution metadata")
    doc={"stage":INLINE_STAGE,"compatibility":compat,
         "expected_values":native_expected,"checks":checks,
         "require":deepcopy(author["require"]),
         "source_ir_sha256":sidecar["original_source_sha256"]}
    return compile_inline_expectations(doc)

def prove_oval_set_provenance(source,author,sidecar):
    if _digest(author)!=sidecar["original_authored_sha256"]:
        reject("authoring changed; pinned original source not proven")
    compiled=compile_oval_set_provenance(author,sidecar)
    if compiled!=source:
        reject("source-compatible OVAL graph differs from pinned source")
    return {
        "stage":STAGE,"exact_typed_OVAL_graph_reproduced":True,
        "original_Test_count":len(source["tests"]),
        "original_Object_count":len(source["objects"]),
        "original_Set_count":sum("set" in obj for obj in source["objects"].values()),
        "original_State_count":len(source["states"]),
        "original_Variable_count":len(source["variables"]),
        "legacy_source_object_ids_in_authoring":0,
        "legacy_source_state_ids_in_authoring":0,
        "legacy_source_test_ids_in_authoring":0,
        "original_scanner_parity_proven":False,
    }
