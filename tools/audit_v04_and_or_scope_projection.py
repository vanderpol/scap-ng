#!/usr/bin/env python3
"""OVAL-aligned AND/OR scope projection for current SCAP-NG 0.4 authoring.

This is a read-only, reversible, scope-sensitive analysis tool. It does NOT
edit the accepted v0.4 grammar or the pinned six-STIG authoring packages.

Logical operators: and/or/one/xor (map exact OVAL AND/OR/ONE/XOR).
Quantifiers: collection.items and matching_items (separate from logic).
The current v0.4 surface has legacy evaluate.all/any/odd and states_match;
projection changes a token ONLY in its proven logical location.

Refs #248 #239.
"""
from __future__ import annotations

from copy import deepcopy

LOGIC_TO_OVAL={"and":"AND","or":"OR","one":"ONE","xor":"XOR"}
EVAL_TO_LOGIC={"all":"and","any":"or","one":"one","odd":"xor"}
STATES_TO_LOGIC={"all":"and","any":"or","one":"one","odd":"xor"}
LOGIC_TO_EVAL={v:k for k,v in EVAL_TO_LOGIC.items()}
LOGIC_TO_STATES={v:k for k,v in STATES_TO_LOGIC.items()}
TEST_LOGICAL={"all","any","one","odd","and","or","xor"}
LEAF={"test","assessment","not_applicable"}


def _bad(msg):
    raise ValueError("0.4 Boolean scope projection: "+msg)


def evaluate_projection(expr, *, accept_canonical=False):
    """Change only complete-Test-result logical combiners; preserve conditionals."""
    if not isinstance(expr,dict) or not expr:
        _bad("invalid evaluate expression")
    if set(expr)&TEST_LOGICAL:
        if len(expr)!=1:
            _bad("logical node has multiple operators")
        key,children=next(iter(expr.items()))
        operators = {**EVAL_TO_LOGIC, **({k:k for k in LOGIC_TO_OVAL} if accept_canonical else {})}
        if key not in operators or not isinstance(children,list) or not children:
            _bad("unknown/empty legacy evaluate operator")
        return {operators[key]:[evaluate_projection(x, accept_canonical=accept_canonical) for x in children]}
    if set(expr)=={"not"}:
        return {"not":evaluate_projection(expr["not"], accept_canonical=accept_canonical)}
    if set(expr)=={"if","then","else"}:
        return {k:evaluate_projection(expr[k], accept_canonical=accept_canonical) for k in ("if","then","else")}
    if len(expr)==1 and next(iter(expr)) in LEAF:
        return deepcopy(expr)
    _bad("unknown evaluate expression or incomplete IF/THEN/ELSE")


def evaluate_inverse(expr):
    if not isinstance(expr,dict) or not expr:
        _bad("invalid projected evaluation")
    if len(expr)==1 and next(iter(expr)) in LOGIC_TO_EVAL:
        key,children=next(iter(expr.items()))
        if not isinstance(children,list) or not children:
            _bad("projected evaluation has empty operands")
        return {LOGIC_TO_EVAL[key]:[evaluate_inverse(x) for x in children]}
    if set(expr)=={"not"}:
        return {"not":evaluate_inverse(expr["not"])}
    if set(expr)=={"if","then","else"}:
        return {k:evaluate_inverse(expr[k]) for k in ("if","then","else")}
    if len(expr)==1 and next(iter(expr)) in LEAF:
        return deepcopy(expr)
    _bad("invalid projected evaluation")


