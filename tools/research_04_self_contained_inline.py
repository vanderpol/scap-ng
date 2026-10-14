#!/usr/bin/env python3
"""Experimental lossless *syntax lowering*, not an adopted 0.4 language.

A private one-consumer Variable/Object may be declared at its sole use site.
The entire definition, including datatype and metadata, travels with it.
Expansion recreates the exact current 0.3 Assessment with no external witness.

Because this only changes representation, it does not prove OVAL/scanner
runtime equivalence, nor show that nesting improves author readability.
"""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
from pathlib import Path
import json
import yaml

VARIABLE_MARKER = "research_inline_variable"
OBJECT_MARKER = "research_inline_object"


def refs(value, name, id_, path=()):
    if isinstance(value, dict):
        if set(value) == {name} and value[name] == id_:
            yield path
        else:
            for k, v in value.items():
                yield from refs(v, name, id_, path + (k,))
    elif isinstance(value, list):
        for idx, child in enumerate(value):
            yield from refs(child, name, id_, path + (idx,))


def object_refs(node, oid, path=()):
    if isinstance(node, dict):
        for k, v in node.items():
            if k == "object" and v == oid:
                yield path + (k,)
            elif k == "in" and v == oid and path and path[-1] == "for_each":
                yield path + (k,)
            else:
                yield from object_refs(v, oid, path + (k,))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from object_refs(v, oid, path + (i,))


def get_node(node, path):
    for k in path:
        node = node[k]
    return node


def put_node(node, path, value):
    if not path:
        raise ValueError("cannot overwrite Assessment root")
    get_node(node, path[:-1])[path[-1]] = deepcopy(value)


def depth(node):
    if isinstance(node, dict):
        return 1 + max([depth(x) for x in node.values()] or [0])
    if isinstance(node, list):
        return 1 + max([depth(x) for x in node] or [0])
    return 0


def metrics(doc):
    text = yaml.safe_dump(doc, sort_keys=False, allow_unicode=True)
    a = doc["assessment"]
    return {
        "lines": len(text.splitlines()),
        "bytes": len(text.encode("utf-8")),
        "max_nesting": depth(doc),
        "named_variables": len(a.get("variables") or {}),
        "named_objects": len(a.get("objects") or {}) + len(a.get("shared_objects") or {}),
    }


def inline_variable(doc, id_, *, allow_chain=False):
    new = deepcopy(doc)
    a = new["assessment"]
    registry = a.get("variables") or {}
    definition = registry.get(id_)
    if not isinstance(definition, dict) or definition.get("kind") not in {"local", "constant"}:
        raise ValueError("Variable is not a typed local/static definition")
    surfaces = {k: v for k, v in a.items() if k != "variables"}
    uses = list(refs(surfaces, "variable", id_))
    for other, payload in registry.items():
        if other != id_:
            uses.extend(("variables", other) + loc for loc in refs(payload, "variable", id_))
    if len(uses) != 1:
        raise ValueError("Variable is not private to one consumer")
    loc = uses[0]
    if loc[0] == "variables" and not allow_chain:
        raise ValueError("Variable is part of a named computation chain")
    if loc[0] not in {"tests", "objects", "states", "shared_objects", "variables"}:
        raise ValueError("Unreviewed consumer location")
    put_node(a, loc, {VARIABLE_MARKER: {"id": id_, "definition": deepcopy(definition)}})
    del a["variables"][id_]
    if not a["variables"]:
        del a["variables"]
    if lower_inline(new) != doc:
        raise ValueError("Independent lowering differs from input")
    return new, {"name": id_, "kind": "variable", "consumer_path": list(loc),
                 "consumer_is_variable": loc[0] == "variables"}


