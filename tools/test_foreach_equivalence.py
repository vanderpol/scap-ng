#!/usr/bin/env python3
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path
import unittest

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from foreach_equivalence import (
    direct_at_least_one_equivalent,
    faithful_at_least_one_selection,
    faithful_all_selection,
    foreach_union_selection,
    equivalent_population,
    project_object_component_complete,
    direct_foreach_desugaring,
    direct_foreach_preconditions,
    DIRECT_FOREACH_REWRITE_ID,
    faithful_direct_evidence,
    foreach_direct_evidence,
    evidence_equivalent,
)
from oval_result_truth_tables import (
    TRUE,
    FALSE,
    resolve_variable_reference,
    apply_variable_reference_context,
    evaluate_collected_object_test,
)


def evaluate_population(population, *, existence, check, state_by_item, has_state=True):
    """Feed a selected Object population through the existing OVAL Test tables."""
    population = list(population)
    kwargs = {
        "flag": "complete",
        "existence": existence,
        "check": check,
        "has_state": has_state,
        "exists": len(population),
    }
    if has_state:
        kwargs["item_results"] = [state_by_item[item] for item in population]
    return evaluate_collected_object_test(**kwargs)


class DirectCollectionExpansionEquivalence(unittest.TestCase):
    def test_exhaustive_equals_domain(self):
        domain = ["a", "b", "c"]
        item_sets = []
        for n in range(len(domain) + 1):
            item_sets.extend(itertools.combinations(domain, n))
        value_sets = []
        for n in range(len(domain) + 1):
            value_sets.extend(itertools.product(domain, repeat=n))

        for items in item_sets:
            for values in value_sets:
                with self.subTest(items=items, values=values):
                    self.assertTrue(
                        direct_at_least_one_equivalent(
                            items,
                            values,
                            lambda item, value: item == value,
                        )
                    )

    def test_duplicate_projected_values_do_not_change_population(self):
        items = ["/home/a", "/home/b", "/home/c"]
        self.assertTrue(
            direct_at_least_one_equivalent(
                items,
                ["/home/a", "/home/a", "/home/b"],
                lambda item, value: item == value,
            )
        )

    def test_arbitrary_binary_predicate_preserves_or_identity(self):
        items = [1, 2, 3, 4, 5]
        values = [2, 3]
        self.assertTrue(
            direct_at_least_one_equivalent(
                items,
                values,
                lambda item, value: item % value == 0,
            )
        )

    def test_all_values_is_not_union_equivalent(self):
        items = [1, 2, 3, 4, 6]
        values = [2, 3]
        predicate = lambda item, value: item % value == 0
        faithful = faithful_all_selection(items, values, predicate)
        foreach_union = foreach_union_selection(items, values, predicate)
        self.assertFalse(equivalent_population(faithful, foreach_union))
        self.assertEqual(faithful, [6])
        self.assertEqual(set(foreach_union), {2, 3, 4, 6})

    def test_zero_source_items_is_object_component_error(self):
        projection = project_object_component_complete([], "home_dir")
        self.assertEqual(projection["status"], "error")
        self.assertEqual(projection["reason"], "source_object_has_no_items")

    def test_missing_projected_field_is_object_component_error(self):
        projection = project_object_component_complete(
            [{"username": "alice"}],
            "home_dir",
        )
        self.assertEqual(projection["status"], "error")
        self.assertEqual(projection["reason"], "item_field_missing:home_dir")

    def test_multiple_source_entities_are_flattened_as_component_values(self):
        projection = project_object_component_complete(
            [{"home_dir": ["/home/a", "/srv/a"]}, {"home_dir": "/home/b"}],
            "home_dir",
        )
        self.assertEqual(projection["status"], "values")
        self.assertEqual(
            projection["values"],
            ["/home/a", "/srv/a", "/home/b"],
        )


