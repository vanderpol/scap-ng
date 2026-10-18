#!/usr/bin/env python3
"""#237: source-facing, strict, offline Windows registry Item snapshots.

This is NOT an operating system registry probe or a proof of OVAL 5.12.3
view, Item-status, datatype and collection semantics. In particular a source
registry Object without windows_view cannot be assigned a made-up default.
"""
from __future__ import annotations

PROVIDER="windows.registry_source_views"
VERSION="b-offline-source-registry-v0.1"
VIEWS=("32bit","64bit")
NUMERIC={"REG_DWORD":(2**32)-1,"REG_QWORD":(2**64)-1}
FLAGS={"complete","incomplete","error","not collected","not applicable"}


def normalize(snapshot, *, hive, key, name, view):
    if hive!="HKLM" or not all(isinstance(x,str) and bool(x) for x in (key,name)) or view not in VIEWS:
        raise ValueError("source registry fixture requires HKLM, key, name and explicit view")
    query={"hive":hive,"key":key,"name":name,"view":view}
    def failure(reason):
        return {"provider":PROVIDER,"version":VERSION,"using":query,
                "status":"error","items":[],"diagnostics":[{"reason":reason}]}
    if not isinstance(snapshot,dict) or set(snapshot)!={"query","status","records"}:
        return failure("unrecognized registry snapshot envelope")
    if snapshot["query"]!=query:
        return failure("query identity mismatch")
    status=snapshot["status"]; records=snapshot["records"]
    if not isinstance(status,str) or status not in FLAGS or not isinstance(records,list):
        return failure("invalid registry status or record array")
    if status not in {"complete","incomplete"} and records:
        return failure("terminal registry status cannot include untrusted Items")
    items=[]
    for i,record in enumerate(records):
        if not isinstance(record,dict) or set(record)!={"value_kind","raw_value"}:
            return failure("unrecognized registry Item fields")
        kind=record["value_kind"]; value=record["raw_value"]
        if kind=="REG_SZ" and isinstance(value,str):
            normalized=value
        elif kind in NUMERIC and type(value) is int and 0<=value<=NUMERIC[kind]:
            normalized=value
        else:
            # Never coerce REG_DWORD zero to string "0" or REG_SZ "0" to 0;
            # do not misrepresent unsupported kind as a missing key.
            return failure("unsupported or incorrectly typed registry value")
        items.append({"id":f"registry:{view}:item:{i}",
                      "fields":{"value":normalized,"value_kind":kind,"view":view}})
    return {"provider":PROVIDER,"version":VERSION,"using":query,
            "status":status,"items":items,"diagnostics":[]}
