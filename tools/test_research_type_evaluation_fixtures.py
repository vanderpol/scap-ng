#!/usr/bin/env python3
"""Focused known-result OVAL-comparison research gate (#200).

Checks independent, source-described expected outcomes against both original
typed predicates and compact typed-operator predicates.

The tiny reference interpreter below covers ONLY tested string/int/bool,
dotted-numeric-version, IPv4/IPv6 comparisons. It is NOT an OVAL evaluator,
a scanner, an RPM/Debian implementation, an Item-collection engine, or proof
of SCAP 1.4 end-to-end equivalence. Unknown/error propagation from Variables,
Tests and collections remains outside this limited fixture gate.
"""
from __future__ import annotations

from ipaddress import ip_network
import json
from pathlib import Path
import re
import unittest

from research_type_syntax_codec import to_authoring, to_canonical

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "tests/datatype-operator-evaluation-0.3/expected-cases.json"
RELATIONAL = {
    "greater_than", "greater_than_or_equal",
    "less_than", "less_than_or_equal",
}


class UndefinedCast(ValueError):
    pass


def parsed_value(value, source_type, target_type):
    if target_type == "string":
        if source_type == "string" and isinstance(value, str):
            return value
        raise UndefinedCast("No string cross-cast in this limited fixture oracle")

    if target_type == "integer":
        if type(value) is int and source_type == "integer":
            return value
        if source_type == "string" and type(value) is str:
            if not re.fullmatch(r"[+-]?[0-9]+", value):
                raise UndefinedCast("Invalid integer lexical content")
            return int(value, 10)
        raise UndefinedCast("Unproven cast to integer")

    if target_type == "boolean":
        if source_type == "boolean" and type(value) is bool:
            return value
        raise UndefinedCast("No Boolean cross-cast in this limited oracle")

    if target_type == "version":
        if source_type != "version" or type(value) is not str:
            raise UndefinedCast("Unproven cast to version")
        # ONLY dotted-numeric version subset, not all valid OVAL versions.
        if not re.fullmatch(r"[0-9]+(?:\.[0-9]+)*", value):
            raise UndefinedCast("Not in proven dotted version subset")
        return tuple(int(i) for i in value.split("."))

    if target_type in {"ipv4", "ipv6"}:
        if source_type != target_type or type(value) is not str:
            raise UndefinedCast("Unproven IP cast")
        try:
            network = ip_network(value, strict=False)
            if network.version != (4 if target_type == "ipv4" else 6):
                raise UndefinedCast("Wrong IP family")
            return network
        except ValueError as exc:
            raise UndefinedCast("Invalid IP prefix/address") from exc

    raise UndefinedCast(f"Unsupported evaluator type: {target_type}")


def compare_ordered(actual, expected, operation):
    if operation == "equals":
        return actual == expected
    if operation == "not_equal":
        return actual != expected
    if operation == "greater_than":
        return actual > expected
    if operation == "greater_than_or_equal":
        return actual >= expected
    if operation == "less_than":
        return actual < expected
    if operation == "less_than_or_equal":
        return actual <= expected
    raise UndefinedCast(f"Unsupported operator {operation}")


def evaluate_limited(observed, comparison):
    """Return 'true', 'false', or 'error' for explicitly supported cases."""
    datatype = comparison["datatype"]
    operation = comparison["operation"]
    try:
        actual = parsed_value(observed["value"], observed["datatype"], datatype)
        expected = parsed_value(comparison["value"], datatype, datatype)
        if datatype == "version":
            a, b = list(actual), list(expected)
            length = max(len(a), len(b))
            actual = tuple(a + [0] * (length - len(a)))
            expected = tuple(b + [0] * (length - len(b)))
        if datatype in {"ipv4", "ipv6"}:
            if operation == "subset_of":
                return "true" if actual.subnet_of(expected) else "false"
            if operation == "superset_of":
                return "true" if actual.supernet_of(expected) else "false"
            if operation in RELATIONAL and actual.prefixlen != expected.prefixlen:
                raise UndefinedCast("OVAL requires error on unequal prefixes")
            actual = (int(actual.network_address), actual.prefixlen)
            expected = (int(expected.network_address), expected.prefixlen)
        result = compare_ordered(actual, expected, operation)
        return "true" if result else "false"
    except (ValueError, TypeError, OverflowError, KeyError, UndefinedCast):
        return "error"


class IndependentlyExpectedOVALComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        obj = json.loads(CASES.read_text(encoding="utf-8"))
        cls.cases = obj["cases"]

    def test_independent_expected_outcomes_and_typed_operator_equivalence(self):
        self.assertEqual(len(self.cases), 13)
        ids = [case["id"] for case in self.cases]
        self.assertEqual(len(ids), len(set(ids)))
        for case in self.cases:
            with self.subTest(case=case["id"]):
                canonical = case["comparison"]
                authored = to_authoring(canonical, "typed-operators")
                self.assertNotIn("compare_as", authored)
                self.assertNotIn("datatype", authored)
                restored = to_canonical(authored)
                self.assertEqual(restored, canonical)
                # Expected outcomes were authored in fixture JSON, not derived
                # from the interpreter or codec under test.
                self.assertEqual(
                    evaluate_limited(case["observed"], canonical),
                    case["expected"],
                )
                self.assertEqual(
                    evaluate_limited(case["observed"], restored),
                    case["expected"],
                )

    def test_source_meaning_does_not_depend_on_observation_datatype(self):
        text_comparison = {
            "value": "01", "operation": "equals", "datatype": "string"
        }
        numeric_comparison = {
            "value": 1, "operation": "equals", "datatype": "integer"
        }
        text_observed = {"datatype": "string", "value": "01"}
        self.assertEqual(evaluate_limited(text_observed, text_comparison), "true")
        self.assertEqual(evaluate_limited(text_observed, numeric_comparison), "true")
        self.assertEqual(
            evaluate_limited(
                {"datatype": "string", "value": "abc"}, numeric_comparison
            ), "error"
        )

    def test_rare_comparators_held_for_real_differential_validation(self):
        # Deliberate gate: syntactic round-trip exists for these source types,
        # but it is NOT evidence of RPM/Debian, arbitrary OVAL version,
        # IOS/fileset or floating-point runtime comparison parity.
        specialized = {
            "rpm_evr", "debian_evr", "binary", "float",
            "ios_version", "fileset_revision",
        }
        self.assertTrue(specialized.isdisjoint({
            case["comparison"]["datatype"] for case in self.cases
        }))


if __name__ == "__main__":
    unittest.main()
