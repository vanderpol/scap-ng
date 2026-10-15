#!/usr/bin/env python3
"""Verify six-outcome invariance and strict scoped absence compression."""
import itertools
import unittest
from copy import deepcopy

from oval_result_truth_tables import evaluate_collected_object_test
from research_04_none_exist_alias import (
    compress_test, expand_test, compress_state_field, expand_state_field,
)

class NoneExistPresetTests(unittest.TestCase):
    def test_test_match_inert_for_all_six_technical_outcomes(self):
        # Complete/incomplete records, missing records and absent/error
        # collected_object flags; verify every allowed check combination
        # with no State, across existence cardinality/status mixes.
        flags=("complete","incomplete","error","not collected","not applicable",
               "does not exist")
        modes=("all","at least one","only one","none satisfy")
        count=0
        for flag,exists,dne,error,not_collected in itertools.product(
            flags,range(3),range(2),range(2),range(2)
        ):
            kw=dict(flag=flag, existence="none_exist", has_state=False,
                    exists=exists,does_not_exist=dne,error=error,
                    not_collected=not_collected)
            expected=evaluate_collected_object_test(check=modes[0],**kw)
            for mode in modes[1:]:
                self.assertEqual(evaluate_collected_object_test(check=mode,**kw),
                                 expected, msg=(flag,exists,dne,error,not_collected,mode))
                count+=1
        self.assertGreater(count,100)

    def test_no_states_absence_can_normalize_even_odd_match(self):
        for match in ("all","one","one_or_more","none"):
            old={"existence":"none","match":match,
                 "object":{"capability":"windows.registry","select":{}}}
            short, original=compress_test(old)
            self.assertEqual(original, match)
            newer=expand_test(short)
            self.assertEqual(newer,{**old,"match":"all"})
            self.assertNotIn("states",newer)

    def test_absence_cannot_consume_state(self):
        for states in ([],[{"field":"x","value":1}]):
            src={"existence":"none","match":"all","states":states}
            with self.assertRaisesRegex(ValueError,"No-state"):
                compress_test(src)
            with self.assertRaisesRegex(ValueError,"No-state"):
                expand_test({"require":"none_exist","states":states})

    def test_absence_cannot_interfere_with_explicit_quantifiers(self):
        with self.assertRaisesRegex(ValueError,"conflicts"):
            expand_test({"require":"none_exist","match":"one"})
        with self.assertRaisesRegex(ValueError,"require"):
            compress_test({"existence":"none","match":"all","require":"something"})

    def test_only_none_existence_accepted(self):
        for existence in ("one","one_or_more","all","optional",None):
            with self.assertRaisesRegex(ValueError,"existence:none"):
                compress_test({"existence":existence,"match":"all"})

    def test_field_none_all_structurally_exact(self):
        old={"field":"stdout_line","value":"forbidden","operation":"equals",
             "existence":"none","match":"all"}
        compact=compress_state_field(old)
        self.assertEqual(expand_state_field(compact),old)
        self.assertEqual(old["value"],"forbidden")

    def test_field_none_one_rejected_pending_semantic_proof(self):
        with self.assertRaisesRegex(ValueError,"exact field"):
            compress_state_field({"field":"stdout_line","value":"x",
                                  "existence":"none","match":"one"})

    def test_missing_match_rejected(self):
        with self.assertRaisesRegex(ValueError,"missing match"):
            compress_test({"existence":"none"})

if __name__=="__main__":
    unittest.main()
