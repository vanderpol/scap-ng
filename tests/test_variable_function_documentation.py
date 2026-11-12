"""Issue #19 retained-variable documentation and schema-shape checks."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / 'schema' / 'variable-expression.schema.json'


class VariableFunctionDocumentationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = json.loads(SCHEMA.read_text())
        cls.expression = cls.document['$defs']['expression']
        cls.branches = {
            next(iter(branch['required'])): branch
            for branch in cls.expression['oneOf']
        }

    def test_retained_expression_inventory_is_complete_and_documented(self):
        expected = {'literal', 'variable', 'values', 'concat',
                    'regex_capture', 'unique', 'merge', 'count', 'split', 'substring', 'arithmetic', 'begin', 'end'}
        self.assertEqual(set(self.branches), expected)
        for name, branch in self.branches.items():
            with self.subTest(expression=name):
                self.assertTrue(branch.get('title'))
                self.assertTrue(branch.get('description'))
                node = branch['properties'][name]
                self.assertTrue(node.get('title'))
                self.assertTrue(node.get('description'))

    def test_concat_help_covers_order_cartesian_product_and_status(self):
        node = self.branches['concat']['properties']['concat']
        self.assertEqual(node['minItems'], 2)
        text = node['description'].lower()
        for term in ('two or more', 'order', 'cartesian product',
                     'nonexistent', 'error', 'incomplete', 'not collected',
                     'not applicable', 'cast', 'incompatible'):
            with self.subTest(term=term):
                self.assertIn(term, text)
        self.assertGreaterEqual(len(node['examples']), 2)
        self.assertTrue(any(len(example) >= 3 for example in node['examples']))
        self.assertTrue(any(isinstance(example[0].get('literal'), list)
                            for example in node['examples']))

    def test_nested_expression_sites_have_author_help(self):
        values = self.branches['values']['properties']['values']['properties']
        self.assertIn('collected field', values['field']['description'].lower())
        regex = self.branches['regex_capture']['properties']['regex_capture']['properties']
        self.assertIn('capture', regex['pattern']['description'].lower())
        self.assertIn('input', regex['value']['title'].lower())
        merge = self.branches['merge']['properties']['merge']['properties']
        for key in ('delimiter', 'sort', 'order', 'values'):
            with self.subTest(key=key):
                self.assertTrue(merge[key].get('title'))
                self.assertTrue(merge[key].get('description'))
        self.assertIn('duplicate',
                      self.branches['unique']['properties']['unique']['description'].lower())

    def test_restored_function_help_and_explicit_options(self):
        for name, required in {
                'split': {'delimiter', 'value'},
                'substring': {'substring_start', 'substring_length', 'value'},
                'arithmetic': {'arithmetic_operation', 'values'},
                'begin': {'character', 'value'},
                'end': {'character', 'value'},
        }.items():
            with self.subTest(function=name):
                node = self.branches[name]['properties'][name]
                self.assertEqual(set(node['required']), required)
                self.assertTrue(node.get('description'))
                for key in required:
                    self.assertTrue(node['properties'][key].get('title'))
                    self.assertTrue(node['properties'][key].get('description'))
        unique = self.branches['unique']['properties']['unique']
        self.assertEqual(len(unique['oneOf']), 2)
        merge = self.branches['merge']['properties']['merge']['properties']['values']
        self.assertEqual(len(merge['oneOf']), 2)

    def test_documentation_does_not_claim_runtime_execution(self):
        text = json.dumps(self.document).lower()
        self.assertNotIn('runtime support is enabled', text)
        self.assertNotIn('compiler guarantees', text)


if __name__ == '__main__':
    unittest.main()
