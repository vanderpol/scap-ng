"""Approved shared controls retain their distinct AST and evidence boundaries."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json
import unittest
import xml.etree.ElementTree as ET

from audit_v04_oval_test_corpus import OvalDocument, assessment_for, check_conversion
from v04_direct_converter import AssessmentConverter, load_mappings, logical_condition
from v04_expanded_source_proof import ExpandedSource, ExpandedNative
from v04_native_bundle_compiler import compile_assessment_program
from audit_v04_eight_assessment_pilot import verify_program
from validate_native_json_schemas import build_validators, document_errors
from oval_source_validation import SourceValidator
from lxml import etree

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tests/fixtures/v04-direct-ordinary-continuation'
O = '{http://oval.mitre.org/XMLSchema/oval-definitions-5}'


class SharedControlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mappings = load_mappings()
        cls.validator = build_validators(ROOT / 'schema/v0.4.0')['assessment.schema.json']

    def convert(self, root, identifier):
        return assessment_for(AssessmentConverter(OvalDocument(root, 'source.xml'), 'source.xml', self.mappings), identifier)

    def assert_proved(self, root, identifier):
        a = self.convert(root, identifier)
        self.assertFalse(list(document_errors(self.validator, {'assessment': a})))
        verify_program(a, compile_assessment_program(a))
        self.assertEqual(ExpandedSource(root).test(identifier), ExpandedNative(a).test(a['evaluate']['test']))
        return a

    def test_original_unknown_has_no_fabricated_object_or_result(self):
        raw = (FIXTURE / 'ind-def_unknown_test.xml').read_bytes()
        self.assertEqual(sha256(raw).hexdigest(), 'f5e8901c703438819f20ef4761d1b4f9f62f630c6c8e96ca016d0d0dd67862a7')
        validation = SourceValidator(ROOT / 'third_party/scap-1.4-schemas/oval_5.12.3').validate(etree.fromstring(raw))
        self.assertEqual(validation['status'], 'VALID')
        root = ET.fromstring(raw)
        test = root.find(O + 'tests')[0]
        a = self.assert_proved(root, test.get('id'))
        native_id = a['evaluate']['test']
        self.assertEqual(set(a['tests'][native_id]), {'capability', 'test_title', 'require', 'reported_elements'})
        for field, value in (('object', {}), ('result', 'true')):
            bad = deepcopy(a)
            bad['tests'][native_id][field] = value
            self.assertTrue(list(document_errors(self.validator, {'assessment': bad})))
            with self.assertRaises(ValueError):
                ExpandedNative(bad).test(native_id)
        for existence in ('all_exist', 'none_exist', 'any_exist', 'only_one_exists'):
            test.set('check_existence', existence)
            self.assert_proved(root, test.get('id'))
        ET.SubElement(test, test.tag.replace('unknown_test', 'object'), object_ref='oval:missing:obj:1')
        with self.assertRaises(ValueError):
            self.convert(root, test.get('id'))

    def test_field_every_does_not_admit_generic_test_all_exist(self):
        root = ET.parse(FIXTURE / 'linux-def_apparmorstatus_test.xml').getroot()
        test = root.find(O + 'tests')[0]
        state = root.find(O + 'states')[0]
        state[0].set('check_existence', 'all_exist')
        a = self.assert_proved(root, test.get('id'))
        self.assertIn('"values_found": "every"', json.dumps(a))
        test.set('check_existence', 'all_exist')
        with self.assertRaisesRegex(ValueError, 'all_exist'):
            self.convert(root, test.get('id'))

    def test_record_every_retains_record_and_member_boundaries(self):
        fixture = json.loads((ROOT / 'tests/fixtures/v04-proof-expansion/windows-01.json').read_text())
        root = ET.fromstring(fixture['source_xml'])
        test = root.find(O + 'tests')[0]
        # Controlled variation isolates field existence from the separately
        # blocked generic Test all_exist normalization.
        test.set('check_existence', 'at_least_one_exists')
        record = next(n for n in root.find(O + 'states').iter() if n.get('datatype') == 'record')
        record.set('check_existence', 'all_exist')
        a = self.assert_proved(root, test.get('id'))
        self.assertIn('"records_found": "every"', json.dumps(a))
        self.assertIn('"values_found": "one_or_more"', json.dumps(a))
        # OVAL record members have entity_check but no check_existence.
        record[0].set('check_existence', 'all_exist')
        with self.assertRaisesRegex(ValueError, 'unsupported attributes'):
            self.convert(root, test.get('id'))

    def test_one_and_xor_survive_singleton_and_multiple_branches(self):
        root = ET.parse(FIXTURE / 'linux-def_apparmorstatus_test.xml').getroot()
        test = root.find(O + 'tests')[0]
        state = root.find(O + 'states')[0]
        for operator in ('ONE', 'XOR'):
            for count in (1, 3):
                with self.subTest(operator=operator, count=count):
                    children = [{'test': str(i)} for i in range(count)]
                    self.assertEqual(logical_condition(operator, children), {operator.lower(): children})
                    state.set('operator', operator)
                    a = self.assert_proved(root, test.get('id'))
                    self.assertIn('"' + operator.lower() + '"', json.dumps(a))
                    visitor = AssessmentConverter(OvalDocument(root, 'source.xml'), 'source.xml', self.mappings)
                    criteria = ET.Element(O + 'criteria', operator=operator)
                    for _ in range(count):
                        ET.SubElement(criteria, O + 'criterion', test_ref=test.get('id'))
                    self.assertEqual(len(visitor.criteria(criteria)[operator.lower()]), count)
        with self.assertRaises(ValueError):
            logical_condition('ONE', [])


if __name__ == '__main__':
    unittest.main()
