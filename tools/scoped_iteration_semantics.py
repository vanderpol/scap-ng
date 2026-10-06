#!/usr/bin/env python3
"""Semantic validation helpers for the SCAP-NG 0.3 scoped-iteration prototype.

Research-only. JSON Schema validates shape; these checks validate lexical scope.
"""
from __future__ import annotations


def binding_references(node):
    """Yield binding-reference dictionaries recursively.

    A binding reference is recognized only when both 'binding' and 'field' are
    present so a scope declaration's own 'binding' property is not mistaken for
    a value reference.
    """
    if isinstance(node, dict):
        if isinstance(node.get("binding"), str) and isinstance(node.get("field"), str):
            yield node
        for value in node.values():
            yield from binding_references(value)
    elif isinstance(node, list):
        for value in node:
            yield from binding_references(value)


def validate_for_each_scopes(scopes, *, final_test=None):
    """Return a list of deterministic lexical-scope errors."""
    errors = []
    visible = set()

    if not isinstance(scopes, list) or not scopes:
        return ["for_each must contain at least one scope"]

    for index, scope in enumerate(scopes):
        name = scope.get("binding") if isinstance(scope, dict) else None
        if not isinstance(name, str) or not name:
            errors.append(f"scope[{index}] has no valid binding name")
            continue

        if name in visible:
            errors.append(f"binding shadowing is not allowed: {name}")

        source = scope.get("object")
        for ref in binding_references(source):
            ref_name = ref["binding"]
            if ref_name not in visible:
                errors.append(
                    f"scope[{index}] object references binding not yet in scope: {ref_name}"
                )

        visible.add(name)

    if final_test is not None:
        for ref in binding_references(final_test):
            if ref["binding"] not in visible:
                errors.append(
                    f"final Test references undeclared binding: {ref['binding']}"
                )

    return errors


def assert_valid_for_each(scopes, *, final_test=None):
    errors = validate_for_each_scopes(scopes, final_test=final_test)
    if errors:
        raise ValueError("; ".join(errors))
    return True
