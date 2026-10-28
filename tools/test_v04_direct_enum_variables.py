"""Closed enum Variables retain shared source graphs and independent matching."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET
from lxml import etree

from audit_v04_oval_test_corpus import OvalDocument, assessment_for, check_conversion, closure
from inventory_v04_six_source_requirements import closure_validity
from oval_source_validation import SourceValidator
from v04_direct_converter import AssessmentConverter, load_mappings
from v04_direct_inventory import SourceInventory
from v04_direct_scap_source import native_identifier
from v04_expanded_source_proof import ExpandedSource, ExpandedNative
from validate_native_json_schemas import build_validators

ROOT = Path(__file__).resolve().parents[1]
O = '{http://oval.mitre.org/XMLSchema/oval-definitions-5}'
I = '{http://oval.mitre.org/XMLSchema/oval-definitions-5#independent}'
W = '{http://oval.mitre.org/XMLSchema/oval-definitions-5#windows}'
REGISTRY = 'oval:navy.navwar.niwcatlantic.scc.test:tst:4000'
HIVE = 'oval:navy.navwar.niwcatlantic.scc.test:var:4000'
HASH = 'oval:org.mitre.oval.test:tst:305'
LOCAL = 'oval:org.scapng.enum:var:900'
ALGORITHMS = ['MD5', 'SHA-1', 'SHA-224', 'SHA-256', 'SHA-384', 'SHA-512', 'MD5']
NATIVE_ALGORITHMS = ['md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512', 'md5']


def walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


class ClosedEnumVariableTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validator = build_validators(ROOT / 'schema/v0.4.0')['assessment.schema.json']
        cls.source_validator = SourceValidator(ROOT / 'third_party/scap-1.4-schemas/oval_5.12.3')
        cls.mappings = load_mappings()

    def original(self, folder, filename):
        directory = ROOT / 'tests/fixtures' / folder
        pin = json.loads((directory / 'provenance.json').read_text())
        item = next(x for x in pin.get('files', [pin]) if Path(x['path']).name == filename)
        raw = (directory / filename).read_bytes()
        self.assertEqual(sha256(raw).hexdigest(), item['sha256'])
        return ET.fromstring(raw)

    def registry(self):
        return self.original('v04-direct-proof-aliases', 'win-def_registry_test.xml')

    def visitor(self, root):
        return AssessmentConverter(OvalDocument(root, 'original.xml'), 'original.xml', self.mappings)

    def check(self, root, ident):
        before = ET.tostring(root)
        visitor = self.visitor(root)
        result = check_conversion(visitor, ident, self.validator)
        self.assertTrue(result['schema_valid'], result)
        self.assertTrue(result['compiled_operands_verified'], result)
        self.assertEqual(result['source_proof'], 'PROVED', result)
        nodes = {i: n for (_, i), n in SourceInventory(OvalDocument(root, 'original.xml')).nodes.items()}
        ids, problems = closure(nodes, ident)
        self.assertFalse(problems)
        self.assertEqual(set(visitor.used), set(ids))
        report = self.source_validator.validate(etree.fromstring(ET.tostring(root)))
        validity = closure_validity([nodes[i] for i in ids], {'original.xml': report})
        self.assertEqual(validity['status'], 'VALID', validity)
        self.assertFalse(any(i['kind'] == 'deprecated' for i in validity['issues']))
        self.assertEqual(ET.tostring(root), before)
        return visitor, assessment_for(visitor, ident)

    def hash_graph(self, check='all', unique=False):
        root = self.original('v04-filehash-acquisition-conflict', 'ind-def_filehash58_test_unix.xml')
        byid = {n.get('id'): n for n in root.iter() if n.get('id')}
        obj = byid[byid[HASH].find(I + 'object').get('object_ref')]
        entity = obj.find(I + 'hash_type')
        constant = byid[entity.get('var_ref')]
        constant[:] = []
        for value in ALGORITHMS:
            ET.SubElement(constant, O + 'value').text = value
        local = ET.SubElement(root.find(O + 'variables'), O + 'local_variable',
                              id=LOCAL, version='1', datatype='string', comment='Closed algorithm Variable graph')
        parent = ET.SubElement(local, O + 'unique') if unique else local
        ET.SubElement(parent, O + 'variable_component', var_ref=constant.get('id'))
        entity.set('var_ref', LOCAL); entity.set('var_check', check)
        return root, constant, local

    def test_original_registry_4000_preserves_source_and_records_translated_graph(self):
        root = self.registry()
        visitor, a = self.check(root, REGISTRY)
        original = native_identifier(next(n for n in root.find(O + 'variables') if n.get('id') == HIVE), 'variable')
        record, = visitor.enum_variable_equivalences
        self.assertEqual(record['source_variable'], HIVE)
        self.assertEqual(record['source_native_variable'], original)
        self.assertEqual(a['variables'][original]['expression']['literal']['value'], 'HKEY_LOCAL_MACHINE')
        self.assertEqual(a['variables'][record['native_variable']]['expression']['literal']['value'], 'local_machine')
        self.assertEqual(a, assessment_for(self.visitor(root), REGISTRY))
        for source_check, native_check in (('all', 'every'), ('at least one', 'one_or_more'),
                                           ('none satisfy', 'none'), ('only one', 'exactly_one')):
            controlled = deepcopy(root)
            byid = {n.get('id'): n for n in controlled.iter() if n.get('id')}
            state = byid[byid[REGISTRY].find(W + 'state').get('state_ref')]
            entity = state.find(W + 'hive')
            entity.text = None; entity.set('var_ref', HIVE); entity.set('var_check', source_check)
            visited, native = self.check(controlled, REGISTRY)
            predicate = next(n for n in walk(native['tests'][native['evaluate']['test']]['require'])
                             if isinstance(n.get('equals'), dict))
            self.assertEqual((predicate['datatype'], predicate['value_match']), ('string', native_check))
            self.assertEqual(predicate['values_matching'], 'every')
            self.assertEqual(len(visited.enum_variable_equivalences), 1)

    def test_all_algorithms_duplicates_unique_and_four_variable_quantifiers(self):
        for source_check, native_check in (('all', 'every'), ('at least one', 'one_or_more'),
                                           ('none satisfy', 'none'), ('only one', 'exactly_one')):
            for unique in (False, True):
                with self.subTest(var_check=source_check, unique=unique):
                    root, constant, _ = self.hash_graph(source_check, unique)
                    visitor, a = self.check(root, HASH)
                    predicate = next(n['algorithm'] for n in walk(a['tests']) if 'algorithm' in n)
                    self.assertEqual((predicate['datatype'], predicate['value_match']), ('string', native_check))
                    self.assertEqual(set(predicate['equals']), {'variable'})
                    self.assertEqual(len(a['tests']), 1)
                    translated = [r['native_variable'] for r in visitor.enum_variable_equivalences]
                    arrays = [a['variables'][n]['expression']['literal'] for n in translated
                              if a['variables'][n]['kind'] == 'constant']
                    self.assertEqual(arrays, [NATIVE_ALGORITHMS])
                    original = native_identifier(constant, 'variable')
                    self.assertEqual(a['variables'][original]['expression']['literal'], ALGORITHMS)
                    self.assertEqual(any('unique' in a['variables'][n]['expression'] for n in translated), unique)
                    self.assertEqual({r['source_variable'] for r in visitor.enum_variable_equivalences}, {LOCAL, constant.get('id')})

    def test_shared_generic_string_use_is_unchanged_in_both_conversion_orders(self):
        for enum_first in (False, True):
            root = self.registry()
            obj = ET.SubElement(root.find(O + 'objects'), I + 'variable_object', id='oval:org.scapng.enum:obj:900', version='1', comment='Generic shared string Object')
            ET.SubElement(obj, I + 'var_ref').text = HIVE
            state = ET.SubElement(root.find(O + 'states'), I + 'variable_state', id='oval:org.scapng.enum:ste:900', version='1', comment='Generic shared string State')
            ET.SubElement(state, I + 'value').text = 'HKEY_LOCAL_MACHINE'
            test = ET.SubElement(root.find(O + 'tests'), I + 'variable_test', id='oval:org.scapng.enum:tst:900', version='1', check='all', comment='Generic shared string Test')
            ET.SubElement(test, I + 'object', object_ref=obj.get('id'))
            ET.SubElement(test, I + 'state', state_ref=state.get('id'))
            nodes = {i: n for (_, i), n in SourceInventory(OvalDocument(root, 'original.xml')).nodes.items()}
            selected = set()
            for ident in (REGISTRY, test.get('id')):
                ids, problems = closure(nodes, ident)
                self.assertFalse(problems); selected.update(ids)
            report = self.source_validator.validate(etree.fromstring(ET.tostring(root)))
            validity = closure_validity([nodes[i] for i in selected], {'original.xml': report})
            self.assertEqual(validity['status'], 'VALID', validity)
            order = [REGISTRY, test.get('id')] if enum_first else [test.get('id'), REGISTRY]
            visitor = self.visitor(root)
            a = assessment_for(visitor, order[0])
            second = visitor.reference(order[1], 'test')
            for source_id, native_id in ((order[0], a['evaluate']['test']), (order[1], second['test'])):
                self.assertEqual(ExpandedSource(root).test(source_id), ExpandedNative(a).test(native_id))
            # An approved enum use cannot authorize another domain through cache.
            with self.assertRaisesRegex(ValueError, 'unsupported enum comparison/value'):
                visitor.enum_variable(HIVE, {'SHA-256': 'sha256'})
            with self.assertRaisesRegex(ValueError, 'bijective'):
                visitor.enum_variable(HIVE, {'HKEY_LOCAL_MACHINE': 'hive', 'HKEY_USERS': 'hive'})

    def test_unknown_values_noncommuting_functions_and_runtime_strings_stay_unsupported(self):
        for mutation in ('unknown', 'concat', 'cast', 'runtime'):
            root = self.registry()
            variable = next(n for n in root.find(O + 'variables') if n.get('id') == HIVE)
            if mutation == 'unknown':
                variable[0].text = 'HKEY_UNKNOWN'
            elif mutation == 'cast':
                variable[0].set('datatype', 'int'); variable[0].text = '42'
            elif mutation == 'runtime':
                obj = next(n for n in root.find(O + 'objects')
                           if n.find(W + 'hive') is not None and n.find(W + 'hive').text == 'HKEY_LOCAL_MACHINE')
                variable[:] = []
                ET.SubElement(variable, O + 'object_component', object_ref=obj.get('id'), item_field='value')
            else:
                variable[:] = []
                function = ET.SubElement(variable, O + 'concat')
                ET.SubElement(function, O + 'literal_component').text = 'HKEY_'
                ET.SubElement(function, O + 'literal_component').text = 'LOCAL_MACHINE'
            result = check_conversion(self.visitor(root), REGISTRY, self.validator)
            self.assertFalse(result['converted'], result)
            self.assertEqual(result['source_proof'], 'NOT_RUN', result)
            self.assertTrue(result['diagnostics'])

    def test_changed_translation_and_variable_matching_fail_independent_proof(self):
        root = self.registry()
        visitor, a = self.check(root, REGISTRY)
        expected = ExpandedSource(root).test(REGISTRY)
        native_id = a['evaluate']['test']
        wrong = deepcopy(a)
        record, = visitor.enum_variable_equivalences
        wrong['variables'][record['native_variable']]['expression']['literal']['value'] = 'users'
        self.assertNotEqual(expected, ExpandedNative(wrong).test(native_id))
        wrong = deepcopy(a)
        predicate = next(n for n in walk(wrong['tests']) if isinstance(n.get('equals'), dict))
        predicate['value_match'] = 'none'
        self.assertNotEqual(expected, ExpandedNative(wrong).test(native_id))
