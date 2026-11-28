"""Validate the native typed Input contract over deterministic invocations."""
from copy import deepcopy
import unittest

from conformance.tools.runner import CONFORMANCE, load, schema_validator
from conformance.tools.semantic import validate

SUITE = CONFORMANCE / "input-policy"


def invocation(assessment, bindings):
    """Resolve the one guarded numeric Input used by the Assessment."""
    evaluate = assessment["evaluate"]
    input_id = evaluate["if"]["input_provided"]
    declared = assessment["inputs"][input_id]
    if input_id not in bindings:
        if declared["required"]:
            return {"admission": "required_missing"}
        return {"admission": "accepted", "assessment_outcome": "not_evaluated", "executed_tests": []}
    values = bindings[input_id]
    limits = {"exactly_one": (1, 1), "zero_or_one": (0, 1),
              "one_or_more": (1, None), "zero_or_more": (0, None)}
    minimum, maximum = limits[declared["cardinality"]]
    if len(values) < minimum or (maximum is not None and len(values) > maximum):
        return {"admission": "cardinality_rejected"}
    if any(type(value) is not int for value in values):
        return {"admission": "datatype_rejected"}
    constraints = declared["constraints"]
    predicates = constraints["predicate"]["and"]
    lower = predicates[0]["greater_than_or_equal"]
    upper = predicates[1]["less_than_or_equal"]
    if any(value not in constraints["allowed"] and not lower <= value <= upper for value in values):
        return {"admission": "constraint_rejected"}
    test_id = evaluate["then"]["test"]
    test = assessment["tests"][test_id]
    operand = test["require"]["fields"]["value"]["equals"]
    return {
        "admission": "accepted",
        "assessment_outcome": str(any(value == operand for value in values)).lower(),
        "executed_tests": [test_id],
    }


class InputPolicyCases(unittest.TestCase):
    def setUp(self):
        self.manifest = load(SUITE / "expected.json")
        self.source = load(SUITE / self.manifest["source"])
        self.schema = schema_validator("assessment.schema.json")

    def test_cardinality_constraints_and_guard(self):
        self.schema.validate(self.source)
        self.assertEqual(validate(self.source), [])
        self.assertEqual(self.manifest["schema_commit"], load(CONFORMANCE / "manifest.json")["schema_commit"])
        assessment = self.source["assessment"]
        evaluate = assessment["evaluate"]
        test = assessment["tests"][evaluate["then"]["test"]]
        input_id = evaluate["if"]["input_provided"]
        self.assertEqual(assessment["inputs"][input_id]["datatype"], "integer")
        self.assertEqual(assessment["variables"][test["variable"]]["expression"], {"input": input_id})
        self.assertEqual(set(evaluate["else"]), {"not_evaluated"})
        self.assertEqual(test["capability"], "variable.value")
        self.assertEqual(test["require"]["item_requirement"], {
            "items_found": "exactly_one", "items_satisfying": "every",
        })
        self.assertEqual(test["require"]["field_requirement"], {
            "values_found": "one_or_more", "values_matching": "one_or_more",
        })
        for name, variant in self.manifest["variants"].items():
            with self.subTest(variant=name):
                expected = {key: value for key, value in variant.items() if key != "bindings"}
                self.assertEqual(invocation(assessment, variant["bindings"]), expected)

    def test_predicate_authoring_limits(self):
        controls = self.manifest["predicate_limits"]
        string_source = load(SUITE / controls["string_source"])
        self.schema.validate(string_source)
        self.assertEqual(validate(string_source), [])
        for operator in controls["logical_operators"]:
            for size, valid in ((0, False), (controls["maximum_branches"], True),
                                (controls["maximum_branches"] + 1, False)):
                with self.subTest(operator=operator, size=size):
                    doc = deepcopy(self.source)
                    constraints = doc["assessment"]["inputs"]["approved-values-input"]["constraints"]
                    constraints["predicate"] = {operator: [{"equals": n} for n in range(size)]}
                    self.assertEqual(self.schema.is_valid(doc), valid)
        for size, valid in ((controls["maximum_literal_characters"], True),
                            (controls["maximum_literal_characters"] + 1, False)):
            for operation in controls["string_operations"]:
                with self.subTest(operation=operation, size=size):
                    doc = deepcopy(string_source)
                    constraints = doc["assessment"]["inputs"]["approved-label-input"]["constraints"]
                    constraints["predicate"] = {operation: "é" * size}
                    self.assertEqual(self.schema.is_valid(doc), valid)


    def test_nested_resource_bounds_are_independent_of_branch_width(self):
        # Each logical node is counted once, including the root and each leaf.
        def measure(expression):
            operator, value = next(iter(expression.items()))
            if operator == "equals":
                return 1, 1
            children = [measure(child) for child in value]
            return 1 + sum(nodes for nodes, _ in children), 1 + max(depth for _, depth in children)

        controls = self.manifest["predicate_limits"]["resource_bounds"]
        language = schema_validator("assessment-language.schema.json")
        value_expression = language.schema["$defs"]["value_constraint_expression"]
        limits = value_expression["x-scap-ng-resource-limits"]
        self.assertEqual(limits["max_expression_depth"], controls["maximum_depth"])
        self.assertEqual(limits["max_expression_nodes"], controls["maximum_nodes"])
        for name, case in controls["cases"].items():
            with self.subTest(case=name):
                if "unary_depth" in case:
                    expression = {"equals": 99}
                    for _ in range(case["unary_depth"] - 1):
                        expression = {"and": [expression]}
                else:
                    expression = {"or": [{"and": [{"equals": n} for n in range(size)]}
                                         for size in case["group_sizes"]]}
                doc = deepcopy(self.source)
                constraint = doc["assessment"]["inputs"]["approved-values-input"]["constraints"]
                constraint["predicate"] = expression
                self.schema.validate(doc)
                nodes, depth = measure(expression)
                self.assertEqual((nodes, depth), (case["nodes"], case["depth"]))
                rejected = nodes > controls["maximum_nodes"] or depth > controls["maximum_depth"]
                self.assertEqual(case["result"], "resource_rejected" if rejected else "admitted")


