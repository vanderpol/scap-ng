#!/usr/bin/env python3
"""#237: strict converted-0.3 State-bearing textfile Test lowerer for B.

Handles ONE direct Test, ONE simple State on a single regex capture group.
Not a proof of original OVAL textfilecontent54 regex, entity cardinality,
regex capture collation, Item creation, or SCAP 1.4 XML equivalence.
"""
from __future__ import annotations

import re


def lower_single_capture_textfile_assessment(source):
    if not isinstance(source,dict) or set(source)!={"assessment"}:
        raise ValueError("one converted Assessment required")
    a=source["assessment"]
    allowed={"assessment_title","class","evaluate","id","mode","purpose",
             "specification","tests","version"}
    if not isinstance(a,dict) or a.get("mode")!="automated" or set(a)-allowed:
        raise ValueError("unsupported Assessment fields or source mode")
    tests=a.get("tests")
    if not isinstance(tests,dict) or len(tests)!=1:
        raise ValueError("State-bearing pilot requires exactly one Test")
    name,test=next(iter(tests.items()))
    if a.get("evaluate")!={"test":name}:
        raise ValueError("nested Test evaluation is not supported")
    if not isinstance(test,dict) or set(test)!={"capability","existence",
                                             "match","object","reported_elements",
                                             "states","test_title"}:
        raise ValueError("unexpected source Test or State contract")
    if test["capability"]!="independent.textfilecontent54":
        raise ValueError("wrong collection capability")
    # Other Test existence scopes need separate zero-Item State proofs.
    existence={"one_or_more":"at_least_one_exists"}
    checks={"all":"all","one":"only one","one_or_more":"at least one","none":"none satisfy"}
    if test["existence"] not in existence or test["match"] not in checks:
        raise ValueError("unsupported source Test existence/matching")
    if test["reported_elements"]!="all":
        raise ValueError("source reported element selection unsupported")
    states=test["states"]
    if not isinstance(states,list) or len(states)!=1:
        raise ValueError("only one source State supported")
    state=states[0]
    if not isinstance(state,dict) or set(state)!={"field","operation","value",
                                                "existence","match"}:
        raise ValueError("unrecognized source State fields/cardinality")
    numeric={"greater_than_or_equal","greater_than","less_than","less_than_or_equal"}
    if (state["field"]!="subexpression" or
        state["operation"] not in numeric|{"equals","not_equals","pattern_match"} or
        state["existence"]!="one_or_more" or state["match"]!="all"):
        raise ValueError("State operation or entity quantifier unsupported")
    if state["operation"] in numeric:
        if type(state["value"]) is not int or not -(2**63)<=state["value"]<2**63:
            raise ValueError("numeric State comparison requires signed int64 literal")
    elif not isinstance(state["value"],str):
        raise ValueError("string State comparison requires literal text")
    if state["operation"]=="pattern_match":
        if len(state["value"])>2048:
            raise ValueError("source State regex exceeds bounded research length")
        try:
            re.compile(state["value"])
        except re.error as exc:
            raise ValueError("source State pattern is not supported by Python fixture") from exc
    obj=test["object"]
    if not isinstance(obj,dict) or set(obj)!={"capability","collect","filesystem",
                                            "object_title","select"}:
        raise ValueError("source Object set/filter/fields unsupported")
    if obj["capability"]!="independent.textfilecontent54" or obj["filesystem"]!="all":
        raise ValueError("unsupported Object capability/filesystem scope")
    flags=obj["collect"]
    if not isinstance(flags,dict) or set(flags)!={"ignore_case","item_creation",
                                                 "multiline","singleline"}:
        raise ValueError("source Object collection modes unsupported")
    if flags["item_creation"]!="all_object_elements_fullfilled" or any(
        type(flags[k]) is not bool for k in ("ignore_case","multiline","singleline")
    ):
        raise ValueError("Item creation or regex mode unsupported")
    selectors=obj["select"]
    if not isinstance(selectors,dict) or set(selectors)!={"full_path","pattern","instance"}:
        raise ValueError("source Object selector shape unsupported")
    if selectors["instance"]!={"operation":"greater_than_or_equal","value":1}:
        raise ValueError("source instance range unsupported")
    full=selectors["full_path"];pattern=selectors["pattern"]
    if (not isinstance(full,dict) or set(full)!={"operation","value"} or
        full["operation"]!="equals" or not isinstance(full["value"],str) or
        not full["value"].startswith("/")):
        raise ValueError("source path selector must be absolute equality")
    if (not isinstance(pattern,dict) or set(pattern)!={"operation","value"} or
        pattern["operation"]!="pattern_match" or not isinstance(pattern["value"],str)):
        raise ValueError("source regex must be a literal pattern match")
    regex=pattern["value"]
    try:
        flags_python=(re.IGNORECASE if flags["ignore_case"] else 0)
        flags_python|=(re.MULTILINE if flags["multiline"] else 0)
        flags_python|=(re.DOTALL if flags["singleline"] else 0)
        parsed=re.compile(regex, flags_python)
    except re.error as exc:
        raise ValueError("unsupported or invalid Python regex fixture") from exc
    if parsed.groups!=1 or parsed.groupindex:
        raise ValueError("source regex must have exactly one unnamed capture group")
    using={"path":full["value"],"pattern":regex,
           "ignore_case":flags["ignore_case"],"multiline":flags["multiline"],
           "singleline":flags["singleline"]}
    return {
        "kind":"compat_oval_provider_state",
        "source_assessment_id":a["id"],
        "source_test_id":name,
        "provider":"linux.textfile_matches",
        "using":using,
        "existence":existence[test["existence"]],
        "check":checks[test["match"]],
        "state":{"field":"subexpression",
                 "operation":state["operation"],
                 "expected":state["value"],
                 "entity_existence":"at_least_one_exists",
                 "entity_check":"all"},
    }
