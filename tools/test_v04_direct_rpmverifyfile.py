"""Original nondeprecated RPM file verification and fail-closed legacy cases."""
from copy import deepcopy
from hashlib import sha1, sha256
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

from lxml import etree
from audit_v04_oval_test_corpus import OvalDocument, assessment_for, check_conversion, closure
from oval_source_validation import SourceValidator
from v04_converter_fixture_support import fixture_documents
from v04_direct_converter import AssessmentConverter, load_mappings
from v04_direct_inventory import SourceInventory
from v04_direct_scap_source import UnsupportedSource
from v04_expanded_source_proof import ExpandedSource, ExpandedNative
from v04_native_bundle_compiler import build_bundle, verify_bundle
from validate_native_json_schemas import build_validators, document_errors

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tests/fixtures/v04-direct-rpmverifyfile'
O = '{http://oval.mitre.org/XMLSchema/oval-definitions-5}'
L = '{http://oval.mitre.org/XMLSchema/oval-definitions-5#linux}'
TEST = 'oval:x:tst:1'
CAP = 'linux.rpmverifyfile'


class DirectRpmVerifyFileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pin = json.loads((FIXTURE / 'provenance.json').read_text())
        cls.raw = (FIXTURE / cls.pin['files'][0]['path']).read_bytes()
        cls.validator = build_validators(ROOT / 'schema/v0.4.0')['assessment.schema.json']
        cls.source_validator = SourceValidator(ROOT / 'third_party/scap-1.4-schemas/oval_5.12.3')

    def root(self):
        return ET.fromstring(self.raw)

    def visitor(self, root):
        return AssessmentConverter(OvalDocument(root, 'original.xml'), 'original.xml', load_mappings())

    def terms(self, root):
        visitor = self.visitor(root); a = assessment_for(visitor, TEST)
        self.assertFalse(list(document_errors(self.validator, {'assessment': a})))
        original = ExpandedSource(root).test(TEST)
        self.assertEqual(original, ExpandedNative(a).test(a['evaluate']['test']))
        raw, _ = build_bundle(fixture_documents(a))
        self.assertEqual(verify_bundle(raw)['programs'], 1)
        return a, original

    def test_original_valid_source_graph_compile_package_and_independent_terms(self):
        item, = self.pin['files']
        self.assertEqual(sha256(self.raw).hexdigest(), item['sha256'])
        self.assertEqual(sha1(b'blob ' + str(len(self.raw)).encode() + b'\0' + self.raw).hexdigest(), item['git_blob'])
        root = self.root(); before = ET.tostring(root)
        validity = self.source_validator.validate(etree.fromstring(self.raw))
        self.assertEqual(validity['status'], 'VALID', validity)
        self.assertFalse(validity['issues'])
        visitor = self.visitor(root); result = check_conversion(visitor, TEST, self.validator)
        expected, = json.loads((FIXTURE / 'conversion-evidence.json').read_text())['cases']
        self.assertEqual({'source': item['path'], 'test': TEST, **result}, expected)
        self.assertEqual(result['source_proof'], 'PROVED')
        nodes = {i: n for (_, i), n in SourceInventory(OvalDocument(root, 'original.xml')).nodes.items()}
        ids, problems = closure(nodes, TEST)
        self.assertFalse(problems); self.assertEqual(set(ids), set(visitor.used))
        self.terms(root)
        self.assertEqual(ET.tostring(root), before)

    def test_all_eleven_switches_are_materialized_and_native_mutations_are_detected(self):
        a, source = self.terms(self.root()); ident = a['evaluate']['test']
        fields = a['tests'][ident]['object']
        switches = [k for k in fields if k.startswith('skip_')]
        self.assertEqual(len(switches), 11)
        self.assertFalse(fields['skip_config_files'])
        self.assertTrue(all(type(fields[k]) is bool for k in switches))
        self.assertTrue(all(fields[k] for k in switches if k != 'skip_config_files'))
        self.assertEqual(fields['epoch'], {'matches_regex': ''})
        self.assertEqual(fields['filepath'], {'equals': '/usr/bin/true'})
        for switch in switches:
            changed = deepcopy(a); changed['tests'][ident]['object'][switch] = not fields[switch]
            self.assertFalse(list(document_errors(self.validator, {'assessment': changed})))
            self.assertNotEqual(ExpandedNative(changed).test(ident), source)

    def test_original_false_defaults_and_explicit_boolean_spellings_remain_distinct(self):
        for attributes in ({}, {'nosize': '0', 'nofiledigest': '1', 'noconfigfiles': 'true'}):
            root = self.root(); behavior = root.find(O + 'objects')[0][0]; behavior.attrib.clear(); behavior.attrib.update(attributes)
            validity = self.source_validator.validate(etree.fromstring(ET.tostring(root)))
            self.assertEqual(validity['status'], 'VALID', validity)
            a, _ = self.terms(root); fields = next(iter(a['tests'].values()))['object']
            self.assertFalse(fields['skip_size'])
            self.assertEqual(fields['skip_file_digest'], bool(attributes))
            self.assertEqual(fields['skip_config_files'], bool(attributes))

    def test_supported_digest_state_is_not_deprecated_md5_or_boolean_success(self):
        root = self.root(); states = ET.SubElement(root, O + 'states')
        state = ET.SubElement(states, L + 'rpmverifyfile_state', id='oval:rpm.derived:ste:1', version='1')
        entity = ET.SubElement(state, L + 'filedigest_differs'); entity.text = 'not performed'
        ET.SubElement(root.find(O + 'tests')[0], L + 'state', state_ref=state.get('id'))
        validity = self.source_validator.validate(etree.fromstring(ET.tostring(root)))
        self.assertEqual(validity['status'], 'VALID', validity); self.assertFalse(validity['issues'])
        a, original = self.terms(root); ident = a['evaluate']['test']
        predicate = a['tests'][ident]['require']['fields']['filedigest_differs']
        self.assertEqual(predicate['equals'], 'not performed')
        self.assertNotIn('datatype', predicate)  # Source default string, not Boolean.
        changed = deepcopy(a); changed['tests'][ident]['require']['fields']['filedigest_differs']['equals'] = 'pass'
        self.assertNotEqual(ExpandedNative(changed).test(ident), original)
        entity.tag = L + 'md5_differs'
        with self.assertRaises(UnsupportedSource): assessment_for(self.visitor(root), TEST)
        with self.assertRaises(ValueError): ExpandedSource(root).test(TEST)

    def test_deprecated_unknown_nonboolean_behaviors_and_foreign_selectors_fail_closed(self):
        for mutation in ('nomd5', 'unknown', 'nonboolean', 'foreign'):
            root = self.root(); obj = root.find(O + 'objects')[0]
            if mutation == 'nomd5': obj[0].set('nomd5', 'true')
            elif mutation == 'unknown': obj[0].set('skip_everything', 'true')
            elif mutation == 'nonboolean': obj[0].set('nosize', 'yes')
            else: ET.SubElement(obj, L + 'query').text = 'no'
            with self.subTest(mutation=mutation), self.assertRaises(UnsupportedSource):
                assessment_for(self.visitor(root), TEST)
            with self.assertRaises(ValueError): ExpandedSource(root).test(TEST)
