#!/usr/bin/env python3
"""Independent truth-table checks derived from pinned OVAL 5.12.3 XSD appinfo."""
import unittest

from oval_result_truth_tables import (
    TRUE, FALSE, ERROR, UNKNOWN, NOT_EVALUATED, NOT_APPLICABLE,
    aggregate_check, aggregate_operator, aggregate_existence,
    evaluate_collected_object_test, evaluate_missing_collected_object_record,
    aggregate_many_to_many, aggregate_state, aggregate_item_states,
    resolve_variable_reference, apply_variable_reference_context,
    evaluate_variable_entity_reference, combine_set_flags, SET_FLAGS,
    decisive_partial_check, decisive_partial_existence,
    NO_VALUES, apply_filter_state_result, select_collected_object_instance,
)


class CheckEnumerationTruthTables(unittest.TestCase):
    def test_all_precedence(self):
        self.assertEqual(aggregate_check("all", [TRUE, TRUE]), TRUE)
        self.assertEqual(aggregate_check("all", [TRUE, FALSE, ERROR]), FALSE)
        self.assertEqual(aggregate_check("all", [TRUE, ERROR, UNKNOWN]), ERROR)
        self.assertEqual(aggregate_check("all", [TRUE, UNKNOWN, NOT_EVALUATED]), UNKNOWN)
        self.assertEqual(aggregate_check("all", [TRUE, NOT_EVALUATED]), NOT_EVALUATED)
        self.assertEqual(aggregate_check("all", [NOT_APPLICABLE]), NOT_APPLICABLE)

    def test_at_least_one_precedence(self):
        self.assertEqual(aggregate_check("at least one", [FALSE, TRUE, ERROR]), TRUE)
        self.assertEqual(aggregate_check("at least one", [FALSE, ERROR, UNKNOWN]), ERROR)
        self.assertEqual(aggregate_check("at least one", [FALSE, UNKNOWN]), UNKNOWN)
        self.assertEqual(aggregate_check("at least one", [FALSE, NOT_EVALUATED]), NOT_EVALUATED)
        self.assertEqual(aggregate_check("at least one", [FALSE, FALSE]), FALSE)
        self.assertEqual(aggregate_check("at least one", [NOT_APPLICABLE]), NOT_APPLICABLE)

    def test_only_one(self):
        self.assertEqual(aggregate_check("only one", [TRUE, FALSE]), TRUE)
        self.assertEqual(aggregate_check("only one", [TRUE, TRUE, ERROR]), FALSE)
        self.assertEqual(aggregate_check("only one", [FALSE, ERROR]), ERROR)
        self.assertEqual(aggregate_check("only one", [FALSE, UNKNOWN]), UNKNOWN)
        self.assertEqual(aggregate_check("only one", [FALSE, NOT_EVALUATED]), NOT_EVALUATED)
        self.assertEqual(aggregate_check("only one", [FALSE, FALSE]), FALSE)
        self.assertEqual(aggregate_check("only one", [NOT_APPLICABLE]), NOT_APPLICABLE)

    def test_none_satisfy(self):
        self.assertEqual(aggregate_check("none satisfy", [FALSE, FALSE]), TRUE)
        self.assertEqual(aggregate_check("none satisfy", [TRUE, ERROR]), FALSE)
        self.assertEqual(aggregate_check("none satisfy", [FALSE, ERROR]), ERROR)
        self.assertEqual(aggregate_check("none satisfy", [FALSE, UNKNOWN]), UNKNOWN)
        self.assertEqual(aggregate_check("none satisfy", [FALSE, NOT_EVALUATED]), NOT_EVALUATED)
        self.assertEqual(aggregate_check("none satisfy", [NOT_APPLICABLE]), NOT_APPLICABLE)


