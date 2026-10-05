#!/usr/bin/env python3
"""Source-backed schema/graph and synthetic ESXi identity/software fixtures."""
import copy
import json
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
import yaml
from jsonschema import Draft202012Validator, ValidationError
from capability_registry import ROOT, load_mapping
from generate_capability_schema import generate, direct_global, immediate_payload_elements, restriction_values
from assessment_results_v02 import item_validator
from reported_elements import project_items
from validate_native_json_schemas import build_validators, document_errors
from validate_generated_capability_semantics import validate_assessment_capability_semantics
from scap_ng_content_compiler import validate_draft_expression_assessments, compile_benchmark, write_bundle, verify_bundle

SUITE = ROOT / 'tests/esx-host-0.2.0'
LEVELS = ['VMwareCertified', 'VMwareAccepted', 'PartnerSupported', 'CommunitySupported', 'Unknown']

class IdentitySoftwareTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.documents = {k: yaml.safe_load((SUITE / 'content' / (k + '.assessment.yaml')).read_text()) for k in ['account', 'vib']}
        cls.validators = build_validators(ROOT / 'schema/v0.2.0')

    def errors(self, doc):
        return list(document_errors(self.validators['assessment.schema.json'], doc))

    def item(self, kind):
        return json.loads((SUITE / (kind + '-item.json')).read_text())

    def test_fields_match_pinned_declarations(self):
        definitions = ET.parse(ROOT / 'third_party/oval-6.0-new-tests/esx-definitions-schema.xsd').getroot()
        characteristics = ET.parse(ROOT / 'third_party/oval-6.0-new-tests/esx-system-characteristics-schema.xsd').getroot()
        for kind in self.documents:
            mapping = load_mapping('esx.host_' + kind)
            native = mapping['native']
            state = immediate_payload_elements(direct_global(definitions, 'element', 'host_' + kind + '_state'))
            item = immediate_payload_elements(direct_global(characteristics, 'element', 'host_' + kind + '_item'))
            self.assertEqual(set(native['state_field_map']), set(state) - {'host_' + kind + '_state'})
            self.assertEqual(set(native['state_field_map']), set(item) - {'host_' + kind + '_item'})
            self.assertTrue(all(v.get('maxOccurs') == '1' for k, v in item.items() if k != 'host_' + kind + '_item'))
            schema = generate(mapping, ROOT)
            Draft202012Validator.check_schema(schema)
            fields = schema['$defs']['collected_item']['allOf'][1]['properties']['fields']['properties']
            for name, description in native['field_documentation'].items():
                self.assertEqual(fields[name]['description'], description)
            with self.assertRaises(ValueError):
                load_mapping(mapping['capability'], '0.1.0')
        self.assertEqual(restriction_values(direct_global(characteristics, 'complexType', 'EntityItemAcceptanceLevelType')), LEVELS)
        self.assertEqual(restriction_values(direct_global(definitions, 'complexType', 'EntityStateAcceptanceLevelType')), LEVELS + [''])
        self.assertEqual(state['version'].get('type'), 'oval-def:EntityStateStringType')

    def test_standalone_and_preflight(self):
        for doc in self.documents.values():
            self.assertFalse(self.errors(doc))
            self.assertFalse(validate_assessment_capability_semantics(doc))
            a = doc['assessment']
            validate_draft_expression_assessments({a['id']: a})
            bad = copy.deepcopy(doc)
            bad['assessment']['specification']['version'] = '0.1.0'
            bad['assessment']['tests']['test-check'].pop('reported_elements')
            self.assertTrue(self.errors(bad))

    def test_reject_invalid_unused_nodes_and_cross_capability(self):
        for kind, doc in self.documents.items():
            for mutation in ['selector', 'datatype', 'field', 'cross-object', 'cross-state', 'unused-test']:
                bad = copy.deepcopy(doc); a = bad['assessment']
                if mutation == 'selector': a['objects']['selected']['select'] = {}
                elif mutation == 'datatype': a['states']['expected']['state']['datatype'] = 'integer'
                elif mutation == 'field': a['states']['expected']['state']['field'] = 'invented'
                elif mutation == 'cross-object': a['objects']['selected'] = copy.deepcopy(self.documents['account' if kind == 'vib' else 'vib']['assessment']['objects']['selected'])
                elif mutation == 'cross-state': a['states']['expected'] = copy.deepcopy(self.documents['account' if kind == 'vib' else 'vib']['assessment']['states']['expected'])
                else:
                    a['tests']['test-unused'] = copy.deepcopy(a['tests']['test-check'])
                    a['tests']['test-unused']['reported_elements'] = ['invented']
                with self.subTest(kind=kind, mutation=mutation):
                    if mutation.startswith('cross-'):
                        self.assertTrue(validate_assessment_capability_semantics(bad))
                    else:
                        self.assertTrue(self.errors(bad))
                    with self.assertRaises(ValueError): validate_draft_expression_assessments({a['id']: a})

    def test_acceptance_levels_and_xml_placeholder(self):
        doc = copy.deepcopy(self.documents['vib'])
        for value in LEVELS:
            doc['assessment']['states']['expected']['state']['value'] = value
            self.assertFalse(self.errors(doc))
            item = self.item('vib'); item['fields']['acceptance_level']['value'] = value
            item_validator(item['capability']).validate(item)
        for value in ['', 'vmwarecertified', 'invented']:
            doc['assessment']['states']['expected']['state']['value'] = value
            self.assertTrue(self.errors(doc))
            item = self.item('vib'); item['fields']['acceptance_level']['value'] = value
            with self.assertRaises(ValidationError): item_validator(item['capability']).validate(item)
        # NG references a Variable directly; XML's empty placeholder is unnecessary.
        doc['assessment']['variables'] = {'required-level': {'variable_title': 'Expected category', 'constant': {'datatype': 'string', 'values': ['VMwareCertified']}}}
        doc['assessment']['states']['expected']['state']['value'] = {'variable': 'required-level'}
        self.assertFalse(self.errors(doc))

    def test_items_status_redaction_and_types(self):
        for kind in self.documents:
            item = self.item(kind); validator = item_validator(item['capability']); validator.validate(item)
            field = 'shell_access_enabled' if kind == 'account' else 'acceptance_level'
            dtype = 'boolean' if kind == 'account' else 'string'
            for status in ['does_not_exist', 'not_collected', 'error']:
                changed = copy.deepcopy(item); changed['fields'][field] = {'datatype': dtype, 'status': status}
                validator.validate(changed)
            changed = copy.deepcopy(item); changed['fields'][field] = {'datatype': dtype, 'status': 'exists', 'redacted': True}
            validator.validate(changed)
            changed['fields'][field]['value'] = item['fields'][field]['value']
            with self.assertRaises(ValidationError): validator.validate(changed)
            changed = copy.deepcopy(item); changed['fields'][field] = [changed['fields'][field]]
            with self.assertRaises(ValidationError): validator.validate(changed)
        bad = self.item('account'); bad['fields']['shell_access_enabled']['value'] = 'false'
        with self.assertRaises(ValidationError): item_validator(bad['capability']).validate(bad)
        bad = self.item('vib'); bad['fields']['version']['datatype'] = 'version'
        with self.assertRaises(ValidationError): item_validator(bad['capability']).validate(bad)

    def test_known_result_oracle(self):
        cases = json.loads((SUITE / 'expected-results/identity-software.json').read_text())['comparisons']
        for case in cases:
            state = self.documents[case['content']]['assessment']['states']['expected']['state']
            self.assertEqual(state['value'], case['expected'])
            self.assertEqual('true' if case['observed'] == case['expected'] else 'false', case['outcome'])
            self.assertTrue(case['reason'])

    def test_reporting_retains_identity_and_redaction(self):
        for kind in self.documents:
            a = self.documents[kind]['assessment']; item = self.item(kind)
            field = a['states']['expected']['state']['field']; identity = 'account_name' if kind == 'account' else 'vib_name'
            required = [identity, 'domain'] if kind == 'account' else [identity]
            item['fields'][field] = {'datatype': 'boolean' if kind == 'account' else 'string', 'status': 'exists', 'redacted': True}
            report = project_items(a, [item], [{'test_ref': 'test-check', 'item_ref': item['id'], 'used_elements': [field], 'required_elements': required, 'relationship': 'direct'}], source_execution_ref='fixture-execution', source_completeness={'logical_complete': True, 'population_complete': True, 'evidence_complete': True})
            fields = report['item_report']['items'][0]['item']['fields']
            self.assertEqual(set(fields), {field, *required})
            self.assertTrue(fields[field]['redacted']); self.assertNotIn('value', fields[field])

    def test_unsigned_compilation_and_verification(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); bench = root / 'benchmark'
            def dump(path, data):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(yaml.safe_dump(data, sort_keys=False), encoding='utf-8')
            dump(bench / 'benchmark.yaml', {'benchmark': {'id': 'esx.identity-software.benchmark', 'version': {'value': '1'}, 'rules': list(self.documents), 'profiles': []}})
            for kind, doc in self.documents.items():
                dump(bench / 'assessments' / (kind + '.assessment.yaml'), doc)
                dump(bench / 'rules' / (kind + '.rule.yaml'), {'rule': {'id': kind, 'assessment_choices': {'automated': {'assessment': '../assessments/' + kind + '.assessment.yaml'}}, 'default_assessment_choice': 'automated'}})
            benchmark, members, index = compile_benchmark(root, bench)
            caps = {json.loads(members[row['path']])['assessment']['tests']['test-check']['capability'] for row in index.values() if row['type'] == 'assessment'}
            self.assertEqual(caps, {'esx.host_account', 'esx.host_vib'})
            package = root / 'fixture.scapng'; write_bundle(package, benchmark, members, index, sign_self_signed=False, provenance={})
            self.assertEqual(verify_bundle(package)['benchmark_id'], 'esx.identity-software.benchmark')

if __name__ == '__main__': unittest.main()
