"""Ordinary capability activation reuses the visitor and independent proof reader."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

from audit_v04_oval_test_corpus import OvalDocument, assessment_for, check_conversion
from v04_direct_converter import AssessmentConverter, load_mappings
from v04_expanded_source_proof import ExpandedSource, ExpandedNative
from v04_scalar_source_proof import CONTRACTS
from validate_native_json_schemas import build_validators

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tests/fixtures/v04-direct-scalars-expanded'
OVAL = '{http://oval.mitre.org/XMLSchema/oval-definitions-5}'
XS = '{http://www.w3.org/2001/XMLSchema}'


class ScalarExpansionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pin = json.loads((FIXTURE / 'provenance.json').read_text())
        cls.validator = build_validators(ROOT / 'schema/v0.4.0')['assessment.schema.json']
        cls.mappings = load_mappings()

    def originals(self):
        for item in self.pin['files']:
            raw = (FIXTURE / Path(item['path']).name).read_bytes()
            self.assertEqual(sha256(raw).hexdigest(), item['sha256'])
            yield item['path'], ET.fromstring(raw)

    def test_originals_validate_compile_and_prove_with_no_special_dispatch(self):
        proved = 0
        seen = set()
        for path, root in self.originals():
            for test in root.find(OVAL + 'tests'):
                with self.subTest(path=path, test=test.get('id')):
                    visitor = AssessmentConverter(OvalDocument(root, path), path, self.mappings)
                    seen.add(visitor.capability(test, 'test')['capability'])
                    result = check_conversion(visitor, test.get('id'), self.validator)
                    self.assertTrue(result['compiled'], result)
                    self.assertEqual(result['source_proof'], 'PROVED', result)
                    proved += 1
        self.assertEqual(proved, 46)
        self.assertEqual(seen, set(self.pin['capabilities']))

    def test_frozen_identities_cover_original_xsd_fields(self):
        # Inspect original declarations independently of the converter's map.
        # Deprecated fields absent from a reviewed map are not silently admitted.
        for capability in self.pin['capabilities']:
            record = CONTRACTS[capability]
            schema = ET.parse(ROOT / record['source']['definitions_schema']).getroot()
            for kind, names in (('object', record['selectors']), ('state', record['fields'])):
                declaration = schema.find(XS + 'element[@name="' + record['source'][kind] + '"]')
                fields = {e.get('name') for e in declaration.iter(XS + 'element') if e.get('name')}
                with self.subTest(capability=capability, kind=kind):
                    self.assertLessEqual(set(names), fields)
                    self.assertEqual(len(set(names.values())), len(names))

    def test_pinned_originals_pass_original_xsd_and_schematron_assertions(self):
        from lxml import etree
        from oval_source_validation import SourceValidator
        validator = SourceValidator(ROOT / 'third_party/scap-1.4-schemas/oval_5.12.3')
        for item in self.pin['files']:
            report = validator.validate(etree.parse(str(FIXTURE / Path(item['path']).name)).getroot())
            with self.subTest(path=item['path']):
                self.assertEqual(report['status'], 'VALID', report)

    def test_original_quantifier_mutants_do_not_prove(self):
        for path, root in self.originals():
            test = root.find(OVAL + 'tests')[0]
            assessment = assessment_for(AssessmentConverter(OvalDocument(root, path), path, self.mappings), test.get('id'))
            identifier = assessment['evaluate']['test']
            expected = ExpandedSource(root).test(test.get('id'))
            for key, value in (('items_found', 'none'), ('items_satisfying', 'none')):
                if key not in assessment['tests'][identifier]['require']:
                    continue
                wrong = deepcopy(assessment)
                wrong['tests'][identifier]['require'][key] = value
                with self.subTest(path=path, mutation=key):
                    self.assertNotEqual(expected, ExpandedNative(wrong).test(identifier))

    def test_foreign_and_unknown_source_fields_are_rejected_independently(self):
        for path, root in self.originals():
            state = root.find(OVAL + 'states')[0]
            reader = ExpandedSource(root)
            capability = reader.capability(state, '_state')
            for field in ('{urn:foreign}value', state.tag.rsplit('}', 1)[0] + '}invented_field'):
                wrong = deepcopy(root)
                changed = next(n for n in wrong.find(OVAL + 'states') if n.get('id') == state.get('id'))
                ET.SubElement(changed, field).text = 'invented'
                with self.subTest(path=path, field=field), self.assertRaises(ValueError):
                    ExpandedSource(wrong).state(state.get('id'), capability)

    def test_no_object_system_capabilities_reject_invented_collection(self):
        for path, root in self.originals():
            for obj in root.find(OVAL + 'objects'):
                reader = ExpandedSource(root)
                capability = reader.capability(obj, '_object')
                if CONTRACTS[capability]['source_kind'] != 'none':
                    continue
                wrong = deepcopy(root)
                changed = next(n for n in wrong.find(OVAL + 'objects') if n.get('id') == obj.get('id'))
                ET.SubElement(changed, changed.tag.rsplit('}', 1)[0] + '}name').text = 'invented'
                with self.subTest(path=path), self.assertRaises(ValueError):
                    ExpandedSource(wrong).object(obj.get('id'))


if __name__ == '__main__':
    unittest.main()
