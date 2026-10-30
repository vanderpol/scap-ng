"""Proof-obligation regressions for non-release authoring projections (#264)."""

from copy import deepcopy
import unittest

from build_v04_proposed_authoring_review import proposal, effective_counts, without_policies
from v04_field_requirement import validate_test


PAIR = {'values_found': 'one_or_more', 'values_matching': 'every'}


class ProposedAuthoringReview(unittest.TestCase):
    def test_single_scalar_field_is_test_wide_even_when_longer(self):
        old = {'items_found': 'one_or_more', 'items_satisfying': 'every',
               'fields': {'mount_options': {'equals': 'nosuid', **PAIR}}}
        new, status = proposal(old)
        self.assertEqual(new['field_requirement'], PAIR)
        self.assertEqual(new['fields'], {'mount_options': {'equals': 'nosuid'}})
        self.assertEqual(status['changes'], 1)
        self.assertEqual(effective_counts(old), effective_counts(new))
        validate_test({'capability': 'linux.partition', 'object': {}, 'require': new})

    def test_two_scalar_fields_are_implicit_and_under_one_policy(self):
        old = {'items_found': 'one_or_more', 'items_satisfying': 'every',
               'fields': {'type': {'equals': 'dword', **PAIR},
                          'value': {'equals': 1, 'datatype': 'integer', **PAIR}}}
        new, status = proposal(old)
        self.assertEqual(status['changes'], 2)
        self.assertEqual(new['fields'], {'type': {'equals': 'dword'},
                                         'value': {'equals': 1, 'datatype': 'integer'}})
        self.assertEqual(without_policies(old), without_policies(new))
        validate_test({'capability': 'windows.registry', 'object': {}, 'require': new})

    def test_different_pair_stays_as_local_override(self):
        exceptional = {'values_found': 'may_be_absent', 'values_matching': 'every'}
        old = {'items_found': 'one_or_more', 'items_satisfying': 'every',
               'fields': {'a': {'equals': 1, **PAIR},
                          'b': {'equals': 2, **exceptional}}}
        new, status = proposal(old)
        self.assertEqual(status['overrides'], 1)
        self.assertEqual(new['field_requirement'], PAIR)
        self.assertEqual(new['fields']['a'], {'equals': 1})
        self.assertEqual(new['fields']['b'], {'equals': 2, **exceptional})
        self.assertEqual(effective_counts(old), effective_counts(new))

    def test_or_and_xor_one_boundaries_remain_untouched(self):
        for operator in ('and', 'or', 'one', 'xor'):
            old = {'items_found': 'one_or_more', 'items_satisfying': 'every',
                   operator: [{'fields': {'a': {'equals': 1, **PAIR}}},
                              {'fields': {'b': {'equals': 2, **PAIR}}}]}
            new, _ = proposal(old)
            self.assertEqual(set(new) & {'and', 'or', 'one', 'xor'}, {operator})
            self.assertEqual(without_policies(old), without_policies(new))
            self.assertEqual(effective_counts(old), effective_counts(new))
            validate_test({'capability': 'windows.registry', 'object': {}, 'require': new})

    def test_absence_is_not_compared_or_silently_defaulted(self):
        old = {'items_found': 'one_or_more', 'items_satisfying': 'every',
               'fields': {'a': {'values_found': 'none'},
                          'b': {'equals': 1, **PAIR}}}
        new, _ = proposal(old)
        self.assertEqual(new['fields']['a'], {'values_found': 'none'})
        self.assertEqual(effective_counts(old), effective_counts(new))
        validate_test({'capability': 'windows.registry', 'object': {}, 'require': new})

    def test_record_member_policies_are_preserved(self):
        old = {'items_found': 'one_or_more', 'items_satisfying': 'every',
               'fields': {'result': {'record': {
                   'records_found': 'one_or_more', 'records_matching': 'every',
                   'fields': {'domainrole': {'equals': '1', **PAIR}}}}}}
        new, status = proposal(old)
        self.assertEqual(new, old)
        self.assertEqual(status['status'], 'no-comparison-field')
        validate_test({'capability': 'windows.wmi.query', 'object': {}, 'require': new})

    def test_item_presence_stays_policy_free(self):
        old = {'items_found': 'none'}
        new, status = proposal(old)
        self.assertEqual(new, old)
        self.assertEqual(status['status'], 'item-presence-only')
        validate_test({'capability': 'windows.service', 'object': {}, 'require': new})


if __name__ == '__main__':
    unittest.main()
