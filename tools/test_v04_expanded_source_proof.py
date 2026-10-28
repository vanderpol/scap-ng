#!/usr/bin/env python3
"""Original-source proof expansion and status/normalization boundaries (#251)."""
from copy import deepcopy
from hashlib import sha256
import itertools
import importlib.util
import json
from pathlib import Path
import re
import tempfile
import sys
import unittest
import xml.etree.ElementTree as ET
import zipfile
from unittest.mock import patch

from audit_v04_eight_assessment_pilot import verify_program
from audit_v04_proof_expansion import manifest_rows, merge_coverage
from test_v04_source_package_semantics import fixture as pilot, consistently_rehash_program
from v04_source_package_semantics import Source, Unsupported, compare, digest, local, xml_term
from v04_expanded_source_proof import (ExpandedSource, ExpandedNative, actual_items_evidence,
    expanded_compare, predicate_order, APPROVED_SHA, APPROVED_SOURCE)
from oval_result_truth_tables import aggregate_operator, apply_filter_state_result, evaluate_collected_object_test
from test_v04_package_consumer import fixture as wrapper_docs
from v04_native_bundle_compiler import build_bundle
from verify_v04_package_consumer import canonical, verify

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / 'tests/fixtures/v04-proof-expansion'
STATES = ('true', 'false', 'error', 'unknown', 'not evaluated', 'not applicable')


def checked(f, normalization=False):
    source = ExpandedSource(ET.fromstring(f['source_xml']))
    source.closure(f['source_definition'])
    if normalization:
        source.admit_pinned_rhel_normalization(f['source_definition'], f['provenance'])
    return expanded_compare(source, f['source_definition'], f['assessment'])


def windows(n):
    return json.loads((FIXTURES / ('windows-' + str(n).zfill(2) + '.json')).read_text())