class OperatorTruthTables(unittest.TestCase):
    def test_and_or_one(self):
        self.assertEqual(aggregate_operator("AND", [TRUE, FALSE, ERROR]), FALSE)
        self.assertEqual(aggregate_operator("OR", [FALSE, TRUE, ERROR]), TRUE)
        self.assertEqual(aggregate_operator("ONE", [TRUE, FALSE]), TRUE)
        self.assertEqual(aggregate_operator("ONE", [TRUE, TRUE, UNKNOWN]), FALSE)

    def test_xor(self):
        self.assertEqual(aggregate_operator("XOR", [TRUE, FALSE, FALSE]), TRUE)
        self.assertEqual(aggregate_operator("XOR", [TRUE, TRUE, FALSE]), FALSE)
        self.assertEqual(aggregate_operator("XOR", [TRUE, ERROR]), ERROR)
        self.assertEqual(aggregate_operator("XOR", [TRUE, UNKNOWN]), UNKNOWN)
        self.assertEqual(aggregate_operator("XOR", [TRUE, NOT_EVALUATED]), NOT_EVALUATED)
        self.assertEqual(aggregate_operator("XOR", [NOT_APPLICABLE]), NOT_APPLICABLE)


class ExistenceTruthTables(unittest.TestCase):
    def test_all_exist(self):
        self.assertEqual(aggregate_existence("all_exist", exists=1), TRUE)
        self.assertEqual(aggregate_existence("all_exist"), FALSE)
        self.assertEqual(aggregate_existence("all_exist", exists=2, does_not_exist=1, error=1), FALSE)
        self.assertEqual(aggregate_existence("all_exist", error=1), ERROR)
        self.assertEqual(aggregate_existence("all_exist", not_collected=1), UNKNOWN)

    def test_any_exist(self):
        self.assertEqual(aggregate_existence("any_exist"), TRUE)
        self.assertEqual(aggregate_existence("any_exist", does_not_exist=3, not_collected=2), TRUE)
        self.assertEqual(aggregate_existence("any_exist", exists=1, error=2), TRUE)
        self.assertEqual(aggregate_existence("any_exist", error=1), ERROR)

    def test_at_least_one_exists(self):
        self.assertEqual(aggregate_existence("at_least_one_exists", exists=1, error=1), TRUE)
        self.assertEqual(aggregate_existence("at_least_one_exists"), FALSE)
        self.assertEqual(aggregate_existence("at_least_one_exists", error=1), ERROR)
        self.assertEqual(aggregate_existence("at_least_one_exists", not_collected=1), UNKNOWN)

    def test_none_exist(self):
        self.assertEqual(aggregate_existence("none_exist"), TRUE)
        self.assertEqual(aggregate_existence("none_exist", exists=1, error=1), FALSE)
        self.assertEqual(aggregate_existence("none_exist", error=1), ERROR)
        self.assertEqual(aggregate_existence("none_exist", not_collected=1), UNKNOWN)

    def test_only_one_exists(self):
        self.assertEqual(aggregate_existence("only_one_exists", exists=1), TRUE)
        self.assertEqual(aggregate_existence("only_one_exists"), FALSE)
        self.assertEqual(aggregate_existence("only_one_exists", exists=2, error=1), FALSE)
        self.assertEqual(aggregate_existence("only_one_exists", error=1), ERROR)
        self.assertEqual(aggregate_existence("only_one_exists", not_collected=1), UNKNOWN)

    def test_rejects_unspecified_empty_boolean_aggregation(self):
        with self.assertRaises(ValueError):
            aggregate_check("all", [])
        with self.assertRaises(ValueError):
            aggregate_operator("AND", [])


