#!/usr/bin/env python3
"""Verify real OVAL Self-Assertion recursive set/filter documents are modeled faithfully."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("oval_ir",HERE/"oval_semantic_ir.py")
oval_ir=importlib.util.module_from_spec(spec)
spec.loader.exec_module(oval_ir)


def set_map(ir):
    return {
        obj["id"]: next((c for c in obj.get("children",[]) if c.get("kind")=="set"),None)
        for obj in ir.get("objects",[])
        if any(c.get("kind")=="set" for c in obj.get("children",[]))
    }


def max_depth(node):
    if not node or node.get("kind")!="set":
        return 0
    nested=[max_depth(c) for c in node.get("children",[]) if c.get("kind")=="set"]
    return 1+(max(nested) if nested else 0)


def structural(node):
    if node.get("kind")=="set":
        return {
            "kind":"set",
            "operator":node.get("operator"),
            "operator_explicit":node.get("operator_explicit"),
            "children":[structural(x) for x in node.get("children",[])],
        }
    if node.get("kind")=="object_ref":
        return {"kind":"object_ref","object_ref":node.get("object_ref")}
    if node.get("kind")=="filter":
        return {
            "kind":"filter",
            "state_ref":node.get("state_ref"),
            "action":node.get("action"),
            "action_explicit":node.get("action_explicit"),
        }
    return {"kind":node.get("kind")}


def verify(path):
    ir=oval_ir.parse(path)
    assert not ir["unresolved_references"], ir["unresolved_references"]
    sets=set_map(ir)

    filtered=sets["oval:org.mitre.oval.test:obj:373"]
    assert filtered["operator"]=="UNION", filtered
    assert filtered["operator_explicit"] is False, filtered
    filters=[x for x in filtered["children"] if x["kind"]=="filter"]
    assert len(filters)==1, filtered
    assert filters[0]["state_ref"]=="oval:org.mitre.oval.test:ste:746", filters[0]
    assert filters[0]["action"]=="exclude", filters[0]
    assert filters[0]["action_explicit"] is False, filters[0]

    deep=sets["oval:org.mitre.oval.test:obj:75"]
    assert max_depth(deep)>=3, max_depth(deep)
    deep_filters=[]
    stack=[deep]
    while stack:
        node=stack.pop()
        for child in node.get("children",[]):
            if child.get("kind")=="filter":
                deep_filters.append(child)
            elif child.get("kind")=="set":
                stack.append(child)
    assert any(x["state_ref"]=="oval:org.mitre.oval.test:ste:746" for x in deep_filters), deep_filters

    filter_edges=[
        x for x in ir.get("dependency_edges",[])
        if x.get("kind")=="set_filter_state"
    ]
    assert filter_edges, ir.get("dependency_edges",[])
    assert any(x["to"]=="oval:org.mitre.oval.test:ste:746" for x in filter_edges), filter_edges
    return {k:structural(v) for k,v in sorted(sets.items())}


ap=argparse.ArgumentParser()
ap.add_argument("unix_file",type=Path)
ap.add_argument("windows_file",type=Path)
args=ap.parse_args()

unix=verify(args.unix_file)
windows=verify(args.windows_file)
assert unix==windows, "Unix and Windows Self-Assertion set structures diverged"
print(json.dumps({
    "status":"PASS",
    "set_objects":len(unix),
    "filtered_object_default_action":"exclude",
    "deep_set_depth":max_depth(unix["oval:org.mitre.oval.test:obj:75"]),
    "unix_windows_structurally_equivalent":True,
},indent=2,sort_keys=True))