def test_projection(test):
    """Preserve whole-condition grouping and its separate Item quantifier."""
    if not isinstance(test,dict) or "require" not in test:
        _bad("Test.require missing")
    req=test["require"]
    states=test.get("states")
    structured=isinstance(req,dict) and "all_items_must" in req
    if structured:
        if "states" in test or "states_match" in test and states is not None:
            _bad("Test has incompatible source state layouts")
        if set(req)!={"items","all_items_must"}:
            _bad("structured source has unknown Item matching qualifier")
        if not isinstance(req["all_items_must"],list) or not req["all_items_must"]:
            _bad("structured source has no conditions")
        if req["items"] not in ("one_or_more","may_be_absent"):
            _bad("unapproved Item existence quantifier")
        operator=test.get("states_match","all")
        if operator not in STATES_TO_LOGIC:
            _bad("unrecognized OVAL State aggregation")
        return {"source_layout":"all_items_must",
                "items_exist":req["items"],
                "matching_items":"all",
                "condition_operator":STATES_TO_LOGIC[operator],
                "operator_explicit":"states_match" in test,
                "conditions":deepcopy(req["all_items_must"]),
                "condition_count":len(req["all_items_must"]),
                "field_scope":deepcopy(test.get("state_fields_require"))}
    if isinstance(states,list):
        if not states:
            _bad("empty list of original States")
        operator=test.get("states_match","all")
        if operator not in STATES_TO_LOGIC:
            _bad("unknown State combination operator")
        return {"source_layout":"legacy_states",
                "source_test_requirement":deepcopy(req),
                "items_exist":"per_paired_requirement",
                "matching_items":"per_paired_requirement",
                "condition_operator":STATES_TO_LOGIC[operator],
                "operator_explicit":"states_match" in test,
                "conditions":deepcopy(states),
                "condition_count":len(states),
                "field_scope":deepcopy(test.get("state_fields_require"))}
    if "states_match" in test:
        _bad("unassociated State combinator")
    if "states" in test:
        _bad("unsupported null or invalid State list")
    return {"source_layout":"without_states",
            "source_test_requirement":deepcopy(req),
            "items_exist":"from_requirement",
            "matching_items":"from_requirement",
            "condition_operator":None,
            "operator_explicit":False,
            "conditions":[],
            "condition_count":0,
            "field_scope":None}


def test_inverse(test,shadow):
    """Rehydrate Test from projection, never copy/move Item quantifier into logic."""
    original=deepcopy(test)
    kind=shadow["source_layout"]
    if kind=="all_items_must":
        original["require"]={"items":shadow["items_exist"],
                             "all_items_must":deepcopy(shadow["conditions"])}
        original.pop("states_match",None)
        original.pop("states",None)
    elif kind=="legacy_states":
        original["require"]=deepcopy(shadow["source_test_requirement"])
        original["states"]=deepcopy(shadow["conditions"])
        original.pop("states_match",None)
    elif kind=="without_states":
        original["require"]=deepcopy(shadow["source_test_requirement"])
        original.pop("states_match",None)
        original.pop("states",None)
    else:
        _bad("unknown projected original layout")
    if kind!="without_states" and shadow["operator_explicit"]:
        op=shadow["condition_operator"]
        if op not in LOGIC_TO_STATES:
            _bad("invalid projected operator")
        original["states_match"]=LOGIC_TO_STATES[op]
    if kind!="without_states" and shadow["field_scope"] is not None:
        original["state_fields_require"]=deepcopy(shadow["field_scope"])
    return original


def document_projection(doc):
    a=doc.get("assessment") if isinstance(doc,dict) else None
    if not isinstance(a,dict) or a.get("mode")!="automated":
        _bad("expected active automated Assessment")
    if a.get("specification",{}).get("version")!="0.4.0":
        _bad("not current 0.4 authoring")
    tests=a.get("tests")
    if not isinstance(tests,dict) or not tests:
        _bad("Assessment has no Tests")
    result={"assessment_id":a.get("id"),"test_logic":{},
            "evaluate_logic":evaluate_projection(a["evaluate"])}
    for name,test in tests.items():
        result["test_logic"][name]=test_projection(test)
    return result


def document_inverse(doc,shadow):
    a=doc["assessment"]
    recreated=deepcopy(doc)
    recreated["assessment"]["evaluate"]=evaluate_inverse(shadow["evaluate_logic"])
    for key,test in a["tests"].items():
        recreated["assessment"]["tests"][key]=test_inverse(test,shadow["test_logic"][key])
    if recreated!=doc:
        _bad("operator projection/inversion lost source Test/expression semantics")
    return True
