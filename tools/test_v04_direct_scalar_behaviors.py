"""Scalar behavior routes preserve original defaults separately from predicates."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

from audit_v04_oval_test_corpus import OvalDocument, assessment_for, check_conversion
from v04_direct_converter import AssessmentConverter, load_mappings
from v04_direct_scalar_behaviors import original_attributes, scalar_behaviors
from v04_expanded_source_proof import ExpandedSource, ExpandedNative
from validate_native_json_schemas import build_validators

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tests/fixtures/v04-direct-scalar-behaviors'
O = '{http://oval.mitre.org/XMLSchema/oval-definitions-5}'
L = '{http://oval.mitre.org/XMLSchema/oval-definitions-5#linux}'


class ScalarBehaviorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mappings = load_mappings()
        cls.mapping = next(m for m in cls.mappings if m['capability'] == 'linux.rpminfo')
        cls.validator = build_validators(ROOT / 'schema/v0.4.0')['assessment.schema.json']

    def original(self):
        pin = json.loads((FIXTURE / 'provenance.json').read_text())['files'][0]
        raw = (FIXTURE / Path(pin['path']).name).read_bytes()
        self.assertEqual(sha256(raw).hexdigest(), pin['sha256'])
        return ET.fromstring(raw)

    def test_all_original_rpm_cases_compile_and_prove(self):
        root = self.original()
        tests = root.find(O + 'tests')
        self.assertEqual(len(tests), 3)
        for test in tests:
            result = check_conversion(AssessmentConverter(OvalDocument(root, 'original.xml'), 'original.xml', self.mappings), test.get('id'), self.validator)
            with self.subTest(test=test.get('id')):
                self.assertTrue(result['compiled'], result)
                self.assertEqual(result['source_proof'], 'PROVED', result)

    def test_original_default_and_explicit_boolean_controls_are_independently_preserved(self):
        declaration = original_attributes(self.mapping['source']['definitions_schema'], self.mapping['source']['object'])['filepaths']
        self.assertEqual((declaration['type'].split(':')[-1], declaration['use'], declaration['default']), ('boolean', 'optional', 'false'))
        self.assertEqual(scalar_behaviors(None, self.mapping), {'include_file_paths': False})
        for token, expected in (('true', True), ('1', True), ('false', False), ('0', False)):
            root = self.original()
            test = root.find(O + 'tests')[0]
            obj = root.find(O + 'objects')[0]
            obj.insert(0, ET.Element(L + 'behaviors', filepaths=token))
            assessment = assessment_for(AssessmentConverter(OvalDocument(root, 'original.xml'), 'original.xml', self.mappings), test.get('id'))
            identifier = assessment['evaluate']['test']
            self.assertEqual(assessment['tests'][identifier]['object']['include_file_paths'], expected)
            source_term = ExpandedSource(root).test(test.get('id'))
            self.assertEqual(source_term, ExpandedNative(assessment).test(identifier))
            wrong = deepcopy(assessment)
            wrong['tests'][identifier]['object']['include_file_paths'] = not expected
            self.assertNotEqual(source_term, ExpandedNative(wrong).test(identifier))

    def test_invalid_unknown_duplicate_and_foreign_behaviors_fail_closed(self):
        for mutation in ('boolean', 'unknown', 'duplicate', 'foreign'):
            root = self.original()
            obj = root.find(O + 'objects')[0]
            behavior = ET.Element(L + 'behaviors', filepaths='false')
            obj.insert(0, behavior)
            if mutation == 'boolean':
                behavior.set('filepaths', 'yes')
            elif mutation == 'unknown':
                behavior.set('invented', 'true')
            elif mutation == 'duplicate':
                obj.insert(0, deepcopy(behavior))
            else:
                behavior.tag = '{urn:foreign}behaviors'
            identifier = root.find(O + 'tests')[0].get('id')
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                assessment_for(AssessmentConverter(OvalDocument(root, 'original.xml'), 'original.xml', self.mappings), identifier)
            with self.assertRaises(ValueError):
                ExpandedSource(root).object(obj.get('id'))


if __name__ == '__main__':
    unittest.main()
