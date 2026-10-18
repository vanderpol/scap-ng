#!/usr/bin/env python3
"""#237 bounded source Apache process -> regex capture -> concat -> version.

Only a 2-variable acyclic dependency shape of converted 0.3 YAML is accepted.
The resulting compiler-owned B IR NEVER grants permission to execute shell.
Original OVAL 5.12.3 variable/regex/version semantics are not yet proven.
"""
from __future__ import annotations
import re

ASSESSMENT_KEYS={"id","version","assessment_title","mode","class","purpose",
                 "specification","tests","evaluate","variables"}
VAR_KEYS={"kind","datatype","title","expression"}
TEST_KEYS={"capability","existence","match","object","reported_elements",
           "states","test_title"}
OBJECT_KEYS={"capability","collect","object_title"}
COLLECT_KEYS={"command","shell","pattern","error_if_exit_status_not_0",
              "error_if_stderr_exists"}
USING_KEYS={"command","shell","error_if_exit_status_not_0",
            "error_if_stderr_exists"}


def _regex(pattern,label):
    if type(pattern) is not str or not pattern or len(pattern)>1024:
        raise ValueError(label+" requires bounded regex literal")
    try:
        value=re.compile(pattern)
    except re.error as exc:
        raise ValueError(label+" contains invalid fixture regex") from exc
    return value


def _collector(obj,label,*,allow_variable):
    if not isinstance(obj,dict) or set(obj)!=OBJECT_KEYS or (
            obj["capability"]!="independent.shellcommand"):
        raise ValueError(label+" unexpected Object, set, or filter")
    raw=obj["collect"]
    if not isinstance(raw,dict) or set(raw)!=COLLECT_KEYS:
        raise ValueError(label+" source collector contract differs")
    command=raw["command"]
    if allow_variable:
        if not isinstance(command,dict) or set(command)!={"variable"} or (
                type(command["variable"]) is not str or not command["variable"]):
            raise ValueError(label+" requires a single local command Variable")
    elif type(command) is not str or not command or len(command)>4096:
        raise ValueError(label+" requires bounded literal command")
    if raw["shell"]!="bash" or any(type(raw[key]) is not bool for key in (
            "error_if_exit_status_not_0","error_if_stderr_exists")):
        raise ValueError(label+" only bash and explicit Boolean command flags")
    _regex(raw["pattern"],label+" collection pattern")
    using={key:raw[key] for key in USING_KEYS}
    return using,raw["pattern"]


def _variable(value,label):
    if not isinstance(value,dict) or set(value)!=VAR_KEYS or (
            value["kind"]!="local" or value["datatype"]!="string" or
            not isinstance(value["title"],str)):
        raise ValueError(label+" must be local string Variable with explicit metadata")
    if not isinstance(value["expression"],dict) or len(value["expression"])!=1:
        raise ValueError(label+" Variable expression must be a single operator")
    return value["expression"]


