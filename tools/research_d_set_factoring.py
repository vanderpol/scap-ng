#!/usr/bin/env python3
"""Refs #246 — D exact-subtree Set reuse without changing original OVAL logic.

Repeated nested Set expressions may refer to an identical already-named Set
expression in the authoring document. Compiling expands them to the exact
original nested Set AST, preserving operands, filters, order and source IDs.
This is compile-time authoring factoring, NOT runtime collection caching.
"""
from __future__ import annotations
from copy import deepcopy
import argparse
import json
from pathlib import Path
import yaml

from research_d_oval_sets import (
    D_STAGE, present_d_oval_sets, compile_d_oval_sets, prove_d_oval_sets)

STAGE = "D_RESEARCH_OVAL_EXACT_NESTED_SET_SUBTREE_FACTORED"
D_KEYS = {"stage", "assessment", "collections", "expected_values", "tests", "evaluate"}


def _fail(message):
    raise ValueError("D exact Set subtree factoring: " + message)


def _key(spec):
    return json.dumps(spec, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False)


def _copy_with_reuse(node, owner, normalized_sets, counts, *, member=False):
    """Factor only an exact nested {set: ...} member, never a Set root.

    The expected replacement is already a named, source-equivalent Set.
    Nothing changes any of the original Set operation, members, filter actions
    or their sequence.
    """
    if isinstance(node, list):
        return [_copy_with_reuse(x, owner, normalized_sets, counts,
                                 member=member) for x in node]
    if not isinstance(node, dict):
        return deepcopy(node)
    if member and set(node) == {"set"}:
        candidates = [alias for alias in normalized_sets.get(_key(node["set"]), [])
                      if alias != owner]
        if candidates:
            chosen = sorted(candidates)[0]
            counts[0] += 1
            return {"reuse_set": chosen}
    return {
        key: _copy_with_reuse(value, owner, normalized_sets, counts,
                              member=(key == "members"))
        for key, value in node.items()
    }


def present_factored_sets(original):
    authored, provenance = present_d_oval_sets(original)
    collections = authored["collections"]
    catalog = {}
    for alias, node in collections.items():
        if "set" in node:
            catalog.setdefault(_key(node["set"]), []).append(alias)
    edits = [0]
    # Build from the original snapshot, not the already-factored definitions.
    rewritten = deepcopy(collections)
    for alias, node in collections.items():
        if "set" in node:
            rewritten[alias]["set"] = _copy_with_reuse(
                node["set"], alias, catalog, edits)
    if edits[0] <= 0:
        _fail("no source-equal nested Set reuse detected")
    authored["stage"] = STAGE
    authored["collections"] = rewritten
    return authored, provenance, edits[0]


def _expand(node, catalog, *, as_member=False, visited=()):
    if isinstance(node, list):
        return [_expand(x, catalog, as_member=as_member, visited=visited) for x in node]
    if not isinstance(node, dict):
        return deepcopy(node)
    if "reuse_set" in node:
        if not as_member or set(node) != {"reuse_set"}:
            _fail("reuse_set only allowed as a standalone nested Set member")
        name = node["reuse_set"]
        if type(name) is not str or name not in catalog:
            _fail("unresolved or unsupported reused Set identity")
        if name in visited or len(visited) > 64:
            _fail("recursive/re-entrant Set alias")
        definition = catalog[name]
        if not isinstance(definition, dict) or "set" not in definition:
            _fail("source binding does not identify a named Set")
        return {"set": _expand(definition["set"], catalog,
                               visited=(*visited, name))}
    return {
        key: _expand(value, catalog, as_member=(key == "members"),
                     visited=visited)
        for key, value in node.items()
    }


def compile_factored_sets(author, provenance):
    if not isinstance(author, dict) or set(author) != D_KEYS or author.get("stage") != STAGE:
        _fail("complete D factored Assessment required")
    collections = author["collections"]
    if not isinstance(collections, dict) or len(collections) != 11:
        _fail("all source Object declarations are required")
    expanded = deepcopy(author)
    expanded["stage"] = D_STAGE
    for alias, obj in collections.items():
        if not isinstance(obj, dict):
            _fail("typed source Object declaration required")
        expanded["collections"][alias] = _expand(
            obj, collections, visited=(alias,))
    # The original D compiler and pinned C authoring source hash are the
    # semantic source of truth. No independent Set evaluator is introduced.
    return compile_d_oval_sets(expanded, provenance)


def prove_factored_sets(original, author, provenance):
    native = compile_factored_sets(author, provenance)
    if native != original:
        _fail("factored Set graph differs from pinned original source")
    # This also validates the original source binding and complete IR by
    # inverting the factored representation before the unchanged compiler.
    plain = deepcopy(author)
    plain["stage"] = D_STAGE
    for alias, obj in author["collections"].items():
        plain["collections"][alias] = _expand(
            obj, author["collections"], visited=(alias,))
    original_proof = prove_d_oval_sets(original, plain, provenance)
    return {**original_proof,
            "factored_exact_set_member_count": _count_reuse(author["collections"]),
            "new_runtime_set_collector_required": False}


def _count_reuse(node):
    if isinstance(node, list):
        return sum(_count_reuse(x) for x in node)
    if isinstance(node, dict):
        if set(node) == {"reuse_set"}:
            return 1
        return sum(_count_reuse(x) for x in node.values())
    return 0


def export_factored_sets(source, destination):
    author, provenance, found = present_factored_sets(source)
    proof = prove_factored_sets(source, author, provenance)
    if found != proof["factored_exact_set_member_count"]:
        _fail("authored Set factor count changed")
    out = Path(destination)
    out.mkdir(parents=True, exist_ok=True)
    core = yaml.safe_dump(author, sort_keys=False, allow_unicode=True)
    (out / "unix-set-seven-tests.0.4-D-reused-sets.yaml").write_text(
        "# 0.4-D source-exact subtree reuse for pinned OVAL 5.12.3 nested Sets.\n"
        "# Reused Sets are expanded by compiler; execution still uses original graph.\n"
        + core, encoding="utf-8")
    proof["authored_lines"] = len(core.splitlines())
    proof["authored_bytes"] = len(core.encode("utf-8"))
    (out / "factoring-proof.json").write_text(
        json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return proof


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    source = json.loads(args.source.read_text(encoding="utf-8"))
    print(json.dumps(export_factored_sets(source, args.out), indent=2))
