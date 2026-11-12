"""Guard the active SCAP-NG 0.4.0 native count expression contract.

Run: python3 -m unittest tests/test_active_count_expression.py
This is a schema-shape test, NOT a runtime or OVAL equivalence proof.
"""
import json
import unittest
from pathlib import Path

SCHEMA = Path(__file__).resolve().parents[1] / "schema" / "variable-expression.schema.json"


class ActiveCountContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        cls.branches = cls.schema["$defs"]["expression"]["oneOf"]

    def test_count_is_active_and_recursively_composable(self):
        forms = {
            next(iter(branch["required"])): branch for branch in self.branches
        }
        self.assertEqual(
            set(forms),
            {"literal", "variable", "values", "concat", "regex_capture",
             "unique", "merge", "count"},
        )
        counted = forms["count"]
        self.assertEqual(counted["properties"]["count"]["$ref"], "#/$defs/expression")
        self.assertFalse(counted["additionalProperties"])
        self.assertEqual(counted["required"], ["count"])

    def test_existing_variable_shapes_remain_unchanged_in_number(self):
        self.assertEqual(self.schema["x-scap-ng-version"], "0.4.0")
        self.assertEqual(len(self.branches), 8)

    def test_count_describes_duplicates_and_failed_collection(self):
        definition = next(branch for branch in self.branches if branch["required"] == ["count"])
        help_text = definition["properties"]["count"]["description"].lower()
        self.assertIn("duplicates", help_text)
        self.assertIn("zero", help_text)
        self.assertIn("error", help_text)
        self.assertIn("not-collected", help_text)


if __name__ == "__main__":
    unittest.main()


class ActiveCountQualification(unittest.TestCase):
    """Schema admission plus explicit status contract vectors.

    These tests qualify authoring shape and the declared semantic contract;
    they are not scanner/runtime equivalence evidence.
    """
    @classmethod
    def setUpClass(cls):
        from jsonschema import Draft202012Validator
        from referencing import Registry, Resource
        cls.schema = json.loads(SCHEMA.read_text(encoding='utf-8'))
        resources = {}
        for path in (SCHEMA.parent).glob('*.json'):
            value = json.loads(path.read_text(encoding='utf-8'))
            if '$id' in value:
                resources[value['$id']] = Resource.from_contents(value)
        cls.validator = Draft202012Validator(cls.schema, registry=Registry().with_resources(resources.items()))

    def assert_valid(self, expression, datatype='integer'):
        declaration = {'kind': 'local', 'datatype': datatype, 'expression': expression}
        errors = list(self.validator.iter_errors(declaration))
        self.assertFalse(errors, [e.message for e in errors])

    def assert_invalid(self, expression, datatype='integer'):
        declaration = {'kind': 'local', 'datatype': datatype, 'expression': expression}
        self.assertTrue(list(self.validator.iter_errors(declaration)))

    def test_nested_duplicate_unique_empty_and_integer_shape(self):
        self.assert_valid({'count': {'count': {'literal': ['a', 'a']}}})
        self.assert_valid({'count': {'unique': {'literal': ['a', 'a']}}})
        self.assert_valid({'count': {'literal': []}})
        self.assert_invalid({'function_call': {'name': 'count', 'arguments': []}})
        # Datatype derivation is a semantic gate, not a JSON Schema claim.
        self.assert_valid({'count': {'literal': ['a']}}, datatype='string')

    def test_missing_input_is_a_semantic_error_not_schema_zero(self):
        # JSON Schema admits a reference-shaped expression; resolution is a
        # separate semantic gate and must not fabricate an empty population.
        self.assert_invalid({'count': {}})

    def test_count_status_contract(self):
        def count_status(status, values=()):
            if status != 'complete':
                return status, None
            return 'complete', len(values)
        for status in ('error', 'unknown', 'not_evaluated', 'incomplete'):
            self.assertEqual(count_status(status), (status, None))
        self.assertEqual(count_status('complete', []), ('complete', 0))
        self.assertEqual(count_status('complete', ['x', 'x']), ('complete', 2))
