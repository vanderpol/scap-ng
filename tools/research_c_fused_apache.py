#!/usr/bin/env python3
"""#245 Prototype a REAL, bounded C Variable operation replacement.

Fuses actual Apache source regex_capture -> concat into ONE explicit pipeline.
Uses PRECOLLECTED and validated shell Items; does not execute OS commands or
claim OVAL regex/collection parity. Source identities are pinned and guarded.
"""
from __future__ import annotations
from copy import deepcopy
from itertools import product
from hashlib import sha256
import json
import re

SOURCE_CAP="independent.shellcommand"
KEY_SOURCE="apache-path-httpd-or-apache2-variable"
KEY_DERIVED="command-gather-apache-version-variable"
MAX_LINES=256
MAX_LEN=4096


def _hash(x):
    return sha256(json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()


def compile_fused_command_pipeline(assessment, *, pinned_variables_sha256):
    source=assessment.get("variables")
    if not isinstance(pinned_variables_sha256,str) or len(pinned_variables_sha256)!=64 or (
        _hash(source)!=pinned_variables_sha256
    ):
        raise ValueError("source Variable fingerprint changed; C fusion cannot claim lossless source")
    if not isinstance(source,dict) or set(source)!={KEY_SOURCE,KEY_DERIVED}:
        raise ValueError("C fusion only proven for this exact Apache two-node dependency")
    capture=source[KEY_SOURCE]["expression"]
    append=source[KEY_DERIVED]["expression"]
    if set(capture)!={"regex_capture"} or set(append)!={"concat"}:
        raise ValueError("C fusion recognizes only capture followed by concat")
    step=capture["regex_capture"]
    if set(step)!={"pattern","value"} or set(step["value"])!={"values"}:
        raise ValueError("unsupported source capture pipeline")
    src=step["value"]["values"]
    if set(src)!={"field","object"} or src["field"]!="stdout_line":
        raise ValueError("unsupported captured Item field")
    obj=src["object"]
    if not isinstance(obj,dict) or set(obj)!={"capability","collect","object_title"} or (
        obj["capability"]!=SOURCE_CAP
    ):
        raise ValueError("source must reuse existing shell capability")
    collect=obj["collect"]
    if set(collect)!={"command","shell","pattern","error_if_exit_status_not_0",
                      "error_if_stderr_exists"} or type(collect["command"]) is not str:
        raise ValueError("dynamic or unsupported acquisition selector")
    terms=append["concat"]
    if not isinstance(terms,list) or len(terms)!=2 or (
        terms[0]!={"variable":KEY_SOURCE}
        or not isinstance(terms[1],dict) or set(terms[1])!={"literal"} or
        terms[1]["literal"].get("datatype")!="string" or
        type(terms[1]["literal"].get("value")) is not str or
        source[KEY_SOURCE].get("datatype")!="string" or
        source[KEY_DERIVED].get("datatype")!="string"
    ):
        raise ValueError("unsupported concatenation dependency or datatype")
    return {
        "kind":"c-research-fused-typed-value-pipeline",
        "source_assessment_id":assessment["id"],
        "source_variables_sha256":pinned_variables_sha256,
        "source_ids":[KEY_SOURCE,KEY_DERIVED],
        "collect":deepcopy(collect),
        "capture_first_group":step["pattern"],
        "append_literal":terms[1]["literal"]["value"],
        "original_scanner_parity_verified":False,
        "collector_executed":False
    }


def evaluate_fused_command_pipeline(plan, evidence):
    """Separate transform implementation, shared *normalized* evidence contract."""
    from research_b_source_shell_snapshot import PROVIDER,VERSION
    if plan.get("kind")!="c-research-fused-typed-value-pipeline":
        raise ValueError("unrecognized C pipeline")
    def outcome(status,values=()):
        return {"status":status,"values":list(values)}
    root=evidence.get(PROVIDER)
    if root is None:return {"captured":outcome("unknown"),"derived":outcome("unknown")}
    if not isinstance(root,dict) or set(root)!={"acquisitions"} or not isinstance(root["acquisitions"],list):
        return {"captured":outcome("error"),"derived":outcome("error")}
    desired={k:plan["collect"][k] for k in ("command","shell","error_if_exit_status_not_0",
                                          "error_if_stderr_exists")}
    matches=[row for row in root["acquisitions"] if isinstance(row,dict) and row.get("using")==desired]
    if len(matches)!=1:return {"captured":outcome("unknown" if not matches else "error"),
                               "derived":outcome("unknown" if not matches else "error")}
    row=matches[0]
    if row.get("provider")!=PROVIDER or row.get("version")!=VERSION:
        return {"captured":outcome("error"),"derived":outcome("error")}
    status=row.get("status")
    if status!="complete":
        mapped={"incomplete":"unknown","not collected":"unknown","not applicable":"not_applicable"}.get(status,"error")
        return {"captured":outcome(mapped),"derived":outcome(mapped)}
    try:
        select=re.compile(plan["collect"]["pattern"])
        capture=re.compile(plan["capture_first_group"])
    except (re.error,TypeError):
        return {"captured":outcome("error"),"derived":outcome("error")}
    if capture.groups<1:
        return {"captured":outcome("error"),"derived":outcome("error")}
    captured=[]
    ids=set()
    for item in row.get("items",[]):
        if not isinstance(item,dict) or set(item)!={"id","fields"} or (
            type(item["id"]) is not str or item["id"] in ids
        ):
            return {"captured":outcome("error"),"derived":outcome("error")}
        ids.add(item["id"])
        fields=item["fields"]
        if not isinstance(fields,dict) or set(fields)!={"stdout_line","stderr_line","exit_status"} or (
            not isinstance(fields["stdout_line"],list) or
            not isinstance(fields["stderr_line"],list) or
            type(fields["exit_status"]) is not int
        ):
            return {"captured":outcome("error"),"derived":outcome("error")}
        if plan["collect"]["error_if_exit_status_not_0"] and fields["exit_status"]!=0:
            return {"captured":outcome("error"),"derived":outcome("error")}
        if plan["collect"]["error_if_stderr_exists"] and fields["stderr_line"]:
            return {"captured":outcome("error"),"derived":outcome("error")}
        for line in fields["stdout_line"]:
            if type(line) is not str or len(line)>MAX_LEN:
                return {"captured":outcome("error"),"derived":outcome("error")}
            if select.search(line):
                m=capture.search(line)
                value=m.group(1) if m and m.group(1) is not None else ""
                captured.append(value)
                if len(captured)>MAX_LINES or len(value)>MAX_LEN:
                    return {"captured":outcome("error"),"derived":outcome("error")}
    if not captured:return {"captured":outcome("error"),"derived":outcome("error")}
    suffix=plan["append_literal"]
    derived=[x+suffix for x in captured]
    if any(len(x)>MAX_LEN for x in derived):
        return {"captured":outcome("values",captured),"derived":outcome("error")}
    return {"captured":outcome("values",captured),
            "derived":outcome("values",derived)}
