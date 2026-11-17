import json
from pathlib import Path
import unittest

ROOT = Path(__file__).parents[1]

class ApplicabilityInheritanceContract(unittest.TestCase):
    def test_rule_applicability_is_optional_and_group_is_recursive(self):
        rule = json.loads((ROOT / 'schema/rule.schema.json').read_text())
        self.assertNotIn('applicability', rule['properties']['rule']['required'])
        benchmark = json.loads((ROOT / 'schema/benchmark.schema.json').read_text())
        group = benchmark['$defs']['group']
        self.assertEqual(group['properties']['groups']['items']['$ref'], '#/$defs/group')
        self.assertIn('applicability', group['properties'])

    def test_expression_preserves_nested_boolean_shape_and_source_provenance(self):
        app = json.loads((ROOT / 'schema/applicability.schema.json').read_text())
        expr = app['$defs']['expression']
        self.assertEqual(len(expr['oneOf']), 4)
        condition = app['properties']['applicability']['properties']['conditions']['additionalProperties']
        self.assertIn('source', condition['properties'])
        # Unqualified source identity is represented, not fabricated as FALSE.
        self.assertEqual(condition['required'], [])

    def test_frozen_040_is_not_modified_in_active_tree(self):
        self.assertEqual(json.loads((ROOT / 'schema/benchmark.schema.json').read_text())['x-scap-ng-version'], '0.4.1')
        self.assertNotIn('schema/v0.4.0', '\n'.join(p.as_posix() for p in ROOT.glob('schema/*')))
