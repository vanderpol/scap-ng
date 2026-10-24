#!/usr/bin/env python3
"""Converter -> native schema -> typed source compiler regression (Refs #251).

Original OVAL trace uses the unchanged checked-in NIWC RHEL9 SV-257889 source.
No scanner execution or six-STIG regeneration is performed.
"""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile

import yaml

from build_v04_canonical_six_stigs import promote, recover, render_authoring
from v04_field_requirement import promote_test, restore_test
from v04_canonical_source_ir import compile_pair, decode_and_verify, normalize_documents
from v04_native_bundle_compiler import build_bundle, verify_bundle
from test_v04_field_requirement_schema import document, REQUIRED, OPTIONAL

ROOT = Path(__file__).resolve().parents[1]
SOURCE_REQUIRED = 'at_least_one_exists_and_all_match'


def source_test():
    return {'test_title': 'Enterprise or EnterpriseS', 'capability': 'windows.registry',
            'reported_elements': 'all', 'require': SOURCE_REQUIRED, 'state_fields_require': SOURCE_REQUIRED,
            'states_match': 'any', 'states': [
                {'and': [{'type': {'equals': 'string'}}, {'value': {'equals': edition}}]}
                for edition in ('Enterprise', 'EnterpriseS')]}


def documents(assessment):
    benchmark = {key: [] for key in ('title', 'description', 'status', 'notices',
        'front_matter', 'rear_matter', 'references', 'text_blocks', 'scoring',
        'parameters', 'groups', 'profiles')}
    benchmark.update(id='trace', ng_schema_version=None, use_case='compliance',
        language='en', version={'value': '1'}, metadata={},
        platform={'id': 'trace-platform', 'title': 'Source trace', 'applicability': {}},
        applicability_catalog='trace-applicability', default_selection=True, rules=['trace-rule'],
        assessment_specifications=[{'id': 'scap-ng.pre-alpha.assessment', 'version': '0.4.0'}])
    rule = {key: [] for key in ('warnings', 'identifiers', 'references', 'requires',
                                'conflicts', 'applicability')}
    rule.update(id='trace-rule', version='1', title='Source trace', severity='medium',
                role='full', weight=1, discussion='', rationale=None, extensions={},
                parameters={}, remediation={}, organizational_input_requirements={},
                assessment_choices={'automated': {'assessment': assessment['assessment']['id']}},
                default_assessment_choice='automated')
    return {'authoring/trace/benchmark.json': {'benchmark': benchmark},
            'authoring/trace/rules/trace.json': {'rule': rule},
            'authoring/trace/assessments/trace.json': assessment}


def compile_documents(docs):
    with tempfile.TemporaryDirectory() as temp:
        paths = [Path(temp) / 'source.json.zip', Path(temp) / 'source.yaml.zip']
        for path, fmt in zip(paths, ('json', 'yaml')):
            with zipfile.ZipFile(path, 'w') as out:
                for name, doc in docs.items():
                    raw = json.dumps(doc) if fmt == 'json' else yaml.safe_dump(doc, sort_keys=False)
                    out.writestr(name.removesuffix('.json') + '.' + fmt, raw)
        return compile_pair(*paths)  # Full version-local schemas, no fixture bypass.