class CollectedObjectIdentitySemantics(unittest.TestCase):
    def test_selects_exact_id_version_variable_instance(self):
        records = [
            {"id": "obj-1", "version": 1, "variable_instance": 1, "flag": "complete"},
            {"id": "obj-1", "version": 1, "variable_instance": 2, "flag": "complete"},
        ]
        self.assertEqual(
            select_collected_object_instance(
                records,
                object_id="obj-1",
                version=1,
                variable_instance=2,
            )["variable_instance"],
            2,
        )

    def test_missing_exact_identity_is_none(self):
        self.assertIsNone(
            select_collected_object_instance(
                [{"id": "obj-1", "version": 1, "variable_instance": 1}],
                object_id="obj-1",
                version=1,
                variable_instance=2,
            )
        )

    def test_duplicate_exact_identity_is_rejected(self):
        records = [
            {"id": "obj-1", "version": 1, "variable_instance": 1},
            {"id": "obj-1", "version": 1, "variable_instance": 1},
        ]
        with self.assertRaises(ValueError):
            select_collected_object_instance(
                records,
                object_id="obj-1",
                version=1,
                variable_instance=1,
            )

    def test_default_variable_instance_is_one(self):
        record = {"id": "obj-1", "version": 1, "flag": "complete"}
        self.assertIs(
            select_collected_object_instance(
                [record],
                object_id="obj-1",
                version=1,
            ),
            record,
        )


class CollectedObjectControlFlow(unittest.TestCase):
    def test_direct_flags_override_normal_evaluation(self):
        self.assertEqual(evaluate_collected_object_test("error", existence="at_least_one_exists"), ERROR)
        self.assertEqual(evaluate_collected_object_test("not collected", existence="at_least_one_exists"), UNKNOWN)
        self.assertEqual(evaluate_collected_object_test("not applicable", existence="at_least_one_exists"), NOT_APPLICABLE)

    def test_does_not_exist_uses_only_existence_mode(self):
        self.assertEqual(evaluate_collected_object_test("does not exist", existence="none_exist"), TRUE)
        self.assertEqual(evaluate_collected_object_test("does not exist", existence="any_exist"), TRUE)
        for mode in ("all_exist", "at_least_one_exists", "only_one_exists"):
            with self.subTest(mode=mode):
                self.assertEqual(evaluate_collected_object_test("does not exist", existence=mode), FALSE)

    def test_complete_short_circuits_failed_existence(self):
        self.assertEqual(
            evaluate_collected_object_test(
                "complete",
                existence="at_least_one_exists",
                exists=0,
                has_state=True,
                item_results=[TRUE],
            ),
            FALSE,
        )
        self.assertEqual(
            evaluate_collected_object_test(
                "complete",
                existence="none_exist",
                exists=0,
                has_state=False,
            ),
            TRUE,
        )

    def test_complete_applies_check_only_after_existence_true(self):
        self.assertEqual(
            evaluate_collected_object_test(
                "complete",
                existence="at_least_one_exists",
                exists=2,
                check="all",
                item_results=[TRUE, FALSE],
            ),
            FALSE,
        )
        self.assertEqual(
            evaluate_collected_object_test(
                "complete",
                existence="at_least_one_exists",
                exists=2,
                check="at least one",
                item_results=[FALSE, TRUE],
            ),
            TRUE,
        )

    def test_incomplete_is_unknown_unless_evidence_is_decisive(self):
        self.assertEqual(
            evaluate_collected_object_test(
                "incomplete",
                existence="at_least_one_exists",
                exists=1,
                check="all",
                item_results=[TRUE],
            ),
            UNKNOWN,
        )
        self.assertEqual(
            evaluate_collected_object_test(
                "incomplete",
                existence="none_exist",
                exists=1,
                has_state=False,
            ),
            FALSE,
        )
        self.assertEqual(
            evaluate_collected_object_test(
                "incomplete",
                existence="only_one_exists",
                exists=2,
                has_state=False,
            ),
            FALSE,
        )
        self.assertEqual(
            evaluate_collected_object_test(
                "incomplete",
                existence="at_least_one_exists",
                exists=2,
                check="all",
                item_results=[TRUE, FALSE],
            ),
            FALSE,
        )
        self.assertEqual(
            evaluate_collected_object_test(
                "incomplete",
                existence="at_least_one_exists",
                exists=2,
                check="at least one",
                item_results=[FALSE, TRUE],
            ),
            TRUE,
        )

    def test_missing_matching_collected_object_record_is_unknown(self):
        self.assertEqual(evaluate_missing_collected_object_record(), UNKNOWN)

    def test_invalid_flag_rejected(self):
        with self.assertRaises(ValueError):
            evaluate_collected_object_test("mystery", existence="at_least_one_exists")


