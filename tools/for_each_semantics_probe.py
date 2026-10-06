#!/usr/bin/env python3
"""Research probes for OVAL value-set semantics versus scoped iteration.

These are semantic counterexamples and result-shape probes, not a production
evaluator. They exist to prevent unsafe rewrite rules from being introduced.
"""
from __future__ import annotations
import itertools, json

from tools.oval_result_truth_tables import (
    TRUE,
    FALSE,
    UNKNOWN,
    evaluate_collected_object_test,
    decisive_partial_check,
    aggregate_check,
    resolve_variable_reference,
    apply_variable_reference_context,
)


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


def nested_required_child_naive(scopes):
    """Demonstrate why host-language all([]) is unsafe for required children."""
    return all(all(scope["child_results"]) for scope in scopes)


def nested_required_child_explicit(scopes):
    """Illustrative native semantics when every parent requires >=1 passing child.

    This is intentionally not claimed to be OVAL lowering. It demonstrates that
    scoped iteration needs an explicit child-existence contract in addition to
    Boolean aggregation.
    """
    per_parent=[]
    for scope in scopes:
        children=list(scope["child_results"])
        per_parent.append(bool(children) and all(children))
    return all(per_parent)


def lineage_only_example():
    """Diagnostic lineage can be richer without changing semantic child truth.

    Two upstream values lead to one downstream child observation. The semantic
    child population is evaluated once; the two lineage edges explain how the
    child became reachable. This must not be confused with two scoped semantic
    relationships.
    """
    return {
        "semantic_children":[{"child":"/etc/target","pass":True}],
        "lineage_edges":[
            {"source":"config-a","child":"/etc/target"},
            {"source":"config-b","child":"/etc/target"},
        ],
    }


def bounded_failure_summary(results, maximum, *, population_complete=True):
    """Compact result/evidence probe consistent with the current NG result model."""
    values=list(results)
    failures=[i for i,v in enumerate(values) if v is False]
    aggregate=all(values)
    retained=failures[:maximum]
    return {
        "aggregate":aggregate,
        "logical_complete":population_complete or bool(failures),
        "population_complete":population_complete,
        "observed_failures":len(failures),
        "actual_failures":len(failures) if population_complete else None,
        "returned_failures":retained,
        "evidence_complete":population_complete and len(failures)<=maximum,
        "truncated_population":len(failures)>maximum or not population_complete,
    }


def incomplete_all_result(observed_item_results):
    """OVAL result for an incomplete collection with check=all."""
    vals=list(observed_item_results)
    return evaluate_collected_object_test(
        "incomplete",
        existence="at_least_one_exists",
        check="all",
        item_results=vals,
        has_state=True,
        exists=len(vals),
    )


def incomplete_at_least_one_result(observed_item_results):
    """OVAL result for an incomplete collection with check=at least one."""
    vals=list(observed_item_results)
    return evaluate_collected_object_test(
        "incomplete",
        existence="at_least_one_exists",
        check="at least one",
        item_results=vals,
        has_state=True,
        exists=len(vals),
    )


def native_partial_check_result(check, observed_item_results, *, population_complete):
    """Conservative native partial-population aggregation probe.

    This intentionally models evaluator-controlled partial population, not the
    inherited OVAL collected_object flag=incomplete contract. If evaluation
    stopped before the population was complete, only an irreversible decisive
    result may be returned; otherwise the result is unknown.
    """
    vals=list(observed_item_results)
    if population_complete:
        return aggregate_check(check, vals)
    decisive=decisive_partial_check(check, vals)
    return decisive if decisive is not None else UNKNOWN


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

    empty_var=resolve_variable_reference([])
    empty_object=apply_variable_reference_context(empty_var,"object")

    missing_child_scopes=[
        {"parent":"alice","child_results":[True]},
        {"parent":"bob","child_results":[]},
    ]

    lineage=lineage_only_example()

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
            "oval_object_var_ref_zero_values":empty_object,
            "naive_all_over_zero_iterations":all([]),
            "finding":"Zero iteration must not inherit programming-language/vacuous all semantics when migrating OVAL empty-variable behavior.",
        },
        "nested_required_child_warning":{
            "scopes":missing_child_scopes,
            "naive_nested_all":nested_required_child_naive(missing_child_scopes),
            "explicit_required_child":nested_required_child_explicit(missing_child_scopes),
            "finding":"Nested iteration needs per-scope existence semantics; Boolean aggregation alone can silently pass a parent with no required child.",
        },
        "incomplete_collection_warning":{
            "oval_all_with_only_observed_passes":incomplete_all_result([TRUE]),
            "oval_all_with_observed_failure":incomplete_all_result([FALSE]),
            "oval_at_least_one_with_observed_pass":incomplete_at_least_one_result([TRUE]),
            "oval_at_least_one_with_observed_failure":incomplete_at_least_one_result([FALSE]),
            "native_partial_at_least_one_with_observed_failure":native_partial_check_result("at least one",[FALSE],population_complete=False),
            "finding":"OVAL collected_object flag=incomplete has explicit inherited result rules that are not identical to conservative evaluator-controlled partial-population semantics. Conversion must preserve the former; native early-stop/resource semantics should not accidentally inherit it.",
        },
        "lineage_is_not_scope":{
            **lineage,
            "semantic_child_count":len(lineage["semantic_children"]),
            "lineage_edge_count":len(lineage["lineage_edges"]),
            "finding":"Diagnostic provenance may retain multiple upstream derivations without multiplying semantic child evaluations. Lineage and scoped iteration are distinct concepts.",
        },
        "bounded_results":{
            "complete":bounded_failure_summary([True,False,False,True],1,population_complete=True),
            "stopped_after_decisive_failure":bounded_failure_summary([True,False],1,population_complete=False),
            "finding":"Failure evidence can be bounded independently of truth; early decisive failure need not serialize every passing or unseen scope.",
        },
    }

    assert report["same_item_function_counterexample"]["equivalent"] is False
    assert report["var_check_is_not_loop_aggregation"]["equivalent"] is False
    assert [x["pass"] for x in scoped]==[True,False]
    assert empty_object=="does_not_exist"
    assert report["nested_required_child_warning"]["naive_nested_all"] is True
    assert report["nested_required_child_warning"]["explicit_required_child"] is False
    assert report["incomplete_collection_warning"]["oval_all_with_only_observed_passes"]==UNKNOWN
    assert report["incomplete_collection_warning"]["oval_all_with_observed_failure"]==FALSE
    assert report["incomplete_collection_warning"]["oval_at_least_one_with_observed_pass"]==TRUE
    assert report["incomplete_collection_warning"]["oval_at_least_one_with_observed_failure"]==FALSE
    assert report["incomplete_collection_warning"]["native_partial_at_least_one_with_observed_failure"]==UNKNOWN
    assert report["lineage_is_not_scope"]["semantic_child_count"]==1
    assert report["lineage_is_not_scope"]["lineage_edge_count"]==2
    print(json.dumps(report,indent=2))
    return report


if __name__=="__main__":
    run()