class DirectForeachDesugaring(unittest.TestCase):
    def test_desugaring_preserves_existing_semantic_nodes(self):
        graph = direct_foreach_desugaring(
            source_object="users",
            item_field="home_dir",
            target_object="init-files",
            target_entity="path",
            operation="equals",
            datatype="string",
        )
        self.assertEqual(graph["rewrite_id"], DIRECT_FOREACH_REWRITE_ID)
        self.assertEqual(graph["aggregation_boundary"], "target_object_population")
        self.assertEqual(
            graph["variable"],
            {
                "kind": "local_variable",
                "expression": {
                    "kind": "object_component",
                    "object_ref": "users",
                    "item_field": "home_dir",
                },
            },
        )
        self.assertEqual(graph["selector"]["var_check"], "at least one")
        self.assertIs(graph["selector"]["variable"], graph["variable"])

    def test_first_proof_class_preconditions_are_fail_closed(self):
        eligible = {
            "variable_id": "oval:test:var:1",
            "candidate_family": "collection_expansion_at_least_one",
            "expression": {
                "kind": "direct_object_projection",
                "record_field": None,
            },
            "targets": [
                {
                    "context": "object_selector",
                    "var_check": "at least one",
                    "tests": [{"test_id": "oval:test:tst:1"}],
                    "object_features": {
                        "variable_entities": [
                            {"var_ref": "oval:test:var:1"}
                        ]
                    },
                }
            ],
        }
        self.assertTrue(direct_foreach_preconditions(eligible)["eligible"])

        for mutation, reason in (
            (
                {"candidate_family": "quantified_projection_all_values"},
                "candidate_family_not_at_least_one_collection_expansion",
            ),
            (
                {"expression": {"kind": "derived_expression", "record_field": None}},
                "projection_is_not_direct_object_component",
            ),
            (
                {"expression": {"kind": "direct_object_projection", "record_field": "name"}},
                "record_field_not_in_first_proof_class",
            ),
            (
                {"targets": [{"context": "object_selector", "var_check": "all"}]},
                "target_var_check_not_at_least_one",
            ),
        ):
            candidate = {
                **eligible,
                **mutation,
            }
            result = direct_foreach_preconditions(candidate)
            self.assertFalse(result["eligible"])
            self.assertIn(reason, result["reasons"])

        helper_target = {
            **eligible,
            "targets": [
                {
                    "context": "object_selector",
                    "var_check": "at least one",
                    "tests": [],
                    "object_features": {
                        "variable_entities": [
                            {"var_ref": "oval:test:var:1"}
                        ]
                    },
                }
            ],
        }
        result = direct_foreach_preconditions(helper_target)
        self.assertFalse(result["eligible"])
        self.assertIn(
            "first_proof_class_requires_directly_tested_target",
            result["reasons"],
        )


class DirectForeachEvidenceEquivalence(unittest.TestCase):
    def test_faithful_and_foreach_reduce_to_same_canonical_evidence(self):
        items = {
            "user-a": {"id":"user-a","fields":{"home_dir":{"datatype":"string","value":"/home/a"}}},
            "user-b": {"id":"user-b","fields":{"home_dir":{"datatype":"string","value":"/home/b"}}},
        }
        faithful = faithful_direct_evidence(
            source_object_ref="users",
            variable_result={
                "status":"complete",
                "item_refs":["user-a","user-b"],
                "values":[
                    {"datatype":"string","value":"/home/a"},
                    {"datatype":"string","value":"/home/b"},
                ],
            },
            items_by_id=items,
            item_field="home_dir",
            target_item_refs=["file-b","file-a"],
        )
        modern = foreach_direct_evidence(
            source_object_ref="users",
            bindings=[
                {"source_item_ref":"user-a","projected_values":[{"datatype":"string","value":"/home/a"}]},
                {"source_item_ref":"user-b","projected_values":[{"datatype":"string","value":"/home/b"}]},
            ],
            target_item_refs=["file-a","file-b"],
            status="complete",
        )
        self.assertTrue(evidence_equivalent(faithful, modern))

    def test_duplicate_values_preserve_source_item_provenance(self):
        items = {
            "user-a": {"id":"user-a","fields":{"home_dir":{"datatype":"string","value":"/shared"}}},
            "user-b": {"id":"user-b","fields":{"home_dir":{"datatype":"string","value":"/shared"}}},
        }
        faithful = faithful_direct_evidence(
            source_object_ref="users",
            variable_result={
                "status":"complete",
                "item_refs":["user-a","user-b"],
                "values":[
                    {"datatype":"string","value":"/shared"},
                    {"datatype":"string","value":"/shared"},
                ],
            },
            items_by_id=items,
            item_field="home_dir",
            target_item_refs=["file-shared"],
        )
        modern = foreach_direct_evidence(
            source_object_ref="users",
            bindings=[
                {"source_item_ref":"user-a","projected_values":[{"datatype":"string","value":"/shared"}]},
                {"source_item_ref":"user-b","projected_values":[{"datatype":"string","value":"/shared"}]},
            ],
            target_item_refs=["file-shared"],
            status="complete",
        )
        self.assertTrue(evidence_equivalent(faithful, modern))
        self.assertEqual(len(faithful["projected"]), 2)

    def test_different_target_population_is_not_equivalent(self):
        base = foreach_direct_evidence(
            source_object_ref="users",
            bindings=[{"source_item_ref":"user-a","projected_values":[{"datatype":"string","value":"/home/a"}]}],
            target_item_refs=["file-a"],
            status="complete",
        )
        changed = foreach_direct_evidence(
            source_object_ref="users",
            bindings=[{"source_item_ref":"user-a","projected_values":[{"datatype":"string","value":"/home/a"}]}],
            target_item_refs=["file-a","file-b"],
            status="complete",
        )
        self.assertFalse(evidence_equivalent(base, changed))

    def test_faithful_projection_mismatch_fails_closed(self):
        items = {
            "user-a": {"id":"user-a","fields":{"home_dir":{"datatype":"string","value":"/home/a"}}}
        }
        with self.assertRaises(ValueError):
            faithful_direct_evidence(
                source_object_ref="users",
                variable_result={
                    "status":"complete",
                    "item_refs":["user-a"],
                    "values":[{"datatype":"string","value":"/wrong"}],
                },
                items_by_id=items,
                item_field="home_dir",
                target_item_refs=[],
            )


