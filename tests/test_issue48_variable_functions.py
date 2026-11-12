"""SCAP-NG 0.4 native Variable transformation contract fixtures."""
from __future__ import annotations

import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_ROOT = ROOT / 'schema'
PREFIX = 'https://scap-ng.dev/schema/v0.4.0/'


def registry():
    resources = {}
    for path in SCHEMA_ROOT.glob('*.schema.json'):
        document = json.loads(path.read_text())
        resource = Resource.from_contents(document)
        resources[PREFIX + path.name] = resource
        resources[document['$id']] = resource
    return Registry().with_resources(resources.items())


def declaration(datatype, expression):
    return {'kind': 'local', 'datatype': datatype, 'expression': expression}


class NativeVariableFunctionSchema(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads((SCHEMA_ROOT / 'variable-expression.schema.json').read_text())
        cls.validator = Draft202012Validator(cls.schema, registry=registry())

    def assert_valid(self, datatype, expression):
        self.validator.validate(declaration(datatype, expression))

    def assert_invalid(self, datatype, expression):
        with self.assertRaises(Exception):
            self.validator.validate(declaration(datatype, expression))

    def test_positive_native_forms_and_nested_composition(self):
        literal = lambda value: {'literal': value}
        self.assert_valid('string', {'split': {'delimiter': ',', 'value': literal('a,,b')}})
        self.assert_valid('string', {'substring': {
            'substring_start': 1, 'substring_length': 3, 'value': literal('abcdef')}})
        self.assert_valid('integer', {'arithmetic': {
            'arithmetic_operation': 'add', 'values': [literal(1), literal([2, 3])]}})
        self.assert_valid('string', {'begin': {'character': '/', 'value': literal('/etc')}})
        self.assert_valid('string', {'end': {'character': '/', 'value': literal('etc/')}})
        self.assert_valid('string', {'unique': [literal(['a', 'a']), literal(['b', 'a'])]})
        self.assert_valid('string', {'merge': {
            'delimiter': ',', 'sort': 'document', 'order': 'ascending',
            'values': [literal(['a', 'b']), literal(['c', 'a'])]}})
        self.assert_valid('integer', {'count': {'unique': [
            literal(['a', 'a']), literal(['b'])]}})

    def test_negative_arity_options_and_datatypes(self):
        literal = lambda value: {'literal': value}
        self.assert_invalid('string', {'split': {'value': literal('a')}})
        self.assert_invalid('string', {'substring': {
            'substring_start': 1, 'substring_length': 1, 'value': literal('a'),
            'extra': True}})
        self.assert_invalid('integer', {'arithmetic': {
            'arithmetic_operation': 'add', 'values': [literal(1)]}})
        self.assert_invalid('string', {'arithmetic': {
            'arithmetic_operation': 'add', 'values': [literal(1), literal(2)]}})
        self.assert_invalid('string', {'begin': {'character': '/', 'value': literal('a'), 'x': 1}})
        self.assert_invalid('string', {'unique': []})
        self.assert_invalid('string', {'merge': {
            'delimiter': ',', 'sort': 'document', 'order': 'ascending', 'values': []}})
        self.assert_invalid('string', {'function': {
            'name': 'split', 'arguments': [literal('a')], 'options': {'delimiter': ','}}})


if __name__ == '__main__':
    unittest.main()
