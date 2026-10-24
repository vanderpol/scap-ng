#!/usr/bin/env python3
"""Pinned original OVAL -> approved 0.4 authoring -> compiled bundle (Refs #251 #248).

SCAP_NG_251_OUTPUT_DIR optionally retains small generated human-review samples.
No corpus sweep or scanner execution; all XML inputs are existing pinned evidence.
"""
from copy import deepcopy
from hashlib import sha256
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile

from build_v04_canonical_six_stigs import promote, recover, render_authoring
from scap_upconvert_v003.build_rhel9_review_slice import lower_definition
from scap_upconvert_v003.convert_collection_review import postprocess_automated_assessment
from scap_upconvert_v003.embed_predicates import embed_predicates, reexpand_predicates
from scap_ng_roundtrip_v003.native_assessment_to_oval import build
from scap_ng_roundtrip_v003.compare_oval_semantics import compare
from research_04_one_grammar_proof import make_single, lower_single, normalize_inert_source_checks
from test_v04_field_requirement_conversion import documents, compile_documents
from v04_flat_object_authoring import flatten_document, load_catalog, restore_document
from v04_canonical_source_ir import decode_and_verify
from v04_canonical_requirement_oracle import compare_original_to_canonical
from v04_native_bundle_compiler import build_bundle, verify_bundle, compile_assessment_program

ROOT = Path(__file__).resolve().parents[1]
CASES = (
    ('rhel_9', 'SV-257889', '7be599449201b641e35a6a0c005b3dfbd812fdc1a94889b90b0b2a161513ffd4', 2),
    ('ms_windows_server_2025', 'SV-278001', 'ffb4e844e9a7cfb1d7d3b549ac219bc0a45963ca8e965864b4fb040b339f75a7', 5),
    ('ms_windows_server_dns', 'SV-259345', '44411063be71910f348a31059b69338f3c83a68db4082cafeac198ff440f04d2', 5),
)


def source_graph(root):
    """Exact lexical attributes/IDs and edges; omitted XSD defaults remain distinct."""
    rows = []
    for node in root.iter():
        if not node.get('id'):
            continue
        rows.append({'id': node.get('id'), 'type': node.tag.rsplit('}', 1)[-1],
                     'attributes': dict(node.attrib),
                     'entities': [{'type': child.tag.rsplit('}', 1)[-1],
                                   'attributes': dict(child.attrib),
                                   'text': (child.text or '').strip()}
                                  for child in node.iter() if child is not node]})
    return rows


