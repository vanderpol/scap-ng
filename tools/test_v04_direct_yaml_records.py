"""Pinned OpenSCAP originals, native operands and YAML record-key identity."""
from copy import deepcopy
from hashlib import sha1, sha256
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

from lxml import etree
from audit_v04_oval_test_corpus import OvalDocument, assessment_for, check_conversion, closure
from audit_v04_eight_assessment_pilot import verify_program
from oval_source_validation import SourceValidator
from v04_direct_converter import AssessmentConverter, load_mappings
from v04_direct_inventory import SourceInventory
from v04_direct_scap_source import UnsupportedSource, digest
from v04_direct_yaml_records import yaml_record_key
from v04_expanded_source_proof import ExpandedSource, ExpandedNative
from v04_native_bundle_compiler import compile_assessment_program, build_bundle, verify_bundle
from v04_a_dataflow_index import index_assessment_dataflow
from v04_field_requirement import validate_test
from v04_yaml_source_proof import original_key
from validate_native_json_schemas import build_validators, document_errors

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tests/fixtures/v04-direct-yaml'
O = '{http://oval.mitre.org/XMLSchema/oval-definitions-5}'
I = '{http://oval.mitre.org/XMLSchema/oval-definitions-5#independent}'
CAP = 'independent.yamlfilecontent'


class DirectYamlRecordsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pin = json.loads((FIXTURE / 'provenance.json').read_text())
        cls.mappings = load_mappings()
        cls.validator = build_validators(ROOT / 'schema/v0.4.0')['assessment.schema.json']
        cls.source_validator = SourceValidator(ROOT / 'third_party/scap-1.4-schemas/oval_5.12.3')

    def visitor(self, root):
        return AssessmentConverter(OvalDocument(root, 'original.xml'), 'original.xml', self.mappings)

    def root(self, name='key'):
        return ET.fromstring((FIXTURE / ('test_probes_yamlfilecontent_' + name + '.xml')).read_bytes())

    def compiled_roundtrip(self, assessment):
        # Explicitly constructed packaging metadata. This is not an original
        # SCAP Benchmark/Rule conversion or an additional production proof.
        benchmark = {'id': 'yaml-integration-fixture', 'ng_schema_version': '0.4.0',
            'use_case': 'compliance', 'version': {'value': '1'},
            'assessment_specifications': [{'id': 'scap-ng.pre-alpha.assessment', 'version': '0.4.0'}],
            'title': [{'text': 'Constructed YAML compilation fixture', 'language': 'en'}],
            'description': [], 'language': 'en', 'status': [], 'metadata': {'constructed_wrapper': True},
            'notices': [], 'front_matter': [], 'rear_matter': [], 'references': [], 'text_blocks': [],
            'platform': {'id': 'fixture-platform', 'title': 'No platform claim', 'applicability': {}},
            'applicability_catalog': 'fixture-applicability', 'scoring': [], 'parameters': [],
            'default_selection': True, 'groups': [], 'profiles': [], 'rules': ['fixture-rule']}
        rule = {'id': 'fixture-rule', 'version': '1', 'title': 'Constructed packaging wrapper',
            'severity': 'unknown', 'role': 'full', 'weight': 1, 'discussion': '', 'rationale': None,
            'extensions': {}, 'warnings': [], 'identifiers': [], 'references': [], 'requires': [],
            'conflicts': [], 'applicability': [], 'parameters': {}, 'remediation': {},
            'organizational_input_requirements': {},
            'assessment_choices': {'automated': {'assessment': assessment['id']}},
            'default_assessment_choice': 'automated'}
        prefix = 'authoring/yaml-integration-fixture/'
        documents = {prefix + 'benchmark.json': {'benchmark': benchmark},
            prefix + 'rules/fixture-rule.json': {'rule': rule},
            prefix + 'applicability.json': {'applicability': {'id': 'fixture-applicability', 'conditions': {}}},
            prefix + 'assessments/original.json': {'assessment': assessment}}
        compiled, _ = build_bundle(documents)
        result = verify_bundle(compiled)
        self.assertEqual(result['programs'], 1)
        self.assertFalse(result['scanner_evaluated'])

    def terms(self, root, ident='oval:0:tst:1'):
        visitor = self.visitor(root)
        a = assessment_for(visitor, ident)
        self.assertFalse(list(document_errors(self.validator, {'assessment': a})))
        index_assessment_dataflow(a)
        for test in a['tests'].values(): validate_test(test)
        source = ExpandedSource(root).test(ident)
        native = ExpandedNative(a).test(a['evaluate']['test'])
        self.assertEqual(source, native)
        verify_program(a, compile_assessment_program(a))
        return a, source

    def test_51_original_sources_45_convert_compile_and_prove_six_explicitly_unsupported(self):
        expected = json.loads((FIXTURE / 'conversion-evidence.json').read_text())
        rows = []
        for item in self.pin['files']:
            raw = (FIXTURE / item['path']).read_bytes()
            self.assertEqual(sha256(raw).hexdigest(), item['sha256'])
            self.assertEqual(sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest(), item['git_blob'])
            if not item['path'].endswith('.xml'):
                continue
            root = ET.fromstring(raw); before = ET.tostring(root)
            validity = self.source_validator.validate(etree.fromstring(raw))
            self.assertEqual(validity['status'], 'VALID', validity)
            self.assertFalse(validity['issues'])
            nodes = {i: n for (_, i), n in SourceInventory(OvalDocument(root, 'original.xml')).nodes.items()}
            for test in root.find(O + 'tests'):
                ident = test.get('id'); visitor = self.visitor(root)
                result = check_conversion(visitor, ident, self.validator)
                rows.append({'source': item['path'], 'test': ident, **result})
                if result['compiled']:
                    ids, problems = closure(nodes, ident)
                    self.assertFalse(problems)
                    self.assertEqual(set(ids), set(visitor.used))
                    a = assessment_for(visitor, ident)
                    index_assessment_dataflow(a)
                    for native_test in a['tests'].values(): validate_test(native_test)
                    self.compiled_roundtrip(a)
                    self.assertEqual(result['source_proof'], 'PROVED', result)
            self.assertEqual(ET.tostring(root), before)
            self.assertEqual((FIXTURE / item['path']).read_bytes(), raw)
        self.assertEqual(sorted(rows, key=lambda r: (r['source'], r['test'])),
                         sorted(expected['cases'], key=lambda r: (r['source'], r['test'])))
        self.assertEqual(len(rows), 51)
        self.assertEqual(sum(r['compiled'] for r in rows), 45)
        self.assertEqual(sum(r['source_proof'] == 'PROVED' for r in rows), 45)
        self.assertEqual(sum(any('unsupported function: split' in d['message'] for d in r['diagnostics']) for r in rows), 3)
        self.assertEqual(sum(any('record_field' in d['message'] for d in r['diagnostics']) for r in rows), 3)

    def test_caret_transport_decodes_once_without_changing_other_record_capabilities(self):
        cases = {'my^camel^case^^^key': 'myCamelCase^Key', '^^a': '^a', '^a': 'A',
                 '#': '#', 'already_lower': 'already_lower', 'a^^^^b': 'a^^b'}
        for encoded, native in cases.items():
            self.assertEqual(yaml_record_key(encoded), native)
            self.assertEqual(original_key(encoded), native)
        for invalid in ('dangling^', 'bad^7', 'bad^_'):
            with self.assertRaises(ValueError): yaml_record_key(invalid)
            with self.assertRaises(ValueError): original_key(invalid)
        root = self.root(); entity = root.find(O + 'states')[0][0]
        entity[0].set('name', '^^a')
        ET.SubElement(entity, O + 'field', name='^a', datatype='string').text = 'different key'
        a, _ = self.terms(root)
        fields = next(iter(a['tests'].values()))['require']['fields']['value']['record']['fields']
        self.assertEqual(set(fields), {'^a', 'A'})
        field = entity[0]; field.set('name', 'bad^7')
        with self.assertRaises(ValueError): self.terms(root)

    def test_record_field_identity_and_quantifier_mutations_are_detected(self):
        a, source = self.terms(self.root(), 'oval:0:tst:6')
        test_id = a['evaluate']['test']
        record = a['tests'][test_id]['require']['fields']['value']['record']
        self.assertIn('lastTransitionTime', record['fields'])
        for mutation in ('key', 'record-check', 'field-check'):
            changed = deepcopy(a); r = changed['tests'][test_id]['require']['fields']['value']['record']
            if mutation == 'key': r['fields']['last^transition^time'] = r['fields'].pop('lastTransitionTime')
            elif mutation == 'record-check': r['records_matching'] = 'none'
            else: r['fields']['status']['values_matching'] = 'none'
            self.assertFalse(list(document_errors(self.validator, {'assessment': changed})))
            self.assertNotEqual(ExpandedNative(changed).test(test_id), source)
        program = compile_assessment_program(a)
        changed = deepcopy(a); changed['tests'][test_id]['object']['yamlpath']['equals'] = '.different'
        with self.assertRaises(ValueError): verify_program(changed, program)

    def test_typed_static_values_and_runtime_variable_references_keep_var_check(self):
        for kind in ('constant_variable', 'local_variable'):
            root = self.root(); field = root.find(O + 'states')[0][0][0]
            field.text = None; field.set('var_ref', 'oval:yaml.derived:var:1')
            field.set('var_check', 'none satisfy'); field.set('entity_check', 'at least one')
            variables = ET.SubElement(root, O + 'variables')
            variable = ET.SubElement(variables, O + kind, id='oval:yaml.derived:var:1', version='1', datatype='string',
                                     comment='Controlled record-field Variable regression')
            if kind == 'constant_variable':
                for value in ('LogForwarding', 'Other', 'Other'): ET.SubElement(variable, O + 'value').text = value
            else:
                ET.SubElement(variable, O + 'object_component', object_ref='oval:0:obj:2', item_field='yamlpath')
            validity = self.source_validator.validate(etree.fromstring(ET.tostring(root)))
            self.assertEqual(validity['status'], 'VALID', validity)
            a, _ = self.terms(root)
            p = next(iter(a['tests'].values()))['require']['fields']['value']['record']['fields']['#']
            self.assertEqual(p['datatype'], 'string')
            self.assertEqual(p['value_match'], 'none')
            self.assertEqual(p['values_matching'], 'one_or_more')
            if kind == 'constant_variable': self.assertEqual(p['equals'], ['LogForwarding', 'Other', 'Other'])
            else: self.assertIn(p['equals']['variable'], a['variables'])

    def test_file_inline_alternatives_traversal_and_invalid_query_comparators(self):
        root = self.root(); obj = root.find(O + 'objects')[0]
        obj[0].text = '/tmp/openshift-logging_key.yaml'; obj[0].tag = I + 'filepath'; obj.remove(obj[1])
        self.terms(root)
        for field in ('content', 'yamlpath'):
            derived = self.root('content'); target = derived.find(O + 'objects')[0].find(I + field)
            target.set('operation', 'not equal')
            with self.assertRaisesRegex(UnsupportedSource, 'requires equality'): self.terms(derived)
        ET.SubElement(obj, I + 'content').text = '{}'
        with self.assertRaisesRegex(UnsupportedSource, 'alternatives'): self.terms(root)
        root = self.root(); obj = root.find(O + 'objects')[0]
        obj.insert(0, ET.Element(I + 'behaviors', max_depth='2', recurse_direction='down', recurse='directories'))
        a, _ = self.terms(root)
        self.assertEqual(next(iter(a['tests'].values()))['object']['traversal'], {'max_depth': 2, 'recurse': 'directories'})
        obj[0].set('recurse_direction', 'up')
        with self.assertRaises(UnsupportedSource): self.terms(root)

    def test_nested_sets_and_ordered_filters_preserve_record_predicates(self):
        root = self.root(); objects = root.find(O + 'objects'); obj = objects[0]
        leaf = deepcopy(obj); leaf.set('id', 'oval:yaml.derived:obj:1'); objects.append(leaf)
        obj[:] = []; outer = ET.SubElement(obj, O + 'set', set_operator='COMPLEMENT')
        inner = ET.SubElement(outer, O + 'set', set_operator='UNION')
        ET.SubElement(inner, O + 'object_reference').text = leaf.get('id')
        ET.SubElement(inner, O + 'filter', action='include').text = 'oval:0:ste:1'
        ET.SubElement(inner, O + 'filter', action='exclude').text = 'oval:0:ste:2'
        a, term = self.terms(root)
        self.assertEqual(len(a.get('shared_objects', {})), 0)
        obj = next(iter(a['tests'].values()))['object']
        filters = obj['set']['operands'][0]['set']['operands'][0]['filters']
        filters.reverse()
        self.assertNotEqual(ExpandedNative(a).test(a['evaluate']['test']), term)

    def test_conversion_is_repeatable_and_does_not_fold_runtime_errors_or_missing_values(self):
        root = self.root(); first, _ = self.terms(root, 'oval:0:tst:3')
        second, _ = self.terms(root, 'oval:0:tst:3')
        self.assertEqual(digest(compile_assessment_program(first)), digest(compile_assessment_program(second)))
        # Original non-scalar query and absent-key query are retained, not
        # precomputed into false/zero/empty Items during conversion.
        for ident, query in (('oval:0:tst:3', '.metadata'), ('oval:0:tst:4', '.doesnt.exist')):
            a, _ = self.terms(root, ident)
            test = next(iter(a['tests'].values()))
            self.assertEqual(test['object']['yamlpath'], {'equals': query})
            self.assertNotIn('items', test['object'])

    def test_duplicate_keys_whole_record_variables_and_unknown_source_fields_fail_closed(self):
        for mutation in ('duplicate', 'whole-record-var', 'unknown-field', 'uppercase'):
            root = self.root(); value = root.find(O + 'states')[0][0]
            if mutation == 'duplicate': value.append(deepcopy(value[0]))
            elif mutation == 'whole-record-var': value.set('var_ref', 'oval:yaml.derived:var:1')
            elif mutation == 'unknown-field': ET.SubElement(root.find(O + 'objects')[0], I + 'script').text = 'no'
            else: value[0].set('name', 'InvalidUppercase')
            with self.subTest(mutation=mutation), self.assertRaises(UnsupportedSource):
                assessment_for(self.visitor(root), 'oval:0:tst:1')
