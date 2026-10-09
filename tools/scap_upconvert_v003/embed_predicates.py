#!/usr/bin/env python3
"""Lossless SCAP-NG 0.3 authoring-only State/Filter locality upgrade.

Only the representation changes. Comparisons, Test aggregation and Object
acquisitions stay untouched. The separate ledger reconstructs the exact input,
including the named State registry, source titles and repeated references.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any


def _at(root: dict, path: list):
    node = root
    for key in path:
        node = node[key]
    return node


def _state_payload(value: Any, named: dict, capability: str, path: list) -> dict:
    """Resolve old local/named States, rejecting any lossy inference."""
    if isinstance(value, str):
        if value not in named:
            raise ValueError(f"{path}: missing named State {value!r}")
        wrapper = named[value]
    else:
        wrapper = value
    if not isinstance(wrapper, dict):
        raise ValueError(f"{path}: State must be a mapping or resolved reference")
    # Already-native local condition; there is no State identity to rewrite.
    if "state" not in wrapper and "capability" not in wrapper:
        return copy.deepcopy(wrapper)
    if set(wrapper) - {"state", "capability", "state_title"}:
        raise ValueError(f"{path}: unsupported State wrapper keys: {sorted(set(wrapper)-{'state','capability','state_title'})}")
    if not capability or wrapper.get("capability") != capability:
        raise ValueError(f"{path}: Filter/Test State capability mismatch: {wrapper.get('capability')!r} != {capability!r}")
    payload = wrapper.get("state")
    if not isinstance(payload, dict) or not payload:
        raise ValueError(f"{path}: State comparison must be a nonempty mapping")
    if "capability" in payload or "state_title" in payload or "state" in payload:
        raise ValueError(f"{path}: ambiguous State comparison keys")
    return copy.deepcopy(payload)


def embed_predicates(document: dict) -> tuple[dict, dict]:
    """Return (native document, reversible non-executable migration ledger).

    An input with malformed or unexpectedly referenced State nodes fails closed.
    Re-expand against the returned ledger before accepting a conversion.
    """
    result = copy.deepcopy(document)
    assessment = result.get("assessment")
    if not isinstance(assessment, dict):
        raise ValueError("expected assessment document")
    if assessment.get("mode") != "automated":
        return result, {"format": "scap-ng-inline-predicates-1", "changes": [], "named_states": None}
    had_named = "states" in assessment
    named = assessment.pop("states", {})
    if not isinstance(named, dict):
        raise ValueError("assessment.states must be a mapping")
    ledger = {
        "format": "scap-ng-inline-predicates-1",
        "named_states": copy.deepcopy(named) if had_named else None,
        "changes": [],
    }
    refs = {}
    for section in ("objects", "shared_objects"):
        for name, obj in (assessment.get(section) or {}).items():
            if name in refs:
                raise ValueError(f"duplicate Object name {name!r}")
            refs[name] = obj

    def change(path: list, new: dict):
        old = copy.deepcopy(_at(result, path))
        if old == new:
            return
        ledger["changes"].append({"path": path, "original": old, "rendered": copy.deepcopy(new)})
        container = _at(result, path[:-1])
        container[path[-1]] = new

    for name, test in (assessment.get("tests") or {}).items():
        if not isinstance(test, dict):
            raise ValueError(f"tests.{name}: invalid Test")
        cap = test.get("capability")
        entries = test.get("states", [])
        if not isinstance(entries, list):
            raise ValueError(f"tests.{name}.states: expected list")
        for i, state in enumerate(entries):
            path = ["assessment", "tests", name, "states", i]
            change(path, _state_payload(state, named, cap, path))

    # Inspect every Object graph (including inline Sets nested in Tests or
    # Variables) without visiting deep evaluate trees recursively.
    stack = [(assessment, ["assessment"], None)]
    while stack:
        node, path, enclosing_cap = stack.pop()
        if isinstance(node, list):
            for i, item in enumerate(node):
                if isinstance(item, (list, dict)):
                    stack.append((item, path + [i], enclosing_cap))
            continue
        if not isinstance(node, dict):
            continue
        cap = node.get("capability", enclosing_cap)
        if "filters" in node:
            entries = node["filters"]
            if not isinstance(entries, list):
                raise ValueError(f"{path}.filters: expected list")
            object_use = node.get("object")
            if isinstance(object_use, str):
                if object_use not in refs:
                    raise ValueError(f"{path}: unresolved Filter Object {object_use!r}")
                cap = refs[object_use].get("capability")
            elif isinstance(object_use, dict):
                cap = object_use.get("capability", cap)
            for i, filt in enumerate(entries):
                location = path + ["filters", i]
                if not isinstance(filt, dict) or filt.get("action") not in ("include", "exclude"):
                    raise ValueError(f"{location}: Filter requires explicit include/exclude action")
                if "state" not in filt:
                    if not any(k in filt for k in ("field", "all", "any", "one", "odd", "fields")):
                        raise ValueError(f"{location}: no Filter comparison")
                    continue
                if set(filt) != {"action", "state"}:
                    raise ValueError(f"{location}: unsupported Filter wrapper fields")
                comparison = _state_payload(filt["state"], named, cap, location)
                if "action" in comparison:
                    raise ValueError(f"{location}: action would collide with predicate")
                change(location, {"action": filt["action"], **comparison})
        for key, value in node.items():
            if key == "filters":
                continue
            if isinstance(value, (dict, list)):
                stack.append((value, path + [key], cap))

    # No State reference may be silently orphaned by removing the registry.
    stack = [assessment]
    while stack:
        value = stack.pop()
        if isinstance(value, dict):
            for key, item in value.items():
                if key == "state" and isinstance(item, str) and item in named:
                    raise ValueError(f"unconverted reference to named State: {item!r}")
                if isinstance(item, (dict, list)):
                    stack.append(item)
        elif isinstance(value, list):
            stack.extend(item for item in value if isinstance(item, (dict, list)))
    if reexpand_predicates(result, ledger) != document:
        raise ValueError("embedded State migration failed exact re-expansion")
    return result, ledger


def reexpand_predicates(document: dict, ledger: dict) -> dict:
    """Reconstruct the complete pre-upgrade source, verifying every replacement."""
    if ledger.get("format") != "scap-ng-inline-predicates-1":
        raise ValueError("unsupported migration ledger")
    result = copy.deepcopy(document)
    for item in reversed(ledger["changes"]):
        current = _at(result, item["path"])
        if current != item["rendered"]:
            raise ValueError(f"changed migrated predicate at {item['path']}")
        _at(result, item["path"][:-1])[item["path"][-1]] = copy.deepcopy(item["original"])
    if ledger.get("named_states") is not None:
        result["assessment"]["states"] = copy.deepcopy(ledger["named_states"])
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Legacy 0.3 YAML or JSON Assessment")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--ledger", type=Path, required=True)
    args = parser.parse_args()
    if args.source.suffix == ".json":
        original = json.loads(args.source.read_text(encoding="utf-8"))
    else:
        import yaml
        original = yaml.safe_load(args.source.read_text(encoding="utf-8"))
    upgraded, ledger = embed_predicates(original)
    if reexpand_predicates(upgraded, ledger) != original:
        raise ValueError("exact re-expansion failed")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.ledger.parent.mkdir(parents=True, exist_ok=True)
    if args.output.suffix == ".json":
        text = json.dumps(upgraded, indent=2) + "\n"
    else:
        import yaml
        text = yaml.safe_dump(upgraded, sort_keys=False, width=120)
    args.output.write_text(text, encoding="utf-8")
    args.ledger.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
