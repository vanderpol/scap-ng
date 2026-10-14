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
        # Ordinary scalar inference would incorrectly choose integer, so the
        # user-preferred syntax carries the needed distinction in the operator.
        compact = {"value": 1, "operation": "float_equals"}
        self.assertEqual(to_authoring(source), compact)
        self.assertEqual(to_canonical(compact), source)
        # Retained only to compare the rejected research alternative.
        old_alternative = {"value": 1, "operation": "equals", "compare_as": "float"}
        self.assertEqual(to_authoring(source, "compare-as"), old_alternative)
        self.assertEqual(to_canonical(old_alternative), source)

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


class ActualOVALMappingBoundaryTests(unittest.TestCase):
    """Exercise the repository's actual OVAL -> typed 0.3 predicate translator.

    Inputs are small OVAL-like entity XML fragments. This is not a test
    of full datastream parsing, Schematron, or host scan evaluation.
    """

    def source_predicate(self, xml):
        import xml.etree.ElementTree as ET
        from scap_upconvert_v003.native_capability_mapping import (
            _native_scalar_predicate,
        )
        entity = ET.fromstring(xml)
        payload = dict(entity.attrib)
        payload["value"] = entity.text or ""
        return _native_scalar_predicate(payload, {"specification_version": "0.3.0"})

    def test_source_lexical_type_and_operation_restore(self):
        cases = [
            (
                '<entity datatype="int" operation="greater than or equal">0010</entity>',
                {"value": 10, "datatype": "integer", "operation": "greater_than_or_equal",
                 "match": "all", "existence": "one_or_more"},
            ),
            (
                '<entity datatype="boolean" operation="equals">1</entity>',
                {"value": True, "datatype": "boolean", "operation": "equals",
                 "match": "all", "existence": "one_or_more"},
            ),
            (
                '<entity datatype="string" operation="equals">01</entity>',
                {"value": "01", "datatype": "string", "operation": "equals",
                 "match": "all", "existence": "one_or_more"},
            ),
            (
                '<entity datatype="version" operation="greater than or equal">2.9</entity>',
                {"value": "2.9", "datatype": "version",
                 "operation": "greater_than_or_equal",
                 "match": "all", "existence": "one_or_more"},
            ),
            (
                '<entity datatype="evr_string" operation="less than">1:2.0-1</entity>',
                {"value": "1:2.0-1", "datatype": "rpm_evr",
                 "operation": "less_than", "match": "all",
                 "existence": "one_or_more"},
            ),
            (
                '<entity datatype="ipv4_address" operation="subset of">192.0.2.0/24</entity>',
                {"value": "192.0.2.0/24", "datatype": "ipv4",
                 "operation": "subset_of", "match": "all",
                 "existence": "one_or_more"},
            ),
        ]
        for xml, expected in cases:
            with self.subTest(xml=xml):
                actual = self.source_predicate(xml)
                self.assertEqual(actual, expected)
                for strategy in STRATEGIES:
                    authored = to_authoring(actual, strategy)
                    self.assertEqual(to_canonical(authored), expected)

    def test_source_float_special_is_real_migration_representation_gap(self):
        # OVAL common datatype supports INF; legacy mapping currently creates
        # a nonfinite Python float. JSON-canonical SCAP-NG cannot store that
        # value as an ordinary number. Never claim a silent conversion.
        for lexical in ("INF", "-INF", "NaN"):
            with self.subTest(lexical=lexical):
                source = self.source_predicate(
                    f'<entity datatype="float" operation="equals">{lexical}</entity>'
                )
                self.assertEqual(source["datatype"], "float")
                with self.assertRaisesRegex(
                    TypeSyntaxError, "special float representation unresolved"
                ):
                    to_authoring(source)


if __name__ == "__main__":
    unittest.main()
