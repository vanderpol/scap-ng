"""Original OpenSSH text-file acquisition, regex flags and capture requirements."""
from copy import deepcopy
import itertools
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

import yaml
from lxml import etree

from v04_direct_scap_source import SourceModel, UnsupportedSource, OVAL
from v04_direct_inventory import SourceInventory
from v04_direct_converter import convert
from v04_direct_yaml import authoring_yaml
from v04_expanded_source_proof import ExpandedSource
from audit_v04_direct_benchmark import verify_original, verify_compiled
from v04_native_bundle_compiler import build_bundle
from validate_native_json_schemas import build_validators, document_errors
from v04_direct_authoring_examples import walk

ROOT = Path(__file__).resolve().parents[1]
PINS = json.loads((ROOT / 'tests/fixtures/v04-direct-prototype/provenance.json').read_text())
I = '{' + OVAL + '#independent}'
CAP = 'independent.textfilecontent'


class DirectTextFileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SourceModel(ROOT / 'tests/fixtures/v04-direct-prototype' / PINS['fixture'], PINS['zip_sha256'])
        cls.rules = [r['source_rule'] for r in SourceInventory(cls.source).rules() if CAP in r['needed_capabilities']]
        cls.docs, cls.trace = convert(cls.source, cls.rules)
        original = etree.parse(str(ROOT / 'third_party/scap-1.4-schemas/oval_5.12.3/independent-definitions-schema.xsd')).getroot()
        cls.source_namespaces = {k: v for k, v in original.nsmap.items() if k}
        cls.path_rules = [r for r in original.iter('{http://purl.oclc.org/dsdl/schematron}rule')
                          if r.get('context', '').startswith(('ind-def:textfilecontent54_object/ind-def:filepath',
                                                             'ind-def:textfilecontent54_object/ind-def:path'))]

    def source_scope_violations(self, obj):
        # Execute the exact original path/behavior assertions in their original
        # context. Whole-source validity is a separate integration gate; do not
        # revalidate a large unchanged datastream for each controlled parameter.
        tree = etree.fromstring(ET.tostring(obj)).getroottree()
        matched, failures = 0, []
        for rule in self.path_rules:
            for entity in tree.xpath('/' + rule.get('context'), namespaces=self.source_namespaces):
                matched += 1
                for assertion in rule.findall('{http://purl.oclc.org/dsdl/schematron}assert'):
                    if not entity.xpath(assertion.get('test'), namespaces=self.source_namespaces):
                        failures.append(' '.join(''.join(assertion.itertext()).split()))
        self.assertGreater(matched, 0, 'original scoped Schematron was not exercised')
        return failures

    def object(self, source):
        binding = self.trace['rules'][0]
        identifier = next(i for i, n in binding['dependencies'].items() if n['kind'] == 'object')
        return binding, source.node(binding['component'], identifier, 'object')

    def test_all_seven_actual_closures_validate_compile_prove_and_roundtrip_yaml(self):
        self.assertEqual(len(self.rules), 7)
        self.assertEqual(len(verify_original(self.source.root, self.docs, self.trace)), 7)
        self.assertEqual(len(verify_compiled(self.docs, build_bundle(self.docs)[0])), 7)
        validators = build_validators(ROOT / 'schema/v0.4.0')
        for doc in self.docs.values():
            self.assertEqual(yaml.safe_load(authoring_yaml(doc)), doc)
            if 'assessment' in doc:
                self.assertFalse(list(document_errors(validators['assessment.schema.json'], doc)))
                for test in doc['assessment']['tests'].values():
                    self.assertIsInstance(test['object'], dict)
                    self.assertNotIn('capability', test['object'])
                    self.assertEqual(test['object']['filesystem'], 'all')
        self.assertTrue(any(n.get('datatype') == 'integer' and n.get('less_than_or_equal') == 600
                            for d in self.docs.values() for n in walk(d)))

    def test_original_optional_defaults_and_all_boolean_flag_combinations_are_exact(self):
        xs = '{http://www.w3.org/2001/XMLSchema}'
        schema = ET.parse(ROOT / 'third_party/scap-1.4-schemas/oval_5.12.3/independent-definitions-schema.xsd').getroot()
        kind = schema.find(xs + 'complexType[@name="Textfilecontent54Behaviors"]')
        attrs = {n.get('name'): n for n in kind.findall('.//' + xs + 'attribute')}
        for name, default in (('ignore_case', 'false'), ('multiline', 'true'), ('singleline', 'false')):
            self.assertEqual((attrs[name].get('use'), attrs[name].get('default')), ('optional', default))
        self.assertEqual((attrs['item_creation'].get('use'), attrs['item_creation'].get('default')),
                         ('optional', 'all_object_elements_fullfilled'))
        scope = schema.find(xs + 'complexType[@name="FileBehaviors"]/' + xs + 'attribute[@name="recurse_file_system"]')
        self.assertEqual((scope.get('use'), scope.get('default')), ('optional', 'all'))
        for flags in itertools.product(('0', '1'), repeat=3):
            source = deepcopy(self.source)
            binding, obj = self.object(source)
            behavior = ET.Element(I + 'behaviors', **dict(zip(('ignore_case', 'multiline', 'singleline'), flags)))
            obj.insert(0, behavior)
            docs, trace = convert(source, [binding['source_rule']])
            verify_original(source.root, docs, trace)
            verify_compiled(docs, build_bundle(docs)[0])
            test = next(t for d in docs.values() if 'assessment' in d for t in d['assessment']['tests'].values())
            self.assertEqual(tuple(test['object'][k] for k in ('ignore_case', 'multiline', 'singleline')),
                             tuple(v == '1' for v in flags))

    def test_item_creation_and_filesystem_scope_are_not_discarded(self):
        for creation, scope in itertools.product(('all_object_elements_fullfilled', 'filepath_exists'), ('all', 'local', 'defined')):
            source = deepcopy(self.source)
            binding, obj = self.object(source)
            if scope == 'defined':
                # Original Schematron prohibits defined filesystem scope on
                # a non-equality filepath. Use a source-valid controlled equality
                # path; the original fixture itself remains unchanged.
                obj.find(I + 'filepath').set('operation', 'equals')
            obj.insert(0, ET.Element(I + 'behaviors', item_creation=creation, recurse_file_system=scope))
            self.assertFalse(self.source_scope_violations(obj))
            docs, trace = convert(source, [binding['source_rule']])
            verify_original(source.root, docs, trace)
            verify_compiled(docs, build_bundle(docs)[0])
            test = next(t for d in docs.values() if 'assessment' in d for t in d['assessment']['tests'].values())
            self.assertEqual(test['object']['item_creation'], creation)
            self.assertEqual(test['object']['filesystem'], 'same' if scope == 'defined' else scope)

    def test_original_pattern_filepath_with_defined_scope_is_rejected(self):
        for operation in ('pattern match', 'case insensitive equals'):
            source = deepcopy(self.source); binding, obj = self.object(source)
            obj.find(I + 'filepath').set('operation', operation)
            obj.insert(0, ET.Element(I + 'behaviors', recurse_file_system='defined'))
            self.assertTrue(any('recurse_file_system' in message for message in self.source_scope_violations(obj)))
            with self.assertRaises(UnsupportedSource): convert(source, [binding['source_rule']])
            with self.assertRaises(ValueError):
                ExpandedSource(source.components[binding['component']]).object(obj.get('id'))

    def test_changed_flags_patterns_instances_and_capture_datatypes_fail_independent_proof(self):
        for mutation in ('ignore_case', 'multiline', 'singleline', 'item_creation', 'filesystem', 'pattern', 'instance', 'capture'):
            docs = deepcopy(self.docs)
            tests = [t for d in docs.values() if 'assessment' in d for t in d['assessment']['tests'].values()]
            test = tests[0]
            if mutation in ('ignore_case', 'multiline', 'singleline'): test['object'][mutation] = not test['object'][mutation]
            elif mutation == 'item_creation': test['object'][mutation] = 'filepath_exists'
            elif mutation == 'filesystem': test['object'][mutation] = 'local'
            elif mutation == 'pattern': test['object']['pattern']['matches_regex'] += 'changed'
            elif mutation == 'instance':
                instance = test['object']['instance']; instance['equals'] = instance.pop('greater_than_or_equal')
            else:
                field = next(n for t in tests for n in walk(t['require']) if n.get('datatype') == 'integer')
                field['datatype'] = 'string'
            with self.subTest(mutation=mutation), self.assertRaises(AssertionError):
                verify_original(self.source.root, docs, self.trace)

    def test_invalid_duplicate_nested_and_unimplemented_behavior_attributes_fail_closed(self):
        for mutation in ('boolean', 'scope', 'creation', 'view', 'traversal', 'nested', 'duplicate', 'unknown'):
            source = deepcopy(self.source)
            binding, obj = self.object(source)
            behavior = ET.Element(I + 'behaviors'); obj.insert(0, behavior)
            if mutation == 'boolean': behavior.set('ignore_case', 'yes')
            elif mutation == 'scope': behavior.set('recurse_file_system', 'invented')
            elif mutation == 'creation': behavior.set('item_creation', 'invented')
            elif mutation == 'view': behavior.set('windows_view', '32_bit')
            elif mutation == 'traversal': behavior.set('recurse_direction', 'down')
            elif mutation == 'nested': ET.SubElement(behavior, I + 'invented')
            elif mutation == 'duplicate': obj.insert(0, ET.Element(I + 'behaviors'))
            else: behavior.set('invented', 'value')
            with self.subTest(mutation=mutation), self.assertRaises(UnsupportedSource):
                convert(source, [binding['source_rule']])
            with self.assertRaises(ValueError):
                ExpandedSource(source.components[binding['component']]).object(obj.get('id'))


if __name__ == '__main__':
    unittest.main()
