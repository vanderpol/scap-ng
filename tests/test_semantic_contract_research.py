"""Research integrity and observed schema boundaries; never a scanner oracle."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import sys
import unittest

from jsonschema import Draft202012Validator
from test_draft202012_and_examples import schema_registry

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from render_contract_research import EXPECTED, load, validate  # noqa: E402
from generate_docs import generated_documents  # noqa: E402


class SemanticContractResearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.research = load('developer-guide-semantic-research.json')
        cls.vectors = load('developer-guide-semantic-vectors.json')
        cls.content = load('developer-guide-content-audit.json')
        cls.lineage = load('developer-guide-oval-audit.json')
        cls.validator = Draft202012Validator(
            json.loads((ROOT / 'schema/assessment.schema.json').read_text()), registry=schema_registry())

    def test_eight_examples_validate_without_runtime_claims(self):
        paths = list((ROOT / 'docs/developer-guide/research-examples').glob('*.json'))
        self.assertEqual({p.stem for p in paths}, EXPECTED)
        for path in paths:
            with self.subTest(capability=path.stem):
                self.validator.validate(json.loads(path.read_text()))
        partition = json.loads((ROOT / self.research['capabilities']['linux.partition']['example']).read_text())
        require = partition['assessment']['tests']['sample-test']['require']
        self.assertEqual(require['field_requirement']['values_matching'], 'one_or_more',
                         'Mount option membership must allow unrelated effective options.')

    def test_all_28_frozen_schema_observations_are_preserved(self):
        self.assertEqual(len(self.vectors['schema_probes']), 28)
        for case in self.vectors['schema_probes']:
            with self.subTest(probe=case['id']):
                example = json.loads((ROOT / self.research['capabilities']['independent.shellcommand']['example']).read_text())
                test = example['assessment']['tests']['sample-test']
                test['capability'], test['object'] = case['capability'], case['object']
                test['require'] = {'item_requirement': {'items_found': 'one_or_more'}}
                self.assertEqual(self.validator.is_valid(example), case['accepted'], case['boundary'])

    def test_native_references_and_legacy_nodes_are_separate_and_complete(self):
        validate(self.research, self.vectors, self.content, self.lineage)
        self.assertEqual(len(self.lineage['files']), 8)
        self.assertEqual(len(self.lineage['nodes']), 39)
        for name, record in self.research['capabilities'].items():
            self.assertEqual(len(record['legacy_nodes']), 6 if name == 'independent.textfilecontent'
                             else 4 if name in {'windows.service', 'linux.partition'} else 5)
            self.assertTrue(record['native_refs'])
            self.assertEqual(record['runtime_qualification'], 'not_established')

    def test_research_cannot_upgrade_itself_to_adopted_or_scanner_verified(self):
        research = deepcopy(self.research)
        research['status'] = 'adopted'
        with self.assertRaisesRegex(ValueError, 'adopted'):
            validate(research, self.vectors, self.content, self.lineage)
        vectors = deepcopy(self.vectors)
        vectors['vectors'][0]['status'] = 'scanner_verified'
        with self.assertRaisesRegex(ValueError, 'qualification'):
            validate(self.research, vectors, self.content, self.lineage)
        research = deepcopy(self.research)
        research['capabilities']['windows.registry']['legacy_nodes'] = ['unix.file/file_item']
        with self.assertRaisesRegex(ValueError, 'provenance'):
            validate(research, self.vectors, self.content, self.lineage)
        research = deepcopy(self.research)
        research['capabilities']['windows.registry']['native_refs'] = ['docs/metadata/developer-guide-oval-audit.json#/nodes']
        with self.assertRaisesRegex(ValueError, 'pinned schema'):
            validate(research, self.vectors, self.content, self.lineage)

    def test_91_proposals_are_fixture_cases_not_measured_outcomes(self):
        self.assertEqual(len(self.vectors['vectors']), 91)
        self.assertEqual(self.vectors['runtime_execution'], 'not_run')
        self.assertEqual({v['capability'] for v in self.vectors['vectors']}, EXPECTED)
        vectors = deepcopy(self.vectors)
        vectors['vectors'][0]['topic'] = 'registry-view'
        with self.assertRaisesRegex(ValueError, 'Cross-capability'):
            validate(self.research, vectors, self.content, self.lineage)
        cases = [v for v in self.vectors['vectors'] if v['id'].startswith('shell-both-failures-')]
        self.assertEqual(len(cases), 4)
        self.assertEqual({(v['input']['error_if_exit_status_not_0'],
                           v['input']['error_if_stderr_exists']) for v in cases},
                         {(False, False), (False, True), (True, False), (True, True)})

    def test_historical_content_and_source_pins_have_not_been_promoted(self):
        self.assertEqual(self.content['archive_sha256'], 'a01ea589501bf8a53e5df68e50ca9478f19543d2bd3844546667fde743c28d8c')
        self.assertEqual(self.content['automated_assessments'], 6817)
        self.assertEqual(self.content['non_automated_assessments_excluded'], 0)
        for record in self.content['capabilities'].values():
            self.assertGreater(record['counts']['tests'], 0)
            for specimen in record['examples']:
                self.assertRegex(specimen['yaml_sha256'], r'^[a-f0-9]{64}$')
                self.assertRegex(specimen['source']['zip_sha256'], r'^[a-f0-9]{64}$')
                self.assertTrue(specimen['source']['nodes'])
        registry = self.content['capabilities']['windows.registry']
        self.assertEqual(registry['object_keys']['traversal'], 1)
        self.assertTrue(any(s['object'].get('traversal', {}).get('max_depth', 'absent') is None
                            for s in registry['examples']))

    def test_generated_research_stays_platform_scoped_and_qualified_as_proposals(self):
        docs = generated_documents()
        for family in ['windows', 'unix', 'linux', 'independent']:
            page = docs[f'developer-contract-research-{family}.md']
            self.assertIn('Recommendations only; not adopted native behavior.', page)
            for cap in EXPECTED:
                self.assertEqual(f'## {cap}\n' in page, cap.split('.')[0] == family)
        self.assertEqual(json.loads(docs['developer-guide-gaps.json'])['summary']['qualified'], 0)


if __name__ == '__main__':
    unittest.main()
