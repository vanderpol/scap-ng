#!/usr/bin/env python3
"""#245 C Windows Registry same-Item proof, no new Windows collector.

A 0.3-derived source fixture is retained; existing source-compatibility
lowerer/evaluator used verbatim. No claim of 0.4-A-valid source, original OVAL
view parity or new native Registry backend.
"""
from __future__ import annotations
from copy import deepcopy
from research_b_source_registry_lowering import lower_source_registry_assessment
from research_c_shared_engine import FORMAT,fingerprint

def lower_c_registry_exact(c, source):
    if not isinstance(c,dict) or set(c)!={"each","where","registry_view",
                                          "collected_items","on_same_item"}:
        raise ValueError("C registry shape unrecognized")
    if c["each"]!="windows.registry" or (
        c["registry_view"]!="unspecified_requires_xml_parity"
    ):
        raise ValueError("registry view cannot be silently defaulted")
    if not isinstance(source,dict) or set(source)!={"assessment"}:
        raise ValueError("original source Assessment required")
    a=source["assessment"]
    if a.get("mode")!="automated" or len(a.get("tests",{}))!=1:
        raise ValueError("requires one source Test")
    test_id,t=next(iter(a["tests"].items()))
    if t.get("capability")!="windows.registry" or a.get("evaluate")!={"test":test_id}:
        raise ValueError("source Test identity or logic changed")
    obj=t["object"]["select"]
    where=c["where"]
    if not isinstance(where,dict) or set(where)!={"hive","key","name"} or (
        where["hive"]!=obj["hive"] or any(
            obj[k].get("operation")!="equals" or
            where[k]!={"equals":obj[k].get("value")}
            for k in ("key","name")
        )
    ):
        raise ValueError("source Registry selector differs")
    if c["collected_items"]!={"exists":t["existence"],"match":t["match"]}:
        raise ValueError("source Item existence or matching changed")
    source_states=t["states"]
    if (not isinstance(source_states,list) or len(source_states)!=1 or
        not isinstance(source_states[0],dict) or set(source_states[0])!={"all"}):
        raise ValueError("expected compound source Registry State")
    original=source_states[0]["all"]
    desired=c["on_same_item"]
    if not isinstance(desired,dict) or set(desired)!={"all"} or (
        not isinstance(desired["all"],list) or len(desired["all"])!=len(original)
    ):
        raise ValueError("same Item State grouping differs")
    for copy,raw in zip(desired["all"],original):
        key=raw["field"]
        if raw["operation"]!="equals" or (
            not isinstance(copy,dict) or set(copy)!={key}
        ):
            raise ValueError("source comparison field/operator differs")
        assertion=copy[key]
        if not isinstance(assertion,dict) or set(assertion)!={
            "equals","field_exists","field_match"
        } or assertion["field_exists"]!=raw["existence"] or (
            assertion["field_match"]!=raw["match"] or
            type(assertion["equals"]) is not type(raw["value"]) or
            assertion["equals"]!=raw["value"]
        ):
            raise ValueError("typed field comparison/cardinality differs")
    # Uses source-compatibility evaluator already written for the B research
    # only as a *backend*. No second collection implementation.
    lowered=lower_source_registry_assessment(source)
    return {"format":FORMAT,"compatibility_ir":deepcopy(lowered),
            "source_sha256":fingerprint(t),"scanner_executed":False,
            "source_parity_verified":False}
