"""Independent bound witnesses and output mutations for the final owner review."""
from copy import deepcopy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import generate_unix_file_reference as docs

URI = docs.NEXT + 'capabilities/unix.file.schema.json'


class CardinalityAndParity(unittest.TestCase):
    def test_required_and_conditionals_use_the_applicable_parent_context(self):
        node = {'type': 'object', 'properties': {'mode': {'type': 'string'}, 'traversal': {'type': 'object'}},
                'if': {'required': ['mode'], 'properties': {'mode': {'const': 'walk'}}},
                'then': {'required': ['traversal']}}
        self.assertEqual(docs.property_occurrences(node, URI, 'traversal'), 'conditional')
        self.assertEqual(docs.property_occurrences(node, URI, 'traversal', context={'mode': 'walk', 'traversal': {}}), '1..1')
        self.assertEqual(docs.property_occurrences(node, URI, 'traversal', context={'mode': 'flat'}), '0..1')
        v = Draft202012Validator(node)
        self.assertFalse(v.is_valid({'mode': 'walk'}))
        self.assertTrue(v.is_valid({'mode': 'walk', 'traversal': {}}))
        self.assertTrue(v.is_valid({'mode': 'flat'}))
        node['required'] = ['traversal']
        self.assertEqual(docs.property_occurrences(node, URI, 'traversal'), '1..1')

    def test_alternative_and_forbidden_property_contexts(self):
        node = {'type': 'object', 'properties': {'filepath': {}, 'path': {}},
                'oneOf': [{'required': ['filepath'], 'not': {'required': ['path']}},
                          {'required': ['path'], 'not': {'required': ['filepath']}}]}
        self.assertEqual(docs.property_occurrences(node, URI, 'filepath'), 'conditional')
        self.assertEqual(docs.property_occurrences(node, URI, 'filepath', context={'filepath': '/f'}), '1..1')
        self.assertEqual(docs.property_occurrences(node, URI, 'path', context={'filepath': '/f'}), '0..0')
        self.assertFalse(Draft202012Validator(node).is_valid({'filepath': '/f', 'path': '/'}))
        # A forbidden VALUE is not a forbidden PROPERTY.
        paired = {'required': ['values_found'], 'properties': {'values_found': {'type': 'string'}},
                  'not': {'required': ['values_found'], 'properties': {'values_found': {'const': 'none'}}}}
        self.assertEqual(docs.property_occurrences(paired, URI, 'values_found'), '1..1')
        self.assertTrue(Draft202012Validator(paired).is_valid({'values_found': 'one_or_more'}))
        self.assertFalse(Draft202012Validator(paired).is_valid({'values_found': 'none'}))

    def test_array_and_map_entry_bounds_do_not_become_named_key_bounds(self):
        array = {'type': 'array', 'items': {'type': 'integer'}}
        self.assertEqual(docs.collection_occurrences(array, URI, 'array'), '0..n')
        array.update(minItems=2, maxItems=4)
        self.assertEqual(docs.collection_occurrences(array, URI, 'array'), '2..4')
        self.assertTrue(Draft202012Validator(array).is_valid([1, 2]))
        self.assertFalse(Draft202012Validator(array).is_valid([1]))
        self.assertFalse(Draft202012Validator(array).is_valid([1, 2, 3, 4, 5]))
        mapping = {'type': 'object', 'properties': {'known': {}}, 'additionalProperties': {'type': 'integer'}, 'minProperties': 2, 'maxProperties': 3}
        self.assertEqual(docs.collection_occurrences(mapping, URI, 'map'), '2..3')
        self.assertEqual(docs.property_occurrences(mapping, URI, 'known'), '0..1')
        self.assertTrue(Draft202012Validator(mapping).is_valid({'a': 1, 'b': 2}))
        self.assertFalse(Draft202012Validator(mapping).is_valid({'a': 1}))
        closed = {'type': 'object', 'properties': {'a': {}, 'b': {}}, 'additionalProperties': False, 'minProperties': 2}
        self.assertEqual(docs.collection_occurrences(closed, URI, 'map'), '2..2')
        self.assertEqual(docs.property_occurrences(closed, URI, 'a'), '1..1')
        self.assertEqual(docs.property_occurrences(closed, URI, 'unknown'), '0..0')
        split = {'allOf': [{'required': ['a']}, {'required': ['b']}]}
        self.assertEqual(docs.collection_occurrences(split, URI, 'map'), '2..n')
        unsupported = {'type': 'array', 'contains': {'const': 1}}
        self.assertEqual(docs.collection_occurrences(unsupported, URI, 'array'), 'unspecified (conditional)')

    def test_payload_presence_is_conditional_and_separate_from_map_key(self):
        source, *_ = docs.load_schemas()
        value = source['$defs']['value_owner_uid']
        self.assertEqual(docs.property_occurrences(value, URI, 'value'), 'conditional')
        self.assertEqual(docs.property_occurrences(value, URI, 'value', context={'datatype': 'integer', 'status': 'error'}), '0..0')
        self.assertEqual(docs.property_occurrences(value, URI, 'value', context={'datatype': 'integer', 'status': 'exists', 'value': 7}), '0..1')
        self.assertEqual(docs.property_occurrences(source['$defs']['item_fields'], URI, 'owner_uid'), '0..1')

    def test_canonical_type_required_array_map_enum_and_default_mutations_reach_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(ROOT / 'schema', root / 'schema')
            shutil.copytree(ROOT / docs.PILOT, root / docs.PILOT)
            file = root / docs.ANNOTATIONS
            original = json.loads(file.read_text())
            changed = deepcopy(original)
            defs = changed['$defs']
            defs['value_owner_uid']['properties']['value']['type'] = 'number'
            defs['item_fields']['required'] = ['owner_uid']
            defs['item_fields']['minProperties'] = 2
            defs['item_fields']['maxProperties'] = 4
            branch = defs['item_fields']['properties']['owner_uid']['oneOf'][1]
            branch.update(minItems=2, maxItems=3)
            defs['object']['properties']['filesystem']['enum'] = ['all', 'local']
            defs['object']['properties']['filesystem']['default'] = 'all'
            file.write_text(json.dumps(changed))
            text, advanced = docs.render(root), docs.render_constraints(root)
            self.assertIn('| `owner_uid` | number | 1..1 key; 1..1 or 2..3 values |', text)
            self.assertIn('dynamic map (2..4 entries)', text)
            self.assertIn('Schema default annotation: `all`', text)
            row = next(line for line in text.splitlines() if line.startswith('| `filesystem`'))
            self.assertIn('`all`, `local`', row)
            self.assertNotIn('`same`', row)
            self.assertIn('| `owner_uid` | `integer` | number | 1..1 or 2..3 |', advanced)
            # A new required nested child is not inferred from the parent's occurrence.
            changed = deepcopy(original)
            traversal = changed['$defs']['object']['properties']['traversal']
            traversal['required'] = ['max_depth', 'recurse']
            changed['$defs']['object']['required'] = ['traversal']
            file.write_text(json.dumps(changed))
            self.assertIn('| `traversal` | object | 1..1 |', docs.render(root))

    def test_metadata_only_mutations_do_not_change_any_generated_page(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(ROOT / 'schema', root / 'schema')
            shutil.copytree(ROOT / docs.PILOT, root / docs.PILOT)
            file = root / 'schema/capability-mappings/supported/unix.file.json'
            mapping = json.loads(file.read_text())
            mapping['native']['field_datatypes']['owner_uid'] = ['invented']
            mapping['native']['object_selector_alternatives'] = [['invented']]
            file.write_text(json.dumps(mapping))
            source = root / docs.PILOT / 'source-map.json'
            pins = json.loads(source.read_text())
            pins['frozen_schema_sha256'][str(file.relative_to(root))] = docs.sha256(file.read_bytes()).hexdigest()
            source.write_text(json.dumps(pins))
            for render in [docs.render, docs.render_constraints, docs.render_parity]:
                self.assertEqual(render(root), render())

    def test_readthedocs_coverage_pins_and_statuses_include_every_item_row(self):
        schema, sources, mapping, *_ = docs.load_schemas()
        historical = sources['readthedocs']
        self.assertEqual({row['field'] for row in historical['items']['rows']}, set(mapping['state_field_map']))
        self.assertEqual(len(historical['items']['rows']), 23)
        self.assertEqual({r['field'] for r in historical['definitions']['rows'] if r['section'] == 'filebehaviors'}, {'max_depth', 'recurse', 'recurse_direction', 'recurse_file_system'})
        for page in historical.values():
            self.assertIn('5.12.3', page['title'])
            self.assertEqual(len(page['html_sha256']), 64)
        checklist = docs.render_parity()
        self.assertEqual(checklist.count('| Item `'), 23)
        for status in ['present', 'native-undecided', 'intentionally shared/link-only']:
            self.assertIn(status, checklist)
        self.assertIn('/$defs/value_type/properties/value', checklist)
        self.assertEqual(len(schema['$defs']['item_fields']['properties']), 23)


if __name__ == '__main__':
    unittest.main()
