"""Owner-review conformance for the proposed canonical 0.4.1 Result."""
import copy
import hashlib
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / 'proposed-schema' / 'result-0.4.1' / 'assessment-result.schema.json'
FIXTURES = ROOT / 'docs' / 'contracts' / 'evidence' / 'result-0.4.1'
EXPECTED_SHA256 = '1a3b4b68d4b54bdc71f66460e74dd8eb184d7fbec10bbc63941aee28e96adab2'
DIAGNOSTIC_SCHEMA = ROOT / 'proposed-schema' / 'result-0.4.1' / 'result-diagnostic.schema.json'
EXPECTED_DIAGNOSTIC_SHA256 = '7f322797deb2cd105e32f896e2a32c2f50a1723e7a2a510f30160f84049a7406'

class Result041Candidate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema_bytes = SCHEMA.read_bytes()
        cls.schema = json.loads(cls.schema_bytes)
        cls.validator = Draft202012Validator(cls.schema)

    def test_candidate_schema_is_exactly_pinned_and_meta_valid(self):
        self.assertEqual(hashlib.sha256(self.schema_bytes).hexdigest(), EXPECTED_SHA256)
        Draft202012Validator.check_schema(self.schema)
        self.assertEqual(self.schema['$id'], 'https://scap-ng.dev/schema/v0.4.1/assessment-result.schema.json')
        self.assertEqual(self.schema['x-scap-ng-version'], '0.4.1')

    def test_diagnostic_schema_is_separately_pinned_and_valid(self):
        data = DIAGNOSTIC_SCHEMA.read_bytes()
        self.assertEqual(hashlib.sha256(data).hexdigest(), EXPECTED_DIAGNOSTIC_SHA256)
        Draft202012Validator.check_schema(json.loads(data))

    def test_all_result_041_fixtures_validate(self):
        expected = {'pass.json', 'fail.json', 'unknown.json', 'incomplete.json',
                    'error.json', 'redacted.json', 'multi-item-multivalue.json',
                    'cardinality-fail.json', 'and-or.json', 'variables-inputs.json'}
        self.assertEqual({p.name for p in FIXTURES.glob('*.json')}, expected)
        for path in FIXTURES.glob('*.json'):
            with self.subTest(path=path.name):
                self.assertFalse(list(self.validator.iter_errors(json.loads(path.read_bytes()))))

    def test_expression_operator_preserves_terminal_test_and_groups(self):
        terminal = json.loads((FIXTURES / 'pass.json').read_bytes())
        self.assertEqual(terminal['expression']['operator'], 'test')
        self.assertEqual(terminal['expression']['test_refs'], ['/tests/rhel9-passwd-owner-test'])
        grouped = json.loads((FIXTURES / 'and-or.json').read_bytes())
        self.assertEqual(grouped['expression']['operator'], 'and')

    def test_unknown_and_error_cannot_carry_fabricated_comparisons(self):
        for name in ('unknown.json', 'incomplete.json', 'error.json'):
            doc = json.loads((FIXTURES / name).read_bytes())
            fields = doc['tests'][0]['require']['fields']
            self.assertEqual(fields, {}, name)
        doc = json.loads((FIXTURES / 'pass.json').read_bytes())
        doc['tests'][0]['require']['fields']['owner_uid']['outcome'] = 'unknown'
        doc['tests'][0]['require']['fields']['owner_uid']['expected'] = {'datatype': 'integer', 'status': 'exists', 'value': 0}
        self.assertTrue(list(self.validator.iter_errors(doc)))

    def test_redaction_has_no_value_and_multivalue_keeps_distinct_items(self):
        redacted = json.loads((FIXTURES / 'redacted.json').read_bytes())
        field = redacted['tests'][0]['require']['fields']['owner_uid']
        self.assertTrue(field['expected']['redacted'])
        self.assertNotIn('value', field['expected'])
        multi = json.loads((FIXTURES / 'multi-item-multivalue.json').read_bytes())
        self.assertEqual(len(multi['tests'][0]['items']), 2)
        self.assertEqual(len(multi['tests'][0]['require']['fields']['owner_uid']['observed']), 2)
