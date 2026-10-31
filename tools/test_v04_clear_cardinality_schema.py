#!/usr/bin/env python3
"""Focused schema boundaries for the 0.4 review-candidate cardinality vocabulary.

These tests check language acceptance, not six-valued evaluator equivalence.
No converter, compiler or scanner behavior is inferred from passing tests.
"""
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator
from referencing import Registry, Resource


ROOT = Path(__file__).resolve().parents[1]
EXISTENCE = ('none', 'exactly_one', 'one_or_more', 'every', 'zero_or_more')
ITEM_EXISTENCE = ('none', 'exactly_one', 'one_or_more', 'zero_or_more')
SATISFACTION = ('none', 'exactly_one', 'one_or_more', 'every')
FIELD_COUNT = {'values_found': 'one_or_more', 'values_matching': 'every'}


def assessment(requirement):
    return {'assessment': {
        'id': 'quantifier-review', 'version': 1,
        'assessment_title': 'Quantifier grammar fixture', 'mode': 'automated',
        'class': 'inventory',
        'specification': {'id': 'scap-ng.pre-alpha.assessment', 'version': '0.4.0'},
        'tests': {'quantifier-test': {
            'test_title': 'Quantifier fixture', 'capability': 'windows.registry',
            'reported_elements': 'all', 'require': requirement}},
        'evaluate': {'test': 'quantifier-test'},
    }}


def with_field(*, existence='one_or_more', satisfying='every', field=None):
    return {'items_found': existence, 'items_satisfying': satisfying,
            'field_requirement': dict(FIELD_COUNT),
            'fields': {'value': field or {'equals': 1, **FIELD_COUNT}}}


class ClearCardinalitySchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        schemas = [json.loads(p.read_text()) for p in
                   (ROOT / 'schema/v0.4.0').glob('*.schema.json')]
        cls.schemas = schemas
        registry = Registry().with_resources(
            (s['$id'], Resource.from_contents(s)) for s in schemas)
        cls.validators = [Draft202012Validator(s, registry=registry) for s in schemas
                          if s['$id'].endswith(('/assessment.schema.json',
                                               '/assessment-language.schema.json'))]
        cls.collected_validator = Draft202012Validator(next(
            s for s in schemas if s['$id'].endswith('/collected-item.schema.json')),
            registry=registry)
        cls.collection_validator = Draft202012Validator(next(
            s for s in schemas if s['$id'].endswith('/collection-result.schema.json')),
            registry=registry)
        language = next(s for s in schemas if s['$id'].endswith('/assessment-language.schema.json'))
        cls.record_selection_validator = Draft202012Validator(
            {'$ref': '#/$defs/object_record_field_predicate',
             '$defs': language['$defs']}, registry=registry)
        common = next(s for s in schemas if s['$id'].endswith('/capability-common.schema.json'))
        cls.filter_validator = Draft202012Validator(
            {'$id': common['$id'], '$ref': '#/$defs/state_filter',
             '$defs': common['$defs']},
            registry=registry)
        cls.list_validator = Draft202012Validator(
            {'$id': common['$id'], '$ref': '#/$defs/list_predicate',
             '$defs': common['$defs']},
            registry=registry)
        report = next(s for s in schemas if s['$id'].endswith('/item-report.schema.json'))
        projected = report['properties']['item_report']['properties']['items']
        cls.projected_item_validator = Draft202012Validator(
            projected['items']['properties']['item'], registry=registry)

    def assert_grammar(self, req, *, valid=True):
        for validator in self.validators:
            with self.subTest(schema=validator.schema['$id'], req=req):
                errors = list(validator.iter_errors(assessment(req)))
                self.assertEqual(not errors, valid,
                                 '\n'.join(e.message for e in errors)[:1300])

    def test_all_semantically_distinct_item_existence_check_pairs_are_expressible(self):
        # OVAL all_exist and at_least_one_exists map to one_or_more in NG.
        # 4 NG Item-existence meanings x 4 OVAL check meanings, including rare pairs.
        for found in ITEM_EXISTENCE:
            self.assert_grammar({'items_found': found})  # State-free case
            for satisfying in SATISFACTION:
                self.assert_grammar(with_field(existence=found,
                                               satisfying=satisfying))

    def test_field_and_record_quantifiers_cover_complete_cross_product(self):
        # Preserve coverage of all combinations, but reject redundant comparison
        # clauses when confirmed absence is the complete requirement. The OVAL
        # source attributes remain separate migration provenance.
        for found in EXISTENCE:
            for matching in SATISFACTION:
                fields = {'equals': 1, 'values_found': found,
                          'values_matching': matching}
                self.assert_grammar(with_field(field=fields), valid=found != 'none')
                record = {'record': {
                    'records_found': found, 'records_matching': matching,
                    'fields': {'productstate': {
                        'bitwise_and': 4096, **FIELD_COUNT}}}}
                self.assert_grammar(with_field(field=record), valid=found != 'none')
        self.assert_grammar(with_field(field={'values_found': 'none'}))
        self.assert_grammar(with_field(field={'record': {'records_found': 'none'}}))

    def test_inline_scalar_and_nested_record_require_explicit_cardinality(self):
        # Field-local cardinality is optional when the Test declares its pair.
        self.assert_grammar(with_field(field={'equals': 1}))
        for field in (
            {'equals': 1, 'values_found': 'one_or_more'},
            {'equals': 1, 'values_matching': 'every'},
            {'equals': 1, 'require': 'at_least_one_exists_and_all_match'},
            {'record': {'records_found': 'one_or_more', 'fields': {
                'productstate': {'bitwise_and': 4096, **FIELD_COUNT}}}},
            {'record': {'records_found': 'one_or_more', 'records_matching': 'every',
                        'fields': {'productstate': {'bitwise_and': 4096}}}},
        ):
            self.assert_grammar(with_field(field=field), valid=False)

    def test_legacy_vocabulary_is_rejected_not_accepted_as_aliases(self):
        for invalid in ('all', 'one', 'at_least_one', 'at least one',
                        'none_exist', 'all_exist', 'may be absent'):
            self.assert_grammar({'items_found': invalid}, valid=False)
            self.assert_grammar(with_field(satisfying=invalid), valid=False)
            self.assert_grammar(with_field(field={
                'equals': 1, 'values_found': 'one_or_more',
                'values_matching': invalid}), valid=False)
        self.assert_grammar({'items_found': 'every'}, valid=False)
        self.assert_grammar(with_field(existence='every'), valid=False)
        for invalid in ('items', 'all_items_must', 'states', 'states_match'):
            req = with_field()
            req[invalid] = 'all'
            self.assert_grammar(req, valid=False)

    def test_complete_state_logic_keeps_one_distinct_from_xor(self):
        fields = [{'fields': {'value': {'equals': 1, **FIELD_COUNT}}},
                  {'fields': {'value': {'equals': 2, **FIELD_COUNT}}}]
        for operator in ('and', 'or', 'one', 'xor'):
            self.assert_grammar({'items_found': 'one_or_more',
                                 'items_satisfying': 'every',
                                 'field_requirement': dict(FIELD_COUNT), operator: fields})
        for operator in ('all', 'any', 'odd'):
            self.assert_grammar({'items_found': 'one_or_more',
                                 'items_satisfying': 'every', operator: fields},
                                valid=False)

    def test_field_requirement_inheritance_is_explicit_and_scoped(self):
        req = {'items_found': 'one_or_more', 'items_satisfying': 'every',
               'field_requirement': dict(FIELD_COUNT),
               'or': [{'fields': {'type': {'equals': 'Enterprise'}}},
                      {'fields': {'type': {'equals': 'EnterpriseS'}}}]}
        self.assert_grammar(req)
        del req['field_requirement']
        self.assert_grammar(req, valid=False)
        req['or'][0]['field_requirement'] = dict(FIELD_COUNT)
        self.assert_grammar(req, valid=False)  # sibling does not inherit
        req['or'][1]['field_requirement'] = dict(FIELD_COUNT)
        self.assert_grammar(req, valid=False)  # not a substitute for Test baseline
        req['field_requirement'] = dict(FIELD_COUNT)
        self.assert_grammar(req)

    def test_expected_operand_cardinality_has_same_tokens_but_distinct_name(self):
        for quantifier in SATISFACTION:
            self.assert_grammar(with_field(field={
                'equals': [1, 2], 'datatype': 'integer',
                'value_match': quantifier, **FIELD_COUNT}))
        for old in ('all', 'one', 'only one', 'at least one'):
            self.assert_grammar(with_field(field={
                'equals': [1, 2], 'datatype': 'integer',
                'value_match': old, **FIELD_COUNT}), valid=False)

    def test_selector_and_list_quantifiers_use_identical_token_set(self):
        for count in SATISFACTION:
            selector = {'equals': 1, 'selection_match': count}
            self.assertFalse(list(self.record_selection_validator.iter_errors(selector)))
            self.assertFalse(list(self.list_validator.iter_errors({
                'item': {'equals': 1, **FIELD_COUNT},
                'values_found': 'one_or_more', 'values_matching': count})))
        for old in ('all', 'one'):
            self.assertTrue(list(self.record_selection_validator.iter_errors({
                'equals': 1, 'selection_match': old})))
            self.assertTrue(list(self.list_validator.iter_errors({
                'item': {'equals': 1, **FIELD_COUNT},
                'values_found': 'one_or_more', 'values_matching': old})))

    def test_object_filter_groups_use_the_same_logical_and_field_vocabulary(self):
        field = {'owner_uid': {'equals': 0, **FIELD_COUNT}}
        inherited = {'owner_uid': {'equals': 0}}
        for operator in ('and', 'or', 'one', 'xor'):
            with self.subTest(operator=operator):
                condition = {'field_requirement': dict(FIELD_COUNT),
                             operator: [inherited]}
                self.assertFalse(list(self.filter_validator.iter_errors(
                    {'include': condition})))
                self.assertFalse(list(self.filter_validator.iter_errors(
                    {'exclude': {operator: [field]}})))
                self.assertTrue(list(self.filter_validator.iter_errors(
                    {'include': {operator: 'not_an_array'}})))
        for legacy in ('all', 'any', 'odd'):
            self.assertTrue(list(self.filter_validator.iter_errors(
                {'include': {legacy: [field]}})))
        self.assertTrue(list(self.filter_validator.iter_errors(
            {'include': {'state_fields_require': dict(FIELD_COUNT),
                         'and': [inherited]}})))

    def test_input_multiplicity_uses_exactly_one_not_logical_one(self):
        validator = next(v for v in self.validators
                         if v.schema['$id'].endswith('/assessment.schema.json'))
        for count in ('exactly_one', 'zero_or_one', 'one_or_more', 'zero_or_more'):
            doc = assessment(with_field())
            doc['assessment']['inputs'] = {'source-values-input': {
                'datatype': 'string', 'cardinality': count, 'required': True}}
            self.assertFalse(list(validator.iter_errors(doc)), count)
        doc['assessment']['inputs']['source-values-input']['cardinality'] = 'one'
        self.assertTrue(list(validator.iter_errors(doc)))

    def test_missing_items_are_not_fabricated_does_not_exist_items(self):
        empty_collection = {'id': 'collection-1', 'capability': 'unix.file',
                            'status': 'complete', 'item_refs': []}
        self.assertFalse(list(self.collection_validator.iter_errors(empty_collection)))
        item = {'id': 'collected-1', 'capability': 'unix.file', 'status': 'exists',
                'fields': {}, 'provenance': {}}
        self.assertFalse(list(self.collected_validator.iter_errors(item)))
        self.assertFalse(list(self.projected_item_validator.iter_errors(item)))
        item['status'] = 'does_not_exist'
        self.assertTrue(list(self.collected_validator.iter_errors(item)))
        self.assertTrue(list(self.projected_item_validator.iter_errors(item)))

    def test_all_schema_enum_values_use_one_spelling_convention(self):
        def walk(node):
            if isinstance(node, dict):
                if isinstance(node.get('enum'), list):
                    for token in node['enum']:
                        if isinstance(token, str):
                            self.assertNotRegex(token, r'\s')
                for value in node.values():
                    walk(value)
            elif isinstance(node, list):
                for value in node:
                    walk(value)

        for schema in self.schemas:
            with self.subTest(schema=schema['$id']):
                walk(schema)

    def test_legacy_source_crosswalk_and_display_terms_match_authoring(self):
        mapping = json.loads((ROOT / 'schema/v0.4.0/capability-mappings/'
                              'supported/unix.file.json').read_text())
        crosswalk = mapping['migration_crosswalk']
        self.assertEqual(crosswalk['check'], {
            'all': 'every', 'at least one': 'one_or_more',
            'only one': 'exactly_one', 'none satisfy': 'none'})
        self.assertEqual(crosswalk['existence'], {
            'all_exist': 'one_or_more', 'at_least_one_exists': 'one_or_more',
            'none_exist': 'none', 'only_one_exists': 'exactly_one',
            'any_exist': 'zero_or_more'})
        sidecar = json.loads((ROOT / 'schema/v0.4.0/'
                              'authoring-vocabulary.en.json').read_text())
        terms = sidecar['term_scopes']
        for key in ('test.require.items_found', 'test.require.items_satisfying',
                    'field.values_found', 'field.values_matching',
                    'record.records_found', 'record.records_matching'):
            self.assertIn(key, terms)
        self.assertFalse([key for key in terms if key.startswith(('test.states',
                                                                   'state.field.',
                                                                   'assessment.evaluate.all',
                                                                   'assessment.evaluate.any',
                                                                   'assessment.evaluate.odd'))])


if __name__ == '__main__':
    unittest.main()