def inline_object(doc, oid):
    new = deepcopy(doc)
    a = new["assessment"]
    locations = [(section, a[section][oid])
                 for section in ("shared_objects", "objects")
                 if isinstance(a.get(section), dict) and oid in a[section]]
    if len(locations) != 1:
        raise ValueError("Object declaration not unique")
    section, definition = locations[0]
    uses = list(object_refs(a, oid))
    if len(uses) != 1:
        raise ValueError("Object does not have exactly one reference")
    loc = uses[0]
    if len(loc) < 3 or loc[-2:] != ("for_each", "in"):
        raise ValueError("Only for_each source nesting is in this research scope")
    put_node(a, loc, {OBJECT_MARKER: {
        "id": oid, "registry": section, "definition": deepcopy(definition)}})
    del a[section][oid]
    if not a[section]:
        del a[section]
    if lower_inline(new) != doc:
        raise ValueError("Independent Object lowering differs from input")
    return new, {"name": oid, "kind": "object", "consumer_path": list(loc)}


def lower_inline(doc):
    """Expand all self-contained private declarations; reject ambiguity."""
    result = deepcopy(doc)
    a = result.get("assessment")
    if not isinstance(a, dict):
        raise ValueError("missing Assessment")
    declarations = []
    def expand(node):
        if isinstance(node, dict):
            if set(node) in ({VARIABLE_MARKER}, {OBJECT_MARKER}):
                is_var = VARIABLE_MARKER in node
                entry = node[VARIABLE_MARKER if is_var else OBJECT_MARKER]
                required = {"id", "definition"} if is_var else {"id", "registry", "definition"}
                if not isinstance(entry, dict) or set(entry) != required:
                    raise ValueError("Incomplete inline declaration")
                id_ = entry["id"]
                if not isinstance(id_, str) or not id_ or not isinstance(entry["definition"], dict):
                    raise ValueError("Invalid declaration identity or body")
                if is_var:
                    if entry["definition"].get("kind") not in {"local", "constant"}:
                        raise ValueError("Unsupported private Variable kind")
                    section = "variables"
                    ref_name = "variable"
                else:
                    section = entry["registry"]
                    if section not in {"objects", "shared_objects"}:
                        raise ValueError("Unsupported private Object registry")
                    ref_name = "object"
                declarations.append((section, id_, deepcopy(entry["definition"])))
                # Collection for_each.in refers to its source Object by a
                # scalar name, unlike an ordinary Object reference mapping.
                return {ref_name: id_} if is_var else id_
            return {k: expand(v) for k, v in node.items()}
        if isinstance(node, list):
            return [expand(v) for v in node]
        return node
    a = expand(a)
    seen = set()
    for section, id_, body in declarations:
        if (section, id_) in seen:
            raise ValueError("Duplicate private declaration")
        seen.add((section, id_))
        target = a.setdefault(section, {})
        if id_ in target:
            raise ValueError("Inline declaration shadows existing declaration")
        target[id_] = body
    # Also forbid duplicate identities split across Object registries.
    overlap = set(a.get("objects") or {}) & set(a.get("shared_objects") or {})
    if overlap:
        raise ValueError("Ambiguous named Object identity")
    result["assessment"] = a
    return result


def assert_exact(a, b):
    if a != b:
        raise ValueError("Structural semantic graph mismatch")


def analyze_chain(assessment):
    """Classify Variable dependency edges/fanout without claiming auto safety."""
    vars_ = assessment.get("variables") or {}
    edges = []
    fanout = Counter()
    for name in vars_:
        usage = sum(1 for _ in refs({k:v for k,v in assessment.items() if k != "variables"},
                                    "variable", name))
        for other, payload in vars_.items():
            if other == name:
                continue
            n = sum(1 for _ in refs(payload, "variable", name))
            usage += n
            edges.extend([(other,name)] * n)
        fanout[name] = usage
    successors = Counter(dst for src, dst in edges)
    private_chained = {
        src for src, dst in edges if fanout[dst] == 1 and
        isinstance(vars_.get(dst), dict) and vars_[dst].get("kind") == "local"
    }
    return {
        "variables": len(vars_),
        "dependency_edges": len(edges),
        "variable_producers_used_once_in_chains": len({dst for src,dst in edges if fanout[dst] == 1}),
        "private_chained_producers": len(private_chained),
        "chain_consumers": len({src for src, dst in edges}),
        "unused_definitions": sum(v == 0 for v in fanout.values()),
        "multi_use_definitions": sum(v > 1 for v in fanout.values()),
    }
