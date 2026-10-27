"""Original file selectors, recursion, permission fields, Sets and Filters."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

from audit_v04_oval_test_corpus import OvalDocument, assessment_for, check_conversion
from v04_direct_converter import AssessmentConverter, load_mappings
from v04_expanded_source_proof import ExpandedSource, ExpandedNative
from v04_direct_file_behaviors import traversal_behaviors
from validate_native_json_schemas import build_validators

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tests/fixtures/v04-direct-file-traversal'
O = '{http://oval.mitre.org/XMLSchema/oval-definitions-5}'
U = '{http://oval.mitre.org/XMLSchema/oval-definitions-5#unix}'
X = '{http://www.w3.org/2001/XMLSchema}'


class DirectFileTraversalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pin = json.loads((FIXTURE / 'provenance.json').read_text())
        cls.mappings = load_mappings()
        cls.validator = build_validators(ROOT / 'schema/v0.4.0')['assessment.schema.json']

    def original(self, name='unix-def_file_test.xml'):
        raw = (FIXTURE / name).read_bytes()
        item = next(p for p in self.pin['files'] if Path(p['path']).name == name)
        self.assertEqual(sha256(raw).hexdigest(), item['sha256'])
        return ET.fromstring(raw)

    def convert(self, root, identifier):
        return assessment_for(AssessmentConverter(OvalDocument(root, 'original.xml'), 'original.xml', self.mappings), identifier)

    def test_original_file_and_set_cases_compile_and_prove_with_explicit_all_exist_blocks(self):
        for item in self.pin['files']:
            root = self.original(Path(item['path']).name)
            proved = 0
            for test in root.find(O + 'tests'):
                result = check_conversion(AssessmentConverter(OvalDocument(root, 'original.xml'), 'original.xml', self.mappings), test.get('id'), self.validator)
                with self.subTest(path=item['path'], test=test.get('id')):
                    if test.get('check_existence') == 'all_exist':
                        self.assertFalse(result['converted'], result)
                    else:
                        self.assertTrue(result['compiled'], result)
                        self.assertEqual(result['source_proof'], 'PROVED', result)
                        proved += 1
            self.assertEqual(proved, item['proved'])

    def test_original_xsd_defaults_and_deprecated_direction_remain_distinct(self):
        root = ET.parse(ROOT / 'third_party/scap-1.4-schemas/oval_5.12.3/unix-definitions-schema.xsd').getroot()
        declaration = root.find(X + 'complexType[@name="FileBehaviors"]')
        defaults = {a.get('name'): a.get('default') for a in declaration.findall(X + 'attribute')}
        self.assertEqual(defaults, {'max_depth': '-1', 'recurse': 'symlinks and directories',
                                   'recurse_direction': 'none', 'recurse_file_system': 'all'})
        self.assertEqual(traversal_behaviors(None, {'full_path': {'equals': '/etc/passwd'}}), {'filesystem': 'all'})
        element = ET.Element(U + 'behaviors', recurse_direction='down', recurse_file_system='defined')
        self.assertEqual(traversal_behaviors(element, {'directory': {'equals': '/etc'}, 'name': None}),
                         {'filesystem': 'same', 'traversal': {'max_depth': None, 'recurse': 'symlinks_and_directories'}})
        # Original XSD says depth/direction do not apply to filepath or to a
        # non-equality path. Ignored source attributes remain in provenance.
        for selectors in ({'full_path': {'equals': '/etc/passwd'}}, {'directory': {'matches_regex': '^/etc/'}, 'name': None}):
            self.assertNotIn('traversal', traversal_behaviors(element, selectors))

    def test_native_selector_permission_and_recursion_mutants_do_not_prove(self):
        root = self.original()
        test = root.find(O + 'tests')[0]
        assessment = self.convert(root, test.get('id'))
        identifier = assessment['evaluate']['test']
        expected = ExpandedSource(root).test(test.get('id'))
        native = assessment['tests'][identifier]
        self.assertIsNone(native['object']['name'])
        for field, value in (('name', {'equals': ''}), ('filesystem', 'local'),
                             ('traversal', {'max_depth': 1, 'recurse': 'directories'})):
            wrong = deepcopy(assessment)
            wrong['tests'][identifier]['object'][field] = value
            with self.subTest(field=field):
                self.assertNotEqual(expected, ExpandedNative(wrong).test(identifier))

    def test_invalid_or_deprecated_behavior_is_never_silently_dropped(self):
        for attributes in ({'recurse_direction': 'up'}, {'max_depth': '-2'}, {'max_depth': 'not-an-int'},
                           {'recurse': 'files'}, {'windows_view': '32_bit'}, {'invented': 'value'}):
            root = self.original()
            test = root.find(O + 'tests')[0]
            obj = root.find(O + 'objects')[0]
            existing = obj.find(U + 'behaviors')
            if existing is not None:
                obj.remove(existing)
            obj.insert(0, ET.Element(U + 'behaviors', **attributes))
            with self.subTest(attributes=attributes), self.assertRaises(ValueError):
                self.convert(root, test.get('id'))
            with self.assertRaises(ValueError):
                ExpandedSource(root).object(obj.get('id'))

    def test_object_component_projection_uses_the_same_reviewed_field_identity(self):
        root = self.original()
        test = root.find(O + 'tests')[0]
        original = root.find(O + 'objects')[0]
        variable_id = 'oval:controlled:var:1'
        variable = ET.SubElement(root.find(O + 'variables'), O + 'local_variable',
                                 id=variable_id, version='1', datatype='string', comment='Source directory values')
        ET.SubElement(variable, O + 'object_component', object_ref=original.get('id'), item_field='path')
        obj = ET.SubElement(root.find(O + 'objects'), U + 'file_object',
                            id='oval:controlled:obj:1', version='1', comment='Files from source directory values')
        ET.SubElement(obj, U + 'filepath', var_ref=variable_id, var_check='at least one')
        test.find(U + 'object').set('object_ref', obj.get('id'))
        assessment = self.convert(root, test.get('id'))
        identifier = assessment['evaluate']['test']
        expected = ExpandedSource(root).test(test.get('id'))
        self.assertEqual(expected, ExpandedNative(assessment).test(identifier))
        expression = next(v['expression']['values'] for v in assessment['variables'].values())
        self.assertEqual(expression['field'], 'directory')
        expression['field'] = 'full_path'
        self.assertNotEqual(expected, ExpandedNative(assessment).test(identifier))


if __name__ == '__main__':
    unittest.main()
