"""Gap reporting distinguishes evidence stages and never promotes conversions."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

from v04_conversion_diagnostics import (classify_failure, summarize_failures,
    IMPLEMENTATION, SCHEMA, VARIABLE, OPERATION, SOURCE, EXTERNAL)
from report_v04_conversion_gaps import corpus_failures, dependency_for, acceptance_failures, additional_source_failures

ROOT = Path(__file__).resolve().parents[1]


class ConversionDiagnosticTests(unittest.TestCase):
    def test_additional_original_yaml_cases_keep_separate_denominators_and_specific_blockers(self):
        dependencies = json.loads((ROOT / 'tests/fixtures/v04-converter-schema-dependencies.json').read_text())
        rows, coverage = additional_source_failures(dependencies)
        self.assertEqual(len(coverage), 1)
        self.assertEqual(coverage[0]['original_tests'], 51)
        self.assertEqual(coverage[0]['compiled'], 45)
        self.assertEqual(coverage[0]['source_valid_nondeprecated_and_term_proved'], 45)
        self.assertEqual(len(rows), 6)
        self.assertTrue(all(r['scope'] == 'additional_original_test' for r in rows))
        summary = summarize_failures(rows)
        self.assertEqual(summary['cases_by_category'][VARIABLE], 3)
        self.assertEqual(summary['cases_by_category'][OPERATION], 3)
        self.assertTrue(all(r['source_validity']['status'] == 'VALID' for r in rows))

    def test_six_failure_categories_have_evidence_and_retain_messages(self):
        cases = [({}, 'unsupported Object field: behaviors', IMPLEMENTATION),
                 ({'dependency': {'id': 'review', 'category': SCHEMA, 'reason': 'Pinned nil path'}}, 'unsupported nil selector', SCHEMA),
                 ({}, 'Variable cast outside bounded proof', VARIABLE),
                 ({}, 'ordered comparison expansion requires integer source datatype', OPERATION),
                 ({'validity': {'status': 'INVALID', 'issues': []}}, 'original source failed', SOURCE),
                 ({'stage': 'infrastructure'}, 'HTTP 503 Egress is over the account limit', EXTERNAL)]
        for kwargs, message, expected in cases:
            with self.subTest(category=expected):
                result = classify_failure(message, **kwargs)
                self.assertEqual(result['category'], expected)
                self.assertEqual(result['message'], message)
                self.assertTrue(result['basis'])

    def test_native_schema_rejection_alone_does_not_establish_schema_limitation(self):
        self.assertEqual(classify_failure('algorithm missing', stage='schema')['category'], IMPLEMENTATION)
        self.assertEqual(classify_failure('independent proof differs', stage='source_proof')['category'], IMPLEMENTATION)

    def test_original_invalidity_and_deprecation_precede_reviewed_gap(self):
        dependency = {'id': 'schema-review', 'category': SCHEMA, 'reason': 'Reviewed source gap'}
        result = classify_failure('native schema failure', dependency=dependency,
            validity={'status': 'VALID', 'issues': [{'kind': 'deprecated'}]})
        self.assertEqual(result['category'], SOURCE)
        self.assertEqual(result['dependency_id'], 'schema-review')
        case = {'rule': 'rule', 'outcome': 'BLOCKED', 'required_capabilities': [],
                'diagnostic': json.dumps([{'category': 'source-invalid', 'message': 'unresolved catalog href'}])}
        records = acceptance_failures({'cases': [case]}, 'original.zip')
        self.assertEqual(records[0]['failures'][0]['category'], SOURCE)

    def test_summary_counts_cases_once_per_category(self):
        record = {'failures': [classify_failure('unsupported Object field: one'),
                               classify_failure('unsupported Object field: two')]}
        counts = summarize_failures([record])['cases_by_category']
        self.assertEqual(counts[IMPLEMENTATION], 1)
        self.assertEqual(sum(counts.values()), 1)

    def test_review_dependencies_match_only_exact_original_document_and_test(self):
        dependencies = json.loads((ROOT / 'tests/fixtures/v04-converter-schema-dependencies.json').read_text())
        row = dependencies['cases'][0]
        self.assertEqual(dependency_for(row['document'], row['test_ids'][0], dependencies), row)
        self.assertIsNone(dependency_for('other.xml', row['test_ids'][0], dependencies))
        self.assertIsNone(dependency_for(row['document'], 'oval:unreviewed:tst:1', dependencies))
        root = ROOT / 'tests/fixtures/v04-direct-schema-dependencies'
        source = root / 'unix-def_sshd_test.xml'
        pin = next(r for r in dependencies['cases'] if r['capability'] == 'unix.sshd')
        self.assertEqual(sha256(source.read_bytes()).hexdigest(), pin['source_sha256'])
        original = ET.parse(source).getroot()
        nil = '{http://www.w3.org/2001/XMLSchema-instance}nil'
        self.assertEqual(sum(n.get(nil) == 'true' for n in original.iter()), 3)

    def test_report_preserves_proved_but_source_invalid_cases_without_admission(self):
        case = {'document': 'test.xml', 'test': 'test', 'capability': 'cap',
                'configured_baseline': {'source_proof': 'PROVED', 'diagnostics': []}}
        report = {'cases': [case]}
        before = deepcopy(report)
        records = corpus_failures(report, {('test.xml', 'test'): {'status': 'INVALID', 'issues': []}}, {'cases': []})
        self.assertEqual(records[0]['conversion_source_proof'], 'PROVED')
        self.assertEqual(records[0]['failures'][0]['category'], SOURCE)
        self.assertEqual(report, before)
        self.assertEqual(corpus_failures(report, {('test.xml', 'test'): {'status': 'VALID', 'issues': []}}, {'cases': []}), [])


if __name__ == '__main__':
    unittest.main()
