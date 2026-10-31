"""Original Object-level text traversal; Test all_exist remains unsupported."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

from lxml import etree
from audit_v04_oval_test_corpus import OvalDocument
from inventory_v04_six_source_requirements import closure_validity
from oval_source_validation import SourceValidator
from v04_converter_fixture_support import fixture_documents
from v04_direct_converter import AssessmentConverter, load_mappings
from v04_direct_scap_source import UnsupportedSource
from v04_expanded_source_proof import ExpandedSource, ExpandedNative
from v04_native_bundle_compiler import build_bundle, verify_bundle
from validate_native_json_schemas import build_validators, document_errors

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tests/fixtures/v04-direct-textfile-traversal'
O = '{http://oval.mitre.org/XMLSchema/oval-definitions-5}'
I = '{http://oval.mitre.org/XMLSchema/oval-definitions-5#independent}'
CAP = 'independent.textfilecontent'


class DirectTextTraversalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pin = json.loads((FIXTURE / 'provenance.json').read_text())
        cls.raw = (FIXTURE / Path(cls.pin['path']).name).read_bytes()
        cls.validators = build_validators(ROOT / 'schema/v0.4.0')
        cls.source_validator = SourceValidator(ROOT / 'third_party/scap-1.4-schemas/oval_5.12.3')

    def root(self):
        return ET.fromstring(self.raw)

    def object(self, root, identifier=None):
        identifier = identifier or self.pin['object_ids'][0]
        return next(n for n in root.find(O + 'objects') if n.get('id') == identifier)

    def terms(self, root, identifier=None):
        identifier = identifier or self.pin['object_ids'][0]
        visitor = AssessmentConverter(OvalDocument(root, 'original.xml'), 'original.xml', load_mappings())
        acquisition = visitor.reference(identifier, 'object')
        # A constructed native compiler wrapper; this explicitly does NOT
        # convert or prove any original all_exist Test from this document.
        a = {'id': 'constructed-object-compiler-wrapper', 'version': 1,
            'assessment_title': 'Original Object only; constructed Test is not original Test conversion',
            'mode': 'automated', 'class': 'compliance',
            'specification': {'id': 'scap-ng.pre-alpha.assessment', 'version': '0.4.0'},
            'tests': {'constructed-object-test': {'capability': CAP, 'object': deepcopy(acquisition),
                'test_title': 'Constructed compiler wrapper for original Object only',
                'require': {'items_found': 'one_or_more'}, 'reported_elements': 'all'}},
            'evaluate': {'test': 'constructed-object-test'}}
        if isinstance(a['tests']['constructed-object-test']['object'], dict):
            a['tests']['constructed-object-test']['object'].pop('capability')
        for section in ('shared_objects', 'variables'):
            if getattr(visitor, section): a[section] = getattr(visitor, section)
        self.assertFalse(list(document_errors(self.validators['assessment.schema.json'], {'assessment': a})))
        original = ExpandedSource(root).object(identifier)
        native = ExpandedNative(a).object(acquisition, CAP)
        self.assertEqual(original, native)
        compiled, _ = build_bundle(fixture_documents(a))
        self.assertEqual(verify_bundle(compiled)['programs'], 1)
        report = self.source_validator.validate(etree.fromstring(ET.tostring(root)))
        validity = closure_validity([{'component': 'original.xml', 'id': i} for i in visitor.used],
                                    {'original.xml': report})
        self.assertEqual(validity['status'], 'VALID', validity)
        self.assertFalse(validity['issues'])
        return a, acquisition, original

    def test_two_byte_pinned_original_objects_validate_compile_and_match_independent_terms(self):
        self.assertEqual(sha256(self.raw).hexdigest(), self.pin['sha256'])
        root = self.root(); before = ET.tostring(root)
        for identifier, depth in zip(self.pin['object_ids'], (1, 'unlimited')):
            _, obj, _ = self.terms(root, identifier)
            self.assertEqual(obj['traversal'], {'max_depth': depth, 'recurse': 'symlinks_and_directories'})
            self.assertEqual((obj['ignore_case'], obj['multiline'], obj['singleline']), (False, True, False))
        self.assertEqual(ET.tostring(root), before)
        self.assertEqual((FIXTURE / Path(self.pin['path']).name).read_bytes(), self.raw)

    def test_regex_flags_item_creation_scope_and_traversal_compose_without_shared_attributes(self):
        root = self.root(); b = self.object(root)[0]
        b.attrib.update(max_depth='2', recurse='directories', recurse_file_system='defined',
                        ignore_case='true', multiline='false', singleline='true', item_creation='filepath_exists')
        _, obj, _ = self.terms(root)
        self.assertEqual(obj['filesystem'], 'same')
        self.assertEqual(obj['traversal'], {'max_depth': 2, 'recurse': 'directories'})
        self.assertEqual((obj['ignore_case'], obj['multiline'], obj['singleline']), (True, False, True))
        self.assertEqual(obj['item_creation'], 'filepath_exists')

    def test_native_depth_recursion_and_regex_mutations_are_detected(self):
        a, obj, source = self.terms(self.root())
        for mutation in ('depth', 'recursion', 'scope', 'regex'):
            changed = deepcopy(obj)
            if mutation == 'depth': changed['traversal']['max_depth'] = 0
            elif mutation == 'recursion': changed['traversal']['recurse'] = 'directories'
            elif mutation == 'scope': changed['filesystem'] = 'local'
            else: changed['ignore_case'] = True
            self.assertNotEqual(ExpandedNative(a).object(changed, CAP), source)
        for field in ('ignore_case', 'multiline', 'singleline', 'depth'):
            changed = deepcopy(obj)
            if field == 'depth': changed['traversal']['max_depth'] = True
            else: changed[field] = int(changed[field])
            with self.assertRaises(ValueError): ExpandedNative(a).object(changed, CAP)
        for invalid in (None, [], 1):
            changed = deepcopy(obj); changed['traversal'] = invalid
            with self.assertRaises(ValueError): ExpandedNative(a).object(changed, CAP)

    def test_original_deprecated_upward_and_invalid_path_controls_fail_closed(self):
        for mutation in ('up', 'pattern-path', 'filepath', 'view', 'depth', 'unknown'):
            root = self.root(); obj = self.object(root); b = obj[0]
            if mutation == 'up': b.set('recurse_direction', 'up')
            elif mutation == 'pattern-path': obj.find(I + 'path').set('operation', 'pattern match')
            elif mutation == 'filepath':
                obj.find(I + 'path').tag = I + 'filepath'; obj.remove(obj.find(I + 'filename'))
            elif mutation == 'view': b.set('windows_view', '32_bit')
            elif mutation == 'depth': b.set('max_depth', '-2')
            else: b.set('unknown', 'true')
            visitor = AssessmentConverter(OvalDocument(root, 'original.xml'), 'original.xml', load_mappings())
            with self.subTest(mutation=mutation), self.assertRaises(UnsupportedSource):
                visitor.reference(obj.get('id'), 'object')
            with self.assertRaises(ValueError): ExpandedSource(root).object(obj.get('id'))

    def test_sets_and_ordered_filters_keep_traversal_on_each_leaf(self):
        root = self.root(); states = root.find(O + 'states')
        state = ET.SubElement(states, I + 'textfilecontent54_state', id='oval:text.derived:ste:1', version='1')
        ET.SubElement(state, I + 'text').text = 'OVAL Interpreter'
        obj = ET.SubElement(root.find(O + 'objects'), I + 'textfilecontent54_object',
                            id='oval:text.derived:obj:1', version='1')
        set_node = ET.SubElement(obj, O + 'set', set_operator='COMPLEMENT')
        for ident in self.pin['object_ids']: ET.SubElement(set_node, O + 'object_reference').text = ident
        for action in ('include', 'exclude'):
            ET.SubElement(set_node, O + 'filter', action=action).text = state.get('id')
        a, native, original = self.terms(root, obj.get('id'))
        for operand in native['set']['operands']:
            self.assertIn('traversal', operand['object'])
        changed = deepcopy(native); changed['set']['operands'][0]['filters'].reverse()
        self.assertNotEqual(ExpandedNative(a).object(changed, CAP), original)

    def test_original_all_exist_tests_still_need_population_contract(self):
        root = self.root()
        visitor = AssessmentConverter(OvalDocument(root, 'original.xml'), 'original.xml', load_mappings())
        with self.assertRaisesRegex(UnsupportedSource, 'unsupported Test existence: all_exist'):
            visitor.reference('oval:org.mitre.oval.test:tst:688', 'test')
