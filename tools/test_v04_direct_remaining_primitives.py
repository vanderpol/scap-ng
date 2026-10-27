"""Source-pinned IIS/NTUSER/query primitives and explicit source-invalid bounds."""
from copy import deepcopy
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

from lxml import etree
import yaml
from v04_direct_scap_source import SourceModel, UnsupportedSource, OVAL
from v04_direct_inventory import SourceInventory
from v04_direct_converter import convert
from v04_expanded_source_proof import ExpandedSource
from v04_direct_authoring_examples import walk
from v04_direct_yaml import authoring_yaml
from audit_v04_direct_benchmark import verify_original, verify_compiled
from v04_native_bundle_compiler import build_bundle
from validate_native_json_schemas import build_validators, document_errors

ROOT = Path(__file__).resolve().parents[1]
PINS = json.loads((ROOT / 'tests/fixtures/v04-direct-prototype/provenance.json').read_text())
O, W = '{' + OVAL + '}', '{' + OVAL + '#windows}'
CAPS = {'windows.appcmd', 'windows.appcmdlistconfig', 'windows.ntuser'}


class RemainingPrimitiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SourceModel(ROOT / 'tests/fixtures/v04-direct-prototype' / PINS['fixture'], PINS['zip_sha256'])
        cls.rules = []
        for row in SourceInventory(cls.source).rules():
            inequality = set(row['needed_capabilities']) == {'independent.shellcommand'} and any(
                any(c.get('operation') == 'case insensitive not equal' for c in cls.source.node(n['component'], n['id'], 'state'))
                for n in row['dependencies'] if n['kind'] == 'state')
            if CAPS & set(row['needed_capabilities']) or inequality:
                cls.rules.append(row['source_rule'])
        cls.docs, cls.trace = convert(cls.source, cls.rules)

    def test_all_five_original_closures_schema_compile_prove_and_yaml_roundtrip(self):
        self.assertEqual(len(self.rules), 5)
        self.assertEqual(len(verify_original(self.source.root, self.docs, self.trace)), 5)
        self.assertEqual(len(verify_compiled(self.docs, build_bundle(self.docs)[0])), 5)
        validators = build_validators(ROOT / 'schema/v0.4.0')
        for doc in self.docs.values():
            self.assertEqual(yaml.safe_load(authoring_yaml(doc)), doc)
            if 'assessment' in doc:
                self.assertFalse(list(document_errors(validators['assessment.schema.json'], doc)))

    def test_case_insensitive_inequality_retains_names_and_field_scopes(self):
        nodes = [n for d in self.docs.values() for n in walk(d) if 'case_insensitive_not_equal' in n]
        self.assertEqual({n['case_insensitive_not_equal'] for n in nodes}, {'Administrator', 'Guest'})
        self.assertTrue(all(n['values_found'] == 'one_or_more' and n['values_matching'] == 'every' for n in nodes))
        docs = deepcopy(self.docs)
        p = next(n for d in docs.values() for n in walk(d) if 'case_insensitive_not_equal' in n)
        p['not_equal'] = p.pop('case_insensitive_not_equal')
        with self.assertRaises(AssertionError): verify_original(self.source.root, docs, self.trace)
        source = deepcopy(self.source)
        binding = next(b for b in self.trace['rules'] if any(v['kind'] == 'state' and any(
            c.get('operation') == 'case insensitive not equal' for c in source.node(b['component'], k, 'state'))
            for k, v in b['dependencies'].items()))
        state = next(source.node(binding['component'], k, 'state') for k, v in binding['dependencies'].items()
                     if v['kind'] == 'state')
        entity = next(c for c in state if c.get('operation') == 'case insensitive not equal')
        entity.set('datatype', 'int'); entity.text = '1'
        with self.assertRaises(UnsupportedSource): convert(source, [binding['source_rule']])
        with self.assertRaises(ValueError): ExpandedSource(source.components[binding['component']]).state(state.get('id'), 'independent.shellcommand')

    def test_iis_false_is_string_and_current_process_environment_is_null(self):
        self.assertTrue(any(n.get('equals') == 'false' and 'datatype' not in n
                            for d in self.docs.values() for n in walk(d)))
        environments = [n for d in self.docs.values() for n in walk(d)
                        if n.get('capability') == 'independent.environmentvariable58']
        self.assertEqual(len(environments), 4)
        self.assertTrue(all(n['pid'] is None for n in environments))
        docs = deepcopy(self.docs)
        env = next(n for d in docs.values() for n in walk(d) if n.get('capability') == 'independent.environmentvariable58')
        env['pid'] = {'equals': 0, 'datatype': 'integer'}
        with self.assertRaises(AssertionError): verify_original(self.source.root, docs, self.trace)
        binding = next(b for b in self.trace['rules'] if any(v['kind'] == 'object' and
                       self.source.node(b['component'], k, 'object').tag.endswith('}environmentvariable58_object')
                       for k, v in b['dependencies'].items()))
        for datatype in (None, 'string'):
            source = deepcopy(self.source)
            obj = next(source.node(binding['component'], k, 'object') for k, v in binding['dependencies'].items()
                       if v['kind'] == 'object' and source.node(binding['component'], k, 'object').tag.endswith('}environmentvariable58_object'))
            pid = next(c for c in obj if c.tag.endswith('}pid'))
            if datatype is None: pid.attrib.pop('datatype')
            else: pid.set('datatype', datatype)
            with self.subTest(datatype=datatype), self.assertRaises(UnsupportedSource):
                convert(source, [binding['source_rule']])
            with self.assertRaises(ValueError):
                ExpandedSource(source.components[binding['component']]).object(obj.get('id'))

    def test_singleton_function_constants_fold_without_erasing_multi_value_products(self):
        binding = next(b for b in self.trace['rules'] if any(
            v['kind'] == 'variable' and self.source.node(b['component'], k, 'variable').tag == O + 'constant_variable'
            for k, v in b['dependencies'].items()))
        source = deepcopy(self.source)
        constant = next(source.node(binding['component'], k, 'variable') for k, v in binding['dependencies'].items()
                        if v['kind'] == 'variable' and source.node(binding['component'], k, 'variable').tag == O + 'constant_variable')
        ET.SubElement(constant, O + 'value').text = 'SECOND-VALUE'
        docs, trace = convert(source, [binding['source_rule']])
        verify_original(source.root, docs, trace)
        verify_compiled(docs, build_bundle(docs)[0])
        named = [v for d in docs.values() if 'assessment' in d
                 for v in d['assessment'].get('variables', {}).values() if v['kind'] == 'constant']
        self.assertTrue(any(v['expression']['literal'][-1] == 'SECOND-VALUE' for v in named))
        function = ET.Element(O + 'variable_component', var_ref=constant.get('id'))
        term = ExpandedSource(source.components[binding['component']]).function(function)
        self.assertEqual(term['constant_values'][-1], {'datatype': 'string', 'value': 'SECOND-VALUE'})
        self.assertGreater(len(term['constant_values']), 1)

    def test_ntuser_defaults_type_and_ordered_exclusions_are_preserved(self):
        xs = '{http://www.w3.org/2001/XMLSchema}'
        schema = ET.parse(ROOT / 'third_party/scap-1.4-schemas/oval_5.12.3/windows-definitions-schema.xsd').getroot()
        behaviors = schema.find(xs + 'complexType[@name="NTUserBehaviors"]')
        for name, default in (('include_default', 'false'), ('item_creation', 'key_and_name_exist')):
            declaration = behaviors.find(xs + 'attribute[@name="' + name + '"]')
            self.assertEqual((declaration.get('use'), declaration.get('default')), ('optional', default))
        a = next(d['assessment'] for d in self.docs.values() if 'assessment' in d and
                 any(t['capability'] == 'windows.ntuser' for t in d['assessment']['tests'].values()))
        test = next(t for t in a['tests'].values() if t['capability'] == 'windows.ntuser')
        self.assertIs(test['object']['include_default'], False)
        self.assertEqual(test['object']['item_creation'], 'key_and_name_exist')
        self.assertEqual(len(test['object']['filters']), 2)
        self.assertTrue(all('exclude' in f for f in test['object']['filters']))
        self.assertTrue(any(n.get('equals') == 'dword' for n in walk(test['require'])))
        for mutation in ('default', 'creation', 'filter-order'):
            docs = deepcopy(self.docs)
            native = next(t for d in docs.values() if 'assessment' in d for t in d['assessment']['tests'].values()
                          if t['capability'] == 'windows.ntuser')['object']
            if mutation == 'default': native['include_default'] = True
            elif mutation == 'creation': native['item_creation'] = 'every_ntuser'
            else: native['filters'].reverse()
            with self.subTest(mutation=mutation), self.assertRaises(AssertionError): verify_original(self.source.root, docs, self.trace)

    def test_iis_filter_and_function_operand_mutants_fail_source_proof(self):
        for mutation in ('filter', 'constant', 'function-order'):
            docs = deepcopy(self.docs)
            a = next(d['assessment'] for d in docs.values() if d.get('assessment', {}).get('variables') and
                     any(n.get('capability') == 'windows.appcmd' for n in walk(d)))
            if mutation == 'filter':
                f = next(n for n in walk(a) if 'include' in n); f['exclude'] = f.pop('include')
            else:
                concat = next(n['concat'] for n in walk(a) if 'concat' in n and
                              any(isinstance(v, dict) and 'literal' in v for v in n['concat']))
                if mutation == 'function-order': concat.reverse()
                else: next(v['literal'] for v in concat if 'literal' in v)['value'] += 'CHANGED'
            with self.subTest(mutation=mutation), self.assertRaises(AssertionError): verify_original(self.source.root, docs, self.trace)

    def test_pattern_path_recursion_is_invalid_in_original_schema_and_stays_blocked(self):
        schema = ET.parse(ROOT / 'third_party/scap-1.4-schemas/oval_5.12.3/windows-definitions-schema.xsd').getroot()
        assertions = [a.get('test') for rule in schema.iter() if rule.tag.endswith('}rule') and
                      'file_object/win-def:path[' in rule.get('context', '')
                      for a in rule if a.tag.endswith('}assert') and '@max_depth' in a.get('test', '')]
        self.assertTrue(assertions)
        row = next(r for r in SourceInventory(self.source).rules() if 'windows.file' in r['needed_capabilities'])
        objects = [self.source.node(n['component'], n['id'], 'object') for n in row['dependencies'] if n['kind'] == 'object']
        self.assertEqual(len(objects), 2)
        for obj in objects:
            entity = etree.fromstring(ET.tostring(obj)).find(W + 'path')
            self.assertEqual(entity.get('operation'), 'pattern match')
            self.assertTrue(all(not entity.xpath(test, namespaces={'win-def': W[1:-1]}) for test in assertions))
        with self.assertRaises(UnsupportedSource): convert(self.source, [row['source_rule']])


if __name__ == '__main__':
    unittest.main()
