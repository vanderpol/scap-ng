#!/usr/bin/env python3
"""Research #235/#229: independent six-state Item/cardinality model cross-check.

Compares our proposed English-first Item phrases against a separately coded
generic OVAL 5.12.3 result-combiner model for all 10 observed Test cardinality
pairs, plus the 5 State-free collection existence modes. This is NOT scanner
runtime/evidence validation and does not prove lossless original XML conversion.
"""
from collections import Counter
from itertools import product
import argparse
import json
from pathlib import Path
from oval_result_truth_tables import (
    evaluate_collected_object_test, TRUE, FALSE, ERROR, UNKNOWN, NOT_EVALUATED, NOT_APPLICABLE,
)
from research_english_first_04_complex import ITEM_REQS, STATELESS_PRESENCE

STATES=(TRUE,FALSE,ERROR,UNKNOWN,NOT_EVALUATED,NOT_APPLICABLE)
FLAGS=("complete","incomplete","does not exist","error","not collected","not applicable")
EXISTS={"at_least_one_item_exists":"at_least_one_exists",
        "items_may_be_absent":"any_exist",
        "all_collected_items_exist":"all_exist",
        "exactly_one_item_exists":"only_one_exists"}
MATCHES={"every_collected_item":"all","some_collected_item":"at least one",
         "exactly_one_collected_item":"only one","no_collected_item":"none satisfy"}
PRESENCE={"at_least_one":"at_least_one_exists","exactly_one":"only_one_exists",
          "none":"none_exist","all_exist":"all_exist","may_be_absent":"any_exist"}

def predicate(check, observed):
    if not observed:return None  # The existing generic reference has no empty aggregation
    counts=Counter(observed)
    if check=="all":
        priority=((FALSE,FALSE),(ERROR,ERROR),(UNKNOWN,UNKNOWN),
                  (NOT_EVALUATED,NOT_EVALUATED),(TRUE,TRUE),(NOT_APPLICABLE,NOT_APPLICABLE))
    elif check=="at least one":
        priority=((TRUE,TRUE),(ERROR,ERROR),(UNKNOWN,UNKNOWN),
                  (NOT_EVALUATED,NOT_EVALUATED),(FALSE,FALSE),(NOT_APPLICABLE,NOT_APPLICABLE))
    elif check=="only one":
        if counts[TRUE]>1:return FALSE
        for x in (ERROR,UNKNOWN,NOT_EVALUATED):
            if counts[x]:return x
        if counts[TRUE]==1:return TRUE
        return FALSE if counts[FALSE] else NOT_APPLICABLE
    elif check=="none satisfy":
        priority=((TRUE,FALSE),(ERROR,ERROR),(UNKNOWN,UNKNOWN),
                  (NOT_EVALUATED,NOT_EVALUATED),(FALSE,TRUE),(NOT_APPLICABLE,NOT_APPLICABLE))
    else:raise ValueError(check)
    return next(value for key,value in priority if counts[key])

def presence(mode, n, absent, err, uncollected):
    if mode=="all_exist":
        if absent:return FALSE
        if err:return ERROR
        if uncollected:return UNKNOWN
        return TRUE if n else FALSE
    if mode=="any_exist":
        if n:return TRUE
        return ERROR if err else TRUE
    if mode=="at_least_one_exists":
        if n:return TRUE
        if err:return ERROR
        if uncollected:return UNKNOWN
        return FALSE
    if mode=="none_exist":
        if n:return FALSE
        if err:return ERROR
        if uncollected:return UNKNOWN
        return TRUE
    if mode=="only_one_exists":
        if n>=2:return FALSE
        if err:return ERROR
        if uncollected:return UNKNOWN
        return TRUE if n==1 else FALSE
    raise ValueError(mode)

