#!/usr/bin/env python3
"""Focused source-backed canonical requirement and six-state oracle guards."""
import unittest
from copy import deepcopy
from pathlib import Path

from v04_canonical_requirement_oracle import (
    comparison_matrix, compare_original_to_canonical, describe, source_axes,
)
from build_v04_canonical_six_stigs import promote
from v04_flat_object_authoring import flatten_document, load_catalog


class SourceRequirementOracleTests(unittest.TestCase):
    def _docs(self, old):
        source = {"authoring/demo/a.json": {"assessment": {
            "id": "a", "mode": "automated", "tests": {"test": old}}}}
        newer = {path: promote(doc)[0] for path, doc in source.items()}
        return source, newer

    def test_state_free_absence_retains_oval_none_exist(self):
        source, newer = self._docs({
            "capability": "unix.file", "require": "none_exist"})
        r = compare_original_to_canonical(source, newer)
        self.assertEqual(r["test_population"]["converted_presence"], 1)
        self.assertFalse(r["scanner_parity"])
        self.assertGreater(r["generic_scenarios"], 0)

    def test_all_match_preserves_distinct_item_and_field_requirements(self):
        old = {
            "capability": "windows.registry",
            "object": {"capability": "windows.registry"},
            "require": "at_least_one_exists_and_all_match",
            "states": [{"value": {"equals": 0,
                                  "require": "at_least_one_exists_and_all_match"}}],
        }
        source, newer = self._docs(old)
        result = compare_original_to_canonical(source, newer)
        self.assertEqual(result["test_population"]["converted_all_items"], 1)
        canonical = newer["authoring/demo/a.json"]["assessment"]["tests"]["test"]
        self.assertEqual(canonical["require"]["items_found"], "one_or_more")
        self.assertEqual(canonical['require']['fields']['value'],
                         {'equals': 0, 'values_found': 'one_or_more', 'values_matching': 'every'})
        self.assertNotIn("capability", canonical["object"])

    def test_flat_object_promotion_must_be_source_exact(self):
        source, prefixed = self._docs({
            "capability": "unix.file",
            "object": {"capability": "unix.file",
                       "select": {"full_path": {"equals": "/etc/real.conf"}}},
            "require": "none_exist",
        })
        catalog = load_catalog(Path(__file__).resolve().parents[1] /
                               "schema/v0.4.0/capability-mappings/supported")
        name = "authoring/demo/a.json"
        flat, inverse = flatten_document(prefixed[name], catalog)
        self.assertTrue(inverse["edits"])
        canonical = {name: flat}
        report = compare_original_to_canonical(source, canonical)
        self.assertEqual(report["source_exact_promotion"], "PASS")
        self.assertEqual(report["test_population"]["converted_presence"], 1)
        mutated = deepcopy(canonical)
        mutated[name]["assessment"]["tests"]["test"]["object"][
            "full_path"]["equals"] = "/etc/altered.conf"
        with self.assertRaisesRegex(ValueError, "differs from exact source"):
            compare_original_to_canonical(source, mutated)
        with self.assertRaisesRegex(ValueError, "differs from exact source"):
            compare_original_to_canonical(source, prefixed)

    def test_unsupported_matching_remains_exception(self):
        source, newer = self._docs({
            "capability": "unix.file", "require": "at_least_one_exists_and_some_match",
            "states": [{"mode": {"equals": "0700", "require": "at_least_one_exists_and_all_match"}}]})
        self.assertEqual(source_axes(source['authoring/demo/a.json']['assessment']['tests']['test']),
                         ('at_least_one_exists', 'at least one', True))
        result = compare_original_to_canonical(source, newer)
        self.assertEqual(result['test_population']['converted_all_items'], 1)
        self.assertFalse(result['source_exception_matching_equivalence_proved'])

    def test_source_change_or_fake_result_fails(self):
        source, newer = self._docs({
            "capability": "unix.file", "require": "at_least_one_exists",
        })
        newer["authoring/demo/a.json"]["assessment"]["tests"]["test"][
            "require"]["items"] = "none"
        with self.assertRaisesRegex(ValueError, "differs from exact source"):
            compare_original_to_canonical(source, newer)

    def test_all_supported_existence_modes_have_matrix(self):
        for found in ('one_or_more', 'none', 'exactly_one', 'may_be_absent'):
            req = {'items_found': found}
            self.assertGreater(comparison_matrix(describe(req))['compared'], 0)

    def test_source_all_exist_is_not_silently_declared_equivalent(self):
        # The owner-approved structural crosswalk deliberately loses this source
        # axis. Provenance retains it; this oracle must never claim equivalence.
        source, newer = self._docs({'capability': 'unix.file', 'require': 'all_exist'})
        with self.assertRaisesRegex(AssertionError, 'does not match source'):
            compare_original_to_canonical(source, newer)

    def test_explicit_contract_normalization_is_distinct_from_field_and_state_axes(self):
        from v04_all_exist_normalization import CONTRACT
        source, newer = self._docs({'capability': 'unix.file', 'require': 'all_exist'})
        report = compare_original_to_canonical(source, newer, collection_contract=CONTRACT)
        self.assertFalse(report['unrestricted_original_axes_equivalent'])
        self.assertEqual(len(report['test_existence_normalizations']), 1)
        # State-bearing / field every is not authorized by the state-free pin.
        source, newer = self._docs({'capability': 'unix.file',
            'require': 'all_exist_and_all_match', 'states': [
                {'mode': {'equals': '0600', 'require': 'all_exist_and_all_match'}}]})
        self.assertEqual(newer['authoring/demo/a.json']['assessment']['tests']['test']
                         ['require']['fields']['mode']['values_found'], 'every')
        with self.assertRaisesRegex(AssertionError, 'does not match source'):
            compare_original_to_canonical(source, newer, collection_contract=CONTRACT)


if __name__ == "__main__":
    unittest.main()
