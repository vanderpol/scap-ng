"""Independent fixed source/sample boundaries; no collector or runtime claims (#251)."""
from copy import deepcopy
from hashlib import sha256
import itertools
import json
import unittest
import xml.etree.ElementTree as ET

from audit_v04_bounded_source_validation import FIXTURES, load_case, namespace, run, result_contract_findings
from oval_result_truth_tables import (aggregate_operator, evaluate_collected_object_test,
    resolve_variable_reference, apply_variable_reference_context, evaluate_variable_entity_reference)
from v04_expanded_source_proof import ExpandedSource, ExpandedNative, expanded_compare
from v04_source_package_semantics import OD, Unsupported, literal


def fixture(rule):
    manifest = json.loads((FIXTURES / 'manifest.json').read_text())
    return load_case(next(r for r in manifest['cases'] if r['rule'] == rule))


class BoundedSourceValidation(unittest.TestCase):
    def test_fixed_eleven_accounting_and_deterministic_nonmutating_report(self):
        before = {p: sha256(p.read_bytes()).hexdigest() for p in FIXTURES.iterdir()}
        report = run()
        self.assertEqual(report, run())
        self.assertEqual(report['outcomes'], {'PROVED': 4, 'UNVERIFIABLE/UNSUPPORTED': 4,
            'EXCLUDED_SOURCE_INVALID': 1, 'EXCLUDED_SOURCE_DEPRECATED': 2})
        self.assertEqual(report['new_records_outside_frozen_floor'], 3)
        self.assertFalse(report['corpus_statuses_modified'])
        self.assertFalse(report['scanner_evaluated'])
        self.assertEqual(before, {p: sha256(p.read_bytes()).hexdigest() for p in before})

    def test_namespace_attribution_is_original_oval_node_not_xccdf_or_package(self):
        report = run()
        findings = report['source_findings_by_namespace']
        self.assertEqual(len(findings['DISA']), 1)
        self.assertEqual(findings['DISA'][0]['kind'], 'deprecated')
        self.assertEqual(len(findings['NIWC']), 3)
        self.assertEqual(sum(i['kind'] == 'invalid' for i in findings['NIWC']), 2)
        self.assertEqual(findings['UNATTRIBUTED'], [])
        case, _, _ = fixture('SV-215833')
        self.assertIn('mil.disa', case['source_rule'])
        self.assertEqual(namespace(case['source_definition']), 'NIWC')

    def test_real_count_retains_cast_aggregation_projection_and_source_state(self):
        case, source, _ = fixture('SV-215838')
        report = expanded_compare(source, case['source_definition'], case['native']['assessment'])
        self.assertEqual(report['outcome'], 'PROVED')
        term = report['comparisons'][0]['source_term']
        variable = term['object']['variable']['local']
        self.assertEqual(variable['datatype'], 'integer')
        values, = variable['expression']['count']
        self.assertEqual(values['values']['object']['capability'], 'iosxe.global')
        self.assertEqual(values['values']['field'], 'global_command')
        self.assertEqual(term['condition']['predicate']['operand'], {'datatype': 'integer', 'value': 2})

    def test_count_mutants_cannot_borrow_the_original_proof(self):
        case, _, _ = fixture('SV-215838')
        for change in ('cast', 'operation', 'operand', 'threshold', 'existence', 'matching', 'field-existence'):
            with self.subTest(change=change):
                assessment = deepcopy(case['native']['assessment'])
                variable = next(iter(assessment['variables'].values()))
                test = next(iter(assessment['tests'].values()))
                if change == 'cast': variable['datatype'] = 'string'
                elif change == 'operation': variable['expression']['function']['name'] = 'unique'
                elif change == 'operand': variable['expression']['function']['arguments'][0]['values']['field'] = 'different_field'
                elif change == 'threshold': test['require']['fields']['value']['greater_than_or_equal'] = 1
                elif change == 'existence': test['require']['items_found'] = 'may_be_absent'
                elif change == 'matching': test['require']['items_satisfying'] = 'one_or_more'
                else: test['require']['fields']['value']['values_found'] = 'may_be_absent'
                source = fixture('SV-215838')[1]
                self.assertNotEqual(expanded_compare(source, case['source_definition'], assessment)['outcome'], 'PROVED')

    def test_count_preserves_multiple_operands_duplicates_and_no_cartesian_rewrite(self):
        case, source, _ = fixture('SV-215838')
        node = ET.fromstring(f'<count xmlns="{OD}"><literal_component datatype="string">x</literal_component>'
                             '<literal_component datatype="string">x</literal_component></count>')
        expected = {'count': [{'literal': {'datatype': 'string', 'value': 'x'}}] * 2}
        self.assertEqual(source.function(node), expected)
        native = ExpandedNative(case['native']['assessment'])
        self.assertEqual(native.function({'function': {'name': 'count', 'arguments': [
            {'literal': {'datatype': 'string', 'value': 'x'}}] * 2, 'options': {}}}), expected)
        self.assertNotEqual(expected, {'count': expected['count'][:1]})

    def test_count_bad_arity_options_namespace_and_unproved_functions_fail_closed(self):
        case, source, _ = fixture('SV-215838')
        for xml in (f'<count xmlns="{OD}"/>', '<count xmlns="urn:other"><literal_component/></count>',
                    f'<count xmlns="{OD}" unknown="true"><literal_component>x</literal_component></count>'):
            with self.subTest(xml=xml), self.assertRaises(Unsupported): source.function(ET.fromstring(xml))
        native = ExpandedNative(case['native']['assessment'])
        for name, args, options in [('count', [], {}), ('count', [{'literal': 'x'}], {'sort': 'document'}),
                                    ('split', [{'literal': 'x'}], {'delimiter': ','})]:
            with self.subTest(name=name, options=options), self.assertRaises(ValueError):
                native.function({'function': {'name': name, 'arguments': args, 'options': options}})

    def test_captured_numeric_text_cast_is_valid_whole_configuration_line_is_not(self):
        self.assertEqual(literal('int', '5'), {'datatype': 'integer', 'value': 5})
        for text in ('exec-timeout 5 0', '', 'unknown'):
            with self.subTest(text=text), self.assertRaises(ValueError): literal('int', text)
        case, source, _ = fixture('SV-215833')
        # Keep both original diagnostic edges: they are input Variable types,
        # not a blanket prohibition on int(regex_capture(...)).
        self.assertEqual({i['source_id'].rsplit(':', 1)[-1] for i in case['original_component_validity']['issues']},
                         {'21583306', '21583307'})
        node = ET.fromstring(f'<oval_definitions xmlns="{OD}"><variables>'
            '<local_variable id="numeric-capture" version="1" datatype="int">'
            '<regex_capture pattern="([0-9]+)"><literal_component datatype="string">5</literal_component>'
            '</regex_capture></local_variable></variables></oval_definitions>')
        term = ExpandedSource(node).variable('numeric-capture')['local']
        self.assertEqual(term['datatype'], 'integer')
        self.assertIn('regex_capture', term['expression'])

    def test_four_valid_windows_all_exist_cases_remain_unproved(self):
        for rule in ('SV-278021', 'SV-278023', 'SV-278101', 'SV-278131'):
            with self.subTest(rule=rule):
                case, source, _ = fixture(rule)
                result = expanded_compare(source, case['source_definition'], case['native']['assessment'])
                self.assertEqual(result['outcome'], 'UNVERIFIABLE/UNSUPPORTED')
                self.assertTrue(all('all_exist' in o['reason'] for o in result['unsupported_obligations']))

    def test_existing_reference_model_complete_and_partial_population_observations(self):
        for exists in (0, 1, 3):
            for existence in ('all_exist', 'at_least_one_exists'):
                self.assertEqual(evaluate_collected_object_test('complete', existence=existence,
                    has_state=False, exists=exists), 'true' if exists else 'false')
        self.assertEqual(evaluate_collected_object_test('complete', existence='all_exist',
            has_state=False, exists=1, does_not_exist=1), 'false')
        self.assertEqual(evaluate_collected_object_test('complete', existence='at_least_one_exists',
            has_state=False, exists=1, does_not_exist=1), 'true')
        self.assertEqual(evaluate_collected_object_test('incomplete', existence='all_exist',
            check='at least one', exists=1, item_results=['true']), 'unknown')
        self.assertEqual(evaluate_collected_object_test('incomplete', existence='at_least_one_exists',
            check='at least one', exists=1, item_results=['true']), 'true')
        for flag, expected in [('error', 'error'), ('not collected', 'unknown'), ('not applicable', 'not applicable')]:
            self.assertEqual(evaluate_collected_object_test(flag, existence='all_exist', has_state=False), expected)

    def test_incomplete_reference_model_discrepancy_is_reported_not_silently_resolved(self):
        finding, = result_contract_findings()
        self.assertEqual(finding['classification'], 'REFERENCE_MODEL_REVIEW_REQUIRED')
        self.assertNotEqual(finding['existing_reference_helper_result'], finding['literal_exception_3a_result'])
        self.assertEqual(finding['source_test'], 'oval:mil.disa.stig.win:tst:25327800')

    def test_variable_zero_values_and_error_unknown_do_not_become_numeric_zero(self):
        empty = resolve_variable_reference([])
        self.assertEqual(apply_variable_reference_context(empty, 'object'), 'does_not_exist')
        self.assertEqual(apply_variable_reference_context(empty, 'state'), 'error')
        for status, quantifier in itertools.product(('error', 'unknown', 'not evaluated'), ('all', 'at least one', 'none satisfy')):
            self.assertEqual(evaluate_variable_entity_reference(variable_status=status, var_check=quantifier,
                entity_check='all'), status)

    def test_logic_one_vs_xor_and_nonboolean_states_are_not_two_state_simplified(self):
        self.assertEqual(aggregate_operator('ONE', ['true'] * 3), 'false')
        self.assertEqual(aggregate_operator('XOR', ['true'] * 3), 'true')
        self.assertEqual(aggregate_operator('AND', ['true', 'error']), 'error')
        self.assertEqual(aggregate_operator('OR', ['false', 'unknown']), 'unknown')
        for operator, values in itertools.product(('AND', 'OR'), itertools.product(
                ('true', 'false', 'error', 'unknown', 'not evaluated', 'not applicable'), repeat=3)):
            self.assertEqual(aggregate_operator(operator, values), aggregate_operator(operator, values[::-1]))


if __name__ == '__main__': unittest.main()
