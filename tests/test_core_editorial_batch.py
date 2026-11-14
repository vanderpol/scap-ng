"""Owner-requested small wording review: no bulk/canonical annotation changes."""
from copy import deepcopy
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import audit_schema_documentation as audit


class CoreEditorialBatch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Editorial Issue #40 is immutable 0.4.0 history; its review notes
        # intentionally do not point into the active 0.4.1 schema family.
        cls._archive = audit.historical_workspace(ROOT)
        cls.historical_root = cls._archive.__enter__()
        try:
            shutil.copytree(ROOT / audit.HISTORICAL_DEST,
                            cls.historical_root / audit.HISTORICAL_DEST,
                            dirs_exist_ok=True)
            cls.result = audit.audit(cls.historical_root, active=False)
            cls.batch, cls.checked = audit.editorial_batch(cls.result)
        except BaseException:
            cls._archive.__exit__(*sys.exc_info())
            raise

    @classmethod
    def tearDownClass(cls):
        cls._archive.__exit__(None, None, None)

    def temporary_batch(self, root, batch):
        shutil.copytree(self.historical_root / 'schema', root / 'schema')
        (root / audit.DEST).mkdir(parents=True)
        (root / audit.DEST / 'editorial-batch.json').write_text(json.dumps(batch))
        shutil.copytree(self.historical_root / 'examples', root / 'examples')

    def test_bounded_diverse_sheet_has_separate_author_and_engineering_fields(self):
        rows = self.batch['proposals']
        self.assertEqual(len(rows), 28)
        self.assertEqual(sum(r['author_description'] is not None for r in rows), 27)
        self.assertGreaterEqual(self.checked, 50)
        required = {'functions', 'Require', 'evaluation', 'variables', 'references', 'results', 'document roots'}
        self.assertLessEqual(required, {r['category'] for r in rows})
        for row in rows:
            self.assertTrue(row['engineering_note'])
            self.assertTrue(row['codex_proposal'])
            self.assertIn(row['editorial_status'], {'accepted_as_written', 'accepted_with_revision', 'draft_style_acceptable_semantic_hold', 'withheld'})
            if row['author_description']:
                self.assertNotEqual(row['author_description'], row['engineering_note'])
                self.assertLessEqual(len(re.findall(r'[.!?](?:\s|$)', row['author_description'])), 2)
        self.assertFalse(self.batch['workflow']['canonical_installation_authorized'])

    def test_batch_1_receipt_preserves_exact_owner_dispositions_and_source_dossier(self):
        from collections import Counter
        counts = Counter(r['editorial_status'] for r in self.batch['proposals'])
        self.assertEqual(dict(counts), {'accepted_as_written': 18, 'accepted_with_revision': 3,
                                     'draft_style_acceptable_semantic_hold': 6, 'withheld': 1})
        for row in self.batch['proposals']:
            self.assertEqual(row['editorial_review_url'], self.batch['review_receipt']['review_url'])
        for mutation in ['status', 'note', 'approval']:
            batch = deepcopy(self.batch)
            if mutation == 'status':
                batch['proposals'][14]['editorial_status'] = 'accepted_as_written'
            elif mutation == 'note':
                batch['proposals'][0]['engineering_note'] += ' Edited after review.'
            else:
                batch['review_receipt']['authorization_url'] = 'https://example.invalid/approval'
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory); self.temporary_batch(root, batch)
                with self.assertRaisesRegex(ValueError, 'receipt|source dossier'):
                    audit.editorial_batch(self.result, root)

    def test_batch_2_receipt_is_distinct_diverse_and_reproducible(self):
        batch, checked = audit.editorial_batch(self.result, filename='editorial-batch-2.json')
        self.assertEqual(len(batch['proposals']), 28)
        self.assertEqual(checked, 56)
        previous = {(r['schema_uri'], r['pointer']) for r in self.batch['proposals']}
        self.assertFalse(previous & {(r['schema_uri'], r['pointer']) for r in batch['proposals']})
        self.assertEqual(sum(r['classification'] == 'semantic_decision_needed' for r in batch['proposals']), 3)
        for row in batch['proposals']:
            expected = ('draft_style_acceptable_semantic_hold' if row['id'] in {'07', '16', '17'} else
                        'accepted_with_revision' if row['id'] in {'06', '18', '19'} else 'accepted_as_written')
            self.assertEqual(row['editorial_status'], expected)
            self.assertEqual(row['proposed_description_owner'], row['schema_uri'] + '#' + row['pointer'])
            self.assertGreaterEqual(len(row['checks']), 2)
            self.assertEqual({c['expected_valid'] for c in row['checks']}, {True, False})
        sheet = audit.editorial_report(self.result, filename='editorial-batch-2.json')
        self.assertEqual((ROOT / audit.DEST / 'EDITORIAL-REVIEW-2.md').read_text(), sheet)
        for row in batch['proposals']:
            for field in ['author_description', 'engineering_note', 'codex_proposal']:
                self.assertIn(row[field], sheet)
        from collections import Counter
        self.assertEqual(Counter(r['editorial_status'] for r in batch['proposals']),
                         {'accepted_as_written': 22, 'accepted_with_revision': 3, 'draft_style_acceptable_semantic_hold': 3})
        batch['proposals'][6]['editorial_status'] = 'accepted_as_written'
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); self.temporary_batch(root, self.batch)
            (root / audit.DEST / 'editorial-batch-2.json').write_text(json.dumps(batch))
            with self.assertRaisesRegex(ValueError, 'receipt'):
                audit.editorial_batch(self.result, root, 'editorial-batch-2.json')

    def test_existing_and_codex_wording_are_exactly_traceable(self):
        prior = {r['id']: r for r in self.result['crosswalk']}
        for row in self.batch['proposals']:
            node = self.result['store'].node(row['schema_uri'] + '#' + row['pointer'])
            self.assertEqual(row['existing_wording'], node.get('description'))
            self.assertEqual(row['source_sha256'], audit.sha256((self.historical_root / row['schema_file']).read_bytes()).hexdigest())
            origin = row['codex_proposal_source']
            if origin['kind'] == 'phase1_crosswalk':
                self.assertEqual(row['codex_proposal'], prior[origin['proposal_id']]['proposed_description'])
                self.assertEqual(origin['commit'], self.batch['phase1_commit'])
            else:
                self.assertEqual(origin['kind'], 'new_bounded_draft_from_pinned_native_sources')

    def test_engineering_caveats_and_filler_cannot_be_published_as_author_help(self):
        for candidate in ['This schema structurally accepts a value.', 'The input_reference field.']:
            batch = deepcopy(self.batch)
            batch['proposals'][0]['author_description'] = candidate
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory); self.temporary_batch(root, batch)
                with self.assertRaisesRegex(ValueError, 'Engineering/status|short one/two-sentence'):
                    audit.editorial_batch(self.result, root)
        batch = deepcopy(self.batch)
        batch['workflow']['canonical_installation_authorized'] = True
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); self.temporary_batch(root, batch)
            with self.assertRaisesRegex(ValueError, 'authorize canonical'):
                audit.editorial_batch(self.result, root)

    def test_foreach_stays_withheld_and_semantic_decisions_remain_pending(self):
        row = next(r for r in self.batch['proposals'] if r['element'] == 'foreach_binding')
        self.assertIsNone(row['author_description'])
        self.assertTrue(row['withheld'])
        for entry in self.batch['proposals']:
            if entry['classification'] == 'semantic_decision_needed':
                self.assertEqual(entry['semantic_status'], 'pending_semantic_review')
        batch = deepcopy(self.batch)
        row = next(r for r in batch['proposals'] if r['element'] == 'foreach_binding')
        row.update(author_description='Iterates over selected Items.', withheld=False)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); self.temporary_batch(root, batch)
            with self.assertRaisesRegex(ValueError, 'Unreachable helper'):
                audit.editorial_batch(self.result, root)

    def test_context_witnesses_do_not_confuse_leaf_acceptance_with_parent_rules(self):
        found = next(r for r in self.batch['proposals'] if r['element'] == 'values_found')
        self.assertTrue(any(c['schema_uri'].endswith('#/$defs/paired_requirement') and not c['expected_valid'] for c in found['checks']))
        provision = next(r for r in self.batch['proposals'] if r['element'] == 'input_provided')
        self.assertTrue(any(not c['expected_valid'] and c['instance'] == {'input_provided': 'example-input'} for c in provision['checks']))
        regex = next(r for r in self.batch['proposals'] if r['element'] == 'regex_capture')
        self.assertTrue(any(c['expected_valid'] and c['instance'].get('pattern') == '.*' for c in regex['checks']))
        typed = next(r for r in self.batch['proposals'] if r['element'] == 'typed_value.value')
        self.assertTrue(any(c['expected_valid'] and c['instance'].get('value') == 'not-an-integer' for c in typed['checks']))
        # Changing the expected outcome must fail rather than silently bless text.
        batch = deepcopy(self.batch); batch['proposals'][0]['checks'][0]['expected_valid'] = False
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); self.temporary_batch(root, batch)
            with self.assertRaisesRegex(ValueError, 'syntax witness disagrees'):
                audit.editorial_batch(self.result, root)

    def test_generated_sheet_contains_every_case_and_changes_no_bulk_patch(self):
        sheet = audit.editorial_report(self.result)
        self.assertEqual((ROOT / audit.DEST / 'EDITORIAL-REVIEW.md').read_bytes(), sheet.encode())
        for row in self.batch['proposals']:
            self.assertIn('<a id="case-' + row['id'] + '"></a>', sheet)
            self.assertIn(row['schema_uri'] + '#' + row['pointer'], sheet)
            if row['author_description']:
                self.assertIn(row['author_description'], sheet)
            self.assertIn(row['engineering_note'], sheet)
        before = {p.name: audit.sha256(p.read_bytes()).hexdigest() for p in (ROOT / audit.DEST).glob('*') if p.is_file()}
        output = audit.artifacts(audit.audit(self.historical_root, active=False))
        self.assertIn('EDITORIAL-REVIEW.md', output)
        for name in ['inventory.jsonl', 'gaps.jsonl', 'crosswalk.jsonl', 'proposed-annotations.patch.json', 'PILOTS.md']:
            self.assertEqual(before[name], audit.sha256(output[name].encode()).hexdigest())
        self.assertTrue(all(g['status'] == 'open' for g in self.result['findings']))
        self.assertTrue(all(p['disposition'] == 'pending' for p in self.result['crosswalk']))


if __name__ == '__main__':
    unittest.main()
