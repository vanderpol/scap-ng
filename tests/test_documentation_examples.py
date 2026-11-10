from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

import yaml
from jsonschema import ValidationError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import documentation_examples as examples
import generate_documentation as reference
import documentation_artifacts as artifacts
import check_documentation_examples as checks


class PairedDocumentationExamples(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.docs = reference.schemas()
        cls.selected = {d['x-doc-capability']: d for d, _ in cls.docs.values() if 'x-doc-examples' in d}
        cls.loader = examples.Examples(ROOT)
        cls.cases = {cap: cls.loader.load(doc) for cap, doc in cls.selected.items()}

    def test_exact_first_five_capabilities_and_ten_self_contained_cases(self):
        self.assertEqual(set(self.cases), {'unix.file', 'windows.registry', 'independent.shellcommand', 'linux.rpminfo', 'windows.service'})
        self.assertEqual(sum(map(len, self.cases.values())), 10)
        for cap, cases in self.cases.items():
            self.assertEqual([c['expected']['label'] for _, c in cases], ['Pass', 'Fail'])
            self.assertEqual(cases[0][1]['assessment'], cases[1][1]['assessment'])
            for _, case in cases:
                test = next(iter(case['assessment']['tests'].values()))
                self.assertTrue(test['object']); self.assertTrue(test['require'])
                self.assertEqual(case['collection_result']['status'], 'complete')
                self.assertEqual(len(case['collected_items']), 1)
                self.assertIn('does not match' if case['expected']['label'] == 'Fail' else 'matches', case['explanation'])

    def test_validation_report_does_not_manufacture_observed_results(self):
        report = checks.report()
        self.assertEqual(report['totals'], {'capabilities':5, 'examples':10, 'syntax_valid':10, 'native_verified':0, 'native_unverified':10})
        for case in report['cases']:
            self.assertIsNone(case['observed_technical_outcome'])
            self.assertEqual(case['native_evaluation'], 'not_run')
        self.assertEqual(report, json.loads((ROOT / checks.DEST).read_text()))

    def test_quality_findings_quote_exact_pinned_source_annotations(self):
        report = json.loads((ROOT / 'docs/examples/oval-documentation-quality.json').read_text())
        source = json.loads((ROOT / 'docs/fidelity/source-documentation.json').read_text())
        self.assertEqual(len(report['findings']), 9)
        self.assertEqual({r['category'] for r in report['findings']}, set(report['categories']))
        docs = {(d['file'], d['xpath']): d for d in source['documents'].values()}
        for finding in report['findings']:
            for key in ['source', 'comparison_source']:
                if key not in finding: continue
                quote = finding[key]
                file = source['files']['5.12.3/' + Path(quote['file']).name]
                self.assertEqual(quote['file_sha256'], file['sha256'])
                self.assertEqual(quote['commit'], file['commit'])
                if quote['quote']:
                    self.assertEqual(docs[(quote['file'], quote['xpath'])]['text'], quote['quote'])
                else:
                    self.assertEqual(finding['id'], 'registry-overview')

    def mutate(self, cap, change):
        tmp = tempfile.TemporaryDirectory(); self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        shutil.copytree(ROOT / 'schema', root / 'schema')
        doc = deepcopy(self.selected[cap])
        for ref in [doc['x-doc-examples']['pin'], *doc['x-doc-examples']['cases']]:
            target = root / ref['path']; target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((ROOT / ref['path']).read_bytes())
        ref = doc['x-doc-examples']['cases'][0]
        data = yaml.safe_load((root / ref['path']).read_text())
        change(data)
        raw = yaml.safe_dump(data, sort_keys=False).encode()
        (root / ref['path']).write_bytes(raw); ref['sha256'] = sha256(raw).hexdigest()
        return root, doc

    def test_missing_require_is_a_schema_rejection_not_an_evaluation(self):
        def change(c): next(iter(c['assessment']['tests'].values())).pop('require')
        root, doc = self.mutate('unix.file', change)
        with self.assertRaises(ValidationError): examples.Examples(root).load(doc)

    def test_wrong_capability_and_unlinked_items_are_rejected(self):
        for change in [lambda c: c.update(capability='windows.service'),
                       lambda c: c['collection_result'].update(item_refs=['wrong-id'])]:
            root, doc = self.mutate('unix.file', change)
            with self.assertRaises(ValueError): examples.Examples(root).load(doc)

    def test_unknown_fields_and_mistyped_payload_are_fixture_errors(self):
        for change in [lambda c: c['collected_items'][0]['fields'].update(misspelled={'datatype':'integer','status':'exists','value':0}),
                       lambda c: c['collected_items'][0]['fields']['owner_uid'].update(value='0')]:
            root, doc = self.mutate('unix.file', change)
            with self.assertRaises(ValueError): examples.Examples(root).load(doc)
        # The frozen schema intentionally has a broad payload shape. Our example
        # qualification does not change that acceptance or claim runtime typing.
        root, doc = self.mutate('unix.file', lambda c: c['collected_items'][0]['fields']['owner_uid'].update(value='0'))
        case = yaml.safe_load((root / doc['x-doc-examples']['cases'][0]['path']).read_text())
        examples.Examples(root).validate('collected-item', case['collected_items'][0])

    def test_missing_stale_pins_and_fabricated_proof_are_rejected(self):
        root, doc = self.mutate('unix.file', lambda c: None)
        (root / doc['x-doc-examples']['pin']['path']).unlink()
        with self.assertRaises(FileNotFoundError): examples.Examples(root).load(doc)
        root, doc = self.mutate('unix.file', lambda c: None)
        doc['x-doc-examples']['cases'][0]['sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'Stale example'): examples.Examples(root).load(doc)
        root, doc = self.mutate('unix.file', lambda c: c['verification'].update(status='proven'))
        with self.assertRaisesRegex(ValueError, 'separately reviewed receipt'): examples.Examples(root).load(doc)

    def test_rendered_fragments_are_exactly_derived_from_complete_fixtures(self):
        for cap, cases in self.cases.items():
            page = examples.render(cases)
            blocks = [yaml.safe_load(t) for t in re.findall(r'```yaml\n(.*?)\n```', page, re.S)]
            assessment = cases[0][1]['assessment']
            self.assertEqual(blocks[0], {k: assessment[k] for k in ['tests','evaluate']})
            for block, (ref, case) in zip(blocks[1:], cases):
                self.assertEqual(block, {k: case[k] for k in ['collection_result','collected_items']})
                self.assertIn(ref['path'], page)
            self.assertIn('native evaluation unverified', page)

    def test_changed_fixture_reaches_page_and_editor_links_without_renderer_changes(self):
        root, doc = self.mutate('unix.file', lambda c: c.update(explanation='Changed canonical fixture explanation.'))
        selected = examples.Examples(root).load(doc)
        self.assertIn('Changed canonical fixture explanation.', examples.render(selected))
        output = reference.generate()
        help_data = json.loads(output[reference.DEST / 'editor-help.json'])
        self.assertEqual(len(help_data['examples']), 10)
        manifest = json.loads(output[reference.DEST / 'manifest.json'])
        self.assertEqual(len(manifest['examples']), 11)
        self.assertEqual({r['path'] for r in help_data['examples']}, {r['path'] for r in self.loader.routes})

    def test_offline_transport_rejects_stale_example_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for relative in ['proposed-schema/documentation', 'docs/reference', 'examples/paired']:
                shutil.copytree(ROOT / relative, root / relative)
            manifest = root / reference.DEST / 'manifest.json'
            pin = sha256(manifest.read_bytes()).hexdigest()
            artifacts.load(root, pin)
            path = root / self.cases['unix.file'][0][0]['path']
            path.write_text(path.read_text() + '\n# stale change\n')
            with self.assertRaisesRegex(ValueError, 'Stale documentation resource'): artifacts.load(root, pin)

    def test_offline_transport_rejects_wrong_example_associations_even_with_rehashed_pack(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for relative in ['proposed-schema/documentation', 'docs/reference', 'examples/paired']:
                shutil.copytree(ROOT / relative, root / relative)
            help_path = root / reference.DEST / 'editor-help.json'
            data = json.loads(help_path.read_text())
            data['examples'][0]['capability'] = 'wrong.capability'
            help_path.write_text(json.dumps(data))
            manifest_path = root / reference.DEST / 'manifest.json'
            manifest = json.loads(manifest_path.read_text())
            manifest['generated'][str(reference.DEST / 'editor-help.json')] = sha256(help_path.read_bytes()).hexdigest()
            manifest_path.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, 'Incorrect example help association'):
                artifacts.load(root, sha256(manifest_path.read_bytes()).hexdigest())
            manifest['examples'].pop(next(iter(manifest['examples'])))
            manifest_path.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, 'Unbound example source'):
                artifacts.load(root, sha256(manifest_path.read_bytes()).hexdigest())


if __name__ == '__main__':
    unittest.main()
