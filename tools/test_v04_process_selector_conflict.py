"""Review evidence only: do not admit an approved mapping with an invalid schema."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

from jsonschema import Draft202012Validator
from referencing import Resource
from lxml import etree

from audit_v04_oval_test_corpus import OvalDocument, assessment_for, probe_mappings
from generate_capability_schema_v04 import generate
from oval_source_validation import SourceValidator
from v04_direct_converter import AssessmentConverter, load_mappings
from validate_native_json_schemas import build_validators, document_errors

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tests/fixtures/v04-process-selector-conflict'
O = '{http://oval.mitre.org/XMLSchema/oval-definitions-5}'


class ProcessSelectorConflictTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pin = json.loads((FIXTURE / 'provenance.json').read_text())
        raw = (FIXTURE / Path(pin['file']).name).read_bytes()
        assert sha256(raw).hexdigest() == pin['sha256']
        cls.raw = raw
        cls.root = ET.fromstring(raw)
        cls.mappings = probe_mappings()
        cls.mapping = next(m for m in cls.mappings if m['capability'] == 'unix.process58')
        cls.validator = build_validators(ROOT / 'schema/v0.4.0')['assessment.schema.json']

    def test_valid_original_combined_selectors_are_blocked_by_overlapping_one_of(self):
        original = SourceValidator(ROOT / 'third_party/scap-1.4-schemas/oval_5.12.3').validate(etree.fromstring(self.raw))
        self.assertEqual(original['status'], 'VALID', original)
        seen = 0
        for test in self.root.find(O + 'tests'):
            assessment = assessment_for(AssessmentConverter(OvalDocument(self.root, 'original.xml'), 'original.xml', self.mappings), test.get('id'))
            errors = list(document_errors(self.validator, {'assessment': assessment}))
            self.assertTrue(errors, test.get('id'))
            self.assertTrue(any('valid under each' in e.message for e in errors), errors)
            seen += 1
        self.assertEqual(seen, 8)
        self.assertNotIn('unix.process58', {m['capability'] for m in load_mappings()})

    def test_review_only_exact_alternative_proposal_has_bounded_effect(self):
        # This candidate exists only inside this test. It is not validation
        # authority and is not used by conversion, compilation or admission.
        candidate = deepcopy(generate(self.mapping, ROOT))
        selectors = set(self.mapping['native']['selector_map'].values())
        for variant in candidate['$defs']['object']['oneOf']:
            if 'set' in variant['required']:
                continue
            excluded = (selectors - set(variant['required'])) | {'set'}
            variant['not'] = {'anyOf': [{'required': [field]} for field in sorted(excluded)]}
        registry = self.validator._registry.with_resource(candidate['$id'], Resource.from_contents(candidate))
        validator = Draft202012Validator({'$ref': candidate['$id'] + '#/$defs/object'}, registry=registry)
        test = self.root.find(O + 'tests')[0]
        assessment = assessment_for(AssessmentConverter(OvalDocument(self.root, 'original.xml'), 'original.xml', self.mappings), test.get('id'))
        obj = next(iter(assessment['tests'].values()))['object']
        self.assertFalse(list(validator.iter_errors(obj)))
        for field in selectors:
            self.assertFalse(list(validator.iter_errors({field: obj[field]})))
        for wrong in ({**obj, 'invented': True}, {**obj, 'set': {'operator': 'union', 'operands': []}},
                      {'pid': {'equals': 'not an integer', 'datatype': 'string'}}):
            self.assertTrue(list(validator.iter_errors(wrong)))


if __name__ == '__main__':
    unittest.main()
