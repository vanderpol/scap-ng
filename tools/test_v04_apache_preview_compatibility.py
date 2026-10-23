#!/usr/bin/env python3
"""Real Apache preview failures: strict current-schema view and exact inverse.

Fixtures are unchanged members of the immutable 4,001-document review ZIP.
Refs #248 #239.
"""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest
import zipfile
import yaml

from build_v04_canonical_six_stigs import promote, recover
from migrate_v04_states_match_to_logic import migrate, validate_exact_inverse
from build_v04_and_or_fields_candidate import project_document, restore_document as restore_fields
from rename_v04_field_requirement_preview import migrate_document, restore_test as restore_renamed
from test_v04_public_cli_smoke import schema_valid_docs, authoring_archives
from v04_canonical_source_ir import _schema_validators, validate_docs, compile_pair, decode_and_verify
from v04_field_requirement import promote_test, restore_test
from v04_restore_missing_applicability import restore_legacy_view_documents
from v04_flat_object_authoring import flatten_document, restore_document, load_catalog
from validate_v04_fields_condition_preview import native_schema_projection

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / 'tests/fixtures/v04-apache-preview'
GATHER = 'gather-all-installation-directories-from-running-apache-httpd-processes-test'
SHARED = 'gather-unique-apache-http-installation-paths-object'


class ApachePreviewCompatibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = {}
        for record in json.loads((FIXTURES / 'provenance.json').read_text())['files']:
            raw = (FIXTURES / record['fixture']).read_bytes()
            if sha256(raw).hexdigest() != record['sha256']:
                raise ValueError('changed pinned Apache fixture')
            cls.sources[record['archive_path']] = json.loads(raw)
        cls.validators = _schema_validators(ROOT / 'schema/v0.4.0')
        cls.catalog = load_catalog(ROOT / 'schema/v0.4.0/capability-mappings/supported')

    def applicability(self):
        return deepcopy(next(doc for path, doc in self.sources.items() if '/applicability/' in path))

    def test_real_apache_objects_and_conditions_need_explicit_canonical_projection(self):
        before = deepcopy(self.sources)
        for path, doc in self.sources.items():
            with self.subTest(path=path):
                with self.assertRaisesRegex(ValueError, 'schema failure'):
                    validate_docs({path: doc}, self.validators)
        projected = native_schema_projection(self.sources)
        validate_docs(projected, self.validators)
        self.assertEqual(self.sources, before)
        for path, source in self.sources.items():
            canonical, _ = promote(source, legacy_review=True)
            recover(canonical, source, legacy_review=True)
            flat, ledger = flatten_document(canonical, self.catalog)
            self.assertEqual(flat, projected[path])
            self.assertEqual(restore_document(flat, ledger), canonical)

    def test_each_affected_preview_stage_validates_and_retains_its_exact_inverse(self):
        for path, source in self.sources.items():
            state_view, state_proof = migrate(source)
            validate_exact_inverse(source, state_view, state_proof)
            fields_view, fields_proof = project_document(source)
            self.assertEqual(restore_fields(fields_view, fields_proof), source)
            renamed, renames = migrate_document(fields_view)
            restored = deepcopy(renamed)
            for proof in renames:
                tid = proof['test']
                restored['assessment']['tests'][tid] = restore_renamed(
                    restored['assessment']['tests'][tid], proof)
            self.assertEqual(restored, fields_view)
            flat, objects = flatten_document(renamed, self.catalog)
            self.assertEqual(restore_document(flat, objects), renamed)
            for stage in (source, state_view, fields_view, renamed, flat):
                with self.subTest(path=path, stage=stage['assessment']['id']):
                    validate_docs(native_schema_projection({path: stage}, objects_flat=stage is flat), self.validators)

    def test_stdout_line_uses_fields_without_changing_pattern_or_cardinality(self):
        source = self.applicability()
        original = source['assessment']['tests'][GATHER]
        with self.assertRaisesRegex(ValueError, 'invalid canonical'):
            promote_test(original)
        current, proof = promote_test(original, legacy_review=True)
        self.assertEqual(current['require'], {'items': 'one_or_more', 'all_items_must': [
            {'fields': {'stdout_line': {'matches_regex': '^/',
             'field_requirement': 'at_least_one_exists_and_all_match'}}}]})
        self.assertEqual(restore_test(current, proof), original)
        bad = deepcopy(current)
        bad['require']['all_items_must'][0]['fields']['stdout_line']['matches_regex'] = '^wrong/'
        with self.assertRaisesRegex(ValueError, 'changed'):
            restore_test(bad, proof)

    def test_named_shared_contracts_variable_graph_and_command_are_preserved(self):
        projected = native_schema_projection(self.sources)
        for path, source in self.sources.items():
            old, new = source['assessment'], projected[path]['assessment']
            self.assertEqual(old.get('variables'), new.get('variables'))
            self.assertEqual(list(old.get('shared_objects', {})), list(new.get('shared_objects', {})))
            if SHARED in old.get('shared_objects', {}):
                original = old['shared_objects'][SHARED]
                flat = new['shared_objects'][SHARED]
                self.assertEqual(flat, {k:v for k,v in original.items() if k != 'collect'}
                                 | original['collect'])
                self.assertEqual(flat['capability'], original['capability'])
                self.assertEqual(flat['object_title'], original['object_title'])
            for tid, test in old['tests'].items():
                if isinstance(test.get('object'), str):
                    self.assertEqual(new['tests'][tid]['object'], test['object'])

    def test_paired_compiler_is_strict_by_default_and_explicitly_checks_legacy_inverse(self):
        docs = schema_valid_docs()
        source = self.applicability()
        docs['authoring/demo/assessments/a1.json'] = source
        docs['authoring/demo/rules/r1.json']['rule']['assessment_choices']['automated']['assessment'] = source['assessment']['id']
        with tempfile.TemporaryDirectory() as tmp:
            archives = authoring_archives(docs, Path(tmp))
            with self.assertRaisesRegex(ValueError, 'schema failure'):
                compile_pair(*archives)
            raw, proof = compile_pair(*archives, legacy_review=True)
        self.assertEqual(proof['native_source_schema'], 'PASS')
        self.assertEqual(proof['legacy_source_inverse'], 'PASS')
        self.assertEqual(proof['schema_validation_view'], 'CANONICAL_PROJECTION_OF_LEGACY_REVIEW_INPUT')
        self.assertEqual(decode_and_verify(json.loads(raw)), native_schema_projection(docs))

    def test_equivalent_projection_cannot_hide_different_source_archives(self):
        docs = schema_valid_docs()
        source = self.applicability()
        docs['authoring/demo/assessments/a1.json'] = source
        docs['authoring/demo/rules/r1.json']['rule']['assessment_choices']['automated']['assessment'] = source['assessment']['id']
        with tempfile.TemporaryDirectory() as tmp:
            jzip, yzip = authoring_archives(docs, Path(tmp))
            with zipfile.ZipFile(yzip) as archive:
                entries = {name: archive.read(name) for name in archive.namelist()}
            key = 'authoring/demo/assessments/a1.yaml'
            doc = yaml.safe_load(entries[key])
            field = doc['assessment']['tests'][GATHER]['require']['all_items_must'][0]['stdout_line']
            field['field_requirement'] = field.pop('require')
            entries[key] = yaml.safe_dump(doc).encode()
            with zipfile.ZipFile(yzip, 'w') as archive:
                for name, raw in entries.items():
                    archive.writestr(name, raw)
            with self.assertRaisesRegex(ValueError, 'source mismatch'):
                compile_pair(jzip, yzip, legacy_review=True)

    def test_projection_is_idempotent_and_does_not_weaken_schema(self):
        current = native_schema_projection(self.sources)
        self.assertEqual(native_schema_projection(current, objects_flat=True), current)
        broken = deepcopy(current)
        doc = next(v for k,v in broken.items() if '/applicability/' in k)
        condition = doc['assessment']['tests'][GATHER]['require']['all_items_must'][0]
        condition.update(condition.pop('fields'))
        with self.assertRaisesRegex(ValueError, 'schema failure'):
            validate_docs(broken, self.validators)

    def test_flat_cmdlet_select_is_a_native_parameter_not_a_legacy_wrapper(self):
        docs = schema_valid_docs()
        test = docs['authoring/demo/assessments/a1.json']['assessment']['tests']['file-mode-test']
        test.update(capability='windows.cmdlet', object={
            'module_name': 'TrustedPlatformModule', 'module_id': None, 'module_version': None,
            'verb': 'Get', 'noun': 'Tpm', 'parameters': None,
            'select': {'fields': {'property': {'selection_match': 'all',
                                             'equals': 'tpmpresent,tpmready,tpmenabled'}}}},
                    require={'items': 'one_or_more'})
        with self.assertRaisesRegex(ValueError, 'ambiguous'):
            native_schema_projection(docs)
        projected = native_schema_projection(docs, objects_flat=True)
        validate_docs(projected, self.validators)
        self.assertEqual(projected, docs)
        invalid = deepcopy(docs)
        invalid['authoring/demo/assessments/a1.json']['assessment']['mode'] = 'not-a-mode'
        with self.assertRaisesRegex(ValueError, 'schema failure'):
            validate_docs(native_schema_projection(invalid, objects_flat=True), self.validators)

    def test_dependency_restoration_requires_immutable_source_and_explicit_view(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake = Path(tmp) / 'changed-original-source.zip'
            fake.write_bytes(b'not the pinned immutable source')
            with self.assertRaisesRegex(ValueError, 'digest mismatch'):
                restore_legacy_view_documents(self.sources, fake)
            with self.assertRaisesRegex(ValueError, 'explicit legacy review'):
                compile_pair(fake, fake, legacy_original_03=fake)

    def test_ambiguous_or_unscoped_legacy_requirements_fail_closed(self):
        base = self.applicability()['assessment']['tests'][GATHER]
        mutations = (
            lambda t: t['require'].update(items='exactly_one'),
            lambda t: t.update(states=[]),
            lambda t: t['require'].update(unknown='invented'),
            lambda t: t['require']['all_items_must'][0]['stdout_line'].pop('require'),
            lambda t: t['require'].update(all_items_must=[{'and': [], 'or': []}]),
            lambda t: t['require'].update(all_items_must=[]),
            lambda t: t['require']['all_items_must'][0]['stdout_line'].update(field_requirement='none_exist'),
        )
        for mutate in mutations:
            test = deepcopy(base)
            mutate(test)
            with self.subTest(mutation=mutate), self.assertRaises(ValueError):
                promote_test(test, legacy_review=True)


if __name__ == '__main__':
    unittest.main()
