#!/usr/bin/env python3
"""Independent truth-table checks derived from pinned OVAL 5.12.3 XSD appinfo."""
import unittest

from oval_result_truth_tables import (
    TRUE, FALSE, ERROR, UNKNOWN, NOT_EVALUATED, NOT_APPLICABLE,
    aggregate_check, aggregate_operator, aggregate_existence,
)


class CheckEnumerationTruthTables(unittest.TestCase):
    def test_all_precedence(self):
        self.assertEqual(aggregate_check("all", [TRUE, TRUE]), TRUE)
        self.assertEqual(aggregate_check("all", [TRUE, FALSE, ERROR]), FALSE)
        self.assertEqual(aggregate_check("all", [TRUE, ERROR, UNKNOWN]), ERROR)
        self.assertEqual(aggregate_check("all", [TRUE, UNKNOWN, NOT_EVALUATED]), UNKNOWN)
        self.assertEqual(aggregate_check("all", [TRUE, NOT_EVALUATED]), NOT_EVALUATED)
        self.assertEqual(aggregate_check("all", [NOT_APPLICABLE]), NOT_APPLICABLE)

    def test_at_least_one_precedence(self):
        self.assertEqual(aggregate_check("at least one", [FALSE, TRUE, ERROR]), TRUE)
        self.assertEqual(aggregate_check("at least one", [FALSE, ERROR, UNKNOWN]), ERROR)
        self.assertEqual(aggregate_check("at least one", [FALSE, UNKNOWN]), UNKNOWN)
        self.assertEqual(aggregate_check("at least one", [FALSE, NOT_EVALUATED]), NOT_EVALUATED)
        self.assertEqual(aggregate_check("at least one", [FALSE, FALSE]), FALSE)
        self.assertEqual(aggregate_check("at least one", [NOT_APPLICABLE]), NOT_APPLICABLE)

    def test_only_one(self):
        self.assertEqual(aggregate_check("only one", [TRUE, FALSE]), TRUE)
        self.assertEqual(aggregate_check("only one", [TRUE, TRUE, ERROR]), FALSE)
        self.assertEqual(aggregate_check("only one", [FALSE, ERROR]), ERROR)
        self.assertEqual(aggregate_check("only one", [FALSE, UNKNOWN]), UNKNOWN)
        self.assertEqual(aggregate_check("only one", [FALSE, NOT_EVALUATED]), NOT_EVALUATED)
        self.assertEqual(aggregate_check("only one", [FALSE, FALSE]), FALSE)
        self.assertEqual(aggregate_check("only one", [NOT_APPLICABLE]), NOT_APPLICABLE)

    def test_none_satisfy(self):
        self.assertEqual(aggregate_check("none satisfy", [FALSE, FALSE]), TRUE)
        self.assertEqual(aggregate_check("none satisfy", [TRUE, ERROR]), FALSE)
        self.assertEqual(aggregate_check("none satisfy", [FALSE, ERROR]), ERROR)
        self.assertEqual(aggregate_check("none satisfy", [FALSE, UNKNOWN]), UNKNOWN)
        self.assertEqual(aggregate_check("none satisfy", [FALSE, NOT_EVALUATED]), NOT_EVALUATED)
        self.assertEqual(aggregate_check("none satisfy", [NOT_APPLICABLE]), NOT_APPLICABLE)


class OperatorTruthTables(unittest.TestCase):
    def test_and_or_one(self):
        self.assertEqual(aggregate_operator("AND", [TRUE, FALSE, ERROR]), FALSE)
        self.assertEqual(aggregate_operator("OR", [FALSE, TRUE, ERROR]), TRUE)
        self.assertEqual(aggregate_operator("ONE", [TRUE, FALSE]), TRUE)
        self.assertEqual(aggregate_operator("ONE", [TRUE, TRUE, UNKNOWN]), FALSE)

    def test_xor(self):
        self.assertEqual(aggregate_operator("XOR", [TRUE, FALSE, FALSE]), TRUE)
        self.assertEqual(aggregate_operator("XOR", [TRUE, TRUE, FALSE]), FALSE)
        self.assertEqual(aggregate_operator("XOR", [TRUE, ERROR]), ERROR)
        self.assertEqual(aggregate_operator("XOR", [TRUE, UNKNOWN]), UNKNOWN)
        self.assertEqual(aggregate_operator("XOR", [TRUE, NOT_EVALUATED]), NOT_EVALUATED)
        self.assertEqual(aggregate_operator("XOR", [NOT_APPLICABLE]), NOT_APPLICABLE)


class ExistenceTruthTables(unittest.TestCase):
    def test_all_exist(self):
        self.assertEqual(aggregate_existence("all_exist", exists=1), TRUE)
        self.assertEqual(aggregate_existence("all_exist"), FALSE)
        self.assertEqual(aggregate_existence("all_exist", exists=2, does_not_exist=1, error=1), FALSE)
        self.assertEqual(aggregate_existence("all_exist", error=1), ERROR)
        self.assertEqual(aggregate_existence("all_exist", not_collected=1), UNKNOWN)

    def test_any_exist(self):
        self.assertEqual(aggregate_existence("any_exist"), TRUE)
        self.assertEqual(aggregate_existence("any_exist", does_not_exist=3, not_collected=2), TRUE)
        self.assertEqual(aggregate_existence("any_exist", exists=1, error=2), TRUE)
        self.assertEqual(aggregate_existence("any_exist", error=1), ERROR)

    def test_at_least_one_exists(self):
        self.assertEqual(aggregate_existence("at_least_one_exists", exists=1, error=1), TRUE)
        self.assertEqual(aggregate_existence("at_least_one_exists"), FALSE)
        self.assertEqual(aggregate_existence("at_least_one_exists", error=1), ERROR)
        self.assertEqual(aggregate_existence("at_least_one_exists", not_collected=1), UNKNOWN)

    def test_none_exist(self):
        self.assertEqual(aggregate_existence("none_exist"), TRUE)
        self.assertEqual(aggregate_existence("none_exist", exists=1, error=1), FALSE)
        self.assertEqual(aggregate_existence("none_exist", error=1), ERROR)
        self.assertEqual(aggregate_existence("none_exist", not_collected=1), UNKNOWN)

    def test_only_one_exists(self):
        self.assertEqual(aggregate_existence("only_one_exists", exists=1), TRUE)
        self.assertEqual(aggregate_existence("only_one_exists"), FALSE)
        self.assertEqual(aggregate_existence("only_one_exists", exists=2, error=1), FALSE)
        self.assertEqual(aggregate_existence("only_one_exists", error=1), ERROR)
        self.assertEqual(aggregate_existence("only_one_exists", not_collected=1), UNKNOWN)

    def test_rejects_unspecified_empty_boolean_aggregation(self):
        with self.assertRaises(ValueError):
            aggregate_check("all", [])
        with self.assertRaises(ValueError):
            aggregate_operator("AND", [])


if __name__ == "__main__":
    unittest.main()
