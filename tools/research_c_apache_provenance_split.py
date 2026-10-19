#!/usr/bin/env python3
"""Refs #245: source-linked provenance sidecar, readable Apache 0.4-C authoring.

The author-edited file contains only named observations, derived operations,
check descriptions, source collections and must requirements. Compiler-owned
legacy A identities, OVAL kind/datatype and digests live in a separate
EXPLICIT sidecar, whose presence and completeness are required. Editing
the authored file may compile to a MODIFIED A graph, but must never be
presented as equivalent to original source without a full source proof.

Research-only 5-Test/19-Variable Apache contract. No new scanner or OVAL
result evaluator. No accepted 0.4-C grammar.
"""
from __future__ import annotations
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path

from research_c_apache_hybrid_authoring import (
    STAGE as FULL_STAGE,compile_c_apache_hybrid,
    present_c_apache_hybrid,prove_c_apache_hybrid)
from research_c_apache_hybrid_authoring import META

STAGE="C_RESEARCH_APACHE_AUTHORING_WITH_REQUIRED_PROVENANCE_SIDECAR"
PROVENANCE="C_RESEARCH_SOURCE_ID_TYPE_BINDINGS_NOT_AUTHORING"
AUTHOR_KEYS={"stage","assessment","observations","derived_values",
             "checks","require"}
PROV_KEYS={"stage","assessment_metadata","original_source_sha256",
           "original_variable_sha256","original_shared_objects_sha256",
           "value_sources","check_sources","observation_sources",
           "original_authoring_sha256"}

def _fail(message):
    raise ValueError("C Apache provenance split: "+message)

def _digest(node):
    return sha256(json.dumps(node,sort_keys=True,ensure_ascii=False,
         separators=(",",":"),allow_nan=False).encode("utf-8")).hexdigest()

def _bound_mapping(mapping,keyset,label):
    if not isinstance(mapping,dict) or set(mapping)!=keyset:
        _fail(label+" identity catalog differs from author aliases")

def _source_projection(full):
    authored={
        "stage":STAGE,
        "assessment":{"id":full["metadata"]["id"],
                      "title":full["metadata"]["assessment_title"]},
        "observations":{
            alias:{k:deepcopy(v) for k,v in observation.items()
                   if k!="source_object"}
            for alias,observation in full["observations"].items()},
        "derived_values":[{"name":step["name"],
                           "description":step["title"],
                           "derive":deepcopy(step["derive"])}
                          for step in full["derived_values"]],
        "checks":{alias:{k:deepcopy(v) for k,v in check.items()
                          if k!="source_id"}
                  for alias,check in full["checks"].items()},
        "require":deepcopy(full["require"]),
    }
    return authored

def present_apache_provenance_split(source):
    full=present_c_apache_hybrid(source)
    authored=_source_projection(full)
    provenance={
        "stage":PROVENANCE,
        "assessment_metadata":{
            k:deepcopy(v) for k,v in full["metadata"].items()
            if k not in ("id","assessment_title")},
        "original_source_sha256":full["source_assessment_sha256"],
        "original_variable_sha256":full["expected_source_variables_sha256"],
        "original_shared_objects_sha256":
            full["expected_source_shared_objects_sha256"],
        "value_sources":{
            step["name"]:{
                "source_id":step["source_id"],
                "kind":step["kind"],
                "datatype":step["datatype"]}
            for step in full["derived_values"]},
        "check_sources":{
            alias:check["source_id"] for alias,check in full["checks"].items()},
        "observation_sources":{
            alias:observation["source_object"]
            for alias,observation in full["observations"].items()},
        "original_authoring_sha256":_digest(authored),
    }
    if len(provenance["value_sources"])!=19 or len(provenance["check_sources"])!=5:
        _fail("original Apache source identity census changed")
    return authored,provenance

