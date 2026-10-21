#!/usr/bin/env python3
"""Adversarial boundaries for lossless 0.4 State OR/AND group modernization."""
import copy
from itertools import product
import unittest

from migrate_v04_states_match_to_logic import migrate,restore,validate_exact_inverse
from oval_result_truth_tables import aggregate_operator


def fixture(scope="any",n=2):
    conds=[{"and":[{"type":{"equals":"string"}},
                   {"value":{"equals":word}}]}
           for word in ("Enterprise","EnterpriseS","Education")[:n]]
    return {"assessment":{"mode":"automated","specification":{"version":"0.4.0"},
            "tests":{"editionid-enterprise-or-enterprises-test":{
                "capability":"windows.registry",
                "states_match":scope,
                "state_fields_require":"at_least_one_exists_and_all_match",
                "require":{"items":"one_or_more","all_items_must":conds}}},
            "evaluate":{"test":"editionid-enterprise-or-enterprises-test"}}}


class StateScopeMigrationTests(unittest.TestCase):
    def test_two_complete_states_are_or_not_field_or(self):
        before=fixture()
        after,proof=migrate(before)
        self.assertEqual(len(proof),1)
        test=after["assessment"]["tests"]["editionid-enterprise-or-enterprises-test"]
        self.assertNotIn("states_match",test)
        self.assertEqual(test["require"]["items"],"one_or_more")
        self.assertEqual(list(test["require"]["all_items_must"][0]),["or"])
        self.assertEqual(len(test["require"]["all_items_must"][0]["or"]),2)
        self.assertEqual(test["state_fields_require"],
                         "at_least_one_exists_and_all_match")
        self.assertTrue(validate_exact_inverse(before,after,proof))
        self.assertEqual(restore(after,proof),before)

    def test_and_states_preserve_entire_condition_boundaries(self):
        before=fixture("all",3)
        after,proof=migrate(before)
        test=after["assessment"]["tests"]["editionid-enterprise-or-enterprises-test"]
        self.assertEqual(list(test["require"]["all_items_must"][0]),["and"])
        self.assertEqual(len(test["require"]["all_items_must"][0]["and"]),3)
        self.assertTrue(validate_exact_inverse(before,after,proof))

    def test_original_oval_six_state_equivalence_for_or_and(self):
        choices=("true","false","error","unknown","not evaluated","not applicable")
        for label,ovop in (("any","OR"),("all","AND")):
            before=fixture(label,3)
            after,ledger=migrate(before)
            test=after["assessment"]["tests"]["editionid-enterprise-or-enterprises-test"]
            op=next(iter(test["require"]["all_items_must"][0]))
            self.assertEqual(op,ovop.lower())
            # The State results are aggregated once per Item, before the
            # separate Test Item check; do not flatten across Item instances.
            for values in product(choices,repeat=3):
                original=aggregate_operator(ovop,values)
                rewritten=aggregate_operator(op.upper(),values)
                self.assertEqual(original,rewritten,(label,values))
            self.assertTrue(validate_exact_inverse(before,after,ledger))

    def test_rejects_unsafe_or_unknown_scope_shapes(self):
        for mutate in (
            lambda t:t["require"].update(items="exactly_one"),
            lambda t:t["require"].update(all_items_must=[]),
            lambda t:t["require"].update(all_items_must=[{"value":{"equals":0}}]),
            lambda t:t["require"].update(all_items_must="not a list"),
            lambda t:t["require"].update(extra="silent_source_loss"),
        ):
            doc=fixture()
            with self.subTest(mutate=str(mutate)), self.assertRaises(ValueError):
                mutate(doc["assessment"]["tests"]["editionid-enterprise-or-enterprises-test"])
                migrate(doc)

    def test_not_interpret_scalar_legacy_tests_as_structured_operators(self):
        for scope in ("any","all"):
            before=fixture(scope)
            test=before["assessment"]["tests"]["editionid-enterprise-or-enterprises-test"]
            test["require"]="at_least_one_exists_and_some_match"
            after,ledger=migrate(before)
            self.assertEqual(after,before)
            self.assertEqual(ledger,[])

    def test_not_rewrite_completely_different_cardinality(self):
        before=fixture()
        t=before["assessment"]["tests"]["editionid-enterprise-or-enterprises-test"]
        t.pop("states_match")
        t["require"]["items"]="none"
        after,ledger=migrate(before)
        self.assertEqual(after,before)
        self.assertEqual(ledger,[])

    def test_inverse_proof_detects_changed_operator_or_state_predicate(self):
        before=fixture()
        after,ledger=migrate(before)
        changed=copy.deepcopy(after)
        req=changed["assessment"]["tests"]["editionid-enterprise-or-enterprises-test"]["require"]
        req["all_items_must"][0]["or"][1]["and"][1]["value"]["equals"]="corrupted"
        with self.assertRaisesRegex(ValueError,"cannot be inverted"):
            restore(changed,ledger)
        changed=copy.deepcopy(after)
        req=changed["assessment"]["tests"]["editionid-enterprise-or-enterprises-test"]["require"]
        req["all_items_must"][0]["and"]=req["all_items_must"][0].pop("or")
        with self.assertRaisesRegex(ValueError,"cannot be inverted"):
            restore(changed,ledger)

    def test_nested_existing_field_or_is_not_reassigned_to_items(self):
        original=fixture()
        original["assessment"]["tests"]["editionid-enterprise-or-enterprises-test"]["require"]["all_items_must"][1]={
            "and":[{"type":{"equals":"string"}},
                   {"or":[{"value":{"equals":"EnterpriseS"}},
                          {"value":{"equals":"Education"}}]}]}
        after,ledger=migrate(original)
        states=after["assessment"]["tests"]["editionid-enterprise-or-enterprises-test"]["require"]["all_items_must"][0]["or"]
        self.assertEqual(list(states[1]),["and"])
        self.assertEqual(list(states[1]["and"][1]),["or"])
        self.assertTrue(validate_exact_inverse(original,after,ledger))


if __name__=="__main__":
    unittest.main()
