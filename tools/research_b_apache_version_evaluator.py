#!/usr/bin/env python3
"""#237: read-only Apache source Variable DAG fixture evaluator.

No command execution. Original OVAL regex, Item and version parity unverified.
"""
from __future__ import annotations
import re
import json
from oval_result_truth_tables import (
    TRUE,FALSE,ERROR,UNKNOWN,NOT_APPLICABLE,
    evaluate_collected_object_test,aggregate_check,
)
from research_b_apache_version_graph import _regex

PROVIDER="independent.shellcommand"
FLAGS={"complete","incomplete","error","not collected","not applicable"}
SAFE_EXE=re.compile(r"/(?:[A-Za-z0-9._+-]+/)*(?:httpd|apache2)\Z")
VERSION=re.compile(r"[0-9]+(?:\.[0-9]+){1,3}\Z")


def _acquisition(fixtures,using):
    root=fixtures.get(PROVIDER)
    if root is None:return None
    if not isinstance(root,dict) or set(root)!={"acquisitions"} or (
            not isinstance(root["acquisitions"],list)):
        raise ValueError("source command evidence requires acquisition set")
    seen=set();found=None
    for query in root["acquisitions"]:
        if not isinstance(query,dict) or not isinstance(query.get("using"),dict):
            raise ValueError("malformed command query in acquisition set")
        key=json.dumps(query["using"],sort_keys=True)
        if key in seen:raise ValueError("duplicate command acquisition identity")
        seen.add(key)
        if query["using"]==using:found=query
    return found


def _verified_items(acquisition,using):
    if acquisition is None:return None,None,"required source query not acquired"
    if acquisition.get("using")!=using:return None,None,"query identity was changed"
    flag=acquisition.get("status");items=acquisition.get("items")
    if type(flag) is not str or flag not in FLAGS or not isinstance(items,list):
        return None,None,"invalid source command collection flag/Items"
    if flag not in {"complete","incomplete"} and items:
        return None,None,"terminal collection has untrusted Items"
    names=set()
    for item in items:
        if not isinstance(item,dict) or not isinstance(item.get("fields"),dict):
            return None,None,"source command Item missing typed fields"
        name=item.get("id")
        if type(name) is not str or not name or name in names:
            return None,None,"duplicate or missing command Item identity"
        names.add(name)
        f=item["fields"]
        if set(f)!={"stdout_line","stderr_line","exit_status"} or (
            not isinstance(f["stdout_line"],list) or
            not isinstance(f["stderr_line"],list) or
            type(f["exit_status"]) is not int or
            any(type(x) is not str for x in f["stdout_line"]+f["stderr_line"])):
            return None,None,"command Item missing valid repeated fields"
        if using["error_if_exit_status_not_0"] and f["exit_status"]!=0:
            return "error",[],None
        if using["error_if_stderr_exists"] and f["stderr_line"]:
            return "error",[],None
    return flag,items,None


def _version(value):
    if type(value) is not str or len(value)>96 or not VERSION.fullmatch(value):
        raise ValueError("unrecognized source version lexical shape")
    parts=[int(n) for n in value.split(".")]
    if any(n>2**31-1 for n in parts):
        raise ValueError("Apache version component out of bounded range")
    return tuple(parts+[0]*(4-len(parts)))


def _terminal(flag):
    return {"error":ERROR,"not collected":UNKNOWN,
            "not applicable":NOT_APPLICABLE}.get(flag)


def evaluate_apache_version(ast,fixtures):
    try:
        source=_acquisition(fixtures,ast["discovery_using"])
        flag,items,reason=_verified_items(source,ast["discovery_using"])
    except (ValueError,TypeError) as exc:
        return ERROR,"invalid discovery acquisition: "+str(exc),0
    if reason:
        return (UNKNOWN if source is None else ERROR),reason,0
    if flag not in {"complete","incomplete"}:
        return _terminal(flag),"source process discovery unavailable",0
    if flag=="incomplete":
        return UNKNOWN,"incomplete process discovery cannot resolve executable identity",len(items)
    selector=_regex(ast["discovery_pattern"],"source collection filter")
    capture=_regex(ast["capture_pattern"],"source executable capture")
    paths=set()
    for item in items:
        for line in item["fields"]["stdout_line"]:
            if len(line)>4096:
                return ERROR,"oversized source process stdout line",len(items)
            if not selector.search(line):continue
            match=capture.search(line)
            if match is None or match.group(1) is None:
                return UNKNOWN,"source filter matched but capture did not resolve",len(items)
            path=match.group(1)
            if not SAFE_EXE.fullmatch(path):
                return ERROR,"unsafe or unsupported executable path capture",len(items)
            paths.add(path)
    if not paths:return UNKNOWN,"no executable path derived from collected Items",len(items)
    if len(paths)!=1:
        return UNKNOWN,"multiple executable paths require unimplemented Variable fan-out",len(items)
    command=next(iter(paths))+ast["command_suffix"]
    if len(command)>4096:
        return ERROR,"derived version command exceeds bounded length",len(items)
    using={**ast["version_using"],"command":command}
    try:
        target=_acquisition(fixtures,using)
        version_flag,version_items,reason=_verified_items(target,using)
    except (ValueError,TypeError) as exc:
        return ERROR,"invalid version acquisition: "+str(exc),len(items)
    if reason:
        return (UNKNOWN if target is None else ERROR),reason,len(items)
    if version_flag not in {"complete","incomplete"}:
        return _terminal(version_flag),"version acquisition unavailable",len(items)
    regex=_regex(ast["version_pattern"],"source version capture")
    expected=_version(ast["state"]["expected"])
    results=[]
    for item in version_items:
        values=[]
        for line in item["fields"]["stdout_line"]:
            if len(line)>4096:
                return ERROR,"oversized version stdout line",len(version_items)
            match=regex.search(line)
            if match is not None:
                try:
                    observed=_version(match.group(1))
                except (ValueError,TypeError):
                    return ERROR,"unsupported version lexical value",len(version_items)
                values.append(TRUE if observed>=expected else FALSE)
        results.append(aggregate_check("at least one",values) if values else FALSE)
    verdict=evaluate_collected_object_test(
        flag=version_flag,existence=ast["existence"],check=ast["check"],
        item_results=results,has_state=True,exists=len(version_items))
    return verdict,"variable DAG fixture evaluated; original OVAL parity unverified",len(version_items)
