#!/usr/bin/env python3
"""Exhaustive bounded oracle checks against pinned OVAL 5.12.3 evaluation charts.

The expected-result functions below are intentionally written independently of
oval_result_truth_tables.py and follow the count conditions printed in
oval-common-schema.xsd evaluation_chart appinfo. Counts 0..2 are sufficient to
exercise every chart predicate (0, 1, 2+ and 0+).
"""
from itertools import product
import unittest

from oval_result_truth_tables import (
    TRUE, FALSE, ERROR, UNKNOWN, NOT_EVALUATED, NOT_APPLICABLE,
    aggregate_check, aggregate_operator, aggregate_existence,
    evaluate_state_entity_existence,
)

RESULT_ORDER = (TRUE, FALSE, ERROR, UNKNOWN, NOT_EVALUATED, NOT_APPLICABLE)


def expand_result_counts(counts):
    values = []
    for value, count in zip(RESULT_ORDER, counts):
        values.extend([value] * count)
    return values


def chart_check(check, counts):
    t, f, e, u, ne, na = counts
    if check == "all":
        if f >= 1: return FALSE
        if e >= 1: return ERROR
        if u >= 1: return UNKNOWN
        if ne >= 1: return NOT_EVALUATED
        if t >= 1: return TRUE
        if na >= 1: return NOT_APPLICABLE
    elif check == "at least one":
        if t >= 1: return TRUE
        if e >= 1: return ERROR
        if u >= 1: return UNKNOWN
        if ne >= 1: return NOT_EVALUATED
        if f >= 1: return FALSE
        if na >= 1: return NOT_APPLICABLE
    elif check == "only one":
        if t >= 2: return FALSE
        if t == 1 and e == u == ne == 0: return TRUE
        if t == 0 and f >= 1 and e == u == ne == 0: return FALSE
        if e >= 1: return ERROR
        if u >= 1: return UNKNOWN
        if ne >= 1: return NOT_EVALUATED
        if t == 0 and f == 0 and na >= 1: return NOT_APPLICABLE
    elif check == "none satisfy":
        if t >= 1: return FALSE
        if e >= 1: return ERROR
        if u >= 1: return UNKNOWN
        if ne >= 1: return NOT_EVALUATED
        if f >= 1: return TRUE
        if na >= 1: return NOT_APPLICABLE
    raise AssertionError((check, counts))


def chart_existence(mode, counts):
    ex, de, er, nc = counts
    if mode == "all_exist":
        if de >= 1: return FALSE
        if er >= 1: return ERROR
        if nc >= 1: return UNKNOWN
        return TRUE if ex >= 1 else FALSE
    if mode == "any_exist":
        if ex >= 1: return TRUE
        if er >= 1: return ERROR
        return TRUE
    if mode == "at_least_one_exists":
        if ex >= 1: return TRUE
        if er >= 1: return ERROR
        if nc >= 1: return UNKNOWN
        return FALSE
    if mode == "none_exist":
        if ex >= 1: return FALSE
        if er >= 1: return ERROR
        if nc >= 1: return UNKNOWN
        return TRUE
    if mode == "only_one_exists":
        if ex >= 2: return FALSE
        if er >= 1: return ERROR
        if nc >= 1: return UNKNOWN
        return TRUE if ex == 1 else FALSE
    raise AssertionError(mode)


class ExhaustiveCheckChartParity(unittest.TestCase):
    def test_all_nonempty_bounded_result_multisets(self):
        for counts in product(range(3), repeat=6):
            if not any(counts):
                continue
            values = expand_result_counts(counts)
            for check in ("all", "at least one", "only one", "none satisfy"):
                with self.subTest(check=check, counts=counts):
                    self.assertEqual(
                        aggregate_check(check, values),
                        chart_check(check, counts),
                    )

    def test_and_or_one_share_the_same_pinned_charts(self):
        mapping = {
            "AND": "all",
            "OR": "at least one",
            "ONE": "only one",
        }
        for counts in product(range(3), repeat=6):
            if not any(counts):
                continue
            values = expand_result_counts(counts)
            for operator, check in mapping.items():
                with self.subTest(operator=operator, counts=counts):
                    self.assertEqual(
                        aggregate_operator(operator, values),
                        chart_check(check, counts),
                    )


class ExhaustiveExistenceChartParity(unittest.TestCase):
    def test_all_bounded_item_status_multisets(self):
        modes = (
            "all_exist",
            "any_exist",
            "at_least_one_exists",
            "none_exist",
            "only_one_exists",
        )
        for counts in product(range(3), repeat=4):
            ex, de, er, nc = counts
            for mode in modes:
                with self.subTest(mode=mode, counts=counts):
                    expected = chart_existence(mode, counts)
                    self.assertEqual(
                        aggregate_existence(
                            mode,
                            exists=ex,
                            does_not_exist=de,
                            error=er,
                            not_collected=nc,
                        ),
                        expected,
                    )
                    self.assertEqual(
                        evaluate_state_entity_existence(
                            mode,
                            exists=ex,
                            does_not_exist=de,
                            error=er,
                            not_collected=nc,
                        ),
                        expected,
                    )


if __name__ == "__main__":
    unittest.main()
