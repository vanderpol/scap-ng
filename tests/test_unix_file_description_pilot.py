"""Acceptance and regression gates for the isolated Issue #38 proposal."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

from jsonschema import Draft202012Validator
from referencing import Resource
import yaml

from test_draft202012_and_examples import schema_registry

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('unix_file_pilot', ROOT / 'tools/generate_unix_file_reference.py')
pilot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pilot)


class UnixFileDescriptionPilot(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema, cls.sources, cls.mapping, _, _ = pilot.load_schemas()
        cls.registry = schema_registry().with_resource(cls.schema['$id'], Resource.from_contents(cls.schema))

    def test_overlay_has_no_new_validation_assertions(self):
        Draft202012Validator.check_schema(self.schema)
        # Structural proof: every sibling of the existing role $ref is a
        # description or a recursively annotation-only properties schema.
        # No type, enum, required, closure, branching or new default is allowed.
        def annotations_only(node):
            self.assertLessEqual(set(node), {'description', 'properties', '$ref', 'examples'})
            if '$ref' in node:
                self.assertEqual(node['$ref'], '#/$defs/field_meanings')
            for child in node.get('properties', {}).values():
                annotations_only(child)
        expected = {
            'object': pilot.PREFIX + 'native-selector.schema.json#/$defs/unix_file_object',
            'item': pilot.PREFIX + 'collected-item.schema.json',
            'require': pilot.PREFIX + 'assessment-language.schema.json#/$defs/canonical_all_items_requirement',
        }
        self.assertEqual(set(self.schema['$defs']), set(expected) | {'field_meanings'})
        annotations_only(self.schema['$defs']['field_meanings'])
        for role, ref in expected.items():
            node = deepcopy(self.schema['$defs'][role])
            self.assertEqual(node.pop('$ref'), ref)
            annotations_only(node)

    def test_frozen_and_proposed_acceptance_match_positive_negative_vectors(self):
        base = {'path': {'equals': '/example'}, 'filename': {'equals': 'config'}, 'filesystem': 'all'}
        objects = [(base, True), ({'filepath': {'equals': '/example/config'}}, True),
                   ({'path': {'equals': '/example'}, 'filename': None}, True)]
        for depth in [0, 1, 'unlimited']:
            for kind in ['directories', 'symlinks', 'symlinks_and_directories']:
                objects.append((dict(base, traversal={'max_depth': depth, 'recurse': kind}), True))
        for traversal in [{}, {'max_depth': 0}, {'recurse': 'directories'},
                          {'max_depth': -1, 'recurse': 'directories'},
                          {'max_depth': True, 'recurse': 'directories'},
                          {'max_depth': '1', 'recurse': 'directories'},
                          {'max_depth': None, 'recurse': 'directories'},
                          {'max_depth': 1, 'recurse': 'files'},
                          {'max_depth': 1, 'recurse': []},
                          {'max_depth': 1, 'recurse': 'directories', 'direction': 'up'}]:
            objects.append((dict(base, traversal=traversal), False))
        objects += [(dict(base, max_depth=1), False), (dict(base, recurse='directories'), False)]
        field = {'datatype': 'integer', 'status': 'exists', 'value': 1000}
        item = {'id': 'example', 'capability': 'unix.file', 'status': 'exists',
                'fields': {'owner_uid': field}, 'provenance': {}}
        items = [(item, True), (dict(item, fields={'owner_uid': [field, field]}), True),
                 (dict(item, fields={'future_field': field}), True),
                 (dict(item, status='does_not_exist'), False),
                 # Frozen structural schema leaves datatype/value consistency to semantic validation.
                 (dict(item, fields={'owner_uid': dict(field, value='invalid')}), True),
                 (dict(item, fields={'owner_uid': dict(field, status='bogus')}), False)]
        req = {'item_requirement': {'items_found': 'one_or_more', 'items_satisfying': 'every'},
               'field_requirement': {'values_found': 'one_or_more', 'values_matching': 'every'},
               'fields': {'owner_uid': {'equals': 1000}}}
        requirements = [(req, True), (dict(req, fields={'future_field': {'equals': 1}}), True),
                        (dict(req, field_requirement={'values_found': 'none', 'values_matching': 'every'}), False),
                        ({'fields': req['fields']}, False), (dict(req, fields={'owner_uid': {'bogus': 1}}), False)]
        for role, vectors in [('object', objects), ('item', items), ('require', requirements)]:
            frozen = Draft202012Validator({'$ref': self.schema['$defs'][role]['$ref']}, registry=self.registry)
            proposed = Draft202012Validator({'$ref': self.schema['$id'] + '#/$defs/' + role}, registry=self.registry)
            for value, expected in vectors:
                with self.subTest(role=role, value=value):
                    original = deepcopy(value)
                    self.assertEqual(frozen.is_valid(value), expected)
                    self.assertEqual(proposed.is_valid(value), expected)
                    self.assertEqual(value, original, 'validation must not insert defaults')

    def test_item_and_require_hovers_share_all_23_schema_descriptions(self):
        fields = self.schema['$defs']['field_meanings']['properties']
        self.assertEqual(len(fields), 23)
        for name in fields:
            item = pilot.hover(self.schema, 'item', 'fields.' + name)
            require = pilot.hover(self.schema, 'require', 'fields.' + name)
            self.assertEqual(item, require)
            self.assertEqual(item['pointer'], '/$defs/field_meanings/properties/' + name)
            self.assertEqual(item['description'], fields[name]['description'])
        for name in ['filepath', 'path', 'filename', 'filesystem', 'traversal',
                     'traversal.max_depth', 'traversal.recurse']:
            self.assertTrue(pilot.hover(self.schema, 'object', name)['description'])
        for name in ['item_requirement', 'item_requirement.items_found',
                     'item_requirement.items_satisfying', 'field_requirement', 'fields']:
            self.assertTrue(pilot.hover(self.schema, 'require', name)['description'])
        with self.assertRaisesRegex(ValueError, 'No proposed description mapping'):
            pilot.hover(self.schema, 'item', 'fields.unknown')

    def test_rendered_reference_shape_and_example(self):
        text = pilot.render()
        item_table = text.split('## Collected Item')[1].split('## Require')[0]
        self.assertEqual(set(re.findall(r'^\| `([^`]+)`', item_table, re.M)), set(self.mapping['state_field_map'].values()))
        self.assertIn('| `traversal` | Controls recursive searching', text)
        self.assertIn('#### `traversal`', text)
        self.assertNotIn('in `traversal`', text)
        self.assertIn('Schema choice (`oneOf`): `object_reference`:', text)
        self.assertIn('**or** inline object', text)
        self.assertNotIn('`filepath` **or** `path` + `filename`', text)
        self.assertIn('array; entries: [typed_value]', text)
        visible = re.sub(r'\]\([^)]+\)', ']', text)
        self.assertEqual(visible.count('OVAL'), 1)
        self.assertIn('Based on the OVAL', text.split('## Sources')[1])
        blocks = re.findall(r'```yaml\n(.*?)```', text, re.S)
        self.assertEqual(len(blocks), 1)
        fragment = yaml.safe_load(blocks[0])
        Draft202012Validator({'$ref': self.schema['$defs']['object']['$ref']}, registry=self.registry).validate(fragment['object'])
        typed = Draft202012Validator({'$ref': pilot.PREFIX + 'result-types.schema.json#/$defs/typed_value'}, registry=self.registry)
        for value in fragment['fields'].values():
            typed.validate(value)
        path = ROOT / pilot.OUTPUT
        for target in re.findall(r'\]\(([^)]+)\)', text):
            if not target.startswith('https:'):
                self.assertTrue((path.parent / target.split('#')[0]).resolve().exists(), target)

    def test_schema_keywords_and_examples_are_the_rendering_authority(self):
        uri = self.schema['$defs']['object']['$ref']
        node = {'oneOf': [{'type': 'integer', 'minimum': 2}, {'const': 'bounded'}]}
        self.assertEqual(pilot.constraints(node, uri), 'oneOf(integer; minimum: 2 or value: `bounded`)')
        node = {'type': 'string', 'enum': ['alpha', 'beta'], 'default': 'beta'}
        self.assertEqual(pilot.constraints(node, uri), 'string; values: `alpha`, `beta`; default annotation: `beta`')
        for role in ['object', 'item']:
            validator = Draft202012Validator({'$ref': self.schema['$defs'][role]['$ref']}, registry=self.registry)
            for example in self.schema['$defs'][role]['examples']:
                validator.validate(example)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(ROOT / 'schema', root / 'schema')
            shutil.copytree(ROOT / pilot.PILOT, root / pilot.PILOT)
            # Metadata is audited for field identity, not used for rendered types
            # or structural alternatives. Re-pin this synthetic pack explicitly.
            file = root / 'schema/capability-mappings/supported/unix.file.json'
            mapping = json.loads(file.read_text())
            mapping['native']['field_datatypes']['owner_uid'] = ['invented']
            mapping['native']['object_selector_alternatives'] = [['invented']]
            file.write_text(json.dumps(mapping))
            source_file = root / pilot.PILOT / 'source-map.json'
            sources = json.loads(source_file.read_text())
            sources['frozen_schema_sha256'][str(file.relative_to(root))] = pilot.sha256(file.read_bytes()).hexdigest()
            source_file.write_text(json.dumps(sources))
            self.assertEqual(pilot.render(root), pilot.render())
            schema_file = root / pilot.ANNOTATIONS
            schema = json.loads(schema_file.read_text())
            schema['$defs']['object']['examples'][0]['traversal']['max_depth'] = 2
            schema_file.write_text(json.dumps(schema))
            self.assertIn('max_depth: 2', pilot.render(root))

    def test_generation_is_exact_and_rejects_stale_output(self):
        self.assertEqual((ROOT / pilot.OUTPUT).read_bytes(), pilot.render().encode())
        first = subprocess.check_output([sys.executable, str(ROOT / 'tools/generate_unix_file_reference.py'), '--hover', 'item.fields.owner_uid'])
        second = subprocess.check_output([sys.executable, str(ROOT / 'tools/generate_unix_file_reference.py'), '--hover', 'item.fields.owner_uid'])
        self.assertEqual(first, second)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(ROOT / 'schema', root / 'schema')
            shutil.copytree(ROOT / pilot.PILOT, root / pilot.PILOT)
            shutil.copytree(ROOT / 'tools', root / 'tools')
            script = root / 'tools/generate_unix_file_reference.py'
            subprocess.run([sys.executable, str(script), '--check'], check=True, capture_output=True)
            (root / pilot.OUTPUT).write_text('stale\n')
            failed = subprocess.run([sys.executable, str(script), '--check'], capture_output=True)
            self.assertEqual(failed.returncode, 1)
            subprocess.run([sys.executable, str(script)], check=True, capture_output=True)
            self.assertEqual((root / pilot.OUTPUT).read_bytes(), (ROOT / pilot.OUTPUT).read_bytes())

    def test_changed_descriptions_flow_to_output_and_mappings_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(ROOT / 'schema', root / 'schema')
            shutil.copytree(ROOT / pilot.PILOT, root / pilot.PILOT)
            target = root / pilot.ANNOTATIONS
            changed = deepcopy(self.schema)
            changed['$defs']['field_meanings']['properties']['owner_uid']['description'] = 'A revised reviewed owner identifier.'
            target.write_text(json.dumps(changed))
            self.assertIn('A revised reviewed owner identifier.', pilot.render(root))
            for mode in ['missing', 'unknown', 'missing_description']:
                changed = deepcopy(self.schema)
                fields = changed['$defs']['field_meanings']['properties']
                if mode == 'missing':
                    del fields['owner_uid']
                elif mode == 'unknown':
                    fields['invented'] = {'description': 'Must not appear.'}
                else:
                    del fields['owner_uid']['description']
                target.write_text(json.dumps(changed))
                with self.assertRaisesRegex(ValueError, 'Missing or unknown'):
                    pilot.render(root)
            target.write_text(json.dumps(self.schema))
            native = root / 'schema/capability-common.schema.json'
            native.write_bytes(native.read_bytes() + b'\n')
            with self.assertRaisesRegex(ValueError, 'Frozen schema pack differs'):
                pilot.load_schemas(root)


if __name__ == '__main__':
    unittest.main()
