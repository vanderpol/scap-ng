"""Single unix.file prototype: source integrity and illustrative shape, not execution."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator
from test_draft202012_and_examples import schema_registry
from test_schema_integrity import PREFIX

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'docs/developer-guide/prototypes'


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


class UnixFileStopGoPrototype(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger = load(DIRECTORY / 'unix-file-comparison.json')
        cls.examples = load(DIRECTORY / 'unix-file-examples.json')
        cls.registry = schema_registry()

    def validator(self, name):
        return Draft202012Validator(load(ROOT / 'schema' / name), registry=self.registry)

    def test_pinned_native_claim_references_resolve_and_match_source_bytes(self):
        self.assertEqual(self.ledger['capability'], 'unix.file')
        self.assertEqual(self.ledger['oval_commit'], '2f140ee5c5dd1ed9606fcd5afc301f6baeb48706')
        sources = self.ledger['sources']
        for source in sources.values():
            if source['kind'] == 'pinned_native_contract':
                path = ROOT / source['file']
                self.assertEqual(sha256(path.read_bytes()).hexdigest(), source['file_sha256'])
                node = load(path)
                if source['json_pointer']:
                    for key in source['json_pointer'][1:].split('/'):
                        key = key.replace('~1', '/').replace('~0', '~')
                        node = node[int(key)] if isinstance(node, list) else node[key]
                self.assertIsNotNone(node)
                self.assertIn(self.ledger['native_commit'], source['url'])
            elif source['kind'] == 'pinned_oval_documentation':
                self.assertIn(self.ledger['oval_commit'], source['url'])
                self.assertGreater(source['direct_documentation_count'], 0)
                self.assertLessEqual(*source['lines'])
        for claim in self.ledger['claims']:
            self.assertIn(claim['disposition'], {'preserved', 'changed', 'unresolved'})
            self.assertTrue(claim['sources'])
            self.assertTrue(set(claim['sources']) <= set(sources))
            self.assertTrue(set(claim.get('decisions', [])) <= set(self.ledger['decisions']))

    def test_three_illustrative_objects_collections_and_items_pass_frozen_structure(self):
        self.assertEqual({case['id'] for case in self.examples['examples']}, {'regular', 'missing', 'denied'})
        object_validator = Draft202012Validator(
            {'$ref': PREFIX + 'native-selector.schema.json#/$defs/unix_file_object'}, registry=self.registry)
        for case in self.examples['examples']:
            with self.subTest(case=case['id']):
                self.assertTrue(case['illustrative_only'])
                self.assertTrue(case['not_scanner_verified'])
                self.assertEqual(case['capability'], 'unix.file')
                object_validator.validate(case['authored_object'])
                self.validator('collection-result.schema.json').validate(case['illustrative_collection'])
                self.assertEqual(case['illustrative_collection']['item_refs'],
                                 [item['id'] for item in case['illustrative_items']])
                for item in case['illustrative_items']:
                    self.validator('collected-item.schema.json').validate(item)
        object_validator.validate(self.examples['alternate_regular_object'])
        self.assertFalse(object_validator.is_valid({'full_path': {'equals': '/fixture/config'}}))

    def test_worked_regular_fields_cover_the_21_field_subset_without_false_defaults(self):
        guide = (DIRECTORY / 'unix-file-scanner.md').read_text()
        core = set(self.ledger['core_fields'])
        regular = next(case for case in self.examples['examples'] if case['id'] == 'regular')
        fields = regular['illustrative_items'][0]['fields']
        self.assertEqual(len(core), 21)
        self.assertEqual(set(fields), core)
        self.assertTrue({'size', 'has_extended_acl'}.isdisjoint(fields))
        native = load(ROOT / 'schema/capability-mappings/supported/unix.file.json')['native']
        for name, field in fields.items():
            self.assertIn('`' + name + '`', guide)
            self.assertIn(field['datatype'], native['field_datatypes'][name])
            self.assertEqual(field['status'], 'exists')
            if field['datatype'] == 'boolean':
                self.assertIs(type(field['value']), bool)
        true_flags = {name for name, value in fields.items() if value['datatype'] == 'boolean' and value['value']}
        self.assertEqual(true_flags, {'owner_read', 'owner_write', 'group_read'}, 'Mode 0100640 has exactly these flags.')
        self.assertEqual(fields['change_time']['value'], regular['fixture']['st_ctim']['tv_sec'])
        for case in self.examples['examples']:
            if case['id'] != 'regular':
                self.assertEqual(case['illustrative_items'], [])

    def test_missing_items_and_error_diagnostics_do_not_inherit_oval_shapes(self):
        regular = self.examples['examples'][0]['illustrative_items'][0]
        missing_item = deepcopy(regular)
        missing_item['status'] = 'does_not_exist'
        self.assertFalse(self.validator('collected-item.schema.json').is_valid(missing_item))
        denied = deepcopy(next(case for case in self.examples['examples'] if case['id'] == 'denied')['illustrative_collection'])
        self.assertEqual(denied['status'], 'error')
        self.assertFalse(denied['population_complete'])
        del denied['diagnostics']
        self.assertFalse(self.validator('collection-result.schema.json').is_valid(denied))
        typed = Draft202012Validator({'$ref': PREFIX + 'result-types.schema.json#/$defs/typed_value'}, registry=self.registry)
        self.assertFalse(typed.is_valid({'datatype': 'integer', 'status': 'not_collected', 'value': 0}))


if __name__ == '__main__':
    unittest.main()
