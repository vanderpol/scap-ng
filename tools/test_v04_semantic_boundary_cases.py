#!/usr/bin/env python3
"""Controlled semantic boundary checks; not a 0.4 scanner/evaluator.

Expected cases are hand-recorded in tests/v04-semantic-boundaries/cases.json.
Use OVAL 5.12.3 reference-combiner helpers and explicitly documented research
filter behavior; do not extrapolate unsupported nested-collector semantics.
"""
from copy import deepcopy
import json
from pathlib import Path
import unittest

from oval_result_truth_tables import (
    aggregate_check,
    aggregate_many_to_many,
    apply_filter_state_result,
    apply_variable_reference_context,
    combine_set_flags,
    evaluate_collected_object_test,
    evaluate_record_entity,
    evaluate_record_field,
    resolve_variable_reference,
)
from research_04_scoped_state_require import compact, expand

FIXTURES = json.loads((Path(__file__).resolve().parents[1] /
    "tests/v04-semantic-boundaries/cases.json").read_text())
REQUIRE = "at_least_one_exists_and_all_match"


class SourcePinnedBoundaryTests(unittest.TestCase):
    def test_pinned_expected_collected_item_outcomes(self):
        for case in FIXTURES["collected"]:
            with self.subTest(case=case["id"]):
                kwargs = {key: deepcopy(case[key]) for key in
                    ("flag", "existence", "check", "has_state", "exists",
                     "does_not_exist", "error", "not_collected", "item_results")
                    if key in case}
                self.assertEqual(evaluate_collected_object_test(**kwargs), case["expected"])

    def test_record_and_record_member_scopes_are_independent(self):
        for case in FIXTURES["records"]:
            with self.subTest(case=case["id"]):
                record_results = []
                for record in case["records"]:
                    member_results = [
                        evaluate_record_field(
                            member["name"], member["comparisons"],
                            member.get("entity_check", "all"))
                        for member in record["fields"]]
                    record_results.append(evaluate_record_entity(member_results))
                actual = aggregate_check(case["record_check"], record_results)
                self.assertEqual(actual, case["expected"])

    def test_cross_record_witnesses_dont_satisfy_one_record(self):
        # Two records each satisfy a different required member; the Assessment
        # must not cherry-pick a passing member from each record.
        r = [x for x in FIXTURES["records"]
             if x["id"] == "cross-record-witnesses-must-not-be-flattened"][0]
        self.assertEqual(
            aggregate_check("at least one", [
                evaluate_record_entity([
                    evaluate_record_field(f["name"], f["comparisons"])
                    for f in record["fields"]])
                for record in r["records"]]), "false")
        flattened = [
            aggregate_check("at least one", [
                evaluate_record_field(member["name"], member["comparisons"])
                for record in r["records"]
                for member in record["fields"] if member["name"] == name])
            for name in ("x", "y")]
        self.assertEqual(flattened, ["true", "true"])
        self.assertEqual(evaluate_record_entity(flattened), "true")

    def test_variable_value_match_before_entity_check(self):
        for case in FIXTURES["many_to_many"]:
            with self.subTest(case=case["id"]):
                actual = aggregate_many_to_many(
                    var_check=case["var_check"],
                    entity_check=case["entity_check"],
                    comparison_rows=case["rows"])
                self.assertEqual(actual, case["expected"])

    def test_filter_unknown_error_never_looks_like_absence(self):
        for case in FIXTURES["filters"]:
            with self.subTest(case=case["id"]):
                self.assertEqual(
                    apply_filter_state_result(case["action"], case["state_result"]),
                    case["expected"])

    def test_set_operator_flag_precedence(self):
        for case in FIXTURES["set_flags"]:
            with self.subTest(case=case["id"]):
                self.assertEqual(
                    combine_set_flags(case["operator"], case["first"], case["second"]),
                    case["expected"])

    def test_zero_value_variable_depends_on_reference_site(self):
        zero = resolve_variable_reference([])
        self.assertEqual(zero["values"], [])
        for case in FIXTURES["zero_variables"]:
            with self.subTest(case=case["id"]):
                self.assertEqual(
                    apply_variable_reference_context(zero, case["context"]),
                    case["expected"])

    def test_research_scoped_require_does_not_inherit_into_record_members(self):
        source = {"assessment": {"tests": {"rec": {"states": [
            {"x": {"equals": 5, "require": REQUIRE}},
            {"result": {"record": {
                "require": "at_least_one_exists_and_some_match",
                "fields": {"domainrole": {
                    "equals": 5, "require": "only_one_exists_and_all_match"}}}}
        ]}}}}
        compacted, _ = compact(source)
        restored = expand(compacted)
        self.assertEqual(restored, source)
        record = compacted["assessment"]["tests"]["rec"]["states"][1]["result"]["record"]
        self.assertEqual(record["require"], "at_least_one_exists_and_some_match")
        self.assertEqual(record["fields"]["domainrole"]["require"],
                         "only_one_exists_and_all_match")

    def test_research_scope_rejects_hidden_defaults(self):
        invalid = {"assessment": {"tests": {"x": {"states": [
            {"domainrole": {"equals": 5}}]}}}}
        with self.assertRaisesRegex(ValueError, "Hidden default"):
            expand(invalid)

    def test_research_scope_rejects_same_value_leaf_override(self):
        invalid = {"assessment": {"tests": {"x": {
            "state_fields_require": REQUIRE,
            "states": [{"x": {"equals": 5, "require": REQUIRE}}]}}}}
        with self.assertRaisesRegex(ValueError, "Redundant"):
            expand(invalid)


if __name__ == "__main__":
    unittest.main()
