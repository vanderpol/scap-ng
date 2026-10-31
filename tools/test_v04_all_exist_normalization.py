"""Pinned production Test normalization and retained OVAL counterexamples (#251)."""
from copy import deepcopy
from hashlib import sha256
import io
import json
from pathlib import Path
import tempfile
import subprocess
import sys
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET
import zipfile

import yaml

from scap_converter_core import convert
from v04_all_exist_normalization import (
    CONTRACT, DEFINITION, SOURCE_SHA256, check_population_contract, contract_evidence,
)
from v04_field_requirement import restore_test
from oval_result_truth_tables import evaluate_collected_object_test
from test_v04_field_requirement_conversion import documents, compile_documents
from v04_canonical_source_ir import decode_and_verify
from v04_native_bundle_compiler import build_bundle, verify_bundle
from build_v04_canonical_six_stigs import render_authoring

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'research/assessment-simplification/evidence/rhel_9/SV-258179/source-oval.xml'


class AllExistNormalizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.native, cls.evidence = convert(SOURCE, DEFINITION,
                                           assessment_id='audit-extended-attribute-syscalls-assessment')

    def test_pinned_source_all_sixteen_tests_metadata_and_inverse(self):
        self.assertEqual(sha256(SOURCE.read_bytes()).hexdigest(), SOURCE_SHA256)
        root = ET.parse(SOURCE).getroot()
        by_id = {n.get('id'): n for n in root.iter() if n.get('id')}
        normalized = self.evidence['test_existence_normalizations']
        self.assertEqual(len(normalized), 16)
        self.assertFalse(self.evidence['unrestricted_oval_equivalence'])
        self.assertEqual(self.evidence['original_oval_semantic_roundtrip'], 'PASS')
        proof = self.evidence['approved_require_projection']
        bindings = self.evidence['source_provenance']['source_test_bindings']
        affected = {r['source_test_id'] for r in normalized}
        self.assertIn('oval:mil.disa.stig.ind:tst:23041300', affected)
        for row in normalized:
            source = by_id[row['source_test_id']]
            self.assertEqual(source.get('check_existence'), 'all_exist')
            self.assertEqual(row['source_test_version'], source.get('version'))
            self.assertEqual(row['source_file_sha256'], SOURCE_SHA256)
            obj = by_id[row['source_object_id']]
            self.assertEqual(row['source_object_version'], obj.get('version'))
            self.assertEqual(row['source_object_xml_sha256'], sha256(ET.tostring(obj)).hexdigest())
            test = self.native['assessment']['tests'][row['native_test_id']]
            self.assertEqual(test['require'], {'items_found': 'one_or_more'})
            self.assertEqual(restore_test(test, proof['test_proofs'][row['native_test_id']])['require'],
                             'all_exist')
        for source_id, old_id in bindings.items():
            if source_id not in affected:
                self.assertEqual(by_id[source_id].get('check_existence', 'at_least_one_exists'),
                                 'at_least_one_exists')
                native_id = proof['identity_projection']['tests'][old_id]
                self.assertEqual(restore_test(self.native['assessment']['tests'][native_id],
                    proof['test_proofs'][native_id])['require'], 'at_least_one_exists')
        example = next(r for r in normalized if r['source_test_id'].endswith(':23041300'))
        test = self.native['assessment']['tests'][example['native_test_id']]
        obj = self.native['assessment']['shared_objects'][test['object']]
        self.assertEqual(obj['full_path']['equals'], '/etc/audit/audit.rules')
        self.assertEqual(obj['instance']['greater_than_or_equal'], 1)
        self.assertIn('setxattr', obj['pattern']['matches_regex'])
        self.assertIn('b32', obj['pattern']['matches_regex'])

    def test_yaml_json_typed_ir_compiled_bundle_preserves_full_program(self):
        parsed = yaml.safe_load(render_authoring(self.native, is_yaml=True))
        self.assertEqual(parsed, json.loads(render_authoring(self.native, is_yaml=False)))
        data, report = compile_documents(documents(parsed))
        self.assertEqual(report['native_source_schema'], 'PASS')
        self.assertEqual(report['yaml_json_byte_parity'], 'PASS')
        decoded = decode_and_verify(json.loads(data))
        self.assertEqual(decoded, documents(parsed))
        raw, manifest = build_bundle(decoded)
        result = verify_bundle(raw)
        self.assertEqual((result['documents'], result['programs'], result['tests']), (3, 1, 24))
        self.assertFalse(result['scanner_evaluated'])
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            entry, = manifest['build_provenance']['compiled_programs'].values()
            program = json.loads(z.read(entry['path']))
        actual = {t['test_id']: t['operands']['require'] for t in program['test_instructions']}
        self.assertEqual(actual, {k: v['require'] for k, v in parsed['assessment']['tests'].items()})
        self.assertTrue(all(t['opcode'] == 'CHECK_COLLECTION_PRESENCE'
                            for t in program['test_instructions']))

    def test_public_cli_retains_original_source_metadata(self):
        with tempfile.TemporaryDirectory() as td:
            output, evidence = Path(td) / 'assessment.json', Path(td) / 'conversion.json'
            subprocess.run([sys.executable, str(ROOT / 'tools/scap_converter_core.py'),
                '--source-xml', str(SOURCE), '--definition-id', DEFINITION,
                '--output', str(output), '--evidence', str(evidence)],
                check=True, capture_output=True, text=True)
            self.assertEqual(json.loads(output.read_text()), self.native)
            report = json.loads(evidence.read_text())
            self.assertEqual(report['source_sha256'], SOURCE_SHA256)
            self.assertEqual(len(report['test_existence_normalizations']), 16)
            self.assertFalse(report['unrestricted_oval_equivalence'])

    def test_original_mixed_population_counterexample_remains_different(self):
        kwargs = dict(has_state=False, check='all', exists=1, does_not_exist=1)
        self.assertEqual(evaluate_collected_object_test('complete', existence='all_exist', **kwargs), 'false')
        self.assertEqual(evaluate_collected_object_test('complete', existence='at_least_one_exists', **kwargs), 'true')
        with self.assertRaisesRegex(ValueError, 'synthetic'):
            check_population_contract('complete', ['exists', 'does_not_exist'])

    def test_native_contract_complete_zero_positive_error_unknown_and_incomplete(self):
        for count in (0, 1, 3):
            for native_flag, oval_flag, expected in (
                    ('complete', 'complete', 'true' if count else 'false'),
                    ('error', 'error', 'error'), ('incomplete', 'incomplete', 'unknown'),
                    ('not_collected', 'not collected', 'unknown')):
                check_population_contract(native_flag, ['exists'] * count)
                for existence in ('all_exist', 'at_least_one_exists'):
                    self.assertEqual(evaluate_collected_object_test(oval_flag, existence=existence,
                        has_state=False, exists=count), expected)
        # Diagnostic evidence cannot be erased to manufacture complete success.
        for status, flag, expected in (('error', 'error', 'error'),
                                       ('not_collected', 'not_collected', 'unknown')):
            with self.assertRaisesRegex(ValueError, 'error/unknown'):
                check_population_contract('complete', ['exists', status])
            check_population_contract(flag, ['exists', status])
            self.assertEqual(evaluate_collected_object_test(flag.replace('_', ' '),
                existence='at_least_one_exists', has_state=False, exists=1), expected)

    def test_result_schema_blocks_synthetic_items_keeps_diagnostic_statuses(self):
        # Exercise the actual version-local Item schema including its references.
        from jsonschema import Draft202012Validator
        schema = json.loads((ROOT / 'schema/v0.4.0/collected-item.schema.json').read_text())
        validator = Draft202012Validator(schema)
        item = {'id': 'audit-rule-item', 'capability': 'independent.textfilecontent',
                'status': 'does_not_exist', 'fields': {}, 'provenance': {}}
        self.assertFalse(validator.is_valid(item))
        for status in ('exists', 'error', 'not_collected'):
            self.assertTrue(validator.is_valid({**item, 'status': status}))
        collection = Draft202012Validator(json.loads(
            (ROOT / 'schema/v0.4.0/collection-result.schema.json').read_text()))
        for status in ('complete', 'incomplete', 'error', 'not_collected'):
            self.assertTrue(collection.is_valid({'id': 'audit-rules-collection',
                'capability': 'independent.textfilecontent', 'status': status, 'item_refs': []}))
        self.assertFalse(contract_evidence(CONTRACT)['unrestricted_oval_equivalence'])

    def test_source_drift_and_unknown_contract_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'changed.xml'
            path.write_bytes(SOURCE.read_bytes().replace(b'check_existence="all_exist"',
                              b'check_existence="at_least_one_exists"', 1))
            with self.assertRaisesRegex(ValueError, 'source SHA differs'):
                convert(path, DEFINITION)
        with self.assertRaisesRegex(ValueError, 'explicit approved'):
            contract_evidence('unreviewed-contract')

    def test_corrupt_mature_graph_not_hidden_by_normalization(self):
        import scap_converter_core as core
        original = core.lower_definition
        def changed(*args, **kwargs):
            result, error = original(*args, **kwargs)
            result = deepcopy(result)
            next(iter(result['assessment']['tests'].values()))['assertion']['existence'] = 'none_exist'
            return result, error
        with patch.object(core, 'lower_definition', side_effect=changed):
            with self.assertRaises((ValueError, AssertionError)):
                convert(SOURCE, DEFINITION)


if __name__ == '__main__':
    unittest.main()
