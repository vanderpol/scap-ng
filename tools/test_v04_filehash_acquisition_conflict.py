"""Pinned filehash58 semantics and the reviewed native acquisition contract.

The converter is deliberately not activated here: this module exercises the
schema-first checkpoint and keeps source lowering fail-closed until integrated.
"""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

from lxml import etree
from audit_v04_oval_test_corpus import OvalDocument, probe_mappings
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
        self.assertNotIn('file.hash', {m['capability'] for m in load_mappings()})
        for obj in self.root.find(O + 'objects'):
            visitor = AssessmentConverter(OvalDocument(self.root, 'original.xml'), 'original.xml', mappings)
            with self.subTest(object=obj.get('id')), self.assertRaisesRegex(ValueError, 'unsupported enum comparison/value'):
                visitor.reference(obj.get('id'), 'object')


if __name__ == '__main__':
    unittest.main()
