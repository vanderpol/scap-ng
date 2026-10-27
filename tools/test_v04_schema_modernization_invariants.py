"""Cross-capability 0.3 modernization preservation in the native 0.4 schema.

The fixtures are deliberately schema-level: they do not claim collector or
scanner equivalence. These guards prevent literal-array and var_check support
from disappearing when another OVAL capability is introduced.
"""

import json
from pathlib import Path
import unittest

from test_generate_capability_schema_v04 import materialize, validate


ROOT = Path(__file__).resolve().parents[1]
MAPS = ROOT / 'schema/v0.4.0/capability-mappings/supported'
QUANTIFIERS = ('none', 'exactly_one', 'one_or_more', 'every')


def datatype_constraint(node):
    """Find the source-XSD-derived datatype enum inside a selector schema."""
    if isinstance(node, dict):
        types = node.get('properties', {}).get('datatype') if isinstance(node.get('properties'), dict) else None
        if isinstance(types, dict) and types.get('enum'):
            return types['enum'][0]
        for value in node.values():
            found = datatype_constraint(value)
            if found:
                return found
    if isinstance(node, list):
        for value in node:
            found = datatype_constraint(value)
            if found:
                return found
    return None


def values_for(datatype, enum):
    if enum:
        return [enum[0], enum[-1]]
    return {
        'string': ['first', 'second'],
        'integer': [1, 2],
        'boolean': [False, True],
        'number': [1.25, 2.5],
        'float': [1.25, 2.5],
    }.get(datatype, ['first', 'second'])


class ModernizationSchemaInvariants(unittest.TestCase):
    def test_all_native_object_selectors_accept_typed_arrays_and_quantifiers(self):
        """Static Variable inlining is capability-independent for selectors."""
        mappings = [json.loads(path.read_text()) for path in sorted(MAPS.glob('*.json'))]
        self.assertEqual(len(mappings), 100)
        examined = 0
        for mapping in mappings:
            native = mapping['native']
            if not native.get('selector_map'):
                continue
            schema = materialize(mapping['capability'])
            for name in sorted(set(native['selector_map'].values())):
                with self.subTest(capability=mapping['capability'], selector=name):
                    field_schema = schema['$defs']['object']['properties'][name]
                    datatype = datatype_constraint(field_schema)
                    self.assertIsNotNone(datatype)
                    enum = native.get('selector_value_enums', {}).get(name)
                    values = values_for(datatype, enum)
                    for value_match in QUANTIFIERS:
                        pred = {'equals': values, 'datatype': datatype, 'value_match': value_match}
                        self.assertFalse(validate(schema, 'object/properties/' + name, pred))
                        reference = {'equals': {'variable': 'sample-variable'},
                                     'datatype': datatype, 'value_match': value_match}
                        self.assertFalse(validate(schema, 'object/properties/' + name, reference))
                    self.assertTrue(validate(schema, 'object/properties/' + name,
                                             {'equals': values, 'datatype': datatype}))
                    self.assertTrue(validate(schema, 'object/properties/' + name,
                                             {'equals': {'variable': 'sample-variable'},
                                              'datatype': datatype}))
                    # The existing compact-scalar modernization remains legal.
                    self.assertFalse(validate(schema, 'object/properties/' + name,
                                              {'equals': values[0]}))
                    examined += 1
        self.assertGreater(examined, 100)

    def test_every_native_state_field_preserves_common_literal_and_record_contracts(self):
        """State-local predicates may not revert to per-capability OVAL States."""
        inspected = 0
        for path in sorted(MAPS.glob('*.json')):
            mapping = json.loads(path.read_text())
            schema = materialize(mapping['capability'])
            expression = schema['$defs'].get('state_predicate')
            if not isinstance(expression, dict):
                continue
            records = set(mapping['native'].get('record_state_fields', []))
            for entry in expression.get('oneOf', []):
                name, = entry['required']
                child = entry['properties'][name]
                with self.subTest(capability=mapping['capability'], field=name):
                    if name in records:
                        self.assertTrue(child['$ref'].endswith('#/$defs/record_wrapper_predicate'))
                    else:
                        self.assertTrue(any(part.get('$ref', '').endswith(
                            '#/$defs/scalar_field_predicate') for part in child['allOf']))
                inspected += 1
        self.assertGreater(inspected, 200)

    def test_value_match_does_not_replace_field_population_matching(self):
        """0.3's expected-value quantifier remains separate from observed values."""
        schema = materialize('file.hash')
        valid = {'algorithm': {'equals': ['md5', 'sha1'], 'datatype': 'string',
                 'value_match': 'one_or_more', 'values_found': 'one_or_more',
                 'values_matching': 'every'}}
        self.assertFalse(validate(schema, 'state_expression', valid))
        for bad in (
            {'algorithm': {'equals': ['md5', 'sha1'], 'datatype': 'string',
                           'values_found': 'one_or_more', 'values_matching': 'every'}},
        ):
            self.assertTrue(validate(schema, 'state_expression', bad))

    def test_pending_strict_array_datatype_requires_coordinated_converter_update(self):
        """Preserve a visible gate for the pre-existing permissive 0.4 behavior.

        Existing source-proved Windows user-rights output omits datatype:string
        from static array selectors. Tightening this must be coordinated with
        explicit-type converter emission; a schema-only change breaks that gate.
        """
        schema = materialize('windows.userright')
        pred = {'equals': ['SE_BACKUP_NAME', 'SE_RESTORE_NAME'], 'value_match': 'every'}
        self.assertFalse(validate(schema, 'object/properties/userright', pred))

    def test_array_and_variable_shapes_are_not_allowed_as_scalar_acquisition_parameters(self):
        """An acquisition contract must opt into multivalued collection semantics."""
        schema = materialize('independent.shellcommand')
        parameter = schema['$defs']['object']['properties']['command']
        # These parameter fields are separate from Object selectors. An OVAL
        # var_ref does not prove that a native collector can expand acquisition.
        self.assertEqual(parameter['oneOf'][0]['type'], 'string')
        self.assertTrue(validate(schema, 'object/properties/command', ['a', 'b']))
        self.assertFalse(validate(schema, 'object/properties/command', {'variable': 'command-variable'}))


if __name__ == '__main__':
    unittest.main()