def _full_from_parts(author,sidecar):
    if not isinstance(author,dict) or set(author)!=AUTHOR_KEYS or author[
        "stage"]!=STAGE:
        _fail("one bounded authored C YAML document required")
    if not isinstance(sidecar,dict) or set(sidecar)!=PROV_KEYS or sidecar[
        "stage"]!=PROVENANCE:
        _fail("separate complete source provenance document required")
    assessment=author["assessment"]
    if (not isinstance(assessment,dict) or set(assessment)!={"id","title"} or
        type(assessment["id"]) is not str or not assessment["id"] or
        type(assessment["title"]) is not str or not assessment["title"].strip()):
        _fail("authored Assessment id and title required")
    metadata={**deepcopy(sidecar["assessment_metadata"]),
              "id":assessment["id"],"assessment_title":assessment["title"]}
    if set(metadata)!=META:_fail("source Assessment metadata not complete")
    observed=author["observations"]
    _bound_mapping(sidecar["observation_sources"],
                   set(observed) if isinstance(observed,dict) else set(),
                   "named observation")
    if len(observed)!=1:_fail("one original named Apache shared source required")
    observations={}
    for alias,item in observed.items():
        if not isinstance(item,dict) or set(item) not in (
            {"from"},{"from","description"}):
            _fail("observation authoring scope unsupported")
        source_id=sidecar["observation_sources"][alias]
        if type(source_id) is not str or not source_id:
            _fail("source Object identity missing")
        observations[alias]={"source_object":source_id,**deepcopy(item)}
    steps=author["derived_values"]
    if not isinstance(steps,list) or len(steps)!=19:
        _fail("all 19 derived values required by this bounded source graph")
    if any(not isinstance(x,dict) or set(x)!={"name","description","derive"}
           or type(x["name"]) is not str or
           type(x["description"]) is not str or not x["description"].strip()
           for x in steps):
        _fail("one name, description and derive operation per value required")
    aliases=[x["name"] for x in steps]
    if len(set(aliases))!=len(steps):
        _fail("duplicate source-independent C value alias")
    _bound_mapping(sidecar["value_sources"],set(aliases),"derived value")
    result_steps=[]
    identities=[]
    for x in steps:
        origin=sidecar["value_sources"][x["name"]]
        if not isinstance(origin,dict) or set(origin)!={
            "source_id","kind","datatype"}:
            _fail("typed source Variable binding missing")
        if (type(origin["source_id"]) is not str or not origin["source_id"]
            or origin["kind"]!="local" or origin["datatype"]!="string"):
            _fail("unsupported source Variable identity/type")
        identities.append(origin["source_id"])
        result_steps.append({"name":x["name"],
                             "title":x["description"],
                             "source_id":origin["source_id"],
                             "kind":origin["kind"],
                             "datatype":origin["datatype"],
                             "derive":deepcopy(x["derive"])})
    if len(set(identities))!=len(identities):
        _fail("two aliases reference same source Variable")
    checks=author["checks"]
    _bound_mapping(sidecar["check_sources"],
                   set(checks) if isinstance(checks,dict) else set(),
                   "Test")
    if len(checks)!=5:_fail("all five source Tests required by this fixture")
    result_checks={}
    source_test_ids=[]
    for alias,check in checks.items():
        if not isinstance(check,dict) or set(check)!={
            "description","from","must"}:
            _fail("expected authored check description/from/must")
        tid=sidecar["check_sources"][alias]
        if type(tid) is not str or not tid:
            _fail("original source Test identity required")
        source_test_ids.append(tid)
        result_checks[alias]={"source_id":tid,**deepcopy(check)}
    if len(set(source_test_ids))!=len(source_test_ids):
        _fail("two C checks reuse one original Test")
    for key in ("original_source_sha256","original_variable_sha256",
                "original_shared_objects_sha256","original_authoring_sha256"):
        value=sidecar[key]
        if type(value) is not str or len(value)!=64 or any(
            c not in "0123456789abcdef" for c in value):
            _fail("source hash missing/invalid: "+key)
    return {
        "stage":FULL_STAGE,"metadata":metadata,
        "observations":observations,"derived_values":result_steps,
        "expected_source_variables_sha256":sidecar["original_variable_sha256"],
        "expected_source_shared_objects_sha256":
            sidecar["original_shared_objects_sha256"],
        "checks":result_checks,"require":deepcopy(author["require"]),
        "source_assessment_sha256":sidecar["original_source_sha256"],
    }

def compile_apache_split(author,provenance, *, require_original_source=True):
    """Independent lowering using authored C and a mandatory source binding.

    require_original_source=False enables explicit author edits, but makes
    NO equivalence assertion. It does not bypass type/capability/graph checks.
    """
    full=_full_from_parts(author,provenance)
    if require_original_source and _digest(author)!=provenance[
        "original_authoring_sha256"]:
        _fail("authoring changed from original; source equivalence not proven")
    return compile_c_apache_hybrid(
        full,require_original_graph_digest=require_original_source)

def prove_apache_split(original,author,provenance):
    if _digest(author)!=provenance["original_authoring_sha256"]:
        _fail("authoring changed; original source proof invalid")
    full=_full_from_parts(author,provenance)
    report=prove_c_apache_hybrid(original,full)
    return {**report,"stage":STAGE,
            "legacy_source_ids_in_authoring":0,
            "legacy_source_ids_in_provenance":25,
            "legacy_types_kinds_in_authoring":0,
            "legacy_types_kinds_in_provenance":19,
            "original_source_equivalent":True,
            "scanner_runtime_parity_proven":False}
