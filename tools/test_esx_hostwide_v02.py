#!/usr/bin/env python3
"""Pinned source and synthetic host-wide evidence; no live VMware collection."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET
import yaml
from jsonschema import Draft202012Validator, ValidationError
from capability_registry import ROOT, load_mapping, mappings
from generate_capability_schema import generate, direct_global, immediate_payload_elements, restriction_values
from assessment_results_v02 import item_validator
from validate_native_json_schemas import build_validators, document_errors
from validate_generated_capability_semantics import validate_assessment_capability_semantics
from scap_ng_content_compiler import validate_draft_expression_assessments, compile_benchmark, write_bundle, verify_bundle
from reported_elements import project_items
from oval_result_truth_tables import aggregate_check

KINDS = ['acceptancelevel', 'lockdown', 'ntpserver', 'coredump', 'authentication']
SUITE = ROOT / 'tests/esx-host-0.2.0'

class HostwideTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.docs = {k: yaml.safe_load((SUITE / 'content' / (k + '.assessment.yaml')).read_text()) for k in KINDS}
        cls.validators = build_validators(ROOT / 'schema/v0.2.0')

    def errors(self, doc):
        return list(document_errors(self.validators['assessment.schema.json'], doc))

    def item(self, kind):
        return json.loads((SUITE / (kind + '-item.json')).read_text())

    def test_source_fields_categories_cardinality_and_annotations(self):
        defs = ET.parse(ROOT / 'third_party/oval-6.0-new-tests/esx-definitions-schema.xsd').getroot()
        sc = ET.parse(ROOT / 'third_party/oval-6.0-new-tests/esx-system-characteristics-schema.xsd').getroot()
        for kind in KINDS:
            m = load_mapping('esx.host_' + kind)
            native = m['native']
            object_name = 'host_' + kind + '_object'
            self.assertEqual(set(immediate_payload_elements(direct_global(defs, 'element', object_name))), {object_name})
            states = immediate_payload_elements(direct_global(defs, 'element', 'host_' + kind + '_state'))
            items = immediate_payload_elements(direct_global(sc, 'element', 'host_' + kind + '_item'))
            states.pop('host_' + kind + '_state'); items.pop('host_' + kind + '_item')
            self.assertEqual(set(states), set(native['state_field_map']))
            self.assertEqual(set(items), set(native['state_field_map']))
            generated = generate(m, ROOT); Draft202012Validator.check_schema(generated)
            fields = generated['$defs']['collected_item']['allOf'][1]['properties']['fields']['properties']
            for name in states:
                self.assertEqual(fields[name]['description'], native['field_documentation'][name])
                self.assertEqual(fields[name].get('type') == 'array', items[name].get('maxOccurs') == 'unbounded')
            for field, values in native.get('state_value_enums', {}).items():
                for root, elements, key in [(defs, states, 'state_value_enums'), (sc, items, 'item_value_enums')]:
                    type_name = elements[field].get('type').split(':')[1]
                    declared = restriction_values(direct_global(root, 'complexType', type_name))
                    self.assertEqual([v for v in declared if v], native[key][field])
        # Item-side placeholder is real upstream syntax, separately documented.
        self.assertIn('', restriction_values(direct_global(sc, 'complexType', 'EntityItemDomainMembershipStatusType')))

    def test_valid_content_version_isolation_and_preflight(self):
        self.assertEqual(len(mappings('0.1.0')), 100)
        for kind, doc in self.docs.items():
            self.assertFalse(self.errors(doc)); self.assertFalse(validate_assessment_capability_semantics(doc))
            a = doc['assessment']; validate_draft_expression_assessments({a['id']: a})
            with self.assertRaises(ValueError): load_mapping('esx.host_' + kind, '0.1.0')
            bad = copy.deepcopy(doc); bad['assessment']['specification']['version'] = '0.1.0'
            self.assertTrue(self.errors(bad))

    def test_selectorless_form_is_explicit_and_exclusive(self):
        for kind, doc in self.docs.items():
            for mutation in ['omit', 'null', 'invent', 'set-and-select', 'unused']:
                bad = copy.deepcopy(doc); a = bad['assessment']; obj = a['objects']['selected']
                if mutation == 'omit': obj.pop('select')
                elif mutation == 'null': obj['select'] = None
                elif mutation == 'invent': obj['select'] = {'host_name': {'datatype': 'string', 'operation': 'equal', 'value': 'host'}}
                elif mutation == 'set-and-select': obj['set'] = {'operator': 'union', 'operands': [{'object': 'selected', 'filters': []}]}
                else:
                    a['objects']['unused'] = copy.deepcopy(obj); a['objects']['unused']['select'] = None
                with self.subTest(kind=kind, mutation=mutation):
                    self.assertTrue(self.errors(bad))
                    with self.assertRaises(ValueError): validate_draft_expression_assessments({a['id']: a})
        m = load_mapping('esx.host_service'); m['native']['selectorless_object'] = True
        with self.assertRaises(ValueError): generate(m, ROOT)
        m = load_mapping('esx.host_lockdown'); m['specification_version'] = '0.1.0'
        with self.assertRaises(ValueError): generate(m, ROOT)

    def test_single_operand_filtered_set_and_compatible_graph(self):
        for kind, doc in self.docs.items():
            changed = copy.deepcopy(doc); a = changed['assessment']; cap = 'esx.host_' + kind
            a['objects']['filtered'] = {'object_title': 'Filtered host observations', 'capability': cap,
                'set': {'operator': 'union', 'operands': [{'object': 'selected', 'filters': [{'state': 'expected', 'action': 'include'}]}]}}
            a['tests']['test-check']['object'] = 'filtered'
            self.assertFalse(self.errors(changed)); self.assertFalse(validate_assessment_capability_semantics(changed))
            validate_draft_expression_assessments({a['id']: a})
            a['objects']['selected'] = copy.deepcopy(self.docs['coredump' if kind != 'coredump' else 'lockdown']['assessment']['objects']['selected'])
            self.assertTrue(validate_assessment_capability_semantics(changed))
            with self.assertRaises(ValueError): validate_draft_expression_assessments({a['id']: a})

    def test_item_types_repeated_values_and_status_redaction(self):
        for kind in KINDS:
            item = self.item(kind); v = item_validator(item['capability']); v.validate(item)
            for field, observed in item['fields'].items():
                repeated = isinstance(observed, list); entity = observed[0] if repeated else observed
                for status in ['does_not_exist', 'not_collected', 'error']:
                    bad = copy.deepcopy(item); value = {'datatype': entity['datatype'], 'status': status}
                    bad['fields'][field] = [value] if repeated else value; v.validate(bad)
                bad = copy.deepcopy(item); value = {'datatype': entity['datatype'], 'redacted': True}
                bad['fields'][field] = [value] if repeated else value; v.validate(bad)
                value['value'] = entity['value']
                with self.assertRaises(ValidationError): v.validate(bad)
                bad = copy.deepcopy(item); bad['fields'][field] = entity if repeated else [entity]
                with self.assertRaises(ValidationError): v.validate(bad)
        bad = self.item('coredump'); bad['fields']['enabled']['value'] = 'true'
        with self.assertRaises(ValidationError): item_validator(bad['capability']).validate(bad)
        bad = self.item('coredump'); bad['fields']['network_server_port']['value'] = '6500'
        with self.assertRaises(ValidationError): item_validator(bad['capability']).validate(bad)
        for kind, field in [('acceptancelevel', 'acceptance_level'), ('lockdown', 'lockdown'), ('authentication', 'domain_membership_status')]:
            doc = copy.deepcopy(self.docs[kind]); values = load_mapping('esx.host_' + kind)['native']['state_value_enums'][field]
            for value in values:
                doc['assessment']['states']['expected']['state']['value'] = value; self.assertFalse(self.errors(doc))
                item = self.item(kind); item['fields'][field]['value'] = value; item_validator(item['capability']).validate(item)
            for value in ['', 'invented']:
                doc['assessment']['states']['expected']['state']['value'] = value; self.assertTrue(self.errors(doc))
                item = self.item(kind); item['fields'][field]['value'] = value
                with self.assertRaises(ValidationError): item_validator(item['capability']).validate(item)

    def test_synthetic_equality_and_entity_quantifiers(self):
        cases = json.loads((SUITE / 'expected-results/hostwide.json').read_text())['comparisons']
        for case in cases:
            state = self.docs[case['content']]['assessment']['states']['expected']['state']
            self.assertEqual(state['value'], case['expected']); self.assertTrue(case['reason'])
            values = case['observed'] if isinstance(case['observed'], list) else [case['observed']]
            rows = ['true' if value == case['expected'] else 'false' for value in values]
            self.assertEqual(aggregate_check('all', rows), case['outcome'])
        self.assertEqual(aggregate_check('all', ['true', 'false']), 'false')
        self.assertEqual(aggregate_check('at least one', ['true', 'false']), 'true')

    def test_reporting_keeps_repetitions_redaction_and_target(self):
        for kind in KINDS:
            a = self.docs[kind]['assessment']; item = self.item(kind)
            field = a['states']['expected']['state']['field']
            report = project_items(a, [item], [{'test_ref': 'test-check', 'item_ref': item['id'], 'used_elements': [field], 'required_elements': []}],
                source_execution_ref='fixture-execution', source_completeness={'logical_complete': True, 'population_complete': True, 'evidence_complete': True})
            projected = report['item_report']['items'][0]['item']
            self.assertEqual(projected['fields'][field], item['fields'][field])
            self.assertEqual(projected['provenance']['target_ref'], 'fixture-esxi-host')

    def test_actual_unsigned_compilation(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); bench = root / 'benchmark'
            def dump(path, data):
                path.parent.mkdir(parents=True, exist_ok=True); path.write_text(yaml.safe_dump(data, sort_keys=False), encoding='utf-8')
            dump(bench / 'benchmark.yaml', {'benchmark': {'id': 'esx.hostwide.fixture', 'version': {'value': '1'}, 'rules': KINDS, 'profiles': []}})
            for kind, doc in self.docs.items():
                dump(bench / 'assessments' / (kind + '.assessment.yaml'), doc)
                dump(bench / 'rules' / (kind + '.rule.yaml'), {'rule': {'id': kind, 'assessment_choices': {'automated': {'assessment': '../assessments/' + kind + '.assessment.yaml'}}, 'default_assessment_choice': 'automated'}})
            benchmark, members, index = compile_benchmark(root, bench)
            caps = {json.loads(members[row['path']])['assessment']['tests']['test-check']['capability'] for row in index.values() if row['type'] == 'assessment'}
            self.assertEqual(caps, {'esx.host_' + k for k in KINDS})
            package = root / 'hostwide.scapng'; write_bundle(package, benchmark, members, index, sign_self_signed=False, provenance={})
            self.assertEqual(verify_bundle(package)['benchmark_id'], 'esx.hostwide.fixture')

if __name__ == '__main__': unittest.main()
