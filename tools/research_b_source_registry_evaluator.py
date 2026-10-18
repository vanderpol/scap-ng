#!/usr/bin/env python3
"""#237: strictly bounded registry source-Test evaluation over BOTH views.

This is a *view-invariant fixture experiment*, not an OVAL registry semantics
implementation. OVAL may select a default view or behave differently; thus
every produced result remains SOURCE PARITY UNVERIFIED. Disagreement across
the two views is UNKNOWN, never an arbitrary 32/64-bit preference. Errors are
not normalized to an empty registry value.
"""
from __future__ import annotations

from oval_result_truth_tables import (
    TRUE,FALSE,ERROR,UNKNOWN,NOT_APPLICABLE,
    evaluate_collected_object_test,aggregate_operator,
)

PROVIDER="windows.registry_source_views"
VIEWS=("32bit","64bit")
FLAGS={"complete","incomplete","error","not collected","not applicable"}


def evaluate_source_registry(ast, fixtures):
    """Return (result, human reason, observed Item count)."""
    evidence=fixtures.get(PROVIDER)
    if evidence is None:
        return UNKNOWN,"source registry views were not supplied",0
    if not isinstance(evidence,dict) or set(evidence)!={"views"} or (
            not isinstance(evidence["views"],dict)):
        return ERROR,"registry source-view envelope invalid",0
    views=evidence["views"]
    if set(views)!=set(VIEWS):
        return UNKNOWN,"both 32bit and 64bit source views are required until original XML resolved",0
    statuses=[]; observed=0
    for view in VIEWS:
        e=views[view]
        using={**ast["using"],"view":view}
        if not isinstance(e,dict) or e.get("using")!=using:
            return ERROR,"registry source-view acquisition identity mismatch",observed
        status=e.get("status")
        items=e.get("items")
        if not isinstance(status,str) or status not in FLAGS or not isinstance(items,list):
            return ERROR,"invalid registry source-view status or Items",observed
        if status not in {"complete","incomplete"} and items:
            return ERROR,"terminal registry collection has unverified Items",observed
        seen=set(); item_results=[]
        for item in items:
            if not isinstance(item,dict) or not isinstance(item.get("fields"),dict):
                return ERROR,"malformed registry source Item",observed
            key=item.get("id")
            if not isinstance(key,str) or not key or key in seen:
                return ERROR,"duplicate or missing registry Item identity",observed
            seen.add(key)
            fields=item["fields"]
            if fields.get("view")!=view or "value" not in fields:
                return ERROR,"registry source Item view/value mismatch",observed
            value=fields["value"]
            kind=fields.get("value_kind")
            supported=(kind=="REG_SZ" and type(value) is str) or (
                kind in ("REG_DWORD","REG_QWORD") and type(value) is int)
            if not supported:
                item_results.append(ERROR)
                continue

            def compare(field):
                expected=field["expected"]
                if field["field"]=="type":
                    registry_type={
                        "REG_SZ":"string","REG_DWORD":"dword","REG_QWORD":"qword",
                    }.get(kind)
                    if registry_type is None:
                        return ERROR
                    return TRUE if registry_type==expected else FALSE
                if field["field"]!="value":
                    return ERROR
                # Never coerce DWORD 0 to source text "0"; original OVAL
                # datatype behavior is still an open source-parity gate.
                if type(value) is not type(expected):
                    return ERROR
                return TRUE if value==expected else FALSE

            source_state=ast["state"]
            if "all" in source_state:
                # Both source field requirements apply to the SAME Item,
                # not a global pool of collected registry Items.
                parts=[compare(field) for field in source_state["all"]]
                item_results.append(aggregate_operator("AND",parts))
            else:
                item_results.append(compare(source_state))
        observed+=len(items)
        result=evaluate_collected_object_test(
            flag=status,existence=ast["existence"],check=ast["check"],
            has_state=True,exists=len(items),item_results=item_results)
        statuses.append(result)
    if statuses[0]==statuses[1]:
        return statuses[0],"both source registry views agree; OVAL XML view parity still unverified",observed
    if ERROR in statuses:
        return ERROR,"registry view conflict includes unsupported/error observation",observed
    return UNKNOWN,"32bit/64bit registry views produce different source Test results",observed
