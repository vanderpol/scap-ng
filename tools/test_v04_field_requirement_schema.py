#!/usr/bin/env python3
"""Production 0.4 field-requirement schema boundaries; no scanner claims.

The Enterprise/EnterpriseS fixture follows the source-backed owner scope packet
review/current/0.4.0-FIELD-REQUIREMENT-SCOPE.md (OVAL State AND, Test OR).
Refs #240 #248 #239.
"""
from copy import deepcopy
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = 'at_least_one_exists_and_all_match'
OPTIONAL = 'may_be_absent_and_all_match'


def requirement():
    return {'items': 'one_or_more', 'field_requirement': REQUIRED,
            'all_items_must': [{'or': [
                {'fields': {'type': {'equals': 'string'},
                            'value': {'equals': 'Enterprise'}}},
                {'fields': {'type': {'equals': 'string'},
                            'value': {'equals': 'EnterpriseS'}}},
            ]}]}


def document(req):
    return {'assessment': {
        'id': 'edition-assessment', 'version': 1,
        'assessment_title': 'Windows Enterprise editions', 'mode': 'automated',
        'class': 'inventory', 'purpose': 'applicability',
        'specification': {'id': 'scap-ng.pre-alpha.assessment', 'version': '0.4.0'},
        'tests': {'edition-test': {
            'test_title': 'Enterprise or EnterpriseS',
            'capability': 'windows.registry', 'reported_elements': 'all',
            'require': req}}, 'evaluate': {'test': 'edition-test'}}}


class ProductionFieldRequirementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        schemas = [json.loads(p.read_text()) for p in
                   (ROOT / 'schema/v0.4.0').glob('*.schema.json')]
        registry = Registry().with_resources(
            (s['$id'], Resource.from_contents(s)) for s in schemas)
        cls.language = next(s for s in schemas if s['$id'].endswith('/assessment-language.schema.json'))
        cls.validators = [Draft202012Validator(s, registry=registry) for s in schemas
                          if s['$id'].endswith(('/assessment.schema.json',
                                               '/assessment-language.schema.json'))]

    def assert_valid(self, req, *, test_changes=None, valid=True):
        doc = document(req)
        doc['assessment']['tests']['edition-test'].update(test_changes or {})
        for validator in self.validators:
            with self.subTest(schema=validator.schema['$id']):
                errors = list(validator.iter_errors(doc))
                self.assertEqual(not errors, valid,
                                 '\n'.join(e.message for e in errors)[:1500])

    def test_enterprise_alternative_complete_conditions(self):
        self.assert_valid(requirement())
        value = requirement()
        value['items'] = 'may_be_absent'
        self.assert_valid(value)

    def test_all_four_scopes_and_nearest_overrides(self):
        value = requirement()
        group = value['all_items_must'][0]
        group['field_requirement'] = OPTIONAL
        group['or'][0]['field_requirement'] = REQUIRED
        group['or'][0]['fields']['value']['field_requirement'] = 'only_one_exists_and_matches'
        group['or'][1] = {'and': [group['or'][1]], 'field_requirement': REQUIRED}
        self.assert_valid(value)
        for scope in (value, group, group['or'][0], group['or'][0]['fields']['value']):
            old = scope['field_requirement']
            scope['field_requirement'] = 'one_or_more'
            self.assert_valid(value, valid=False)
            scope['field_requirement'] = old

    def test_explicit_requirement_can_start_at_any_scope(self):
        for scope in ('group', 'condition', 'field'):
            value = requirement()
            del value['field_requirement']
            group = value['all_items_must'][0]
            if scope == 'group':
                group['field_requirement'] = REQUIRED
            else:
                for condition in group['or']:
                    if scope == 'condition':
                        condition['field_requirement'] = REQUIRED
                    else:
                        for field in condition['fields'].values():
                            field['field_requirement'] = REQUIRED
            self.assert_valid(value)

    def test_missing_scope_and_sibling_leakage_rejected(self):
        value = requirement()
        del value['field_requirement']
        self.assert_valid(value, valid=False)
        group = value['all_items_must'][0]
        group['or'][0]['field_requirement'] = REQUIRED
        self.assert_valid(value, valid=False)
        group['or'][1] = {'and': [group['or'][1]], 'field_requirement': REQUIRED}
        self.assert_valid(value)
        del group['or'][1]['field_requirement']
        group['or'][1]['and'][0]['fields']['value']['field_requirement'] = REQUIRED
        self.assert_valid(value, valid=False)  # type remains unscoped

    def test_legacy_names_rejected_at_each_canonical_scope(self):
        for name in ('require', 'state_fields_require', 'override_fields_requirement',
                     'fields_require', 'fields_requirement', 'state'):
            for location in ('test', 'group', 'condition', 'field'):
                with self.subTest(name=name, location=location):
                    value = requirement()
                    group = value['all_items_must'][0]
                    target = {'test': value, 'group': group,
                              'condition': group['or'][0],
                              'field': group['or'][0]['fields']['value']}[location]
                    target[name] = REQUIRED
                    self.assert_valid(value, valid=False)
        for name in ('state_fields_require', 'field_requirement',
                     'override_fields_requirement', 'collected_items_require'):
            self.assert_valid(requirement(), test_changes={name: REQUIRED}, valid=False)

    def test_population_and_field_policy_are_distinct(self):
        for items in ('none', 'exactly_one', 'all', 'and', REQUIRED):
            value = requirement(); value['items'] = items
            self.assert_valid(value, valid=False)
        for items in ('one_or_more', 'none', 'exactly_one', 'all', 'may_be_absent'):
            self.assert_valid({'items': items})  # existing state-free vocabulary
        value = requirement(); del value['items']
        self.assert_valid(value, valid=False)

    def test_complete_condition_logic_and_structural_rejections(self):
        for op in ('and', 'or', 'one', 'xor'):
            value = requirement()
            value['all_items_must'][0] = {op: value['all_items_must'][0]['or']}
            self.assert_valid(value)
        for condition in ({'or': []}, {'fields': {}}, {'or': 'all'},
                          {'or': [{'fields': {'value': {'equals': 1}}}], 'and': []},
                          {'value': {'equals': 'Enterprise', 'field_requirement': REQUIRED}},
                          {'fields': [{'value': {'equals': 1}}], 'fields_operator': 'or'}):
            value = requirement(); value['all_items_must'] = [condition]
            self.assert_valid(value, valid=False)
        for changes in ({'states': []}, {'states_match': 'any'}):
            self.assert_valid(requirement(), test_changes=changes, valid=False)

    def test_operator_and_dynamic_operand_guards_preserved(self):
        for pred in ({'bitwise_and': 4096}, {'version_greater_than': '1.2'},
                     {'equals': [1, 2], 'datatype': 'integer', 'value_match': 'one'},
                     {'equals': {'variable': 'edition-variable'},
                      'datatype': 'string', 'value_match': 'one_or_more'},
                     {'equals': {'input': 'edition-input'},
                      'datatype': 'string', 'value_match': 'all'}):
            value = requirement()
            value['all_items_must'] = [{'fields': {'value': pred}}]
            self.assert_valid(value)
        for pred in ({'equals': [1, 2]}, {'equals': {'variable': 'edition-variable'}},
                     {'equals': 1, 'not_equal': 2}, {'unrecognized_operator': 1}):
            value = requirement(); value['all_items_must'] = [{'fields': {'value': pred}}]
            self.assert_valid(value, valid=False)

    def test_uncommon_source_exact_and_record_fallback_retained(self):
        state = {'value': {'record': {
            'require': 'at_least_one_exists_and_some_match',
            'fields': {'productstate': {'bitwise_and': 4096, 'require': REQUIRED}}}}}
        for op in ('and', 'or', 'one', 'xor'):
            self.assert_valid('only_one_exists_and_none_match', test_changes={
                'states': [{op: [deepcopy(state), deepcopy(state)]}],
                'states_match': 'any'})
        self.assert_valid('only_one_exists')

    def test_machine_readable_scope_and_and_descriptions(self):
        defs = self.language['$defs']
        self.assertIn('all fields', defs['canonical_all_items_requirement']['properties']['field_requirement']['description'])
        self.assertIn('this field only', defs['canonical_field_predicate']['properties']['field_requirement']['description'])
        for name in ('canonical_condition', 'canonical_inherited_condition'):
            for branch in defs[name]['oneOf']:
                text = branch['properties']['field_requirement']['description']
                self.assertIn('nearest explicitly declared', text)
                self.assertIn('no implicit default', text)
                self.assertIn('independently of require.items', text)
                if branch['required'] == ['fields']:
                    self.assertIn('implicitly ANDed', branch['description'])
                else:
                    self.assertIn('all descendant fields in every branch', text)


if __name__ == '__main__':
    unittest.main()
