#!/usr/bin/env python3
"""Reversible 0.4 field_requirement projection after complete-State AND/OR lowering.

This is an authoring migration candidate. Exact inverse is proven; scanner
equivalence and canonical schema promotion are separate gates. Refs #248 #239.
"""
from copy import deepcopy
import hashlib
import json


def digest(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False).encode()).hexdigest()


def rename(node, old, new, path, changes):
    if old not in node:
        return
    if new in node:
        raise ValueError(f"conflicting field requirement: {path}")
    node[new] = node.pop(old)
    changes.append((list(path), old, new))


def rewrite_conditions(node, path, changes):
    if isinstance(node, list):
        for i, child in enumerate(node):
            rewrite_conditions(child, path + (i,), changes)
        return
    if not isinstance(node, dict):
        return
    rename(node, "state_fields_require", "field_requirement", path, changes)
    if "fields" in node:
        if isinstance(node.get("require"), str):
            rename(node, "require", "field_requirement", path, changes)
        fields = node["fields"]
        if not isinstance(fields, dict):
            raise ValueError(f"invalid fields mapping: {path}")
        for field, value in fields.items():
            if isinstance(value, dict):
                rename(value, "require", "field_requirement",
                       path + ("fields", field), changes)
        return
    for op in ("and", "or", "one", "xor"):
        if op in node:
            rewrite_conditions(node[op], path + (op,), changes)


def migrate(source):
    candidate = deepcopy(source)
    changes = []
    assessment = candidate.get("assessment") if isinstance(candidate, dict) else None
    if isinstance(assessment, dict) and assessment.get("mode") == "automated":
        for test_id, test in (assessment.get("tests") or {}).items():
            path = ("assessment", "tests", test_id)
            if not isinstance(test, dict):
                raise ValueError(f"invalid Test: {test_id}")
            if "state_fields_require" in test:
                requirement = test.get("require")
                if not isinstance(requirement, dict) or "field_requirement" in requirement:
                    raise ValueError(f"cannot hoist Test field requirement: {test_id}")
                requirement["field_requirement"] = test.pop("state_fields_require")
                changes.append((list(path), "state_fields_require",
                                "require.field_requirement"))
            requirement = test.get("require")
            if isinstance(requirement, dict) and "all_items_must" in requirement:
                rewrite_conditions(requirement["all_items_must"],
                                   path + ("require", "all_items_must"), changes)
    return candidate, {"source": digest(source), "candidate": digest(candidate),
                       "changes": changes}


def restore(candidate, ledger):
    if digest(candidate) != ledger["candidate"]:
        raise ValueError("candidate mutated after conversion")
    restored = deepcopy(candidate)
    for path, old, new in reversed(ledger["changes"]):
        node = restored
        for segment in path:
            node = node[segment]
        if new == "require.field_requirement":
            if old in node or "field_requirement" not in node["require"]:
                raise ValueError("cannot invert Test field requirement")
            node[old] = node["require"].pop("field_requirement")
        else:
            if old in node or new not in node:
                raise ValueError("cannot invert local field requirement")
            node[old] = node.pop(new)
    if digest(restored) != ledger["source"]:
        raise ValueError("inverse does not reconstruct original source")
    return restored
