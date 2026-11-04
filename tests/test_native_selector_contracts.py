"""Capability-specific native Object selector contract checks for issue #14."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

from jsonschema import Draft202012Validator
import yaml

PROJECT = Path(__file__).resolve().parents[1]
SCHEMA = PROJECT / 'schema'
sys.path.insert(0, str(PROJECT / 'tests'))
from test_draft202012_and_examples import UniqueYaml, load, schema_registry  # noqa: E402


class NativeSelectorContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = schema_registry()
        cls.validator = Draft202012Validator(load(SCHEMA / 'assessment.schema.json'),
                                             registry=cls.registry)
        cls.windows = yaml.load(
            (PROJECT / 'examples/windows-server-2025-lock-screen.assessment.yaml').read_text(),
            Loader=UniqueYaml)
        cls.linux = yaml.load(
            (PROJECT / 'examples/linux-home-nosuid.assessment.yaml').read_text(),
            Loader=UniqueYaml)

    def assert_valid(self, document):
        self.assertEqual(list(self.validator.iter_errors(document)), [])

    def assert_invalid(self, document):
        self.assertTrue(list(self.validator.iter_errors(document)))

    @staticmethod
    def object_for(document, test_id):
        return document['assessment']['tests'][test_id]['object']

    def test_reviewed_positive_operator_and_value_forms_validate(self):
        windows = deepcopy(self.windows)
        obj = self.object_for(windows, 'verifies-prevent-enabling-screen-slide-show-is-set-enabled-test')
        obj['hive'] = {'equals': ['local_machine', 'users'], 'value_match': 'every'}
        obj['key'] = {'case_insensitive_equals': 'SOFTWARE\\Policies\\Microsoft\\Windows\\Personalization'}
        obj['name'] = {'matches_regex': 'NoLockScreen.*'}
        self.assert_valid(windows)

        nullable = deepcopy(self.windows)
        nullable_obj = self.object_for(nullable, 'verifies-prevent-enabling-screen-slide-show-is-set-enabled-test')
        nullable_obj['key'] = None
        nullable_obj['name'] = None
        self.assert_valid(nullable)

        linux = deepcopy(self.linux)
        obj = self.object_for(linux, 'home-is-mounted-with-the-nosuid-option-test')
        obj['mount_point'] = {'case_insensitive_not_equal': '/tmp'}
        self.assert_valid(linux)

    def test_registry_hive_rejects_generic_operator_leak(self):
        for predicate in (
            {'float_greater_than': 'local_machine'},
            {'pattern_match': 'local_machine'},
            {'equals': 'invalid_hive'},
            {'equals': ['local_machine', 'invalid_hive']},
            {'equals': 1},
            {'equals': 'local_machine', 'not_equal': 'users'},
        ):
            with self.subTest(predicate=predicate):
                document = deepcopy(self.windows)
                self.object_for(document, 'verifies-prevent-enabling-screen-slide-show-is-set-enabled-test')['hive'] = predicate
                self.assert_invalid(document)

    def test_reviewed_string_selector_value_and_unknown_key_boundaries(self):
        for field, predicate in (
            ('key', {'equals': 42}),
            ('name', {'matches_regex': ['not', 'a', 'scalar']}),
            ('name', {'equals': {'unexpected': 'object'}}),
        ):
            with self.subTest(field=field, predicate=predicate):
                document = deepcopy(self.windows)
                self.object_for(document, 'verifies-prevent-enabling-screen-slide-show-is-set-enabled-test')[field] = predicate
                self.assert_invalid(document)

        document = deepcopy(self.windows)
        self.object_for(document, 'verifies-prevent-enabling-screen-slide-show-is-set-enabled-test')['unsupported_selector'] = {'equals': 'x'}
        self.assert_invalid(document)

    def test_partition_selector_has_the_same_explicit_native_boundary(self):
        for predicate in (
            {'float_greater_than': '/home'},
            {'pattern_match': '/home'},
            {'matches_regex': 5},
        ):
            with self.subTest(predicate=predicate):
                document = deepcopy(self.linux)
                self.object_for(document, 'home-is-mounted-with-the-nosuid-option-test')['mount_point'] = predicate
                self.assert_invalid(document)

    def batch_document(self, capability, obj):
        document = deepcopy(self.windows)
        test = next(iter(document['assessment']['tests'].values()))
        test['capability'] = capability
        test['object'] = obj
        return document

    def test_filesystem_and_windows_batch_positive_negative_boundary_contracts(self):
        batch = {
            'unix.file': {
                'selectors': ('filepath', 'path', 'filename'),
                'nullable': {'filename'},
                'enum': {},
            },
            'windows.file': {
                'selectors': ('filepath', 'path', 'filename'),
                'nullable': {'filename'},
                'enum': {},
            },
            'windows.fileeffectiverights': {
                'selectors': ('filepath', 'path', 'filename', 'trustee_sid'),
                'nullable': {'filename'},
                'enum': {},
            },
            'windows.ntuser': {
                'selectors': ('key', 'name'),
                'nullable': {'name'},
                'enum': {},
            },
            'windows.regkeyeffectiverights': {
                'selectors': ('hive', 'key', 'trustee_sid'),
                'nullable': {'key'},
                'enum': {'hive': 'local_machine'},
            },
        }
        native_ops = ('equals', 'not_equal', 'case_insensitive_equals',
                      'case_insensitive_not_equal', 'matches_regex')
        for capability, spec in batch.items():
            with self.subTest(capability=capability):
                for field in spec['selectors']:
                    operators = ('equals',) if field in spec['enum'] else native_ops
                    for operator in operators:
                        value = spec['enum'].get(field, 'C:/Policy\\item')
                        self.assert_valid(self.batch_document(capability, {
                            field: {operator: value}
                        }))

                    if field in spec['nullable']:
                        self.assert_valid(self.batch_document(capability, {field: None}))
                    else:
                        self.assert_invalid(self.batch_document(capability, {field: None}))

                    for predicate in (
                        {'equals': 7},
                        {'equals': []},
                        {'greater_than': 'C:/Policy'},
                        {'pattern_match': 'C:/Policy'},
                    ):
                        with self.subTest(field=field, predicate=predicate):
                            self.assert_invalid(self.batch_document(capability, {field: predicate}))

                self.assert_invalid(self.batch_document(
                    capability, {'unsupported_selector': {'equals': 'x'}}))

    def test_batch_preserves_variables_lists_and_native_regex_spelling(self):
        for capability, field in (
            ('unix.file', 'filepath'),
            ('windows.file', 'path'),
            ('windows.fileeffectiverights', 'trustee_sid'),
            ('windows.ntuser', 'key'),
            ('windows.regkeyeffectiverights', 'key'),
        ):
            with self.subTest(capability=capability, field=field):
                self.assert_valid(self.batch_document(capability, {
                    field: {'value_match': 'every', 'matches_regex': {'variable': 'selector-values-variable'}}
                }))
                self.assert_valid(self.batch_document(capability, {
                    field: {'value_match': 'every', 'equals': ['one', 'two']}
                }))

    def test_native_spelling_round_trips_without_rewriting(self):
        raw = (PROJECT / 'examples/linux-home-nosuid.assessment.yaml').read_text()
        parsed = yaml.load(raw, Loader=UniqueYaml)
        mount_point = self.object_for(parsed, 'home-is-mounted-with-the-nosuid-option-test')['mount_point']
        self.assertEqual(list(mount_point), ['matches_regex'])
        serialized = yaml.safe_dump(parsed, sort_keys=False)
        reparsed = yaml.safe_load(serialized)
        self.assertEqual(list(self.object_for(reparsed, 'home-is-mounted-with-the-nosuid-option-test')['mount_point']),
                         ['matches_regex'])

    def test_contract_input_and_generated_pack_are_integrity_bound(self):
        source = json.loads((SCHEMA / 'native-selector-contracts.json').read_text())
        generated = json.loads((SCHEMA / 'native-selector.schema.json').read_text())
        audit = json.loads((PROJECT / 'docs/metadata/native-selector-audit.json').read_text())
        self.assertEqual(generated['x-generated-from'], 'native-selector-contracts.json')
        self.assertEqual(audit['selector_count'],
                         audit['resolved_count'] + audit['unresolved_count'])
        for capability, contract in source['resolved'].items():
            prefix = capability.replace('.', '_')
            self.assertIn(f'{prefix}_object', generated['$defs'])
            for selector in contract['selectors']:
                self.assertIn(f'{prefix}_{selector}_selector', generated['$defs'])
        self.assertEqual(audit['resolved_count'], 19)
        self.assertEqual(audit['unresolved_count'], 122)
        self.assertGreater(audit['unresolved_count'], 0,
                           'ambiguous mappings must remain visibly unresolved')
        for item in audit['selectors']:
            if item['status'] == 'resolved':
                self.assertTrue(item['allowed_operators'])
                self.assertTrue(item['value_types'])


if __name__ == '__main__':
    unittest.main()
