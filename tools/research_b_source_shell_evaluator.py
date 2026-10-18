#!/usr/bin/env python3
"""#237: source shellcommand State over repeated typed stdout_line entities.

Fixture engine only; does not execute commands and does not prove original
OVAL shellcommand Item/State or shell exit/error semantics.
"""
from __future__ import annotations
from oval_result_truth_tables import (
    TRUE,FALSE,ERROR,UNKNOWN,
    aggregate_check,evaluate_collected_object_test,
)


def evaluate_source_shell(ast,fixtures):
    provider="independent.shellcommand"
    evidence=fixtures.get(provider)
    if evidence is None:
        return UNKNOWN,"command result not supplied",0
    if not isinstance(evidence,dict) or evidence.get("using")!=ast["using"]:
        return ERROR,"shell command acquisition identity mismatch",0
    flag=evidence.get("status")
    if not isinstance(flag,str) or flag not in {
        "complete","incomplete","error","not collected","not applicable"
    } or not isinstance(evidence.get("items"),list):
        return ERROR,"invalid shell collection envelope",0
    items=evidence["items"]
    if flag not in {"complete","incomplete"} and items:
        return ERROR,"unverifiable command Items on terminal status",len(items)
    statuses=[];ids=set()
    for item in items:
        if not isinstance(item,dict) or not isinstance(item.get("fields"),dict):
            return ERROR,"malformed command evidence Item",len(items)
        name=item.get("id")
        if not isinstance(name,str) or not name or name in ids:
            return ERROR,"missing or duplicate command Item identity",len(items)
        ids.add(name)
        fields=item["fields"]
        stdout=fields.get("stdout_line")
        stderr=fields.get("stderr_line")
        exitcode=fields.get("exit_status")
        if (not isinstance(stdout,list) or not isinstance(stderr,list) or
            type(exitcode) is not int or
            any(type(v) is not str for v in stdout+stderr)):
            statuses.append(ERROR)
            continue
        if ast["using"]["error_if_exit_status_not_0"] and exitcode!=0:
            statuses.append(ERROR)
            continue
        if ast["using"]["error_if_stderr_exists"] and stderr:
            statuses.append(ERROR)
            continue
        # A repeated stdout_line entity is ONE Item's multivalued field.
        # Preserve its cardinality; don't turn each line into an Object Item.
        if not stdout:
            statuses.append(FALSE)
        else:
            matches=[TRUE if line==ast["state"]["expected"] else FALSE for line in stdout]
            statuses.append(aggregate_check(ast["state"]["entity_check"],matches))
    result=evaluate_collected_object_test(
        flag=flag,existence=ast["existence"],check=ast["check"],
        has_state=True,exists=len(items),item_results=statuses)
    return result,"offline source shell stdout entity check; XML parity unverified",len(items)
