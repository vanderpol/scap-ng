"""Focused migration-contract tests; not an admission of new converter output."""

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator
from tools.v04_variable_function_migration import (canonical_assessment, canonical_expression,
                                                    legacy_expression, UnsupportedExpression)


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / 'schema/v0.4.0/variable-function-expression.schema.json').read_text())
VALIDATOR = Draft202012Validator(SCHEMA)


def call(name, args=None, options=None):
    return {'function': {'name': name, 'arguments': args or [{'variable': 'source-variable'}],
                         'options': options if options is not None else {}}}


class CanonicalFunctionExpressionTests(unittest.TestCase):
    def assert_valid(self, expression):
        self.assertEqual(list(VALIDATOR.iter_errors(expression)), [])

    def assert_invalid(self, expression):
        self.assertFalse(VALIDATOR.is_valid(expression), expression)

    def test_all_thirteen_names_have_valid_forms(self):
        options = {
            'arithmetic': {'arithmetic_operation': 'add'},
            'begin': {'character': '/'}, 'end': {'character': '/'},
            'split': {'delimiter': ':'},
            'substring': {'substring_start': 3, 'substring_length': 2},
            'regex_capture': {'pattern': '(.*)'},
        }
        for name in SCHEMA['$defs']['function_call']['properties']['function']['properties']['name']['enum']:
            with self.subTest(name=name):
                args = [{'variable': 'left-variable'}, {'variable': 'right-variable'}] if name in ('concat', 'arithmetic') else None
                self.assert_valid(call(name, args, options.get(name)))

    def test_nested_canonical_functions(self):
        nested = call('begin', [call('substring', options={'substring_start': 3, 'substring_length': 2})],
                      {'character': 'prefix-'})
        self.assert_valid(nested)

    def test_reject_old_layout_and_typo(self):
        self.assert_invalid({'substring': {'value': {'variable': 'source-variable'}, 'start': 3, 'length': 2}})
        self.assert_invalid(call('substring', options={'start': 3, 'length': 2}))
        self.assert_invalid(call('substring', options={'substring_start': 3, 'substring_length': 2, 'unknown': 1}))

    def test_reject_missing_options_and_bad_arity(self):
        self.assert_invalid(call('substring'))
        self.assert_invalid(call('concat'))
        self.assert_invalid(call('begin', args=[{'variable': 'a'}, {'variable': 'b'}], options={'character': '/'}))
        self.assert_invalid(call('time_difference', args=[{'variable': 'a'}] * 3))

    def test_reject_malformed_operand(self):
        self.assert_invalid(call('count', [{'variable': 'v', 'literal': 'x'}]))
        self.assert_invalid(call('count', [{'function': {'name': 'unique', 'arguments': [], 'options': {}}}]))

    def test_reject_unsupported_types_and_options(self):
        self.assert_invalid(call('glob_to_regex', options={'glob_noescape': 'false'}))
        self.assert_invalid(call('time_difference', options={'format_2': 'local_time'}))
        self.assert_invalid(call('substring', options={'substring_start': 2147483648, 'substring_length': 2}))
        self.assert_invalid(call('arithmetic', [{'variable': 'a'}, {'variable': 'b'}], {'arithmetic_operation': 'subtract'}))

    def test_legacy_four_function_migration(self):
        legacy = {'merge': {'delimiter': ',', 'sort': 'document', 'order': 'ascending',
                            'values': {'unique': {'regex_capture': {
                                'pattern': '(.*)', 'value': {'concat': [
                                    {'variable': 'v'}, {'literal': {'datatype': 'string', 'value': '-suffix'}}]
                                }}}}}}
        original = json.dumps(legacy, sort_keys=True)
        migrated = canonical_expression(legacy)
        self.assert_valid(migrated)
        self.assertEqual(json.dumps(legacy, sort_keys=True), original)
        self.assertEqual(migrated['function']['name'], 'merge')
        self.assertEqual(migrated['function']['arguments'][0]['function']['name'], 'unique')
        self.assertEqual(legacy_expression(migrated), legacy)

    def test_real_apache_fixture_migration(self):
        document = json.loads((ROOT / 'tests/fixtures/v04-apache-preview/SV-214251.json').read_text())
        migrated = canonical_assessment(document)
        self.assertEqual(document['assessment']['tests'], migrated['assessment']['tests'])
        for variable in migrated['assessment']['variables'].values():
            if variable.get('kind') == 'local':
                self.assert_valid(variable['expression'])
        for key, original in document['assessment']['variables'].items():
            if original.get('kind') == 'local':
                self.assertEqual(legacy_expression(migrated['assessment']['variables'][key]['expression']),
                                 original['expression'])

    def test_unknown_expression_fails_closed(self):
        with self.assertRaises(UnsupportedExpression):
            canonical_expression({'arithmetic': [1, 2]})

    def test_existing_local_variable_fixtures_round_trip(self):
        covered = 0
        for path in (ROOT / 'tests/fixtures').rglob('*.json'):
            try:
                document = json.loads(path.read_text())
            except (ValueError, UnicodeError):
                continue
            assessment = document.get('assessment') if isinstance(document, dict) else None
            if not isinstance(assessment, dict) or not isinstance(assessment.get('variables'), dict):
                continue
            local = {k: v for k, v in assessment['variables'].items()
                     if isinstance(v, dict) and v.get('kind') == 'local' and 'expression' in v}
            if not local:
                continue
            migrated = canonical_assessment(document)
            for key, variable in local.items():
                with self.subTest(file=str(path.relative_to(ROOT)), variable=key):
                    expression = migrated['assessment']['variables'][key]['expression']
                    self.assert_valid(expression)
                    self.assertEqual(legacy_expression(expression), variable['expression'])
                    covered += 1
        self.assertGreaterEqual(covered, 70)


if __name__ == '__main__':
    unittest.main()
