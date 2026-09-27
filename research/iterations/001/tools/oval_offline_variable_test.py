#!/usr/bin/env python3
"""Offline evaluator for target-independent OVAL variable_test content.

This intentionally supports only semantics that can be evaluated without a
platform collector. It is designed first for the OVAL Community Self-Assertion
agnostic corpus, where variable_object/variable_test content simulates system
data. Unsupported constructs return not_evaluated rather than being guessed.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("oval_ir", HERE / "oval_semantic_ir.py")
oval_ir = importlib.util.module_from_spec(spec)
spec.loader.exec_module(oval_ir)


def combine_check(check, values):
    values = list(values)
    if not values:
        return "false"
    if any(v not in {"true", "false"} for v in values):
        return oval_ir.oval_combine_results("AND", values)
    true_count = values.count("true")
    check = (check or "all").lower()
    if check == "all":
        return "true" if true_count == len(values) else "false"
    if check == "at least one":
        return "true" if true_count >= 1 else "false"
    if check == "none satisfy":
        return "true" if true_count == 0 else "false"
    if check == "only one":
        return "true" if true_count == 1 else "false"
    return "not_evaluated"


def existence_result(check_existence, count):
    check = (check_existence or "at_least_one_exists").lower()
    if check == "at_least_one_exists":
        return "true" if count >= 1 else "false"
    if check == "none_exist":
        return "true" if count == 0 else "false"
    if check == "only_one_exists":
        return "true" if count == 1 else "false"
    if check == "any_exist":
        # OVAL any_exist is true whether zero, one, or many exist, provided
        # collection itself did not error. The Self-Assertion content explicitly
        # exercises the zero-item case.
        return "true"
    if check == "all_exist":
        # For an exactly collected synthetic object, every returned item exists.
        # Empty collection does not satisfy all_exist.
        return "true" if count >= 1 else "false"
    return "not_evaluated"


def as_bool(value):
    s = str(value).strip().lower()
    if s in {"true", "1"}:
        return True
    if s in {"false", "0"}:
        return False
    raise ValueError(value)


def version_parts(value):
    parts = re.split(r"[._+-]", str(value))
    out = []
    for part in parts:
        if part.isdigit():
            out.append((0, int(part)))
        else:
            out.append((1, part))
    return tuple(out)


def cast(value, datatype):
    dt = (datatype or "string").lower()
    if dt == "int":
        return int(str(value).strip())
    if dt == "float":
        return Decimal(str(value).strip())
    if dt == "boolean":
        return as_bool(value)
    if dt == "version":
        return version_parts(value)
    return str(value)


def compare(actual, expected, operation="equals", datatype="string"):
    op = (operation or "equals").lower()
    try:
        a = cast(actual, datatype)
        b = cast(expected, datatype)
    except (ValueError, InvalidOperation):
        return "error"

    if op == "equals":
        return "true" if a == b else "false"
    if op == "not equal":
        return "true" if a != b else "false"
    if op == "case insensitive equals":
        return "true" if str(actual).casefold() == str(expected).casefold() else "false"
    if op == "case insensitive not equal":
        return "true" if str(actual).casefold() != str(expected).casefold() else "false"
    if op == "greater than":
        return "true" if a > b else "false"
    if op == "greater than or equal":
        return "true" if a >= b else "false"
    if op == "less than":
        return "true" if a < b else "false"
    if op == "less than or equal":
        return "true" if a <= b else "false"
    if op == "pattern match":
        try:
            return "true" if re.search(str(expected), str(actual)) else "false"
        except re.error:
            return "error"
    if op == "bitwise and":
        try:
            return "true" if (int(a) & int(b)) == int(b) else "false"
        except Exception:
            return "error"
    if op == "bitwise or":
        try:
            return "true" if (int(a) | int(b)) == int(b) else "false"
        except Exception:
            return "error"
    if op in {"subset of", "superset of"}:
        # Supported later with datatype-specific set semantics.
        return "not_evaluated"
    return "not_evaluated"


def child_value(node):
    return node.get("value", "")


class OfflineEvaluator:
    def __init__(self, ir):
        self.ir = ir
        self.objects = {x["id"]: x for x in ir.get("objects", [])}
        self.states = {x["id"]: x for x in ir.get("states", [])}
        self.tests = {x["id"]: x for x in ir.get("tests", [])}
        self.definitions = {x["id"]: x for x in ir.get("definitions", [])}
        self.variables = ir.get("variable_resolution", {})
        self._object_stack = set()
        self._definition_stack = set()

    def object_items(self, object_ref):
        if object_ref in self._object_stack:
            return None
        obj = self.objects.get(object_ref)
        if not obj or obj.get("type") != "variable_object":
            return None
        self._object_stack.add(object_ref)
        try:
            sets = [x for x in obj.get("children", []) if x.get("kind") == "set"]
            if sets:
                if len(sets) != 1:
                    return None
                return self.set_items(sets[0])

            refs = [
                x.get("value")
                for x in obj.get("children", [])
                if x.get("kind") == "element" and x.get("name") == "var_ref"
            ]
            if len(refs) != 1 or not refs[0]:
                return None
            resolved = self.variables.get(refs[0], {})
            if resolved.get("status") != "exact_static":
                return None
            return [{"value": list(resolved.get("values", []))}]
        finally:
            self._object_stack.remove(object_ref)

    def set_items(self, node):
        operands = []
        filters = []
        for child in node.get("children", []):
            if child.get("kind") == "object_ref":
                items = self.object_items(child.get("object_ref"))
                if items is None:
                    return None
                operands.append(items)
            elif child.get("kind") == "set":
                items = self.set_items(child)
                if items is None:
                    return None
                operands.append(items)
            elif child.get("kind") == "filter":
                filters.append(child)

        if filters:
            # Exact state-backed filters are a later executor layer.
            return None
        if not operands:
            return None
        try:
            return oval_ir.oval_set_items(node.get("operator", "UNION"), operands)
        except ValueError:
            return None

    def expected_values(self, entity):
        attrs = entity.get("attributes", {})
        var_ref = attrs.get("var_ref")
        if var_ref:
            resolved = self.variables.get(var_ref, {})
            if resolved.get("status") != "exact_static":
                return None
            return list(resolved.get("values", []))
        return [child_value(entity)]

    def entity_result(self, actual_values, entity):
        attrs = entity.get("attributes", {})
        operation = attrs.get("operation", "equals")
        datatype = attrs.get("datatype", "string")
        expected = self.expected_values(entity)
        if expected is None:
            return "not_evaluated"

        var_check = attrs.get("var_check", "all")
        per_actual = []
        for actual in actual_values:
            against_variable = [
                compare(actual, target, operation, datatype)
                for target in expected
            ]
            per_actual.append(combine_check(var_check, against_variable))

        return combine_check(attrs.get("entity_check", "all"), per_actual)

    def state_result(self, item, state_ref):
        state = self.states.get(state_ref)
        if not state:
            return "not_evaluated"
        entity_results = []
        for entity in state.get("entities", []):
            if entity.get("kind") != "element":
                return "not_evaluated"
            name = entity.get("name")
            actual = item.get(name)
            if actual is None:
                return "false"
            actual_values = actual if isinstance(actual, list) else [actual]
            entity_results.append(self.entity_result(actual_values, entity))
        if not entity_results:
            return "true"
        return oval_ir.oval_combine_results(state.get("operator", "AND"), entity_results)

    def test_result(self, test_ref):
        test = self.tests.get(test_ref)
        if not test:
            return "not_evaluated"
        if test.get("type") == "unknown_test":
            return "unknown"
        if test.get("type") != "variable_test":
            return "not_evaluated"
        if len(test.get("objects", [])) != 1:
            return "not_evaluated"

        items = self.object_items(test["objects"][0].get("object_ref"))
        if items is None:
            return "not_evaluated"

        existence = existence_result(test.get("check_existence"), len(items))
        if existence != "true":
            return existence

        state_refs = [x.get("state_ref") for x in test.get("states", [])]
        if not state_refs:
            return "true"

        item_results = []
        for item in items:
            per_state = [self.state_result(item, ref) for ref in state_refs]
            item_results.append(
                oval_ir.oval_combine_results(test.get("state_operator", "AND"), per_state)
            )
        return combine_check(test.get("check", "all"), item_results)

    def criteria_result(self, node):
        if node is None:
            return "not_evaluated"
        kind = node.get("kind")
        if kind == "test_ref":
            value = self.test_result(node.get("test_ref"))
        elif kind == "definition_ref":
            value = self.definition_result(node.get("definition_ref"))
        elif kind == "boolean":
            values = [self.criteria_result(x) for x in node.get("children", [])]
            if not values:
                return "not_evaluated"
            value = oval_ir.oval_combine_results(node.get("operator", "AND"), values)
        else:
            return "not_evaluated"
        return oval_ir.oval_negate_result(value) if node.get("negate") else value

    def definition_result(self, definition_ref):
        if definition_ref in self._definition_stack:
            return "error"
        definition = self.definitions.get(definition_ref)
        if not definition:
            return "not_evaluated"
        self._definition_stack.add(definition_ref)
        try:
            return self.criteria_result(definition.get("criteria"))
        finally:
            self._definition_stack.remove(definition_ref)


def evaluate_file(path):
    ir = oval_ir.parse(path)
    ev = OfflineEvaluator(ir)
    return {
        definition["id"]: ev.definition_result(definition["id"])
        for definition in ir.get("definitions", [])
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path)
    args = ap.parse_args()
    result = evaluate_file(args.input)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
