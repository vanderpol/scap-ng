#!/usr/bin/env python3
"""#237: strict lowering of one state-free Linux partition Test (research).

Consumes converted SCAP-NG 0.3 Assessment data, NOT raw SCAP 1.4 XML.
Does not claim OVAL linux.partition collection or mount namespace parity.
"""
from __future__ import annotations


def lower_state_free_partition_assessment(source):
    if not isinstance(source,dict) or set(source)!={"assessment"}:
        raise ValueError("single source Assessment mapping required")
    a=source["assessment"]
    if not isinstance(a,dict) or a.get("mode")!="automated":
        raise ValueError("partition lowering requires automated Assessment")
    tests=a.get("tests")
    if not isinstance(tests,dict) or len(tests)!=1:
        raise ValueError("partition lowering requires exactly one Test")
    test_id,t=next(iter(tests.items()))
    if a.get("evaluate")!={"test":test_id}:
        raise ValueError("partition lowering supports direct single-Test evaluation only")
    if not isinstance(t,dict) or set(t)!={
            "capability","existence","match","object","reported_elements","test_title"}:
        raise ValueError("partition State, Variable or other Test semantics unsupported")
    if (t["capability"],t["existence"],t["match"])!=(
            "linux.partition","one_or_more","all") or t["reported_elements"]!="all":
        raise ValueError("unsupported linux.partition source Test requirements")
    obj=t["object"]
    if not isinstance(obj,dict) or set(obj)!={
            "capability","object_title","select"} or obj["capability"]!="linux.partition":
        raise ValueError("unsupported Linux partition Object/for_each")
    select=obj["select"]
    if not isinstance(select,dict) or set(select)!={"mount_point"}:
        raise ValueError("unsupported partition selection or source Object set")
    cond=select["mount_point"]
    if not isinstance(cond,dict) or set(cond)!={"operation","value"} or cond["operation"]!="equals":
        raise ValueError("mount point requires simple exact equality")
    path=cond["value"]
    if type(path)!=str or not path.startswith("/"):
        raise ValueError("mount point must be a literal absolute path")
    return {"kind":"compat_oval_provider_existence",
            "source_assessment_id":a["id"],
            "source_test_id":test_id,
            "provider":"linux.mounts",
            "using":{},
            "where":{"field":"mount_point","equals":path},
            "existence":"at_least_one_exists"}
