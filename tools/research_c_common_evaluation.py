#!/usr/bin/env python3
"""#245 C capability-neutral assessment semantics proof (RESEARCH ONLY).

One shared Item/existence and Assessment truth boundary across collectors.
This adapter delegates to pinned A/OVAL 5.12.3 table implementations; it
does not compare Item fields, run collection, or approve a new C grammar.
"""
from __future__ import annotations

from oval_result_truth_tables import evaluate_collected_object_test, RESULTS
from v04_a_truth_plan import compile_expression, execute_supplied_results

C_EXPR={"every":"all","one_of":"any","exactly_one":"one","odd_count":"odd"}
ITEM_CHECKS={"every":"all","one_of":"at least one","exactly_one":"only one",
             "none":"none satisfy"}
EXISTS={"at_least_one_exists","none_exist","only_one_exists","any_exist","all_exist"}
FLAGS={"complete":"complete","incomplete":"incomplete","error":"error",
       "not_collected":"not collected","not_applicable":"not applicable",
       "does_not_exist":"does not exist"}
SIX=frozenset(("true","false","error","unknown","not_evaluated","not_applicable"))


def population_outcome(requirement, evidence):
    """Evaluate a capability-neutral *already-collected* Item population.

    Evidence carries a capability ID for provenance but it does not select
    provider-specific logic. Complete empty differs from missing/incomplete.
    Item predicates have ALREADY been evaluated by a typed comparator.
    """
    if not isinstance(requirement,dict) or set(requirement)!={"exists","items_match","has_state"}:
        raise ValueError("C existence, item matching and State presence are explicit")
    if requirement["exists"] not in EXISTS or type(requirement["has_state"]) is not bool:
        raise ValueError("invalid existence / State contract")
    if requirement["items_match"] not in ITEM_CHECKS:
        raise ValueError("unrecognized Item-matching operator")
    if not isinstance(evidence,dict) or set(evidence)!={"capability","status","items",
                                                        "does_not_exist","error","not_collected"}:
        raise ValueError("invalid collected-evidence envelope")
    if not isinstance(evidence["capability"],str) or not evidence["capability"] or (
        evidence["status"] not in FLAGS or not isinstance(evidence["items"],list)
    ):
        raise ValueError("invalid capability/evidence status")
    if any(type(evidence[x]) is not int or evidence[x]<0 for x in (
        "does_not_exist","error","not_collected"
    )):
        raise ValueError("negative or noninteger collected Item counts")
    status=evidence["status"]
    items=evidence["items"]
    if status in {"error","not_collected","not_applicable","does_not_exist"} and items:
        raise ValueError("terminal collection status cannot have trusted Items")
    names=set()
    outcomes=[]
    for item in items:
        if not isinstance(item,dict) or set(item)!={"id","outcome"} or (
            type(item["id"]) is not str or not item["id"] or item["id"] in names
        ):
            raise ValueError("duplicate/malformed collected Item identity")
        names.add(item["id"])
        result=item["outcome"]
        if type(result) is not str or result not in SIX:
            raise ValueError("unrecognized six-state typed Item result")
        if not requirement["has_state"]:
            raise ValueError("existence-only Test cannot carry comparison outcomes")
        outcomes.append(result.replace("_"," "))
    if status=="complete" and requirement["has_state"] and not items and (
        requirement["exists"] in {"none_exist","any_exist"}
    ):
        # The OVAL source helper has no definition for aggregating ZERO State
        # outcomes when existence passes. Do not invent vacuous truth: this
        # requires explicit semantic review, or a State-free Test.
        raise ValueError("empty complete State Test has unresolved aggregation semantics")
    result=evaluate_collected_object_test(
        FLAGS[status], existence=requirement["exists"],
        check=ITEM_CHECKS[requirement["items_match"]],
        item_results=outcomes if requirement["has_state"] else None,
        has_state=requirement["has_state"],
        exists=len(items),does_not_exist=evidence["does_not_exist"],
        error=evidence["error"],not_collected=evidence["not_collected"],
    )
    if result not in RESULTS:
        raise ValueError("invalid backend evaluation outcome")
    return result.replace(" ","_")


def lower_c_assessment_logic(node, assessment):
    """C vocabulary to existing A Assessment expression AST, fail closed."""
    if not isinstance(assessment,dict) or assessment.get("mode")!="automated":
        raise ValueError("automated Assessment required")
    def convert(x,depth=0):
        if depth>128 or not isinstance(x,dict) or len(x)!=1:
            raise ValueError("C expression requires one operator and bounded depth")
        op,payload=next(iter(x.items()))
        if op=="check":
            if type(payload) is not str or payload not in assessment.get("tests",{}):
                raise ValueError("missing Test reference")
            return {"test":payload}
        if op=="depends_on":
            if type(payload) is not str or payload not in assessment.get("dependencies",{}):
                raise ValueError("missing dependency reference")
            return {"assessment":payload}
        if op in C_EXPR:
            if not isinstance(payload,list) or not payload:
                raise ValueError("empty C operator list")
            return {C_EXPR[op]:[convert(v,depth+1) for v in payload]}
        if op=="not":
            return {"not":convert(payload,depth+1)}
        raise ValueError("unknown C expression operator or implicit condition")
    result=convert(node)
    sandbox=dict(assessment,evaluate=result)
    plan=compile_expression(sandbox)
    return {"source_tree":result,"plan":plan,"authoring_research_only":True,
            "collections_evaluated":False,"scanner_executed":False}


def evaluate_c_assessment_logic(lowered, leaf_results, dependency_results=None):
    if lowered.get("authoring_research_only") is not True or (
        lowered.get("collections_evaluated") is not False
    ):
        raise ValueError("not a C research logic lowering")
    return execute_supplied_results(lowered["plan"],leaf_results,dependency_results)
