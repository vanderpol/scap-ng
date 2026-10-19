#!/usr/bin/env python3
"""#245 Source-checked C fusion for THREE Apache loaded-config Variable ops.

Research against precollected original source Items ONLY. The source 0.3
independent.shellcommand capability, dynamically resolved command Variable,
field selector and source Item identities are UNCHANGED. The C evaluator
fuses regex_capture -> unique -> merge; OVAL regex dialect, unique ordering
and live collector parity remain unverified.
"""
from __future__ import annotations
from copy import deepcopy
from hashlib import sha256
import json
import re

from research_b_source_shell_snapshot import PROVIDER,VERSION

A="all-loaded-configuration-filepaths-variable"
B="merged-list-all-loaded-config-files-variable"
COMMAND="command-gather-httpd-apache2-list-all-loaded-configuration-files-variable"
MAX_VALUE=4096
MAX_VALUES=256

def _hash(value):
    return sha256(json.dumps(value,sort_keys=True,separators=(",",":"),
                            ensure_ascii=False).encode()).hexdigest()

def compile_loaded_files_fusion(assessment,*,pinned_source_sha256):
    variables=assessment.get("variables")
    if not isinstance(variables,dict) or pinned_source_sha256!=_hash(variables):
        raise ValueError("source Variable DAG changed; C optimizer cannot assert equivalence")
    if A not in variables or B not in variables or COMMAND not in variables:
        raise ValueError("required source graph IDs missing")
    first=variables[A]["expression"]
    second=variables[B]["expression"]
    if set(first)!={"unique"} or set(first["unique"])!={"regex_capture"}:
        raise ValueError("source regex capture/unique shape changed")
    extract=first["unique"]["regex_capture"]
    if set(extract)!={"pattern","value"} or set(extract["value"])!={"values"}:
        raise ValueError("source path extraction shape changed")
    val=extract["value"]["values"]
    if set(val)!={"field","object"} or val["field"]!="stdout_line":
        raise ValueError("source item field identity changed")
    obj=val["object"]
    if set(obj)!={"capability","collect","object_title"} or (
        obj["capability"]!=PROVIDER
    ):
        raise ValueError("source provider changed")
    collect=obj["collect"]
    if set(collect)!={"command","shell","pattern","error_if_exit_status_not_0",
                      "error_if_stderr_exists"} or (
        collect["command"]!={"variable":COMMAND} or collect["shell"]!="bash"
    ):
        raise ValueError("dynamic original source command reference must be retained")
    if set(second)!={"merge"}:
        raise ValueError("source merge shape changed")
    merge=second["merge"]
    if set(merge)!={"delimiter","sort","order","values"} or (
        merge["sort"]!="document" or merge["order"]!="ascending"
        or merge["values"]!={"variable":A}
        or type(merge["delimiter"]) is not str
    ):
        raise ValueError("source merge order/delimiter/dependency changed")
    if any(variables[x].get("datatype")!="string" for x in (A,B,COMMAND)):
        raise ValueError("source variable datatype mismatch")
    return {
        "kind":"c-research-apache-extract-distinct-join-fusion",
        "source_assessment_id":assessment["id"],
        "source_variables_sha256":pinned_source_sha256,
        "original_source_ids":[A,B],
        "dynamic_command_source_id":COMMAND,
        "collect":deepcopy(collect),
        "extract_first":extract["pattern"],
        "join_with":merge["delimiter"],
        "scanner_executed":False,
        "original_source_parity_verified":False,
    }


def evaluate_loaded_files_fusion(plan,evidence,*,resolved_command):
    """Execute one C value pipeline over A-provided normalized Item payloads."""
    if plan.get("kind")!="c-research-apache-extract-distinct-join-fusion":
        raise ValueError("unrecognized C source optimization")
    def envelope(status,seq=()):
        return {"status":status,"values":list(seq)}
    def both(status):
        return {"paths":envelope(status),"merged":envelope(status)}
    if not isinstance(resolved_command,dict) or set(resolved_command)!={
        "source_variable","status","values"
    } or resolved_command["source_variable"]!=plan["dynamic_command_source_id"]:
        return both("error")
    if resolved_command["status"]!="values":
        if resolved_command["values"]!=[]:
            return both("error")
        return both(resolved_command["status"] if resolved_command["status"] in (
            "unknown","error","not_applicable","no_values") else "error")
    commands=resolved_command["values"]
    if not isinstance(commands,list) or len(commands)!=1:
        return both("unknown")
    command=commands[0]
    if type(command) is not str or not command or len(command)>MAX_VALUE:
        return both("error")
    got=evidence.get(PROVIDER)
    if got is None:return both("unknown")
    if not isinstance(got,dict) or set(got)!={"acquisitions"} or (
        not isinstance(got["acquisitions"],list)
    ):
        return both("error")
    collect=plan["collect"]
    using={"command":command,"shell":collect["shell"],
           "error_if_exit_status_not_0":collect["error_if_exit_status_not_0"],
           "error_if_stderr_exists":collect["error_if_stderr_exists"]}
    matching=[row for row in got["acquisitions"] if isinstance(row,dict) and
              row.get("using")==using]
    if not matching:return both("unknown")
    if len(matching)!=1:return both("error")
    row=matching[0]
    if row.get("provider")!=PROVIDER or row.get("version")!=VERSION:
        return both("error")
    status=row.get("status")
    if status!="complete":
        return both({"incomplete":"unknown","not collected":"unknown",
                     "not applicable":"not_applicable"}.get(status,"error"))
    try:
        choose=re.compile(collect["pattern"])
        extract=re.compile(plan["extract_first"])
        if extract.groups<1:return both("error")
    except (TypeError,re.error):
        return both("error")
    items=row.get("items")
    if not isinstance(items,list):return both("error")
    seen_ids=set()
    dedup=set()
    paths=[]
    for item in items:
        if not isinstance(item,dict) or set(item)!={"id","fields"} or (
            type(item["id"]) is not str or not item["id"] or item["id"] in seen_ids
        ):
            return both("error")
        seen_ids.add(item["id"])
        fields=item["fields"]
        if not isinstance(fields,dict) or set(fields)!={"stdout_line","stderr_line","exit_status"}:
            return both("error")
        if not isinstance(fields["stdout_line"],list) or (
            any(type(v) is not str for v in fields["stdout_line"])
        ) or not isinstance(fields["stderr_line"],list) or (
            any(type(v) is not str for v in fields["stderr_line"])
        ) or type(fields["exit_status"]) is not int:
            return both("error")
        if collect["error_if_exit_status_not_0"] and fields["exit_status"]!=0:
            return both("error")
        if collect["error_if_stderr_exists"] and fields["stderr_line"]:
            return both("error")
        for line in fields["stdout_line"]:
            if len(line)>MAX_VALUE:return both("error")
            if not choose.search(line):continue
            match=extract.search(line)
            extracted=(match.group(1) if match and match.group(1) is not None
                       else "")
            if len(extracted)>MAX_VALUE:return both("error")
            if extracted not in dedup:
                dedup.add(extracted)
                paths.append(extracted)
            if len(paths)>MAX_VALUES:return both("error")
    if not paths:return both("error")
    joined=plan["join_with"].join(paths)
    return {"paths":envelope("values",paths),
            "merged":envelope("values",[joined]) if len(joined)<=MAX_VALUE
            else envelope("error")}
