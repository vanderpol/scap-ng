#!/usr/bin/env python3
"""Small, scanner-independent native authoring semantic gate.

JSON Schema answers whether a document has the right shape.  This module holds
only approved 0.4.1 rules whose rejection is required before collection.  It
never evaluates evidence and must not be used to manufacture scanner results.
"""
from __future__ import annotations

from typing import Any


def _objects(value: Any):
    if isinstance(value, dict):
        if "capability" in value:
            yield value
        for child in value.values():
            yield from _objects(child)
    elif isinstance(value, list):
        for child in value:
            yield from _objects(child)


def _record_names(record: Any) -> tuple[set[str], bool]:
    """Return explicit selection names and whether the record is dynamic."""
    if record is None:
        return set(), False
    if not isinstance(record, dict):
        return set(), True
    fields = record.get("fields")
    if not isinstance(fields, dict):
        # A record with an unrecognised/dynamic representation is fail-closed.
        return set(), True
    names = set(fields)
    dynamic = any(
        isinstance(name, str) and (name.startswith("{") or name.endswith("}"))
        or isinstance(value, dict) and any(key in value for key in ("variable", "input"))
        for name, value in fields.items()
    )
    return names, dynamic


def validate(document: dict[str, Any]) -> list[dict[str, str]]:
    """Return deterministic semantic rejections for an authored Assessment."""
    errors: list[dict[str, str]] = []
    tests = document.get("assessment", {}).get("tests", {})
    for test_name, test in tests.items():
        if not isinstance(test, dict):
            continue
        capability = test.get("capability")
        for obj in _objects(test.get("object")):
            if obj.get("capability") != capability:
                continue
            if capability == "windows.cmdlet" and "select" in obj:
                names, dynamic = _record_names(obj.get("select"))
                if "*" in names:
                    errors.append({"test": test_name, "rule": "windows.cmdlet.select_no_wildcard", "reason": "object.select contains the wildcard member '*'"})
                elif dynamic:
                    errors.append({"test": test_name, "rule": "windows.cmdlet.select_no_wildcard", "reason": "object.select field names are dynamic or unverifiable; validation fails closed"})
            if capability in {"windows.ntuser", "windows.registry", "windows.regkeyeffectiverights"} and "traversal" in obj:
                key = obj.get("key")
                if isinstance(key, dict) and "equals" not in key:
                    errors.append({"test": test_name, "rule": f"{capability}.pattern_key_no_traversal", "reason": "traversal is combined with a non-equality key selector"})
        if capability == "windows.auditeventpolicysubcategories":
            fields = test.get("require", {}).get("fields", {})
            if isinstance(fields, dict) and "kerberos_ticket_events" in fields:
                errors.append({"test": test_name, "rule": "windows.auditeventpolicysubcategories.supported_fields", "reason": "deprecated kerberos_ticket_events is not a native field"})
    return errors
