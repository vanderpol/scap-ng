"""Bounded 0.4 human-authoring projection regressions (Refs #264)."""

from copy import deepcopy
from pathlib import Path
import json
import unittest

from v04_human_authoring_compact import (
    compact_source_state, compact_test_requirement, restore,
)
from v04_field_requirement import validate_test


PAIR = {'values_found': 'one_or_more', 'values_matching': 'every'}
ROOT = Path(__file__).resolve().parents[1]


def field(name, value, policy=None):
    return {'fields': {name: {'equals': value, **(policy or PAIR)}}}


def require(conditions, operator='and'):
    return {'items_found': 'one_or_more', 'items_satisfying': 'every',
            operator: conditions}


def check(required):
    validate_test({'test_title': 'bounded registry example',
                   'capability': 'windows.registry',
                   'object': {'hive': {'equals': 'local_machine'},
                              'key': {'equals': r'Software\Microsoft\Windows\CurrentVersion\Policies\System'},
                              'name': {'equals': 'EnableVirtualization'}},
                   'require': required, 'reported_elements': 'all'})


class HumanAuthoringCompact(unittest.TestCase):
    def test_single_oval_state_and_compacts_to_inherited_policy(self):
        source = {'and': [field('type', 'dword'),
                          {'fields': {'value': {'equals': 1, 'datatype': 'integer', **PAIR}}}]}
        combined, state_edit = compact_source_state(source)
        self.assertEqual(list(combined['fields']), ['type', 'value'])
        self.assertEqual(restore(combined, state_edit), source)

        root = {'items_found': 'one_or_more', 'items_satisfying': 'every', **combined}
        short, test_edit = compact_test_requirement(root)
        self.assertEqual(short['field_requirement'], PAIR)
        self.assertEqual(short['fields']['type'], {'equals': 'dword'})
        self.assertEqual(short['fields']['value'], {'equals': 1, 'datatype': 'integer'})
        self.assertEqual(restore(short, test_edit), root)
        check(short)
        self.assertEqual(compact_test_requirement(short), (short, None))
        self.assertEqual(compact_source_state(combined), (combined, None))

    def test_mixed_cardinalities_stay_explicit_local_override(self):
        optional = {'values_found': 'may_be_absent', 'values_matching': 'every'}
        root = require([field('type', 'dword'), field('value', 1),
                        field('optional_field', 'x', optional)])
        short, edit = compact_test_requirement(root)
        self.assertEqual(short['field_requirement'], PAIR)
        self.assertEqual(short['and'][0]['fields']['type'], {'equals': 'dword'})
        self.assertEqual(short['and'][2]['fields']['optional_field'],
                         {'equals': 'x', **optional})
        self.assertEqual(restore(short, edit), root)

    def test_or_and_one_xor_boundaries_remain_unchanged(self):
        for operator in ('or', 'one', 'xor', 'and'):
            root = require([field('a', 1), field('b', 2)], operator)
            short, edit = compact_test_requirement(root)
            self.assertEqual(set(short) & {'and', 'or', 'one', 'xor'}, {operator})
            self.assertEqual(len(short[operator]), 2)
            self.assertEqual(restore(short, edit), root)

    def test_multiple_source_states_never_auto_merge(self):
        # The caller separately presents each source State. It must not call
        # compact_source_state on the Test's cross-State AND.
        state1, _ = compact_source_state({'and': [field('a', 1), field('b', 2)]})
        state2, _ = compact_source_state({'and': [field('c', 3), field('d', 4)]})
        root = require([state1, state2])
        short, edit = compact_test_requirement(root)
        self.assertEqual(len(short['and']), 2)
        self.assertEqual(set(short['and'][0]['fields']), {'a', 'b'})
        self.assertEqual(set(short['and'][1]['fields']), {'c', 'd'})
        self.assertEqual(restore(short, edit), root)

    def test_duplicate_name_record_absence_and_missing_policy_block_state_fold(self):
        blocked = [
            {'and': [field('x', 1), field('x', 2)]},
            {'and': [field('x', 1), {'fields': {'r': {'record': {'fields': {}}}}}]},
            {'and': [field('x', 1), {'fields': {'y': {'values_found': 'none'}}}]},
            {'and': [field('x', 1), {'or': [field('z', 2)]}]},
        ]
        for source in blocked:
            with self.subTest(source=source):
                self.assertEqual(compact_source_state(source), (source, None))
        # Any absence-only leaf vetoes hoisting instead of adding an
        # inherited matching quantifier to a predicate without comparison.
        root = require([field('a', 1), field('b', 2),
                        {'fields': {'c': {'values_found': 'none'}}}])
        self.assertEqual(compact_test_requirement(root), (root, None))

    def test_non_uniform_pair_without_common_majority_is_unchanged(self):
        required = require([field('a', 1), field('b', 2,
                            {'values_found': 'exactly_one', 'values_matching': 'every'})])
        self.assertEqual(compact_test_requirement(required), (required, None))

    def test_edited_candidate_cannot_be_recovered_as_original(self):
        root = require([field('a', 1), field('b', 2)])
        short, edit = compact_test_requirement(root)
        altered = deepcopy(short)
        altered['and'][1]['fields']['b']['equals'] = 3
        with self.assertRaisesRegex(ValueError, 'changed'):
            restore(altered, edit)

    def test_real_source_fixture_opt_in_converts_and_ledger_marks_unverified(self):
        from v04_direct_scap_source import SourceModel
        from v04_direct_converter import convert
        from v04_expanded_source_proof import ExpandedSource, ExpandedNative
        from v04_native_bundle_compiler import build_bundle
        fixture = ROOT / 'tests/fixtures/v04-direct-prototype'
        pins = json.loads((fixture / 'provenance.json').read_text())
        source = SourceModel(fixture / pins['fixture'], pins['zip_sha256'])
        baseline, _ = convert(source, pins['rules'])
        candidate, trace = convert(source, pins['rules'], human_compact=True)
        self.assertEqual(set(baseline), set(candidate))
        built, _ = build_bundle(candidate)
        self.assertTrue(built.startswith(b'PK'), 'compact native source must compile')
        for path in baseline:
            if 'assessment' in baseline[path]:
                self.assertEqual(baseline[path]['assessment']['id'],
                                 candidate[path]['assessment']['id'])
                for test in candidate[path]['assessment']['tests'].values():
                    validate_test(test)
        by_assessment = {doc['assessment']['id']: doc['assessment']
                         for doc in candidate.values() if 'assessment' in doc}
        for binding in trace['rules']:
            if not binding.get('human_authoring_compaction_review'):
                continue
            original_reader = ExpandedSource(source.components[binding['component']])
            converted_reader = ExpandedNative(by_assessment[binding['assessment']])
            for source_id, node in binding['dependencies'].items():
                if node['kind'] != 'test':
                    continue
                # The source and native readers independently reduce their
                # respective XML and YAML boolean + cardinality expressions.
                from v04_direct_converter import native_identifier
                expected = original_reader.test(source_id)
                actual = converted_reader.test(native_identifier(
                    source.node(binding['component'], source_id, 'test'), 'test'))
                self.assertEqual(expected, actual)
        edits = [binding for binding in trace['rules']
                 if binding.get('human_authoring_compaction_review')]
        self.assertTrue(edits, 'source fixture must exercise at least one compaction')
        self.assertTrue(all(row['conversion_status'] == 'CONVERTED_UNVERIFIED'
                            and row['independent_static_proof_eligible'] is False
                            for row in edits))


if __name__ == '__main__':
    unittest.main()
