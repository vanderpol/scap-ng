"""Ordinary mapping growth uses original files and closure-scoped source validity."""
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
from v04_scalar_source_proof import CONTRACTS
from validate_native_json_schemas import build_validators

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tests/fixtures/v04-direct-ordinary-continuation'
O = '{http://oval.mitre.org/XMLSchema/oval-definitions-5}'
XS = '{http://www.w3.org/2001/XMLSchema}'


class OrdinaryContinuationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pin = json.loads((FIXTURE / 'provenance.json').read_text())
        cls.mappings = load_mappings()
        cls.validator = build_validators(ROOT / 'schema/v0.4.0')['assessment.schema.json']

    def originals(self):
        for item in self.pin['files']:
            raw = (FIXTURE / Path(item['path']).name).read_bytes()
            self.assertEqual(sha256(raw).hexdigest(), item['sha256'])
            yield item, raw, ET.fromstring(raw)

    def test_all_original_cases_prove_or_keep_their_exact_blockers(self):
        total, proved = 0, 0
        for item, _, root in self.originals():
            accepted, blocked = 0, []
            for test in root.find(O + 'tests'):
                result = check_conversion(AssessmentConverter(OvalDocument(root, item['path']), item['path'], self.mappings), test.get('id'), self.validator)
                with self.subTest(path=item['path'], test=test.get('id')):
                    if result['compiled']:
                        self.assertEqual(result['source_proof'], 'PROVED', result)
                        accepted += 1
                    else:
                        self.assertTrue(result['diagnostics'])
                        blocked.append(test.get('id'))
                total += 1
            self.assertEqual(accepted, item['proved'])
            self.assertEqual(sorted(blocked), sorted(r['test'] for r in item['blocked_tests']))
            proved += accepted
        self.assertEqual((total, proved), (32, 28))

    def test_every_proved_original_closure_passes_original_xsd_and_schematron(self):
        validator = SourceValidator(ROOT / 'third_party/scap-1.4-schemas/oval_5.12.3')
        checked = 0
        for item, raw, root in self.originals():
            report = validator.validate(etree.fromstring(raw))
            self.assertEqual(report['status'], item['source_document_validity'])
            model = OvalDocument(root, item['path'])
            nodes = {i: n for (_, i), n in SourceInventory(model).nodes.items()}
            blocked = {r['test'] for r in item['blocked_tests']}
            for test in root.find(O + 'tests'):
                if test.get('id') in blocked:
                    continue
                ids, problems = closure(nodes, test.get('id'))
                self.assertFalse(problems)
                valid = closure_validity([nodes[i] for i in ids], {item['path']: report})
                with self.subTest(path=item['path'], test=test.get('id')):
                    self.assertEqual(valid['status'], 'VALID', valid)
                    self.assertFalse(any(i['kind'] == 'deprecated' for i in valid['issues']))
                checked += 1
        self.assertEqual(checked, 28)

    def test_reviewed_fields_and_behavior_defaults_match_original_declarations(self):
        for cap in self.pin['capabilities']:
            contract = CONTRACTS[cap]
            schema = ET.parse(ROOT / contract['source']['definitions_schema']).getroot()
            for kind, fields in (('object', contract['selectors']), ('state', contract['fields'])):
                declaration = schema.find(XS + 'element[@name="' + contract['source'][kind] + '"]')
                names = {n.get('name') for n in declaration.iter(XS + 'element') if n.get('name')}
                self.assertLessEqual(set(fields), names)
            if not contract.get('behaviors'):
                continue
            obj = schema.find(XS + 'element[@name="' + contract['source']['object'] + '"]')
            name = obj.find('.//' + XS + 'element[@name="behaviors"]').get('type').split(':')[-1]
            declaration = schema.find(XS + 'complexType[@name="' + name + '"]')
            for field, spec in contract['behaviors'].items():
                attribute = declaration.find(XS + 'attribute[@name="' + field + '"]')
                self.assertEqual(attribute.get('use'), 'optional')
                self.assertEqual(attribute.get('type').split(':')[-1], 'boolean')
                self.assertEqual(attribute.get('default'), 'true' if spec['default'] else 'false')

    def test_changed_native_quantifiers_or_collection_flags_do_not_prove(self):
        for item, _, root in self.originals():
            blocked = {r['test'] for r in item['blocked_tests']}
            test = next(t for t in root.find(O + 'tests') if t.get('id') not in blocked)
            assessment = assessment_for(AssessmentConverter(OvalDocument(root, item['path']), item['path'], self.mappings), test.get('id'))
            identifier = assessment['evaluate']['test']
            expected = ExpandedSource(root).test(test.get('id'))
            wrong = deepcopy(assessment)
            wrong['tests'][identifier]['require']['items_found'] = 'none'
            self.assertNotEqual(expected, ExpandedNative(wrong).test(identifier))
            capability = assessment['tests'][identifier]['capability']
            for behavior in CONTRACTS[capability].get('behaviors', {}).values():
                wrong = deepcopy(assessment)
                obj = wrong['tests'][identifier]['object']
                if isinstance(obj, str):
                    obj = wrong['shared_objects'][obj]
                field = behavior['field']
                obj[field] = not obj[field]
                with self.subTest(path=item['path'], behavior=field):
                    self.assertNotEqual(expected, ExpandedNative(wrong).test(identifier))


if __name__ == '__main__':
    unittest.main()
