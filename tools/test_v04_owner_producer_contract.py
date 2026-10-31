"""Fresh bounded source conversion; archived authoring/programs untouched (#255/#268)."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
import xml.etree.ElementTree as ET

from audit_v04_oval_test_corpus import OvalDocument
from generate_capability_schema_v04 import generate
from test_generate_capability_schema_v04 import validate as generated_errors
from validate_native_json_schemas import build_validators, document_errors
from v04_direct_authoring_contract import test_requirement
from v04_direct_converter import AssessmentConverter, convert, load_mappings
from v04_direct_scap_source import SourceModel, UnsupportedSource, native_identifier
from v04_expanded_source_proof import ExpandedSource, expanded_compare
from v04_source_package_semantics import Native
from v04_native_bundle_compiler import build_bundle, compile_assessment_program

ROOT = Path(__file__).resolve().parents[1]


class OwnerProducerContract(unittest.TestCase):
    def test_source_pair_materialized_and_equal_local_pair_removed_without_boundary_loss(self):
        original = {'items_found': 'one_or_more', 'items_satisfying': 'every', 'and': [
            {'fields': {'type': {'equals': 'dword', 'values_found': 'one_or_more', 'values_matching': 'every'}}},
            {'fields': {'value': {'equals': 1, 'values_found': 'one_or_more', 'values_matching': 'one_or_more'}}}]}
        result = test_requirement(original)
        self.assertEqual(result['field_requirement'], {'values_found': 'one_or_more', 'values_matching': 'every'})
        self.assertEqual(result['and'][0], {'fields': {'type': {'equals': 'dword'}}})
        self.assertEqual(result['and'][1], original['and'][1])
        self.assertEqual(len(result['and']), 2)
        self.assertEqual(test_requirement(result), result)
        self.assertIn('values_found', original['and'][0]['fields']['type'])

    def test_no_editor_suggestion_can_supply_missing_source_comparison_counts(self):
        for field in ({'equals': 1}, {'equals': 1, 'values_found': 'one_or_more'},
                      {'equals': 1, 'values_matching': 'every'}):
            with self.subTest(field=field), self.assertRaises(ValueError):
                test_requirement({'items_found': 'one_or_more', 'items_satisfying': 'every', 'fields': {'value': field}})

    def test_item_presence_exemption_field_absence_and_optional_spelling(self):
        self.assertEqual(test_requirement({'items_found': 'may_be_absent'}), {'items_found': 'zero_or_more'})
        self.assertEqual(test_requirement({'items_found': 'none'}), {'items_found': 'none'})
        absent = test_requirement({'items_found': 'one_or_more', 'items_satisfying': 'every',
                                  'fields': {'name': {'values_found': 'none'}}})
        self.assertEqual(absent['fields']['name'], {'values_found': 'none'})
        original = {'items_found': 'one_or_more', 'items_satisfying': 'every', 'fields': {
            'value': {'equals': 'may_be_absent', 'values_found': 'may_be_absent', 'values_matching': 'every'}}}
        result = test_requirement(original)
        self.assertEqual(result['fields']['value']['equals'], 'may_be_absent')
        self.assertEqual(result['field_requirement']['values_found'], 'zero_or_more')

    def test_names_are_bounded_readable_source_ids_external_and_collisions_rejected(self):
        first = ET.Element('test', id='oval:source:tst:1', comment='Verify owner permissions')
        second = ET.Element('test', id='oval:source:tst:2', comment='Verify owner permissions')
        self.assertEqual(native_identifier(first, 'test'), 'verify-owner-permissions-test')
        self.assertEqual(native_identifier(first, 'test'), native_identifier(second, 'test'))
        first.set('comment', 'Meaningful purpose ' * 100)
        self.assertLessEqual(len(native_identifier(first, 'assessment')), 64)
        converter = AssessmentConverter(SimpleNamespace(), 'fixture', [])
        first.set('comment', 'Verify owner permissions')
        converter.native_name(first, 'test')
        with self.assertRaisesRegex(UnsupportedSource, 'collision.*oval:source:tst:1.*oval:source:tst:2'):
            converter.native_name(second, 'test')
        self.assertEqual(first.get('id'), 'oval:source:tst:1')

    def test_record_members_inherit_without_losing_correlation_or_exceptions(self):
        pair = {'values_found': 'one_or_more', 'values_matching': 'every'}
        original = {'items_found': 'one_or_more', 'items_satisfying': 'every', 'fields': {
            'result': {'record': {'records_found': 'one_or_more', 'records_matching': 'exactly_one',
                'fields': {'name': {'equals': 'Example', **pair},
                           'value': {'equals': 'Allowed', 'values_found': 'one_or_more', 'values_matching': 'one_or_more'}}}}}}
        result = test_requirement(original)
        reader = Native({'tests': {}, 'mode': 'automated', 'specification': {
            'id': 'scap-ng.pre-alpha.assessment', 'version': '0.4.0'}})
        self.assertEqual(reader.condition(original), reader.condition(result))
        record = result['fields']['result']['record']
        self.assertEqual(record['records_matching'], 'exactly_one')
        self.assertNotIn('values_found', record['fields']['name'])
        self.assertEqual(record['fields']['value']['values_matching'], 'one_or_more')

    def test_original_windows_two_rule_schema_generated_contract_compile_and_fresh_proof(self):
        folder = ROOT / 'tests/fixtures/v04-direct-prototype'
        pin = json.loads((folder / 'provenance.json').read_text())
        archive = folder / pin['fixture']
        original_hash = sha256(archive.read_bytes()).hexdigest()
        source = SourceModel(archive, pin['zip_sha256'])
        documents, trace = convert(source, pin['rules'])
        validators = build_validators(ROOT / 'schema/v0.4.0')
        for document in documents.values():
            kind, = document
            self.assertEqual(list(document_errors(validators[kind + '.schema.json'], document)), [])
        self.assertEqual(len(trace['rules']), 2)
        for row in trace['rules']:
            assessment = next(d['assessment'] for d in documents.values()
                              if 'assessment' in d and d['assessment']['id'] == row['assessment'])
            self.assertNotIn('purpose', assessment)
            self.assertLessEqual(len(assessment['id']), 64)
            self.assertTrue(row['authoring_contract_migration']['requires_fresh_proof'])
            for ident, test in assessment['tests'].items():
                self.assertLessEqual(len(ident), 64)
                self.assertIn('reported_elements', test)
                mapping = next(m for m in load_mappings() if m['capability'] == test['capability'])
                self.assertEqual(generated_errors(generate(mapping, ROOT), 'test', test), [])
            result = expanded_compare(ExpandedSource(source.components[row['component']]), row['definition'],
                                      assessment, invocation_purpose='assessment')
            self.assertEqual(result['outcome'], 'PROVED')
            self.assertFalse(result['historical_root_purpose_metadata'])
        build_bundle(documents)
        self.assertEqual(original_hash, sha256(archive.read_bytes()).hexdigest())

    def test_pinned_rhel_definition_new_authoring_proof_and_invocation_context(self):
        folder = ROOT / 'tests/fixtures/v04-independent-validation'
        case = json.loads((folder / 'SV-257851.json').read_text())
        raw = (folder / 'SV-257851.xml').read_bytes()
        self.assertEqual(sha256(raw).hexdigest(), case['source_slice_sha256'])
        original = ET.fromstring(raw)
        converter = AssessmentConverter(OvalDocument(original, 'original.xml'), 'original.xml', load_mappings())
        evaluate = converter.reference(case['source_definition'], 'definition')
        assessment = {'id': 'home-mount-nosuid-assessment', 'version': 1, 'assessment_title': 'Home mount nosuid',
            'mode': 'automated', 'class': 'compliance', 'specification': {
                'id': 'scap-ng.pre-alpha.assessment', 'version': '0.4.0'}, 'tests': converter.tests, 'evaluate': evaluate}
        validator = build_validators(ROOT / 'schema/v0.4.0')['assessment.schema.json']
        self.assertEqual(list(document_errors(validator, {'assessment': assessment})), [])
        compile_assessment_program(assessment)
        for purpose in (None, 'assessment', 'applicability'):
            result = expanded_compare(ExpandedSource(original), case['source_definition'], assessment,
                                      invocation_purpose=purpose)
            self.assertEqual(result['outcome'], 'PROVED')
            self.assertEqual(result['invocation_purpose'], purpose)
        changed = deepcopy(assessment); changed['class'] = 'vulnerability'
        with self.assertRaisesRegex(ValueError, 'class boundary'):
            expanded_compare(ExpandedSource(original), case['source_definition'], changed)
        self.assertIn('purpose', case['native']['assessment'])  # Archived witness stays unchanged.


if __name__ == '__main__': unittest.main()
