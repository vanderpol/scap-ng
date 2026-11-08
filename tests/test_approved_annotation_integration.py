"""Approved next-version descriptions remain sourced from actual schema nodes."""
from copy import deepcopy
import json
import os
import subprocess
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import generate_approved_annotation_pilot as pilot
from schema_documentation import SchemaStore, description_lookup, pointer


class ApprovedAnnotationIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.store, cls.sources = pilot.load()

    def copy_inputs(self, root):
        shutil.copytree(ROOT / 'schema', root / 'schema')
        shutil.copytree(ROOT / 'docs/research/issue40', root / 'docs/research/issue40')
        shutil.copytree(ROOT / pilot.DEST, root / pilot.DEST)
        shutil.copytree(ROOT / 'examples', root / 'examples')

    def test_bounded_selection_only_uses_approved_rows_and_keeps_validation(self):
        result, sources, proposed, expected, witnesses = pilot.proposal()
        self.assertEqual(len(sources['entries']), 8)
        self.assertEqual(len(sources['resource_routes']), 5)
        self.assertEqual(len(witnesses), 17)
        self.assertFalse(sources['production_installation_authorized'])
        self.assertEqual(len(sources['native_file_hashes']), 145)
        # Independently compare before/after assertions without trusting the builder.
        def assertions(node):
            if isinstance(node, list):
                return [assertions(v) for v in node]
            if not isinstance(node, dict):
                return node
            return {k: assertions(v) for k, v in node.items() if k not in {'description', '$id'}}
        inverse = {new: old for old, new in sources['resource_routes'].items()}
        for old, new in sources['resource_routes'].items():
            self.assertEqual(assertions(pilot.remap(proposed[new], new, inverse)),
                             assertions(pilot.remap(result['documents'][old], old, {})))
        self.assertTrue(any(c['expected_valid'] for c in witnesses))
        self.assertTrue(any(not c['expected_valid'] for c in witnesses))

    def test_reference_and_offline_help_share_actual_annotation_pointers(self):
        output = pilot.render(self.store, self.sources)
        offline = json.loads(output['offline-help.json'])
        self.assertFalse(offline['live_vscode_ui_verified'])
        for source, help_row in zip(self.sources['entries'], offline['entries']):
            found = description_lookup(self.store, source['help_route'])
            self.assertEqual(help_row['description_pointer'], source['new_pointer'])
            self.assertEqual(help_row['description'], self.store.node(source['new_pointer']))
            self.assertIn(help_row['description'], output['REFERENCE.md'])
            self.assertEqual(found['description'], help_row['description'])
        inputs = next(r for r in offline['entries'] if r['name'] == 'input-reference')
        self.assertEqual(len(inputs['lookup_chain']), 3)  # route -> use -> shared owner
        outcomes = self.store.node(pilot.NEXT + 'result-types.schema.json#/$defs/technical_outcome')['enum']
        self.assertEqual(outcomes, ['true', 'false', 'error', 'unknown', 'not_evaluated', 'not_applicable'])
        for value in outcomes:
            self.assertIn('`' + value + '`', output['REFERENCE.md'])

    def test_changed_schema_sentence_flows_to_both_outputs_without_a_prose_model(self):
        docs = deepcopy(self.store.documents)
        source = self.sources['entries'][0]
        uri, fragment = source['new_pointer'].split('#')
        parent = pointer(docs[uri], fragment.rsplit('/', 1)[0])
        parent['description'] = 'Synthetic replacement for propagation test.'
        changed = SchemaStore(docs)
        output = pilot.render(changed, self.sources)
        self.assertIn(parent['description'], output['REFERENCE.md'])
        self.assertEqual(json.loads(output['offline-help.json'])['entries'][0]['description'], parent['description'])
        del parent['description']
        with self.assertRaisesRegex(ValueError, 'Missing description'):
            pilot.render(SchemaStore(docs), self.sources)

    def test_all_proposal_refs_resolve_without_network_and_unknown_routes_fail(self):
        self.assertTrue(description_lookup(self.store, self.sources['entries'][3]['help_route']))
        with self.assertRaisesRegex(ValueError, 'Outside pinned local schema pack'):
            description_lookup(self.store, 'https://unavailable.invalid/missing.schema.json')
        cyclic = {'$schema': 'https://json-schema.org/draft/2020-12/schema', '$id': 'urn:cycle', '$ref': 'urn:cycle'}
        with self.assertRaisesRegex(ValueError, 'Cyclic description'):
            description_lookup(SchemaStore({'urn:cycle': cyclic}), 'urn:cycle')

    def test_check_is_exact_byte_read_only_and_rejects_stale_generated_artifacts(self):
        for name, content in pilot.render(self.store, self.sources).items():
            self.assertEqual((ROOT / pilot.DEST / name).read_bytes(), content.encode())
        for seed in ['1', '42']:
            checked = subprocess.run([sys.executable, str(ROOT / 'tools/generate_approved_annotation_pilot.py'), '--check'],
                                     env=dict(os.environ, PYTHONHASHSEED=seed), capture_output=True, text=True)
            self.assertEqual(checked.returncode, 0, checked.stderr)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); self.copy_inputs(root)
            before = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*') if p.is_file()}
            self.assertEqual(pilot.main(['--check'], root), 0)
            self.assertEqual(before, {str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*') if p.is_file()})
            for name in ['REFERENCE.md', 'offline-help.json', 'source-map.json']:
                path = root / pilot.DEST / name
                original = path.read_bytes(); path.write_text('stale\n')
                self.assertEqual(pilot.main(['--check'], root), 1)
                path.write_bytes(original)

    def test_stale_or_missing_descriptions_and_changed_assertions_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); self.copy_inputs(root)
            source = self.sources['entries'][0]
            path = root / source['fixture_file']
            original = json.loads(path.read_text())
            for change in ['missing', 'unapproved', 'assertion']:
                doc = deepcopy(original)
                node = pointer(doc, '/$defs/input_reference')
                if change == 'missing':
                    node.pop('description')
                elif change == 'unapproved':
                    node['description'] = 'Unreviewed change.'
                else:
                    node['required'] = []
                path.write_text(pilot.encode(doc))
                with self.assertRaisesRegex(ValueError, 'Missing/stale proposed'):
                    pilot.load(root)
            path.write_text(pilot.encode(original))
            selection_file = root / pilot.DEST / 'selection.json'
            selection = json.loads(selection_file.read_text())
            selection['entries'][0].update(batch='editorial-batch-2.json', case='07')
            selection_file.write_text(pilot.encode(selection))
            with self.assertRaisesRegex(ValueError, 'semantic hold'):
                pilot.load(root)


if __name__ == '__main__':
    unittest.main()