class EarlyTerminationSemantics(unittest.TestCase):
    def test_check_quantifiers_only_stop_on_irreversible_outcomes(self):
        self.assertEqual(decisive_partial_check("all", [TRUE, FALSE]), FALSE)
        self.assertIsNone(decisive_partial_check("all", [TRUE, TRUE]))

        self.assertEqual(decisive_partial_check("at least one", [FALSE, TRUE]), TRUE)
        self.assertIsNone(decisive_partial_check("at least one", [FALSE, FALSE]))

        self.assertEqual(decisive_partial_check("only one", [TRUE, TRUE]), FALSE)
        self.assertIsNone(decisive_partial_check("only one", [TRUE]))

        self.assertEqual(decisive_partial_check("none satisfy", [FALSE, TRUE]), FALSE)
        self.assertIsNone(decisive_partial_check("none satisfy", [FALSE, FALSE]))

    def test_existence_quantifiers_only_stop_on_irreversible_outcomes(self):
        self.assertEqual(decisive_partial_existence("at_least_one_exists", exists=1), TRUE)
        self.assertIsNone(decisive_partial_existence("at_least_one_exists", exists=0))

        self.assertEqual(decisive_partial_existence("none_exist", exists=1), FALSE)
        self.assertIsNone(decisive_partial_existence("none_exist", exists=0))

        self.assertEqual(decisive_partial_existence("only_one_exists", exists=2), FALSE)
        self.assertIsNone(decisive_partial_existence("only_one_exists", exists=1))

        self.assertIsNone(decisive_partial_existence("all_exist", exists=1))
        self.assertEqual(decisive_partial_existence("any_exist", exists=1), TRUE)
        self.assertIsNone(decisive_partial_existence("any_exist", exists=0))

    def test_error_like_observations_do_not_create_new_shortcuts(self):
        self.assertIsNone(decisive_partial_check("all", [TRUE, ERROR]))
        self.assertIsNone(decisive_partial_check("at least one", [FALSE, UNKNOWN]))

    def test_every_check_shortcut_is_stable_under_additional_results(self):
        cases = (
            ("all", [FALSE], FALSE),
            ("at least one", [TRUE], TRUE),
            ("only one", [TRUE, TRUE], FALSE),
            ("none satisfy", [TRUE], FALSE),
        )
        future_results = (TRUE, FALSE, ERROR, UNKNOWN, NOT_EVALUATED, NOT_APPLICABLE)
        for check, observed, expected in cases:
            self.assertEqual(decisive_partial_check(check, observed), expected)
            for first in future_results:
                with self.subTest(check=check, suffix=(first,)):
                    self.assertEqual(aggregate_check(check, observed + [first]), expected)
                for second in future_results:
                    with self.subTest(check=check, suffix=(first, second)):
                        self.assertEqual(
                            aggregate_check(check, observed + [first, second]),
                            expected,
                        )

    def test_every_existence_shortcut_is_stable_under_additional_statuses(self):
        cases = (
            ("at_least_one_exists", 1, TRUE),
            ("any_exist", 1, TRUE),
            ("none_exist", 1, FALSE),
            ("only_one_exists", 2, FALSE),
        )
        future_statuses = ("exists", "does_not_exist", "error", "not_collected")
        for mode, starting_exists, expected in cases:
            self.assertEqual(
                decisive_partial_existence(mode, exists=starting_exists),
                expected,
            )
            for status in future_statuses:
                counts = {
                    "exists": starting_exists,
                    "does_not_exist": 0,
                    "error": 0,
                    "not_collected": 0,
                }
                counts[status] += 1
                with self.subTest(mode=mode, status=status):
                    self.assertEqual(aggregate_existence(mode, **counts), expected)


