#!/usr/bin/env python3
"""#235: focused semantic counterexamples before pruning rare OVAL constructs.

The tests are deliberately exact OVAL generic reference checks. They do not
establish that native simplifications are accepted or scanner-proven.
"""
import unittest
from oval_result_truth_tables import (
    TRUE, FALSE, ERROR, UNKNOWN, NOT_APPLICABLE,
    aggregate_existence, aggregate_check, aggregate_operator,
    evaluate_collected_object_test,
)

class RemovalGuards(unittest.TestCase):
    def test_exactly_one_is_not_at_least_one(self):
        self.assertEqual(TRUE,aggregate_existence("only_one_exists",exists=1))
        self.assertEqual(FALSE,aggregate_existence("only_one_exists",exists=2))
        self.assertEqual(TRUE,aggregate_existence("at_least_one_exists",exists=2))

    def test_optional_is_not_required(self):
        self.assertEqual(TRUE,aggregate_existence("any_exist",exists=0))
        self.assertEqual(FALSE,aggregate_existence("at_least_one_exists",exists=0))

    def test_optional_is_not_absence_on_collection_error(self):
        self.assertEqual(ERROR,aggregate_existence("any_exist",exists=0,error=1))
        self.assertEqual(TRUE,aggregate_existence("any_exist",exists=1,error=1))

    def test_none_exist_is_not_none_satisfy(self):
        self.assertEqual(FALSE,evaluate_collected_object_test(
            "complete", existence="none_exist", has_state=False, exists=1))
        self.assertEqual(TRUE,evaluate_collected_object_test(
            "complete",existence="at_least_one_exists",
            check="none satisfy",item_results=[FALSE],exists=1))

    def test_only_one_match_is_not_some_match(self):
        self.assertEqual(FALSE,aggregate_check("only one",[TRUE,TRUE]))
        self.assertEqual(TRUE,aggregate_check("at least one",[TRUE,TRUE]))

    def test_oval_one_and_xor_are_not_synonyms(self):
        self.assertEqual(FALSE,aggregate_operator("ONE",[TRUE,TRUE,TRUE]))
        self.assertEqual(TRUE,aggregate_operator("XOR",[TRUE,TRUE,TRUE]))
        self.assertEqual(TRUE,aggregate_operator("OR",[TRUE,TRUE,TRUE]))

    def test_all_exist_vs_some_incomplete_collection(self):
        args={"has_state":True,"check":"all","item_results":[FALSE],"exists":1}
        self.assertEqual(UNKNOWN,evaluate_collected_object_test(
            "incomplete",existence="all_exist",**args))
        self.assertEqual(FALSE,evaluate_collected_object_test(
            "incomplete",existence="at_least_one_exists",**args))

    def test_not_applicable_keeps_six_state(self):
        self.assertEqual(NOT_APPLICABLE,evaluate_collected_object_test(
            "not applicable",existence="at_least_one_exists",has_state=False))

if __name__=="__main__":
    unittest.main()
