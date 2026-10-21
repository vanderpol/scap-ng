#!/usr/bin/env python3
"""Pinned OVAL 5.12.3 AND/OR/ONE/XOR vs proposed 0.4 logical vocabulary.

OVAL source schema declares four logical operators AND, OR, ONE, XOR on both
Test.state_operator and State.operator, distinct from Test.check
(all, at least one, only one, none satisfy) and check_existence.

The independent proposed-expression model below is intentionally separate
from the existing OVAL reference combiner. It does NOT implement scanner
collection or certify user-authored 0.4 grammar. Refs #248 #239.
"""
from __future__ import annotations
from collections import Counter

RESULTS=("true","false","error","unknown","not evaluated","not applicable")
OPERATORS={"and":"AND","or":"OR","one":"ONE","xor":"XOR"}
ITEM_QUANTIFIERS={"all":"all","one_or_more":"at least one",
                  "exactly_one":"only one","none":"none satisfy"}


def candidate_logic(operator, results):
    values=list(results)
    if not values or any(value not in RESULTS for value in values):
        raise ValueError("Logical operators need at least one valid six-state result")
    if operator not in OPERATORS:
        raise ValueError("No 'any' or 'all' logical aliases: choose AND/OR/ONE/XOR")
    cnt=Counter(values)
    t,f=cnt["true"],cnt["false"]
    err,unk,nev=cnt["error"],cnt["unknown"],cnt["not evaluated"]
    na=cnt["not applicable"]
    if operator=="and" and f:
        return "false"
    if operator=="or" and t:
        return "true"
    if operator=="one" and t>1:
        return "false"
    if err:return "error"
    if unk:return "unknown"
    if nev:return "not evaluated"
    if operator=="and":
        return "true" if t else "not applicable"
    if operator=="or":
        return "false" if f else "not applicable"
    if operator=="one":
        if t==1:return "true"
        return "false" if f else "not applicable"
    # OVAL XOR means an odd number of true inputs, NOT exactly one.
    if t or f:return "true" if t%2 else "false"
    if na:return "not applicable"
    raise AssertionError("Unknown logical combination")


def candidate_item_quantifier(quantifier, results):
    values=list(results)
    if not values or any(value not in RESULTS for value in values):
        raise ValueError("Item matching quantifier needs nonempty collected results")
    if quantifier not in ITEM_QUANTIFIERS:
        raise ValueError("No item OR: use matching_items quantifier")
    c=Counter(values)
    if quantifier=="all":
        if c["false"]:return "false"
    elif quantifier=="one_or_more":
        if c["true"]:return "true"
    elif quantifier=="exactly_one":
        if c["true"]>1:return "false"
    elif quantifier=="none":
        if c["true"]:return "false"
    for status in ("error","unknown","not evaluated"):
        if c[status]:return status
    if quantifier=="all":
        return "true" if c["true"] else "not applicable"
    if quantifier=="one_or_more":
        return "false" if c["false"] else "not applicable"
    if quantifier=="exactly_one":
        if c["true"]==1:return "true"
        return "false" if c["false"] else "not applicable"
    if quantifier=="none":
        return "true" if c["false"] else "not applicable"
    raise AssertionError(quantifier)


def scoped_state_item(field_results_by_state, *,
                      fields_operators, state_operator):
    """Every list of field results is ONE OVAL State on ONE Item.

    The outer state operator combines complete States on the same Item,
    not individual field hits from different States or collected Items.
    """
    if len(field_results_by_state)!=len(fields_operators):
        raise ValueError("State/operator mismatch")
    states=[candidate_logic(op,fields)
            for fields,op in zip(field_results_by_state,fields_operators)]
    return candidate_logic(state_operator,states)


def checked_items(item_state_results, *,
                  fields_operators_by_item, state_operator,
                  matching_items):
    """For already-existing, complete Items only; existence evaluated elsewhere."""
    outcomes=[]
    for states,ops in zip(item_state_results,fields_operators_by_item):
        outcomes.append(scoped_state_item(states,
                       fields_operators=ops,state_operator=state_operator))
    if len(outcomes)!=len(item_state_results):
        raise ValueError("Item field/operator count mismatch")
    return candidate_item_quantifier(matching_items,outcomes)
