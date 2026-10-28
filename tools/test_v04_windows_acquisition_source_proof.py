"""Independently prove original Windows acquisition; existing programs stay fixed."""
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
from v04_expanded_source_proof import ExpandedSource, ExpandedNative
from validate_native_json_schemas import build_validators, document_errors
from v04_windows_acquisition_source_proof import ntuser_defaults

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tests/fixtures/v04-windows-acquisition-proof'


def objects(value):
    if isinstance(value, dict):
        if 'object' in value and isinstance(value['object'], dict):
            yield value['object']
        for child in value.values():
            yield from objects(child)
    elif isinstance(value, list):
        for child in value:
            yield from objects(child)


class WindowsAcquisitionProofTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pin = json.loads((FIXTURE / 'provenance.json').read_text())
        cls.validator = build_validators(ROOT / 'schema/v0.4.0')['assessment.schema.json']
        cls.source_validator = SourceValidator(ROOT / 'third_party/scap-1.4-schemas/oval_5.12.3')
        cls.mappings = load_mappings()

    def originals(self):
        for item in self.pin['files']:
            raw = (FIXTURE / Path(item['path']).name).read_bytes()
            self.assertEqual(sha256(raw).hexdigest(), item['sha256'])
            yield item, raw, ET.fromstring(raw)

    def visitor(self, root):
        return AssessmentConverter(OvalDocument(root, 'original.xml'), 'original.xml', self.mappings)

    def test_eight_original_cases_validate_compile_and_prove_with_unchanged_programs(self):
        checked = 0
        for item, raw, root in self.originals():
            report = self.source_validator.validate(etree.fromstring(raw))
            nodes = {i: n for (_, i), n in SourceInventory(OvalDocument(root, 'original.xml')).nodes.items()}
            before = ET.tostring(root)
            for case in item['tests']:
                ident = case['id']
                visitor = self.visitor(root)
                result = check_conversion(visitor, ident, self.validator)
                with self.subTest(source=item['path'], test=ident):
                    self.assertTrue(result['schema_valid'], result)
                    self.assertTrue(result['compiled_operands_verified'], result)
                    self.assertEqual(result['source_proof'], 'PROVED', result)
                    self.assertEqual(result['program_sha256'], case['existing_program_sha256'])
                    ids, problems = closure(nodes, ident)
                    self.assertFalse(problems)
                    self.assertEqual(set(ids), set(visitor.used))
                    validity = closure_validity([nodes[i] for i in ids], {'original.xml': report})
                    self.assertEqual(validity['status'], 'VALID', validity)
                    self.assertFalse(any(i['kind'] == 'deprecated' for i in validity['issues']))
                checked += 1
            self.assertEqual(ET.tostring(root), before)
            self.assertEqual((FIXTURE / Path(item['path']).name).read_bytes(), raw)
        self.assertEqual(checked, 8)

    def test_nil_acquisition_is_not_empty_string_or_an_omitted_selector(self):
        checked = 0
        for item, _, root in self.originals():
            for case in item['tests']:
                ident = case['id']
                a = assessment_for(self.visitor(root), ident)
                acquisition = next(objects(a))
                nullable = [k for k, value in acquisition.items() if value is None]
                if not nullable:
                    continue
                self.assertEqual(len(nullable), 1)
                key, = nullable
                native_id = a['evaluate']['test']
                expected = ExpandedSource(root).test(ident)
                wrong = deepcopy(a)
                next(objects(wrong))[key] = {'equals': ''}
                self.assertFalse(list(document_errors(self.validator, {'assessment': wrong})))
                self.assertNotEqual(expected, ExpandedNative(wrong).test(native_id))
                wrong = deepcopy(a); del next(objects(wrong))[key]
                with self.assertRaises(ValueError):
                    ExpandedNative(wrong).test(native_id)
                checked += 1
        self.assertEqual(checked, 4)

    def test_ntuser_collection_defaults_depth_population_and_types_are_independent(self):
        self.assertEqual(ntuser_defaults()['include_default'], 'false')
        self.assertEqual(ntuser_defaults()['item_creation'], 'key_and_name_exist')
        checked = 0
        for item, _, root in self.originals():
            if not item['path'].endswith('win-def_ntuser_test.xml'):
                continue
            for case in item['tests']:
                ident = case['id']
                a = assessment_for(self.visitor(root), ident)
                acquisition = next(objects(a)); native_id = a['evaluate']['test']
                expected = ExpandedSource(root).test(ident)
                for field, value in (('include_default', True),
                                     ('item_creation', 'every_ntuser' if acquisition['item_creation'] == 'key_and_name_exist' else 'key_and_name_exist')):
                    wrong = deepcopy(a); next(objects(wrong))[field] = value
                    self.assertFalse(list(document_errors(self.validator, {'assessment': wrong})))
                    self.assertNotEqual(expected, ExpandedNative(wrong).test(native_id))
                wrong = deepcopy(a); next(objects(wrong))['include_default'] = 0
                with self.assertRaisesRegex(ValueError, 'NTUSER collection parameters'):
                    ExpandedNative(wrong).test(native_id)
                if 'traversal' in acquisition:
                    wrong = deepcopy(a); traversal = next(objects(wrong))['traversal']
                    traversal['max_depth'] = 2 if traversal['max_depth'] != 2 else 3
                    self.assertFalse(list(document_errors(self.validator, {'assessment': wrong})))
                    self.assertNotEqual(expected, ExpandedNative(wrong).test(native_id))
                checked += 1
        self.assertEqual(checked, 6)
