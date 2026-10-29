"""Source-pinned activation of the existing Solaris SMF identity contract (#251)."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from unittest import TestCase, main, mock
import xml.etree.ElementTree as ET
from lxml import etree

from audit_v04_oval_test_corpus import OvalDocument, assessment_for, check_conversion
from audit_v04_eight_assessment_pilot import verify_program
from inventory_v04_six_source_requirements import closure_validity
from oval_source_validation import SourceValidator
from v04_direct_converter import AssessmentConverter, CAPABILITIES, load_mappings
from v04_direct_inventory import SourceInventory
from v04_direct_scap_source import digest, xml_identity
from v04_expanded_source_proof import ExpandedSource, ExpandedNative
from v04_native_bundle_compiler import compile_assessment_program
from v04_scalar_source_proof import contract
from validate_native_json_schemas import build_validators

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT/'tests/fixtures/v04-solaris-smf'
CASES = json.loads((FIXTURE/'provenance.json').read_text())['cases']
O = '{http://oval.mitre.org/XMLSchema/oval-definitions-5}'
S = '{http://oval.mitre.org/XMLSchema/oval-definitions-5#solaris}'
TEST = 'oval:mil.disa.stig.solaris11:tst:5900'
OBJECT = 'oval:mil.disa.stig.solaris11:obj:5900'

class SolarisSmfTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = build_validators(ROOT/'schema/v0.4.0')['assessment.schema.json']
        cls.validator = SourceValidator(ROOT/'third_party/scap-1.4-schemas/oval_5.12.3')

    def original(self, index=0):
        case = CASES[index]
        raw = (FIXTURE/case['fixture']).read_bytes()
        self.assertEqual(sha256(raw).hexdigest(), case['sha256'])
        root = ET.fromstring(raw)
        nodes = {n.get('id'):n for n in root.iter() if n.get('id')}
        self.assertEqual(set(nodes), {d['id'] for d in case['dependencies']})
        for d in case['dependencies']:
            self.assertEqual(digest(xml_identity(nodes[d['id']])), d['sha256'])
        return root

    def visitor(self, root):
        return AssessmentConverter(OvalDocument(root, 'original.xml'), 'original.xml', load_mappings())

    def proved(self, root, test=TEST):
        before = ET.tostring(root)
        result = check_conversion(self.visitor(root), test, self.schema)
        self.assertTrue(result['schema_valid'], result)
        self.assertTrue(result['compiled_operands_verified'], result)
        self.assertEqual(result['source_proof'], 'PROVED', result)
        self.assertEqual(ET.tostring(root), before)
        return assessment_for(self.visitor(root), test)

    def node(self, root, identifier):
        return next(n for n in root.iter() if n.get('id') == identifier)

    def test_original_architecture_closures_valid_nondeprecated_and_all_smf_tests_prove(self):
        for i, case in enumerate(CASES):
            root = self.original(i)
            checked = self.validator.validate(etree.fromstring(ET.tostring(root)))
            nodes = list(SourceInventory(OvalDocument(root, 'original.xml')).nodes.values())
            validity = closure_validity(nodes, {'original.xml':checked})
            self.assertEqual(validity['status'], 'VALID', validity)
            self.assertFalse(any(x['kind'] == 'deprecated' for x in validity['issues']))
            for test in case['tests']:
                with self.subTest(architecture=case['fixture'], test=test):
                    self.proved(root, test)

    def test_frozen_crosswalk_matches_original_xsd_and_preserves_source_spelling(self):
        record = contract('solaris.smf')
        root = ET.parse(ROOT/record['source']['definitions_schema']).getroot()
        x = '{http://www.w3.org/2001/XMLSchema}'
        state = root.find(x+'element[@name="smf_state"]')
        obj = root.find(x+'element[@name="smf_object"]')
        self.assertEqual({n.get('name') for n in state.findall('.//'+x+'sequence/'+x+'element')}, set(record['fields']))
        self.assertIn('fmri', {n.get('name') for n in obj.findall('.//'+x+'element')})
        self.assertEqual(record['fields']['server_arguements'], 'server_arguements')
        with mock.patch('v04_direct_converter.CAPABILITIES', CAPABILITIES+('solaris.package',)):
            with self.assertRaisesRegex(ValueError, 'outside approved direct-converter scope'):
                load_mappings()

    def test_existing_stateful_count_and_match_axes_remain_independent(self):
        for found in ['at_least_one_exists', 'only_one_exists', 'any_exist']:
            for matching in ['all', 'at least one', 'only one', 'none satisfy']:
                root = self.original()
                test = self.node(root, TEST)
                test.set('check_existence', found)
                test.set('check', matching)
                self.proved(root)
        a = self.proved(self.original(), 'oval:mil.disa.stig.solaris11:tst:5400')
        self.assertEqual(next(iter(a['tests'].values()))['require'], {'items_found':'none'})

    def test_selector_state_and_count_mutants_reject_in_both_independent_consumers(self):
        root = self.original()
        a = self.proved(root)
        key = a['evaluate']['test']
        for change in ['selector', 'state', 'count']:
            mutant = deepcopy(a)
            test = mutant['tests'][key]
            if change == 'selector':test['object']['fmri']['equals'] = 'svc://localhost/another:default'
            elif change == 'state':test['require']['fields']['service_state']['equals'] = 'ONLINE'
            else:test['require']['items_satisfying'] = 'none'
            self.assertFalse(list(self.schema.iter_errors({'assessment':mutant})))
            self.assertNotEqual(ExpandedSource(root).test(TEST), ExpandedNative(mutant).test(key))
            with self.assertRaises((ValueError, AssertionError)):
                verify_program(mutant, compile_assessment_program(a))

    def test_unknown_fields_namespaces_attributes_and_nil_fail_closed(self):
        for change in ['field', 'namespace', 'attribute', 'nil']:
            root = self.original()
            entity = self.node(root, OBJECT).find(S+'fmri')
            if change == 'field':entity.tag = S+'invented'
            elif change == 'namespace':entity.tag = O+'fmri'
            elif change == 'attribute':entity.set('invented', 'true')
            else:entity.set('{http://www.w3.org/2001/XMLSchema-instance}nil', 'true')
            with self.subTest(change=change), self.assertRaises(ValueError):
                ExpandedSource(root).object(OBJECT)
            with self.assertRaises(ValueError):
                assessment_for(self.visitor(root), TEST)

    def test_all_exist_and_stateful_absence_stay_blocked(self):
        for found in ['all_exist', 'none_exist']:
            root = self.original()
            self.node(root, TEST).set('check_existence', found)
            if found == 'all_exist':
                with self.assertRaises(ValueError):ExpandedSource(root).test(TEST)
            with self.assertRaises(ValueError):assessment_for(self.visitor(root), TEST)

    def test_direct_filter_is_preserved_and_not_silently_dropped(self):
        root = self.original()
        obj = self.node(root, OBJECT)
        ET.SubElement(obj, O+'filter', action='exclude').text = 'oval:mil.disa.stig.solaris11:ste:1700'
        a = self.proved(root)
        key = a['evaluate']['test']
        for action in ['drop', 'invert']:
            mutant = deepcopy(a)
            obj = mutant['tests'][key]['object']
            if action == 'drop':obj.pop('filters')
            else:obj['filters'][0] = {'include':obj['filters'][0]['exclude']}
            self.assertNotEqual(ExpandedSource(root).test(TEST), ExpandedNative(mutant).test(key))
            with self.assertRaises((ValueError, AssertionError)):
                verify_program(mutant, compile_assessment_program(a))

if __name__ == '__main__':main()
