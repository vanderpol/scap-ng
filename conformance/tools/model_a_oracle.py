#!/usr/bin/env python3
"""Independent truth oracle for the approved complete-known-nonempty Model A.

This is intentionally narrower than RI execution. It implements only the
owner-approved integer/string equality domain from docs/contracts/0.4-evaluation.md:
one logical Variable source group, ordered duplicate-preserving values, explicit
value_match, values_matching, values_found, items_found, and items_satisfying.
Unknown/error/empty/incomplete status precedence is rejected as outside scope.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


SUPPORTED = (str, int)
CARDINALITIES = {"none", "exactly_one", "one_or_more", "every", "zero_or_more"}


def _values(literal: Any) -> list[Any]:
    if isinstance(literal, Mapping) and "datatype" in literal and "value" in literal:
        literal = literal["value"]
    if isinstance(literal, list):
        return list(literal)
    return [literal]


def _check_value(value: Any) -> None:
    if isinstance(value, bool) or not isinstance(value, SUPPORTED):
        raise ValueError("Model A oracle only accepts integer/string values")


def _cardinality(count: int, population: int, token: str) -> bool:
    if token not in CARDINALITIES:
        raise ValueError(f"unsupported cardinality: {token}")
    return {"none": count == 0, "exactly_one": count == 1, "one_or_more": count >= 1, "every": count == population, "zero_or_more": True}[token]


def _resolve(expression: Any, variables: dict[str, list[Any]]) -> list[Any]:
    if isinstance(expression, Mapping) and "variable" in expression:
        if expression["variable"] not in variables:
            raise ValueError("unresolved Variable reference")
        return list(variables[expression["variable"]])
    return _values(expression)


def evaluate(document: Mapping[str, Any]) -> dict[str, Any]:
    """Evaluate the single Model A Test and return independent observations."""
    body = document["assessment"]
    declarations = body.get("variables", {})
    variables: dict[str, list[Any]] = {}
    resolving: set[str] = set()

    def resolve_variable(name: str) -> list[Any]:
        if name in variables: return list(variables[name])
        if name in resolving: raise ValueError("cyclic Variable reference")
        declaration = declarations.get(name)
        if declaration is None: raise ValueError("unresolved Variable reference")
        resolving.add(name)
        if declaration.get("kind") == "constant":
            values = _values(declaration["expression"]["literal"])
        elif declaration.get("kind") == "local" and isinstance(declaration.get("expression"), Mapping) and "variable" in declaration["expression"]:
            values = resolve_variable(declaration["expression"]["variable"])
        else:
            raise ValueError("Model A oracle only accepts constant or direct local alias Variables")
        for value in values: _check_value(value)
        resolving.remove(name); variables[name] = list(values)
        return list(values)

    for name in declarations: resolve_variable(name)
    tests = body["tests"]
    if len(tests) != 1:
        raise ValueError("Model A oracle requires exactly one Test")
    test = next(iter(tests.values()))
    if test.get("capability") != "variable.value" or "variable" not in test:
        raise ValueError("Model A oracle requires variable.value Test")
    observed = variables.get(test["variable"])
    if observed is None or not observed:
        raise ValueError("Model A requires one complete known nonempty Variable")
    for value in observed: _check_value(value)
    require = test["require"]
    item_requirement = require["item_requirement"]
    items_found = 1
    fields = require.get("fields", {})
    if len(fields) != 1 or "value" not in fields:
        raise ValueError("Model A oracle requires one value field predicate")
    field = fields["value"]
    expected = _resolve(field.get("equals"), variables) if "equals" in field else []
    for value in expected: _check_value(value)
    datatype = field.get("datatype")
    if datatype not in (None, "integer", "string"):
        raise ValueError("Model A oracle only supports integer/string datatype")
    operation = "equals" if "equals" in field else None
    if operation != "equals":
        raise ValueError("Model A oracle only supports equals")
    match_results: list[bool] = []
    value_match = field.get("value_match", "one_or_more")
    for observed_value in observed:
        primitive = [observed_value == expected_value and type(observed_value) is type(expected_value) for expected_value in expected]
        matched = sum(primitive)
        match_results.append(_cardinality(matched, len(primitive), value_match))
    field_requirement = require.get("field_requirement", {})
    values_matching = field.get("values_matching", field_requirement.get("values_matching", "every"))
    values_found = field.get("values_found", field_requirement.get("values_found", "one_or_more"))
    field_exists = _cardinality(len(observed), len(observed), values_found)
    field_matches = _cardinality(sum(match_results), len(match_results), values_matching)
    item_condition = field_exists and field_matches
    items_satisfying = 1 if item_condition else 0
    item_result = _cardinality(items_satisfying, items_found, item_requirement.get("items_satisfying", "every"))
    outcome = "true" if _cardinality(items_found, 1, item_requirement["items_found"]) and item_result else "false"
    return {"technical_outcome": outcome, "items_found": items_found, "items_satisfying": items_satisfying, "values_found": len(observed), "values_matching": sum(match_results), "value_match": value_match, "values_matching_requirement": values_matching}
