"""Pinned effective-rights permissions, SID filters, variables and path forms."""
from copy import deepcopy
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

import yaml

from v04_direct_scap_source import SourceModel, UnsupportedSource, OVAL
from v04_direct_inventory import SourceInventory
from v04_direct_converter import convert
from v04_expanded_source_proof import ExpandedSource, original_file_rights_contract
from v04_direct_yaml import authoring_yaml
from audit_v04_direct_benchmark import verify_original, verify_compiled
from v04_native_bundle_compiler import build_bundle
from validate_native_json_schemas import build_validators, document_errors
from v04_direct_authoring_examples import capability_examples, walk

ROOT = Path(__file__).resolve().parents[1]
PINS = json.loads((ROOT / 'tests/fixtures/v04-direct-prototype/provenance.json').read_text())
O, W = '{' + OVAL + '}', '{' + OVAL + '#windows}'
CAP = 'windows.fileeffectiverights'


class DirectFileRightsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SourceModel(ROOT / 'tests/fixtures/v04-direct-prototype' / PINS['fixture'], PINS['zip_sha256'])
        cls.rules = [r['source_rule'] for r in SourceInventory(cls.source).rules() if CAP in r['needed_capabilities']]
        cls.docs, cls.trace = convert(cls.source, cls.rules)

    def dependency(self, source, kind, *, boolean=False):
        for binding in self.trace['rules']:
            for identifier, node in binding['dependencies'].items():
                if node['kind'] != kind:
                    continue
                element = source.node(binding['component'], identifier, kind)
                if element.tag != W + 'fileeffectiverights53_' + kind:
                    continue
                if boolean and not any(c.get('datatype') == 'boolean' for c in element):
                    continue
                return binding, element
        self.fail('original rights dependency unavailable')

    def test_all_eight_actual_closures_validate_compile_prove_and_roundtrip_yaml(self):
        self.assertEqual(len(self.rules), 8)
        self.assertEqual(len(verify_original(self.source.root, self.docs, self.trace)), 8)
        self.assertEqual(len(verify_compiled(self.docs, build_bundle(self.docs)[0])), 8)
        validators = build_validators(ROOT / 'schema/v0.4.0')
        for doc in self.docs.values():
            self.assertEqual(yaml.safe_load(authoring_yaml(doc)), doc)
            if 'assessment' in doc:
                self.assertFalse(list(document_errors(validators['assessment.schema.json'], doc)))
        objects = [n for d in self.docs.values() for n in walk(d) if 'filesystem' in n]
        self.assertTrue(any('full_path' in n for n in objects))
        self.assertTrue(any('directory' in n and 'name' in n for n in objects))
        self.assertTrue(all(n['filesystem'] == 'all' for n in objects))

    def test_original_sid_defaults_permissions_and_whole_graph_dependencies_remain_explicit(self):
        fields, defaults = original_file_rights_contract()
        self.assertEqual(defaults, {'include_group': 'true', 'resolve_group': 'false'})
        self.assertEqual(fields['file_write_data'], 'boolean')
        self.assertNotIn('windows_view', fields)
        self.assertTrue(any(d.get('assessment', {}).get('variables') for d in self.docs.values()))
        self.assertTrue(any('filters' in n for d in self.docs.values() for n in walk(d)))
        self.assertTrue(any(n.get('datatype') == 'boolean' and n.get('equals') is False
                            for d in self.docs.values() for n in walk(d)))
        examples = capability_examples(self.docs, CAP)
        self.assertEqual(set(examples), {'source-filter-variable', 'shared-acquisition'})
        self.assertEqual(len({a['id'] for a in examples.values()}), len(examples))
        for d in self.docs.values():
            for n in walk(d):
                self.assertNotIn('include_group', n)
                self.assertNotIn('resolve_group', n)

    def test_actual_permission_sid_filter_variable_and_collection_mutants_fail_independent_proof(self):
        for mutation in ('permission', 'sid', 'filter', 'variable', 'scope', 'existence'):
            docs = deepcopy(self.docs)
            nodes = [n for d in docs.values() for n in walk(d)]
            if mutation == 'permission':
                n = next(n for n in nodes if n.get('datatype') == 'boolean' and isinstance(n.get('equals'), bool))
                n['equals'] = not n['equals']
            elif mutation == 'sid':
                n = next(n for n in nodes if isinstance(n.get('equals'), str) and n['equals'].startswith('S-1-'))
                n['equals'] += '-changed'
            elif mutation == 'filter':
                n = next(n for n in nodes if 'exclude' in n); n['include'] = n.pop('exclude')
            elif mutation == 'variable':
                n = next(n for n in nodes if n.get('value_match') == 'one_or_more')
                n['value_match'] = 'every'
            elif mutation == 'scope':
                n = next(n for n in nodes if n.get('filesystem') == 'all'); n['filesystem'] = 'local'
            else:
                n = next(n for n in nodes if n.get('items_found') == 'none'); n['items_found'] = 'one_or_more'
            with self.subTest(mutation=mutation), self.assertRaises(AssertionError):
                verify_original(self.source.root, docs, self.trace)

    def test_invalid_source_types_fields_and_group_expansion_behaviors_fail_closed(self):
        for mutation in ('datatype', 'omitted-type', 'field', 'behavior'):
            source = deepcopy(self.source)
            binding, state = self.dependency(source, 'state', boolean=True)
            entity = next(c for c in state if c.get('datatype') == 'boolean')
            if mutation == 'datatype': entity.set('datatype', 'string')
            elif mutation == 'omitted-type': entity.attrib.pop('datatype')
            elif mutation == 'field': entity.tag = W + 'invented'
            else:
                binding, obj = self.dependency(source, 'object')
                obj.insert(0, ET.Element(W + 'behaviors', resolve_group='true'))
            with self.subTest(mutation=mutation), self.assertRaises(UnsupportedSource):
                convert(source, [binding['source_rule']])
            reader = ExpandedSource(source.components[binding['component']])
            with self.assertRaises(ValueError):
                if mutation == 'behavior': reader.object(obj.get('id'))
                else: reader.state(state.get('id'), CAP)

    def test_controlled_two_path_complement_keeps_ordered_filters_on_each_operand(self):
        source = deepcopy(self.source)
        binding = next(b for b in self.trace['rules'] if sum(v['kind'] == 'object' and
            source.node(b['component'], k, 'object').tag == W + 'fileeffectiverights53_object' and
            source.node(b['component'], k, 'object').find(W + 'filepath') is not None
            for k, v in b['dependencies'].items()) >= 2)
        objects = [source.node(binding['component'], k, 'object') for k, v in binding['dependencies'].items()
                   if v['kind'] == 'object' and source.node(binding['component'], k, 'object').tag == W + 'fileeffectiverights53_object']
        leaves = [n for n in objects if n.find(W + 'filepath') is not None]
        group = next(n.find(O + 'set') for n in objects if n.find(O + 'set') is not None)
        group.set('set_operator', 'COMPLEMENT')
        original_filters = [deepcopy(c) for c in group if c.tag == O + 'filter']
        group[:] = []
        for leaf in leaves[:2]: ET.SubElement(group, O + 'object_reference').text = leaf.get('id')
        group.extend(original_filters)
        source.index()
        docs, trace = convert(source, [binding['source_rule']])
        verify_original(source.root, docs, trace)
        verify_compiled(docs, build_bundle(docs)[0])
        native = next(n['set'] for d in docs.values() for n in walk(d) if n.get('set', {}).get('operator') == 'difference')
        self.assertEqual(len(native['operands']), 2)
        self.assertTrue(all(len(x['filters']) == len(original_filters) for x in native['operands']))
        self.assertTrue(original_filters)
        native['operands'].reverse()
        with self.assertRaises(AssertionError): verify_original(source.root, docs, trace)


if __name__ == '__main__':
    unittest.main()
