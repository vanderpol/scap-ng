#!/usr/bin/env python3
"""Refs #245: source-pinned read-only C observation view of RHEL9 SV-257889.

Preserves separate source-variable-selected file populations, eight permission
bits, and two different OVAL existence modes. The full old 0.1.0 source graph
is a COMPATIBILITY sidecar, not a lossless native 0.4-C conversion.
"""
from __future__ import annotations
from copy import deepcopy
from hashlib import sha256
import json

from research_c_permissions_macro import (
    lower_no_more_permissive_than, prove_legacy_source_permission_state_context
)

SOURCE_ASSESSMENT="niwc.rhel_9.SV-257889.automated"
PERMISSIONS_STATE="state-mode-0740-or-less-permissive"
SOURCE_SITES={
    "non_system_users_home_files": {
        "object":"local-initialization-files-non-system-users-object",
        "variable":"home-directories-non-system-users-variable",
        "test":"test-local-initialization-files-non-system-users-have-mode-0740-or",
        "exists":"any_exist",
    },
    "root_home_files": {
        "object":"local-initialization-files-root-user-object",
        "variable":"home-directory-root-user-variable",
        "test":"test-local-initialization-files-root-have-mode-0740-or-less-permissive",
        "exists":"at_least_one_exists",
    },
}

def digest(value):
    return sha256(json.dumps(value,sort_keys=True,separators=(",",":"),
                             ensure_ascii=False).encode()).hexdigest()

def present_source_account_observations(doc):
    a=doc.get("assessment") if isinstance(doc,dict) and "assessment" in doc else doc
    if not isinstance(a,dict) or a.get("id")!=SOURCE_ASSESSMENT or (
        a.get("specification",{}).get("version")!="0.1.0" or
        a.get("mode")!="automated" or
        len(a.get("objects",{}))!=5 or len(a.get("variables",{}))!=2 or
        len(a.get("states",{}))!=5 or len(a.get("tests",{}))!=2
    ):
        raise ValueError("unsupported/non-pinned RHEL source graph")
    original_all=[{"test":params["test"]} for params in SOURCE_SITES.values()]
    if a.get("evaluate")!={"all":original_all}:
        raise ValueError("RHEL source Tests are two independent AND branches")
    macro=lower_no_more_permissive_than({"no_more_permissive_than":"0740"})
    if len(macro["states"])!=8:
        raise ValueError("source permissions expansion differs")
    proof=prove_legacy_source_permission_state_context(
        a,state_id=PERMISSIONS_STATE,permitted="0740")
    if proof["source_conversion_authorized"] or proof["filters_rewritten"]:
        raise ValueError("research macro must never authorize global changes")
    collected={}
    for alias,ids in SOURCE_SITES.items():
        obj=a["objects"].get(ids["object"])
        var=a["variables"].get(ids["variable"])
        test=a["tests"].get(ids["test"])
        if not isinstance(obj,dict) or not isinstance(var,dict) or (
            not isinstance(test,dict) or obj.get("capability")!="unix.file" or
            test.get("capability")!="unix.file" or
            test.get("object")!=ids["object"] or
            test.get("states")!=[PERMISSIONS_STATE] or
            test.get("check")!="all" or
            test.get("check_existence")!=ids["exists"]
        ):
            raise ValueError("source Item existence, Test or Object linkage changed")
        selector=obj.get("select")
        if not isinstance(selector,dict) or set(selector)!={"path","filename"}:
            raise ValueError("unexpected file selection")
        path=selector["path"]
        if path!={"operation":"equals","datatype":"string",
                  "variable_check":"at least one",
                  "value":{"variable":ids["variable"]}}:
            raise ValueError("source Variable multiplicity/selector changed")
        if selector["filename"]!={"operation":"pattern match",
                                  "datatype":"string",
                                  "value":r"^\.[^\s\.]+"}:
            raise ValueError("source original initialization-file regex changed")
        if obj.get("filters")!=[{"action":"exclude","state":"state-unix-file"}] or (
            obj.get("behaviors")!={"max_depth":"1","recurse":"symlinks",
                                   "recurse_direction":"down"}
        ):
            raise ValueError("source file filters/recursion changed")
        expression=var.get("expression")
        if expression!={"values":{"object":(
            "only-non-system-users-uid-999-home-dirs-excluding-root-object"
            if alias=="non_system_users_home_files" else
            "only-root-users-uid-0-home-dirs-excluding-root-directory-object"),
            "field":"home_dir"}}:
            raise ValueError("original global home-directory Variable dependency changed")
        collected[alias]={
            "source_object":ids["object"],
            "source_variable":ids["variable"],
            "source_test":ids["test"],
            "from_capability":"unix.file",
            "source_item_existence":ids["exists"],
            "source_item_match":"all",
            "original_population":deepcopy(obj),
            "original_value_derivation":deepcopy(var),
            "permission_bits":{"no_more_permissive_than":"0740"},
            "global_source_variable_values":True,
            "per_parent_foreach_invented":False,
        }
    return {
        "stage":"C_RESEARCH_RHEL_TWO_POPULATIONS_READ_ONLY",
        "source_assessment":SOURCE_ASSESSMENT,
        "source_sha256":digest(a),
        "observations":collected,
        "require":{"every":[{"check":name} for name in SOURCE_SITES]},
        "source_compatibility_graph":{
            "objects":deepcopy(a["objects"]),
            "variables":deepcopy(a["variables"]),
            "states":deepcopy(a["states"]),
            "tests":deepcopy(a["tests"]),
            "evaluate":deepcopy(a["evaluate"]),
        },
        "source_conversion_authorized":False,
        "scanner_executed":False,
        "local_permissions_macro_guard":proof["status"],
    }

def reconstruct_source_account_observations(view, source):
    a=source.get("assessment") if "assessment" in source else source
    if not isinstance(view,dict) or view!=present_source_account_observations(a):
        raise ValueError("source compatibility graph or C view changed")
    return deepcopy(a)
