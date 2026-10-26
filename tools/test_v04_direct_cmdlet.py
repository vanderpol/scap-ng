"""Original cmdlet invocation records, nil constraints and structured results."""
from copy import deepcopy
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

import yaml
from v04_direct_scap_source import SourceModel, UnsupportedSource, OVAL
from v04_direct_inventory import SourceInventory
from v04_direct_converter import convert
from v04_expanded_source_proof import ExpandedSource
from v04_direct_yaml import authoring_yaml
from v04_direct_authoring_examples import authoring_statistics, walk
from audit_v04_direct_benchmark import verify_original, verify_compiled
from v04_native_bundle_compiler import build_bundle
from validate_native_json_schemas import build_validators, document_errors

ROOT = Path(__file__).resolve().parents[1]
PINS = json.loads((ROOT / 'tests/fixtures/v04-direct-prototype/provenance.json').read_text())
O, W = '{' + OVAL + '}', '{' + OVAL + '#windows}'
NIL = '{http://www.w3.org/2001/XMLSchema-instance}nil'
CAP = 'windows.cmdlet'


class DirectCmdletTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SourceModel(ROOT / 'tests/fixtures/v04-direct-prototype' / PINS['fixture'], PINS['zip_sha256'])
        cls.rows = [r for r in SourceInventory(cls.source).rules() if CAP in r['needed_capabilities']]
        cls.rules, cls.blocked = [], []
        for row in cls.rows:
            try:
                convert(cls.source, [row['source_rule']])
            except UnsupportedSource as error:
                cls.blocked.append((row, str(error)))
            else:
                cls.rules.append(row['source_rule'])
        cls.docs, cls.trace = convert(cls.source, cls.rules)

    def input_object(self, source):
        binding = self.trace['rules'][0]
        identifier = next(k for k, v in binding['dependencies'].items() if v['kind'] == 'object' and
                          source.node(binding['component'], k, 'object').tag == W + 'cmdlet_object')
        return binding, source.node(binding['component'], identifier, 'object')

    def test_six_original_closures_validate_compile_prove_and_roundtrip_including_two_wmi(self):
        self.assertEqual(len(self.rows), 7)
        self.assertEqual(len(self.rules), 6)
        self.assertEqual(sum('windows.wmi.query' in r['needed_capabilities'] for r in self.rows), 2)
        self.assertEqual(len(verify_original(self.source.root, self.docs, self.trace)), 6)
        self.assertEqual(len(verify_compiled(self.docs, build_bundle(self.docs)[0])), 6)
        validators = build_validators(ROOT / 'schema/v0.4.0')
        for doc in self.docs.values():
            self.assertEqual(yaml.safe_load(authoring_yaml(doc)), doc)
            if 'assessment' in doc:
                self.assertFalse(list(document_errors(validators['assessment.schema.json'], doc)))
        self.assertEqual(authoring_statistics(self.docs)['deprecated_grammar'], 0)
        self.assertTrue(any(n.get('equals') == '100' for d in self.docs.values() for n in walk(d)))

    def test_original_nil_record_missing_required_datatype_is_not_silently_repaired(self):
        from lxml import etree
        self.assertEqual(len(self.blocked), 1)
        row, error = self.blocked[0]
        self.assertIn('invalid nil input datatype', error)
        source = deepcopy(self.source)
        component = next(n['component'] for n in row['dependencies'] if n['kind'] == 'object')
        obj = next(source.node(n['component'], n['id'], 'object') for n in row['dependencies']
                   if n['kind'] == 'object' and source.node(n['component'], n['id'], 'object').tag == W + 'cmdlet_object')
        parameters = obj.find(W + 'parameters')
        self.assertEqual(parameters.attrib, {NIL: 'true'})
        schema = ET.parse(ROOT / 'third_party/scap-1.4-schemas/oval_5.12.3/windows-definitions-schema.xsd').getroot()
        assertions = [a.get('test') for rule in schema.iter() if rule.tag.endswith('}rule') and
                      rule.get('context') == 'win-def:cmdlet_object/win-def:parameters'
                      for a in rule if a.tag.endswith('}assert')]
        self.assertIn("@datatype='record'", assertions)
        node = etree.fromstring(ET.tostring(parameters))
        self.assertFalse(node.xpath("@datatype='record'"))
        with self.assertRaises(ValueError): ExpandedSource(source.components[component]).object(obj.get('id'))
        # An explicitly typed controlled derivative proves; it is not original coverage.
        parameters.set('datatype', 'record')
        docs, trace = convert(source, [row['source_rule']])
        self.assertEqual(len(verify_original(source.root, docs, trace)), 1)
        self.assertEqual(len(verify_compiled(docs, build_bundle(docs)[0])), 1)

    def test_null_module_constraints_and_capability_select_are_not_generic_wrappers(self):
        validators = build_validators(ROOT / 'schema/v0.4.0')
        for doc in self.docs.values():
            if 'assessment' not in doc:
                continue
            for test in doc['assessment']['tests'].values():
                if test['capability'] != CAP:
                    continue
                obj = test['object']
                self.assertIsNone(obj['module_id']); self.assertIsNone(obj['module_version'])
                self.assertIn('fields', obj['select'])
                self.assertNotIn('capability', obj)
                self.assertNotIn('collect', obj)
        doc = deepcopy(next(d for d in self.docs.values() if 'assessment' in d))
        test = next(t for t in doc['assessment']['tests'].values() if t['capability'] == CAP)
        test['object']['select'] = {'hive': {'equals': 'local_machine'}}
        self.assertTrue(list(document_errors(validators['assessment.schema.json'], doc)))
        self.assertGreater(authoring_statistics({'bad': doc})['deprecated_grammar'], 0)

    def test_record_field_selection_and_expected_value_matching_keep_separate_scopes(self):
        source = deepcopy(self.source)
        binding, obj = self.input_object(source)
        field = obj.find(W + 'parameters')[0]
        field.text = None; field.set('var_ref', 'oval:direct.cmdlet.test:var:1'); field.set('entity_check', 'at least one')
        variables = source.components[binding['component']].find(O + 'variables')
        variable = ET.SubElement(variables, O + 'constant_variable', id='oval:direct.cmdlet.test:var:1',
                                 version='1', datatype='string', comment='Controlled cmdlet parameter values')
        for value in ('Win32_Useraccount', 'Win32_ComputerSystem'): ET.SubElement(variable, O + 'value').text = value
        source.index()
        docs, trace = convert(source, [binding['source_rule']])
        verify_original(source.root, docs, trace); verify_compiled(docs, build_bundle(docs)[0])
        p = next(n for d in docs.values() for n in walk(d) if n.get('selection_match') == 'one_or_more')
        self.assertEqual(p['value_match'], 'every')
        p['selection_match'] = 'every'
        with self.assertRaises(AssertionError): verify_original(source.root, docs, trace)

    def test_invalid_nil_records_names_and_wildcard_inputs_fail_closed(self):
        for mutation in ('nil-verb', 'nil-value', 'nil-version-type', 'duplicate', 'uppercase', 'record-type', 'comparator', 'wildcard'):
            source = deepcopy(self.source)
            binding, obj = self.input_object(source)
            record = obj.find(W + 'parameters')
            if mutation == 'nil-verb':
                verb = obj.find(W + 'verb'); verb.text = None; verb.set(NIL, 'true')
            elif mutation == 'nil-value': obj.find(W + 'module_id').text = 'not-empty'
            elif mutation == 'nil-version-type': obj.find(W + 'module_version').attrib.pop('datatype')
            elif mutation == 'duplicate': record.append(deepcopy(record[0]))
            elif mutation == 'uppercase': record[0].set('name', 'UPPERCASE')
            elif mutation == 'record-type': record.set('datatype', 'string')
            elif mutation == 'comparator': record.set('operation', 'not equal')
            else: obj.find(W + 'select')[0].text = '*'
            with self.subTest(mutation=mutation), self.assertRaises(UnsupportedSource): convert(source, [binding['source_rule']])
            with self.assertRaises(ValueError): ExpandedSource(source.components[binding['component']]).object(obj.get('id'))

    def test_source_input_types_null_identity_and_state_requirements_reject_native_mutants(self):
        for mutation in ('null', 'input-type', 'selection', 'state'):
            docs = deepcopy(self.docs)
            test = next(t for d in docs.values() if 'assessment' in d for t in d['assessment']['tests'].values() if t['capability'] == CAP)
            if mutation == 'null': test['object']['module_id'] = ''
            elif mutation == 'input-type':
                p = next(n for d in docs.values() for n in walk(d) if n.get('equals') == '100')
                p['equals'] = 100; p['datatype'] = 'integer'
            elif mutation == 'selection': test['object']['parameters']['fields']['class']['selection_match'] = 'none'
            else:
                p = next(n for d in docs.values() for n in walk(d) if 'records_matching' in n)
                p['records_matching'] = 'none'
            with self.subTest(mutation=mutation), self.assertRaises(AssertionError): verify_original(self.source.root, docs, self.trace)


if __name__ == '__main__':
    unittest.main()
