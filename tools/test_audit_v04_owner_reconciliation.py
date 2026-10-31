"""Audit boundaries and source/default facts, not authoring acceptance (#255/#268)."""
from hashlib import sha256
import json
from pathlib import Path
import unittest

from audit_v04_owner_reconciliation import ROOT, SourceDefaults, audit, control, slug_capability


class OwnerReconciliationAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit()

    def test_all_hundred_contracts_and_preserved_original_qnames(self):
        rows = self.report['capabilities']
        self.assertEqual(len(rows), 100)
        row = next(r for r in rows if r['capability'] == 'independent.textfilecontent')
        self.assertEqual(row['native_expected_name'], 'independent.textfilecontent')
        self.assertEqual(row['source']['test'], 'textfilecontent54_test')
        self.assertTrue(row['source_default_declarations'])
        self.assertEqual(slug_capability('windows.file'), 'windows.file')

    def test_five_controls_with_paired_field_requirement_as_one(self):
        self.assertEqual(self.report['annotated_control_count'], 5)
        controls = self.report['annotated_hideable_controls']
        self.assertEqual(sum(c['scalar_members'] for c in controls), 6)
        paired, = [c for c in controls if isinstance(c['default'], dict)]
        self.assertEqual(paired['control_count'], 1)
        self.assertEqual(set(paired['default']), {'values_found', 'values_matching'})

    def test_204_declarations_are_189_attribute_and_15_element_defaults(self):
        summary = self.report['source_defaults_summary']
        self.assertEqual(summary['definitions_xsd_raw_declarations'], 204)
        self.assertEqual(summary['definitions_attribute_defaults'], 189)
        self.assertEqual(summary['definitions_element_defaults'], 15)
        examples = [r for r in self.report['source_default_declarations'] if r['declaration_kind'] == 'element']
        self.assertTrue(all('not an absent optional element' in r['omitted_source_behavior'] for r in examples))

    def test_windows_recurse_and_scope_depth_are_independent(self):
        defaults = self.report['source_default_declarations']
        windows = [r for r in defaults if r['source_path'].endswith('windows-definitions-schema.xsd')
                   and r['attribute'] == 'recurse' and 'FileBehaviors' in r['declaration_context']]
        self.assertEqual([r['source_default'] for r in windows], ['directories'])
        scope = next(r for r in defaults if r['attribute'] == 'recurse_file_system'
                     and 'FileBehaviors' in r['declaration_context'])
        self.assertEqual(scope['source_default'], 'all')
        self.assertEqual(scope['ng_editor_suggestion'], 'local')
        self.assertNotEqual(control('recurse', [])[0], control('recurse_file_system', [])[0])
        self.assertNotEqual(control('max_depth', [])[0], control('recurse_direction', [])[0])

    def test_historical_fixtures_are_preserved_and_new_annotations_not_inferred(self):
        fixture = ROOT / 'tests/fixtures/v04-native-generator-parity.json'
        digest = sha256(fixture.read_bytes()).hexdigest()
        self.assertTrue(any(r['status'] == 'PRESERVE_PINNED_OR_EXPLICITLY_MIGRATE_NEW_COPY' for r in self.report['drift']))
        self.assertTrue(all(r['hideable'] == 'NOT_APPROVED_AS_ADDITIONAL_HIDDEN_DEFAULT'
            for r in self.report['source_default_declarations'] if r['attribute'] == 'error_if_stderr_exists'))
        self.assertEqual(digest, sha256(fixture.read_bytes()).hexdigest())


if __name__ == '__main__': unittest.main()
