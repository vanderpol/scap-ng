#!/usr/bin/env python3
import itertools
import unittest

from foreach_equivalence import (
    UNARY_CONCAT_FOREACH_REWRITE_ID,
    project_object_component_complete,
    unary_concat_foreach_desugaring,
    unary_concat_foreach_preconditions,
    unary_concat_selection_equivalent,
    unary_literal_concat_values,
)


def dconf_candidate(**expression_overrides):
    expression = {
        "kind": "unary_concat_object_projection",
        "collection_operands": 1,
        "dynamic_operands": 1,
        "nested_functions": 0,
        "source_datatype": "string",
        "record_field": None,
        "prefix": "/etc/dconf/db/",
        "suffix": ".d/locks",
    }
    expression.update(expression_overrides)
    return {
        "candidate_family": "collection_expansion_at_least_one",
        "variable_id": "dconf-user-database-locks-directories",
        "expression": expression,
        "targets": [
            {
                "context": "object_selector",
                "entity": "path",
                "var_check": "at least one",
                "tests": [{"test_type": "textfilecontent54_test"}],
                "object_features": {
                    "variable_entities": [
                        {
                            "entity": "path",
                            "var_ref": "dconf-user-database-locks-directories",
                        }
                    ]
                },
            }
        ],
    }


class UnaryConcatForeachTests(unittest.TestCase):
    def test_maps_one_collection_operand_through_literal_prefix_suffix(self):
        self.assertEqual(
            unary_literal_concat_values(
                ["local", "site"],
                prefix="/etc/dconf/db/",
                suffix=".d/locks",
            ),
            [
                "/etc/dconf/db/local.d/locks",
                "/etc/dconf/db/site.d/locks",
            ],
        )

    def test_selector_population_identity_over_small_matrix(self):
        target_items = [
            "/etc/dconf/db/local.d/locks",
            "/etc/dconf/db/site.d/locks",
            "/etc/dconf/db/other.d/locks",
        ]
        predicate = lambda item, value: item == value
        source_values = ["local", "site", "other"]

        for width in range(1, len(source_values) + 1):
            for values in itertools.combinations(source_values, width):
                with self.subTest(values=values):
                    self.assertTrue(
                        unary_concat_selection_equivalent(
                            target_items,
                            values,
                            predicate,
                            prefix="/etc/dconf/db/",
                            suffix=".d/locks",
                        )
                    )

    def test_duplicate_source_values_preserve_target_population(self):
        self.assertTrue(
            unary_concat_selection_equivalent(
                ["/etc/dconf/db/local.d/locks"],
                ["local", "local"],
                lambda item, value: item == value,
                prefix="/etc/dconf/db/",
                suffix=".d/locks",
            )
        )

    def test_desugaring_retains_object_component_and_concat(self):
        graph = unary_concat_foreach_desugaring(
            source_object="dconf-user-databases",
            item_field="subexpression",
            prefix="/etc/dconf/db/",
            suffix=".d/locks",
            target_object="locked-setting-lines",
            target_entity="path",
            operation="equals",
            datatype="string",
        )
        self.assertEqual(
            graph["rewrite_id"],
            UNARY_CONCAT_FOREACH_REWRITE_ID,
        )
        expression = graph["variable"]["expression"]
        self.assertEqual(expression["kind"], "concat")
        self.assertEqual(
            [x["kind"] for x in expression["operands"]],
            ["literal", "object_component", "literal"],
        )
        self.assertEqual(
            graph["selector"]["var_check"],
            "at least one",
        )

    def test_zero_source_items_still_error_before_concat(self):
        projected = project_object_component_complete([], "subexpression")
        self.assertEqual(projected["status"], "error")
        self.assertEqual(projected["reason"], "source_object_has_no_items")

    def test_real_dconf_shape_is_in_bounded_proof_class(self):
        report = unary_concat_foreach_preconditions(dconf_candidate())
        self.assertTrue(report["eligible"])
        self.assertEqual(
            report["rewrite_id"],
            UNARY_CONCAT_FOREACH_REWRITE_ID,
        )
        self.assertEqual(report["reasons"], [])

    def test_two_dynamic_operands_are_rejected(self):
        report = unary_concat_foreach_preconditions(
            dconf_candidate(
                collection_operands=2,
                dynamic_operands=2,
            )
        )
        self.assertFalse(report["eligible"])
        self.assertIn(
            "requires_exactly_one_collection_valued_operand",
            report["reasons"],
        )
        self.assertIn(
            "requires_exactly_one_dynamic_operand",
            report["reasons"],
        )

    def test_nested_function_is_rejected(self):
        report = unary_concat_foreach_preconditions(
            dconf_candidate(nested_functions=1)
        )
        self.assertFalse(report["eligible"])
        self.assertIn(
            "nested_functions_not_in_first_unary_concat_class",
            report["reasons"],
        )

    def test_state_or_filter_consumer_is_rejected(self):
        candidate = dconf_candidate()
        candidate["targets"][0]["context"] = "state_filter"
        report = unary_concat_foreach_preconditions(candidate)
        self.assertFalse(report["eligible"])
        self.assertIn("consumer_is_not_object_selector", report["reasons"])

    def test_var_check_all_is_rejected(self):
        candidate = dconf_candidate()
        candidate["targets"][0]["var_check"] = "all"
        report = unary_concat_foreach_preconditions(candidate)
        self.assertFalse(report["eligible"])
        self.assertIn(
            "target_var_check_not_at_least_one",
            report["reasons"],
        )


if __name__ == "__main__":
    unittest.main()