class MachineReadableTransformationContract(unittest.TestCase):
    def test_rewrite_contract_matches_code_identifier_and_remains_disabled(self):
        contract_path = (
            Path(__file__).resolve().parents[1]
            / "research"
            / "assessment-simplification"
            / "foreach-07"
            / "transformation-v1.json"
        )
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
        self.assertEqual(contract["id"], DIRECT_FOREACH_REWRITE_ID)
        self.assertEqual(
            contract["desugaring"]["aggregation_boundary"],
            "target_object_population",
        )
        self.assertEqual(
            contract["source_pattern"]["effective_var_check"],
            "at least one",
        )
        self.assertFalse(contract["automatic_rewrite_enabled"])


class DownstreamTestResultEquivalence(unittest.TestCase):
    """If collection population/status are equal, all later Test scopes stay equal."""

    def test_complete_population_preserves_existence_and_check_results(self):
        items = ["a", "b", "c"]
        predicate = lambda item, value: item == value
        state_assignments = list(itertools.product((TRUE, FALSE), repeat=len(items)))
        value_sequences = [
            ["a"],
            ["b"],
            ["a", "b"],
            ["a", "a", "b"],
            ["a", "b", "c"],
            ["missing"],
        ]
        existence_modes = (
            "any_exist",
            "at_least_one_exists",
            "all_exist",
            "none_exist",
            "only_one_exists",
        )
        checks = ("all", "at least one", "only one", "none satisfy")

        for values in value_sequences:
            faithful = faithful_at_least_one_selection(items, values, predicate)
            modern = foreach_union_selection(items, values, predicate)
            self.assertTrue(equivalent_population(faithful, modern))
            for assignment in state_assignments:
                state_by_item = dict(zip(items, assignment))
                for existence in existence_modes:
                    for check in checks:
                        # The repository truth-table helper intentionally
                        # rejects State aggregation over an empty Item list.
                        # Preserve that unresolved corner separately instead of
                        # inventing vacuous truth for any CheckEnumeration.
                        if not faithful:
                            continue
                        with self.subTest(
                            values=values,
                            assignment=assignment,
                            existence=existence,
                            check=check,
                        ):
                            left = evaluate_population(
                                faithful,
                                existence=existence,
                                check=check,
                                state_by_item=state_by_item,
                            )
                            right = evaluate_population(
                                modern,
                                existence=existence,
                                check=check,
                                state_by_item=state_by_item,
                            )
                            self.assertEqual(left, right)

    def test_existence_only_tests_include_zero_item_cases(self):
        items = ["a", "b"]
        predicate = lambda item, value: item == value
        for values in ([], ["a"], ["a", "b"], ["missing"]):
            faithful = faithful_at_least_one_selection(items, values, predicate)
            modern = foreach_union_selection(items, values, predicate)
            for existence in (
                "any_exist",
                "at_least_one_exists",
                "all_exist",
                "none_exist",
                "only_one_exists",
            ):
                with self.subTest(values=values, existence=existence):
                    left = evaluate_population(
                        faithful,
                        existence=existence,
                        check="all",
                        state_by_item={},
                        has_state=False,
                    )
                    right = evaluate_population(
                        modern,
                        existence=existence,
                        check="all",
                        state_by_item={},
                        has_state=False,
                    )
                    self.assertEqual(left, right)


if __name__ == "__main__":
    unittest.main()
