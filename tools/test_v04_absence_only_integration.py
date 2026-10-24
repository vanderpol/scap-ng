#!/usr/bin/env python3
"""Pinned OVAL absence integration; record absence is an explicit XML control.

No scanner is implemented. Existence outcomes below come from the maintained
OVAL reference algebra, never from executing generated Assessments. Refs #251 #248.
"""
from copy import deepcopy
from hashlib import sha256
import io
import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile

from lxml import etree
import yaml

from build_v04_canonical_six_stigs import promote, recover, render_authoring, upgrade_v003
from scap_converter_core import convert
from scap_upconvert_v003.build_rhel9_review_slice import lower_definition
from scap_upconvert_v003.convert_collection_review import postprocess_automated_assessment
from scap_ng_roundtrip_v003.native_assessment_to_oval import build
from scap_ng_roundtrip_v003.compare_oval_semantics import compare
from test_v04_field_requirement_conversion import documents, compile_documents
from prove_v04_oval_macos_gatekeeper_source import source_to_native
from v04_canonical_source_ir import decode_and_verify
from v04_native_bundle_compiler import build_bundle, verify_bundle
from v04_field_requirement import promote_test, restore_test, validate_test, field_scopes
from oval_result_truth_tables import evaluate_state_entity_existence, evaluate_record_field

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / 'tests/fixtures/v04-absence-only'
OD = 'http://oval.mitre.org/XMLSchema/oval-definitions-5'


def predicates(node, name):
    if isinstance(node, dict):
        if name in node.get('fields', {}):
            yield node['fields'][name]
        for value in node.values():
            yield from predicates(value, name)
    elif isinstance(node, list):
        for value in node:
            yield from predicates(value, name)


class AbsenceOnlyIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for row in json.loads((FIXTURES / 'provenance.json').read_text())['files']:
            if sha256((FIXTURES / row['fixture']).read_bytes()).hexdigest() != row['sha256']:
                raise AssertionError('pinned original source changed: ' + row['fixture'])

    def compiled(self, native):
        text = render_authoring(native, is_yaml=True)
        self.assertEqual(yaml.safe_load(text), native)
        data, report = compile_documents(documents(yaml.safe_load(text)))
        self.assertEqual(report['native_source_schema'], 'PASS')
        self.assertEqual(report['yaml_json_byte_parity'], 'PASS')
        decoded = decode_and_verify(json.loads(data))
        self.assertEqual(decoded, documents(native))
        raw, manifest = build_bundle(decoded)
        checked = verify_bundle(raw)
        self.assertFalse(checked['scanner_evaluated'])
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            path = manifest['build_provenance']['compiled_programs'][native['assessment']['id']]['path']
            program = json.loads(archive.read(path))
        for instruction in program['test_instructions']:
            original = native['assessment']['tests'][instruction['test_id']]
            self.assertEqual(instruction['operands']['require'], original['require'])
        return program

    def test_original_gatekeeper_absence_and_inheritance_compile_without_matcher(self):
        raw = (FIXTURES / 'macos-def_gatekeeper_test.xml').read_bytes()
        original = source_to_native(raw)  # Independently verifies the original SHA/graph.
        native, _ = promote(original)
        recover(native, original)
        self.assertEqual(list(predicates(native, 'unlabeled')), [{'values_found': 'none'}])
        self.compiled(native)

        # Explicit absence overrides an inherited comparison pair, and receives
        # no synthetic matching count in the typed-IR index or native program.
        for test in native['assessment']['tests'].values():
            test['require']['field_requirement'] = {
                'values_found': 'one_or_more', 'values_matching': 'every'}
            validate_test(test)
            self.assertIn({'values_found': 'none'}, [
                row['field_requirement'] for row in field_scopes(test['require'])])
        self.compiled(native)

    def test_original_dns_missing_text_is_absence_not_an_empty_comparison(self):
        path = ROOT / 'research/assessment-simplification/evidence/ms_windows_server_dns/SV-259345/source-oval.xml'
        self.assertEqual(sha256(path.read_bytes()).hexdigest(),
                         '44411063be71910f348a31059b69338f3c83a68db4082cafeac198ff440f04d2')
        source = ET.parse(path).getroot()
        absent = [n for n in source.iter() if n.tag.endswith('}stdout_line')
                  and n.get('check_existence') == 'none_exist']
        self.assertEqual(len(absent), 2)
        for node in absent:
            self.assertIsNone(node.text)
            self.assertEqual(node.attrib, {'check_existence': 'none_exist'})
        native, evidence = convert(path, 'oval:navy.navwar.niwcatlantic.scc.windows:def:259345')
        self.assertEqual(evidence['original_oval_semantic_roundtrip'], 'PASS')
        values = list(predicates(native, 'stdout_line'))
        self.assertEqual(values.count({'values_found': 'none'}), 2)
        self.assertFalse(any(p.get('values_found') == 'none' and 'equals' in p for p in values))
        self.compiled(native)

        # Source-backed control: change only the original absence declaration
        # into a present-value comparison whose literal value is empty. This
        # must keep equals:"", not take the absence migration above.
        control = deepcopy(source)
        empty = next(n for n in control.iter() if n.tag.endswith('}stdout_line')
                     and n.get('check_existence') == 'none_exist')
        empty.set('check_existence', 'at_least_one_exists')
        empty.set('operation', 'equals')
        empty.text = ''
        lowered, error = lower_definition(control,
            'oval:navy.navwar.niwcatlantic.scc.windows:def:259345',
            'empty-string-control-assessment', collection_graph=True, provenance={})
        self.assertIsNone(error)
        aligned, _ = postprocess_automated_assessment(lowered, target_ng_version='0.3.0')
        compared, _ = upgrade_v003(aligned)
        operands = list(predicates(compared, 'stdout_line'))
        self.assertEqual(sum(p.get('equals') == '' for p in operands), 1)
        self.assertEqual(operands.count({'values_found': 'none'}), 1)
        self.compiled(compared)

    def test_record_absence_control_uses_original_wmi_parser_and_xsd(self):
        # Controlled variant, not a claim that the publisher shipped this case.
        original = ET.parse(FIXTURES / 'win-def_wmi57_object_test.xml').getroot()
        control = deepcopy(original)
        for state in control.findall('.//{' + OD + '#windows}wmi57_state'):
            records = state.findall('{' + OD + '#windows}result')
            self.assertTrue(records)
            for record in records:
                self.assertTrue(list(record))  # Original fixture has real comparisons.
                record.clear()
                record.set('datatype', 'record')
                record.set('check_existence', 'none_exist')
            schema = etree.XMLSchema(etree.parse(str(ROOT /
                'third_party/scap-1.4-schemas/oval_5.12.3/windows-definitions-schema.xsd')))
            schema.assertValid(etree.fromstring(ET.tostring(state)))
        did = 'oval:org.mitre.oval.test:def:10'
        old, error = lower_definition(control, did, 'record-absence-assessment',
                                      collection_graph=True, provenance={})
        self.assertIsNone(error)
        rebuilt, rebuilt_id = build(old)
        with tempfile.TemporaryDirectory() as td:
            source, reverse = Path(td) / 'original-control.xml', Path(td) / 'reverse.xml'
            ET.ElementTree(control).write(source, encoding='utf-8')
            rebuilt.write(reverse, encoding='utf-8')
            self.assertTrue(compare(source, reverse, did, rebuilt_id, root_only=True)['equal'])
        aligned, _ = postprocess_automated_assessment(old, target_ng_version='0.3.0')
        native, _ = upgrade_v003(aligned)
        self.assertEqual(list(predicates(native, 'result')), [{'record': {'records_found': 'none'}}])
        self.compiled(native)
        # The typed source compiler indexes the absent record without requiring
        # a matching cardinality or inventing any member-field obligations.
        test = next(iter(native['assessment']['tests'].values()))
        self.assertIn({'records_found': 'none'}, [row['record_requirement']
            for row in field_scopes(test['require']) if 'record_requirement' in row])

    def test_present_empty_string_is_preserved_and_invalid_combinations_reject(self):
        old = {'capability': 'windows.registry', 'require': 'at_least_one_exists_and_all_match',
               'states': [{'value': {'require': 'at_least_one_exists_and_all_match',
                                     'datatype': 'string', 'equals': ''}}]}
        current, ledger = promote_test(old)
        self.assertEqual(current['require']['fields']['value'], {
            'datatype': 'string', 'equals': '', 'values_found': 'one_or_more', 'values_matching': 'every'})
        self.assertEqual(restore_test(current, ledger), old)
        for bad in ({'values_found': 'none', 'equals': ''},
                    {'values_found': 'none', 'values_matching': 'none'},
                    {'record': {'records_found': 'none', 'records_matching': 'every'}},
                    {'record': {'records_found': 'none', 'fields': {}}}):
            test = deepcopy(current)
            test['require']['fields']['value'] = bad
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                validate_test(test)
        # Nonempty source comparisons and record-member predicates are not
        # thrown away merely to satisfy the stricter authoring schema.
        for value in ({'require': 'none_exist', 'equals': 'meaningful'},
                      {'record': {'require': 'none_exist', 'fields': {'x': {'equals': ''}}}}):
            bad = deepcopy(old)
            bad['states'] = [{'value': value}]
            with self.subTest(source=value), self.assertRaises(ValueError):
                promote_test(bad)

    def test_absence_status_reference_keeps_error_and_uncollected_distinct(self):
        # The XSD gives both simple and complex State entities the same source
        # check_existence contract. Do not substitute empty strings, missing
        # record members or arbitrary incomplete evidence for explicit absence.
        for counts, expected in (({'does_not_exist': 1}, 'true'), ({'exists': 1}, 'false'),
                                 ({'error': 1}, 'error'), ({'not_collected': 1}, 'unknown'),
                                 ({'does_not_exist': 1, 'error': 1}, 'error'),
                                 ({'does_not_exist': 1, 'not_collected': 1}, 'unknown')):
            with self.subTest(counts=counts):
                self.assertEqual(evaluate_state_entity_existence('none_exist', **counts), expected)
        self.assertEqual(evaluate_record_field('missing-member', []), 'error')


if __name__ == '__main__':
    unittest.main()
