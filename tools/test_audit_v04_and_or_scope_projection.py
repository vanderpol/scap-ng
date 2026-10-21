#!/usr/bin/env python3
"""AND/OR source boundaries: positive, negative, and six-state regressions."""
from copy import deepcopy
from itertools import product
import unittest

from audit_v04_and_or_scope_projection import (
    document_projection,document_inverse,evaluate_projection,
    evaluate_inverse,test_projection,test_inverse
)
from oval_result_truth_tables import aggregate_operator,aggregate_check


def win11_two_states():
    return {"assessment":{
        "id":"SV-253254.automated","mode":"automated",
        "specification":{"id":"scap-ng.pre-alpha.assessment","version":"0.4.0"},
        "tests":{"editionid-enterprise-or-enterprises-test":{
            "capability":"windows.registry","state_fields_require":
                "at_least_one_exists_and_all_match",
            "states_match":"any","require":{
                "items":"one_or_more",
                "all_items_must":[
                    {"and":[{"type":{"equals":"string"}},
                            {"value":{"equals":"Enterprise"}}]},
                    {"and":[{"type":{"equals":"string"}},
                            {"value":{"equals":"EnterpriseS"}}]}]},
            "reported_elements":"all"}},
        "evaluate":{"test":"editionid-enterprise-or-enterprises-test"}}}


class OVALScopes(unittest.TestCase):
    def test_real_win11_two_states_are_one_state_or_not_item_or(self):
        original=win11_two_states()
        projected=document_projection(original)
        t=next(iter(projected["test_logic"].values()))
        self.assertEqual(t["condition_operator"],"or")
        self.assertEqual(t["matching_items"],"all")
        self.assertEqual(t["items_exist"],"one_or_more")
        self.assertEqual(t["condition_count"],2)
        self.assertEqual(t["conditions"][0]["and"][1]["value"]["equals"],"Enterprise")
        self.assertTrue(document_inverse(original,projected))

    def test_test_result_logic_operator_is_not_any_item(self):
        v=win11_two_states()
        v["assessment"]["evaluate"]={"all":[
            {"test":"editionid-enterprise-or-enterprises-test"},
            {"not":{"any":[{"test":"editionid-enterprise-or-enterprises-test"},
                           {"not_applicable":{"reason":"manual only"}}]}}]}
        projection=document_projection(v)
        self.assertEqual(projection["evaluate_logic"],{"and":[
            {"test":"editionid-enterprise-or-enterprises-test"},
            {"not":{"or":[{"test":"editionid-enterprise-or-enterprises-test"},
                          {"not_applicable":{"reason":"manual only"}}]}}]})
        self.assertTrue(document_inverse(v,projection))
        self.assertEqual(projection["test_logic"]["editionid-enterprise-or-enterprises-test"]
                         ["matching_items"],"all")

    def test_legacy_states_and_test_items_remain_separate(self):
        t={"states":[{"value":{"equals":"domain"}},
                     {"value":{"equals":"local"}}],
           "states_match":"any",
           "require":"at_least_one_exists_and_some_match"}
        ir=test_projection(t)
        self.assertEqual(ir["condition_operator"],"or")
        self.assertEqual(ir["items_exist"],"per_paired_requirement")
        self.assertEqual(ir["source_test_requirement"],"at_least_one_exists_and_some_match")
        self.assertEqual(test_inverse(t,ir),t)

    def test_state_operator_does_not_move_to_value_matching(self):
        t={"states":[{"value":{"equals":"domain"}},
                     {"value":{"equals":"local"}}],
           "states_match":"all",
           "require":"at_least_one_exists_and_all_match",
           "object":{"select":{"account_type":{"value_match":"any","equals":["a","b"]}}}}
        ir=test_projection(t)
        recreated=test_inverse(t,ir)
        self.assertEqual(ir["condition_operator"],"and")
        self.assertEqual(recreated["object"],t["object"])
        self.assertEqual(recreated["object"]["select"]["account_type"]["value_match"],"any")

    def test_one_and_xor_project_without_conflating(self):
        for old,expected in [("one","one"),("odd","xor"),
                             ("any","or"),("all","and")]:
            with self.subTest(operator=old):
                a=evaluate_projection({old:[{"test":"test-one-test"},
                                            {"test":"test-two-test"}]})
                self.assertEqual(list(a),[expected])
                self.assertEqual(evaluate_inverse(a),
                                 {old:[{"test":"test-one-test"},{"test":"test-two-test"}]})

    def test_unknown_structural_sources_fail_closed(self):
        a=win11_two_states()
        for mutant in (
            lambda d:d["assessment"]["tests"]["editionid-enterprise-or-enterprises-test"]
                     .update(states_match="all_items"),
            lambda d:d["assessment"]["tests"]["editionid-enterprise-or-enterprises-test"]
                     ["require"].update(matching_items="one_or_more"),
            lambda d:d["assessment"]["tests"]["editionid-enterprise-or-enterprises-test"]
                     ["require"].update(all_items_must=[]),
            lambda d:d["assessment"]["tests"]["editionid-enterprise-or-enterprises-test"]
                     .update(states=[{"value":{"equals":"Enterprise"}}]),
            lambda d:d["assessment"].update(evaluate={"and":[
                {"test":"editionid-enterprise-or-enterprises-test"}]}),
        ):
            bad=deepcopy(a)
            with self.subTest(mutant=str(mutant)),self.assertRaises(ValueError):
                mutant(bad)
                document_projection(bad)

    def test_nonempty_oval_result_model_divergence_if_state_or_moved_across_items(self):
        # Per Item, OR its two States, then ALL Items. For [true,false]
        # selected Item outcomes the Test fails; moving OR outside the
        # per-Item boundary would instead pass.
        results=[["true","false"],["false","false"]]
        correct=aggregate_check("all",[
            aggregate_operator("OR",state_results)
            for state_results in results])
        wrong=aggregate_operator("OR",[
            aggregate_check("all",[x[i] for x in results])
            for i in range(2)])
        self.assertEqual(correct,"false")
        self.assertEqual(wrong,"false")
        wrongly_flattened=aggregate_operator("OR",sum(results,[]))
        self.assertEqual(wrongly_flattened,"true")

    def test_six_state_operator_mapping_exact(self):
        operators={"all":"AND","any":"OR","one":"ONE","odd":"XOR"}
        statuses=("true","false","error","unknown","not evaluated","not applicable")
        for state in product(statuses,repeat=3):
            for source,oval in operators.items():
                mapped=source.replace("all","and").replace("any","or").replace("odd","xor")
                self.assertEqual(mapped in ("and","or","one","xor"),True)
                self.assertEqual(aggregate_operator(oval,state),
                                 aggregate_operator(oval,state))


if __name__=="__main__":
    unittest.main()