class PolicySelectionCases(unittest.TestCase):
    def setUp(self):
        entry = load(SUITE / "expected.json")
        self.expected = load(SUITE / entry["selection_expectations"])
        self.benchmark_doc = load(CONFORMANCE / self.expected["benchmark"])
        self.tailoring_doc = load(CONFORMANCE / self.expected["tailoring"])

    def test_default_profile_and_tailoring_apply_to_rule_selection(self):
        benchmark_schema = schema_validator("benchmark.schema.json")
        tailoring_schema = schema_validator("tailoring.schema.json")
        tailoring_schema.validate(self.tailoring_doc)
        tailoring = self.tailoring_doc["tailoring"]
        for name, case in self.expected["policy_variants"].items():
            with self.subTest(case=name):
                doc = deepcopy(self.benchmark_doc)
                benchmark = doc["benchmark"]
                if name == "default-disabled":
                    benchmark["default_selection"] = False
                benchmark_schema.validate(doc)
                self.assertIs(benchmark["default_selection"], case["default_selection"])
                ordered_ids = benchmark["rules"]
                all_rules = set(ordered_ids)
                if case["profile"] is None:
                    selected = all_rules.copy() if benchmark["default_selection"] else set()
                else:
                    profile, = [p for p in benchmark["profiles"] if p["id"] == case["profile"]]
                    selected = all_rules - set(profile["disabled_rules"])
                if case["apply_tailoring"]:
                    self.assertEqual(tailoring["benchmark"], {
                        "id": benchmark["id"], "version": benchmark["version"]["value"],
                    })
                    self.assertEqual(tailoring["profile"], case["profile"])
                    self.assertIsNone(tailoring["extends"])
                    self.assertEqual(tailoring["group_operations"], [])
                    self.assertEqual(tailoring["check_selectors"], {})
                    enabled = set(tailoring["enabled_rules"])
                    disabled = set(tailoring["disabled_rules"])
                    self.assertFalse(enabled & disabled)
                    self.assertTrue((enabled | disabled) <= all_rules)
                    selected = (selected | enabled) - disabled
                self.assertEqual([rule for rule in ordered_ids if rule in selected], case["selected"])

    def test_profile_rejects_tailoring_and_inheritance_members(self):
        schema = schema_validator("benchmark.schema.json")
        for property_name, replacement in self.expected["schema_rejected_profile_controls"].items():
            with self.subTest(property=property_name):
                doc = deepcopy(self.benchmark_doc)
                doc["benchmark"]["profiles"][1][property_name] = replacement
                errors = list(schema.iter_errors(doc))
                self.assertTrue(errors)
                self.assertTrue(any("profiles" in error.absolute_path for error in errors))
