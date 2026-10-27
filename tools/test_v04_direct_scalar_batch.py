"""A metadata-backed capability batch with independent original-source terms."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

from audit_v04_oval_test_corpus import OvalDocument, check_conversion, assessment_for
from v04_direct_converter import AssessmentConverter, load_mappings
from v04_expanded_source_proof import ExpandedSource, ExpandedNative
from v04_scalar_source_proof import CONTRACTS, contract
from validate_native_json_schemas import build_validators

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tests/fixtures/v04-direct-scalars'
O = '{http://oval.mitre.org/XMLSchema/oval-definitions-5}'


class ScalarBatchProofTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validators = build_validators(ROOT / 'schema/v0.4.0')
        cls.mappings = load_mappings()

    def originals(self):
        pin = json.loads((FIXTURE / 'provenance.json').read_text())
        for item in pin['files']:
            raw = (FIXTURE / Path(item['path']).name).read_bytes()
            self.assertEqual(sha256(raw).hexdigest(), item['sha256'])
            yield item['path'], ET.fromstring(raw)

    def test_batch_source_terms_schema_and_compiled_operands(self):
        proved, blocked = 0, []
        for path, root in self.originals():
            model = OvalDocument(root, path)
            for test in root.find(O + 'tests'):
                result = check_conversion(AssessmentConverter(model, path, self.mappings),
                                          test.get('id'), self.validators['assessment.schema.json'])
                if test.get('check_existence') == 'all_exist':
                    self.assertFalse(result['compiled'])
                    blocked.append(test.get('id'))
                    continue
                with self.subTest(path=path, test=test.get('id')):
                    self.assertTrue(result['compiled'], result)
                    self.assertEqual(result['source_proof'], 'PROVED', result)
                    proved += 1
        # The four pinned files contain 19 Tests. Five additional sysctl
        # cases in the complete corpus are retained in its macOS directory.
        self.assertEqual((proved, len(blocked)), (18, 1))

    def test_no_object_family_source_stays_object_free_and_regex_is_retained(self):
        path, root = next((p, r) for p, r in self.originals() if 'family' in p)
        test = root.find(O + 'tests')[0]
        visitor = AssessmentConverter(OvalDocument(root, path), path, self.mappings)
        assessment = assessment_for(visitor, test.get('id'))
        native = next(iter(assessment['tests'].values()))
        self.assertNotIn('object', native)
        self.assertIn('matches_regex', json.dumps(native['require']))
        expected = ExpandedSource(root).test(test.get('id'))
        actual = ExpandedNative(assessment).test(assessment['evaluate']['test'])
        self.assertEqual(expected, actual)

    def test_changed_selector_and_condition_fail_source_term_comparison(self):
        path, root = next((p, r) for p, r in self.originals() if 'sysctl' in p)
        test = root.find(O + 'tests')[0]
        assessment = assessment_for(AssessmentConverter(OvalDocument(root, path), path, self.mappings), test.get('id'))
        wrong = deepcopy(assessment)
        native_id = wrong['evaluate']['test']
        wrong['tests'][native_id]['object']['name'] = {'equals': 'controlled.wrong.name'}
        self.assertNotEqual(ExpandedSource(root).test(test.get('id')), ExpandedNative(wrong).test(native_id))

    def test_changed_mapping_cannot_redefine_the_independent_proof_contract(self):
        changed = deepcopy(CONTRACTS)
        changed['unix.sysctl']['mapping_sha256'] = '0' * 64
        contract.cache_clear()
        try:
            with patch('v04_scalar_source_proof.CONTRACTS', changed), self.assertRaisesRegex(ValueError, 'unreviewed scalar proof mapping'):
                contract('unix.sysctl')
        finally:
            contract.cache_clear()

    def test_foreign_acquisition_fields_and_system_selectors_fail_closed(self):
        for path, root in self.originals():
            source = ExpandedSource(root)
            for node in root.find(O + 'objects'):
                if node.find(O + 'set') is not None:
                    continue
                wrong = deepcopy(root)
                target = next(n for n in wrong.find(O + 'objects') if n.get('id') == node.get('id'))
                ET.SubElement(target, '{urn:unapproved}invented_selector').text = 'wrong'
                with self.subTest(path=path, object=node.get('id')), self.assertRaises(ValueError):
                    ExpandedSource(wrong).object(node.get('id'))

    def test_original_condition_mutations_are_not_proved(self):
        for path, root in self.originals():
            test = next(t for t in root.find(O + 'tests') if t.get('check_existence') != 'all_exist')
            assessment = assessment_for(AssessmentConverter(OvalDocument(root, path), path, self.mappings), test.get('id'))
            native_id = assessment['evaluate']['test']
            expected = ExpandedSource(root).test(test.get('id'))
            assessment['tests'][native_id]['require']['items_found'] = 'none'
            with self.subTest(path=path):
                self.assertNotEqual(expected, ExpandedNative(assessment).test(native_id))


if __name__ == '__main__':
    unittest.main()
