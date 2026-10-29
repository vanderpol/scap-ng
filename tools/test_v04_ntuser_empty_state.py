"""Original NTUSER empty-State operands retain filters and quantifiers (#251)."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET
from lxml import etree

from audit_v04_oval_test_corpus import OvalDocument, assessment_for, check_conversion
from inventory_v04_six_source_requirements import closure_validity
from oval_source_validation import SourceValidator
from v04_direct_converter import AssessmentConverter, load_mappings
from v04_direct_inventory import SourceInventory
from v04_direct_scap_source import digest, xml_identity
from v04_expanded_source_proof import ExpandedSource, expanded_compare
from validate_native_json_schemas import build_validators

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tests/fixtures/v04-ntuser-empty-state'
CASES = json.loads((FIXTURE / 'provenance.json').read_text())['cases']
O = '{http://oval.mitre.org/XMLSchema/oval-definitions-5}'
W = '{http://oval.mitre.org/XMLSchema/oval-definitions-5#windows}'


def walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


class NTUSEREmptyStateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validator = build_validators(ROOT / 'schema/v0.4.0')['assessment.schema.json']
        cls.source_validator = SourceValidator(ROOT / 'third_party/scap-1.4-schemas/oval_5.12.3')

    def original(self, case=CASES[0]):
        raw = (FIXTURE / case['fixture']).read_bytes()
        self.assertEqual(sha256(raw).hexdigest(), case['fixture_sha256'])
        root = ET.fromstring(raw)
        nodes = {n.get('id'): n for n in root.iter() if n.get('id')}
        self.assertEqual(set(nodes), {n['id'] for n in case['dependencies']})
        for record in case['dependencies']:
            self.assertEqual(digest(xml_identity(nodes[record['id']])), record['sha256'])
        return root

    def visitor(self, root, mappings=None):
        return AssessmentConverter(OvalDocument(root, 'original.xml'), 'original.xml',
                                   load_mappings() if mappings is None else mappings)

    def proved(self, root, case=CASES[0]):
        before = ET.tostring(root)
        visitor = self.visitor(root)
        result = check_conversion(visitor, case['test'], self.validator)
        self.assertTrue(result['schema_valid'], result)
        self.assertTrue(result['compiled_operands_verified'], result)
        self.assertEqual(result['source_proof'], 'PROVED', result)
        self.assertEqual(before, ET.tostring(root))
        return assessment_for(self.visitor(root), case['test'])

    def entity(self, root):
        return root.find('.//' + W + 'type')

    def test_two_original_closures_valid_non_deprecated_and_proved(self):
        for case in CASES:
            with self.subTest(case=case['fixture']):
                root = self.original(case)
                check = self.source_validator.validate(etree.fromstring(ET.tostring(root)))
                inventory = SourceInventory(OvalDocument(root, 'original.xml'))
                validity = closure_validity(list(inventory.nodes.values()), {'original.xml': check})
                self.assertEqual(validity['status'], 'VALID', validity)
                self.assertFalse(any(i['kind'] == 'deprecated' for i in validity['issues']))
                a = self.proved(root, case)
                filters = next(n['filters'] for n in walk(a) if 'filters' in n)
                self.assertEqual(len(filters), 2)
                self.assertEqual(list(filters[0]), ['exclude'])
                self.assertEqual(list(filters[1]), ['exclude'])
                self.assertEqual(filters[0]['exclude']['enabled']['equals'], False)
                predicate = filters[1]['exclude']['type']
                self.assertEqual(predicate['equals'], [''])
                self.assertEqual(predicate['value_match'], 'one_or_more')
                # OVAL EntityStateSimpleBaseType defaults check_existence to
                # at_least_one_exists, independently of entity_check=all.
                self.assertEqual(predicate['values_found'], 'one_or_more')
                self.assertEqual(predicate['values_matching'], 'every')

    def test_literal_and_duplicate_empty_constants_preserve_quantifiers(self):
        for source_check, native_check in [('all', 'every'), ('at least one', 'one_or_more'),
                                           ('only one', 'exactly_one'), ('none satisfy', 'none')]:
            root = self.original()
            entity = self.entity(root)
            entity.set('var_check', source_check)
            ET.SubElement(root.find(O + 'variables')[0], O + 'value')
            a = self.proved(root)
            predicate = next(n['type'] for n in walk(a) if 'type' in n)
            self.assertEqual(predicate['equals'], ['', ''])
            self.assertEqual(predicate['value_match'], native_check)
        root = self.original()
        entity = self.entity(root)
        entity.attrib.pop('var_ref'); entity.attrib.pop('var_check')
        root.remove(root.find(O + 'variables'))
        self.proved(root)

    def test_missing_mapping_authorization_and_wrong_domain_fail_closed(self):
        for change in ('annotation', 'enum', 'capability'):
            mappings = load_mappings()
            m = next(m for m in mappings if m['capability'] == 'windows.ntuser')
            if change == 'annotation':
                m['migration_crosswalk']['source_defect_corrections'].clear()
            elif change == 'enum':
                m['native']['state_value_enums']['type'].remove('')
            else:
                m['capability'] = 'windows.registry'
            with self.subTest(change=change), self.assertRaises(ValueError):
                assessment_for(self.visitor(self.original(), mappings), CASES[0]['test'])

    def test_unknown_constant_cast_and_unsupported_operations_fail_closed(self):
        for change in ('unknown', 'cast', 'case insensitive equals', 'pattern match', 'not equal'):
            root = self.original()
            entity = self.entity(root)
            if change == 'unknown':
                root.find('.//' + O + 'value').text = 'reg_invented'
            elif change == 'cast':
                entity.set('datatype', 'int')
            else:
                entity.set('operation', change)
            with self.subTest(change=change), self.assertRaises(ValueError):
                assessment_for(self.visitor(root), CASES[0]['test'])

    def test_independent_reader_rejects_unknown_empty_cast(self):
        for change in ('unknown', 'cast'):
            root = self.original()
            if change == 'unknown':
                root.find('.//' + O + 'value').text = 'reg_invented'
            else:
                root.find(O + 'variables')[0].set('datatype', 'int')
            with self.subTest(change=change), self.assertRaises(ValueError):
                state = next(n for n in root.find(O + 'states') if n.find(W + 'type') is not None)
                ExpandedSource(root).state(state.get('id'), 'windows.ntuser')

    def test_native_mutations_cannot_keep_independent_proof(self):
        root = self.original()
        original = self.proved(root)
        for change in ('operand', 'quantifier', 'action', 'order', 'drop', 'absence'):
            a = deepcopy(original)
            filters = next(n['filters'] for n in walk(a) if 'filters' in n)
            predicate = filters[1]['exclude']['type']
            if change == 'operand': predicate['equals'] = ['string']
            elif change == 'quantifier': predicate['value_match'] = 'every'
            elif change == 'action': filters[1] = {'include': filters[1]['exclude']}
            elif change == 'order': filters.reverse()
            elif change == 'drop': filters.pop()
            else:
                predicate.clear(); predicate['values_found'] = 'none'
            with self.subTest(change=change):
                try:
                    proof = expanded_compare(ExpandedSource(root), CASES[0]['definition'], a)
                except ValueError:
                    continue
                self.assertNotEqual(proof['outcome'], 'PROVED', proof)


if __name__ == '__main__':
    unittest.main()
