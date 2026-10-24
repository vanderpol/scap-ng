#!/usr/bin/env python3
"""0.4 field cardinality scoping and record requirements, no scanner claims.

The Enterprise/EnterpriseS fixture retains the reviewed real-source shape:
two independent complete conditions joined with OR; per-field existence and
matching requirements must be explicit or inherited through declared scopes.
Refs #240 #248 #239.
"""
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator
from referencing import Registry, Resource


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {'values_found': 'one_or_more', 'values_matching': 'every'}
OPTIONAL = {'values_found': 'may_be_absent', 'values_matching': 'every'}


def requirement():
    return {'items_found': 'one_or_more', 'items_satisfying': 'every',
            'field_requirement': dict(REQUIRED),
            'or': [
                {'fields': {'type': {'equals': 'string'},
                            'value': {'equals': 'Enterprise'}}},
                {'fields': {'type': {'equals': 'string'},
                            'value': {'equals': 'EnterpriseS'}}},
            ]}


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
            with self.subTest(schema=validator.schema['$id'], req=req):
                errors = list(validator.iter_errors(doc))
                self.assertEqual(not errors, valid,
                                 '\n'.join(e.message for e in errors)[:1400])

    def test_enterprise_alternative_complete_conditions(self):
        self.assert_valid(requirement())
        req = requirement()
        req['items_found'] = 'may_be_absent'
        req['items_satisfying'] = 'one_or_more'
        self.assert_valid(req)

    def test_test_group_condition_and_field_scopes(self):
        req = requirement()
        # Test-wide inheritance applies to both OR alternatives.
        self.assert_valid(req)
        req['or'][0] = {'and': [req['or'][0]], 'field_requirement': dict(OPTIONAL)}
        req['or'][0]['and'][0]['field_requirement'] = dict(REQUIRED)
        req['or'][0]['and'][0]['fields']['value'].update(OPTIONAL)
        self.assert_valid(req)
        for scope in (req, req['or'][0], req['or'][0]['and'][0]):
            old = scope['field_requirement']
            scope['field_requirement'] = 'at_least_one_exists_and_all_match'
            self.assert_valid(req, valid=False)
            scope['field_requirement'] = old
        field = req['or'][0]['and'][0]['fields']['value']
        field['values_matching'] = 'all'
        self.assert_valid(req, valid=False)

    def test_explicit_requirement_can_start_at_each_scope(self):
        for scope in ('test', 'group', 'condition', 'field'):
            req = requirement()
            if scope != 'test':
                del req['field_requirement']
                if scope == 'group':
                    # Individual alternatives can inherit from their own group.
                    req['or'] = [{'and': [alt], 'field_requirement': dict(REQUIRED)}
                                 for alt in req['or']]
                elif scope == 'condition':
                    for alt in req['or']:
                        alt['field_requirement'] = dict(REQUIRED)
                else:
                    for alt in req['or']:
                        for field in alt['fields'].values():
                            field.update(REQUIRED)
            self.assert_valid(req)

    def test_missing_scope_and_sibling_leakage_rejected(self):
        req = requirement()
        del req['field_requirement']
        self.assert_valid(req, valid=False)
        req['or'][0]['field_requirement'] = dict(REQUIRED)
        self.assert_valid(req, valid=False)
        req['or'][1]['field_requirement'] = dict(REQUIRED)
        self.assert_valid(req)
        del req['or'][1]['field_requirement']
        req['or'][1]['fields']['value'].update(REQUIRED)
        self.assert_valid(req, valid=False)  # type remains unscoped

    def test_old_names_rejected_in_every_scope(self):
        for name in ('require', 'state_fields_require', 'states_match',
                     'override_fields_requirement', 'fields_require', 'state'):
            req = requirement()
            req[name] = dict(REQUIRED)
            self.assert_valid(req, valid=False)
            req = requirement()
            req['or'][0][name] = dict(REQUIRED)
            self.assert_valid(req, valid=False)
            req = requirement()
            req['or'][0]['fields']['value'][name] = dict(REQUIRED)
            self.assert_valid(req, valid=False)
        for name in ('state_fields_require', 'field_requirement',
                     'override_fields_requirement', 'collected_items_require'):
            self.assert_valid(requirement(),
                              test_changes={name: dict(REQUIRED)}, valid=False)

    def test_item_existence_does_not_encode_satisfaction(self):
        for found in ('none', 'exactly_one', 'one_or_more', 'may_be_absent'):
            self.assert_valid({'items_found': found})
            for satisfying in ('none', 'exactly_one', 'one_or_more', 'every'):
                req = requirement()
                req['items_found'] = found
                req['items_satisfying'] = satisfying
                self.assert_valid(req)
        for old in ('all', 'every', 'and', 'at_least_one_exists'):
            req = requirement()
            req['items_found'] = old
            self.assert_valid(req, valid=False)

    def test_logical_operators_and_structural_rejections(self):
        for operator in ('and', 'or', 'one', 'xor'):
            req = requirement()
            req[operator] = req.pop('or')
            self.assert_valid(req)
        for invalid in ({'or': []}, {'fields': {}}, {'or': 'all'},
                        {'or': [{'fields': {'value': {'equals': 1}}}], 'and': []},
                        {'fields': [{'value': {'equals': 1}}]},
                        {'or': [{'fields': {'value': {'equals': 1}}}],
                         'field_requirement': 'one_or_more'}):
            req = {'items_found': 'one_or_more', 'items_satisfying': 'every', **invalid}
            self.assert_valid(req, valid=False)

    def test_expected_operand_matching_remains_independent(self):
        for pred in ({'bitwise_and': 4096}, {'version_greater_than': '1.2'},
                     {'equals': [1, 2], 'datatype': 'integer',
                      'value_match': 'exactly_one'},
                     {'equals': {'variable': 'edition-variable'},
                      'datatype': 'string', 'value_match': 'one_or_more'},
                     {'equals': {'input': 'edition-input'},
                      'datatype': 'string', 'value_match': 'every'}):
            req = requirement()
            req['or'] = [{'fields': {'value': pred}}]
            self.assert_valid(req)
        for pred in ({'equals': [1, 2]}, {'equals': {'variable': 'edition-variable'}},
                     {'equals': 1, 'not_equal': 2}, {'unknown_comparison': 1}):
            req = requirement()
            req['or'] = [{'fields': {'value': pred}}]
            self.assert_valid(req, valid=False)

    def test_existing_record_nesting_with_distinct_requirements(self):
        # Source-backed Windows 11 SV-253264 record subtree; fixture wrapper
        # is not a claim to reconstruct the complete source OVAL Test.
        record = {'record': {
            'records_found': 'one_or_more', 'records_matching': 'one_or_more',
            'fields': {'productstate': {'bitwise_and': 4096, **REQUIRED}}}}
        req = requirement()
        req['or'] = [{'fields': {'value': record}}]
        self.assert_valid(req)
        for invalid in (
            {'record': {'fields': record['record']['fields']}},
            {'record': {'records_found': 'one_or_more',
                        'fields': record['record']['fields']}},
            {'record': {'records_found': 'one_or_more',
                        'records_matching': 'every',
                        'fields': {'productstate': {'bitwise_and': 4096}}}},
            {'record': {**record['record'], 'item_conditions': 'all'}},
            {'bitwise_and': 4096, 'records_matching': 'every'},
        ):
            req['or'] = [{'fields': {'value': invalid}}]
            self.assert_valid(req, valid=False)

    def test_field_absence_has_one_canonical_comparator_free_form(self):
        # OVAL State entity check_existence=none_exist is independent of
        # value matching. A field-local absence overrides inherited matching.
        req = requirement()
        req['or'] = [{'fields': {'unlabeled': {'values_found': 'none'}}}]
        self.assert_valid(req)
        del req['field_requirement']
        self.assert_valid(req)  # explicit absence needs no inherited pair

        for predicate in (
            {'values_found': 'none', 'values_matching': 'every'},
            {'values_found': 'none', 'equals': ''},
            {'values_found': 'none', 'datatype': 'string'},
            {'values_found': 'none', 'value_match': 'none'},
            {'values_found': 'none', 'redact_result': True},
            {'values_found': 'none', 'equals': None},
            {'require': 'none_exist'},
            {'absent': True},
            {'exists': False},
            {'values_found': 'one_or_more'},
        ):
            with self.subTest(predicate=predicate):
                req['or'] = [{'fields': {'unlabeled': predicate}}]
                self.assert_valid(req, valid=False)

        # 'none matching' means values were observed but failed comparison.
        req = requirement()
        req['or'] = [{'fields': {'unlabeled': {
            'values_found': 'one_or_more', 'values_matching': 'none',
            'equals': 'unexpected'}}}]
        self.assert_valid(req)

    def test_field_absence_cannot_be_duplicated_as_inherited_pair(self):
        for scope in ('test', 'condition'):
            req = requirement()
            requirement_pair = {'values_found': 'none', 'values_matching': 'every'}
            if scope == 'test':
                req['field_requirement'] = requirement_pair
            else:
                req['or'][0]['field_requirement'] = requirement_pair
            self.assert_valid(req, valid=False)

    def test_record_and_record_member_absence_use_matching_count_vocabulary(self):
        req = requirement()
        req['or'] = [{'fields': {'record_value': {
            'record': {'records_found': 'none'}}}}]
        self.assert_valid(req)
        req['or'] = [{'fields': {'record_value': {'record': {
            'records_found': 'one_or_more', 'records_matching': 'every',
            'fields': {'unlabeled': {'values_found': 'none'}}}}}}]
        self.assert_valid(req)

        for record in (
            {'records_found': 'none', 'records_matching': 'every'},
            {'records_found': 'none', 'fields': {'unlabeled': {'values_found': 'none'}}},
            {'records_found': 'none', 'redact_result': True},
            {'records_found': 'one_or_more'},
            {'records_found': 'one_or_more', 'records_matching': 'every'},
            {'require': 'none_exist'},
        ):
            with self.subTest(record=record):
                req['or'] = [{'fields': {'record_value': {'record': record}}}]
                self.assert_valid(req, valid=False)

    def test_description_distinguishes_three_scopes(self):
        definitions = self.language['$defs']
        self.assertEqual(definitions['cardinality']['enum'],
                         ['none', 'exactly_one', 'one_or_more', 'every'])
        self.assertNotIn('every', definitions['item_existence_cardinality']['enum'])
        self.assertIn('provenance',
                      definitions['canonical_all_items_requirement']['properties']
                      ['items_found']['description'])
        self.assertIn('never silently defaulted',
                      definitions['canonical_all_items_requirement']['description'])


if __name__ == '__main__':
    unittest.main()
