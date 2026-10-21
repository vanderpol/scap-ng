#!/usr/bin/env python3
"""OVAL 5.12.3 six-state, source-scope and reversible field-layout pilot."""
from __future__ import annotations

from copy import deepcopy
from itertools import product
from pathlib import Path
import unittest

from oval_result_truth_tables import aggregate_operator
from research_v04_oval_logic_scopes import RESULTS, candidate_logic
from preview_v04_oval_operator_field_groups import (
    field_group, inverse_field_group, project, restore, source_graph,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tests/v04-oval-operator-scopes/oval-independent-operators.xml"


def evaluate_group(group, values):
    if "fields_operator" in group:
        entries = group["fields"]
        return candidate_logic(group["fields_operator"], values[:len(entries)])
    return candidate_logic("and", values[:len(group["fields"])])


class ReversibleOVALFieldGroupTests(unittest.TestCase):
    def setUp(self):
        self.graph = source_graph(SOURCE)
        self.candidate, self.proof = project(self.graph)

    def test_all_six_schema_valid_oval_examples_recover_original_graph(self):
        self.assertEqual(len(self.graph["tests"]), 6)
        self.assertEqual(len(self.graph["states"]), 6)
        self.assertEqual(restore(self.candidate, self.proof), self.graph)
        again, proof = project(self.graph)
        self.assertEqual((again, proof), (self.candidate, self.proof))

    def test_test_state_operator_is_outside_complete_field_groups(self):
        expected = ("or", "one", "xor")
        for i, operator in enumerate(expected):
            group = self.candidate["tests"][i]["item_condition"]
            self.assertEqual(list(group), [operator])
            self.assertEqual(len(group[operator]), 2 if i == 0 else 3)
            for state in group[operator]:
                self.assertEqual(set(state), {"fields"})
        # A SINGLE original State with OR/ONE/XOR over its fields MUST
        # not be mistaken for Test.state_operator OR/ONE/XOR.
        for i, operator in enumerate(expected, start=3):
            group = self.candidate["tests"][i]["item_condition"]
            self.assertEqual(group["fields_operator"], operator)
            self.assertEqual(len(group["fields"]), 2)
            self.assertNotIn(operator, group)

    def test_original_check_and_item_existence_not_reinterpreted(self):
        self.assertEqual(self.candidate["tests"][0]["item_matching_oval"],
                         "at least one")
        for test in self.candidate["tests"]:
            self.assertEqual(test["item_existence_oval"],
                             "at_least_one_exists")
            self.assertEqual(test["item_matching_oval"],
                             self.graph["tests"][
                                 self.candidate["tests"].index(test)
                             ]["attributes"]["check"])
        # The pilot explicitly carries source Test check semantics; it
        # does NOT invent a 'one_or_more' logical OR for that stage.

    def test_all_six_state_vectors_match_original_oval_operator_tables(self):
        total = 0
        for test, view in zip(self.graph["tests"], self.candidate["tests"]):
            refs = test["state_refs"]
            widths = [len(self.graph["states"][ref]["fields"]) for ref in refs]
            for results in product(RESULTS, repeat=sum(widths)):
                offset, originals, rendered = 0, [], []
                groups = (view["item_condition"][
                    test["attributes"]["state_operator"].lower()]
                    if len(refs) > 1 else [view["item_condition"]])
                for ref, width, group in zip(refs, widths, groups):
                    values = results[offset:offset+width]
                    offset += width
                    original_op = self.graph["states"][ref]["attributes"].get(
                        "operator", "AND")
                    originals.append(aggregate_operator(original_op, values))
                    rendered.append(evaluate_group(group, values))
                source_expected = aggregate_operator(
                    test["attributes"]["state_operator"], originals)
                projected_actual = candidate_logic(
                    test["attributes"]["state_operator"].lower(), rendered)
                self.assertEqual(source_expected, projected_actual,
                                 (test["id"], results))
                total += 1
        # Fixture has max 3 field outcomes per Test (not a scanner runtime).
        self.assertEqual(total, 3*6**3 + 3*6**2)

    def test_mixed_fields_from_different_states_cannot_be_flattened(self):
        # State A: true AND false = false; State B: false AND true = false.
        # State-level OR is false. A single field-level OR would be true.
        faithful = candidate_logic("or", [
            candidate_logic("and", ["true", "false"]),
            candidate_logic("and", ["false", "true"])])
        corrupt = candidate_logic("or", ["true", "false", "false", "true"])
        self.assertEqual(faithful, "false")
        self.assertEqual(corrupt, "true")

    def test_repeated_field_names_use_ordered_entries_even_for_and(self):
        original = {"attributes": {"operator": "AND"},
                    "fields": [
                      {"name": "value", "attributes": {"operation": "equals"},
                       "text": "alpha"},
                      {"name": "value", "attributes": {"operation": "equals"},
                       "text": "beta"}]}
        candidate = field_group(original)
        self.assertEqual(candidate["fields_operator"], "and")
        self.assertIsInstance(candidate["fields"], list)
        self.assertEqual([next(iter(x)) for x in candidate["fields"]],
                         ["value", "value"])
        self.assertEqual(inverse_field_group(candidate,
                         original["attributes"]), original)

    def test_field_or_one_xor_not_downgraded_to_or_or_any(self):
        for op in ("OR", "ONE", "XOR"):
            source = {"attributes": {"operator": op},
                      "fields": [
                        {"name": "stdout_line", "attributes": {},
                         "text": "alpha"},
                        {"name": "stderr_line", "attributes": {},
                         "text": "beta"}]}
            group = field_group(source)
            self.assertEqual(group["fields_operator"], op.lower())
            self.assertEqual(inverse_field_group(group,
                             source["attributes"]), source)
            for replacement in ("any", "all", "one_or_more"):
                altered = deepcopy(group)
                altered["fields_operator"] = replacement
                with self.assertRaises(ValueError):
                    inverse_field_group(altered, source["attributes"])

    def test_mutating_check_field_or_operator_breaks_source_inverse(self):
        variants = [
            lambda doc: doc["tests"][0].update(
                item_matching_oval="all"),
            lambda doc: doc["tests"][0]["item_condition"].update(
                {"and": doc["tests"][0]["item_condition"].pop("or")}),
            lambda doc: doc["tests"][3]["item_condition"].update(
                fields_operator="and"),
            lambda doc: doc["tests"][3]["item_condition"]["fields"][0][
                "exit_status"].update(text="9"),
        ]
        for mutation in variants:
            edited = deepcopy(self.candidate)
            mutation(edited)
            with self.assertRaises(ValueError):
                restore(edited, self.proof)


if __name__ == "__main__":
    unittest.main()
