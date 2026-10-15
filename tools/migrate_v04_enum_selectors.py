#!/usr/bin/env python3
"""Research-only, lossless source migration for OVAL enum-valued Object selectors.

Reviewed OVAL mappings sometimes encode a selector field as a *literal enum
value*, e.g. windows.registry select.hive: local_machine. The 0.4 single
authored grammar instead uses select.hive: {equals: local_machine}.

This function NEVER guesses a comparator: conversion is permitted ONLY for a
scalar value explicitly listed in the capability's reviewed selector_value_enums.
The inverse transformation is structurally exact; typed dynamic/regex or
collection inputs are left unchanged for their respective source rules.
"""
from copy import deepcopy


def migrate(document, supported_mappings):
    out=deepcopy(document)
    changes=[]
    def walk(node,path,cap):
        if isinstance(node,list):
            for i,value in enumerate(node):
                walk(value,path+[i],cap)
            return
        if not isinstance(node,dict):return
        curcap=node.get("capability",cap)
        if not isinstance(curcap,str):curcap=cap
        select=node.get("select")
        if isinstance(select,dict) and curcap in supported_mappings:
            enums=supported_mappings[curcap].get("native",{}).get("selector_value_enums",{})
            for field,allowed in enums.items():
                if field not in select:continue
                val=select[field]
                if isinstance(val,str):
                    if val not in allowed:
                        raise ValueError(
                            f"Non-enumerated selector value {curcap}.{field}={val!r}; "
                            "refuse to infer equality or coerce it"
                        )
                    select[field]={"equals":val}
                    changes.append({"path":path+["select",field],"source_value":val,
                                    "capability":curcap,"field":field})
        for key,val in node.items():
            walk(val,path+[key],curcap)
    walk(out,[],None)
    return out,changes


def restore(document,changes):
    out=deepcopy(document)
    for note in reversed(changes):
        target=out
        for key in note["path"][:-1]:
            target=target[key]
        field=note["path"][-1]
        if target[field]!={"equals":note["source_value"]}:
            raise ValueError(f"Enum migration source proof mismatch at {note['path']}")
        target[field]=note["source_value"]
    return out
