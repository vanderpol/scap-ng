"""Original datatype suites preserve algorithms, lexical values and Variable graphs."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

from lxml import etree
from audit_v04_oval_test_corpus import OvalDocument, assessment_for, check_conversion, closure
from oval_source_validation import SourceValidator
from v04_direct_converter import AssessmentConverter, load_mappings
from v04_direct_inventory import SourceInventory
from v04_direct_authoring_examples import walk
from v04_expanded_source_proof import ExpandedSource, ExpandedNative
from validate_native_json_schemas import build_validators, document_errors

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tests/fixtures/v04-direct-special-datatypes'
O = '{http://oval.mitre.org/XMLSchema/oval-definitions-5}'
I = '{http://oval.mitre.org/XMLSchema/oval-definitions-5#independent}'


class SpecialDatatypeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pin = json.loads((FIXTURE / 'provenance.json').read_text())
        cls.validator = build_validators(ROOT / 'schema/v0.4.0')['assessment.schema.json']
        cls.mappings = load_mappings()

    def visitor(self, root):
        return AssessmentConverter(OvalDocument(root, 'original.xml'), 'original.xml', self.mappings)

    def originals(self):
        for item in self.pin['files']:
            raw = (FIXTURE / Path(item['path']).name).read_bytes()
            self.assertEqual(sha256(raw).hexdigest(), item['sha256'])
            yield item, raw, ET.fromstring(raw)

    def test_all_114_original_tests_validate_compile_and_independently_prove(self):
        source_validator = SourceValidator(ROOT / 'third_party/scap-1.4-schemas/oval_5.12.3')
        checked = 0
        for item, raw, root in self.originals():
            report = source_validator.validate(etree.fromstring(raw))
            self.assertEqual(report['status'], 'VALID', report)
            self.assertFalse(any(i['kind'] == 'deprecated' for i in report['issues']))
            before = ET.tostring(root)
            nodes = {i: n for (_, i), n in SourceInventory(OvalDocument(root, 'original.xml')).nodes.items()}
            for ident in item['test_ids']:
                visitor = self.visitor(root)
                result = check_conversion(visitor, ident, self.validator)
                with self.subTest(source=item['path'], test=ident):
                    self.assertTrue(result['schema_valid'], result)
                    self.assertTrue(result['compiled_operands_verified'], result)
                    self.assertEqual(result['source_proof'], 'PROVED', result)
                    dependencies, problems = closure(nodes, ident)
                    self.assertFalse(problems)
                    self.assertEqual(set(visitor.used), set(dependencies))
                    self.assertTrue(all(v['sha256'] == nodes[k]['sha256'] for k, v in visitor.used.items()))
                checked += 1
            self.assertEqual(ET.tostring(root), before)
            self.assertEqual((FIXTURE / Path(item['path']).name).read_bytes(), raw)
        self.assertEqual(checked, 114)

    def test_type_erasure_and_wrong_operator_fail_independent_comparison(self):
        for item, _, root in self.originals():
            if item['path'].endswith('oval_int_datatype.xml'):
                continue  # Typed-prefix erasure is checked on special types.
            ident = item['test_ids'][0]
            a = assessment_for(self.visitor(root), ident)
            native_id = a['evaluate']['test']
            expected = ExpandedSource(root).test(ident)
            for mutation in ('erase-type', 'wrong-operation', 'conflicting-type'):
                wrong = deepcopy(a)
                predicate = next(n for n in walk(wrong['tests'][native_id]['require'])
                                 if any(k.endswith('_equals') for k in n))
                key = next(k for k in predicate if k.endswith('_equals'))
                if mutation == 'erase-type':
                    predicate['equals'] = predicate.pop(key); predicate['datatype'] = 'string'
                    # This alternative still validates; schema acceptance alone
                    # cannot establish the original datatype's algorithm.
                    self.assertFalse(list(document_errors(self.validator, {'assessment': wrong})))
                    self.assertNotEqual(expected, ExpandedNative(wrong).test(native_id))
                elif mutation == 'wrong-operation':
                    predicate[key.removesuffix('_equals') + '_not_equal'] = predicate.pop(key)
                    self.assertNotEqual(expected, ExpandedNative(wrong).test(native_id))
                else:
                    predicate['datatype'] = 'string'
                    # The current schema can accept this conflicting annotation.
                    # Semantic proof must reject it independently of any later
                    # schema tightening; do not lock the permissive gap in here.
                    with self.assertRaisesRegex(ValueError, 'conflicting native comparison datatype'):
                        ExpandedNative(wrong).test(native_id)

    def test_typed_static_arrays_and_named_dependencies_retain_each_var_check(self):
        _, _, original = next(x for x in self.originals() if 'version_datatype' in x[0]['path'])
        for check, native_check in (('all', 'every'), ('at least one', 'one_or_more'),
                                    ('none satisfy', 'none'), ('only one', 'exactly_one')):
            for named in (False, True):
                root = deepcopy(original)
                variable = root.find(O + 'variables')[0]
                variable.append(deepcopy(variable[0]))  # Duplicate values remain two values.
                state = root.find(O + 'states')[0]
                entity = state.find(I + 'value')
                reference = variable.get('id')
                if named:
                    local = ET.SubElement(root.find(O + 'variables'), O + 'local_variable',
                        id='oval:org.scapng.datatype:var:1', version='1', datatype='version')
                    ET.SubElement(local, O + 'variable_component', var_ref=reference)
                    reference = local.get('id')
                entity.text = None; entity.set('var_ref', reference); entity.set('var_check', check)
                ident = root.find(O + 'tests')[0].get('id')
                result = check_conversion(self.visitor(root), ident, self.validator)
                self.assertEqual(result['source_proof'], 'PROVED', result)
                self.assertTrue(result['compiled_operands_verified'], result)
                a = assessment_for(self.visitor(root), ident)
                predicate = next(n for n in walk(a['tests'][a['evaluate']['test']]['require']) if 'version_equals' in n)
                self.assertEqual((predicate['datatype'], predicate['value_match']), ('version', native_check))
                self.assertEqual(predicate['values_matching'], 'every')
                self.assertIsInstance(predicate['version_equals'], dict if named else list)
                if not named:
                    self.assertEqual(len(predicate['version_equals']), 2)
                self.assertEqual(a, assessment_for(self.visitor(root), ident))

    def test_inapplicable_operations_casts_and_float_values_stay_unsupported(self):
        _, _, root = next(x for x in self.originals() if 'version_datatype' in x[0]['path'])
        for mutation in ('regex', 'cast', 'float'):
            original = deepcopy(root)
            entity = original.find(O + 'states')[0].find(I + 'value')
            if mutation == 'regex':
                entity.set('operation', 'pattern match'); expected = 'unsupported typed comparison'
            elif mutation == 'cast':
                entity.set('var_ref', original.find(O + 'variables')[0].get('id'))
                entity.set('datatype', 'string'); entity.text = None; expected = 'Variable cast'
            else:
                entity.set('datatype', 'float'); entity.text = 'NaN'; expected = 'unsupported scalar datatype'
            with self.subTest(mutation=mutation), self.assertRaisesRegex(ValueError, expected):
                assessment_for(self.visitor(original), original.find(O + 'tests')[0].get('id'))
