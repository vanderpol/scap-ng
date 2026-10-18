#!/usr/bin/env python3
"""#237 partial source Variable DAG evaluation over precollected command Items.

Research fixture only: never executes commands, never returns source parity
or scanner execution. OVAL v5.12.3 merge document-order semantics are known;
actual collector System Characteristics Item order and regex dialect remain unverified.
"""
from __future__ import annotations
import json
import re
from research_b_variable_schedule import FORMAT as PLAN_FORMAT
from research_b_variable_value_ops import values,capture,concat,unique,merge

PROVIDER="independent.shellcommand"
MAX_COMMANDS=256
MAX_LINE=4096

def _fail():
    return values(status="error")

def _pending():
    return values(status="unknown")

def _collection(fixtures,using,pattern):
    source=fixtures.get(PROVIDER)
    if source is None:
        return _pending()
    if not isinstance(source,dict) or set(source)!={"acquisitions"} or (
            not isinstance(source["acquisitions"],list)) or (
            len(source["acquisitions"])>MAX_COMMANDS):
        return _fail()
    seen=set();matching=None
    for item in source["acquisitions"]:
        if not isinstance(item,dict) or not isinstance(item.get("using"),dict):
            return _fail()
        try:
            ident=json.dumps(item["using"],sort_keys=True)
        except (ValueError,TypeError):
            return _fail()
        if ident in seen:return _fail()
        seen.add(ident)
        if item["using"]==using:matching=item
    if matching is None:
        return _pending()
    if matching.get("provider")!=PROVIDER or matching.get("version")!="offline-source-shell-result-v0.1":
        return _fail()
    status=matching.get("status")
    if status in {"incomplete","not collected"}:
        return _pending()
    if status=="not applicable":
        return values(status="not_applicable")
    if status!="complete" or not isinstance(matching.get("items"),list):
        return _fail()
    try:
        regex=re.compile(pattern)
    except re.error:
        return _fail()
    ids=set();found=[]
    for item in matching["items"]:
        if not isinstance(item,dict) or not isinstance(item.get("fields"),dict):
            return _fail()
        name=item.get("id")
        if type(name) is not str or not name or name in ids:
            return _fail()
        ids.add(name)
        fields=item["fields"]
        if set(fields)!={"stdout_line","stderr_line","exit_status"} or (
            not isinstance(fields["stdout_line"],list)) or (
            not isinstance(fields["stderr_line"],list)) or (
            type(fields["exit_status"]) is not int) or any(
            type(x) is not str for x in fields["stdout_line"]+fields["stderr_line"]):
            return _fail()
        if using["error_if_exit_status_not_0"] and fields["exit_status"]!=0:
            return _fail()
        if using["error_if_stderr_exists"] and fields["stderr_line"]:
            return _fail()
        for line in fields["stdout_line"]:
            if len(line)>MAX_LINE:
                return _fail()
            if regex.search(line):
                found.append(line)
                if len(found)>256:return _fail()
    # Original OVAL ObjectComponent documentation calls zero collected
    # Items an error. Do not claim successful empty values for this pilot.
    return values(found) if found else _fail()

