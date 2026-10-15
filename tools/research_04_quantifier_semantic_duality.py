#!/usr/bin/env python3
"""0.4 semantic rewrite checks, using pinned OVAL 5.12.3 reference result tables.

Proves ONLY the aggregation-level identity:
  none_satisfy(P) == all_satisfy(not P)
on nonempty populations with six-valued truth. Does not assume every native
comparison is safely invertible (regex, WMI, record, absence, sets, errors).
Also exhibits counterexamples for tempting non-equivalent rewrites.
"""
import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path
from oval_result_truth_tables import (
    TRUE,FALSE,ERROR,UNKNOWN,NOT_EVALUATED,NOT_APPLICABLE,
    aggregate_check,aggregate_existence,evaluate_collected_object_test,
    evaluate_record_field,
)
OUTCOMES=(TRUE,FALSE,ERROR,UNKNOWN,NOT_EVALUATED,NOT_APPLICABLE)
INVERT={TRUE:FALSE,FALSE:TRUE,ERROR:ERROR,UNKNOWN:UNKNOWN,
        NOT_EVALUATED:NOT_EVALUATED,NOT_APPLICABLE:NOT_APPLICABLE}
EXISTENCE={"one_or_more":"at_least_one_exists","one":"only_one_exists",
           "all":"all_exist","optional":"any_exist","none":"none_exist"}
MATCH={"all":"all","one":"only one","one_or_more":"at least one","none":"none satisfy"}

def prove_check_duality():
    examined=0
    for n in range(1,5):
        for row in product(OUTCOMES,repeat=n):
            before=aggregate_check("none satisfy",row)
            after=aggregate_check("all",map(INVERT.__getitem__,row))
            examined+=1
            if before!=after:
                raise AssertionError(f"OVAL check duality counterexample: {row} {before} != {after}")
    return examined

def prove_contextual_duality():
    # Holds when State evaluation can truly produce a complemented six-valued
    # result for every collected Item, and Object collection is unchanged.
    cases=0
    for existence in ("all_exist","any_exist","at_least_one_exists","only_one_exists"):
        for flag in ("complete","incomplete"):
            for n in range(1,4):
                for row in product(OUTCOMES,repeat=n):
                    opts=dict(existence=existence,flag=flag,has_state=True,exists=n)
                    before=evaluate_collected_object_test(item_results=row,
                        check="none satisfy",**opts)
                    after=evaluate_collected_object_test(
                        item_results=tuple(INVERT[r] for r in row),
                        check="all",**opts)
                    cases+=1
                    if before!=after:
                        raise AssertionError(
                            f"Check inversion not context-equivalent: {opts} {row} {before} {after}"
                        )
    return cases

def prove_single_item_check_equivalence():
    """With exactly one collected Item, all and only-one matching coincide.

    More generally, one-exists gates two Items before State matching matters.
    Check incomplete/error flags so no unproven Boolean-only shortcut leaks.
    """
    examined=0
    for flag in ("complete","incomplete"):
        for n in (1,2,3):
            for row in product(OUTCOMES,repeat=n):
                opts=dict(flag=flag,existence="only_one_exists",exists=n,
                          has_state=True,item_results=row)
                before=evaluate_collected_object_test(check="all",**opts)
                after=evaluate_collected_object_test(check="only one",**opts)
                examined+=1
                if before!=after:
                    raise AssertionError(
                        f"one/all and one/one differ under {opts}: {before} {after}"
                    )
    for flag in ("error","not collected","not applicable","does not exist"):
        a=evaluate_collected_object_test(flag,existence="only_one_exists",
                                         check="all",has_state=True)
        b=evaluate_collected_object_test(flag,existence="only_one_exists",
                                         check="only one",has_state=True)
        examined+=1
        if a!=b:
            raise AssertionError(f"Top-level flag mismatch {flag}: {a} {b}")
    return examined


def prove_state_free_irrelevant_check():
    """State-free Test match aggregation is unreachable in reference model."""
    examined=0
    for exists in range(4):
        for existence in EXISTENCE.values():
            for flag in ("complete","incomplete","does not exist",
                         "error","not collected","not applicable"):
                a=evaluate_collected_object_test(flag,existence=existence,
                    check="all",has_state=False,exists=exists)
                for check in ("all","at least one","only one","none satisfy"):
                    b=evaluate_collected_object_test(flag,existence=existence,
                        check=check,has_state=False,exists=exists)
                    examined+=1
                    if a!=b:
                        raise AssertionError(
                            f"State-free check affected outcome: {existence} {flag} {exists} {check}"
                        )
    return examined


