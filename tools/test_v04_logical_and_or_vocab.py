#!/usr/bin/env python3
"""Approved logical names and cardinalities occupy separate scopes (Refs #251 #248)."""
from copy import deepcopy
import unittest
from test_v04_clear_cardinality_schema import with_field
from v04_field_requirement import validate_test
from v04_canonical_result_plan import compile_canonical_result_plan, evaluate_supplied_results
from test_v04_canonical_result_plan import authored


class LogicalVocabTests(unittest.TestCase):
    def test_canonical_condition_operators_and_legacy_rejection(self):
        branch = {'fields': with_field()['fields']}
        for operator in ('and', 'or', 'one', 'xor'):
            req = {'items_found': 'one_or_more', 'items_satisfying': 'every',
                   operator: [deepcopy(branch), deepcopy(branch)]}
            validate_test({'require': req})
        for operator in ('all', 'any', 'odd'):
            req = {'items_found': 'one_or_more', 'items_satisfying': 'every', operator: [branch]}
            with self.assertRaises(ValueError): validate_test({'require': req})

    def test_one_is_exactly_one_branch_xor_is_odd_parity(self):
        supplied = {key: 'true' for key in ('left-test', 'right-test', 'third-test')}
        branches = [{'test': key} for key in supplied]
        for operator, expected in [('one', 'false'), ('xor', 'true')]:
            plan = compile_canonical_result_plan(authored({operator: branches}))
            self.assertEqual(evaluate_supplied_results(plan, supplied)['outcome'], expected)

    def test_cardinality_tokens_are_not_logical_operators(self):
        for operator in ('none', 'exactly_one', 'one_or_more', 'every'):
            req = {'items_found': 'one_or_more', 'items_satisfying': 'every',
                   operator: [{'fields': with_field()['fields']}]}
            with self.assertRaises(ValueError): validate_test({'require': req})


if __name__ == '__main__':
    unittest.main()
