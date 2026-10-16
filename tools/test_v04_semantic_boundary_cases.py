#!/usr/bin/env python3
"""Controlled semantic boundary checks; not a 0.4 scanner/evaluator.

Expected cases are hand-recorded in tests/v04-semantic-boundaries/cases.json.
Use OVAL 5.12.3 reference-combiner helpers and explicitly documented research
filter behavior; do not extrapolate unsupported nested-collector semantics.
"""
from copy import deepcopy
from itertools import product
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
from foreach_equivalence import (
    project_object_component_complete,
    faithful_at_least_one_selection,
    foreach_union_selection,
    faithful_all_selection,
    equivalent_population,
)

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

    def test_incomplete_exactly_one_existence_and_matching_are_joint(self):
        # A single observed failed State proves failure under exactly-one
        # existence: no future Item => match fails; any future Item =>
        # only-one existence fails.
        self.assertEqual(evaluate_collected_object_test(
            "incomplete", existence="only_one_exists",
            check="only one", exists=1, item_results=["false"]), "false")
        # A passing State cannot prove true before the Item count is final.
        self.assertEqual(evaluate_collected_object_test(
            "incomplete", existence="only_one_exists",
            check="at least one", exists=1, item_results=["true"]), "unknown")
        # All-exist is not monotonic, so later missing Items could invalidate it.
        self.assertEqual(evaluate_collected_object_test(
            "incomplete", existence="all_exist",
            check="at least one", exists=1, item_results=["true"]), "unknown")

    def test_incomplete_collections_only_return_irreversible_check_results(self):
        # Independent expected table, not computed by decisive_partial_check.
        # Each enumerated row is a *partial* observed population; unobserved
        # Items may have any of the six values. 0..3 observed Items exercises
        # 1,036 quantifier/population combinations.
        states = ("true", "false", "error", "unknown",
                  "not evaluated", "not applicable")
        checks = ("all", "at least one", "only one", "none satisfy")
        count = 0
        for n in range(4):
            for observed in product(states, repeat=n):
                for check in checks:
                    with self.subTest(observed=observed, check=check):
                        if check == "all" and "false" in observed:
                            expected = "false"
                        elif check == "at least one" and "true" in observed:
                            expected = "true"
                        elif check == "only one" and observed.count("true") >= 2:
                            expected = "false"
                        elif check == "none satisfy" and "true" in observed:
                            expected = "false"
                        else:
                            expected = "unknown"
                        self.assertEqual(evaluate_collected_object_test(
                            "incomplete", existence="at_least_one_exists",
                            has_state=True, check=check, exists=n,
                            item_results=list(observed)), expected)
                        count += 1
        self.assertEqual(count, 1036)

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

    def test_source_backed_rhel9_sv257889_foreach_is_one_object_population(self):
        # The RHEL9 source projects interactive users' home directories via
        # ObjectComponent/local Variable into one target Object selector.
        # This bounded proof only covers direct projection, complete source
        # collection, and target var_check='at least one'.
        users = [{"home_dir": "/home/alice"},
                 {"home_dir": ["/home/bob", "/srv/bob"]}]
        projection = project_object_component_complete(users, "home_dir")
        self.assertEqual(projection["status"], "values")
        candidates = [
            {"directory": "/home/alice", "name": ".vimrc", "pass": True},
            {"directory": "/home/bob", "name": ".bashrc", "pass": False},
            {"directory": "/srv/bob", "name": ".profile", "pass": True},
            {"directory": "/etc", "name": "passwd", "pass": True}]
        selector = lambda item, path: item["directory"] == path
        source = faithful_at_least_one_selection(
            candidates, projection["values"], selector)
        modern = foreach_union_selection(candidates, projection["values"], selector)
        self.assertTrue(equivalent_population(source, modern))
        self.assertEqual(len(source), 3)
        check_results = [("true" if x["pass"] else "false") for x in modern]
        # One Test over all collected target Items: some match => true.
        actual = evaluate_collected_object_test(
            "complete", existence="at_least_one_exists",
            check="at least one", exists=len(modern),
            item_results=check_results, has_state=True)
        self.assertEqual(actual, "true")
        # Incorrect per-home Tests AND-ed together => false. Do not make this
        # semantic transformation while authoring a collection for_each.
        separate = [
            evaluate_collected_object_test(
                "complete", existence="at_least_one_exists",
                check="at least one", exists=len(per_home),
                item_results=[("true" if x["pass"] else "false")
                              for x in per_home], has_state=True)
            for home in projection["values"]
            for per_home in [faithful_at_least_one_selection(candidates, [home], selector)]
        ]
        self.assertEqual(separate, ["true", "false", "true"])
        self.assertEqual(aggregate_check("all", separate), "false")

    def test_foreach_zero_and_missing_source_are_errors_not_empty_success(self):
        self.assertEqual(project_object_component_complete([], "home_dir")["status"],
                         "error")
        self.assertEqual(project_object_component_complete(
            [{"username": "alice"}], "home_dir")["status"], "error")

    def test_foreach_varcheck_all_must_not_use_union(self):
        targets = [{"directory": "x"}, {"directory": "y"}]
        predicate = lambda item, value: item["directory"] == value
        direct_all = faithful_all_selection(targets, ["x", "y"], predicate)
        expanded_any = foreach_union_selection(targets, ["x", "y"], predicate)
        self.assertEqual(direct_all, [])
        self.assertEqual(len(expanded_any), 2)
        self.assertFalse(equivalent_population(direct_all, expanded_any))

    def test_filtered_source_unknown_must_not_be_silently_skipped(self):
        # A non-Boolean filter-State outcome is a collection error in
        # the documented native contract, not "this user is excluded".
        filtered = ["true", "false", "unknown"]
        outcomes = [apply_filter_state_result("include", value)
                    for value in filtered]
        self.assertEqual(outcomes, [True, False, "error"])

    def test_research_scoped_require_does_not_inherit_into_record_members(self):
        source = {"assessment": {"tests": {"rec": {"states": [
            {"x": {"equals": 5, "require": REQUIRE}},
            {"result": {"record": {
                "require": "at_least_one_exists_and_some_match",
                "fields": {"domainrole": {
                    "equals": 5, "require": "only_one_exists_and_all_match"}}}}}
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
