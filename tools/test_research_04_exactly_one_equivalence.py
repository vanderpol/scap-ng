#!/usr/bin/env python3
"""#235: prove exactly-one EXISTS + ALL MATCH vs exactly-one EXISTS + ONE MATCH.

Under a successful cardinality requirement of only_one_exists, at most one
existing Item can be evaluated, so check='all' and check='only one' yield the
same six-state result. This ONLY applies when existence is exactly one,
not when two or more existing Items are possible.
"""
from itertools import product
import unittest
from oval_result_truth_tables import (
    TRUE,FALSE,ERROR,UNKNOWN,NOT_EVALUATED,NOT_APPLICABLE,
    evaluate_collected_object_test
)
OUTCOMES=(TRUE,FALSE,ERROR,UNKNOWN,NOT_EVALUATED,NOT_APPLICABLE)
FLAGS=("complete","incomplete","error","not collected","not applicable","does not exist")

class ExactlyOneRequirements(unittest.TestCase):
    def test_exact_one_exists_all_equals_exact_one_exists_one_matches(self):
        cases=0
        for flag in FLAGS:
            for exists in range(4):
                for does_not_exist,error,not_collected in product(range(2),repeat=3):
                    for results in product(OUTCOMES,repeat=exists):
                        args={
                            "flag":flag,"existence":"only_one_exists",
                            "item_results":list(results),"has_state":True,
                            "exists":exists,"does_not_exist":does_not_exist,
                            "error":error,"not_collected":not_collected,
                        }
                        self.assertEqual(
                            evaluate_collected_object_test(check="all",**args),
                            evaluate_collected_object_test(check="only one",**args),
                            msg=f"Exact-one State match divergence: {args}"
                        )
                        cases+=1
        self.assertGreater(cases,10000)
        print(f"exactly-one existence equivalence: {cases} exhaustive source-generic vectors")

    def test_at_least_one_exists_does_not_subsume_uniqueness(self):
        common={"flag":"complete","check":"at least one",
                "item_results":[TRUE,FALSE],"has_state":True,"exists":2}
        self.assertEqual(FALSE,evaluate_collected_object_test(
            existence="only_one_exists",**common))
        self.assertEqual(TRUE,evaluate_collected_object_test(
            existence="at_least_one_exists",**common))

    def test_exact_one_match_does_not_mean_exactly_one_exists(self):
        result=evaluate_collected_object_test(
            "complete",existence="at_least_one_exists",check="only one",
            item_results=[TRUE,FALSE],has_state=True,exists=2)
        self.assertEqual(TRUE,result)
        result=evaluate_collected_object_test(
            "complete",existence="only_one_exists",check="only one",
            item_results=[TRUE,FALSE],has_state=True,exists=2)
        self.assertEqual(FALSE,result)

    def test_exactly_one_statefree_simplest_mode(self):
        self.assertEqual(TRUE,evaluate_collected_object_test(
            "complete",existence="only_one_exists",has_state=False,exists=1))
        self.assertEqual(FALSE,evaluate_collected_object_test(
            "complete",existence="only_one_exists",has_state=False,exists=2))

    def test_incomplete_one_is_unknown_but_two_is_false(self):
        self.assertEqual(UNKNOWN,evaluate_collected_object_test(
            "incomplete",existence="only_one_exists",has_state=False,exists=1))
        self.assertEqual(FALSE,evaluate_collected_object_test(
            "incomplete",existence="only_one_exists",has_state=False,exists=2))

if __name__=="__main__":
    unittest.main()