class FilterStateSelectionSemantics(unittest.TestCase):
    def test_default_exclude_behavior_for_boolean_results(self):
        self.assertFalse(apply_filter_state_result(None, TRUE))
        self.assertTrue(apply_filter_state_result(None, FALSE))

    def test_include_behavior_for_boolean_results(self):
        self.assertTrue(apply_filter_state_result("include", TRUE))
        self.assertFalse(apply_filter_state_result("include", FALSE))

    def test_non_boolean_results_are_not_silently_coerced(self):
        for result in (ERROR, UNKNOWN, NOT_EVALUATED, NOT_APPLICABLE):
            with self.subTest(result=result):
                with self.assertRaises(NotImplementedError):
                    apply_filter_state_result("exclude", result)



class SetFlagPropagation(unittest.TestCase):
    def test_union_representative_cases(self):
        self.assertEqual(combine_set_flags("UNION", "complete", "does_not_exist"), "complete")
        self.assertEqual(combine_set_flags("UNION", "complete", "incomplete"), "incomplete")
        self.assertEqual(combine_set_flags("UNION", "not_collected", "not_applicable"), "not_collected")

    def test_intersection_representative_cases(self):
        self.assertEqual(combine_set_flags("INTERSECTION", "error", "does_not_exist"), "does_not_exist")
        self.assertEqual(combine_set_flags("INTERSECTION", "complete", "not_collected"), "not_collected")
        self.assertEqual(combine_set_flags("INTERSECTION", "complete", "not_applicable"), "complete")

    def test_complement_is_order_sensitive(self):
        self.assertEqual(combine_set_flags("COMPLEMENT", "complete", "does_not_exist"), "complete")
        self.assertEqual(combine_set_flags("COMPLEMENT", "does_not_exist", "complete"), "does_not_exist")
        self.assertEqual(combine_set_flags("COMPLEMENT", "complete", "not_applicable"), "error")

    def test_every_table_cell_produces_known_flag(self):
        for operator in ("UNION", "INTERSECTION", "COMPLEMENT"):
            for left in SET_FLAGS:
                for right in SET_FLAGS:
                    with self.subTest(operator=operator, left=left, right=right):
                        self.assertIn(combine_set_flags(operator, left, right), SET_FLAGS)

    def test_invalid_inputs_rejected(self):
        with self.assertRaises(ValueError):
            combine_set_flags("XOR", "complete", "complete")
        with self.assertRaises(ValueError):
            combine_set_flags("UNION", "mystery", "complete")


class VariableReferenceSemantics(unittest.TestCase):
    def test_zero_values_remain_distinct_until_reference_context(self):
        self.assertEqual(
            resolve_variable_reference([]),
            {"status": NO_VALUES, "values": []},
        )

    def test_zero_values_object_reference_means_does_not_exist(self):
        result = resolve_variable_reference([])
        self.assertEqual(
            apply_variable_reference_context(result, "object"),
            "does_not_exist",
        )

    def test_zero_values_state_reference_means_error(self):
        result = resolve_variable_reference([])
        self.assertEqual(
            apply_variable_reference_context(result, "state"),
            ERROR,
        )

    def test_values_are_preserved(self):
        self.assertEqual(
            resolve_variable_reference(["a", "b"]),
            {"status": TRUE, "values": ["a", "b"]},
        )

    def test_empty_string_is_a_real_value(self):
        self.assertEqual(
            resolve_variable_reference([""]),
            {"status": TRUE, "values": [""]},
        )

    def test_empty_variable_is_not_empty_string(self):
        zero = resolve_variable_reference([])
        sentinel = resolve_variable_reference([""])
        self.assertEqual(zero["status"], NO_VALUES)
        self.assertEqual(sentinel["status"], TRUE)
        self.assertNotEqual(zero["values"], sentinel["values"])


