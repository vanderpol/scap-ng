#!/usr/bin/env python3
"""Research probes for OVAL value-set semantics versus scoped iteration.

These are semantic counterexamples, not a production evaluator.
They exist to prevent unsafe rewrite rules from being introduced.
"""
from __future__ import annotations
import itertools, json

def oval_cartesian_product(rows, left, right):
    a=[r[left] for r in rows]
    b=[r[right] for r in rows]
    return [x*y for x,y in itertools.product(a,b)]

def bound_elementwise_product(rows, left, right):
    return [r[left]*r[right] for r in rows]

def equals_with_var_check(actual, values, check):
    comps=[actual==v for v in values]
    if check=="all":
        return all(comps)
    if check=="at least one":
        return any(comps)
    if check=="none satisfy":
        return not any(comps)
    if check=="only one":
        return sum(bool(x) for x in comps)==1
    raise ValueError(check)

def iterate_values_exist(system_values, values, aggregate):
    scoped=[v in system_values for v in values]
    if aggregate=="all":
        return all(scoped)
    if aggregate=="at least one":
        return any(scoped)
    raise ValueError(aggregate)

def run():
    rows=[
        {"item":"p1","block_size":2,"total_space":10},
        {"item":"p2","block_size":3,"total_space":20},
    ]
    cart=oval_cartesian_product(rows,"block_size","total_space")
    paired=bound_elementwise_product(rows,"block_size","total_space")

    values=["/home/a","/home/b"]
    actual="/home/a"
    var_all=equals_with_var_check(actual,values,"all")
    loop_all=iterate_values_exist({"/home/a","/home/b"},values,"all")

    shared_child={
        "parents":[
            {"user":"alice","expected_gid":100,"home":"/shared"},
            {"user":"bob","expected_gid":200,"home":"/shared"},
        ],
        "child":{"path":"/shared","actual_gid":100},
    }
    scoped=[
        {
            "user":p["user"],
            "path":p["home"],
            "pass":shared_child["child"]["actual_gid"]==p["expected_gid"],
        }
        for p in shared_child["parents"]
    ]

    report={
        "same_item_function_counterexample":{
            "source_rows":rows,
            "oval_cartesian_products":cart,
            "scoped_same_item_products":paired,
            "equivalent":sorted(cart)==sorted(paired),
            "finding":"Separate object_component projections followed by an OVAL multi-component function are not generally equivalent to same-Item scoped evaluation.",
        },
        "var_check_is_not_loop_aggregation":{
            "actual_object_value":actual,
            "variable_values":values,
            "oval_equals_var_check_all":var_all,
            "naive_iterate_each_value_then_all_exist":loop_all,
            "equivalent":var_all==loop_all,
            "finding":"Object-entity var_check quantifies comparisons for one candidate Item; it is not a request to instantiate one child Object per variable value.",
        },
        "shared_child_parent_identity":{
            "input":shared_child,
            "scoped_results":scoped,
            "flattened_child_count":1,
            "scoped_relationship_count":len(scoped),
            "finding":"One child Item can participate in multiple parent relationships with different expected values; flattening child identity cannot represent both relationship outcomes.",
        },
        "empty_source_warning":{
            "oval_object_var_ref_zero_values":"object considered not to exist",
            "naive_all_over_zero_iterations":True,
            "finding":"Zero iteration must not inherit programming-language/vacuous all semantics when migrating OVAL empty-variable behavior.",
        },
    }
    assert report["same_item_function_counterexample"]["equivalent"] is False
    assert report["var_check_is_not_loop_aggregation"]["equivalent"] is False
    assert [x["pass"] for x in scoped]==[True,False]
    print(json.dumps(report,indent=2))

if __name__=="__main__":
    run()
