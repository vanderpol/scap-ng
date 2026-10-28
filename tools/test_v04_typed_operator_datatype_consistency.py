"""Prevent contradictory self-describing comparison datatypes in 0.4 (Refs #255).

The comparator defines the comparison domain. An explicit, matching datatype
remains valid because the direct converter emits it for non-string source types.
"""
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator
from referencing import Registry, Resource


ROOT = Path(__file__).resolve().parents[1] / 'schema/v0.4.0'


class TypedComparisonDatatypeConsistencyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        schemas = [json.loads(p.read_text()) for p in ROOT.glob('*.schema.json')]
        registry = Registry().with_resources(
            (schema['$id'], Resource.from_contents(schema)) for schema in schemas)
        language = next(s for s in schemas if s['$id'].endswith('assessment-language.schema.json'))
        cls.definitions = language['$defs']
        cls.registry = registry

    def valid(self, scope, predicate):
        validator = Draft202012Validator(
            {'$ref': f'#/$defs/{scope}', '$defs': self.definitions}, registry=self.registry)
        return not list(validator.iter_errors(predicate))

    def test_matching_and_mismatching_explicit_datatypes(self):
        for scope in ('scalar_field_predicate', 'record_field_predicate',
                      'object_selector_predicate'):
            for key, domain, value in (
                ('version_equals', 'version', '1.0'),
                ('ipv4_subset_of', 'ipv4', '192.0.2.0/24'),
                ('rpm_evr_greater_than', 'rpm_evr', '0:1.0-1'),
                ('float_equals', 'float', 1.25),
            ):
                base = {key: value, 'datatype': domain}
                if scope != 'object_selector_predicate':
                    base.update(values_found='one_or_more', values_matching='every')
                with self.subTest(scope=scope, comparison=key):
                    self.assertTrue(self.valid(scope, base))
                    bad = {**base, 'datatype': 'string'}
                    self.assertFalse(self.valid(scope, bad))
                    without_redundant_tag = {k: v for k, v in base.items() if k != 'datatype'}
                    self.assertTrue(self.valid(scope, without_redundant_tag))

    def test_ordinary_string_comparison_unaffected(self):
        for scope in ('scalar_field_predicate', 'record_field_predicate',
                      'object_selector_predicate'):
            value = {'equals': 'example', 'datatype': 'string'}
            if scope != 'object_selector_predicate':
                value.update(values_found='one_or_more', values_matching='every')
            self.assertTrue(self.valid(scope, value))

    def test_every_typed_operator_in_active_scopes(self):
        guard = self.definitions['typed_comparison_datatype_consistency']
        for operation, rule in guard['dependentSchemas'].items():
            domain = rule['properties']['datatype']['const']
            value = 1.25 if domain == 'float' else '1.0'
            for scope in ('scalar_field_predicate', 'record_field_predicate',
                          'object_selector_predicate'):
                predicate = {operation: value, 'datatype': domain}
                if scope != 'object_selector_predicate':
                    predicate.update(values_found='one_or_more', values_matching='every')
                with self.subTest(scope=scope, operation=operation):
                    self.assertTrue(self.valid(scope, predicate))
                    self.assertFalse(self.valid(scope, {**predicate, 'datatype': 'string'}))


if __name__ == '__main__':
    unittest.main()
