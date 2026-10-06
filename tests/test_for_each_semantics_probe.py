from tools.for_each_semantics_probe import (
    run,
    oval_cartesian_product,
    bound_elementwise_product,
    equals_with_var_check,
    iterate_values_exist,
    nested_required_child_naive,
    nested_required_child_explicit,
    lineage_only_example,
    bounded_failure_summary,
    incomplete_all_result,
    incomplete_at_least_one_result,
    native_partial_check_result,
)
from tools.oval_result_truth_tables import TRUE, FALSE, UNKNOWN


def test_cartesian_not_same_item_pairing():
    rows=[{"a":2,"b":10},{"a":3,"b":20}]
    assert oval_cartesian_product(rows,"a","b")==[20,40,30,60]
    assert bound_elementwise_product(rows,"a","b")==[20,60]


def test_var_check_all_is_not_iteration_all():
    vals=["/a","/b"]
    assert equals_with_var_check("/a",vals,"all") is False
    assert iterate_values_exist({"/a","/b"},vals,"all") is True


def test_missing_required_child_cannot_use_vacuous_all():
    scopes=[
        {"parent":"a","child_results":[True]},
        {"parent":"b","child_results":[]},
    ]
    assert nested_required_child_naive(scopes) is True
    assert nested_required_child_explicit(scopes) is False


def test_incomplete_population_decisiveness_matches_oval():
    assert incomplete_all_result([TRUE])==UNKNOWN
    assert incomplete_all_result([FALSE])==FALSE
    assert incomplete_at_least_one_result([TRUE])==TRUE
    # OVAL 5.12.3 explicitly permits false here for collected_object flag=incomplete.
    assert incomplete_at_least_one_result([FALSE])==FALSE
    # Native evaluator-controlled partial population is a different condition.
    assert native_partial_check_result("at least one",[FALSE],population_complete=False)==UNKNOWN


def test_lineage_does_not_multiply_semantic_children():
    example=lineage_only_example()
    assert len(example["semantic_children"])==1
    assert len(example["lineage_edges"])==2


def test_evidence_cap_does_not_change_truth():
    complete=bounded_failure_summary([True,False,False,True],1,population_complete=True)
    assert complete["aggregate"] is False
    assert complete["actual_failures"]==2
    assert complete["returned_failures"]==[1]
    assert complete["truncated_population"] is True

    early=bounded_failure_summary([True,False],1,population_complete=False)
    assert early["aggregate"] is False
    assert early["logical_complete"] is True
    assert early["population_complete"] is False
    assert early["actual_failures"] is None


def test_probe_suite():
    report=run()
    assert report["empty_source_warning"]["oval_object_var_ref_zero_values"]=="does_not_exist"
