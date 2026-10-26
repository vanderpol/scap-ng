"""Original WMI record boundaries and complete multi-capability source closures."""
from copy import deepcopy
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET
from unittest.mock import patch

from v04_direct_scap_source import SourceModel, UnsupportedSource, OVAL
from v04_direct_converter import CAPABILITIES, convert
from v04_direct_inventory import SourceInventory
from audit_v04_direct_benchmark import verify_original, verify_compiled
from v04_native_bundle_compiler import build_bundle
from v04_direct_authoring_examples import walk
from oval_result_truth_tables import evaluate_record_field, evaluate_record_entity

ROOT = Path(__file__).resolve().parents[1]
PINS = json.loads((ROOT / 'tests/fixtures/v04-direct-prototype/provenance.json').read_text())
O, W = '{' + OVAL + '}', '{' + OVAL + '#windows}'
CAP = 'windows.wmi.query'


class DirectWmiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SourceModel(ROOT / 'tests/fixtures/v04-direct-prototype' / PINS['fixture'], PINS['zip_sha256'])
        cls.rows = [r for r in SourceInventory(cls.source).rules() if CAP in r['needed_capabilities']]
        cls.rules = []
        cls.blocked = {}
        # Preserve the original WMI-only admission boundary. The separate
        # cmdlet suite proves the additional complete mixed closures.
        cls.catalog = tuple(c for c in CAPABILITIES if c != 'windows.cmdlet')
        for row in cls.rows:
            try:
                with patch('v04_direct_converter.CAPABILITIES', cls.catalog):
                    convert(cls.source, [row['source_rule']])
            except UnsupportedSource as error:
                cls.blocked[row['source_rule']] = str(error)
            else:
                cls.rules.append(row['source_rule'])
        cls.docs, cls.trace = convert(cls.source, cls.rules)

    def record_source(self, source):
        binding = next(b for b in self.trace['rules'] if sum(v['kind'] == 'state' and
            source.node(b['component'], k, 'state').tag == W + 'wmi57_state'
            for k, v in b['dependencies'].items()) == 1)
        sid = next(k for k, v in binding['dependencies'].items()
                   if v['kind'] == 'state' and source.node(binding['component'], k, 'state').tag == W + 'wmi57_state')
        return binding, source.node(binding['component'], sid, 'state').find(W + 'result')

    def test_all_18_original_wmi_closures_prove_compile_and_complete_five_user_rights_rules(self):
        self.assertEqual((len(self.rows), len(self.rules), len(self.blocked)), (26, 18, 8))
        self.assertNotIn('records', self.trace['unsupported'])
        self.assertIn('record-level Variables, nested records, record absence and masking', self.trace['unsupported'])
        self.assertEqual(len(verify_original(self.source.root, self.docs, self.trace)), 18)
        self.assertEqual(len(verify_compiled(self.docs, build_bundle(self.docs)[0])), 18)
        self.assertTrue(all(any(s in error for s in ('all_exist', 'cmdlet', 'user_test')) for error in self.blocked.values()))
        mixed = [r['source_rule'] for r in self.rows if 'windows.userright' in r['needed_capabilities']]
        self.assertEqual(len(mixed), 5)
        self.assertTrue(set(mixed) <= set(self.rules))
        for d in self.docs.values():
            if 'assessment' not in d:
                continue
            for obj in d['assessment'].get('shared_objects', {}).values():
                if obj['capability'] == CAP:
                    self.assertIn('wql equals', obj['object_title'])
                    self.assertIn('namespace equals', obj['object_title'])

    def test_original_record_and_field_datatypes_queries_and_names_are_preserved(self):
        records = [node['record'] for d in self.docs.values() if 'assessment' in d
                   for node in walk(d['assessment']) if 'record' in node]
        self.assertTrue(records)
        self.assertTrue(all(r['records_found'] == 'one_or_more' and r['records_matching'] == 'every' for r in records))
        # Original implicit strings that look numeric must remain strings.
        self.assertTrue(any(v.get('equals') == '2' and 'datatype' not in v
                            for r in records for v in r['fields'].values()))
        self.assertTrue(any(v.get('datatype') == 'integer' and v.get('less_than_or_equal') == 600
                            for r in records for v in r['fields'].values()))
        for binding in self.trace['rules']:
            a = next(d['assessment'] for d in self.docs.values() if d.get('assessment', {}).get('id') == binding['assessment'])
            self.assertNotIn('states', a)
        verify_original(self.source.root, self.docs, self.trace)

    def test_controlled_multi_field_record_stays_one_record_before_any_record_aggregation(self):
        source = deepcopy(self.source)
        binding, record = self.record_source(source)
        record[:] = []
        record.set('entity_check', 'at least one')
        for name, value in (('domainrole', '2'), ('name', 'example-host')):
            ET.SubElement(record, O + 'field', name=name).text = value
        for k, v in binding['dependencies'].items():
            if v['kind'] == 'object':
                obj = source.node(binding['component'], k, 'object')
                if obj.tag == W + 'wmi57_object':
                    obj.find(W + 'namespace').text = r'ROOT\CIMV2'
                    obj.find(W + 'wql').text = 'SELECT DomainRole, Name FROM Win32_ComputerSystem'
        source.index()
        docs, trace = convert(source, [binding['source_rule']])
        verify_original(source.root, docs, trace)
        verify_compiled(docs, build_bundle(docs)[0])
        a = next(d['assessment'] for d in docs.values() if 'assessment' in d)
        wrapper = next(n for n in walk(a) if 'record' in n)
        self.assertEqual(wrapper['record']['records_matching'], 'one_or_more')
        self.assertEqual(set(wrapper['record']['fields']), {'domainrole', 'name'})
        # Separate existential records could incorrectly borrow a field from
        # a different row; the independent term reader rejects that rewrite.
        test = next(t for t in a['tests'].values() if t['capability'] == CAP)
        condition = next(n for n in walk(test['require']) if n.get('fields', {}).get('result') is wrapper)
        fields = wrapper['record']['fields']
        aggregate = {k: v for k, v in condition.items() if k != 'fields'}
        condition.clear(); condition.update(aggregate)
        condition.update({'and': [{'fields': {'result': {'record': {'records_found': 'one_or_more',
            'records_matching': 'one_or_more', 'fields': {k: v}}}}} for k, v in fields.items()]})
        with self.assertRaises(AssertionError):
            verify_original(source.root, docs, trace)

    def test_missing_record_member_error_and_field_before_record_order_follow_original_xsd(self):
        xs = '{http://www.w3.org/2001/XMLSchema}'
        root = ET.parse(ROOT / 'third_party/scap-1.4-schemas/oval_5.12.3/oval-definitions-schema.xsd').getroot()
        text = ''.join(root.find(xs + 'complexType[@name="EntityStateFieldType"]').itertext())
        self.assertIn('an error should be reported', text)
        self.assertEqual(evaluate_record_field('domainrole', []), 'error')
        self.assertEqual(evaluate_record_entity(['true', 'error']), 'error')
        self.assertEqual(evaluate_record_entity(['true', 'false']), 'false')
        self.assertEqual(evaluate_record_entity(['true', 'true']), 'true')

    def test_source_record_invalid_comparators_names_context_variables_and_absence_reject(self):
        for mutation in ('comparator', 'duplicate', 'uppercase', 'namespace', 'field-existence', 'variable', 'absence', 'mask'):
            source = deepcopy(self.source)
            binding, record = self.record_source(source)
            if mutation == 'comparator': record.set('operation', 'not equal')
            elif mutation == 'duplicate': record.append(deepcopy(record[0]))
            elif mutation == 'uppercase': record[0].set('name', record[0].get('name').upper())
            elif mutation == 'namespace': record[0].tag = W + 'field'
            elif mutation == 'field-existence': record[0].set('check_existence', 'none_exist')
            elif mutation == 'variable': record.set('var_check', 'at least one')
            elif mutation == 'absence': record.set('check_existence', 'none_exist')
            else: record.set('mask', 'true')
            source.index()
            with self.subTest(mutation=mutation), self.assertRaises(UnsupportedSource):
                convert(source, [binding['source_rule']])


if __name__ == '__main__':
    unittest.main()