def evaluate_source_variable_plan(plan,fixtures):
    if (not isinstance(plan,dict) or plan.get("format")!=PLAN_FORMAT or
        plan.get("execution_supported") is not False or
        plan.get("original_source_parity_verified") is not False):
        raise ValueError("only nonexecuting source Variable plans supported")
    nodes=plan.get("nodes");shared=plan.get("source_shared_objects")
    if (not isinstance(nodes,list) or not nodes or len(nodes)>512 or
            not isinstance(shared,dict)):
        raise ValueError("invalid source Variable plan nodes/shared Objects")
    resolved={}
    def expr(node,depth=0):
        if depth>64 or not isinstance(node,dict) or len(node)!=1:
            return _fail()
        if "variable" in node:
            name=node["variable"]
            return resolved.get(name,_pending()) if type(name) is str else _fail()
        if "literal" in node:
            obj=node["literal"]
            if not isinstance(obj,dict) or set(obj)!={"datatype","value"} or (
                    obj["datatype"]!="string" or type(obj["value"]) is not str):
                return _fail()
            try:return values([obj["value"]])
            except ValueError:return _fail()
        if "values" in node:
            descriptor=node["values"]
            if not isinstance(descriptor,dict) or set(descriptor)!={"field","object"} or (
                    descriptor["field"]!="stdout_line"):
                return _fail()
            obj=descriptor["object"]
            if type(obj) is str:obj=shared.get(obj)
            if not isinstance(obj,dict) or set(obj)!={"capability","collect","object_title"} or (
                    obj["capability"]!=PROVIDER):
                return _fail()
            c=obj["collect"]
            required={"command","shell","pattern","error_if_exit_status_not_0",
                      "error_if_stderr_exists"}
            if not isinstance(c,dict) or set(c)!=required:
                return _fail()
            raw=c["command"]
            if type(raw) is str:
                command=values([raw])
            elif isinstance(raw,dict) and set(raw)=={"variable"}:
                command=expr(raw,depth+1)
            else:
                return _fail()
            if command["status"]!="values":return command
            if len(command["values"])!=1:return _pending()
            if (not command["values"][0] or len(command["values"][0])>MAX_LINE or
                c["shell"] not in {"bash","powershell"} or
                type(c["pattern"]) is not str or len(c["pattern"])>1024 or any(
                type(c[k]) is not bool for k in (
                  "error_if_exit_status_not_0","error_if_stderr_exists"))):
                return _fail()
            using={k:c[k] for k in ("shell","error_if_exit_status_not_0",
                                    "error_if_stderr_exists")}
            using["command"]=command["values"][0]
            return _collection(fixtures,using,c["pattern"])
        if "regex_capture" in node:
            spec=node["regex_capture"]
            if not isinstance(spec,dict) or set(spec)!={"pattern","value"}:
                return _fail()
            return capture(expr(spec["value"],depth+1),spec["pattern"])
        if "concat" in node:
            subs=node["concat"]
            if not isinstance(subs,list) or not 2<=len(subs)<=64:
                return _fail()
            return concat([expr(x,depth+1) for x in subs])
        if "unique" in node:
            return unique(expr(node["unique"],depth+1))
        if "merge" in node:
            data=node["merge"]
            if not isinstance(data,dict) or set(data)!={"delimiter","sort","order","values"}:
                return _fail()
            return merge(expr(data["values"],depth+1),
                         delimiter=data["delimiter"],sort=data["sort"],order=data["order"])
        return _fail()
    trace=[]
    for node in nodes:
        if not isinstance(node,dict) or set(node)!={
            "id","operator","depends_on","source_expression","source_datatype","source_kind"}:
            raise ValueError("malformed source Variable plan node")
        key=node["id"]
        if type(key) is not str or not key or key in resolved:
            raise ValueError("duplicate/missing source Variable ID")
        deps=node["depends_on"]
        if not isinstance(deps,list) or any(
                type(x) is not str or x not in resolved for x in deps):
            raise ValueError("unresolved/out-of-order source Variable dependencies")
        if node["source_datatype"]!="string" or node["source_kind"]!="local" or (
            not isinstance(node["source_expression"],dict)) or (
            set(node["source_expression"])!={node["operator"]}):
            raise ValueError("unsupported source Variable type/operator")
        result=expr(node["source_expression"])
        resolved[key]=result
        trace.append({"id":key,"operator":node["operator"],
                      "status":result["status"],"cardinality":len(result["values"])})
    return {
        "format":"scap-ng-b-variable-fixture-evaluation/0.1",
        "source_assessment_id":plan["source_assessment_id"],
        "execution_supported":False,
        "original_source_parity_verified":False,
        "nodes_evaluated":len(nodes),
        "variable_values":resolved,
        "trace":trace,
    }
