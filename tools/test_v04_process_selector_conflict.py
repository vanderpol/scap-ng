"""Owner-approved selector correction, original evidence and retained legacy failure."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

from jsonschema import Draft202012Validator
from referencing import Resource
from lxml import etree

from audit_v04_oval_test_corpus import OvalDocument, assessment_for, check_conversion, probe_mappings
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
        cls.mapping = next(m for m in cls.mappings if m['capability'] == 'unix.process')
        cls.validator = build_validators(ROOT / 'schema/v0.4.0')['assessment.schema.json']

    def test_valid_original_combined_selectors_are_blocked_by_overlapping_one_of(self):
        # Retain the original failure as a negative legacy-contract case, while
        # requiring the approved correction to validate/compile/prove all eight.
        original = SourceValidator(ROOT / 'third_party/scap-1.4-schemas/oval_5.12.3').validate(etree.fromstring(self.raw))
        self.assertEqual(original['status'], 'VALID', original)
        legacy = deepcopy(generate(self.mapping, ROOT))
        for variant in legacy['$defs']['object']['oneOf']:
            if 'set' not in variant['required']:
                variant['not'] = {'required': ['set']}
        registry = self.validator._registry.with_resource(legacy['$id'], Resource.from_contents(legacy))
        legacy_validator = Draft202012Validator({'$ref': legacy['$id'] + '#/$defs/object'}, registry=registry)
        seen = 0
        for test in self.root.find(O + 'tests'):
            assessment = assessment_for(AssessmentConverter(OvalDocument(self.root, 'original.xml'), 'original.xml', self.mappings), test.get('id'))
            errors = list(document_errors(self.validator, {'assessment': assessment}))
            self.assertFalse(errors, test.get('id'))
            obj = next(iter(assessment['tests'].values()))['object']
            self.assertTrue(any('valid under each' in e.message for e in legacy_validator.iter_errors(obj)))
            result = check_conversion(AssessmentConverter(OvalDocument(self.root, 'original.xml'), 'original.xml', load_mappings()), test.get('id'), self.validator)
            self.assertTrue(result['compiled'], result)
            self.assertEqual(result['source_proof'], 'PROVED', result)
            seen += 1
        self.assertEqual(seen, 8)
        self.assertIn('unix.process', {m['capability'] for m in load_mappings()})

    def test_review_only_exact_alternative_proposal_has_bounded_effect(self):
        # Retain the isolated proposal and require it to agree with the now
        # approved active generator; this test cannot define runtime semantics.
        candidate = deepcopy(generate(self.mapping, ROOT))
        selectors = set(self.mapping['native']['selector_map'].values())
        for variant in candidate['$defs']['object']['oneOf']:
            if 'set' in variant['required']:
                continue
            excluded = selectors - set(variant['required'])
            if excluded:
                variant['not'] = {'anyOf': [{'required': [field]} for field in sorted(excluded | {'set'})]}
        self.assertEqual(candidate, generate(self.mapping, ROOT))
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

    def test_file_alternatives_and_set_direct_exclusions_stay_exact(self):
        mapping = next(m for m in self.mappings if m['capability'] == 'unix.file')
        schema = generate(mapping, ROOT)
        registry = self.validator._registry.with_resource(schema['$id'], Resource.from_contents(schema))
        validator = Draft202012Validator({'$ref': schema['$id'] + '#/$defs/object'}, registry=registry)
        full = {'full_path': {'equals': '/etc/passwd'}, 'filesystem': 'all'}
        split = {'directory': {'equals': '/etc'}, 'name': None, 'filesystem': 'all'}
        for obj in (full, split):
            self.assertFalse(list(validator.iter_errors(obj)))
        set_object = {'set': {'operator': 'union', 'operands': [{'object': full, 'filters': []}]}}
        self.assertFalse(list(validator.iter_errors(set_object)))
        for wrong in ({**full, 'directory': split['directory']}, {**full, **split},
                      {**set_object, 'full_path': full['full_path']},
                      {**set_object, 'for_each': {'in': 'unresolved-object', 'item': 'entry'}}):
            self.assertTrue(list(validator.iter_errors(wrong)))


if __name__ == '__main__':
    unittest.main()
