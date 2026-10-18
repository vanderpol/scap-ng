#!/usr/bin/env python3
"""#237: bounded source shellcommand Test -> B compiler-owned fixture IR.

Accepts one direct, static, single-State command output check only. This code
NEVER executes the command. Dynamic commands, local Variables, regex-driven
Item creation, stdout parsing variants and compound States remain unsupported.
Converted 0.3 input is not original SCAP 1.4 XML parity.
"""
from __future__ import annotations


def lower_source_shell_assessment(source):
    if not isinstance(source,dict) or set(source)!={"assessment"}:
        raise ValueError("source shell command must be one Assessment")
    a=source["assessment"]
    allowed={"assessment_title","class","evaluate","id","mode","purpose",
             "specification","tests","version"}
    if not isinstance(a,dict) or a.get("mode")!="automated" or set(a)-allowed:
        raise ValueError("source shell Assessment Variables/inputs unsupported")
    tests=a.get("tests")
    if not isinstance(tests,dict) or len(tests)!=1:
        raise ValueError("bounded shell check requires one direct source Test")
    tid,t=next(iter(tests.items()))
    if not isinstance(tid,str) or not tid or a.get("evaluate")!={"test":tid}:
        raise ValueError("invalid direct source shell Test reference")
    if not isinstance(t,dict) or set(t)!={"capability","existence","match",
                                        "object","states","test_title","reported_elements"}:
        raise ValueError("unsupported shell Test fields or States")
    if (t["capability"]!="independent.shellcommand" or t["existence"]!="one_or_more" or
        t["match"]!="all" or t["reported_elements"]!="all"):
        raise ValueError("unsupported source shell Test cardinality")
    obj=t["object"]
    if not isinstance(obj,dict) or set(obj)!={"capability","collect","object_title"} or (
            obj["capability"]!="independent.shellcommand"):
        raise ValueError("unsupported source shell Object filters/sets")
    collect=obj["collect"]
    expected={"command","shell","error_if_exit_status_not_0","error_if_stderr_exists"}
    if not isinstance(collect,dict) or set(collect)!=expected:
        raise ValueError("unsupported command collection arguments")
    using={
        "command":collect["command"],
        "shell":collect["shell"],
        "error_if_exit_status_not_0":collect["error_if_exit_status_not_0"],
        "error_if_stderr_exists":collect["error_if_stderr_exists"],
    }
    if type(using["command"]) is not str or not using["command"] or (
        len(using["command"])>4096) or using["shell"] not in {"bash","powershell"} or any(
            type(using[k]) is not bool for k in
            ("error_if_exit_status_not_0","error_if_stderr_exists")):
        raise ValueError("source command must be bounded literal plus typed flags")
    states=t["states"]
    if not isinstance(states,list) or len(states)!=1:
        raise ValueError("bounded source shell supports exactly one State")
    st=states[0]
    if (not isinstance(st,dict) or set(st)!={"field","operation","value",
                                            "existence","match"} or
        st["field"]!="stdout_line" or st["operation"]!="equals" or
        st["existence"]!="one_or_more" or st["match"]!="all" or
        type(st["value"]) is not str):
        raise ValueError("unsupported shell stdout entity comparison/cardinality")
    return {
        "kind":"compat_oval_shellcommand_state",
        "source_assessment_id":a["id"],
        "source_test_id":tid,
        "provider":"independent.shellcommand",
        "using":using,
        "existence":"at_least_one_exists",
        "check":"all",
        "state":{"field":"stdout_line","operation":"equals","expected":st["value"],
                 "entity_existence":"at_least_one_exists","entity_check":"all"},
    }
