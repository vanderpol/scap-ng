#!/usr/bin/env python3
"""Focused reversible review-archive bridge guards (Refs #233 #251)."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from build_v04_canonical_six_stigs import promote
from migrate_v04_six_stig_review_archive import upgrade_documents, write_archive
from test_export_v04_registry_pilot import fixture as registry_review
from v04_a_authoring_graph_index import read_authoring_archive


class ReviewArchiveBridgeTests(unittest.TestCase):
    def test_existing_registry_source_reversibly_promotes(self):
        source = registry_review()
        path = 'authoring/samples/registry.assessment.json'
        outputs, counts, changed, blockers = upgrade_documents({path: source})
        self.assertEqual(blockers, [])
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
        outputs, _, _, blockers = upgrade_documents({path: source})
        self.assertEqual(outputs, {})
        self.assertEqual(len(blockers), 1)
        self.assertEqual(blockers[0]['path'], path)
        self.assertIn('field absence cannot discard a meaningful comparison',
                      blockers[0]['reason'])


if __name__ == '__main__':
    unittest.main()
