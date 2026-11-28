"""Verify the native function examples against independent fixture calculations."""
from copy import deepcopy
from itertools import product
from math import prod
import re
import unittest

from conformance.tools.runner import CONFORMANCE, load, schema_validator
from conformance.tools.semantic import validate

SUITE = CONFORMANCE / "function-boundaries"


def expected_values(expression, resolved):
    """Oracle for the complete, known inputs used in these fixtures."""
    match expression:
        case {"literal": list(values)}:
            return values
        case {"literal": scalar}:
            return [scalar]
        case {"variable": identifier}:
            return resolved[identifier]
        case {"arithmetic": {"arithmetic_operation": "multiply", "values": operands}}:
            return [prod(values) for values in product(*(expected_values(arg, resolved) for arg in operands))]
        case {"unique": list(operands)}:
            flattened = (value for arg in operands for value in expected_values(arg, resolved))
            return list(dict.fromkeys(flattened))
        case {"split": {"delimiter": delimiter, "value": operand}}:
            return [part for text in expected_values(operand, resolved) for part in text.split(delimiter)]
        case {"concat": operands}:
            return ["".join(parts) for parts in product(*(expected_values(arg, resolved) for arg in operands))]
        case {"substring": {"substring_start": start, "substring_length": length, "value": operand}}:
            values = expected_values(operand, resolved)
            if any(start > len(text) for text in values):
                raise ValueError("substring start exceeds source string")
            index = max(0, start - 1)
            return [text[index:] if length < 0 else text[index:index + length] for text in values]
        case {"regex_capture": {"pattern": pattern, "value": operand}}:
            matches = (re.search(pattern, text) for text in expected_values(operand, resolved))
            return [match.groups()[0] if match and match.groups() else "" for match in matches]
        case {"merge": {"delimiter": delimiter, "sort": "document", "order": "ascending", "values": operand}}:
            return [delimiter.join(expected_values(operand, resolved))]
        case {"count": operand}:
            return [len(expected_values(operand, resolved))]
    raise ValueError(f"Unexpected fixture expression {expression!r}")


class FunctionBoundaryCases(unittest.TestCase):
    def setUp(self):
        self.manifest = load(SUITE / "expected.json")
        self.source = load(SUITE / self.manifest["source"])
        self.schema = schema_validator("assessment.schema.json")

    def test_ordered_populations_and_authored_assertions(self):
        self.schema.validate(self.source)
        self.assertEqual(validate(self.source), [])
        self.assertEqual(self.manifest["schema_commit"], load(CONFORMANCE / "manifest.json")["schema_commit"])
        oval_pin = load(CONFORMANCE / "oval-source-coverage.json")["pins"]["oval_5_12_3"]
        self.assertEqual(self.manifest["oval_schema_commit"], oval_pin)
        assessment = self.source["assessment"]
        resolved = {}
        for key, variable in assessment["variables"].items():
            resolved[key] = expected_values(variable["expression"], resolved)

        populations = self.manifest["populations"]
        self.assertTrue(populations.keys() <= resolved.keys())
        for key, expected in populations.items():
            with self.subTest(variable=key):
                self.assertEqual(resolved[key], expected["values"])
                datatype = {"integer": int, "string": str}[expected["datatype"]]
                self.assertTrue(all(type(value) is datatype for value in resolved[key]))

        self.assertCountEqual(
            [leaf["test"] for leaf in assessment["evaluate"]["and"]], assessment["tests"].keys(),
        )
        for key, test in assessment["tests"].items():
            with self.subTest(test=key):
                self.assertEqual(test["capability"], "variable.value")
                requirement = test["require"]
                self.assertEqual(requirement["item_requirement"],
                                 {"items_found": "exactly_one", "items_satisfying": "every"})
                field = requirement["fields"]["value"]
                observed = resolved[test["variable"]]
                operand = field["equals"]
                requirements = requirement["field_requirement"]
                self.assertEqual(requirements["values_matching"], "every")
                if isinstance(operand, list):
                    self.assertEqual(field["value_match"], "exactly_one")
                    self.assertEqual(requirements["values_found"], "one_or_more")
                    self.assertTrue(observed)
                    self.assertTrue(all(operand.count(value) == 1 for value in observed))
                else:
                    self.assertEqual(requirements["values_found"], "exactly_one")
                    self.assertEqual(observed, [operand])

    def test_substring_range_error_stays_at_expression_scope(self):
        expected = self.manifest["exceptional_expression"]
        doc = load(SUITE / expected["source"])
        self.schema.validate(doc)
        self.assertEqual(validate(doc), [])
        assessment = doc["assessment"]
        test = assessment["tests"][assessment["evaluate"]["test"]]
        self.assertEqual(test["variable"], expected["variable"])
        expression = assessment["variables"][test["variable"]]["expression"]
        self.assertEqual(expected["status"], "error")
        self.assertEqual(expected["assessment_outcome"], "held")
        with self.assertRaisesRegex(ValueError, "substring start exceeds source string"):
            expected_values(expression, {})

    def test_invalid_function_authoring_and_order_sensitivity(self):
        for control in self.manifest["authoring_controls"]:
            with self.subTest(control=control):
                mutant = deepcopy(self.source)
                expression = mutant["assessment"]["variables"][control["variable"]]["expression"]
                expression[control["operation"]][control["parameter"]] = control["replacement"]
                errors = list(self.schema.iter_errors(mutant))
                self.assertTrue(errors)
                self.assertTrue(any(control["variable"] in error.absolute_path for error in errors))

        expectation = self.manifest["populations"]["split-parts-variable"]["values"]
        mutation = self.source["assessment"]["variables"]["split-parts-variable"]["expression"]
        mutation["split"]["value"]["literal"].reverse()
        changed = expected_values(mutation, {})
        self.assertCountEqual(changed, expectation)
        self.assertNotEqual(changed, expectation)
