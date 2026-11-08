"""Review-only next-version schema delta; not production 0.4 acceptance."""
import json
from pathlib import Path
import sys
import unittest

from jsonschema import Draft202012Validator
from referencing import Resource
import yaml

from test_draft202012_and_examples import schema_registry

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import propose_unix_file_schema_integration as integration


class UnixFileCanonicalIntegrationProposal(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.documents = integration.proposal()
        cls.capability = cls.documents[integration.DEST / 'capabilities/unix.file.schema.json']
        cls.registry = schema_registry().with_resources(
            (doc['$id'], Resource.from_contents(doc)) for doc in cls.documents.values())

    def validator(self, uri):
        return Draft202012Validator({'$ref': uri}, registry=self.registry)

    def test_candidate_files_are_deterministic_and_schema_valid(self):
        self.assertEqual(self.documents, integration.proposal())
        for file, doc in self.documents.items():
            self.assertEqual((ROOT / file).read_bytes(), (json.dumps(doc, indent=2) + '\n').encode())
            Draft202012Validator.check_schema(doc)

    def test_all_23_contracts_have_shared_meanings_and_real_type_nodes(self):
        source, _, mapping, _, _ = integration.load_schemas()
        defs = self.capability['$defs']
        self.assertEqual(defs['field_meanings'], source['$defs']['field_meanings'])
        self.assertEqual(len(defs['item_fields']['properties']), 23)
        for name, node in defs['item_fields']['properties'].items():
            meaning = '#/$defs/field_meanings/properties/' + name
            self.assertEqual(node['$ref'], meaning)
            self.assertEqual(defs['require_fields']['properties'][name]['$ref'], meaning)
            tag = defs['value_' + name]['properties']['datatype']['$ref'].split('/')[-1]
            expected = mapping['field_datatypes'][name][0]
            self.assertEqual(defs[tag]['const'], expected)
            self.assertEqual(defs['value_' + name]['properties']['value']['type'], expected)

    def test_proposed_item_dispatch_and_exact_compatibility_delta(self):
        future = self.validator(integration.NEXT + 'collected-item.schema.json')
        frozen = self.validator(integration.PREFIX + 'collected-item.schema.json')
        field = {'datatype': 'integer', 'status': 'exists', 'value': 1000}
        base = {'id': 'example', 'capability': 'unix.file', 'status': 'exists',
                'fields': {'owner_uid': field}, 'provenance': {}}
        for change in [field, [field, field], {'datatype': 'integer', 'status': 'error'},
                       {'datatype': 'integer', 'status': 'does_not_exist'}]:
            value = dict(base, fields={'owner_uid': change})
            self.assertTrue(frozen.is_valid(value)); self.assertTrue(future.is_valid(value))
        for change in [dict(field, datatype='string', value='1000'),
                       dict(field, value='1000'), dict(field, value=1.5), dict(field, value=True)]:
            value = dict(base, fields={'owner_uid': change})
            self.assertTrue(frozen.is_valid(value)); self.assertFalse(future.is_valid(value))
            # Other capabilities retain their existing generic contract.
            self.assertTrue(future.is_valid(dict(value, capability='unrelated.capability')))
        self.assertTrue(future.is_valid(dict(base, fields={'future_field': field})))
        self.assertFalse(future.is_valid(dict(base, fields={'owner_uid': dict(field, status='error')})))

    def test_assessment_dispatch_requirements_and_presence_remain_distinct(self):
        frozen = self.validator(integration.PREFIX + 'assessment.schema.json')
        future = self.validator(integration.NEXT + 'assessment.schema.json')
        # Existing examples of other capabilities retain acceptance.
        for file in (ROOT / 'examples').glob('*.yaml'):
            value = yaml.safe_load(file.read_text())
            frozen.validate(value); future.validate(value)
        document = yaml.safe_load((ROOT / 'examples/linux-home-nosuid.assessment.yaml').read_text())
        test = {'test_title': 'Example', 'capability': 'unix.file', 'reported_elements': 'all',
                'object': {'filepath': {'equals': '/example'}},
                'require': {'item_requirement': {'items_found': 'none'}}}
        document['assessment']['tests'] = {'example-test': test}
        frozen.validate(document); future.validate(document)
        requirement = {'item_requirement': {'items_found': 'one_or_more', 'items_satisfying': 'every'},
                       'field_requirement': {'values_found': 'one_or_more', 'values_matching': 'every'},
                       'fields': {'owner_uid': {'datatype': 'integer', 'equals': 1000}}}
        test['require'] = requirement
        frozen.validate(document); future.validate(document)
        requirement['fields']['owner_uid'] = {'datatype': 'string', 'equals': '1000'}
        self.assertTrue(frozen.is_valid(document)); self.assertFalse(future.is_valid(document))
        # Omitted comparison datatypes remain inferred; this proposal does not
        # pretend to replace the semantic compiler's operand checks.
        requirement['fields']['owner_uid'] = {'equals': 1000}
        future.validate(document)
        condition = {'fields': requirement.pop('fields')}
        requirement['and'] = [condition]
        frozen.validate(document); future.validate(document)
        condition['fields']['owner_uid'] = {'datatype': 'string', 'equals': '1000'}
        self.assertTrue(frozen.is_valid(document)); self.assertFalse(future.is_valid(document))


if __name__ == '__main__':
    unittest.main()
