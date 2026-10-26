"""Original Windows service selectors/enums with independent closure proof."""
from copy import deepcopy
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

from v04_direct_scap_source import SourceModel, UnsupportedSource, OVAL
from v04_direct_inventory import SourceInventory
from v04_direct_converter import convert
from v04_expanded_source_proof import ExpandedSource, original_service_contract
from audit_v04_direct_benchmark import verify_original, verify_compiled
from v04_native_bundle_compiler import build_bundle
from validate_native_json_schemas import build_validators, document_errors
from v04_direct_authoring_examples import walk

ROOT = Path(__file__).resolve().parents[1]
PINS = json.loads((ROOT / 'tests/fixtures/v04-direct-prototype/provenance.json').read_text())
O, W = '{' + OVAL + '}', '{' + OVAL + '#windows}'
CAP = 'windows.service'


class DirectServiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SourceModel(ROOT / 'tests/fixtures/v04-direct-prototype' / PINS['fixture'], PINS['zip_sha256'])
        cls.rows = [r for r in SourceInventory(cls.source).rules() if CAP in r['needed_capabilities']]
        cls.rules = [r['source_rule'] for r in cls.rows]
        cls.docs, cls.trace = convert(cls.source, cls.rules)

    def dependency(self, source, binding, kind):
        identifier = next(i for i, n in binding['dependencies'].items() if n['kind'] == kind)
        return source.node(binding['component'], identifier, kind)

    def test_both_original_closures_schema_validate_compile_and_prove_with_inline_objects(self):
        self.assertEqual(len(self.rules), 2)
        self.assertEqual(len(verify_original(self.source.root, self.docs, self.trace)), 2)
        self.assertEqual(len(verify_compiled(self.docs, build_bundle(self.docs)[0])), 2)
        validators = build_validators(ROOT / 'schema/v0.4.0')
        for doc in self.docs.values():
            if 'assessment' in doc:
                self.assertFalse(list(document_errors(validators['assessment.schema.json'], doc)))
                a = doc['assessment']
                self.assertNotIn('shared_objects', a)
                for test in a['tests'].values():
                    self.assertEqual(test['capability'], CAP)
                    self.assertIsInstance(test['object'], dict)
                    self.assertNotIn('capability', test['object'])
        self.assertIn('SERVICE_RUNNING', original_service_contract()['current_state'][1])

    def test_service_name_case_comparison_and_state_literals_are_not_normalized(self):
        objects = [t['object'] for d in self.docs.values() if 'assessment' in d for t in d['assessment']['tests'].values()]
        self.assertTrue(any(o['service_name'].get('equals') == 'bthserv' for o in objects))
        self.assertTrue(any(o['service_name'].get('case_insensitive_equals') == 'sshd' for o in objects))
        for mutation in ('selector', 'state', 'quantifier'):
            docs = deepcopy(self.docs)
            test = next(t for d in docs.values() if 'assessment' in d for t in d['assessment']['tests'].values()
                        if 'case_insensitive_equals' in t['object']['service_name'])
            if mutation == 'selector':
                selector = test['object']['service_name']
                selector['equals'] = selector.pop('case_insensitive_equals')
            elif mutation == 'state':
                field = next(n for n in walk(test['require']) if n.get('equals') == 'SERVICE_RUNNING')
                field['equals'] = 'SERVICE_STOPPED'
            else: test['require']['items_satisfying'] = 'one_or_more'
            with self.subTest(mutation=mutation), self.assertRaises(AssertionError):
                verify_original(self.source.root, docs, self.trace)

    def test_controlled_set_filters_keep_relative_complement_and_shared_identity(self):
        source = deepcopy(self.source)
        binding = self.trace['rules'][0]
        obj = self.dependency(source, binding, 'object')
        state = self.dependency(source, binding, 'state')
        test = self.dependency(source, binding, 'test')
        wrapper = ET.SubElement(source.components[binding['component']].find(O + 'objects'), W + 'service_object',
            id='oval:direct.service.test:obj:1', version='1', comment='Source service comparison Set')
        group = ET.SubElement(wrapper, O + 'set', set_operator='COMPLEMENT')
        for _ in range(2): ET.SubElement(group, O + 'object_reference').text = obj.get('id')
        ET.SubElement(group, O + 'filter', action='include').text = state.get('id')
        test.find(W + 'object').set('object_ref', wrapper.get('id'))
        source.index()
        docs, trace = convert(source, [binding['source_rule']])
        verify_original(source.root, docs, trace)
        verify_compiled(docs, build_bundle(docs)[0])
        a = next(d['assessment'] for d in docs.values() if 'assessment' in d)
        self.assertEqual(len(a['shared_objects']), 1)
        group = next(n['set'] for n in walk(a) if 'set' in n)
        self.assertEqual(group['operator'], 'difference')
        self.assertEqual(group['operands'][0]['object'], group['operands'][1]['object'])
        self.assertTrue(all(set(x['filters'][0]) == {'include'} for x in group['operands']))
        group['operator'] = 'union'
        with self.assertRaises(AssertionError): verify_original(source.root, docs, trace)

    def test_unknown_enums_fields_and_object_selectors_fail_closed(self):
        for mutation in ('enum', 'state-field', 'object-field'):
            source = deepcopy(self.source)
            binding = self.trace['rules'][0]
            state = self.dependency(source, binding, 'state')
            if mutation == 'enum': state[0].text = 'SERVICE_INVENTED'
            elif mutation == 'state-field': state[0].tag = W + 'invented'
            else: ET.SubElement(self.dependency(source, binding, 'object'), W + 'invented').text = 'value'
            with self.subTest(mutation=mutation), self.assertRaises(UnsupportedSource):
                convert(source, [binding['source_rule']])
            reader = ExpandedSource(source.components[binding['component']])
            with self.assertRaises(ValueError):
                if mutation == 'object-field': reader.object(self.dependency(source, binding, 'object').get('id'))
                else: reader.state(state.get('id'), CAP)


if __name__ == '__main__':
    unittest.main()
