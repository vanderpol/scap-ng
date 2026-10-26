"""Authoring locality/presentation contracts, independently of semantic proof."""
from copy import deepcopy
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

import yaml
from v04_direct_converter import AssessmentConverter, convert, convert_benchmark, load_mappings
from v04_direct_scap_source import SourceModel, OVAL
from v04_direct_yaml import authoring_yaml, compact_registry_object
from v04_direct_authoring_examples import authoring_statistics, choose_examples, example_filename, walk, DEPRECATED
from validate_native_json_schemas import classify
from audit_v04_direct_benchmark import verify_original, verify_compiled
from v04_native_bundle_compiler import build_bundle
from v04_object_contract import object_sites

ROOT = Path(__file__).resolve().parents[1]
PINS = json.loads((ROOT / 'tests/fixtures/v04-direct-prototype/provenance.json').read_text())
O = '{' + OVAL + '}'


def mapping_member(node, key):
    return next(value for name, value in node.value if name.value == key)


class DirectAuthoringStyle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SourceModel(ROOT / 'tests/fixtures/v04-direct-prototype' / PINS['fixture'], PINS['zip_sha256'])
        cls.documents, cls.trace, cls.coverage = convert_benchmark(cls.source)
        cls.examples = choose_examples(cls.documents)

    def leaf_source(self):
        binding = next(b for b in self.trace['rules'] if b['assessment'] == self.examples['01-inline-registry']['id'])
        component = binding['component']
        test_id = next(k for k, d in binding['dependencies'].items() if d['kind'] == 'test')
        source = deepcopy(self.source)
        test = source.node(component, test_id, 'test')
        identifier = next(child.get('object_ref') for child in test if child.get('object_ref'))
        return source, component, test_id, identifier

    def test_local_single_use_ignores_extra_tests_elsewhere_in_original_source(self):
        source, component, test_id, identifier = self.leaf_source()
        duplicate = deepcopy(source.node(component, test_id, 'test'))
        duplicate.set('id', 'oval:org.scapng.authoring:tst:900001')
        source.components[component].find(O + 'tests').append(duplicate)
        source.index()
        self.assertGreater(source.object_references[component, identifier], 1)
        converter = AssessmentConverter(source, component, load_mappings())
        converter.reference(test_id, 'test')
        test, = converter.tests.values()
        self.assertIsInstance(test['object'], dict)
        self.assertNotIn('capability', test['object'])
        self.assertNotIn('object_title', test['object'])
        self.assertEqual(converter.shared_objects, {})
        definition = ET.SubElement(source.components[component].find(O + 'definitions'), O + 'definition',
            id='oval:org.scapng.authoring:def:900006', version='1', **{'class': 'compliance'})
        criteria = ET.SubElement(definition, O + 'criteria')
        for _ in range(2):
            ET.SubElement(criteria, O + 'criterion', test_ref=test_id)
        source.index()
        self.assertEqual(source.object_uses(component, definition.get('id'), 'definition')[identifier], 1)
        criteria[1].set('test_ref', duplicate.get('id'))
        source.index()
        self.assertEqual(source.object_uses(component, definition.get('id'), 'definition')[identifier], 2)
        converter = AssessmentConverter(source, component, load_mappings())
        converter.reference(definition.get('id'), 'definition')
        self.assertEqual(len(converter.shared_objects), 1)

    def test_real_reuse_preserves_stable_identity_and_meaningful_source_title(self):
        # This checks the original pinned seven-use acquisition, independently
        # of which newly supported capability supplies the first shared example.
        assessment = next(d['assessment'] for d in self.documents.values() if 'assessment' in d
            and 'legal-notice-text-8db50cbc-object' in d['assessment'].get('shared_objects', {}))
        self.assertEqual(len(assessment['shared_objects']), 1)
        identifier, obj = next(iter(assessment['shared_objects'].items()))
        self.assertEqual(obj['object_title'], 'Legal notice text')
        self.assertEqual(obj['capability'], 'windows.registry')
        self.assertEqual(sum(t.get('object') == identifier for t in assessment['tests'].values()), 7)
        self.assertEqual(identifier, 'legal-notice-text-8db50cbc-object')

    def test_set_reuse_counts_distinct_edges_but_does_not_merge_equal_source_objects(self):
        source, component, test_id, identifier = self.leaf_source()
        original = source.node(component, identifier, 'object')
        duplicate = deepcopy(original)
        duplicate_id = 'oval:org.scapng.authoring:obj:900002'
        duplicate.set('id', duplicate_id)
        source.components[component].find(O + 'objects').append(duplicate)
        root = ET.SubElement(source.components[component].find(O + 'objects'), original.tag,
                             id='oval:org.scapng.authoring:obj:900003', version='1')
        node = ET.SubElement(root, O + 'set')
        for target in (identifier, duplicate_id):
            ET.SubElement(node, O + 'object_reference').text = target
        source.index()
        converter = AssessmentConverter(source, component, load_mappings())
        acquisition = converter.reference(root.get('id'), 'object')
        self.assertEqual(converter.shared_objects, {})
        self.assertEqual(len(acquisition['set']['operands']), 2)
        node[1].text = identifier
        source.index()
        # Force the fallback to acquisition facts instead of a generic title.
        original.set('comment', 'windows-registry-object')
        converter = AssessmentConverter(source, component, load_mappings())
        acquisition = converter.reference(root.get('id'), 'object')
        self.assertEqual(len(converter.shared_objects), 1)
        title = next(iter(converter.shared_objects.values()))['object_title']
        self.assertIn('HKEY_LOCAL_MACHINE', title)
        self.assertIn('key equals', title)
        self.assertEqual(acquisition['set']['operands'][0]['object'], acquisition['set']['operands'][1]['object'])

    def test_variable_and_filter_dependency_graph_participates_in_sharing(self):
        source, component, test_id, identifier = self.leaf_source()
        # Source-backed dependency edges with controlled topology, not a new
        # original Rule proof: Test -> Object -> Filter State -> Variable -> Object.
        state = ET.SubElement(source.components[component].find(O + 'states'),
            '{http://oval.mitre.org/XMLSchema/oval-definitions-5#windows}registry_state',
            id='oval:org.scapng.authoring:ste:900004', version='1')
        ET.SubElement(state, '{http://oval.mitre.org/XMLSchema/oval-definitions-5#windows}value',
                      var_ref='oval:org.scapng.authoring:var:900005')
        variable = ET.SubElement(source.components[component].find(O + 'variables'), O + 'local_variable',
            id='oval:org.scapng.authoring:var:900005', version='1', datatype='string')
        ET.SubElement(variable, O + 'object_component', object_ref=identifier, item_field='value')
        ET.SubElement(source.node(component, identifier, 'object'), O + 'filter').text = state.get('id')
        source.index()
        self.assertEqual(source.object_uses(component, test_id, 'test')[identifier], 2)
        # The graph is cyclic; planning must not hide the existing fail-closed gate.
        with self.assertRaisesRegex(ValueError, 'cyclic'):
            AssessmentConverter(source, component, load_mappings()).reference(test_id, 'test')

    def test_all_yaml_equals_native_json_and_simple_object_nodes_are_flow_style(self):
        count = 0
        for document in self.documents.values():
            text = authoring_yaml(document)
            self.assertEqual(yaml.safe_load(text), document)
            if 'assessment' not in document:
                continue
            tree = yaml.compose(text)
            for site in object_sites(document['assessment']):
                if site.private and site.inherited:
                    self.assertNotIn('capability', site.node)
                if site.private and compact_registry_object(site.node, site.capability):
                    node = tree
                    for part in site.path:
                        node = node.value[part] if isinstance(part, int) else mapping_member(node, part)
                    self.assertTrue(node.flow_style, site.path)
                    self.assertEqual(node.start_mark.line, node.end_mark.line, site.path)
                    count += 1
            node = mapping_member(yaml.compose(text), 'assessment')
            tests = mapping_member(node, 'tests')
            for key, native in document['assessment']['tests'].items():
                test = mapping_member(tests, key)
                if compact_registry_object(native.get('object'), native['capability']):
                    obj = mapping_member(test, 'object')
                    self.assertTrue(obj.flow_style)
                    self.assertEqual(obj.start_mark.line, obj.end_mark.line)
                    self.assertNotIn('capability', native['object'])
                self.assertFalse(mapping_member(test, 'require').flow_style)
        self.assertEqual(count, authoring_statistics(self.documents)['one_line_objects'])
        self.assertGreater(count, 50)

    def test_windows_paths_regex_empty_and_yaml_ambiguous_strings_keep_scalar_types(self):
        for value in (r'Software\Policies\Example', r'^a\b.*\d+$', '', 'on', 'false', 'null', '01', '1.0', '2026-10-25', 'a: b', '#value'):
            document = deepcopy({'assessment': self.examples['01-inline-registry']})
            test = next(iter(document['assessment']['tests'].values()))
            test['object']['key'] = {'equals': value}
            with self.subTest(value=value):
                self.assertEqual(yaml.safe_load(authoring_yaml(document)), document)

    def test_complex_sets_and_nested_require_alternatives_stay_visible_and_structured(self):
        document = {'assessment': deepcopy(self.examples['05-nested-set'])}
        text = authoring_yaml(document)
        self.assertEqual(yaml.safe_load(text), document)
        self.assertIn('set:\n', text)
        # Presentation-only shape probe; not an invented source conversion.
        test = next(iter(document['assessment']['tests'].values()))
        test['require'] = {'items_found': 'one_or_more', 'items_satisfying': 'every', 'or': [
            {'fields': {'type': {'equals': 'dword'}, 'value': {'equals': 0, 'datatype': 'integer'}}},
            {'fields': {'type': {'equals': 'dword'}, 'value': {'equals': 1, 'datatype': 'integer'}}}]}
        self.assertEqual(yaml.safe_load(authoring_yaml(document)), document)
        self.assertIn('require:\n', authoring_yaml(document))

    def test_no_object_contract_and_exclusively_current_grammar(self):
        for doc in self.documents.values():
            if 'assessment' not in doc:
                continue
            for node in walk(doc['assessment']):
                self.assertFalse(set(node) & DEPRECATED)
            for test in doc['assessment']['tests'].values():
                self.assertIsInstance(test['require'], dict)
                if test['capability'] == 'windows.auditeventpolicysubcategories':
                    self.assertNotIn('object', test)
        stats = authoring_statistics(self.documents)
        self.assertEqual((stats['assessments'], stats['tests'], stats['no_object_tests']), (238, 335, 85))
        self.assertEqual(stats['shared_objects'], stats['multiply_used_named_objects'])

    def test_representatives_retain_independent_source_and_compiled_operand_proof(self):
        for a in self.examples.values():
            self.assertEqual(classify(Path(example_filename(a) + '.yaml')), ('assessment', 'assessment.schema.json'))
        selected = {a['id'] for a in self.examples.values()}
        rules = [b['source_rule'] for b in self.trace['rules'] if b['assessment'] in selected]
        docs, trace = convert(self.source, rules)
        self.assertEqual(len(verify_original(self.source.root, docs, trace)), len(selected))
        self.assertEqual(len(verify_compiled(docs, build_bundle(docs)[0])), len(selected))


if __name__ == '__main__':
    unittest.main()