class VariableStatusPropagation(unittest.TestCase):
    def test_error_short_circuits_quantifiers(self):
        self.assertEqual(
            evaluate_variable_entity_reference(
                variable_status=ERROR,
                var_check="at least one",
                entity_check="at least one",
                comparison_rows=[[TRUE]],
            ),
            ERROR,
        )

    def test_unknown_short_circuits_quantifiers(self):
        self.assertEqual(
            evaluate_variable_entity_reference(
                variable_status=UNKNOWN,
                var_check="all",
                entity_check="all",
                comparison_rows=[[TRUE, TRUE]],
            ),
            UNKNOWN,
        )

    def test_resolved_variable_uses_existing_quantifier_order(self):
        self.assertEqual(
            evaluate_variable_entity_reference(
                variable_status=TRUE,
                var_check="at least one",
                entity_check="all",
                comparison_rows=[[TRUE, FALSE], [TRUE, FALSE]],
            ),
            TRUE,
        )

    def test_resolved_variable_requires_comparison_rows(self):
        with self.assertRaises(ValueError):
            evaluate_variable_entity_reference(
                variable_status=TRUE,
                var_check="all",
                entity_check="all",
            )


class StateEntityAggregationOrder(unittest.TestCase):
    def test_var_check_applies_before_entity_check(self):
        rows = [
            [TRUE, FALSE],
            [FALSE, FALSE],
        ]
        self.assertEqual(
            aggregate_many_to_many(
                var_check="at least one",
                entity_check="all",
                comparison_rows=rows,
            ),
            FALSE,
        )
        self.assertEqual(
            aggregate_many_to_many(
                var_check="at least one",
                entity_check="at least one",
                comparison_rows=rows,
            ),
            TRUE,
        )

    def test_entity_and_variable_quantifiers_are_not_interchangeable(self):
        rows = [
            [TRUE, FALSE],
            [TRUE, FALSE],
        ]
        self.assertEqual(
            aggregate_many_to_many(
                var_check="all",
                entity_check="at least one",
                comparison_rows=rows,
            ),
            FALSE,
        )
        self.assertEqual(
            aggregate_many_to_many(
                var_check="at least one",
                entity_check="all",
                comparison_rows=rows,
            ),
            TRUE,
        )

    def test_error_precedence_is_applied_at_each_scope(self):
        rows = [
            [TRUE, ERROR],
            [FALSE, FALSE],
        ]
        self.assertEqual(
            aggregate_many_to_many(
                var_check="all",
                entity_check="all",
                comparison_rows=rows,
            ),
            FALSE,
        )
        self.assertEqual(
            aggregate_many_to_many(
                var_check="all",
                entity_check="at least one",
                comparison_rows=rows,
            ),
            ERROR,
        )

    def test_state_operator_combines_predicates_after_entity_evaluation(self):
        self.assertEqual(aggregate_state("AND", [TRUE, FALSE, ERROR]), FALSE)
        self.assertEqual(aggregate_state("OR", [FALSE, TRUE, ERROR]), TRUE)
        self.assertEqual(aggregate_state("ONE", [TRUE, FALSE, FALSE]), TRUE)

    def test_test_state_operator_combines_states_per_item(self):
        self.assertEqual(aggregate_item_states("AND", [TRUE, FALSE]), FALSE)
        self.assertEqual(aggregate_item_states("OR", [FALSE, TRUE]), TRUE)
        self.assertEqual(aggregate_item_states("XOR", [TRUE, TRUE]), FALSE)

    def test_rejects_empty_many_to_many_shape(self):
        with self.assertRaises(ValueError):
            aggregate_many_to_many(
                var_check="all",
                entity_check="all",
                comparison_rows=[],
            )
        with self.assertRaises(ValueError):
            aggregate_many_to_many(
                var_check="all",
                entity_check="all",
                comparison_rows=[[]],
            )


if __name__ == "__main__":
    unittest.main()
