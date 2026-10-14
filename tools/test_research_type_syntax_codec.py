#!/usr/bin/env python3
"""Independent typed-canonical expectations and fail-closed tests (#200).

This tests syntax reversibility. Scanner-runtime outcomes from OVAL 5.12.3
remain separate conformance obligations; this suite does not simulate them.
"""
import unittest

from research_type_syntax_codec import (
    DATATYPES, TYPE_OPERATIONS, STRATEGIES, TypeSyntaxError,
    inferred_scalar_type, to_authoring, to_canonical,
)


class CodecTests(unittest.TestCase):
    def test_ordinary_scalars_and_lexical_strings(self):
        cases = [
            ({"value": "01", "operation": "equals", "datatype": "string"},
             {"value": "01", "operation": "equals"}),
            ({"value": "True", "operation": "equals", "datatype": "string"},
             {"value": "True", "operation": "equals"}),
            ({"value": 1, "operation": "equals", "datatype": "integer"},
             {"value": 1, "operation": "equals"}),
            ({"value": True, "operation": "equals", "datatype": "boolean"},
             {"value": True, "operation": "equals"}),
            ({"value": False, "operation": "not_equal", "datatype": "boolean"},
             {"value": False, "operation": "not_equal"}),
            ({"value": 1.5, "operation": "greater_than", "datatype": "float"},
             {"value": 1.5, "operation": "greater_than"}),
            ({"value": 4096, "operation": "bitwise_and", "datatype": "integer"},
             {"value": 4096, "operation": "bitwise_and"}),
        ]
        for original, authored in cases:
            with self.subTest(original=original):
                self.assertEqual(to_authoring(original), authored)
                self.assertEqual(to_canonical(authored), original)

    def test_versions_equality_and_compare_as_alternative(self):
        canonical = {"value": "1.0.0", "operation": "equals", "datatype": "version"}
        self.assertEqual(
            to_authoring(canonical, "hybrid"),
            {"value": "1.0.0", "operation": "version_equals"},
        )
        self.assertEqual(
            to_authoring(canonical, "compare-as"),
            {"value": "1.0.0", "operation": "equals", "compare_as": "version"},
        )
        self.assertEqual(
            to_canonical({"value": "1.0.0", "operation": "version_equals"}),
            canonical,
        )

    def test_source_comparison_type_not_runtime_item_type(self):
        # A collected Registry text "01" vs typed integer 1 is still
        # an integer State comparison; no Item type inference is permitted.
        canonical = {"field": "value", "value": 1,
                     "operation": "equals", "datatype": "integer"}
        authored = {"field": "value", "value": 1, "operation": "equals"}
        self.assertEqual(to_canonical(authored), canonical)
        self.assertEqual(to_authoring(canonical), authored)
        self.assertEqual(inferred_scalar_type("01"), "string")
        self.assertEqual(inferred_scalar_type(1), "integer")
        self.assertEqual(inferred_scalar_type(True), "boolean")
        self.assertEqual(inferred_scalar_type("True"), "string")

    def test_float_expected_with_integer_literal_is_not_integer(self):
        source = {"value": 1, "operation": "equals", "datatype": "float"}
        compact = {"value": 1, "operation": "equals", "compare_as": "float"}
        self.assertEqual(to_authoring(source), compact)
        self.assertEqual(to_canonical(compact), source)

    def test_special_datatype_families_remain_distinct(self):
        examples = [
            ("version", "1.0", "greater_than"),
            ("rpm_evr", "1:2.0-1", "greater_than"),
            ("debian_evr", "1.0~rc1", "less_than"),
            ("ipv4", "192.0.2.0/24", "subset_of"),
            ("ipv6", "2001:db8::/64", "superset_of"),
            ("binary", "0a0b", "equals"),
            ("fileset_revision", "1.2.3.4", "equals"),
            ("ios_version", "12.2(3)T", "greater_than"),
        ]
        for datatype, value, operation in examples:
            original = {"value": value, "operation": operation,
                        "datatype": datatype}
            for strategy in STRATEGIES:
                with self.subTest(datatype=datatype, strategy=strategy):
                    self.assertEqual(
                        to_canonical(to_authoring(original, strategy)), original,
                    )

    def test_all_matrix_combinations_reversible(self):
        values = {
            "string": "x", "boolean": True, "integer": 1, "float": 1.25,
            "binary": "0aff", "version": "1.0",
            "ipv4": "192.0.2.0/24", "ipv6": "2001:db8::/64",
            "rpm_evr": "1:2.0-1", "debian_evr": "1.0~rc1",
            "fileset_revision": "1.2.3.4", "ios_version": "12.2(3)T",
        }
        self.assertEqual(set(TYPE_OPERATIONS), DATATYPES)
        for datatype, operations in TYPE_OPERATIONS.items():
            if datatype == "record":
                self.assertEqual(operations, {"equals"})
                continue   # record children are intentionally held explicit
            for operation in operations:
                original = {"value": values[datatype], "operation": operation,
                            "datatype": datatype}
                for strategy in STRATEGIES:
                    with self.subTest(datatype=datatype, operation=operation,
                                      strategy=strategy):
                        self.assertEqual(
                            to_canonical(to_authoring(original, strategy)),
                            original,
                        )

    def test_dynamic_arrays_record_and_variable_contracts_remain_typed(self):
        canonical = {"assessment": {
            "variables": {"a-variable": {"datatype": "string",
                                         "expression": {"concat": ["a", "b"]}},
                          "b-variable": {"datatype": "integer", "value": 1}},
            "inputs": {"approved": {"datatype": "integer", "required": True}},
            "checks": [
                {"value": {"variable": "a-variable"},
                 "operation": "equals", "datatype": "string"},
                {"value": [1, 2], "operation": "equals",
                 "datatype": "integer", "value_match": "all"},
                {"value": {"record": {"name": "x"}}, "operation": "equals",
                 "datatype": "record"},
            ],
        }}
        self.assertEqual(to_authoring(canonical), canonical)
        self.assertEqual(to_canonical(canonical), canonical)

    def test_invalid_source_types_and_operations_rejected(self):
        bad = [
            {"value": True, "operation": "greater_than", "datatype": "boolean"},
            {"value": "x", "operation": "bitwise_and", "datatype": "string"},
            {"value": "1", "operation": "equals", "datatype": "integer"},
            {"value": True, "operation": "equals", "datatype": "integer"},
            {"value": "x", "operation": "equals", "datatype": "float"},
            {"value": "x", "operation": "equals", "datatype": "unknown"},
        ]
        for source in bad:
            with self.subTest(source=source):
                with self.assertRaises(TypeSyntaxError):
                    to_authoring(source)

    def test_unknown_ambiguous_and_untyped_refs_fail_closed(self):
        bad = [
            {"value": "1", "operation": "equals",
             "datatype": "string", "compare_as": "version"},
            {"value": "1", "operation": "equals", "compare_as": "unknown"},
            {"value": [1, 2], "operation": "equals", "compare_as": "integer"},
            {"value": {"variable": "x"}, "operation": "equals"},
            {"value": [1], "operation": "equals"},
            {"value": "x", "operation": "version_invalid"},
            {"value": 1, "operation": "rpm_evr_equals"},
        ]
        for source in bad:
            with self.subTest(source=source):
                with self.assertRaises(TypeSyntaxError):
                    to_canonical(source)

    def test_nonfinite_oval_float_lexical_form_is_explicitly_not_supported(self):
        for value in ("INF", "-INF", "NaN"):
            with self.subTest(value=value):
                with self.assertRaisesRegex(
                    TypeSyntaxError, "special float representation unresolved"
                ):
                    to_authoring(
                        {"value": value, "operation": "equals",
                         "datatype": "float"}
                    )


if __name__ == "__main__":
    unittest.main()
