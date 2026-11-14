"""Phase-1 inventory, proposal, baseline and shared-renderer acceptance gates."""
from copy import deepcopy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import audit_schema_documentation as audit
import schema_documentation as shared
import generate_unix_file_reference as unix


def strip_annotations(node):
    # Remove annotations only at schema nodes. A data property or enum object
    # literally named description/title is a validation value, not an annotation.
    if not isinstance(node, dict):
        return deepcopy(node)
    result = {}
    for key, value in node.items():
        if key in {'description', 'title', 'examples'}:
            continue
        if key in audit.MAPS:
            result[key] = {name: strip_annotations(child) for name, child in value.items()}
        elif key in audit.ARRAYS:
            result[key] = [strip_annotations(child) for child in value]
        elif key in audit.SINGLES and isinstance(value, (dict, bool)):
            result[key] = strip_annotations(value)
        else:
            result[key] = deepcopy(value)
    return result


class CoreDocumentationAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # The original Issue #40 review is a frozen 0.4.0 evidence set.
        # Validate its actual schema snapshot instead of resolving its 0.4.0
        # JSON pointers against the one active 0.4.1 family.
        cls._archive = audit.historical_workspace(ROOT)
        cls.historical_root = cls._archive.__enter__()
        try:
            shutil.copytree(ROOT / audit.HISTORICAL_DEST,
                            cls.historical_root / audit.HISTORICAL_DEST,
                            dirs_exist_ok=True)
            cls.result = audit.audit(cls.historical_root, active=False)
            cls.outputs = audit.artifacts(cls.result)
        except BaseException:
            cls._archive.__exit__(*sys.exc_info())
            raise

    @classmethod
    def tearDownClass(cls):
        cls._archive.__exit__(None, None, None)

    def fixture(self, root):
        shutil.copytree(self.historical_root / 'schema', root / 'schema')
        notes = root / audit.DEST
        notes.mkdir(parents=True)
        shutil.copy(ROOT / audit.DEST / 'review-notes.json', notes / 'review-notes.json')

    def test_complete_discovery_pointer_accounting_and_explicit_exclusions(self):
        paths = list((self.historical_root / 'schema').rglob('*.json'))
        expected = {str(p.relative_to(ROOT)) for p in paths if '$schema' in json.loads(p.read_text()) and '$id' in json.loads(p.read_text())}
        self.assertEqual(set(self.result['schemas']), expected)
        self.assertEqual(len(self.result['manifest']), len(paths))
        self.assertEqual(len(self.result['inventory']), len(self.result['nodes']))
        for record in self.result['inventory']:
            value = self.result['store'].node(record['schema_uri'] + '#' + record['pointer'])
            self.assertIsInstance(value, (dict, bool))
        for omitted in self.result['excluded']:
            self.assertIn('capability-specific', omitted['reason'])
        self.assertTrue(any(not r['public'] and r['role'] == 'alternative' for r in self.result['inventory']))
        self.assertTrue(any(r['role'] == 'field' and '/items/properties/' in r['pointer'] and r['public'] for r in self.result['inventory']))
        # Shared rendering is one implementation, not a copy for the new audit.
        self.assertIs(unix.property_occurrences, shared.property_occurrences)
        self.assertIs(audit.property_occurrences, shared.property_occurrences)

    def test_discovery_does_not_assume_schema_filenames_and_resolves_shared_help(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); self.fixture(root)
            uri = 'https://example.invalid/unconventional-core'
            document = {'$schema': 'https://json-schema.org/draft/2020-12/schema', '$id': uri,
                        '$defs': {'help': {'type': 'string', 'description': 'Identifier used by the enclosing test fixture.'},
                                  'missing': {'type': 'string'}},
                        'properties': {'first': {'$ref': '#/$defs/help'}, 'second': {'allOf': [{'$ref': '#/$defs/help'}]},
                                       'a': {'$ref': '#/$defs/missing'}, 'b': {'$ref': '#/$defs/missing'},
                                       'slash/name': {'type': 'integer'}}}
            (root / 'schema' / 'not-a-standard-schema-filename.json').write_text(json.dumps(document))
            result = audit.audit(root)
            by_key = {r['schema_uri'] + '#' + r['pointer']: r for r in result['inventory']}
            for name in ['first', 'second']:
                self.assertEqual(by_key[uri + '#/properties/' + name]['description_source'], uri + '#/$defs/help')
            missing = [g for g in result['findings'] if g['schema_uri'] == uri and g['pointer'] == '/$defs/missing' and g['category'] == 'missing_description']
            self.assertEqual(len(missing), 1)
            self.assertTrue({uri + '#/properties/a', uri + '#/properties/b'} <= set(missing[0]['affected_nodes']))
            self.assertIn(uri + '#/properties/slash~1name', by_key)

    def test_conditionally_introduced_fields_are_not_lost_as_guard_overrides(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); self.fixture(root)
            uri = 'https://example.invalid/conditional-core'
            doc = {'$schema': 'https://json-schema.org/draft/2020-12/schema', '$id': uri,
                   'properties': {'mode': {'type': 'string'}},
                   'if': {'properties': {'mode': {'const': 'special'}}},
                   'then': {'properties': {'conditional_only': {'const': 'enabled'}}}}
            (root / 'schema' / 'conditional.json').write_text(json.dumps(doc))
            result = audit.audit(root)
            record = next(r for r in result['inventory'] if r['schema_uri'] == uri and r['pointer'] == '/then/properties/conditional_only')
            self.assertTrue(record['public'])
            self.assertEqual(record['role'], 'conditional_field')
            guard = next(r for r in result['inventory'] if r['schema_uri'] == uri and r['pointer'] == '/if/properties/mode')
            self.assertFalse(guard['public'])
            gap = next(g for g in result['findings'] if g['schema_uri'] == uri and g['pointer'] == record['pointer'])
            self.assertIn('conditional branch', gap['proposed_replacement'])

    def test_malformed_descriptions_and_nonprovisional_filler_are_rejected(self):
        text, _, _ = audit.structural_wording({'node': {'const': True}, 'element': 'flag', 'role': 'field'})
        self.assertIn('`true`', text)
        self.assertNotIn('`True`', text)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); self.fixture(root)
            uri = 'https://example.invalid/malformed-help'
            doc = {'$schema': 'https://json-schema.org/draft/2020-12/schema', '$id': uri,
                   'properties': {'flag': {'type': 'boolean', 'description': {'bad': 'not text'}}}}
            (root / 'schema' / 'malformed.json').write_text(json.dumps(doc))
            result = audit.audit(root)
            self.assertTrue(any(g['schema_uri'] == uri and 'malformed' in g['impact'] for g in result['findings']))
        bad = dict(self.result, crosswalk=deepcopy(self.result['crosswalk']))
        proposal = next(p for p in bad['crosswalk'] if not p['non_annotation_followup'])
        proposal['proposed_description'] = 'The value field.'
        proposal['provisional'] = False
        with self.assertRaisesRegex(ValueError, 'filler'):
            audit.validate_register(bad)

    def test_gap_deduplication_crosswalk_completeness_and_status_rules(self):
        self.assertTrue(audit.validate_register(self.result))
        keys = [(g['schema_uri'], g['pointer'], g['role'], g['category']) for g in self.result['findings']]
        self.assertEqual(len(keys), len(set(keys)))
        proposals = {p['id']: p for p in self.result['crosswalk']}
        for finding in self.result['findings']:
            self.assertIn(finding['proposal_id'], proposals)
            self.assertTrue(finding['proposed_replacement'] or finding['category'] == 'missing_editor_help_binding')
            self.assertEqual(finding['status'], 'open')
        bad = dict(self.result, findings=deepcopy(self.result['findings']))
        bad['findings'][0]['status'] = 'resolved'
        with self.assertRaisesRegex(ValueError, 'resolution pointer'):
            audit.validate_register(bad)
        bad = dict(self.result, crosswalk=deepcopy(self.result['crosswalk']))
        proposal = next(p for p in bad['crosswalk'] if p['existing_description'] and p['existing_description'] != p['proposed_description'])
        proposal['disposition'] = 'accepted'
        with self.assertRaisesRegex(ValueError, 'approval link'):
            audit.validate_register(bad)
        proposal['approval_link'] = audit.ISSUE
        proposal['resolution_pointer'] = proposal['schema_uri'] + '#' + proposal['pointer'] + '/description'
        with self.assertRaisesRegex(ValueError, 'wording drifted'):
            audit.validate_register(bad)

    def test_all_proposed_patches_are_annotations_and_preserve_assertion_trees(self):
        preview = audit.apply_preview(self.result, self.result['crosswalk'])
        for uri, document in self.result['documents'].items():
            self.assertEqual(strip_annotations(document), strip_annotations(preview[uri]), uri)
            Draft202012Validator.check_schema(preview[uri])
        for proposal in self.result['crosswalk']:
            current = self.result['nodes'][proposal['schema_uri'] + '#' + proposal['pointer']]['node']
            self.assertEqual(proposal['existing_description'], current.get('description'))
            expected_hash = audit.sha256((self.historical_root / proposal['schema_file']).read_bytes()).hexdigest()
            self.assertEqual(proposal['precondition']['file_sha256'], expected_hash)
            for operation in proposal['operations']:
                self.assertIn(operation['path'].rsplit('/', 1)[-1], {'description', 'title', 'examples'})
        malicious = deepcopy(self.result['crosswalk'][0])
        malicious['operations'] = [{'op': 'add', 'path': '/required', 'value': ['invented']}]
        with self.assertRaisesRegex(ValueError, 'Validation keyword'):
            audit.apply_preview(self.result, [malicious])
        malicious['operations'] = [{'op': 'add', 'path': '/properties/description', 'value': False}]
        with self.assertRaisesRegex(ValueError, 'schema node'):
            audit.apply_preview(self.result, [malicious])
        self.assertEqual(strip_annotations({'properties': {'description': {'type': 'integer'}}, 'enum': [{'description': 1}]}), {'properties': {'description': {'type': 'integer'}}, 'enum': [{'description': 1}]})

    def test_active_language_reachability_and_inactive_candidates_are_distinct(self):
        language = audit.language_catalog(self.result)
        self.assertEqual({r['name'] for r in language['active_variable_forms']}, {'literal', 'variable', 'values', 'concat', 'regex_capture', 'unique', 'merge', 'count', 'split', 'substring', 'arithmetic', 'begin', 'end'})
        self.assertTrue(all(r['assessment_reachable'] for r in language['active_variable_forms']))
        self.assertTrue(language['spelling_notes']['else_if'])
        self.assertFalse(language['spelling_notes']['elseif'])
        self.assertFalse(language['spelling_notes']['foreach_or_for_each_authored_placement'])
        self.assertEqual(len(language['unreachable_shared_foreach_helpers']), 2)
        self.assertTrue(all(not r['assessment_reachable'] and r['incoming_refs'] == 0 for r in language['unreachable_shared_foreach_helpers']))
        inactive = {r['name'] for r in language['inactive_function_call_names']}
        self.assertTrue({'arithmetic', 'substring', 'split'} <= inactive)
        self.assertTrue(any(r['language_status'] == 'inactive_migration_candidate' for r in self.result['inventory']))

    def test_core_and_concat_preview_examples_keep_positive_negative_acceptance(self):
        targets = [p for p in self.result['crosswalk'] if p['pointer'] in {'/$defs/canonical_all_items_requirement', '/$defs/expression/oneOf/3/properties/concat'}]
        self.assertEqual(len(targets), 2)
        preview = audit.apply_preview(self.result, targets)
        after = shared.SchemaStore(preview)
        for proposal in targets:
            ref = proposal['schema_uri'] + '#' + proposal['pointer']
            validators = [Draft202012Validator({'$ref': ref}, registry=store.registry) for store in [self.result['store'], after]]
            if 'concat' in ref:
                vectors = [([{'literal': 'a'}, {'literal': 'b'}], True), ([{'literal': 'a'}], False), ([], False),
                           ([{'function': {'name': 'arithmetic'}}, {'literal': 'b'}], False)]
            else:
                good = {'item_requirement': {'items_found': 'one_or_more', 'items_satisfying': 'every'},
                        'field_requirement': {'values_found': 'one_or_more', 'values_matching': 'every'},
                        'fields': {'example_field': {'equals': 'expected'}}}
                incomplete = deepcopy(good); del incomplete['field_requirement']['values_matching']
                vectors = [(good, True), (incomplete, False), ({'fields': {'example_field': {'bogus': 1}}}, False)]
            for value, expected in vectors:
                for validator in validators:
                    self.assertEqual(validator.is_valid(value), expected)
        # Every newly proposed example is schema-valid at its exact target.
        for proposal in self.result['crosswalk']:
            for operation in proposal['operations']:
                if operation['path'].endswith('/examples') and operation['op'] in {'add', 'replace'}:
                    validator = Draft202012Validator({'$ref': proposal['schema_uri'] + '#' + proposal['pointer']}, registry=after.registry)
                    for example in operation['value']:
                        validator.validate(example)

    def test_baseline_detects_new_nodes_generic_filler_and_provisional_non_resolution(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); self.fixture(root)
            baseline = audit.baseline_for(audit.audit(root))
            uri = 'https://example.invalid/new-core'
            file = root / 'schema' / 'new-root.json'
            doc = {'$schema': 'https://json-schema.org/draft/2020-12/schema', '$id': uri,
                   'description': 'A fixture for documentation regression checks.', 'properties': {'flag': {'type': 'boolean'}}}
            file.write_text(json.dumps(doc))
            first = audit.audit(root)
            self.assertTrue(audit.baseline_regressions(first, baseline)['new'])
            missing_baseline = audit.baseline_for(first)
            doc['properties']['flag']['description'] = 'The flag field.'
            file.write_text(json.dumps(doc))
            filler = audit.audit(root)
            self.assertTrue(audit.baseline_regressions(filler, missing_baseline)['new'])
            self.assertTrue(any(g['schema_uri'] == uri and g['category'] == 'vague_description' for g in filler['findings']))
            doc['properties']['flag']['description'] = 'Meaning is not yet documented here; permitted shape alone does not establish runtime behavior.'
            file.write_text(json.dumps(doc))
            provisional = audit.audit(root)
            self.assertTrue(any(g['schema_uri'] == uri and g['category'] == 'unspecified_schema_contract' for g in provisional['findings']))
            self.assertTrue(all(g['status'] != 'resolved' for g in provisional['findings']))

    def test_shared_binding_followups_do_not_duplicate_prose_or_tighten_consumers(self):
        bindings = [p for p in self.result['crosswalk'] if p['proposed_description_ref']]
        self.assertTrue(bindings)
        for proposal in bindings:
            self.assertEqual(proposal['operations'], [])
            self.assertTrue(proposal['non_annotation_followup'])
            self.assertIn('tighten', proposal['binding_warning'])
            self.assertIn(proposal['proposed_description_ref'], self.result['nodes'])
        editor = [p for p in self.result['crosswalk'] if p['non_annotation_followup'] and not p['proposed_description_ref']]
        self.assertEqual(len(editor), 1)
        self.assertEqual(editor[0]['operations'], [])

    def test_exact_generation_links_baseline_and_frozen_bytes(self):
        self.assertEqual(self.outputs, audit.artifacts(audit.audit()))
        for name, text in self.outputs.items():
            self.assertEqual((ROOT / audit.DEST / name).read_bytes(), text.encode())
            if name.endswith('.md'):
                import re
                for target in re.findall(r'\]\(([^)]+)\)', text):
                    if not target.startswith('http'):
                        self.assertTrue((ROOT / audit.DEST / target.split('#')[0]).resolve().exists(), target)
        baseline = json.loads((ROOT / audit.DEST / 'baseline.json').read_text())
        difference = audit.baseline_regressions(self.result, baseline)
        self.assertEqual(difference['new'], []); self.assertEqual(difference['changed'], [])
        paths = sorted((self.historical_root / 'schema').rglob('*.json'))
        before = {str(p): audit.sha256(p.read_bytes()).hexdigest() for p in paths}
        subprocess.run([sys.executable, 'tools/audit_schema_documentation.py', '--check'], cwd=ROOT, check=True, capture_output=True)
        self.assertEqual(before, {str(p): audit.sha256(p.read_bytes()).hexdigest() for p in paths})


if __name__ == '__main__':
    unittest.main()
