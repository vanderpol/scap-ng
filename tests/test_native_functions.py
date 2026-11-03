"""Bounded owner-directed three-function shape and compatibility (#10)."""
from copy import deepcopy
import json
from pathlib import Path
import unittest
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]


def call(name, args, **options):
    return {'function': {'name': name, 'arguments': args, 'options': options}}


class FunctionShape(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads((ROOT/'schema/variable-expression.schema.json').read_text())
        resources = [(d['$id'], Resource.from_contents(d)) for p in (ROOT/'schema').glob('*.schema.json')
                     for d in [json.loads(p.read_text())]]
        cls.validator = Draft202012Validator(cls.schema, registry=Registry().with_resources(resources))

    def accepts(self, expr, datatype='string'):
        self.validator.validate(dict(kind='local', datatype=datatype, expression=expr))

    def test_three_operations_require_explicit_complete_options(self):
        self.accepts(call('arithmetic', [{'literal': [1, 2]}, {'literal': [3, 4, 5]}], arithmetic_operation='add'), 'integer')
        self.accepts(call('substring', [{'literal': 'abcdefg'}], substring_start=3, substring_length=-1))
        self.accepts(call('split', [{'literal': '-a-a-'}], delimiter='-'))
        for expr in (call('count', [{'literal': 'x'}]), call('concat', [{'literal': 'a'}, {'literal': 'b'}]),
                     call('arithmetic', [{'literal': 1}], arithmetic_operation='add'),
                     call('split', [{'literal': 'x'}]), call('split', [{'literal': 'x'}], delimiter=',', flags='g'),
                     call('substring', [{'literal': 'x'}], substring_start=1, substring_length=2**31),
                     call('arithmetic', [{'literal': 1}, {'literal': 2}], arithmetic_operation='divide')):
            self.assertTrue(list(self.validator.iter_errors(dict(kind='local', datatype='string', expression=expr))))

    def test_no_option_normalization_and_no_implicit_result_cast(self):
        for start in (-2147483648, 0, 2147483647):
            self.accepts(call('substring', [{'literal': ''}], substring_start=start, substring_length=-1))
        self.accepts(call('split', [{'literal': 'a.*b'}], delimiter='.*'))
        self.accepts(call('split', [{'literal': ''}], delimiter=''))
        expr=call('arithmetic', [{'literal': 2}, {'literal': 3}], arithmetic_operation='multiply')
        self.assertTrue(list(self.validator.iter_errors(dict(kind='local', datatype='string', expression=expr))))

    def test_exact_inverse_preserves_all_previous_grammar(self):
        current=deepcopy(self.schema)
        current['$defs'].pop('function_expression')
        self.assertEqual(current['$defs']['expression']['oneOf'].pop(), {'$ref':'#/$defs/function_expression'})
        self.assertEqual(len(current['$defs']['declaration']['allOf']), 4)
        del current['$defs']['declaration']['allOf'][1:]
        old=json.loads((ROOT/'tests/fixtures/pre-function-variable-expression.json').read_text())
        for key in ('title','description','x-last-modified','x-scap-ng-owner-decision'):
            if key in old:current[key]=old[key]
            else:current.pop(key,None)
        self.assertEqual(current,old)
