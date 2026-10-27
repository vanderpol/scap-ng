"""Schema-independent file acquisition uses original graphs and independent proof."""
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
from v04_direct_scalar_behaviors import original_attributes
from v04_expanded_source_proof import ExpandedSource, ExpandedNative
from v04_scalar_source_proof import CONTRACTS
from validate_native_json_schemas import build_validators

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tests/fixtures/v04-direct-interim-files'
O = '{http://oval.mitre.org/XMLSchema/oval-definitions-5}'


class InterimFileTests(unittest.TestCase):
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

    def visitor(self, root):
        return AssessmentConverter(OvalDocument(root, 'original.xml'), 'original.xml', self.mappings)

    def test_original_authoring_compilation_and_independent_terms(self):
        total = proved = 0
        for item, raw, root in self.originals():
            before = ET.tostring(root)
            actual = 0
            for ident in item['test_ids']:
                result = check_conversion(self.visitor(root), ident, self.validator)
                with self.subTest(file=item['path'], test=ident):
                    if ident in item['blocked']:
                        self.assertEqual(result['diagnostics'], item['blocked'][ident])
                        self.assertFalse(result['converted'])
                    else:
                        self.assertTrue(result['compiled'], result)
                        self.assertTrue(result['compiled_operands_verified'])
                        self.assertEqual(result['source_proof'], 'PROVED', result)
                        actual += 1
                total += 1
            self.assertEqual(actual, item['proved'])
            self.assertEqual(ET.tostring(root), before)
            self.assertEqual((FIXTURE / Path(item['path']).name).read_bytes(), raw)
            proved += actual
        self.assertEqual((total, proved), (35, 31))

    def test_original_validity_is_separate_from_diagnostic_conversion(self):
        validator = SourceValidator(ROOT / 'third_party/scap-1.4-schemas/oval_5.12.3')
        proved = 0
        for item, raw, root in self.originals():
            report = validator.validate(etree.fromstring(raw))
            self.assertEqual(report['status'], item['source_document_validity'])
            nodes = {i: n for (_, i), n in SourceInventory(OvalDocument(root, item['path'])).nodes.items()}
            for ident in item['test_ids']:
                ids, problems = closure(nodes, ident)
                self.assertFalse(problems)
                validity = closure_validity([nodes[i] for i in ids], {item['path']: report})
                expected = item['closure_validity'][ident]
                self.assertEqual(validity['status'], expected['status'], (ident, validity))
                self.assertEqual(any(i['kind'] == 'deprecated' for i in validity['issues']), expected['deprecated'])
                if validity['status'] == 'VALID' and not expected['deprecated'] and ident not in item['blocked']:
                    proved += 1
        self.assertEqual(proved, 30)

    def test_dependency_ids_and_shared_graphs_survive_repeat_conversion(self):
        for item, _, root in self.originals():
            nodes = {i: n for (_, i), n in SourceInventory(OvalDocument(root, item['path'])).nodes.items()}
            for ident in set(item['test_ids']) - item['blocked'].keys():
                first, second = self.visitor(root), self.visitor(root)
                a, b = assessment_for(first, ident), assessment_for(second, ident)
                self.assertEqual(a, b)
                self.assertEqual(first.used, second.used)
                ids, problems = closure(nodes, ident)
                self.assertFalse(problems)
                self.assertEqual(set(first.used), set(ids))
                self.assertTrue(all(v['sha256'] == nodes[k]['sha256'] for k, v in first.used.items()))

    def test_acquisition_status_controls_and_traversal_mutants_do_not_prove(self):
        for item, _, root in self.originals():
            ident = next(i for i in item['test_ids'] if i not in item['blocked'])
            a = assessment_for(self.visitor(root), ident)
            test_id = a['evaluate']['test']
            expected = ExpandedSource(root).test(ident)
            for field, value in (('filesystem', 'local'), ('traversal', {'max_depth': 0, 'recurse': 'directories'})):
                wrong = deepcopy(a)
                native = wrong['tests'][test_id]['object']
                if isinstance(native, str):
                    native = wrong['shared_objects'][native]
                if 'set' in native:
                    continue  # Original Set boundary is checked separately below.
                native[field] = value
                with self.subTest(file=item['path'], field=field):
                    self.assertNotEqual(expected, ExpandedNative(wrong).test(test_id))
            if 'xmlfilecontent' in item['path']:
                wrong = deepcopy(a)
                native = wrong['tests'][test_id]['object']
                native = wrong['shared_objects'][native] if isinstance(native, str) else native
                native['item_creation'] = 'filepath_exists' if native['item_creation'] == 'all_object_elements_fullfilled' else 'all_object_elements_fullfilled'
                self.assertNotEqual(expected, ExpandedNative(wrong).test(test_id))

    def test_xml_behavior_defaults_are_original_inherited_declarations(self):
        cap = CONTRACTS['independent.xmlfilecontent']
        attributes = original_attributes(cap['source']['definitions_schema'], cap['source']['object'])
        self.assertEqual(attributes['item_creation']['default'], 'all_object_elements_fullfilled')
        self.assertEqual(attributes['recurse_direction']['default'], 'none')
        self.assertEqual(attributes['max_depth']['default'], '-1')
        self.assertEqual(attributes['recurse_file_system']['default'], 'all')

    def test_original_windows_set_operators_and_filters_are_not_interchangeable(self):
        root = ET.parse(FIXTURE / 'oval-def_set-windows.xml').getroot()
        item = next(i for i in self.pin['files'] if i['path'].endswith('oval-def_set-windows.xml'))
        seen = set()
        for ident in item['test_ids']:
            a = assessment_for(self.visitor(root), ident)
            test_id = a['evaluate']['test']
            expected = ExpandedSource(root).test(ident)
            def objects(value):
                if isinstance(value, dict):
                    yield value
                    for child in value.values():
                        yield from objects(child)
                elif isinstance(value, list):
                    for child in value:
                        yield from objects(child)
            wrong = deepcopy(a)
            for node in objects(wrong):
                if 'operator' in node and len(node.get('operands', [])) > 1:
                    seen.add(node['operator'])
                    node['operator'] = 'intersection' if node['operator'] == 'union' else 'union'
                    self.assertNotEqual(expected, ExpandedNative(wrong).test(test_id))
                    break
            wrong = deepcopy(a)
            for node in objects(wrong):
                if node.get('filters'):
                    original = node['filters'][0]
                    action, predicate = next(iter(original.items()))
                    node['filters'][0] = {'include' if action == 'exclude' else 'exclude': predicate}
                    self.assertNotEqual(expected, ExpandedNative(wrong).test(test_id))
                    break
        self.assertEqual(seen, {'union', 'intersection', 'difference'})

    def test_unknown_deprecated_mixed_or_contentful_behaviors_fail_closed(self):
        for attr, value in (('windows_view', '32_bit'), ('recurse_direction', 'up'), ('mystery', 'true'),
                            ('item_creation', 'unknown')):
            root = ET.parse(FIXTURE / 'ind-def_xmlfilecontent_test_unix.xml').getroot()
            test = root.find(O + 'tests')[0]
            reference = test[0].get('object_ref')
            obj = next(o for o in root.find(O + 'objects') if o.get('id') == reference)
            ns = obj.tag.rsplit('}', 1)[0] + '}'
            behavior = obj.find(ns + 'behaviors')
            if behavior is None:
                behavior = ET.Element(ns + 'behaviors')
                obj.insert(0, behavior)
            behavior.set(attr, value)
            with self.subTest(attribute=attr), self.assertRaises(ValueError):
                assessment_for(self.visitor(root), test.get('id'))


if __name__ == '__main__':
    unittest.main()
