"""Issue #43 Phase A: one pinned, acceptance-preserving documentation pack."""
from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import generate_review_documentation_pack as pack
from schema_documentation import SchemaStore, description_lookup
from schema_documentation_pack import load_pack, resolve_help


class ReviewDocumentationPack(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.store, cls.provenance, cls.core, cls.pins = pack.build()
        cls.output = pack.outputs(cls.store, cls.provenance, cls.core, cls.pins)
        cls.metadata = json.loads(cls.output['editor-metadata.json'])
        cls.pin = sha256(cls.output['manifest.json'].encode()).hexdigest()

    def test_one_namespace_exact_resources_and_independent_export_loader(self):
        self.assertEqual(len(self.store.documents), 36)
        self.assertEqual(len(self.core), 8)
        self.assertEqual(len(self.metadata['entries']), 68)
        for uri in self.store.documents:
            self.assertTrue(uri.startswith(pack.PREFIX))
        with tempfile.TemporaryDirectory() as directory:
            dest = Path(directory) / 'pack'
            shutil.copytree(ROOT / pack.DEST, dest)
            # No checkout, historical sources, prior proposal namespaces or network.
            store, metadata = load_pack(dest, self.pin)
            self.assertEqual(store.documents, self.store.documents)
            self.assertEqual(metadata, self.metadata)
        manifest = json.loads(self.output['manifest.json'])
        self.assertTrue(manifest['review_only'])
        self.assertIsNone(manifest['release_version'])
        self.assertFalse(manifest['live_vscode_ui_verified'])
        self.assertEqual(manifest['source_commits'], pack.COMMITS)

    def test_all_independent_vectors_retain_expected_before_after_acceptance(self):
        evidence = self.provenance['validation_evidence']
        self.assertEqual(len(evidence), 157)
        self.assertEqual({e['native_valid'] for e in evidence}, {True, False})
        for row in evidence:
            self.assertEqual(row['native_valid'], row['expected_valid'], row['name'])
            self.assertEqual(row['review_pack_valid'], row['expected_valid'], row['name'])
        self.assertEqual(len(self.provenance['structural_parity']), 35)
        for row in self.provenance['structural_parity']:
            self.assertEqual(row['normalized_restored_sha256'], row['normalized_native_sha256'])

    def test_pr39_tightening_is_not_installed(self):
        candidate = json.loads((ROOT / pack.SOURCE).read_text())
        native = {}
        for path in (ROOT / 'schema').glob('*.schema.json'):
            doc = json.loads(path.read_text()); native[doc['$id']] = doc
        proposed = SchemaStore(dict(native, **{candidate['$id']: candidate}))
        before = Draft202012Validator({'$ref': 'https://scap-ng.dev/schema/v0.4.1/collected-item.schema.json'}, registry=SchemaStore(native).registry)
        prior = Draft202012Validator({'$ref': candidate['$id'] + '#/$defs/item'}, registry=proposed.registry)
        review = Draft202012Validator({'$ref': pack.PREFIX + 'collected-item.schema.json'}, registry=self.store.registry)
        for payload in ['not-an-integer', 1.5, True]:
            item = {'id': 'example', 'capability': 'unix.file', 'status': 'exists', 'provenance': {},
                    'fields': {'owner_uid': {'datatype': 'integer', 'status': 'exists', 'value': payload}}}
            self.assertTrue(before.is_valid(item))
            self.assertFalse(prior.is_valid(item))
            self.assertTrue(review.is_valid(item))
        # No capability-specific tag/value definitions were brought into Phase A.
        cap = self.store.documents[pack.CAP]
        self.assertFalse(any(name.startswith(('value_', 'datatype_')) for name in cap['$defs']))

    def test_shared_authority_nested_traversal_and_parent_cardinality(self):
        for row in self.metadata['entries']:
            found = resolve_help(self.store, row['capability'], row['role'], row['field'], self.metadata)
            self.assertEqual(found['description'], self.store.node(row['description_pointer']))
        item_rows = [r for r in self.metadata['entries'] if r['role'] == 'item']
        self.assertEqual(len(item_rows), 23)
        for item in item_rows:
            req = next(r for r in self.metadata['entries'] if r['role'] == 'require' and r['field'] == item['field'])
            self.assertEqual(item['description_pointer'], req['description_pointer'])
            self.assertEqual(item['description'], req['description'])
        depth = next(r for r in self.metadata['entries'] if r['field'] == 'traversal.max_depth')
        self.assertEqual(depth['occurrences'], '1..1')
        fields = next(r for r in self.metadata['entries'] if r['role'] == 'require' and r['field'] == 'fields')
        self.assertEqual(fields['occurrences'], 'conditional')
        pair = next(r for r in self.metadata['entries'] if r['field'] == 'field_requirement.values_found')
        self.assertNotIn('`none`', pair['options'])

    def test_semantic_holds_and_foreach_remain_unimported(self):
        holds = self.provenance['held_proposals_excluded']
        self.assertEqual(holds['editorial-batch.json'], ['15', '16', '17', '18', '21', '26', '28'])
        self.assertEqual(holds['editorial-batch-2.json'], ['07', '16', '17'])
        for name, ids in holds.items():
            batch = json.loads((ROOT / pack.audit.DEST / name).read_text())
            for row in batch['proposals']:
                if row['id'] in ids:
                    self.assertEqual(row['semantic_status'], 'pending_semantic_review')
                    # The held rows are retained only in the historical
                    # worksheet; no row may enter the generated help routes.
                    self.assertFalse(any(e.get('source_pointer', '').endswith('/' + row['id'])
                                         for e in self.provenance['annotations']))
        self.assertFalse(any('foreach' in r['field'] for r in self.metadata['entries']))

    def test_schema_mutation_drives_all_generated_help_without_sidecar_prose(self):
        documents = deepcopy(self.store.documents)
        owner = documents[pack.CAP]['$defs']['field_meanings']['properties']['owner_uid']
        owner['description'] = 'Synthetic description mutation.'
        changed = pack.outputs(SchemaStore(documents), self.provenance, self.core, self.pins)
        for name in ['reference.md', 'constraints.md', 'editor-metadata.json']:
            self.assertIn(owner['description'], changed[name])
        del owner['description']
        with self.assertRaisesRegex(ValueError, 'Missing description'):
            pack.outputs(SchemaStore(documents), self.provenance, self.core, self.pins)

    def test_loader_rejects_missing_resources_stale_hashes_and_wrong_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            dest = Path(directory) / 'pack'; shutil.copytree(ROOT / pack.DEST, dest)
            with self.assertRaisesRegex(ValueError, 'external pin'):
                load_pack(dest, '0' * 64)
            with self.assertRaisesRegex(ValueError, 'external immutable'):
                load_pack(dest, '')
            path = dest / 'schemas/capabilities/unix.file.schema.json'
            raw = path.read_bytes(); path.unlink()
            with self.assertRaisesRegex(ValueError, 'Missing/outside'):
                load_pack(dest, self.pin)
            path.write_bytes(raw + b' ')
            with self.assertRaisesRegex(ValueError, 'resource hash'):
                load_pack(dest, self.pin)
            path.write_bytes(raw)
            metadata = dest / 'editor-metadata.json'; metadata.write_text('{}')
            with self.assertRaisesRegex(ValueError, 'Generated pack file hash'):
                load_pack(dest, self.pin)

    def test_unknown_or_wrong_capability_role_and_schema_origin_fail(self):
        for capability, role, field in [('windows.file', 'item', 'fields.owner_uid'), ('unix.file', 'object', 'owner_uid'), ('unix.file', 'object', 'traversal.unknown')]:
            with self.assertRaisesRegex(ValueError, 'Unknown or ambiguous'):
                resolve_help(self.store, capability, role, field, self.metadata)
        wrong = deepcopy(self.metadata)
        wrong['entries'][0]['schema_pointer'] = pack.PREFIX + 'result-types.schema.json#/$defs/technical_outcome'
        row = wrong['entries'][0]
        with self.assertRaisesRegex(ValueError, 'Stale or misrouted'):
            resolve_help(self.store, row['capability'], row['role'], row['field'], wrong)

    def test_byte_reproduction_hash_seed_stability_and_pack_source_links(self):
        for name, text in self.output.items():
            self.assertEqual((ROOT / pack.DEST / name).read_bytes(), text.encode(), name)
        for seed in ['7', '93']:
            result = subprocess.run([sys.executable, str(ROOT / 'tools/generate_review_documentation_pack.py'), '--check'], env=dict(os.environ, PYTHONHASHSEED=seed), capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
        for row in self.metadata['entries']:
            self.assertTrue((ROOT / pack.resource_file(row['description_pointer'].split('#')[0])).exists())


if __name__ == '__main__':
    unittest.main()