class ExpandedSourceProofTests(unittest.TestCase):
    def test_fixed_manifest_balance_no_prior_identity_and_pinned_fixtures(self):
        rows = manifest_rows()
        self.assertEqual(len(rows), 24)
        for row in rows:
            with self.subTest(case=row['case']):
                f = windows(row['case'])
                self.assertEqual(f['assessment']['id'], row['assessment'])
                self.assertEqual(digest({'assessment': f['assessment']}), row['assessment_member']['sha256'])
                self.assertEqual(digest(f['compiled_program']), row['compiled_program_member']['sha256'])
                source = ExpandedSource(ET.fromstring(f['source_xml']))
                closure = source.closure(f['source_definition'])
                self.assertEqual(closure['nodes'], f['provenance']['source_dependency_closure']['nodes'])
                verify_program(f['assessment'], f['compiled_program'])
                if row['case'] == 14:
                    # Keep the historical pinned packet immutable. The newly
                    # proved generic command controls discharge this old gap.
                    self.assertEqual(f['provenance']['rule'], 'SV-278146')
                    self.assertEqual(f['expected_outcome'], 'UNVERIFIABLE/UNSUPPORTED')
                    original_reader = Source(ET.fromstring(f['source_xml']))
                    self.assertEqual(compare(original_reader, f['source_definition'], f['assessment'],
                                             native_type=ExpandedNative)['outcome'], f['expected_outcome'])
                    self.assertEqual(checked(f)['outcome'], 'PROVED')
                    mutant = deepcopy(f)
                    test = next(t for t in mutant['assessment']['tests'].values()
                                if t['object'].get('error_if_stderr_exists') is True)
                    test['object']['error_if_stderr_exists'] = False
                    self.assertEqual(checked(mutant)['outcome'], 'MISMATCH')
                elif row['case'] == 3:
                    # Preserve the immutable historical packet and its former
                    # unsupported outcome. Approved typed-operator decoding now
                    # discharges the version comparison obligation generically.
                    self.assertEqual(f['provenance']['rule'], 'SV-253263')
                    self.assertEqual(f['expected_outcome'], 'UNVERIFIABLE/UNSUPPORTED')
                    self.assertEqual(checked(f)['outcome'], 'PROVED')
                    mutant = deepcopy(f)
                    test = next(iter(mutant['assessment']['tests'].values()))
                    predicate = test['require']['and'][1]['fields']['value']
                    predicate['greater_than_or_equal'] = predicate.pop('version_greater_than_or_equal')
                    predicate['datatype'] = 'string'
                    self.assertEqual(checked(mutant)['outcome'], 'MISMATCH')
                else:
                    self.assertEqual(checked(f)['outcome'], f['expected_outcome'])
        with patch.dict(sys.modules, {'resource': None}):
            spec = importlib.util.spec_from_file_location('proof_without_resource',
                ROOT / 'tools/audit_v04_proof_expansion.py')
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self.assertIsNone(module.resource)

    def test_three_original_blockers_revisited_and_oracle_stays_unverified(self):
        for platform, rule, normalization, expected in (
            ('rhel_9', 'SV-257889', False, 'PROVED'),
            ('rhel_9', 'SV-258179', True, 'PROVED_WITH_EXPLICIT_APPROVED_NORMALIZATION'),
            ('apache_server_2-4_unix_server', 'SV-214228', False, 'PROVED'),
            ('oracle_linux_9', 'SV-271844', False, 'UNVERIFIABLE/UNSUPPORTED')):
            with self.subTest(rule=rule):
                self.assertEqual(checked(pilot(platform, rule), normalization)['outcome'], expected)

    def test_prior_four_exact_proofs_reproduce_under_expanded_rules(self):
        for platform, rule in (('ms_windows_11', 'SV-253254'), ('ms_windows_11', 'SV-253260'),
                               ('ms_windows_server_2025', 'SV-278001'), ('ms_windows_server_dns', 'SV-259345')):
            with self.subTest(rule=rule):
                self.assertEqual(checked(pilot(platform, rule))['outcome'], 'PROVED')

    def test_state_and_or_commute_for_all_six_states_without_erasing_duplicates(self):
        for op, a, b in itertools.product(('AND', 'OR'), STATES, STATES):
            self.assertEqual(aggregate_operator(op, [a, b]), aggregate_operator(op, [b, a]))
        x, y = {'field': 'x'}, {'field': 'y'}
        self.assertEqual(predicate_order({'or': [x, y]}), predicate_order({'or': [y, x]}))
        self.assertNotEqual(predicate_order({'or': [x, y]}), predicate_order({'or': [x, y, y]}))
        self.assertNotEqual(predicate_order({'and': [x, y]}), predicate_order({'or': [x, y]}))

    def test_consistently_forged_file_selector_filter_and_foreach_scope_rejected(self):
        for change in ('selector', 'filter', 'scope'):
            with self.subTest(change=change):
                f = pilot('rhel_9', 'SV-257889')
                obj = next(iter(f['assessment']['tests'].values()))['object']
                if change == 'selector':
                    obj['name']['matches_regex'] += 'CHANGED'
                elif change == 'filter':
                    obj['filters'][0]['include'] = obj['filters'][0].pop('exclude')
                else:
                    obj['directory']['from'] = 'another-user.home_dir'
                consistently_rehash_program(f)
                self.assertIn(checked(f)['outcome'], ('MISMATCH', 'UNVERIFIABLE/UNSUPPORTED'))

    def test_set_filters_remain_ordered_and_before_enclosing_operator(self):
        f = pilot('rhel_9', 'SV-257889')
        cohort = next(v for v in f['assessment']['shared_objects'].values() if 'set' in v)
        cohort['set']['operands'][0]['filters'].reverse()
        consistently_rehash_program(f)
        self.assertEqual(checked(f)['outcome'], 'MISMATCH')

    def test_single_operand_set_identity_and_binary_complement_operand_order(self):
        f = pilot('rhel_9', 'SV-257889')
        native = ExpandedNative(f['assessment'])
        cohort = next(v for v in f['assessment']['shared_objects'].values() if 'set' in v)
        original = deepcopy(cohort['set'])
        for op in ('union', 'intersection', 'difference'):
            mutated = {**original, 'operator': op}
            self.assertEqual(native.set_term(mutated, 'unix.password')['operator'], 'identity')
        binary = {'operator': 'difference', 'operands': [deepcopy(original['operands'][0]),
            {'object': {'capability': 'unix.password', 'username': {'equals': 'root'}}}]}
        a = native.set_term(binary, 'unix.password')
        binary['operands'].reverse()
        b = native.set_term(binary, 'unix.password')
        self.assertNotEqual(a, b)

    def test_filter_nonboolean_results_remain_errors_and_completeness_not_erased(self):
        for action in ('include', 'exclude'):
            for state in STATES[2:]:
                self.assertEqual(apply_filter_state_result(action, state), 'error')
        for status in ('incomplete', 'error', 'not_collected'):
            actual_items_evidence(status, ['exists'])
            with self.assertRaisesRegex(Unsupported, 'cannot claim complete success'):
                actual_items_evidence(status, ['exists'], claims_complete_success=True)

    def test_rhel_exact_sixteen_normalizations_and_original_counterexample_retained(self):
        self.assertEqual(sha256(APPROVED_SOURCE.read_bytes()).hexdigest(), APPROVED_SHA)
        r = checked(pilot('rhel_9', 'SV-258179'), True)
        self.assertEqual(len(r['normalizations_applied']), 16)
        self.assertTrue(all(n['approved_source_sha256'] == APPROVED_SHA and
                            n['unrestricted_oval_equivalence'] is False for n in r['normalizations_applied']))
        for existence, expected in (('all_exist', 'false'), ('at_least_one_exists', 'true')):
            self.assertEqual(evaluate_collected_object_test('complete', existence=existence,
                check='all', has_state=False, exists=1, does_not_exist=1), expected)
        with self.assertRaisesRegex(Unsupported, 'synthetic'):
            actual_items_evidence('complete', ['exists', 'does_not_exist'])

    def test_complete_empty_error_unknown_and_incomplete_boundaries(self):
        for count in (0, 1, 3):
            actual_items_evidence('complete', ['exists'] * count)
            for native, oval, expected in (('complete', 'complete', 'true' if count else 'false'),
                 ('incomplete', 'incomplete', 'unknown'), ('error', 'error', 'error'),
                 ('not_collected', 'not collected', 'unknown')):
                actual_items_evidence(native, ['exists'] * count)
                for existence in ('all_exist', 'at_least_one_exists'):
                    self.assertEqual(evaluate_collected_object_test(oval, existence=existence,
                        check='all', has_state=False, exists=count), expected)
        for items in (['exists', 'error'], ['exists', 'not_collected']):
            with self.assertRaisesRegex(Unsupported, 'cannot become complete'):
                actual_items_evidence('complete', items)
        # Incomplete does not universally mean unknown: decisive partial
        # results remain permitted by the existing source result contract.
        self.assertEqual(evaluate_collected_object_test('incomplete', existence='none_exist',
                         exists=1, has_state=False), 'false')
        self.assertEqual(evaluate_collected_object_test('incomplete', existence='at_least_one_exists',
                         exists=1, item_results=['true'], check='at least one'), 'true')

    def test_normalization_source_mutation_and_unapproved_scope_fail_closed(self):
        f = pilot('rhel_9', 'SV-258179')
        root = ET.fromstring(f['source_xml'])
        next(n for n in root.iter() if local(n) == 'pattern').text += 'CHANGED'
        f['source_xml'] = ET.tostring(root, encoding='unicode')
        with self.assertRaisesRegex(Unsupported, 'closure differs'):
            checked(f, True)
        f = pilot('rhel_9', 'SV-258179')
        f['provenance']['source_zip_sha256'] = '0' * 64
        with self.assertRaisesRegex(Unsupported, 'unapproved RHEL'):
            checked(f, True)
        self.assertEqual(checked(pilot('rhel_9', 'SV-258179'))['outcome'], 'UNVERIFIABLE/UNSUPPORTED')

    def test_textfile_behavior_instance_and_dynamic_pattern_mutants_rejected(self):
        for change in ('multiline', 'instance', 'pattern', 'datatype'):
            with self.subTest(change=change):
                f = pilot('rhel_9', 'SV-258179')
                t = next(iter(f['assessment']['tests'].values()))
                if change == 'multiline':
                    t['object']['multiline'] = False
                elif change == 'instance':
                    t['object']['instance']['greater_than_or_equal'] = 2
                elif change == 'pattern':
                    v = next(iter(f['assessment']['variables'].values()))
                    v['expression']['concat'].reverse()
                else:
                    t['object']['instance']['datatype'] = 'string'
                    t['object']['instance']['greater_than_or_equal'] = '1'
                consistently_rehash_program(f)
                self.assertEqual(checked(f, True)['outcome'], 'MISMATCH')

    def test_apache_regex_capture_merge_unique_and_discovery_order_mutants_rejected(self):
        for change in ('capture', 'delimiter', 'sort', 'order', 'discovery', 'missing'):
            with self.subTest(change=change):
                f = pilot('apache_server_2-4_unix_server', 'SV-214228')
                variables = f['assessment']['variables']
                if change == 'capture':
                    v = next(v for v in variables.values() if 'regex_capture' in v['expression'])
                    v['expression']['regex_capture']['pattern'] += 'CHANGED'
                elif change in ('delimiter', 'sort', 'order'):
                    v = next(v for v in variables.values() if 'merge' in v['expression'])
                    v['expression']['merge'][change] = {'delimiter': ',', 'sort': 'lexicographic', 'order': 'descending'}[change]
                elif change == 'discovery':
                    next(iter(variables.values()))['expression']['concat'].reverse()
                else:
                    variables.pop(next(iter(variables)))
                consistently_rehash_program(f)
                self.assertIn(checked(f)['outcome'], ('MISMATCH', 'UNVERIFIABLE/UNSUPPORTED'))

    def test_function_defaults_typed_empty_values_and_missing_metadata(self):
        source = ExpandedSource(ET.fromstring(pilot('apache_server_2-4_unix_server', 'SV-214228')['source_xml']))
        native = ExpandedNative(pilot('apache_server_2-4_unix_server', 'SV-214228')['assessment'])
        n = ET.fromstring('<merge xmlns="http://oval.mitre.org/XMLSchema/oval-definitions-5"><literal_component></literal_component></merge>')
        expected = {'merge': {'delimiter': '', 'sort': 'document', 'order': 'ascending',
                             'values': {'literal': {'datatype': 'string', 'value': ''}}}}
        self.assertEqual(source.function(n), expected)
        self.assertEqual(native.function(expected), expected)
        del expected['merge']['order']
        with self.assertRaisesRegex(Unsupported, 'explicit default'):
            native.function(expected)

    def test_specification_anchor_hashes_and_regex_capture_boundaries(self):
        packet = json.loads((ROOT / 'docs/audit/v04-proof-expansion/proof-rule-anchors.json').read_text())
        for rule in packet['rules']:
            for side in ('source', 'native'):
                anchor = rule[side]
                self.assertEqual(sha256((ROOT / anchor['path']).read_bytes()).hexdigest(), anchor['sha256'])
        # Restricted literal examples of the XSD's first-match/first-capture
        # rule. This is NOT a substitute for OVAL regex-engine conformance.
        xsd = (ROOT / 'third_party/scap-1.4-schemas/oval_5.12.3/oval-definitions-schema.xsd').read_text()
        self.assertIn('only the first capture is used', xsd)
        self.assertIn('If no matches are found', xsd)
        for pattern, value, expected in (('(a)(b)', 'abab', 'a'), ('(a+)', 'baaa', 'aaa')):
            self.assertEqual(re.search(pattern, value).group(1), expected)
        f = pilot('apache_server_2-4_unix_server', 'SV-214228')
        root = ET.fromstring(f['source_xml'])
        capture = next(n for n in root.iter() if local(n) == 'regex_capture')
        original = capture.get('pattern')
        capture.set('pattern', '(?:' + original + ')()')
        f['source_xml'] = ET.tostring(root, encoding='unicode')
        self.assertEqual(checked(f)['outcome'], 'MISMATCH')

    def test_missing_collection_dependency_cannot_be_hidden_by_foreach(self):
        f = pilot('rhel_9', 'SV-257889')
        f['assessment']['shared_objects'].clear()
        consistently_rehash_program(f)
        self.assertEqual(checked(f)['outcome'], 'UNVERIFIABLE/UNSUPPORTED')

    def test_fully_rehashed_schema_valid_package_forgery_still_fails_original_proof(self):
        f = windows(2)
        docs = wrapper_docs()
        docs['authoring/demo/assessments/a1.json'] = {'assessment': f['assessment']}
        docs['authoring/demo/rules/r1.json']['rule']['assessment_choices']['automated']['assessment'] = f['assessment']['id']
        raw, _ = build_bundle(docs)
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'control.scapng'
            path.write_bytes(raw)
            verify(path)
            with zipfile.ZipFile(path) as z:
                members = {n: z.read(n) for n in z.namelist()}
            manifest = json.loads(members['META-INF/manifest.json'])
            aid = f['assessment']['id']
            program_info = manifest['build_provenance']['compiled_programs'][aid]
            self.assertEqual(digest(json.loads(members[program_info['path']])), f['provenance']['program_sha256'])
            next(iter(f['assessment']['tests'].values()))['object']['key']['equals'] += '\\FORGED'
            consistently_rehash_program(f)
            for row, value in ((manifest['objects'][aid], {'assessment': f['assessment']}),
                               (program_info, f['compiled_program'])):
                members[row['path']] = canonical(value)
                row.update(size=len(members[row['path']]), sha256=sha256(members[row['path']]).hexdigest())
            graph = []
            for ident, row in manifest['objects'].items():
                doc = json.loads(members[row['path']])
                graph.append({'kind': next(iter(doc)), 'id': ident, 'sha256': digest(doc)})
            manifest['build_provenance']['source_graph_sha256'] = digest(sorted(graph, key=lambda r: (r['kind'], r['id'])))
            members['META-INF/manifest.json'] = canonical(manifest)
            forged = Path(td) / 'forged.scapng'
            with zipfile.ZipFile(forged, 'w') as z:
                for name, value in members.items():
                    z.writestr(name, value)
            self.assertEqual(verify(forged)['status'], 'INDEPENDENT_PACKAGE_CONSUMER_PASS')
            self.assertEqual(checked(f)['outcome'], 'MISMATCH')

    def test_monotonic_ledger_blocks_lost_proof_duplicate_identity_and_denominator_drift(self):
        import csv
        from audit_v04_proof_expansion import PILOT_CSV
        with PILOT_CSV.open() as stream:
            rows = list(csv.DictReader(stream))
        with self.assertRaisesRegex(ValueError, 'previous exact proof'):
            merge_coverage(rows, [])
        proofs = []
        for row in rows:
            if row['packaged_original_oval_equivalence'].startswith('PROVED'):
                proofs.append({'assessment': row['id'], 'assessment_sha256': row['proof_assessment_sha256'],
                    'program_sha256': row['proof_program_sha256'], 'case': 'test', 'outcome': 'PROVED'})
        self.assertEqual(merge_coverage(rows, proofs)[1]['new_proved'], 4)
        with self.assertRaisesRegex(ValueError, 'duplicate proof identity'):
            merge_coverage(rows, proofs + proofs[:1])
        with self.assertRaisesRegex(ValueError, 'denominator drift'):
            merge_coverage(rows + rows[:1], proofs)


if __name__ == '__main__':
    unittest.main()
