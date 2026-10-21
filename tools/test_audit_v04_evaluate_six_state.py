#!/usr/bin/env python3
"""Adversarial AND/OR Test-result rename six-state differential fixtures."""
from copy import deepcopy
import unittest

from audit_v04_evaluate_six_state import compare,evaluate,vector_matrix
from migrate_v04_evaluate_and_or import migrate
from oval_result_truth_tables import RESULTS


def source(expression):
    return {"assessment":{
        "id":"sample-assessment","mode":"automated",
        "tests":{"a-test":{"states_match":"any",
                           "require":{"items":"one_or_more",
                                      "all_items_must":[{"or":[
                                          {"value":{"equals":"a"}},
                                          {"value":{"equals":"b"}}]}]},
                           "object":{"select":{"items":{"value_match":"any"}}}}},
        "evaluate":expression}}


class ResultScopeTests(unittest.TestCase):
    def test_nested_and_or_xor_exactly_preserve_source_unrelated_fields(self):
        orig=source({"all":[{"test":"a-test"},
                            {"not":{"any":[{"assessment":"other-assessment"},
                                           {"odd":[{"test":"c-test"},
                                                   {"test":"d-test"},
                                                   {"test":"e-test"}]}]}}]})
        changed,_=migrate(orig)
        result=compare(orig,changed)
        self.assertIsNotNone(result)
        self.assertGreater(result["vectors"],150)
        self.assertEqual(changed["assessment"]["tests"],orig["assessment"]["tests"])
        self.assertEqual(changed["assessment"]["tests"]["a-test"]["states_match"],"any")
        self.assertEqual(changed["assessment"]["tests"]["a-test"]["require"]["items"],"one_or_more")
        self.assertEqual(changed["assessment"]["tests"]["a-test"]["object"]["select"]["items"]["value_match"],"any")

    def test_not_and_else_with_six_states(self):
        orig=source({"if":{"test":"a-test"},
                     "then":{"all":[{"test":"b-test"},
                                    {"not":{"test":"c-test"}}]},
                     "else":{"any":[{"not_applicable":{"reason":"applicability"}},
                                    {"test":"d-test"}]}})
        new,_=migrate(orig)
        self.assertIsNotNone(compare(orig,new))
        for status in RESULTS:
            self.assertEqual(evaluate({"not":{"test":"a-test"}},{"test:a-test":status}),
                             {"true":"false","false":"true"}.get(status,status))

    def test_operator_flip_is_detected(self):
        orig=source({"all":[{"test":"a-test"},{"test":"b-test"}]})
        new,_=migrate(orig)
        mutated=deepcopy(new)
        mutated["assessment"]["evaluate"]["or"]=mutated["assessment"]["evaluate"].pop("and")
        with self.assertRaisesRegex(ValueError,"six-state result mismatch"):
            compare(orig,mutated)

    def test_lost_operand_is_detected(self):
        orig=source({"any":[{"test":"a-test"},{"test":"b-test"}]})
        new,_=migrate(orig)
        mutated=deepcopy(new)
        mutated["assessment"]["evaluate"]["or"].pop()
        with self.assertRaisesRegex(ValueError,"operands lost or invented"):
            compare(orig,mutated)

    def test_item_quantifier_must_never_change(self):
        orig=source({"any":[{"test":"a-test"},{"test":"b-test"}]})
        new,_=migrate(orig)
        mutated=deepcopy(new)
        mutated["assessment"]["tests"]["a-test"]["require"]["items"]="may_be_absent"
        with self.assertRaisesRegex(ValueError,"changed non-evaluate"):
            compare(orig,mutated)

    def test_field_operator_must_not_change(self):
        orig=source({"all":[{"test":"a-test"},{"test":"b-test"}]})
        new,_=migrate(orig)
        mutated=deepcopy(new)
        mutated["assessment"]["tests"]["a-test"]["require"]["all_items_must"][0]["and"]=[{"value":{"equals":"a"}}]
        with self.assertRaisesRegex(ValueError,"changed non-evaluate"):
            compare(orig,mutated)

    def test_rare_xor_and_one_differ_on_three_true(self):
        orig=source({"odd":[{"test":"a-test"},{"test":"b-test"},{"test":"c-test"}]})
        new,_=migrate(orig)
        self.assertIsNotNone(compare(orig,new))
        mutated=deepcopy(new)
        mutated["assessment"]["evaluate"]["one"]=mutated["assessment"]["evaluate"].pop("xor")
        with self.assertRaisesRegex(ValueError,"six-state result mismatch"):
            compare(orig,mutated)

    def test_bounded_matrix_includes_every_six_state_status(self):
        scenarios=vector_matrix({"test:a-test","test:b-test"})
        for status in RESULTS:
            self.assertTrue(any(x["test:a-test"]==status for x in scenarios))
            self.assertTrue(any(x["test:b-test"]==status for x in scenarios))


if __name__=="__main__":
    unittest.main()
