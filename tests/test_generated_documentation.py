"""Generated docs and OVAL lineage are deterministic, gap-aware and auditable."""

import json
from pathlib import Path
import sys
import tempfile
import unittest


PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / 'tools'))
from generate_docs import generated_documents, render_developer_pilot, verify_documents  # noqa: E402


class DocumentationDriftTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.docs = generated_documents()

    def test_published_documentation_matches_exactly(self):
        self.assertEqual(verify_documents(self.docs, PROJECT / 'docs' / 'generated'), {})

    def test_tampered_documentation_fails_the_gate(self):
        with tempfile.TemporaryDirectory(prefix='scapng-doc-drift-') as temp:
            directory = Path(temp)
            for filename, content in self.docs.items():
                (directory / filename).write_text(content, encoding='utf-8')
            self.assertEqual(verify_documents(self.docs, directory), {})
            filename = 'scanner-implementation-catalog.md'
            (directory / filename).write_text('stale scanner instructions\n',
                                             encoding='utf-8')
            self.assertEqual(set(verify_documents(self.docs, directory)), {filename})

    def test_every_capability_has_a_scanner_implementation_section(self):
        catalog = self.docs['scanner-implementation-catalog.md']
        capabilities = [path.stem for path in
                        (PROJECT / 'schema' / 'capability-mappings').rglob('*.json')]
        self.assertEqual(len(capabilities), 104)
        for name in capabilities:
            with self.subTest(capability=name):
                self.assertEqual(catalog.count(f'### {name}\n'), 1)
        self.assertIn('**Implementation steps:** Not yet reviewed/documented.', catalog)

    def test_oval_field_lineage_is_complete_but_not_normative(self):
        audit = json.loads((PROJECT / 'docs' / 'metadata' /
                            'windows.ntuser-oval-audit.json').read_text())
        notes = json.loads((PROJECT / 'docs' / 'metadata' /
                            'windows.ntuser-source-notes.json').read_text())
        mapping = json.loads((PROJECT / 'schema' / 'capability-mappings' /
                              'supported' / 'windows.ntuser.json').read_text())
        native_fields = set(mapping['native']['state_field_map'])
        self.assertEqual(len(native_fields), 15)
        self.assertEqual(native_fields, set(notes['fields']))
        for node in ('ntuser_item', 'ntuser_state'):
            self.assertEqual(native_fields, set(audit['nodes'][node]['fields']))
        self.assertEqual(notes['review_status'], 'pending_native_equivalence_review')
        self.assertIn('Legacy review status:', self.docs['scanner-windows-ntuser.md'])

    def test_platform_pilots_remain_separate_and_non_normative(self):
        expected = {
            'windows': ('windows.registry', 'unix.file'),
            'unix': ('unix.file', 'windows.registry'),
            'independent': ('independent.shellcommand', 'windows.registry'),
        }
        for platform, (included, excluded) in expected.items():
            with self.subTest(platform=platform):
                page = self.docs[f'developer-guide-{platform}-pilot.md']
                self.assertIn(f'## {included}\n', page)
                self.assertNotIn(f'## {excluded}\n', page)
                self.assertIn('Proposal only:', page)
                self.assertIn('Pending research', page)
                self.assertIn('not yet qualified', page)

    def test_pilot_annotations_cannot_invent_capability_fields(self):
        proposal = json.loads((PROJECT / 'docs' / 'metadata' /
                               'schema-documentation-pilot.json').read_text())
        mapping_paths = sorted((PROJECT / 'schema' / 'capability-mappings' /
                                'supported').glob('*.json'))
        mappings = [('supported', path, json.loads(path.read_text()))
                    for path in mapping_paths]
        proposal['capabilities']['windows.registry']['properties']['not_a_field'] = {
            'description': 'bad',
            'x-scap-ng-scanner': {'documentation_status': 'partial',
                                  'known_contract': 'unknown',
                                  'open_question': 'unknown'}
        }
        with self.assertRaisesRegex(ValueError, 'not_a_field'):
            render_developer_pilot('0.4.0', mappings, proposal)


if __name__ == '__main__':
    unittest.main()
