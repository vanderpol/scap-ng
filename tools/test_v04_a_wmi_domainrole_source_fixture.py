#!/usr/bin/env python3
"""#229/#232: pinned 0.4-A WMI record-entity Test result oracle fixtures."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from v04_a_wmi_domainrole_source_fixture import (
    EXPECTED_ROLES, ANCHORS, STAGE, compile_record_role_test,
    oracle_observed_record_test, source_fixtures, reference_scenarios,
)


def authored(test_id):
    return {
        "capability": "windows.wmi.query",
        "require": "at_least_one_exists_and_all_match",
        "states_match": "any",
        "states": [
            {"result": {"record": {"fields": {
                "domainrole": {"equals": role,
                               "require": "at_least_one_exists_and_all_match"}},
                "require": "at_least_one_exists_and_all_match"}}}
            for role in EXPECTED_ROLES[test_id]
        ],
    }


def fixture_sources():
    output = {}
    for i, (aid, names) in enumerate(sorted(ANCHORS.items())):
        output[f"authoring/windows/assessment-{i}.json"] = {
            "assessment": {"id": aid, "mode": "automated",
                           "tests": {name: authored(name) for name in names}}}
    return output


class WmiRoleSourceOracleTests(unittest.TestCase):
    def test_exact_source_three_tests_and_18_distinct_role_cases(self):
        entries = source_fixtures(fixture_sources())
        result = reference_scenarios(entries)
        self.assertEqual(result["stage"], STAGE)
        self.assertEqual(result["anchored_assessments"], 2)
        self.assertEqual(result["anchored_WMI_tests"], 3)
        self.assertEqual(result["complete_single_record_role_cases"], 18)
        self.assertTrue(all(x["observed"] == x["expected"] for x in result["cases"]))

    def test_all_six_domain_roles_classified_without_cross_branch_leak(self):
        for testid, expected_roles in EXPECTED_ROLES.items():
            test = compile_record_role_test(testid, authored(testid))
            for role in ("0", "1", "2", "3", "4", "5"):
                expected = "true" if role in expected_roles else "false"
                got = oracle_observed_record_test(test, {
                    "flag": "complete", "items": [{"result": {"domainrole": role}}]})
                with self.subTest(test=testid, role=role):
                    self.assertEqual(got["result"], expected)
                    self.assertFalse(got["windows_wmi_queried"])
                    self.assertFalse(got["scanner_executed"])

    def test_complete_zero_item_is_failure_not_pass(self):
        id = next(iter(EXPECTED_ROLES))
        test = compile_record_role_test(id, authored(id))
        result = oracle_observed_record_test(test, {"flag": "complete", "items": []})
        self.assertEqual(result["result"], "false")

    def test_incomplete_matching_item_does_not_prove_all_match(self):
        id = next(iter(EXPECTED_ROLES))
        test = compile_record_role_test(id, authored(id))
        got = oracle_observed_record_test(test, {
            "flag": "incomplete", "items": [{"result": {"domainrole": test["role_values"][0]}}]})
        self.assertEqual(got["result"], "unknown")

    def test_incomplete_nonmatch_is_decisive_failure(self):
        id = next(iter(EXPECTED_ROLES))
        test = compile_record_role_test(id, authored(id))
        got = oracle_observed_record_test(test, {
            "flag": "incomplete", "items": [{"result": {"domainrole": "999"}}]})
        self.assertEqual(got["result"], "false")

    def test_nonmatching_second_item_invalidates_all_requirement(self):
        id = next(iter(EXPECTED_ROLES))
        test = compile_record_role_test(id, authored(id))
        got = oracle_observed_record_test(test, {
            "flag": "complete",
            "items": [{"result": {"domainrole": test["role_values"][0]}},
                      {"result": {"domainrole": "999"}}]})
        self.assertEqual(got["result"], "false")

    def test_missing_or_wrongly_typed_record_is_error_not_absence(self):
        id = next(iter(EXPECTED_ROLES))
        test = compile_record_role_test(id, authored(id))
        for item in ({"result": {}}, {"result": {"domainrole": 3}},
                     {"result": {"domainrole": ["1", "3"]}},
                     {"result": {"domainrole": "1", "other": "extra"}},
                     {"wrong": "value"}):
            with self.subTest(item=item):
                result = oracle_observed_record_test(test, {
                    "flag": "complete", "items": [item]})
                self.assertEqual(result["result"], "error")

    def test_collection_error_unknown_and_not_applicable_preserved(self):
        id = next(iter(EXPECTED_ROLES))
        test = compile_record_role_test(id, authored(id))
        for flag, expected in (("error", "error"),
                               ("not collected", "unknown"),
                               ("not applicable", "not_applicable"),
                               ("does not exist", "false")):
            with self.subTest(flag=flag):
                got = oracle_observed_record_test(test, {"flag": flag, "items": []})
                self.assertEqual(got["result"], expected)

    def test_unapproved_quantifier_default_or_comparator_fails_closed(self):
        id = next(iter(EXPECTED_ROLES))
        for change in ("states_match", "record_require", "field_require",
                       "record_field_name", "extra_field", "value"):
            t = authored(id)
            if change == "states_match":
                t.pop("states_match")
            elif change == "record_require":
                t["states"][0]["result"]["record"]["require"] = "none_exist"
            elif change == "field_require":
                t["states"][0]["result"]["record"]["fields"]["domainrole"]["require"] = "none_exist"
            elif change == "record_field_name":
                t["states"][0]["result"]["record"]["fields"]["different"] = (
                    t["states"][0]["result"]["record"]["fields"].pop("domainrole"))
            elif change == "extra_field":
                t["states"][0]["result"]["record"]["fields"]["domainrole"]["unexpected"] = True
            elif change == "value":
                t["states"][0]["result"]["record"]["fields"]["domainrole"]["equals"] = "6"
            with self.subTest(change=change):
                with self.assertRaises(ValueError):
                    compile_record_role_test(id, t)

    def test_missing_or_duplicate_source_assessment_rejected(self):
        docs = fixture_sources()
        removed = deepcopy(docs)
        removed.pop(next(iter(removed)))
        with self.assertRaisesRegex(ValueError, "missing real WMI"):
            source_fixtures(removed)
        duplicate = deepcopy(docs)
        duplicate["authoring/shared/duplicate.json"] = deepcopy(next(iter(docs.values())))
        with self.assertRaisesRegex(ValueError, "duplicate source Assessment"):
            source_fixtures(duplicate)

    def test_invalid_collection_payload_rejected(self):
        id = next(iter(EXPECTED_ROLES))
        test = compile_record_role_test(id, authored(id))
        for bad in ({"flag": "maybe", "items": []},
                    {"flag": "complete", "items": None},
                    {"items": []}):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    oracle_observed_record_test(test, bad)


if __name__ == "__main__":
    unittest.main()