def lower_apache_version_graph(source):
    if not isinstance(source,dict) or set(source)!={"assessment"}:
        raise ValueError("requires one converted Apache Assessment")
    a=source["assessment"]
    if not isinstance(a,dict) or a.get("mode")!="automated" or set(a)!=ASSESSMENT_KEYS:
        raise ValueError("source Apache Assessment requires bounded Variable graph")
    tests=a["tests"]
    if not isinstance(tests,dict) or len(tests)!=1:
        raise ValueError("single direct Test required for Apache graph pilot")
    test_id,t=next(iter(tests.items()))
    if not isinstance(test_id,str) or not test_id or a.get("evaluate")!={"test":test_id}:
        raise ValueError("Apache graph must have direct Test reference")
    if not isinstance(t,dict) or set(t)!=TEST_KEYS or (
        t["capability"]!="independent.shellcommand" or
        t["existence"]!="one_or_more" or t["match"]!="all" or
        t["reported_elements"]!="all"):
        raise ValueError("Apache graph Test capability/cardinality unsupported")
    states=t["states"]
    if not isinstance(states,list) or len(states)!=1 or not isinstance(states[0],dict):
        raise ValueError("one source Apache version State expected")
    st=states[0]
    if set(st)!={"existence","field","match","operation","value"} or (
        st["existence"]!="one_or_more" or st["field"]!="subexpression" or
        st["match"]!="one_or_more" or
        st["operation"]!="version_greater_than_or_equal" or
        type(st["value"]) is not str or
        not re.fullmatch(r"[0-9]+(?:\.[0-9]+){1,3}",st["value"])):
        raise ValueError("source Apache version State semantics unsupported")
    target_using,target_pattern=_collector(t["object"],"Apache version",
                                           allow_variable=True)
    target_ref=target_using.pop("command")["variable"]
    target_group=_regex(target_pattern,"Apache version")
    if target_group.groups!=1 or target_group.groupindex:
        raise ValueError("Apache version source pattern must capture one group")

    variables=a["variables"]
    if not isinstance(variables,dict) or target_ref not in variables or len(variables)!=2:
        # The graph must be a closed acyclic pair, without unused Variables.
        raise ValueError("unsupported or unreferenced Apache Variable dependency")
    build=_variable(variables[target_ref],target_ref)
    if set(build)!={"concat"} or not isinstance(build["concat"],list) or len(build["concat"])!=2:
        raise ValueError("Apache command Variable requires binary concat")
    source_ref,constant=build["concat"]
    if (not isinstance(source_ref,dict) or set(source_ref)!={"variable"} or
        type(source_ref["variable"]) is not str or
        source_ref["variable"]==target_ref or
        not isinstance(constant,dict) or set(constant)!={"literal"} or
        not isinstance(constant["literal"],dict) or
        set(constant["literal"])!={"datatype","value"} or
        constant["literal"]["datatype"]!="string" or
        constant["literal"]["value"]!=" -V"):
        raise ValueError("unsupported source concat dependency or suffix")
    discovery_ref=source_ref["variable"]
    if discovery_ref not in variables or discovery_ref==target_ref or (
            set(variables)!={target_ref,discovery_ref}):
        raise ValueError("source dynamic command Variable missing, unused or cyclic")
    capture=_variable(variables[discovery_ref],discovery_ref)
    if set(capture)!={"regex_capture"} or not isinstance(capture["regex_capture"],dict):
        raise ValueError("source executable path Variable requires regex_capture")
    graph=capture["regex_capture"]
    if set(graph)!={"pattern","value"} or not isinstance(graph["value"],dict) or (
            set(graph["value"])!={"values"} or not isinstance(graph["value"]["values"],dict)):
        raise ValueError("source regex_capture expression unsupported")
    source_values=graph["value"]["values"]
    if set(source_values)!={"field","object"} or source_values["field"]!="stdout_line":
        raise ValueError("source regex_capture must consume stdout_line collection")
    capture_expr=_regex(graph["pattern"],"executable path capture")
    if capture_expr.groups!=1 or capture_expr.groupindex:
        raise ValueError("executable path extraction must capture exactly one group")
    source_using,source_pattern=_collector(source_values["object"],"process discovery",
                                           allow_variable=False)
    return {
        "kind":"compat_oval_shellcommand_variable_version",
        "source_assessment_id":a["id"],
        "source_test_id":test_id,
        "provider":"independent.shellcommand",
        "discovery_using":source_using,
        "discovery_pattern":source_pattern,
        "capture_pattern":graph["pattern"],
        "capture_variable":discovery_ref,
        "command_variable":target_ref,
        "command_suffix":constant["literal"]["value"],
        "version_using":target_using,
        "version_pattern":target_pattern,
        "existence":"at_least_one_exists",
        "check":"all",
        "state":{"field":"subexpression",
                 "operation":"version_greater_than_or_equal",
                 "expected":st["value"],
                 "entity_existence":"at_least_one_exists",
                 "entity_check":"at least one"},
    }


def validate_apache_version_ir(node):
    """Validate the research IR shape; source-leaf reconstruction is separate."""
    keys={"kind","source_assessment_id","source_test_id","provider",
          "discovery_using","discovery_pattern","capture_pattern",
          "capture_variable","command_variable","command_suffix",
          "version_using","version_pattern","existence","check","state"}
    if not isinstance(node,dict) or set(node)!=keys:
        raise ValueError("invalid source Apache graph IR keys")
    if node["kind"]!="compat_oval_shellcommand_variable_version" or (
            node["provider"]!="independent.shellcommand"):
        raise ValueError("invalid Apache graph kind/provider")
    if any(type(node[k]) is not str or not node[k] for k in (
            "source_assessment_id","source_test_id","capture_variable",
            "command_variable")) or (
            node["capture_variable"]==node["command_variable"]):
        raise ValueError("invalid Apache graph source identity or cyclic variables")
    if node["command_suffix"]!=" -V":
        raise ValueError("unsupported source Apache command Variable suffix")
    for key in ("discovery_using","version_using"):
        using=node[key]
        expected=USING_KEYS if key=="discovery_using" else (
            USING_KEYS-{"command"})
        if not isinstance(using,dict) or set(using)!=expected:
            raise ValueError("invalid Apache graph source query arguments")
        if key=="discovery_using":
            if type(using["command"]) is not str or not using["command"] or (
                    len(using["command"])>4096):
                raise ValueError("invalid source discovery command")
        if using["shell"]!="bash" or any(type(using[x]) is not bool for x in (
                "error_if_exit_status_not_0","error_if_stderr_exists")):
            raise ValueError("Apache graph source command flags invalid")
    if _regex(node["capture_pattern"],"source executable capture").groups!=1:
        raise ValueError("source Apache executable capture group count invalid")
    if _regex(node["version_pattern"],"source version regex").groups!=1:
        raise ValueError("source Apache version capture group count invalid")
    _regex(node["discovery_pattern"],"source discovery filter")
    state=node["state"]
    if (not isinstance(state,dict) or set(state)!={
            "field","operation","expected","entity_existence","entity_check"} or
            state["field"]!="subexpression" or
            state["operation"]!="version_greater_than_or_equal" or
            state["entity_existence"]!="at_least_one_exists" or
            state["entity_check"]!="at least one" or
            type(state["expected"]) is not str or
            not re.fullmatch(r"[0-9]+(?:\.[0-9]+){1,3}",state["expected"])):
        raise ValueError("source Apache version State shape invalid")
    if node["existence"]!="at_least_one_exists" or node["check"]!="all":
        raise ValueError("source Apache version Test cardinality invalid")
