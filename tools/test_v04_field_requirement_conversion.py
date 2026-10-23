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


def source_test():
    return {'test_title': 'Enterprise or EnterpriseS', 'capability': 'windows.registry',
            'reported_elements': 'all', 'require': REQUIRED, 'state_fields_require': REQUIRED,
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
    def test_generated_yaml_defaults_to_inline_object_and_field_predicates(self):
        source = document(REQUIRED)
        test = source['assessment']['tests']['edition-test'] = source_test()
        test['object'] = {'hive': {'equals': 'local_machine'},
                          'name': {'equals': 'EditionID'}}
        converted, _ = promote(source)
        emitted = render_authoring(converted, is_yaml=True)
        self.assertIn('object: {hive: {equals: local_machine}, name: {equals: EditionID}}', emitted)
        self.assertIn('fields: {type: {equals: string}, value: {equals: Enterprise}}', emitted)
        self.assertNotIn('states_match:', emitted)
        self.assertNotIn('state_fields_require:', emitted)
        self.assertEqual(yaml.safe_load(emitted), converted)

    def test_enterprise_states_stay_whole_and_compile_in_both_formats(self):
        old = document(REQUIRED)
        old['assessment']['tests']['edition-test'] = source_test()
        unchanged = deepcopy(old)
        proof = {}
        new, counts = promote(old, provenance=proof)
        test = new['assessment']['tests']['edition-test']
        self.assertEqual(counts['all_items_must'], 1)
        self.assertEqual(test['require']['items'], 'one_or_more')
        self.assertEqual(test['require']['field_requirement'], REQUIRED)
        branches = test['require']['all_items_must'][0]['or']
        self.assertEqual([c['fields']['value']['equals'] for c in branches],
                         ['Enterprise', 'EnterpriseS'])
        self.assertTrue(all(set(c['fields']) == {'type', 'value'} for c in branches))
        self.assertNotIn('states_match', test)
        self.assertNotIn('state_fields_require', test)
        self.assertEqual(restore_test(test, proof['edition-test']), source_test())
        recover(new, old)
        self.assertEqual(old, unchanged)
        raw, report = compile_documents(documents(new))
        self.assertEqual(report['native_source_schema'], 'PASS')
        self.assertEqual(report['yaml_json_byte_parity'], 'PASS')
        self.assertEqual(report['source_reconstruction'], 'PASS')
        self.assertFalse(report['scanner_parity'])
        self.assertEqual(decode_and_verify(json.loads(raw)), documents(new))
        bundle, _ = build_bundle(documents(new))
        native = verify_bundle(bundle)
        self.assertEqual(native['status'], 'NATIVE_040_COMPILED_CONTENT_BUNDLE_NOT_SCANNER_TESTED')
        self.assertEqual((native['documents'], native['programs'], native['tests']), (3, 1, 1))
        self.assertFalse(native['scanner_evaluated'])

    def test_test_and_condition_and_individual_scope_preserve_overrides(self):
        old = source_test()
        old['states'][0]['state_fields_require'] = OPTIONAL
        old['states'][0]['and'][1]['value']['require'] = 'only_one_exists_and_matches'
        new, proof = promote_test(old)
        branches = new['require']['all_items_must'][0]['or']
        self.assertEqual(branches[0]['field_requirement'], OPTIONAL)
        self.assertNotIn('field_requirement', branches[1])
        self.assertEqual(branches[0]['fields']['value']['field_requirement'],
                         'only_one_exists_and_matches')
        self.assertEqual(restore_test(new, proof), old)
        # A new authored logical-group declaration is independently validated
        # and preserved by the compiler (there is no requirement inference).
        new['require']['all_items_must'][0]['field_requirement'] = OPTIONAL
        doc = document(new['require'])
        raw, _ = compile_documents(documents(doc))
        indexed = json.loads(raw)['records'][0]['typed_tests'][0]
        self.assertEqual([row['field_requirement'] for row in indexed['field_requirements']],
                         [OPTIONAL, 'only_one_exists_and_matches', OPTIONAL, OPTIONAL])
        self.assertEqual(indexed['field_requirements'][2]['declaration_path'],
                         ['require', 'all_items_must', 0, 'field_requirement'])
        self.assertEqual(indexed['field_requirements'][0]['declaration_path'],
                         ['require', 'all_items_must', 0, 'or', 0, 'field_requirement'])

    def test_each_test_state_operator_is_preserved(self):
        for source, target in [('all', 'and'), ('any', 'or'), ('one', 'one'), ('odd', 'xor')]:
            with self.subTest(source=source):
                old = source_test(); old['states_match'] = source
                new, proof = promote_test(old)
                self.assertEqual(set(new['require']['all_items_must'][0]), {target})
                self.assertEqual(restore_test(new, proof), old)

    def test_presence_population_and_canonical_repromotion_are_explicit(self):
        for source, items in [('none_exist', 'none'), ('only_one_exists', 'exactly_one'),
                              ('at_least_one_exists', 'one_or_more'),
                              ('all_exist', 'all'), ('may_be_absent', 'may_be_absent')]:
            old = {'capability': 'unix.file', 'require': source}
            new, proof = promote_test(old)
            self.assertEqual(new['require'], {'items': items})
            self.assertEqual(restore_test(new, proof), old)
            repeated, ledger = promote_test(new)
            self.assertEqual(repeated, new)
            self.assertEqual(ledger['shape'], 'unchanged')
        old = source_test(); old['require'] = OPTIONAL
        new, _ = promote_test(old)
        self.assertEqual(new['require']['items'], 'may_be_absent')
        self.assertEqual(new['require']['field_requirement'], REQUIRED)

    def test_dynamic_expected_values_and_comparators_remain_unchanged(self):
        for predicate in (
            {'bitwise_and': 4096, 'require': REQUIRED},
            {'version_greater_than': '1.2', 'require': REQUIRED},
            {'equals': [1, 2], 'value_match': 'one', 'datatype': 'integer', 'require': OPTIONAL},
            {'equals': {'variable': 'expected-variable'}, 'value_match': 'all',
             'datatype': 'string', 'require': REQUIRED},
        ):
            old = source_test(); old['states'] = [{'value': predicate}]
            old.pop('states_match')
            new, proof = promote_test(old)
            field = new['require']['all_items_must'][0]['fields']['value']
            expected = deepcopy(predicate)
            expected['field_requirement'] = expected.pop('require')
            self.assertEqual(field, expected)
            self.assertEqual(restore_test(new, proof), old)

    def test_missing_scope_mixed_names_and_ambiguous_operators_fail(self):
        for mutate in (
            lambda t: t.pop('state_fields_require'),
            lambda t: t.pop('states_match'),
            lambda t: t.update(states_match='invented'),
            lambda t: t['states'][0].update(state_fields_require=None),
            lambda t: t.update(collected_items_require=REQUIRED),
            lambda t: t['states'][0]['and'][0]['type'].update(field_requirement=OPTIONAL),
        ):
            old = source_test(); mutate(old)
            with self.subTest(old=old), self.assertRaises(ValueError):
                promote_test(old)
        new, _ = promote_test(source_test())
        for mutate in (
            lambda t: t.update(states_match='any'),
            lambda t: t.update(state_fields_require=REQUIRED),
            lambda t: t['require'].update(items='none'),
            lambda t: t['require']['all_items_must'][0]['or'][0]['fields']['value'].update(require=REQUIRED),
            lambda t: t['require'].pop('field_requirement'),
        ):
            bad = deepcopy(new); mutate(bad)
            doc = document(bad['require']); doc['assessment']['tests']['edition-test'] = bad
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                normalize_documents(documents(doc))

    def test_uncommon_state_record_and_repeated_field_fallbacks_are_exact(self):
        for reason, state in (
            *[('non_and_state_operator', {op: source_test()['states'][0]['and']})
              for op in ('or', 'one', 'xor')],
            ('repeated_state_field', {'and': [{'value': {'equals': 1, 'require': REQUIRED}},
                                            {'value': {'equals': 2, 'require': REQUIRED}}]}),
            ('record_cardinality', {'value': {'record': {'require': OPTIONAL,
                'fields': {'member': {'equals': 'x', 'require': REQUIRED}}}}}),
        ):
            with self.subTest(reason=reason):
                old = source_test(); old['states'] = [state]; old.pop('states_match')
                new, proof = promote_test(old)
                self.assertEqual(new, old)
                self.assertEqual(proof['diagnostic'], reason)
                self.assertEqual(restore_test(new, proof), old)
                raw, _ = compile_documents(documents({'assessment': {
                    **document(REQUIRED)['assessment'], 'tests': {'edition-test': new}}}))
                self.assertEqual(json.loads(raw)['records'][0]['typed_tests'][0]['fallback_diagnostic'], reason)
        old = source_test(); old['require'] = 'only_one_exists_and_none_match'
        new, proof = promote_test(old)
        self.assertEqual(new, old)
        self.assertEqual(proof['diagnostic'], 'uncommon_test_requirement')

    def test_inverse_rejects_changed_population_logic_value_and_ledger(self):
        new, proof = promote_test(source_test())
        for mutate in (
            lambda t: t['require'].update(items='may_be_absent'),
            lambda t: t['require']['all_items_must'][0].update(
                and_=t['require']['all_items_must'][0].pop('or')),
            lambda t: t['require']['all_items_must'][0]['or'][0]['fields']['value'].update(equals='Education'),
        ):
            bad = deepcopy(new); mutate(bad)
            with self.assertRaises(ValueError): restore_test(bad, proof)
        corrupt = deepcopy(proof); corrupt['source_test']['states_match'] = 'all'
        with self.assertRaises(ValueError): restore_test(new, corrupt)

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
        self.assertEqual(stats['all_items_must'], 2)
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
        restored = restore_evaluate(restored, evaluate_ledger)
        for tid, proof in proofs.items():
            restored['assessment']['tests'][tid] = restore_test(restored['assessment']['tests'][tid], proof)
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
