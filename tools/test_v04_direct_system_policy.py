"""Pinned password/lockout policy graphs and approved no-Object acquisition."""
from copy import deepcopy
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

from v04_direct_scap_source import SourceModel, UnsupportedSource, OVAL
from v04_direct_inventory import SourceInventory
from v04_direct_converter import AssessmentConverter, convert, load_mappings
from v04_direct_system_policy import POLICIES
from v04_expanded_source_proof import ExpandedSource, original_policy_contract
from audit_v04_direct_benchmark import verify_original, verify_compiled
from v04_native_bundle_compiler import build_bundle
from validate_native_json_schemas import build_validators, document_errors
from v04_direct_authoring_examples import walk

ROOT = Path(__file__).resolve().parents[1]
PINS = json.loads((ROOT / 'tests/fixtures/v04-direct-prototype/provenance.json').read_text())
O, W = '{' + OVAL + '}', '{' + OVAL + '#windows}'


class DirectSystemPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SourceModel(ROOT / 'tests/fixtures/v04-direct-prototype' / PINS['fixture'], PINS['zip_sha256'])
        cls.rows = [r for r in SourceInventory(cls.source).rules() if POLICIES & set(r['needed_capabilities'])]
        cls.rules = [r['source_rule'] for r in cls.rows]
        cls.docs, cls.trace = convert(cls.source, cls.rules)

    def entity(self, source, cap='windows.passwordpolicy', field='min_passwd_len'):
        for binding in self.trace['rules']:
            for identifier, node in binding['dependencies'].items():
                if node['kind'] != 'state':
                    continue
                state = source.node(binding['component'], identifier, 'state')
                entity = state.find(W + field)
                if state.tag == W + cap.split('.')[-1] + '_state' and entity is not None:
                    return binding, state, entity
        self.fail('original policy field unavailable')

    def test_all_ten_original_closures_schema_validate_compile_and_prove_without_objects(self):
        self.assertEqual(len(self.rules), 10)
        self.assertEqual(sum('windows.passwordpolicy' in r['needed_capabilities'] for r in self.rows), 7)
        self.assertEqual(len(verify_original(self.source.root, self.docs, self.trace)), 10)
        self.assertEqual(len(verify_compiled(self.docs, build_bundle(self.docs)[0])), 10)
        validators = build_validators(ROOT / 'schema/v0.4.0')
        for doc in self.docs.values():
            if 'assessment' not in doc:
                continue
            self.assertFalse(list(document_errors(validators['assessment.schema.json'], doc)))
            assessment = doc['assessment']
            self.assertNotIn('shared_objects', assessment)
            for test in assessment['tests'].values():
                self.assertIn(test['capability'], POLICIES)
                self.assertNotIn('object', test)
                self.assertIsInstance(test['require'], dict)

    def test_original_fixed_types_are_required_not_omission_defaults(self):
        for field in ('min_passwd_len', 'password_complexity'):
            source = deepcopy(self.source)
            binding, state, entity = self.entity(source, field=field)
            entity.attrib.pop('datatype')
            with self.subTest(field=field), self.assertRaises(UnsupportedSource):
                convert(source, [binding['source_rule']])
            with self.assertRaises(ValueError):
                ExpandedSource(source.components[binding['component']]).state(state.get('id'), 'windows.passwordpolicy')
        types = {n['datatype'] for d in self.docs.values() for n in walk(d) if 'datatype' in n}
        self.assertTrue({'integer', 'boolean'} <= types)

    def test_constant_variable_original_var_check_default_and_explicit_alternative(self):
        for var_check, matching in ((None, 'every'), ('at least one', 'one_or_more')):
            source = deepcopy(self.source)
            binding, state, entity = self.entity(source)
            entity.text = None
            identifier = 'oval:direct.policy.test:var:1'
            entity.set('var_ref', identifier)
            if var_check:
                entity.set('var_check', var_check)
            variables = source.components[binding['component']].find(O + 'variables')
            variable = ET.SubElement(variables, O + 'constant_variable', id=identifier, version='1', datatype='int', comment='Controlled policy length values')
            for value in ('14', '15'):
                ET.SubElement(variable, O + 'value').text = value
            source.index()
            docs, trace = convert(source, [binding['source_rule']])
            predicate = next(n for d in docs.values() for n in walk(d) if n.get('value_match') == matching)
            self.assertEqual(predicate['greater_than_or_equal'], [14, 15])
            verify_original(source.root, docs, trace)
            verify_compiled(docs, build_bundle(docs)[0])
            predicate['value_match'] = 'none'
            with self.assertRaises(AssertionError):
                verify_original(source.root, docs, trace)

    def test_original_field_type_and_range_errors_fail_closed_in_both_readers(self):
        for mutation in ('unknown', 'datatype', 'range', 'range-lexical'):
            source = deepcopy(self.source)
            binding, state, entity = self.entity(source, field='max_passwd_age')
            if mutation == 'unknown': entity.tag = W + 'invented_policy'
            elif mutation == 'datatype': entity.set('datatype', 'string')
            else: entity.text = '-1' if mutation == 'range' else 'not-an-integer'
            with self.subTest(mutation=mutation), self.assertRaises(UnsupportedSource):
                convert(source, [binding['source_rule']])
            with self.assertRaises(ValueError):
                ExpandedSource(source.components[binding['component']]).state(state.get('id'), 'windows.passwordpolicy')
        self.assertEqual({k for k, (_, ranged) in original_policy_contract('windows.lockoutpolicy').items() if ranged},
                         {'force_logoff', 'lockout_duration'})

    def test_singleton_source_selectors_sets_filters_and_variable_acquisition_reject(self):
        for cap in POLICIES:
            binding = next(b for b in self.trace['rules'] if any(
                n['kind'] == 'object' and self.source.node(b['component'], i, 'object').tag == W + cap.split('.')[-1] + '_object'
                for i, n in b['dependencies'].items()))
            identifier = next(i for i, n in binding['dependencies'].items() if n['kind'] == 'object')
            for child in (W + 'selector', O + 'set', O + 'filter'):
                source = deepcopy(self.source)
                ET.SubElement(source.node(binding['component'], identifier, 'object'), child).text = 'invented'
                with self.subTest(cap=cap, child=child), self.assertRaises(UnsupportedSource):
                    convert(source, [binding['source_rule']])
            visitor = AssessmentConverter(self.source, binding['component'], load_mappings())
            component = ET.Element(O + 'object_component', object_ref=identifier, item_field='invented')
            with self.assertRaises(UnsupportedSource):
                visitor.function(component)

    def test_native_dummy_objects_changed_cardinality_and_boolean_logic_reject(self):
        for mutation in ('object', 'found', 'boolean'):
            docs = deepcopy(self.docs)
            a = next(d['assessment'] for d in docs.values() if 'assessment' in d and
                     any('and' in n for n in walk(d['assessment']['tests'])))
            test = next(iter(a['tests'].values()))
            if mutation == 'object': test['object'] = {}
            elif mutation == 'found': test['require']['items_found'] = 'none'
            else:
                condition = next(n for n in walk(a['tests']) if 'and' in n)
                condition['or'] = condition.pop('and')
            with self.subTest(mutation=mutation), self.assertRaises(AssertionError):
                verify_original(self.source.root, docs, self.trace)
            if mutation == 'object':
                with self.assertRaises(ValueError): build_bundle(docs)


if __name__ == '__main__':
    unittest.main()
