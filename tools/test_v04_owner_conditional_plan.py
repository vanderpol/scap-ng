"""Decisions 8/24–26: supplied outcomes and independent instruction reader (#255/#268)."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from jsonschema import Draft202012Validator
from test_v04_canonical_result_plan import authored
from v04_canonical_result_plan import compile_canonical_result_plan, evaluate_supplied_results
from verify_v04_package_consumer import expression_plan

ROOT = Path(__file__).resolve().parents[1]


def branch():
    return {'if': {'test': 'left-test'}, 'then': {'test': 'right-test'},
            'else': {'test': 'third-test'}}


class Reads(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reads = []

    def __getitem__(self, name):
        self.reads.append(name)
        return super().__getitem__(name)


class OwnerConditionalPlan(unittest.TestCase):
    def test_all_six_guard_results_and_only_selected_branch_reads(self):
        plan = compile_canonical_result_plan(authored(branch()))
        for state in ('true', 'false', 'error', 'unknown', 'not_evaluated', 'not_applicable'):
            with self.subTest(state=state):
                supplied = Reads({'left-test': state, 'right-test': 'true', 'third-test': 'false'})
                result = evaluate_supplied_results(plan, supplied)
                self.assertEqual(result['outcome'], {'true': 'true', 'false': 'false'}.get(state, state))
                expected = ['left-test'] + (['right-test'] if state == 'true' else ['third-test'] if state == 'false' else [])
                self.assertEqual(supplied.reads, expected)
                self.assertFalse(result['scanner_executed'])
                self.assertFalse(result['tests_evaluated'])

    def test_ordered_else_if_first_true_wins_even_when_selected_result_is_false(self):
        tree = {'if': {'test': 'left-test'}, 'then': {'not_applicable': {'reason': 'Initial condition'}},
                'else_if': [
                    {'if': {'test': 'right-test'}, 'then': {'test': 'third-test'}},
                    {'if': {'test': 'third-test'}, 'then': {'not_evaluated': {'reason': 'Later condition'}}}],
                'else': {'not_applicable': {'reason': 'No selected mode'}}}
        plan = compile_canonical_result_plan(authored(tree))
        supplied = Reads({'left-test': 'false', 'right-test': 'true', 'third-test': 'false'})
        result = evaluate_supplied_results(plan, supplied)
        self.assertEqual(result['outcome'], 'false')
        self.assertEqual(supplied.reads, ['left-test', 'right-test', 'third-test'])
        self.assertFalse(result['manual_follow_up_required'])
        self.assertEqual(result['explicit_terminal_outcomes'], [])

    def test_indeterminate_else_if_does_not_fall_through(self):
        tree = branch()
        tree['else_if'] = [{'if': {'test': 'right-test'}, 'then': {'test': 'third-test'}}]
        plan = compile_canonical_result_plan(authored(tree))
        for state in ('error', 'unknown', 'not_evaluated', 'not_applicable'):
            result = evaluate_supplied_results(plan, {'left-test': 'false', 'right-test': state})
            self.assertEqual(result['outcome'], state)

    def test_explicit_terminals_retain_reasons_and_do_not_turn_errors_or_failures_into_followup(self):
        for terminal in ('not_applicable', 'not_evaluated'):
            plan = compile_canonical_result_plan(authored({terminal: {'reason': 'Remote inspection unavailable'}}))
            result = evaluate_supplied_results(plan, {})
            self.assertEqual(result['outcome'], terminal)
            self.assertEqual(result['explicit_terminal_outcomes'][0]['reason'], 'Remote inspection unavailable')
            self.assertEqual(result['manual_follow_up_required'], terminal == 'not_evaluated')
        tree = branch()
        tree['else'] = {'not_evaluated': {'reason': 'Remote inspection unavailable'}}
        plan = compile_canonical_result_plan(authored(tree))
        for state in ('false', 'error'):
            result = evaluate_supplied_results(plan, {'left-test': 'true', 'right-test': state})
            self.assertEqual(result['outcome'], state)
            self.assertFalse(result['manual_follow_up_required'])

    def test_missing_unselected_outcome_allowed_missing_selected_outcome_errors(self):
        plan = compile_canonical_result_plan(authored(branch()))
        self.assertEqual(evaluate_supplied_results(plan, {'left-test': 'true', 'right-test': 'true'})['outcome'], 'true')
        with self.assertRaisesRegex(ValueError, 'selected right-test'):
            evaluate_supplied_results(plan, {'left-test': 'true'})
        with self.assertRaisesRegex(ValueError, 'undeclared'):
            evaluate_supplied_results(plan, {'left-test': 'unknown', 'other-test': 'true'})

    def test_static_reference_closure_includes_every_branch(self):
        source = authored(branch())
        source['tests'].pop('third-test')
        with self.assertRaisesRegex(ValueError, 'unresolved test'):
            compile_canonical_result_plan(source)

    def test_conditional_dependency_context_is_external_and_guarded(self):
        tree = branch()
        tree['then'] = {'assessment': 'remote-assessment'}
        source = authored(tree)
        source['class'] = 'vulnerability'
        source['dependencies'] = {'remote-assessment': {'assessment_id': 'actual-remote-assessment', 'purpose': 'assessment'}}
        plan = compile_canonical_result_plan(source)
        self.assertEqual(evaluate_supplied_results(plan, {'left-test': 'unknown'})['outcome'], 'unknown')
        self.assertEqual(evaluate_supplied_results(plan, {'left-test': 'true'}, {'remote-assessment': 'false'})['outcome'], 'false')
        self.assertEqual(source['class'], 'vulnerability')
        self.assertNotIn('purpose', source)

    def test_independent_reader_matches_blocks_and_detects_branch_reordering(self):
        tree = branch()
        tree['else_if'] = [{'if': {'test': 'right-test'}, 'then': {'not_applicable': {'reason': 'Alternate'}}}]
        source = authored({'and': [tree, {'not': {'test': 'third-test'}}]})
        plan = compile_canonical_result_plan(source)
        instructions, required = expression_plan(source)
        self.assertEqual(instructions, plan['instructions'])
        self.assertEqual(required, plan['requires'])
        changed = deepcopy(instructions)
        changed[0]['branches'].reverse()
        self.assertNotEqual(changed, plan['instructions'])

    def test_schema_and_compiler_reject_missing_else_bad_order_shape_and_reason(self):
        schema = Draft202012Validator(json.loads((ROOT / 'schema/v0.4.0/expression.schema.json').read_text()))
        valid = branch()
        valid['else_if'] = [{'if': {'test': 'right-test'}, 'then': {'not_evaluated': {'reason': 'Remote ACL'}}}]
        self.assertTrue(schema.is_valid(valid))
        bad = []
        missing = deepcopy(valid); del missing['else']; bad.append(missing)
        wrong = deepcopy(valid); wrong['else_if'] = {'if': {'test': 'right-test'}}; bad.append(wrong)
        extra = deepcopy(valid); extra['else_if'][0]['else'] = {'test': 'third-test'}; bad.append(extra)
        bad.extend([{kind: {'reason': reason}} for kind in ('not_applicable', 'not_evaluated') for reason in ('', '  ', None)])
        for tree in bad:
            with self.subTest(tree=tree):
                self.assertFalse(schema.is_valid(tree))
                with self.assertRaises(ValueError): compile_canonical_result_plan(authored(tree))

    def test_legacy_native_boolean_aliases_rejected_even_inside_conditional(self):
        for alias in ('all', 'any', 'odd'):
            tree = branch(); tree['then'] = {alias: [{'test': 'right-test'}]}
            with self.subTest(alias=alias), self.assertRaises(ValueError):
                compile_canonical_result_plan(authored(tree))

    def test_current_authoring_compiles_and_independent_package_reader_checks_branch_blocks(self):
        from test_v04_package_consumer import fixture
        from v04_native_bundle_compiler import build_bundle
        from verify_v04_package_consumer import verify
        documents = fixture()  # Explicit new copy; historical fixture is untouched.
        assessment = next(d['assessment'] for d in documents.values() if 'assessment' in d)
        assessment.pop('purpose')
        test = assessment['tests']['file-mode-test']
        test['require']['field_requirement'] = {'values_found': 'one_or_more', 'values_matching': 'every'}
        test['require']['fields'] = {'owner_uid': {'equals': 0, 'datatype': 'integer'}}
        assessment['tests']['alternate-file-test'] = deepcopy(test)
        assessment['evaluate'] = {'if': {'test': 'file-mode-test'},
            'then': {'not_evaluated': {'reason': 'Explicitly limited remote inspection'}},
            'else_if': [{'if': {'test': 'alternate-file-test'},
                         'then': {'not_applicable': {'reason': 'Alternate condition excludes this inspection'}}}],
            'else': {'not_applicable': {'reason': 'Remote inspection does not apply'}}}
        raw, _ = build_bundle(documents)
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory) / 'sample.scapng'
            package.write_bytes(raw)
            external = {(kind, body['id']): (path, document)
                        for path, document in documents.items() for kind, body in document.items()}
            self.assertEqual(verify(package, source=external)['status'], 'INDEPENDENT_PACKAGE_CONSUMER_PASS')


if __name__ == '__main__': unittest.main()
