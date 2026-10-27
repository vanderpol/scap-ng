"""Pinned filehash58 semantics and the reviewed native acquisition contract.

The original schema-first test identities are retained through converter
integration. Source, authoring, compilation and independent proof stay distinct.
"""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

from lxml import etree
from audit_v04_oval_test_corpus import OvalDocument, probe_mappings, assessment_for, check_conversion, closure
from v04_direct_inventory import SourceInventory
from v04_expanded_source_proof import ExpandedSource, ExpandedNative
from validate_native_json_schemas import build_validators
from oval_result_truth_tables import aggregate_check
from oval_source_validation import SourceValidator
from test_generate_capability_schema_v04 import materialize, validate
from v04_direct_converter import AssessmentConverter, load_mappings

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tests/fixtures/v04-filehash-acquisition-conflict'
O = '{http://oval.mitre.org/XMLSchema/oval-definitions-5}'
I = '{http://oval.mitre.org/XMLSchema/oval-definitions-5#independent}'


class FileHashAcquisitionConflictTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pin = json.loads((FIXTURE / 'provenance.json').read_text())
        cls.raw = (FIXTURE / Path(cls.pin['path']).name).read_bytes()
        cls.root = ET.fromstring(cls.raw)
        cls.schema = materialize('file.hash')
        cls.validator = build_validators(ROOT / 'schema/v0.4.0')['assessment.schema.json']

    def test_original_multi_algorithm_and_complement_objects_are_valid(self):
        self.assertEqual(sha256(self.raw).hexdigest(), self.pin['sha256'])
        source = SourceValidator(ROOT / 'third_party/scap-1.4-schemas/oval_5.12.3').validate(etree.fromstring(self.raw))
        self.assertEqual(source['status'], 'VALID', source)
        objects = self.root.find(O + 'objects')
        self.assertEqual(len(objects), 3)
        self.assertEqual([n.find(I + 'hash_type').get('var_check') for n in objects],
                         ['at least one', 'none satisfy', 'at least one'])
        self.assertEqual([len(n.findall(O + 'value')) for n in self.root.find(O + 'variables')], [2, 4])

    def test_schema_accepts_original_multi_algorithm_and_complement_selection(self):
        """Existing selector vocabulary, not NOT/OR or one acquisition per Test."""
        obj = {'capability': 'file.hash', 'full_path': {'equals': '/bin/ls'},
               'filesystem': 'local'}
        selections = (
            (['md5', 'sha1'], 'one_or_more'),
            (['sha224', 'sha256', 'sha384', 'sha512'], 'none'),
            (['sha224', 'sha256', 'sha384', 'sha512'], 'one_or_more'),
        )
        for algorithms, cardinality in selections:
            with self.subTest(algorithms=algorithms, value_match=cardinality):
                candidate = {**obj, 'algorithm': {'equals': algorithms,
                             'datatype': 'string', 'value_match': cardinality}}
                self.assertFalse(validate(self.schema, 'object', candidate))
                # OVAL hash_type defaults to string/equals; preserve a scalar
                # literal without a synthetic array wrapper as well.
                scalar = {**obj, 'algorithm': {'equals': algorithms[0]}}
                self.assertFalse(validate(self.schema, 'object', scalar))
        candidate = {**obj, 'algorithm': {'equals': {'variable': 'hash-types-variable'},
                     'datatype': 'string', 'value_match': 'none'}}
        self.assertFalse(validate(self.schema, 'object', candidate))

    def test_schema_rejects_missing_algorithm_and_bad_enumerations(self):
        obj = {'capability': 'file.hash', 'full_path': {'equals': '/bin/ls'},
               'filesystem': 'local', 'algorithm': {'equals': ['sha224', 'sha256'],
               'datatype': 'string', 'value_match': 'none'}}
        bad = [
            {key: value for key, value in obj.items() if key != 'algorithm'},
            {**obj, 'algorithm': 'sha256'},
            {**obj, 'algorithm': {'equals': ['sha224', 'SHA-256'],
                                'datatype': 'string', 'value_match': 'none'}},
            {**obj, 'algorithm': {'equals': ['sha224', 'sha256'], 'datatype': 'string'}},
            {**obj, 'algorithm': {'equals': 'sha256', 'value_match': 'none'}},
            {**obj, 'algorithm': {'pattern_match': 'sha.*', 'datatype': 'string'}},
        ]
        for candidate in bad:
            with self.subTest(candidate=candidate):
                self.assertTrue(validate(self.schema, 'object', candidate))

    def test_state_algorithm_value_match_independent_of_collected_items(self):
        for algorithms, value_match in (
            (['sha224', 'sha256', 'sha384', 'sha512'], 'none'),
            (['md5', 'sha1'], 'one_or_more'),
        ):
            candidate = {'algorithm': {'equals': algorithms, 'datatype': 'string',
                         'value_match': value_match, 'values_found': 'one_or_more',
                         'values_matching': 'every'}}
            self.assertFalse(validate(self.schema, 'state_expression', candidate))

    def test_original_source_binding_is_now_mapped_but_converter_remains_deferred(self):
        mappings = probe_mappings()
        mapping = next(m for m in mappings if m['capability'] == 'file.hash')
        self.assertEqual(mapping['native']['selector_map']['hash_type'], 'algorithm')
        self.assertEqual(mapping['native']['selector_value_crosswalk']['hash_type'], 'hash_algorithm')
        self.assertEqual(mapping['native']['state_value_crosswalk']['hash_type'], 'hash_algorithm')
        self.assertNotIn('algorithm', mapping['native'].get('collection_parameters', {}))
        # Retain the schema-owner checkpoint identity, now testing integration.
        self.assertIn('file.hash', {m['capability'] for m in load_mappings()})
        before = ET.tostring(self.root)
        nodes = {i: n for (_, i), n in SourceInventory(OvalDocument(self.root, 'original.xml')).nodes.items()}
        for test in self.root.find(O + 'tests'):
            visitor = self.visitor(self.root)
            ident = test.get('id')
            result = check_conversion(visitor, ident, self.validator)
            with self.subTest(test=ident):
                self.assertTrue(result['schema_valid'], result)
                self.assertTrue(result['compiled_operands_verified'], result)
                self.assertEqual(result['source_proof'], 'PROVED', result)
                dependencies, problems = closure(nodes, ident)
                self.assertFalse(problems)
                self.assertEqual(set(visitor.used), set(dependencies))
                self.assertTrue(all(v['sha256'] == nodes[k]['sha256'] for k, v in visitor.used.items()))
                self.assertEqual(assessment_for(self.visitor(self.root), ident),
                                 assessment_for(self.visitor(self.root), ident))
        self.assertEqual(ET.tostring(self.root), before)
        self.assertEqual((FIXTURE / Path(self.pin['path']).name).read_bytes(), self.raw)

    def visitor(self, root):
        return AssessmentConverter(OvalDocument(root, 'original.xml'), 'original.xml', load_mappings())

    def test_all_six_algorithms_all_four_quantifiers_and_duplicate_values(self):
        # Read the original finite Object domain from the pinned normative XSD.
        x = '{http://www.w3.org/2001/XMLSchema}'
        schema = ET.parse(ROOT / 'third_party/scap-1.4-schemas/oval_5.12.3/independent-definitions-schema.xsd')
        declaration = schema.find(x + 'complexType[@name="EntityObjectHashTypeType"]')
        domain = [e.get('value') for e in declaration.findall('.//' + x + 'enumeration') if e.get('value')]
        self.assertEqual(set(domain), {'MD5', 'SHA-1', 'SHA-224', 'SHA-256', 'SHA-384', 'SHA-512'})
        native_domain = ['md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512']
        pairs = dict(zip(domain, [v.lower().replace('-', '') for v in domain]))
        for check, match in (('all', 'every'), ('at least one', 'one_or_more'),
                             ('none satisfy', 'none'), ('only one', 'exactly_one')):
            for source_values in ([v] for v in domain):
                for values in (source_values, domain[:2], domain[2:], domain, ['MD5', 'MD5']):
                    root = deepcopy(self.root)
                    variable = root.find(O + 'variables')[0]
                    variable[:] = []
                    for value in values:
                        ET.SubElement(variable, O + 'value').text = value
                    obj = root.find(O + 'objects')[0]
                    obj.find(I + 'hash_type').set('var_check', check)
                    actual = self.visitor(root).reference(obj.get('id'), 'object')['algorithm']
                    self.assertEqual(actual, {'equals': [pairs[v] for v in values],
                                             'datatype': 'string', 'value_match': match})
                    # Independent finite relation check, over the COMPLETE six-
                    # algorithm acquisition domain, including complement and
                    # exactly-one behavior when expected values are duplicated.
                    selected = {pairs[v] for v in domain if aggregate_check(check,
                                ['true' if v == w else 'false' for w in values]) == 'true'}
                    native_selected = {v for v in native_domain if aggregate_check(check,
                                       ['true' if v == w else 'false' for w in actual['equals']]) == 'true'}
                    self.assertEqual(selected, native_selected)
        # No Variable means one scalar, with no synthetic array or value_match.
        for value in domain:
            root = deepcopy(self.root)
            obj = root.find(O + 'objects')[0]
            entity = obj.find(I + 'hash_type'); entity.attrib.clear(); entity.text = value
            self.assertEqual(self.visitor(root).reference(obj.get('id'), 'object')['algorithm'],
                             {'equals': pairs[value]})

    def test_state_inequality_retains_each_variable_quantifier(self):
        for check in ('all', 'at least one', 'none satisfy', 'only one'):
            root = deepcopy(self.root)
            for state in root.find(O + 'states'):
                entity = state.find(I + 'hash_type')
                entity.set('operation', 'not equal'); entity.set('var_check', check)
            validity = SourceValidator(ROOT / 'third_party/scap-1.4-schemas/oval_5.12.3').validate(
                etree.fromstring(ET.tostring(root)))
            self.assertEqual(validity['status'], 'VALID', validity)
            for test in root.find(O + 'tests'):
                result = check_conversion(self.visitor(root), test.get('id'), self.validator)
                self.assertEqual(result['source_proof'], 'PROVED', result)
                self.assertTrue(result['compiled_operands_verified'], result)

    def test_runtime_variable_preserves_typed_projection_and_unique_graph(self):
        for check in ('all', 'at least one', 'none satisfy', 'only one'):
            for unique in (False, True):
                root = deepcopy(self.root)
                obj = root.find(O + 'objects')[0]
                source = deepcopy(obj); source.set('id', 'oval:org.scapng.hash:obj:1')
                entity = source.find(I + 'hash_type'); entity.attrib.clear(); entity.text = 'SHA-256'
                root.find(O + 'objects').append(source)
                variable = root.find(O + 'variables')[0]
                variable.tag = O + 'local_variable'; variable[:] = []
                parent = ET.SubElement(variable, O + 'unique') if unique else variable
                ET.SubElement(parent, O + 'object_component', object_ref=source.get('id'), item_field='hash_type')
                obj.find(I + 'hash_type').set('var_check', check)
                ident = root.find(O + 'tests')[0].get('id')
                validity = SourceValidator(ROOT / 'third_party/scap-1.4-schemas/oval_5.12.3').validate(
                    etree.fromstring(ET.tostring(root)))
                self.assertEqual(validity['status'], 'VALID', validity)
                result = check_conversion(self.visitor(root), ident, self.validator)
                self.assertEqual(result['source_proof'], 'PROVED', result)
                self.assertTrue(result['compiled_operands_verified'], result)
                visitor = self.visitor(root)
                a = assessment_for(visitor, ident)
                test = a['tests'][a['evaluate']['test']]
                self.assertEqual(test['object']['algorithm']['datatype'], 'string')
                self.assertIn('variable', test['object']['algorithm']['equals'])
                self.assertEqual(len(a['variables']), 1)
                state = next(s for s in root.find(O + 'states')
                             if s.find(I + 'hash_type').get('var_ref') == variable.get('id'))
                state.find(I + 'hash_type').set('var_check', check)
                state_test = next(t for t in root.find(O + 'tests')
                                  if any(c.get('state_ref') == state.get('id') for c in t))
                for operation in ('equals', 'not equal'):
                    state.find(I + 'hash_type').set('operation', operation)
                    result = check_conversion(self.visitor(root), state_test.get('id'), self.validator)
                    self.assertEqual(result['source_proof'], 'PROVED', result)
                    self.assertTrue(result['compiled_operands_verified'], result)
                # Reusing the cached enum Variable as an ordinary string must
                # not change SHA-256 into sha256 outside the enum relation.
                digest = ET.Element(I + 'hash', var_ref=variable.get('id'))
                mapping = next(m for m in load_mappings() if m['capability'] == 'file.hash')
                with self.assertRaisesRegex(ValueError, 'matching enum consumer'):
                    visitor.predicate(digest, mapping)
                original_string = ExpandedSource(root).entity(digest)
                native_string = ExpandedNative(a).predicate({
                    'equals': test['object']['algorithm']['equals'], 'datatype': 'string',
                    'value_match': 'every', 'values_found': 'one_or_more', 'values_matching': 'every'})
                self.assertNotEqual(original_string, native_string)

    def test_unsupported_enum_operands_fail_closed_and_mutations_do_not_prove(self):
        for mutation in ('invalid', 'empty-artifact', 'wrong-case', 'pattern', 'computed-string'):
            root = deepcopy(self.root)
            variable = root.find(O + 'variables')[0]
            if mutation == 'computed-string':
                variable.tag = O + 'local_variable'; variable[:] = []
                ET.SubElement(variable, O + 'literal_component', datatype='string').text = 'SHA-256'
                expected = 'approved alias-domain projection'
            elif mutation == 'pattern':
                root.find(O + 'objects')[0].find(I + 'hash_type').set('operation', 'pattern match')
                expected = 'unsupported enum'
            else:
                variable[0].text = {'invalid': 'SHA-999', 'empty-artifact': '', 'wrong-case': 'sha256'}[mutation]
                expected = 'enum'
            with self.subTest(mutation=mutation), self.assertRaisesRegex(ValueError, expected):
                assessment_for(self.visitor(root), root.find(O + 'tests')[0].get('id'))
        for test in self.root.find(O + 'tests'):
            ident = test.get('id')
            a = assessment_for(self.visitor(self.root), ident)
            source = ExpandedSource(self.root).test(ident)
            for mutation in ('algorithm', 'value-match', 'population', 'filesystem'):
                wrong = deepcopy(a)
                native = wrong['tests'][wrong['evaluate']['test']]
                if mutation == 'algorithm': native['object']['algorithm']['equals'][0] = 'sha1'
                elif mutation == 'value-match':
                    old = native['object']['algorithm']['value_match']
                    native['object']['algorithm']['value_match'] = 'every' if old != 'every' else 'none'
                elif mutation == 'population': native['require']['items_satisfying'] = 'one_or_more'
                else: native['object']['filesystem'] = 'local'
                with self.subTest(test=ident, mutation=mutation):
                    self.assertNotEqual(source, ExpandedNative(wrong).test(wrong['evaluate']['test']))


if __name__ == '__main__':
    unittest.main()
