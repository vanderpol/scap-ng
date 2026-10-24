#!/usr/bin/env python3
"""Focused reversible review-archive bridge guards (Refs #233 #251)."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from build_v04_canonical_six_stigs import promote
from migrate_v04_six_stig_review_archive import (
    ORACLE_OLD_REQUIRE, ORACLE_PATH, ORACLE_TEST, normalized_oracle_document,
    attest_oracle_source, upgrade_documents, write_archive,
)
from test_export_v04_registry_pilot import fixture as registry_review
from test_export_v04_shellcommand_pilot import native as shell_review
from v04_a_authoring_graph_index import read_authoring_archive


class ReviewArchiveBridgeTests(unittest.TestCase):
    def test_existing_registry_source_reversibly_promotes(self):
        source = registry_review()
        path = 'authoring/samples/registry.assessment.json'
        outputs, counts, changed, blockers, exceptions = upgrade_documents({path: source})
        self.assertEqual(blockers, [])
        self.assertEqual(exceptions, [])
        self.assertEqual(changed, [path])
        self.assertEqual(outputs[path], promote(source, legacy_review=True)[0])
        self.assertGreater(counts['structured_condition'], 0)
        with tempfile.TemporaryDirectory() as directory:
            json_path = Path(directory) / 'out.json.zip'
            yaml_path = Path(directory) / 'out.yaml.zip'
            write_archive(json_path, outputs, 'json')
            write_archive(yaml_path, outputs, 'yaml')
            self.assertEqual(read_authoring_archive(json_path, 'json')[path], outputs[path])
            self.assertEqual(read_authoring_archive(yaml_path, 'yaml')
                             [path.removesuffix('.json') + '.yaml'], outputs[path])

    def test_absence_with_comparison_is_not_silently_removed(self):
        source = deepcopy(registry_review())
        test = next(iter(source['assessment']['tests'].values()))
        test.pop('states', None)
        test.pop('states_match', None)
        test.pop('state_fields_require', None)
        test['require'] = {'items': 'may_be_absent', 'all_items_must': [
            {'fields': {'type': {'field_requirement': 'none_exist', 'equals': 'string'}}}]}
        path = 'authoring/samples/rejected.assessment.json'
        outputs, _, _, blockers, _ = upgrade_documents({path: source})
        self.assertEqual(outputs, {})
        self.assertEqual(len(blockers), 1)
        self.assertEqual(blockers[0]['path'], path)
        self.assertIn('field absence cannot discard a meaningful comparison',
                      blockers[0]['reason'])

    def test_owner_approved_oracle_exception_removes_only_universal_pattern(self):
        original = {'assessment': {'tests': {ORACLE_TEST: {
            'capability': 'independent.shellcommand',
            'require': deepcopy(ORACLE_OLD_REQUIRE)}}}}
        attestation = {'source_zip_sha256': 'pinned-source-for-function-test'}
        normalized, proof = normalized_oracle_document(ORACLE_PATH, original, attestation)
        field = normalized['assessment']['tests'][ORACLE_TEST]['require'][
            'all_items_must'][0]['fields']['stderr_line']
        self.assertEqual(field, {'field_requirement': 'none_exist'})
        self.assertEqual(proof['original_requirement'], ORACLE_OLD_REQUIRE)
        self.assertEqual(original['assessment']['tests'][ORACLE_TEST]['require'],
                         ORACLE_OLD_REQUIRE)
        with self.assertRaisesRegex(ValueError, 'attestation required'):
            normalized_oracle_document(ORACLE_PATH, original, None)
        mutated = deepcopy(original)
        mutated['assessment']['tests'][ORACLE_TEST]['require'][
            'all_items_must'][0]['fields']['stderr_line']['matches_regex'] = '.+'
        with self.assertRaisesRegex(ValueError, 'approved source shape'):
            normalized_oracle_document(ORACLE_PATH, mutated, attestation)

    def test_source_zip_pin_must_not_be_bypassed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'fake.zip'
            write_archive(path, {'authoring/fake.json': {'assessment': {'id': 'fake'}}}, 'json')
            with self.assertRaisesRegex(ValueError, 'SHA-256 mismatch'):
                attest_oracle_source(path)

    def test_approved_shape_promotes_to_comparator_free_absence(self):
        source = deepcopy(shell_review())
        assessment = source['assessment']
        old_name, test = next(iter(assessment['tests'].items()))
        assessment['tests'] = {ORACLE_TEST: test}
        assessment['evaluate'] = {'test': ORACLE_TEST}
        test.pop('states', None)
        test.pop('states_match', None)
        test['require'] = deepcopy(ORACLE_OLD_REQUIRE)
        outputs, _, changed, blockers, exceptions = upgrade_documents(
            {ORACLE_PATH: source}, oracle_attestation={'source_zip_sha256': 'verified'})
        self.assertEqual(blockers, [])
        self.assertEqual(changed, [ORACLE_PATH])
        self.assertEqual(len(exceptions), 1)
        req = outputs[ORACLE_PATH]['assessment']['tests'][ORACLE_TEST]['require']
        self.assertEqual(req['items_found'], 'may_be_absent')
        self.assertEqual(req['items_satisfying'], 'every')
        self.assertEqual(req['and'][0]['fields']['stderr_line'], {'values_found': 'none'})
        self.assertEqual(assessment['evaluate'], {'test': ORACLE_TEST})


if __name__ == '__main__':
    unittest.main()
