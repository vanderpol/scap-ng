#!/usr/bin/env python3
"""#235: FAIL-CLOSED one-family source-shape lowerer for B research.

Accepts only the pinned state-free Chrony textfilecontent54 Test shape.
It is NOT generic SCAP 1.4/OVAL XML conversion: input is converted 0.3 YAML.
Exact regex engine, item_creation, filesystem and host parity UNPROVEN.
"""
from __future__ import annotations

from pathlib import Path
import yaml


def lower_state_free_textfile_assessment(source):
    if not isinstance(source, dict) or set(source) != {"assessment"}:
        raise ValueError("single converted Assessment document required")
    a = source["assessment"]
    if not isinstance(a,dict) or a.get("mode") != "automated":
        raise ValueError("source must be an automated Assessment")
    allowed={"assessment_title","class","evaluate","id","mode","purpose",
             "specification","tests","version"}
    if set(a)-allowed:
        raise ValueError("unsupported Assessment-level Variables, shared Objects or inputs")
    tests = a.get("tests")
    if not isinstance(tests,dict) or len(tests) != 1:
        raise ValueError("only one local state-free Test is supported")
    test_id, t = next(iter(tests.items()))
    if a.get("evaluate") != {"test":test_id}:
        raise ValueError("only a single directly evaluated Test is supported")
    if set(t) != {"capability","existence","match","object",
                  "reported_elements","test_title"}:
        raise ValueError("unsupported Test details or State/Variable semantics")
    if (t["capability"],t["existence"],t["match"]) != (
            "independent.textfilecontent54","one_or_more","all"):
        raise ValueError("unsupported Test capability/cardinality")
    if t["reported_elements"] != "all":
        raise ValueError("unsupported source evidence reporting")
    obj=t["object"]
    if not isinstance(obj,dict) or set(obj) != {
            "capability","collect","filesystem","object_title","select"}:
        raise ValueError("unsupported original Object shape")
    if (obj["capability"],obj["filesystem"]) != (
            "independent.textfilecontent54","all"):
        raise ValueError("unsupported source collection family")
    collect=obj["collect"]
    if not isinstance(collect,dict) or set(collect)!={
            "ignore_case","item_creation","multiline","singleline"}:
        raise ValueError("unexpected source collection options")
    if collect["item_creation"] != "all_object_elements_fullfilled":
        raise ValueError("unsupported source Item creation option")
    for name in ("ignore_case","multiline","singleline"):
        if type(collect[name]) is not bool:
            raise ValueError("source regex flags must be Boolean")
    selectors=obj["select"]
    if not isinstance(selectors,dict) or set(selectors)!={
            "full_path","pattern","instance"}:
        raise ValueError("source must select path, pattern and instance")
    full=selectors["full_path"]
    match=selectors["pattern"]
    instance=selectors["instance"]
    if not isinstance(full,dict) or set(full)!={"operation","value"} or (
            full["operation"]!="equals" or type(full["value"]) is not str or
            not full["value"].startswith("/")):
        raise ValueError("source path is not a single absolute equality selector")
    if not isinstance(match,dict) or set(match)!={"operation","value"} or (
            match["operation"]!="pattern_match" or
            type(match["value"]) is not str or not match["value"]):
        raise ValueError("unsupported source pattern selector")
    if instance != {"operation":"greater_than_or_equal","value":1}:
        raise ValueError("unsupported source instance boundary")
    using={"path":full["value"],"pattern":match["value"],
           "ignore_case":collect["ignore_case"],"multiline":collect["multiline"],
           "singleline":collect["singleline"]}
    return {"kind":"compat_oval_provider_existence",
            "source_assessment_id":a["id"],
            "source_test_id":test_id,
            "provider":"linux.textfile_matches",
            "using":using,
            "existence":"at_least_one_exists"}


def read_source(path):
    return lower_state_free_textfile_assessment(yaml.safe_load(Path(path).read_text()))
