"""Apply the native exact-equality contract to literal boundary cases."""
import unittest

from conformance.tools.runner import CONFORMANCE, load, schema_validator
from conformance.tools.semantic import validate

SUITE = CONFORMANCE / "exact-equality"


class ExactEqualityCases(unittest.TestCase):
    def test_exact_equality_uses_uncoerced_scalars(self):
        manifest = load(SUITE / "expected.json")
        source = load(SUITE / manifest["source"])
        schema_validator("assessment.schema.json").validate(source)
        self.assertEqual(validate(source), [])
        assessment = source["assessment"]
        self.assertEqual(assessment["tests"].keys(), manifest["test_outcomes"].keys())
        outcomes = {}
        for key, test in assessment["tests"].items():
            with self.subTest(test=key):
                self.assertEqual(test["capability"], "variable.value")
                expression = assessment["variables"][test["variable"]]["expression"]
                observed = expression["literal"]["value"]
                requirement = test["require"]
                self.assertEqual(requirement["item_requirement"],
                                 {"items_found": "exactly_one", "items_satisfying": "every"})
                self.assertEqual(requirement["field_requirement"],
                                 {"values_found": "exactly_one", "values_matching": "every"})
                operand = requirement["fields"]["value"]["equals"]
                if expression["literal"]["datatype"] == "integer":
                    self.assertIs(type(operand), int)
                    self.assertIs(type(observed), int)
                else:
                    self.assertEqual(expression["literal"]["datatype"], "string")
                    self.assertIs(type(operand), str)
                    self.assertIs(type(observed), str)
                outcomes[key] = observed == operand
                self.assertIs(outcomes[key], manifest["test_outcomes"][key])

        trace = assessment["evaluate"]["and"]
        named = [(term.get("not", term)["test"], "not" in term) for term in trace]
        self.assertCountEqual([key for key, _ in named], outcomes)
        self.assertIs(all(outcomes[key] != negate for key, negate in named), manifest["assessment_outcome"])

    def test_boundaries_distinguish_implicit_coercions(self):
        source = load(SUITE / "exact-equality.assessment.yaml")["assessment"]
        variables = source["variables"]
        tests = source["tests"]
        self.assertEqual(float(variables["large-adjacent-variable"]["expression"]["literal"]["value"]),
                         float(tests["large-adjacent-test"]["require"]["fields"]["value"]["equals"]))
        self.assertEqual(variables["empty-space-variable"]["expression"]["literal"]["value"],
                         tests["empty-space-test"]["require"]["fields"]["value"]["equals"].strip())
