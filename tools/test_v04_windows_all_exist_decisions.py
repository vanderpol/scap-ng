#!/usr/bin/env python3
"""Source-backed counterexamples; no new all_exist admission (#251)."""
import unittest
import xml.etree.ElementTree as ET

from audit_v04_windows_all_exist_decisions import analyze, fixture, CASES
from v04_expanded_source_proof import ExpandedSource, expanded_compare


class WindowsAllExistDecisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = analyze()

    def row(self, flag='complete', states=('true',), dne=0, err=0, nc=0):
        return next(r for r in self.report['vectors'] if r['flag'] == flag
            and r['item_results'] == list(states) and r['does_not_exist'] == dne
            and r['error'] == err and r['not_collected'] == nc)

    def test_pinned_three_tests_and_original_population_are_preserved(self):
        cases = self.report['cases']
        self.assertEqual([[t['id'] for t in c['tests']] for c in cases], [
            ['oval:mil.disa.stig.win:tst:25325900'],
            ['oval:mil.disa.stig.win:tst:25344600', 'oval:mil.disa.stig.win:tst:25344601']])
        wmi = cases[0]['tests'][0]
        self.assertIn('SELECT protectionstatus FROM win32_encryptablevolume', str(wmi['original_object']))
        self.assertNotIn('WHERE', str(wmi['original_object']))
        a, b = cases[1]['tests']
        self.assertEqual(a['object_id'], b['object_id'])
        self.assertNotEqual(a['original_state'], b['original_state'])
        for c in cases:
            for t in c['tests']:
                self.assertFalse(t['normalization_approved'])

    def test_complete_actual_items_only_exact_table_subset(self):
        eligible = [r for r in self.report['vectors'] if r['complete_actual_items_only']]
        self.assertTrue(eligible)
        self.assertTrue(all(r['equal'] for r in eligible))
        self.assertEqual(self.row(states=())['reference_helper_all_exist'], 'false')
        self.assertEqual(self.row(states=('true', 'false'))['reference_helper_all_exist'], 'false')

    def test_mixed_dne_counterexample_and_incomplete_counterexample_remain(self):
        mixed = self.row(dne=1)
        self.assertEqual((mixed['reference_helper_all_exist'], mixed['reference_helper_at_least_one_exists']), ('false', 'true'))
        partial = self.row(flag='incomplete', states=('false',))
        # Record the existing helper discrepancy rather than approving it as
        # original OVAL semantics or using it to admit a new normalization.
        self.assertEqual((partial['reference_helper_all_exist'], partial['reference_helper_at_least_one_exists']), ('unknown', 'false'))
        finding = self.report['source_text_counterexample']
        self.assertEqual(finding['source_text_expected_result'], 'false')
        schema = __import__('pathlib').Path(__file__).resolve().parents[1] / 'third_party/scap-1.4-schemas/oval_5.12.3/oval-results-schema.xsd'
        self.assertIn(finding['quote'], schema.read_text())
        self.assertFalse(mixed['complete_actual_items_only'])
        self.assertFalse(partial['complete_actual_items_only'])

    def test_error_unknown_collection_and_six_state_evidence_not_erased(self):
        self.assertEqual(self.row(flag='error')['reference_helper_all_exist'], 'error')
        self.assertEqual(self.row(flag='not collected')['reference_helper_all_exist'], 'unknown')
        for s in ('error', 'unknown', 'not evaluated', 'not applicable'):
            r = self.row(states=(s,))
            self.assertEqual(r['reference_helper_all_exist'], r['reference_helper_at_least_one_exists'])
            self.assertNotEqual(r['reference_helper_all_exist'], 'true')
        self.assertNotEqual(self.row(err=1)['reference_helper_all_exist'], self.row()['reference_helper_all_exist'])
        self.assertNotEqual(self.row(nc=1)['reference_helper_all_exist'], self.row()['reference_helper_all_exist'])

    def test_production_proof_admission_stays_closed(self):
        for number, pin in CASES:
            f = fixture(number, pin)
            source = ExpandedSource(ET.fromstring(f['source_xml']))
            result = expanded_compare(source, f['source_definition'], f['assessment'])
            self.assertEqual(result['outcome'], 'UNVERIFIABLE/UNSUPPORTED')
        self.assertEqual(self.report['normalizations_implemented'], 0)
        self.assertFalse(self.report['coverage_promoted'])


if __name__ == '__main__':
    unittest.main()