def counterexamples():
    # "exactly one exists" cannot be reduced to at least one exists and
    # exactly one satisfying State (the latter accepts extra nonmatching Items).
    many=(TRUE,FALSE)
    test_one=evaluate_collected_object_test(
        "complete",existence="only_one_exists",check="all",
        item_results=many,exists=2)
    test_some_one=evaluate_collected_object_test(
        "complete",existence="at_least_one_exists",check="only one",
        item_results=many,exists=2)
    if test_one==test_some_one:
        raise AssertionError("Expected exact-one counterexample was lost")
    # Neither 'none matching' nor 'any matching' can mean zero Items collected.
    some=aggregate_check("none satisfy",(FALSE,))
    absent=aggregate_existence("none_exist",exists=1)
    if some==absent:
        raise AssertionError("Expected field absence vs none satisfy counterexample lost")
    # Incomplete, error and unknown must retain nonboolean meaning.
    example_with_error=aggregate_check("none satisfy",(FALSE,ERROR))
    example_wrong_boolean=TRUE
    if example_with_error==example_wrong_boolean:
        raise AssertionError("Error propagation counterexample lost")
    missing_record_field=evaluate_record_field("productstate",(),entity_check="all")
    if missing_record_field!=ERROR:
        raise AssertionError("Record field absence must remain ERROR, not be treated as none_exist")
    # Plain comparison operator negation is NOT guaranteed to be a dual:
    # pattern_match regex has no standard 0.3 not_pattern_match inverse.
    return {
        "exactly_one_exists_vs_exactly_one_matches":{
            "case":"Two Items exist, one State passes, one State fails",
            "original_only_one_exists_all_match":test_one,
            "reduced_at_least_one_exists_one_match":test_some_one,
            "source_equivalent":False,
        },
        "none_entities_exist_vs_none_entities_match":{
            "case":"One field entity exists but does not match prohibited value",
            "original_none_exist":absent,"none_satisfy_comparison":some,
            "source_equivalent":False,
        },
        "naive_negative_aggregation_discards_error":{
            "case":"One State result false and another error",
            "original_none_satisfy":example_with_error,
            "incorrect_boolean_all_not":example_wrong_boolean,
            "source_equivalent":False,
        },
        "record_missing_nested_subfield_is_not_absence_success":{
            "case":"Expected structured record field has zero observed values",
            "original_record_field_result":missing_record_field,
            "incorrect_flattened_absence_result":"true",
            "source_equivalent":False,
            "proof_needed":"Preserve record field presence/error behavior and nested record quantifier levels",
        },
        "zero_observed_items_with_state":{
            "case":"collected_object complete, existence none, zero Items, State present",
            "reference_test_with_state":"undefined by reference helper: aggregation requires nonempty State results",
            "safe_rewrite_to_state_free":False,
            "proof_needed":"OVAL 5.12.3 schema/ref evaluator corpus plus actual scanner on zero/error/incomplete cases",
        },
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    r={
        "source":"SCAP-NG pinned OVAL 5.12.3 truth-table helpers",
        "nonempty_aggregation_case_count":prove_check_duality(),
        "nonempty_test_context_case_count":prove_contextual_duality(),
        "exact_one_existing_item_all_vs_one_matching_case_count":prove_single_item_check_equivalence(),
        "state_free_matching_irrelevance_case_count":prove_state_free_irrelevant_check(),
        "counterexamples":counterexamples(),
        "limitations":[
            "Pure result-level duality proves no native comparator inversion: no implicit regex inversion, datatype coercion, or record negation.",
            "Zero-Item State-bearing none-existence and incomplete collection require differential vendor evaluator checks; source semantic rewrite not authorized.",
            "Exact quantifier pair-to-name lowering is source-equivalent without changing any OVAL Test method.",
            "No shellcommand/manual fallback is required just because a pair is uncommon; keep automated typed check.",
        ],
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
    print(json.dumps(r,indent=2,sort_keys=True))
if __name__=="__main__":
    main()