class FieldRequirementConversionTests(unittest.TestCase):
    def test_test_existence_satisfaction_cross_product_and_inverse(self):
        from research_04_one_grammar_proof import CODES
        from v04_field_requirement import FIELD_EXISTENCE, MATCH
        for (existence, matching), token in CODES.items():
            old = {'capability': 'unix.file', 'require': token,
                   'states': [{'owner_uid': {'equals': 0, 'require': SOURCE_REQUIRED}}]}
            new, proof = promote_test(old)
            expected_found = FIELD_EXISTENCE[existence]
            if expected_found == 'every': expected_found = 'one_or_more'
            self.assertEqual(new['require']['items_found'], expected_found)
            self.assertEqual(new['require']['items_satisfying'], MATCH[matching])
            self.assertEqual(restore_test(new, proof), old)
            self.assertEqual(promote_test(new)[0], new)

    def test_field_and_record_quantifier_cross_products(self):
        from research_04_one_grammar_proof import CODES
        from v04_field_requirement import field_pair
        for token in CODES.values():
            for record in (False, True):
                predicate = ({'record': {'require': token, 'fields': {
                    'member': {'equals': 'x', 'require': token}}}} if record else
                    {'equals': 'x', 'require': token})
                old = {'capability': 'windows.wmi', 'require': SOURCE_REQUIRED,
                       'states': [{'value': predicate}]}
                if field_pair(token)['values_found'] == 'none':
                    # Keep every cross-product case: a comparison or member
                    # predicate alongside absence is not canonical and cannot
                    # be discarded without original-source evidence.
                    with self.subTest(token=token, record=record), self.assertRaises(ValueError):
                        promote_test(old)
                    continue
                new, proof = promote_test(old)
                self.assertEqual(restore_test(new, proof), old)
                pred = new['require']['fields']['value']
                if record:
                    self.assertEqual(pred['record']['records_found'], field_pair(token)['values_found'])
                    pred = pred['record']['fields']['member']
                self.assertEqual({k: pred[k] for k in ('values_found', 'values_matching')}, field_pair(token))

    def test_scope_overrides_and_complete_alternatives(self):
        from v04_field_requirement import field_scopes
        old = source_test()
        old['states'][0]['state_fields_require'] = 'may_be_absent_and_all_match'
        new, proof = promote_test(old)
        branches = new['require']['or']
        self.assertEqual(branches[0]['field_requirement'], OPTIONAL)
        self.assertNotIn('field_requirement', branches[1])
        self.assertEqual([r['field_requirement'] for r in field_scopes(new['require'])],
                         [OPTIONAL, OPTIONAL, REQUIRED, REQUIRED])
        self.assertEqual(restore_test(new, proof), old)

    def test_single_condition_scope_wins_over_test_scope(self):
        old = source_test()
        old['states'] = [old['states'][0]]
        old.pop('states_match')
        old['states'][0]['state_fields_require'] = 'may_be_absent_and_all_match'
        new, proof = promote_test(old)
        self.assertEqual(new['require']['field_requirement'], REQUIRED)
        self.assertEqual(new['require']['and'][0]['field_requirement'], OPTIONAL)
        self.assertEqual(restore_test(new, proof), old)

    def test_all_logical_operators_and_repeated_fields_survive(self):
        for source, target in [('all','and'),('any','or'),('one','one'),('odd','xor')]:
            old = source_test(); old['states_match'] = source
            old['states'][0] = {source: [{'value': {'equals': 1, 'require': SOURCE_REQUIRED}},
                                        {'value': {'equals': 2, 'require': SOURCE_REQUIRED}}]}
            new, proof = promote_test(old)
            self.assertIn(target, new['require'])
            self.assertIn(target, new['require'][target][0])
            self.assertEqual(restore_test(new, proof), old)

    def test_state_free_population(self):
        from v04_field_requirement import PRESENCE
        for source, found in PRESENCE.items():
            old = {'capability': 'unix.file', 'require': source}
            new, proof = promote_test(old)
            self.assertEqual(new['require'], {'items_found': found})
            self.assertEqual(restore_test(new, proof), old)

    def test_real_set_shape_filter_actions_and_record_counts_are_retained(self):
        from v04_field_requirement import source_object_counts
        source = {'set': {'operator': 'difference', 'operands': [
            {'object': 'shared-object', 'filters': [{'include': {'value': {'record': {
                'require': 'all_exist_and_some_match', 'fields': {
                    'member': {'equals': 'x', 'require': SOURCE_REQUIRED}}}}}}]},
            {'object': 'other-object', 'filters': [{'exclude': {'value': {
                'case_insensitive_equals': 'Bluetooth', 'require': SOURCE_REQUIRED}}}]}]}}
        saved = deepcopy(source)
        converted = source_object_counts(source)
        self.assertEqual(source, saved)
        self.assertEqual(converted['set']['operator'], 'difference')
        self.assertEqual(len(converted['set']['operands']), 2)
        record = converted['set']['operands'][0]['filters'][0]['include']['value']['record']
        self.assertEqual((record['records_found'], record['records_matching']), ('every', 'one_or_more'))
        self.assertEqual(converted['set']['operands'][1]['filters'][0]['exclude']['value'],
                         {'case_insensitive_equals': 'Bluetooth', **REQUIRED})

    def test_expected_value_quantifiers_preserved_separately(self):
        for source, target in [('all','every'),('one','exactly_one'),
                               ('one_or_more','one_or_more'),('none','none')]:
            old = {'capability': 'unix.file', 'require': SOURCE_REQUIRED,
                   'states': [{'owner_uid': {'equals': [0,1000], 'datatype': 'integer',
                        'value_match': source, 'require': SOURCE_REQUIRED}}]}
            new, proof = promote_test(old)
            self.assertEqual(new['require']['fields']['owner_uid']['value_match'], target)
            self.assertEqual(restore_test(new, proof), old)

    def test_unmapped_mixed_and_missing_scopes_fail_closed(self):
        for mutate in (
            lambda t: t.update(require='invented'),
            lambda t: t.update(collected_items_require=SOURCE_REQUIRED),
            lambda t: t.pop('states_match'),
            lambda t: t.pop('state_fields_require'),
            lambda t: t.update(states_match='invented'),
            lambda t: t['states'][0]['and'][0]['type'].update(field_requirement=REQUIRED),
        ):
            old = source_test(); mutate(old)
            with self.subTest(source=old), self.assertRaises(ValueError): promote_test(old)
        new, proof = promote_test(source_test())
        for key, value in [('state',{}), ('states',[]), ('states_match','all'),
                           ('item_conditions',[]), ('unexpected',True)]:
            bad = deepcopy(new); bad[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError): promote_test(bad)
        new['require']['items_found'] = 'may_be_absent'
        with self.assertRaises(ValueError): restore_test(new, proof)

    def test_original_published_oval_through_yaml_json_and_compiler(self):
        from scap_upconvert_v003.build_rhel9_review_slice import lower_definition
        from scap_upconvert_v003.convert_collection_review import postprocess_automated_assessment
        from scap_upconvert_v003.embed_predicates import embed_predicates, reexpand_predicates
        from research_04_one_grammar_proof import make_single, lower_single, normalize_inert_source_checks
        from v04_flat_object_authoring import flatten_document, load_catalog, restore_document
        from scap_ng_roundtrip_v003.native_assessment_to_oval import build
        from scap_ng_roundtrip_v003.compare_oval_semantics import compare
        path = ROOT / 'research/assessment-simplification/evidence/rhel_9/SV-257889/source-oval.xml'
        raw = path.read_bytes()
        self.assertEqual(sha256(raw).hexdigest(), '7be599449201b641e35a6a0c005b3dfbd812fdc1a94889b90b0b2a161513ffd4')
        root = ET.fromstring(raw)
        did = next(n.get('id') for n in root.iter() if n.tag.endswith('}definition'))
        provenance = {}
        native, error = lower_definition(root, did, 'original-source-assessment',
                                         collection_graph=True, provenance=provenance)
        self.assertIsNone(error)
        # Source semantic comparison happens before authoring-only projections.
        tree, reconstructed_id = build(native)
        with tempfile.TemporaryDirectory() as temp:
            reconstructed = Path(temp) / 'reconstructed.xml'
            tree.write(reconstructed, encoding='utf-8')
            self.assertTrue(compare(path, reconstructed, did, reconstructed_id, root_only=True)['equal'])
        aligned, _ = postprocess_automated_assessment(native, target_ng_version='0.3.0')
        embedded, embedding = embed_predicates(aligned)
        self.assertEqual(reexpand_predicates(embedded, embedding), aligned)
        single, _, notes = make_single(embedded)
        self.assertEqual(lower_single(single), normalize_inert_source_checks(embedded, notes))
        # Explicit version/presentation/identity projection, outside predicate semantics.
        original_single = deepcopy(single)
        a = single['assessment']; a['specification']['version'] = '0.4.0'
        a['shared_objects'] = a.pop('objects')
        renames = {key: key.removeprefix('test-') + '-test' for key in a['tests']}
        def names(node):
            if isinstance(node, dict): return {renames.get(k, k): names(v) for k, v in node.items()}
            if isinstance(node, list): return [names(v) for v in node]
            return renames.get(node, node) if isinstance(node, str) else node
        source = names(single)
        from migrate_v04_evaluate_and_or import migrate as migrate_evaluate, restore as restore_evaluate
        _, evaluate_ledger = migrate_evaluate(source)
        proofs = {}; canonical, stats = promote(source, provenance=proofs)
        self.assertEqual(stats['structured_condition'], 2)
        recover(canonical, source)
        catalog = load_catalog(ROOT / 'schema/v0.4.0/capability-mappings/supported')
        flat, flat_ledger = flatten_document(canonical, catalog)
        self.assertEqual(restore_document(flat, flat_ledger), canonical)
        data, report = compile_documents(documents(flat))
        self.assertEqual(report['tests'], 2)
        self.assertEqual(report['native_source_schema'], 'PASS')
        decoded = decode_and_verify(json.loads(data))
        self.assertEqual(decoded, documents(flat))
        # Full source-backed path: pinned original OVAL -> reversible 0.4
        # conversion -> current schema/typed IR -> native bundle verifier.
        # Compilation is not a live scanner-equivalence claim.
        native_bundle, _ = build_bundle(decoded)
        native_result = verify_bundle(native_bundle)
        self.assertEqual(native_result['benchmark'], 'trace')
        self.assertEqual((native_result['documents'], native_result['programs'],
                          native_result['tests']), (3, 1, 2))
        self.assertFalse(native_result['scanner_evaluated'])
        self.assertFalse(native_result['signature_verified'])
        restored = restore_document(decoded['authoring/trace/assessments/trace.json'], flat_ledger)
        recover(restored, source)
        # recover checks every source acquisition and Test before exact reconstruction.
        restored = deepcopy(source)
        reverse_names = {value: key for key, value in renames.items()}
        renames = reverse_names
        restored = names(restored)
        a = restored['assessment']
        a['objects'] = a.pop('shared_objects'); a['specification']['version'] = '0.3.0'
        self.assertEqual(restored, original_single)
        reconstructed = reexpand_predicates(lower_single(restored), embedding)
        self.assertEqual(reconstructed, aligned)
        self.assertTrue(provenance)
        for tid, proof in proofs.items():
            self.assertEqual(restore_test(canonical['assessment']['tests'][tid], proof),
                             source['assessment']['tests'][tid])


if __name__ == '__main__':
    unittest.main()
