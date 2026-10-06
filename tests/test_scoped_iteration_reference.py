from tools.oval_result_truth_tables import (
    TRUE,
    FALSE,
    ERROR,
    UNKNOWN,
)
from tools.scoped_iteration_reference import (
    evaluate_complete_scope,
    evaluate_partial_scope,
    compact_scope_summary,
)


def test_complete_all_scope():
    result=evaluate_complete_scope(
        check_existence="at_least_one_exists",
        check="all",
        body_outcomes=[TRUE, TRUE, FALSE],
    )
    assert result["outcome"]==FALSE
    assert result["logical_complete"] is True
    assert result["population_complete"] is True


def test_zero_source_is_explicit_existence_result_not_vacuous_truth():
    required=evaluate_complete_scope(
        check_existence="at_least_one_exists",
        check="all",
        body_outcomes=[],
    )
    assert required["outcome"]==FALSE
    assert required["body_evaluated"] is False

    prohibited=evaluate_complete_scope(
        check_existence="none_exist",
        check="all",
        body_outcomes=[],
    )
    assert prohibited["outcome"]==TRUE
    assert prohibited["body_evaluated"] is False


def test_complete_error_propagates_through_scope_check():
    result=evaluate_complete_scope(
        check_existence="at_least_one_exists",
        check="all",
        body_outcomes=[TRUE, ERROR],
    )
    assert result["outcome"]==ERROR


def test_partial_all_false_is_decisive():
    result=evaluate_partial_scope(
        check_existence="at_least_one_exists",
        check="all",
        observed_body_outcomes=[TRUE, FALSE],
        observed_exists=2,
    )
    assert result["outcome"]==FALSE
    assert result["logical_complete"] is True
    assert result["population_complete"] is False


def test_partial_all_only_passes_is_not_decisive():
    result=evaluate_partial_scope(
        check_existence="at_least_one_exists",
        check="all",
        observed_body_outcomes=[TRUE, TRUE],
        observed_exists=2,
    )
    assert result["outcome"]==UNKNOWN
    assert result["logical_complete"] is False


def test_partial_at_least_one_true_is_decisive():
    result=evaluate_partial_scope(
        check_existence="at_least_one_exists",
        check="at least one",
        observed_body_outcomes=[FALSE, TRUE],
        observed_exists=2,
    )
    assert result["outcome"]==TRUE
    assert result["logical_complete"] is True
    assert result["population_complete"] is False


def test_partial_only_failures_cannot_prove_at_least_one_false():
    result=evaluate_partial_scope(
        check_existence="at_least_one_exists",
        check="at least one",
        observed_body_outcomes=[FALSE, FALSE],
        observed_exists=2,
    )
    assert result["outcome"]==UNKNOWN
    assert result["logical_complete"] is False


def test_partial_only_one_two_successes_is_decisive_false():
    result=evaluate_partial_scope(
        check_existence="at_least_one_exists",
        check="only one",
        observed_body_outcomes=[TRUE, TRUE],
        observed_exists=2,
    )
    assert result["outcome"]==FALSE
    assert result["logical_complete"] is True


def test_partial_none_satisfy_success_seen_is_decisive_false():
    result=evaluate_partial_scope(
        check_existence="at_least_one_exists",
        check="none satisfy",
        observed_body_outcomes=[FALSE, TRUE],
        observed_exists=2,
    )
    assert result["outcome"]==FALSE
    assert result["logical_complete"] is True


def test_partial_existence_only_one_two_items_is_decisive_false():
    result=evaluate_partial_scope(
        check_existence="only_one_exists",
        check="all",
        observed_body_outcomes=[TRUE, TRUE],
        observed_exists=2,
    )
    assert result["outcome"]==FALSE
    assert result["existence_outcome"]==FALSE
    assert result["logical_complete"] is True


def test_compact_summary_retains_counts_not_all_scope_records():
    summary=compact_scope_summary(
        [TRUE]*1000+[FALSE],
        retained=[
            {
                "outcome":FALSE,
                "bindings":{"user":"item-42"},
                "item_refs":["item-991"],
            }
        ],
        population_complete=True,
        evidence_complete=False,
    )
    assert summary["evaluated_scopes"]==1001
    assert summary["outcome_counts"][TRUE]==1000
    assert summary["outcome_counts"][FALSE]==1
    assert len(summary["retained_scope_evidence"])==1
    assert summary["evidence_complete"] is False