def independent(flag, mode, check, values, has_state, n, absent, err, uncollected):
    if flag=="error":return ERROR
    if flag=="not collected":return UNKNOWN
    if flag=="not applicable":return NOT_APPLICABLE
    if flag=="does not exist":return TRUE if mode in ("none_exist","any_exist") else FALSE
    exists_result=presence(mode,n,absent,err,uncollected)
    if flag=="complete":
        if exists_result!=TRUE:return exists_result
        return predicate(check,values) if has_state else TRUE
    if flag!="incomplete":raise ValueError(flag)
    if mode=="none_exist" and n>=1:return FALSE
    if mode=="only_one_exists" and n>1:return FALSE
    if has_state:
        p=predicate(check,values)
        if mode=="only_one_exists":
            if n==1 and len(values)==1 and p==FALSE:return FALSE
            return UNKNOWN
        if mode=="all_exist":return UNKNOWN
        if mode in ("at_least_one_exists","any_exist") and n:
            c=Counter(values)
            if check=="all" and c[FALSE]:return FALSE
            if check=="at least one" and c[TRUE]:return TRUE
            if check=="only one" and c[TRUE]>=2:return FALSE
            if check=="none satisfy" and c[TRUE]:return FALSE
    return UNKNOWN

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output")
    opts=parser.parse_args()
    modes={}
    for source,(exist_key,match_key) in ITEM_REQS.items():
        modes[source]=(EXISTS[exist_key],MATCHES[match_key],True)
    for source,english in STATELESS_PRESENCE.items():
        modes["statefree:"+source]=(PRESENCE[english],"all",False)
    if len(modes)!=len(ITEM_REQS)+len(STATELESS_PRESENCE):raise AssertionError("Missing mode")

    tally=Counter()
    mismatches=[]
    per_mode={}
    for name,(mode,check,has_state) in modes.items():
        tested=0
        for n in range(4):
            results=product(STATES,repeat=n) if has_state else [()]
            for values in results:
                for absent,err,uncollected in product((0,1),repeat=3):
                    for flag in FLAGS:
                        args=dict(existence=mode,check=check,has_state=has_state,
                                  item_results=list(values) if has_state else None,
                                  exists=n,does_not_exist=absent,error=err,not_collected=uncollected)
                        try:
                            expected=evaluate_collected_object_test(flag,**args)
                        except (AssertionError, ValueError) as exc:
                            if not (isinstance(exc, ValueError) and "requires at least one input" in str(exc)) and not isinstance(exc, AssertionError):
                                raise
                            # The reference's aggregate_check(empty) is not defined.
                            # Never turn this corner into an invented passing result.
                            tally["unresolved_empty_reference"]+=1
                            continue
                        actual=independent(flag,mode,check,values,has_state,n,absent,err,uncollected)
                        tested+=1
                        tally["comparison_cases"]+=1
                        if expected!=actual:
                            mismatches.append(dict(name=name,flag=flag,values=values,
                                  n=n,absent=absent,err=err,uncollected=uncollected,
                                  expected=expected,actual=actual))
        per_mode[name]=tested
    if mismatches:
        raise AssertionError("Two-model discrepancy: "+json.dumps(mismatches[:12],indent=2))
    report={
        "status":"PASS: independent generic result combiner agrees for supported scenarios; NO scanner/runtime parity",
        "source_oval_result_model":"tools/oval_result_truth_tables.py",
        "source_english_first_modes":"tools/research_english_first_04_complex.py",
        "result_states":list(STATES),
        "collection_flags":list(FLAGS),
        "counts":dict(tally),
        "item_modes":len(ITEM_REQS),
        "state_free_modes":len(STATELESS_PRESENCE),
        "per_mode_cases":per_mode,
        "known_limitations":[
            "The generic reference has an undefined aggregate_check(empty) outcome for some complete collections where none_exist is true and a State remains attached; those cases are counted, not guessed.",
            "Both models operate on generic item State outcomes; they do not collect data or independently prove OVAL XML->SCAP-NG conversion, record/variable matching, scanner execution or evidence parity.",
            "Each readable phrase is interpreted through its explicit source existence and match axes, not hidden global defaults."
        ]
    }
    if opts.output:Path(opts.output).write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:report[k] for k in ("status","counts","item_modes","state_free_modes")},indent=2))

if __name__=="__main__":main()
