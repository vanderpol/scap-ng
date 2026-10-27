"""Shared Variable graphs preserve collection, declaration and aggregation boundaries."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

from audit_v04_oval_test_corpus import OvalDocument, assessment_for, check_conversion, closure
from v04_direct_converter import AssessmentConverter, load_mappings
from v04_direct_inventory import SourceInventory
from v04_expanded_source_proof import ExpandedSource, ExpandedNative
from validate_native_json_schemas import build_validators

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tests/fixtures/v04-direct-variables'
O = '{http://oval.mitre.org/XMLSchema/oval-definitions-5}'
I = '{http://oval.mitre.org/XMLSchema/oval-definitions-5#independent}'


class DirectVariableTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validator = build_validators(ROOT / 'schema/v0.4.0')['assessment.schema.json']
        cls.mappings = load_mappings()
        cls.pin = json.loads((FIXTURE / 'provenance.json').read_text())

    def original(self, name):
        raw = (FIXTURE / name).read_bytes()
        pin = next(p for p in self.pin['files'] if Path(p['path']).name == name)
        self.assertEqual(sha256(raw).hexdigest(), pin['sha256'])
        return ET.fromstring(raw)

    def convert(self, root, identifier):
        return assessment_for(AssessmentConverter(OvalDocument(root, 'original.xml'), 'original.xml', self.mappings), identifier)

    def test_pinned_original_graphs_compile_and_prove_or_retain_exact_blockers(self):
        proved = 0
        for item in self.pin['files']:
            root = self.original(Path(item['path']).name)
            actual = 0
            for test in root.find(O + 'tests'):
                visitor = AssessmentConverter(OvalDocument(root, item['path']), item['path'], self.mappings)
                result = check_conversion(visitor, test.get('id'), self.validator)
                with self.subTest(path=item['path'], test=test.get('id')):
                    if result['compiled']:
                        self.assertEqual(result['source_proof'], 'PROVED', result)
                        actual += 1
                    else:
                        self.assertTrue(result['diagnostics'], result)
                        self.assertEqual(result['source_proof'], 'NOT_RUN', result)
            self.assertEqual(actual, item['proved'], item['path'])
            proved += actual
        self.assertEqual(proved, 21)

    def test_text_variable_reference_is_a_real_dependency_and_cycles_fail(self):
        root = self.original('oval-def_constant_variable.xml')
        test = root.find(O + 'tests')[0]
        obj = root.find(O + 'objects')[0]
        source_id = obj[0].text.strip()
        model = OvalDocument(root, 'original.xml')
        nodes = {i: n for (_, i), n in SourceInventory(model).nodes.items()}
        dependencies, problems = closure(nodes, test.get('id'))
        self.assertFalse(problems)
        self.assertIn(source_id, dependencies)
        # Independent source closure follows the same reference from XML itself.
        self.assertIn(source_id, {n['id'] for n in ExpandedSource(root).closure(test.get('id'))['nodes']})
        obj[0].text = 'oval:missing:var:1'
        with self.assertRaisesRegex(ValueError, 'unresolved variable'):
            self.convert(root, test.get('id'))
        obj[0].text = test.get('id')
        with self.assertRaisesRegex(ValueError, 'wrong reference kind'):
            self.convert(root, test.get('id'))
        obj[0].text = source_id
        variable = next(v for v in root.find(O + 'variables') if v.get('id') == source_id)
        variable.tag = O + 'local_variable'
        variable[:] = []
        ET.SubElement(variable, O + 'object_component', object_ref=obj.get('id'), item_field='value')
        with self.assertRaisesRegex(ValueError, 'cyclic'):
            self.convert(root, test.get('id'))
        with self.assertRaisesRegex(ValueError, 'cyclic'):
            ExpandedSource(root).closure(test.get('id'))

    def test_aggregation_defaults_order_and_operands_remain_explicit(self):
        root = self.original('oval-def_merge.xml')
        test = root.find(O + 'tests')[0]
        assessment = self.convert(root, test.get('id'))
        merge = next(v['expression']['merge'] for v in assessment['variables'].values() if 'merge' in v['expression'])
        self.assertEqual((merge['delimiter'], merge['sort'], merge['order']), (':', 'natural', 'ascending'))
        self.assertIn('variable', merge['values'])
        expected = ExpandedSource(root).test(test.get('id'))
        native_id = assessment['evaluate']['test']
        for key, value in (('delimiter', ','), ('sort', 'document'), ('order', 'descending')):
            wrong = deepcopy(assessment)
            expression = next(v['expression']['merge'] for v in wrong['variables'].values() if 'merge' in v['expression'])
            expression[key] = value
            with self.subTest(key=key):
                self.assertNotEqual(expected, ExpandedNative(wrong).test(native_id))

    def test_unique_keeps_one_collection_and_does_not_evaluate_or_deduplicate_constants(self):
        root = self.original('oval-def_merge.xml')
        test = root.find(O + 'tests')[0]
        merge = root.find(O + 'variables')[0][0]
        merge.tag = O + 'unique'
        merge.attrib.clear()
        constant = next(v for v in root.find(O + 'variables') if v.tag == O + 'constant_variable')
        constant.append(deepcopy(constant[0]))
        assessment = self.convert(root, test.get('id'))
        identifier = assessment['evaluate']['test']
        self.assertEqual(ExpandedSource(root).test(test.get('id')), ExpandedNative(assessment).test(identifier))
        values = next(v['expression']['literal'] for v in assessment['variables'].values() if v['kind'] == 'constant')
        self.assertEqual(values, [1, 4, 5, 2, 3, 1])
        self.assertIn('unique', json.dumps(assessment))

    def test_unsupported_identity_filters_aggregation_arity_and_casts_fail_closed(self):
        for mutation in ('identity', 'filter', 'arity', 'sort', 'namespace', 'cast', 'invalid literal'):
            root = self.original('oval-def_merge.xml')
            test = root.find(O + 'tests')[0]
            if mutation == 'identity':
                ET.SubElement(root.find(O + 'states')[0], I + 'var_ref').text = 'oval:another:var:1'
            elif mutation == 'filter':
                ET.SubElement(root.find(O + 'objects')[0], O + 'filter').text = root.find(O + 'states')[0].get('id')
            elif mutation == 'arity':
                merge = root.find(O + 'variables')[0][0]
                merge.append(deepcopy(merge[0]))
            elif mutation == 'sort':
                root.find(O + 'variables')[0][0].set('sort', 'invented')
            elif mutation == 'namespace':
                root.find(O + 'objects')[0][0].tag = '{urn:foreign}var_ref'
            elif mutation == 'cast':
                value = root.find(O + 'states')[0][0]
                value.set('var_ref', next(v.get('id') for v in root.find(O + 'variables') if v.tag == O + 'constant_variable'))
                value.text = None
            else:
                next(v for v in root.find(O + 'variables') if v.tag == O + 'constant_variable')[0].text = 'not an integer'
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                self.convert(root, test.get('id'))

    def test_named_constant_mutation_is_not_a_proof(self):
        root = self.original('oval-def_constant_variable.xml')
        test = root.find(O + 'tests')[0]
        assessment = self.convert(root, test.get('id'))
        expected = ExpandedSource(root).test(test.get('id'))
        named = next(iter(assessment['variables'].values()))
        values = named['expression']['literal']
        self.assertTrue(values)
        value = values[0]
        values[0] = not value if isinstance(value, bool) else value + 1 if isinstance(value, int) else value + 'changed'
        self.assertNotEqual(expected, ExpandedNative(assessment).test(assessment['evaluate']['test']))


if __name__ == '__main__':
    unittest.main()
