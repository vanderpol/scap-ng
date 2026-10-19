#!/usr/bin/env python3
"""Refs #245: native C requirements over shared *precollected* Apache facts.

This deliberately uses the existing A/OVAL generic Item/existence result
tables. Its directive predicate rules are NEW NATIVE POLICY; they are not
faithful translations of old grep-based source Tests. No OS collector.
"""
from research_c_apache_directive_observations import select_directives
from research_c_common_evaluation import population_outcome

def evaluate_directive_requirement(observation, directive, *, expected, every_item):
    if directive not in ("session","sessioncookiename") or type(every_item) is not bool:
        raise ValueError("bounded directive and explicit Item scope required")
    if directive=="session":
        if expected!="on":
            raise ValueError("pilot Session policy only accepts On")
    elif expected!=("httponly","secure"):
        raise ValueError("pilot Cookie policy requires explicit HttpOnly and Secure tokens")
    selection=select_directives(observation,directive)
    outcomes=[]
    for item in selection["items"]:
        args=item["arguments"]
        if directive=="session":
            conforms=args.strip().lower()=="on"
        else:
            parts={x.lower() for x in args.split()}
            conforms=set(expected)<=parts
        outcomes.append({"id":item["id"],
                         "outcome":"true" if conforms else "false"})
    return {
        "outcome":population_outcome(
            {"exists":"at_least_one_exists",
             "items_match":"every" if every_item else "one_of",
             "has_state":True},
            {"capability":"c-research.apache-directive-raw-lines",
             "status":selection["status"],
             "items":outcomes,
             "does_not_exist":0,"error":0,"not_collected":0}),
        "source_population":selection["population"],
        "provenance":selection["provenance"],
        "native_policy_not_source_equivalent":True,
        "scanner_executed":False,
    }
