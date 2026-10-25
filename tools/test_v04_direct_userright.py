"""Pinned user-rights closures, complete admission and independent source proof."""
from copy import deepcopy
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

import yaml
from v04_direct_scap_source import SourceModel, UnsupportedSource, OVAL
from v04_direct_converter import CAPABILITIES, convert
from v04_direct_inventory import SourceInventory
from v04_expanded_source_proof import original_userright_contract
from v04_object_contract import object_sites
from v04_direct_yaml import authoring_yaml
from audit_v04_direct_benchmark import verify_original, verify_compiled
from v04_native_bundle_compiler import build_bundle
from validate_native_json_schemas import build_validators, document_errors
from v04_direct_authoring_examples import capability_examples, example_filename

ROOT = Path(__file__).resolve().parents[1]
PINS = json.loads((ROOT / 'tests/fixtures/v04-direct-prototype/provenance.json').read_text())
O, W = '{' + OVAL + '}', '{' + OVAL + '#windows}'
CAP = 'windows.userright'


class DirectUserrightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SourceModel(ROOT / 'tests/fixtures/v04-direct-prototype' / PINS['fixture'], PINS['zip_sha256'])
        cls.rows = [r for r in SourceInventory(cls.source).rules() if CAP in r['needed_capabilities']]
        cls.rules = [r['source_rule'] for r in cls.rows if set(r['needed_capabilities']) <= set(CAPABILITIES)]
        cls.docs, cls.trace = convert(cls.source, cls.rules)
        cls.by_assessment = {d['assessment']['id']: d['assessment'] for d in cls.docs.values() if 'assessment' in d}

    def filter_case(self):
        return next((b, self.by_assessment[b['assessment']]) for b in self.trace['rules']
                    if any(s.node.get('filters') for s in object_sites(self.by_assessment[b['assessment']])))

    def test_complete_39_rule_census_admits_only_34_proved_closures_and_blocks_mixed_wmi(self):
        self.assertEqual((len(self.rows), len(self.rules)), (39, 34))
        self.assertEqual(len(verify_original(self.source.root, self.docs, self.trace)), 34)
        self.assertEqual(len(verify_compiled(self.docs, build_bundle(self.docs)[0])), 34)
        blocked = [r for r in self.rows if r['source_rule'] not in self.rules]
        self.assertEqual(len(blocked), 5)
        for row in blocked:
            self.assertIn('windows.wmi.query', row['needed_capabilities'])
            with self.subTest(rule=row['source_rule']), self.assertRaisesRegex(UnsupportedSource, 'wmi57'):
                convert(self.source, [row['source_rule']])
            self.assertNotIn(row['source_rule'], {b['source_rule'] for b in self.trace['rules']})

    def test_public_schema_capability_validation_yaml_and_legitimate_sharing(self):
        validators = build_validators(ROOT / 'schema/v0.4.0')
        for document in self.docs.values():
            kind, = document
            self.assertEqual(list(document_errors(validators[kind + '.schema.json'], document)), [])
            self.assertEqual(yaml.safe_load(authoring_yaml(document)), document)
        shared = []
        for a in self.by_assessment.values():
            for key, obj in a.get('shared_objects', {}).items():
                shared.append(key)
                self.assertEqual(obj['capability'], CAP)
                self.assertIn('SE_DENY_SERVICE_LOGON_NAME', obj['object_title'])
                self.assertGreater(sum(t.get('object') == key for t in a['tests'].values()), 1)
            for test in a['tests'].values():
                if isinstance(test.get('object'), dict):
                    self.assertNotIn('capability', test['object'])
                    self.assertNotIn('object_title', test['object'])
        self.assertEqual(len(shared), 1)
        examples = capability_examples(self.docs, CAP)
        self.assertEqual(set(examples), {'ordinary-acquisition', 'source-filter-variable', 'shared-acquisition'})
        for a in examples.values():
            self.assertTrue(example_filename(a).endswith('.assessment'))

    def test_actual_variable_filter_absence_case_retains_default_all_and_source_identity(self):
        binding, assessment = self.filter_case()
        test, = assessment['tests'].values()
        self.assertEqual(test['require'], {'items_found': 'none'})
        self.assertEqual(test['object']['userright']['value_match'], 'every')
        values = test['object']['userright']['equals']
        self.assertEqual(len(values), 45)
        variable_id, = [k for k, v in binding['dependencies'].items() if v['kind'] == 'variable']
        variable = self.source.node(binding['component'], variable_id, 'variable')
        self.assertEqual(values, [v.text for v in variable])
        object_id = next(k for k, v in binding['dependencies'].items() if v['kind'] == 'object')
        entity = self.source.node(binding['component'], object_id, 'object').find(W + 'userright')
        self.assertNotIn('var_check', entity.attrib)
        self.assertEqual(entity.get('var_ref'), variable_id)
        # Empty trustee_name is matched as a present value, never field absence.
        include = test['object']['filters'][0]['include']['and']
        name = next(v['trustee_name'] for v in include if 'trustee_name' in v)
        self.assertEqual(name['matches_regex'], '^$')
        self.assertEqual(name['values_found'], 'one_or_more')
        xs = '{http://www.w3.org/2001/XMLSchema}'
        xsd = ET.parse(ROOT / 'third_party/scap-1.4-schemas/oval_5.12.3/oval-definitions-schema.xsd').getroot()
        text = ''.join(xsd.find('.//' + xs + 'attribute[@name="var_check"]').itertext())
        self.assertIn('If var_ref is present but var_check is not', text)

    def test_wrong_var_check_filter_boolean_and_cardinality_fail_independent_proof(self):
        binding, assessment = self.filter_case()
        for mutation in ('expected-quantifier', 'filter-action', 'filter-condition', 'absence', 'field-absence'):
            docs = deepcopy(self.docs)
            a = next(d['assessment'] for d in docs.values() if d.get('assessment', {}).get('id') == assessment['id'])
            test, = a['tests'].values()
            if mutation == 'expected-quantifier':
                test['object']['userright']['value_match'] = 'one_or_more'
            elif mutation == 'filter-action':
                f = test['object']['filters'][0]; f['exclude'] = f.pop('include')
            elif mutation == 'filter-condition':
                c = test['object']['filters'][0]['include']; c['or'] = c.pop('and')
            elif mutation == 'absence':
                test['require']['items_found'] = 'one_or_more'
            else:
                c = test['object']['filters'][0]['include']['and']
                next(v for v in c if 'trustee_name' in v)['trustee_name'] = {'values_found': 'none'}
            with self.subTest(mutation=mutation), self.assertRaises(AssertionError):
                verify_original(self.source.root, docs, self.trace)

    def test_invalid_source_enums_fields_and_cycles_fail_closed(self):
        binding, _ = self.filter_case()
        oid = next(k for k, v in binding['dependencies'].items() if v['kind'] == 'object')
        variable_id = next(k for k, v in binding['dependencies'].items() if v['kind'] == 'variable')
        for mutation in ('enum', 'field', 'cycle', 'comparator'):
            source = deepcopy(self.source)
            obj = source.node(binding['component'], oid, 'object')
            if mutation == 'enum':
                source.node(binding['component'], variable_id, 'variable')[0].text = 'NOT_A_USER_RIGHT'
            elif mutation == 'field':
                ET.SubElement(obj, W + 'invented').text = 'selector'
            elif mutation == 'cycle':
                v = source.node(binding['component'], variable_id, 'variable')
                v.tag = O + 'local_variable'; v[:] = []
                ET.SubElement(v, O + 'object_component', object_ref=oid, item_field='userright')
            else:
                obj.find(W + 'userright').set('operation', 'pattern match')
            source.index()
            with self.subTest(mutation=mutation), self.assertRaises(UnsupportedSource):
                convert(source, [binding['source_rule']])

    def test_controlled_sets_preserve_order_filters_and_source_object_identity(self):
        binding, _ = self.filter_case()
        source = deepcopy(self.source)
        oid = next(k for k, v in binding['dependencies'].items() if v['kind'] == 'object')
        obj = source.node(binding['component'], oid, 'object')
        second = deepcopy(obj); second.set('id', 'oval:org.scapng.userright:obj:1')
        objects = source.components[binding['component']].find(O + 'objects'); objects.append(second)
        obj[:] = []
        node = ET.SubElement(obj, O + 'set', set_operator='COMPLEMENT')
        # Reuse one acquisition identity twice. Filters stay inside that leaf.
        for _ in range(2): ET.SubElement(node, O + 'object_reference').text = second.get('id')
        source.index()
        docs, trace = convert(source, [binding['source_rule']])
        verify_original(source.root, docs, trace)
        verify_compiled(docs, build_bundle(docs)[0])
        a = next(d['assessment'] for d in docs.values() if 'assessment' in d)
        self.assertEqual(len(a['shared_objects']), 1)
        test, = a['tests'].values()
        self.assertEqual(test['object']['set']['operator'], 'difference')
        operands = test['object']['set']['operands']
        self.assertEqual(operands[0]['object'], operands[1]['object'])
        fields, values = original_userright_contract()
        self.assertEqual(fields, {'userright', 'trustee_name', 'trustee_sid'})
        self.assertEqual(len(values), 45)


if __name__ == '__main__':
    unittest.main()
