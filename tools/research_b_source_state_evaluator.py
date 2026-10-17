#!/usr/bin/env python3
"""#237: evaluate one source-shaped textfile State against raw typed Items.

The generic Test six-state combiners are imported from pinned OVAL 5.12.3
research. Actual OVAL regex capture, Item flags, source XML semantics and
missing-entity aggregation remain research boundaries.
"""
from __future__ import annotations

from oval_result_truth_tables import (
    TRUE, FALSE, ERROR, UNKNOWN, NOT_APPLICABLE, evaluate_collected_object_test,
    evaluate_state_entity_existence,
)

FLAGS={"complete":"complete","incomplete":"incomplete","error":"error",
       "not collected":"not collected","not applicable":"not applicable"}


def evaluate_source_textfile_state(ast, evidence):
    """Return (test result, reason, observed count, evaluated Item count)."""
    provider=ast["provider"]
    if evidence is None:
        return UNKNOWN,"source State acquisition unavailable",0,0
    if not isinstance(evidence,dict) or evidence.get("using")!=ast["using"]:
        return ERROR,"source State acquisition identity mismatch",0,0
    flag=evidence.get("status")
    if not isinstance(flag,str) or flag not in FLAGS or not isinstance(evidence.get("items"),list):
        return ERROR,"invalid source State collection envelope",0,0
    items=evidence["items"]
    if flag not in {"complete","incomplete"} and items:
        return ERROR,"terminal source State collection has unverified Items",len(items),0
    if flag in {"error","not collected","not applicable"}:
        result=evaluate_collected_object_test(
            flag=FLAGS[flag],existence=ast["existence"],
            check=ast["check"],has_state=True,exists=0)
        return result,"source State collection not complete",0,0

    ids=set()
    item_results=[]
    for item in items:
        if not isinstance(item,dict) or not isinstance(item.get("fields"),dict):
            return ERROR,"source State Item missing typed evidence",len(items),len(item_results)
        ident=item.get("id")
        if not isinstance(ident,str) or not ident or ident in ids:
            return ERROR,"missing or duplicate source State Item identity",len(items),len(item_results)
        ids.add(ident)
        fields=item["fields"]
        if (fields.get("full_path")!=ast["using"]["path"] or
            type(fields.get("instance")) is not int or fields["instance"]<1 or
            not isinstance(fields.get("match_text"),str)):
            return ERROR,"source State selector/Item field mismatch",len(items),len(item_results)
        if "subexpression" not in fields:
            item_results.append(UNKNOWN)
            continue
        value=fields["subexpression"]
        if isinstance(value,dict) and set(value)=={"field_status"}:
            status=value["field_status"]
            if status=="absent":
                item_results.append(evaluate_state_entity_existence(
                    ast["state"]["entity_existence"],exists=0))
            elif status=="unknown":
                item_results.append(UNKNOWN)
            elif status=="error":
                item_results.append(ERROR)
            else:
                return ERROR,"invalid State field flag",len(items),len(item_results)
        elif type(value) is not str:
            item_results.append(ERROR)
        else:
            op=ast["state"]["operation"]
            matches=value==ast["state"]["expected"]
            if op=="not_equals":matches=not matches
            item_results.append(TRUE if matches else FALSE)
    result=evaluate_collected_object_test(
        flag=FLAGS[flag],existence=ast["existence"],check=ast["check"],
        item_results=item_results,has_state=True,exists=len(items))
    return (result,"source Test plus State over observed typed Items; OVAL source parity unverified",
            len(items),len(item_results))
