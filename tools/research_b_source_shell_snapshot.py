#!/usr/bin/env python3
"""#237: typed offline *already acquired* shell command output, no execution.

The scanner must separately implement a safe, signed-content-authorized
command runner and justify its OVAL stdout_line/exit_status Item semantics.
This adapter does not invoke shells or PowerShell, and does not prove parity.
"""
from __future__ import annotations

PROVIDER="independent.shellcommand"
VERSION="offline-source-shell-result-v0.1"
STATUSES={"complete","incomplete","error","not collected","not applicable"}


def normalize(snapshot, *, command, shell, error_if_exit_status_not_0,
              error_if_stderr_exists):
    using={"command":command,"shell":shell,
           "error_if_exit_status_not_0":error_if_exit_status_not_0,
           "error_if_stderr_exists":error_if_stderr_exists}
    if (type(command) is not str or not command or len(command)>4096 or
        shell not in {"bash","powershell"} or
        type(error_if_exit_status_not_0) is not bool or
        type(error_if_stderr_exists) is not bool):
        raise ValueError("source command acquisition identity is invalid")
    def fail(reason):
        return {"provider":PROVIDER,"version":VERSION,"using":using,
                "status":"error","items":[],"diagnostics":[{"reason":reason}]}
    if not isinstance(snapshot,dict) or set(snapshot)!={"query","status","records"}:
        return fail("unrecognized shell source snapshot envelope")
    if snapshot["query"]!=using:
        return fail("command acquisition identity mismatch")
    status=snapshot["status"];records=snapshot["records"]
    if not isinstance(status,str) or status not in STATUSES or not isinstance(records,list):
        return fail("invalid command output status or records")
    if status not in {"complete","incomplete"} and records:
        return fail("terminal command collection has unverified Items")
    items=[]
    for i,record in enumerate(records):
        if not isinstance(record,dict) or set(record)!={
            "stdout_line","stderr_line","exit_status"}:
            return fail("malformed source command Item")
        stdout=record["stdout_line"];stderr=record["stderr_line"];exitcode=record["exit_status"]
        if (not isinstance(stdout,list) or not isinstance(stderr,list) or
            any(type(v) is not str for v in stdout+stderr) or
            type(exitcode) is not int):
            return fail("command Item types invalid")
        if error_if_exit_status_not_0 and exitcode!=0:
            return fail("source command rejected nonzero exit status")
        if error_if_stderr_exists and stderr:
            return fail("source command rejected stderr")
        items.append({"id":f"shell-source-item:{i}",
                      "fields":{"stdout_line":list(stdout),
                                "stderr_line":list(stderr),
                                "exit_status":exitcode}})
    return {"provider":PROVIDER,"version":VERSION,"using":using,
            "status":status,"items":items,"diagnostics":[]}
