#!/usr/bin/env python3
"""#237: narrowly lower a state-free Windows WMI source existence Test.

Converted 0.3 source only, not original SCAP 1.4 XML or real Windows WMI.
Retains original WQL byte-for-byte. The caller-supplied WMI snapshot must
attest that the exact query ran and return an honest collection status.
"""
from __future__ import annotations

import re


def validate_wmi_query(ns,query):
    if (not isinstance(ns,str) or
        not re.fullmatch(r"[A-Za-z][\\w]*(?:\\\\[\\w]+)*",ns) or len(ns)>256):
        raise ValueError("WMI namespace must be an explicit bounded path")
    if (not isinstance(query,str) or len(query)>4096 or
        not re.match(r"^\\s*SELECT\\s+\\S+",query,re.IGNORECASE) or
        not re.search(r"\\bFROM\\b",query,re.IGNORECASE) or
        ";" in query or "\\x00" in query):
        raise ValueError("only bounded read-only WMI SELECT fixture queries supported")


def lower_state_free_wmi_assessment(source):
    if not isinstance(source, dict) or set(source) != {"assessment"}:
        raise ValueError("source WMI Assessment must be a single document")
    a=source["assessment"]
    keys={"assessment_title","class","evaluate","id","mode","purpose",
          "specification","tests","version"}
    if not isinstance(a,dict) or a.get("mode")!="automated" or set(a)-keys:
        raise ValueError("unsupported Assessment-level source WMI dependencies")
    tests=a.get("tests")
    if not isinstance(tests,dict) or len(tests)!=1:
        raise ValueError("one state-free WMI Test required")
    name,test=next(iter(tests.items()))
    if a.get("evaluate")!={"test":name}:
        raise ValueError("direct WMI Test reference required")
    if not isinstance(test,dict) or set(test)!={"capability","existence",
                                             "match","object","reported_elements",
                                             "test_title"}:
        raise ValueError("unhandled WMI State or source Test details")
    if (test["capability"]!="windows.wmi.query" or test["match"]!="all"
        or test["reported_elements"]!="all"):
        raise ValueError("unsupported WMI Test capability/item aggregation")
    existence={"none":"none_exist","one_or_more":"at_least_one_exists"}
    if test["existence"] not in existence:
        raise ValueError("unsupported WMI source Item existence semantics")
    obj=test["object"]
    if not isinstance(obj,dict) or set(obj)!={"capability","collect","object_title"}:
        raise ValueError("unsupported WMI Object set/selector semantics")
    if obj["capability"]!="windows.wmi.query":
        raise ValueError("WMI Object and Test capability differ")
    collected=obj["collect"]
    if not isinstance(collected,dict) or set(collected)!={"namespace","query"}:
        raise ValueError("unsupported WMI query acquisition fields")
    ns=collected["namespace"]; query=collected["query"]
    if (not isinstance(ns,str) or not re.fullmatch(r"[A-Za-z][\w]*(?:\\[\w]+)*",ns)
        or len(ns)>256):
        raise ValueError("WMI namespace must be an explicit bounded path")
    if (not isinstance(query,str) or len(query)>4096 or
        not re.match(r"^\s*SELECT\s+\S+",query,re.IGNORECASE) or
        not re.search(r"\bFROM\b",query,re.IGNORECASE) or
        ";" in query or "\x00" in query):
        raise ValueError("only bounded read-only WMI SELECT fixture queries supported")
    return {
        "kind":"compat_oval_provider_existence",
        "source_assessment_id":a["id"],
        "source_test_id":name,
        "provider":"windows.wmi.query",
        "using":{"namespace":ns,"query":query},
        "existence":existence[test["existence"]],
    }