class ApprovedPipelineTests(unittest.TestCase):
    def check_case(self, case):
        platform, rule, checksum, count = case
        path = ROOT / 'research/assessment-simplification/evidence' / platform / rule / 'source-oval.xml'
        self.assertEqual(sha256(path.read_bytes()).hexdigest(), checksum)
        root = ET.parse(path).getroot()
        did = next(n.get('id') for n in root.iter() if n.tag.endswith('}definition'))
        mapping = {}
        native, error = lower_definition(root, did, 'source-' + rule.lower() + '-assessment',
                                         collection_graph=True, provenance=mapping)
        self.assertIsNone(error)
        tree, reconstructed_id = build(native)
        with tempfile.TemporaryDirectory() as tmp:
            reconstructed = Path(tmp) / 'oval.xml'
            tree.write(reconstructed, encoding='utf-8')
            self.assertTrue(compare(path, reconstructed, did, reconstructed_id, root_only=True)['equal'])
        aligned, _ = postprocess_automated_assessment(native, target_ng_version='0.3.0')
        embedded, embedding = embed_predicates(aligned)
        single, _, notes = make_single(embedded)
        self.assertEqual(lower_single(single), normalize_inert_source_checks(embedded, notes))
        original_single = deepcopy(single)
        a = single['assessment']
        a['specification']['version'] = '0.4.0'
        a['shared_objects'] = a.pop('objects')
        renames = {key: key.removeprefix('test-') + '-test' for key in a['tests']}
        for section, suffix in [('shared_objects', 'object'), ('variables', 'variable')]:
            renames.update({key: key + '-' + suffix for key in a.get(section, {})
                            if not key.endswith('-' + suffix)})
        # Explicit reversible identity projection; source XML IDs remain in the sidecar.
        def names(node, table):
            if isinstance(node, dict):
                return {table.get(k, k): names(v, table) for k, v in node.items()}
            if isinstance(node, list):
                return [names(v, table) for v in node]
            return table.get(node, node) if isinstance(node, str) else node
        source = names(single, renames)
        proofs = {}
        canonical, _ = promote(source, provenance=proofs)
        recover(canonical, source)
        catalog = load_catalog(ROOT / 'schema/v0.4.0/capability-mappings/supported')
        flat, flat_ledger = flatten_document(canonical, catalog)
        from scap_converter_core import convert
        production, production_evidence = convert(path, did, assessment_id=a['id'])
        self.assertEqual(production, flat)
        self.assertEqual(production_evidence['original_oval_semantic_roundtrip'], 'PASS')
        source_audit = compare_original_to_canonical(
            {'authoring/trace/a.json': source}, {'authoring/trace/a.json': flat})
        self.assertEqual(source_audit['source_exact_promotion'], 'PASS')
        data, report = compile_documents(documents(flat))
        decoded = decode_and_verify(json.loads(data))
        self.assertEqual(report['tests'], count)
        self.assertEqual(report['native_source_schema'], 'PASS')
        self.assertEqual(report['yaml_json_byte_parity'], 'PASS')
        self.assertEqual(decoded, documents(flat))
        raw, manifest = build_bundle(decoded)
        result = verify_bundle(raw)
        self.assertEqual((result['documents'], result['programs'], result['tests']), (3, 1, count))
        self.assertFalse(result['scanner_evaluated'])
        self.assertFalse(result['signature_verified'])
        self.assertEqual(restore_document(flat, flat_ledger), canonical)
        # Replay and checksum validation of the retained source graph, including
        # Set/filter position, then reverse identity and presentation projections.
        recover(restore_document(flat, flat_ledger), source)
        restored = names(source, {value: key for key, value in renames.items()})
        restored['assessment']['objects'] = restored['assessment'].pop('shared_objects')
        restored['assessment']['specification']['version'] = '0.3.0'
        self.assertEqual(restored, original_single)
        self.assertEqual(reexpand_predicates(lower_single(restored), embedding), aligned)
        # Compile the other Object representation as well. Keep sharing by
        # changing a single consumer only; the named declaration remains intact.
        alternate = deepcopy(flat)
        aa = alternate['assessment']
        shared = aa.get('shared_objects') or {}
        for tid, test in aa['tests'].items():
            obj = test.get('object')
            if isinstance(obj, str):
                inline = deepcopy(shared[obj])
                self.assertEqual(inline.pop('capability'), test['capability'])
                test['object'] = inline
                break
            if isinstance(obj, dict):
                shared = aa.setdefault('shared_objects', {})
                shared['pipeline-shared-object'] = {'capability': test['capability'], **deepcopy(obj)}
                test['object'] = 'pipeline-shared-object'
                break
        else:
            self.fail('real source case has no Object consumer')
        other_raw, _ = build_bundle(documents(alternate))
        self.assertEqual(verify_bundle(other_raw)['tests'], count)
        self.assertEqual(len(compile_assessment_program(aa)['test_instructions']), count)
        target = os.environ.get('SCAP_NG_251_OUTPUT_DIR')
        if target:
            out = Path(target) / rule
            out.mkdir(parents=True, exist_ok=True)
            for is_yaml, suffix in [(True, 'yaml'), (False, 'json')]:
                (out / ('authoring.' + suffix)).write_text(render_authoring(flat, is_yaml=is_yaml))
            with zipfile.ZipFile(io.BytesIO(raw)) as archive:
                program_path = manifest['build_provenance']['compiled_programs'][a['id']]['path']
                (out / 'compiled.json').write_bytes(archive.read(program_path) + b'\n')
            evidence = {'source': path.relative_to(ROOT).as_posix(), 'sha256': checksum,
                        'definition_id': did, 'source_graph': source_graph(root),
                        'source_mapping': mapping, 'test_proofs': proofs,
                        'source_defaults': {'standard': 'OVAL 5.12.3',
                            'test_check_existence': 'at_least_one_exists',
                            'state_operator': 'AND', 'test_state_operator': 'AND',
                            'var_check': 'all', 'entity_check': 'all',
                            'entity_check_existence': 'at_least_one_exists'},
                        'inert_source_check_notes': notes, 'authoring_report': report,
                        'compiled_report': result, 'original_oval_semantic_roundtrip': 'PASS',
                        'schema_baseline': '5a43f45a972fb63526e71ac872b21d97a676044c',
                        'requirement_source_audit': source_audit,
                        'production_converter_evidence': production_evidence,
                        'scanner_equivalence': False}
            (out / 'provenance.json').write_text(json.dumps(evidence, indent=2) + '\n')

    def test_real_all_exist_source_requires_owner_population_decision(self):
        from build_v04_canonical_six_stigs import upgrade_v003
        path = ROOT / 'research/assessment-simplification/evidence/rhel_9/SV-258179/source-oval.xml'
        self.assertEqual(sha256(path.read_bytes()).hexdigest(),
                         '463b539c469c3302aa52c23fdca35814f40fd5fd7de31346964e1b4a97b5d8a9')
        root = ET.parse(path).getroot()
        original = next(n for n in root.iter() if n.get('id') == 'oval:mil.disa.stig.ind:tst:23041300')
        self.assertEqual(original.get('check_existence'), 'all_exist')
        did = next(n.get('id') for n in root.iter() if n.tag.endswith('}definition'))
        native, error = lower_definition(root, did, 'all-exist-counterexample-assessment',
                                         collection_graph=True, provenance={})
        self.assertIsNone(error)
        aligned, _ = postprocess_automated_assessment(native, target_ng_version='0.3.0')
        with self.assertRaisesRegex(AssertionError, 'does not match source'):
            upgrade_v003(aligned)
        from oval_result_truth_tables import evaluate_collected_object_test
        boundary = dict(has_state=False, check='all', exists=1, does_not_exist=1)
        self.assertEqual(evaluate_collected_object_test('complete', existence='all_exist', **boundary), 'false')
        self.assertEqual(evaluate_collected_object_test('complete', existence='at_least_one_exists', **boundary), 'true')

    def test_linux_filters_permissions_and_variables(self):
        self.check_case(CASES[0])

    def test_windows_enterprise_state_or_through_inline_yaml_and_compiled_json(self):
        """Real two-State OR, using existing adapters; not unified CLI coverage."""
        import yaml
        from build_v04_canonical_six_stigs import upgrade_v003

        path = ROOT / 'research/assessment-simplification/evidence/ms_windows_11/SV-253254/source-oval.xml'
        self.assertEqual(sha256(path.read_bytes()).hexdigest(),
                         'a056aafd7326bac213cab63da8c3746a49dfd5fc03f1812426bc8804e6e32926')
        root = ET.parse(path).getroot()
        did = 'oval:mil.disa.stig.defs:def:253254'
        native, error = lower_definition(root, did, 'enterprise-editions-assessment',
                                         collection_graph=True, provenance={})
        self.assertIsNone(error)
        tree, reconstructed_id = build(native)
        with tempfile.TemporaryDirectory() as tmp:
            reconstructed = Path(tmp) / 'oval.xml'
            tree.write(reconstructed, encoding='utf-8')
            self.assertTrue(compare(path, reconstructed, did, reconstructed_id,
                                    root_only=True)['equal'])
        aligned, _ = postprocess_automated_assessment(native, target_ng_version='0.3.0')
        flat, _ = upgrade_v003(aligned)
        assessment = flat['assessment']
        test = assessment['tests']['editionid-enterprise-or-enterprises-test']
        # The upgrader retains source Object identity. Explicitly exercise the
        # supported inline representation for this single-consumer fixture.
        shared_program = compile_assessment_program(assessment)
        obj = assessment.pop('shared_objects')[test['object']]
        self.assertEqual(obj.pop('capability'), test['capability'])
        test['object'] = obj
        self.assertEqual(obj['hive'], 'local_machine')
        self.assertEqual(obj['key']['equals'], r'SOFTWARE\Microsoft\Windows NT\CurrentVersion')
        self.assertEqual(obj['name']['equals'], 'EditionId')
        expected = {'items_found': 'one_or_more', 'items_satisfying': 'every',
                    'or': [{'and': [{'fields': {field: {
                        'datatype': 'string', 'equals': value,
                        'values_found': 'one_or_more', 'values_matching': 'every'}}}
                        for field, value in [('type', 'string'), ('value', edition)]]}
                        for edition in ('Enterprise', 'EnterpriseS')]}
        self.assertEqual(test['require'], expected)
        self.assertNotIn('states', test)
        self.assertNotIn('states_match', test)
        text = render_authoring(flat, is_yaml=True)
        parsed = yaml.safe_load(text)
        self.assertEqual(parsed, flat)
        self.assertIsInstance(parsed['assessment']['tests'][
            'editionid-enterprise-or-enterprises-test']['object'], dict)
        data, report = compile_documents(documents(parsed))
        self.assertEqual(report['native_source_schema'], 'PASS')
        self.assertEqual(report['yaml_json_byte_parity'], 'PASS')
        decoded = decode_and_verify(json.loads(data))
        self.assertEqual(decoded, documents(parsed))
        raw, manifest = build_bundle(decoded)
        self.assertEqual(verify_bundle(raw)['tests'], 1)
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            program_path = manifest['build_provenance']['compiled_programs'][assessment['id']]['path']
            program = json.loads(archive.read(program_path))
        shared_instruction, = shared_program['test_instructions']
        self.assertEqual(shared_instruction['operands']['require'], expected)
        self.assertEqual(shared_instruction['operands']['object'], 'editionid-object')
        instruction, = program['test_instructions']
        self.assertEqual(instruction['opcode'], 'CHECK_ITEM_CONDITION')
        self.assertEqual(instruction['operands']['object'], obj)
        self.assertEqual(instruction['operands']['require'], expected)

    def test_windows_record_and_shared_object(self):
        self.check_case(CASES[1])

    def test_windows_dns_variables_and_filters(self):
        self.check_case(CASES[2])


if __name__ == '__main__':
    unittest.main()
