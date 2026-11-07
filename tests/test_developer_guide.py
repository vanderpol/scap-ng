"""Contract projections, deliberate validation gaps and deterministic documentation."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest

from jsonschema import Draft202012Validator
from test_draft202012_and_examples import schema_registry

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / 'tools'))
from developer_guide import DOCUMENTATION_STATUSES, model, pointer  # noqa: E402
from generate_docs import (generated_documents, load, mappings_inventory,  # noqa: E402
                           render_developer_pilot, verify_documents)


class DeveloperGuideTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mappings = mappings_inventory()
        cls.proposal = load(PROJECT / 'docs/metadata/schema-documentation-pilot.json')
        cls.docs = generated_documents()
        cls.validator = Draft202012Validator(load(PROJECT / 'schema/assessment.schema.json'),
                                             registry=schema_registry())
        cls.examples = {p.stem: load(p) for p in
                        (PROJECT / 'docs/developer-guide/examples').glob('*.json')}

    def object_for(self, document):
        return document['assessment']['tests']['sample-test']['object']

    def test_platform_partition_and_gap_counts_reconcile(self):
        inventory = json.loads(self.docs['developer-guide-gaps.json'])
        self.assertEqual(inventory['summary'], dict(capabilities=104, supported=100,
                         experimental=4, platform_families=15, reviewed_pilots=3,
                         qualified=0, selectors=145, unresolved_selectors=117,
                         missing_result_datatypes=38))
        pages = [value for key, value in self.docs.items()
                 if key.startswith('developer-guide-') and key.endswith('.md')
                 and key not in {'developer-guide-index.md', 'developer-guide-contract-model.md'}]
        self.assertEqual(len(pages), 15)
        for record in inventory['capabilities']:
            name = record['capability']
            self.assertEqual(sum(page.count(f'## {name}\n') for page in pages), 1)
            suffix = '-pilot' if record['platform'] in {'windows', 'unix', 'independent'} else ''
            self.assertIn(f'## {name}\n', self.docs[f'developer-guide-{record["platform"]}{suffix}.md'])

    def test_generation_ignores_incidental_input_order(self):
        proposal = deepcopy(self.proposal)
        proposal['capabilities'] = dict(reversed(list(proposal['capabilities'].items())))
        for cap in proposal['capabilities'].values():
            cap['properties'] = dict(reversed(list(cap['properties'].items())))
        expected = render_developer_pilot('0.4.0', self.mappings, self.proposal)
        self.assertEqual(expected, render_developer_pilot('0.4.0', list(reversed(self.mappings)), proposal))
        self.assertEqual(self.docs, generated_documents())

    def test_byte_gate_detects_crlf_and_missing_empty_files(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)
            (path / 'example.md').write_bytes(b'line\r\n')
            self.assertEqual(set(verify_documents({'example.md': 'line\n'}, path)), {'example.md'})
            self.assertEqual(set(verify_documents({'absent.md': ''}, path)), {'absent.md'})

    def test_annotations_require_resolvable_authority_and_separate_questions(self):
        mutations = [lambda a: a.update(contract_refs=['/native/missing']),
                     lambda a: a.update(contract_refs=[]),
                     lambda a: a.update(documentation_status='reviewed_qualified'),
                     lambda a: a.update(qualification_status='qualified'),
                     lambda a: a.update(source_lineage=[]),
                     lambda a: a.update(source_lineage=[{'audit_node': 'unix.file/file_object',
                                                         'disposition': 'legacy_candidate'}]),
                     lambda a: a.update(open_question='')]
        for mutate in mutations:
            proposal = deepcopy(self.proposal)
            mutate(proposal['capabilities']['windows.registry']['properties']['hive']['x-scap-ng-scanner'])
            with self.subTest(proposal=proposal), self.assertRaises(ValueError):
                model(self.mappings, proposal)

    def test_annotation_platform_and_capability_cannot_be_invented(self):
        proposal = deepcopy(self.proposal)
        proposal['format'] = 'unknown'
        with self.assertRaisesRegex(ValueError, 'Unsupported'):
            model(self.mappings, proposal)
        proposal = deepcopy(self.proposal)
        proposal['capabilities']['windows.registry']['platform'] = 'unix'
        with self.assertRaisesRegex(ValueError, 'platform mismatch'):
            model(self.mappings, proposal)
        proposal = deepcopy(self.proposal)
        proposal['capabilities']['fictional.object'] = {}
        with self.assertRaisesRegex(ValueError, 'Orphan'):
            model(self.mappings, proposal)

    def test_authored_and_collected_file_names_remain_distinct(self):
        record = next(r for r in model(self.mappings, self.proposal) if r['name'] == 'unix.file')
        self.assertEqual(set(record['selectors']), {'filepath', 'path', 'filename'})
        self.assertTrue({'full_path', 'directory', 'name'} <= set(record['fields']))
        self.assertIn('matches_regex', record['resolved']['filepath']['operators'])
        self.assertNotIn('pattern_match', record['resolved']['filepath']['operators'])

    def test_shell_evidence_datatype_is_not_comparison_cast(self):
        record = next(r for r in model(self.mappings, self.proposal) if r['name'] == 'independent.shellcommand')
        self.assertEqual(record['native']['field_datatypes']['stdout_line'], ['string'])
        self.assertIn('float', record['native']['state_field_datatypes']['stdout_line'])
        self.assertEqual(set(record['parameters']), {'shell', 'command', 'pattern',
                         'error_if_exit_status_not_0', 'error_if_stderr_exists'})

    def test_three_examples_validate_with_local_frozen_resources(self):
        self.assertEqual(set(self.examples), {'windows.registry', 'unix.file', 'independent.shellcommand'})
        for name, example in self.examples.items():
            with self.subTest(capability=name):
                self.validator.validate(example)
                malformed = deepcopy(example)
                malformed['assessment']['tests']['sample-test']['object'] = []
                self.assertFalse(self.validator.is_valid(malformed))

    def test_file_selector_alias_and_source_operator_are_rejected(self):
        for field, predicate in [('full_path', {'equals': '/etc/passwd'}),
                                 ('filepath', {'pattern_match': '.*'}),
                                 ('filepath', {'equals': 42})]:
            example = deepcopy(self.examples['unix.file'])
            example['assessment']['tests']['sample-test']['object'] = {field: predicate}
            self.assertFalse(self.validator.is_valid(example), (field, predicate))
        directory = deepcopy(self.examples['unix.file'])
        directory['assessment']['tests']['sample-test']['object'] = {'path': {'equals': '/etc'}, 'filename': None}
        self.validator.validate(directory)

    def test_registry_enum_and_traversal_rejection_are_preserved(self):
        for change in [dict(hive={'equals': 'HKEY_LOCAL_MACHINE'}),
                       dict(traversal={'max_depth': 0})]:
            example = deepcopy(self.examples['windows.registry'])
            self.object_for(example).update(change)
            self.assertFalse(self.validator.is_valid(example))
        example = deepcopy(self.examples['windows.registry'])
        self.object_for(example).update(key=None, name=None)
        self.validator.validate(example)

    def test_shell_generic_acceptance_is_documented_not_silently_tightened(self):
        for mutate in [lambda o: o.pop('error_if_stderr_exists'),
                       lambda o: o.update(error_if_stderr_exists='true'),
                       lambda o: o.update(shell='unknown'), lambda o: o.pop('command')]:
            example = deepcopy(self.examples['independent.shellcommand'])
            mutate(self.object_for(example))
            self.validator.validate(example)
        self.assertIn('generic Object baseline accepts',
                      (PROJECT / 'docs/developer-guide/pilot-review.md').read_text())

    def test_legacy_provenance_is_complete_and_not_native_qualification(self):
        audit = load(PROJECT / 'docs/metadata/developer-guide-oval-audit.json')
        self.assertEqual(audit['upstream_commit'], '2f140ee5c5dd1ed9606fcd5afc301f6baeb48706')
        self.assertEqual(audit['status'], 'legacy_research_not_native_contract')
        self.assertEqual(len(audit['files']), 8)
        self.assertEqual(len(audit['nodes']), 39)
        for file in audit['files'].values():
            self.assertIn(audit['upstream_commit'], file['url'])
            self.assertRegex(file['sha256'], r'^[0-9a-f]{64}$')
        for node in audit['nodes'].values():
            self.assertIn(node['file'], audit['files'])
            self.assertGreater(node['annotation_count'], 0)
            self.assertTrue(node['xpath'].startswith('/xsd:schema/'))

    def test_all_capabilities_expose_five_contract_sections_and_honest_status(self):
        ledger = json.loads(self.docs['developer-guide-gaps.json'])
        statuses = {r['capability']: r['contract_status'] for r in ledger['capabilities']}
        for record in model(self.mappings, self.proposal):
            contract = record['contracts']
            with self.subTest(capability=record['name']):
                self.assertEqual(set(contract), {'authoring_contract', 'collection_contract',
                                 'evaluation_contract', 'provenance', 'documentation_status',
                                 'runtime_qualification'})
                for section in statuses[record['name']]:
                    self.assertIn(contract[section]['documentation_status'], DOCUMENTATION_STATUSES)
                    self.assertEqual(statuses[record['name']][section], contract[section]['documentation_status'])
                self.assertEqual(contract['collection_contract']['returned_fields'], record['fields'])
                self.assertEqual(contract['collection_contract']['acquisition']['documentation_status'], 'unresolved')
                self.assertEqual(contract['evaluation_contract']['missing_error_behavior']['documentation_status'], 'unresolved')
                self.assertEqual(contract['documentation_status'], 'partially_documented')
                self.assertEqual(contract['runtime_qualification'], 'not_established')
                self.assertEqual(contract['provenance']['native']['disposition'], 'native_contract_reference')
                self.assertEqual(contract['provenance']['legacy']['disposition'], 'legacy_candidate')

    def test_shared_evaluation_and_variable_references_resolve_without_legacy_defaults(self):
        for record in model(self.mappings, self.proposal):
            contract = record['contracts']
            author, evaluation = contract['authoring_contract'], contract['evaluation_contract']
            refs = [author['variables'][key] for key in
                    ('selector_value_reference', 'variable_reference', 'input_reference')]
            refs += [evaluation[key] for key in ('requirements', 'presence_only', 'comparisons')]
            refs += list(evaluation['cardinality'].values())
            for ref in refs:
                filename, fragment = ref.split('#')
                self.assertIsInstance(pointer(load(PROJECT / filename), fragment), dict)
            self.assertEqual(evaluation['capability_semantic_rules'], record['rules'])
            self.assertEqual(evaluation['comparison_datatype_overrides'],
                             record['native'].get('state_field_datatypes', {}))
        records = {r['name']: r for r in model(self.mappings, self.proposal)}
        shell = records['independent.shellcommand']['contracts']['authoring_contract']
        self.assertTrue(shell['collection_parameters']['command']['allow_variable'])
        self.assertIsNone(shell['variables']['parameter_allow_variable']['error_if_stderr_exists'])
        unix = records['unix.file']['contracts']['authoring_contract']
        self.assertIn('traversal', unix['collection_controls'])
        self.assertNotIn('traversal', records['windows.registry']['contracts']['authoring_contract']['collection_controls'])


if __name__ == '__main__':
    unittest.main()
