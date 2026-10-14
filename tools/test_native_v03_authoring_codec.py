#!/usr/bin/env python3
"""0.3 compact authoring acceptance tests; source expands before typed checks."""
import copy
import unittest

from native_v03_authoring_codec import canonicalize_assessment_document


def wrap(comparison):
    return {
        "assessment": {
            "id": "test.assessment",
            "specification": {"id": "scap-ng.pre-alpha.assessment", "version": "0.3.0"},
            "tests": {
                "example-test": {
                    "states": [{
                        "field": "value",
                        "value": comparison["value"],
                        "operation": comparison["operation"],
                        **({"datatype": comparison["datatype"]}
                           if "datatype" in comparison else {}),
                        "match": "all",
                        "existence": "one_or_more",
                    }]
                }
            },
        }
    }


class NativeV03TypedAuthoringTests(unittest.TestCase):
    def test_typed_version_authored_to_canonical(self):
        src=wrap({"value":"2.4", "operation":"version_greater_than_or_equal"})
        original=copy.deepcopy(src)
        canonical=canonicalize_assessment_document(src)
        node=canonical["assessment"]["tests"]["example-test"]["states"][0]
        self.assertEqual(node["datatype"],"version")
        self.assertEqual(node["operation"],"greater_than_or_equal")
        self.assertEqual(src,original)

    def test_scalar_and_string_must_remain_distinct(self):
        for value,kind in ((True,"boolean"),(1,"integer"),(1.5,"float"),("01","string"),("True","string")):
            with self.subTest(value=value):
                src=wrap({"value":value,"operation":"equals"})
                canonical=canonicalize_assessment_document(src)
                self.assertEqual(canonical["assessment"]["tests"]["example-test"]["states"][0]["datatype"],kind)

    def test_error_invalid_dynamic_without_explicit_datatype(self):
        for value in ({"variable":"missing-variable"},[1,2],None):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    canonicalize_assessment_document(wrap({"value":value,"operation":"equals"}))

    def test_valid_explicit_dynamic_preserved(self):
        src=wrap({"value":{"variable":"some-variable"},
                  "datatype":"integer","operation":"equals"})
        self.assertEqual(canonicalize_assessment_document(src),src)

    def test_reject_compare_as_everywhere(self):
        src=wrap({"value":"1.2","operation":"greater_than"})
        src["assessment"]["tests"]["example-test"]["states"][0]["compare_as"]="version"
        with self.assertRaisesRegex(ValueError,"compare_as"):
            canonicalize_assessment_document(src)

    def test_reject_invalid_special_type_operator(self):
        for value, operation in (("1.2","rpm_evr_pattern_match"), (7,"version_equals"), ("1","unknown_eq")):
            with self.subTest(operation=operation):
                with self.assertRaises(ValueError):
                    canonicalize_assessment_document(wrap({"value":value,"operation":operation}))

    def test_current_v03_json_schema_accepts_compact_typed_comparisons(self):
        import json
        from pathlib import Path
        from jsonschema import Draft202012Validator
        source = Path(__file__).resolve().parents[1] / "schema/v0.3.0/capability-common.schema.json"
        definitions = json.loads(source.read_text())["$defs"]
        for section in ("object_entity_base", "state_entity_base", "scalar_value_predicate"):
            validator = Draft202012Validator({
                "$defs": definitions, "$ref": "#/$defs/" + section
            })
            base = {"value": "1.2", "operation": "version_equals"}
            if section != "object_entity_base":
                base.update(match="all", existence="one_or_more")
            self.assertEqual(list(validator.iter_errors(base)), [], section)
            self.assertEqual(list(validator.iter_errors({
                **base, "operation": "equals", "datatype": "version"
            })), [], section)
            self.assertTrue(list(validator.iter_errors({
                **base, "datatype": "version"
            })), "typed source with datatype should be rejected")
            self.assertTrue(list(validator.iter_errors({
                **base, "value": {"variable": "some-variable"}, "operation": "equals"
            })), "bare dynamic reference cannot silently infer datatype")
            self.assertTrue(list(validator.iter_errors({
                **base, "value": 8, "operation": "version_equals"
            })), "version typed op requires string literal")

    def test_canonical_03_backward_compatible_and_02_unmodified(self):
        original=wrap({"value":"1.2","datatype":"version","operation":"equals"})
        self.assertEqual(canonicalize_assessment_document(original),original)
        legacy=copy.deepcopy(original)
        legacy["assessment"]["specification"]["version"]="0.2.0"
        self.assertEqual(canonicalize_assessment_document(legacy),legacy)


if __name__=="__main__":
    unittest.main()
