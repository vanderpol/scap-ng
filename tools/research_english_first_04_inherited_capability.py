#!/usr/bin/env python3
"""Research-only, fail-closed test of redundant check.inspect for named sources.

Checks which use a named from may inherit a source's declared capability,
provided the original check's capability agrees and no competing acquisition
mode is present. This tests structural dictionaries, NOT scanner/OVAL semantics.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import sys

import yaml


class Unsupported(ValueError):
    """A change cannot be justified by this narrow reversible experiment."""


SET_OPS = ("union", "difference", "intersection", "complement")


def infer_type(node: dict, sources: dict, active: tuple[str, ...] = ()) -> str:
    """Resolve a typed source DAG, rejecting ambiguous or cyclic compositions."""
    if not isinstance(node, dict):
        raise Unsupported("Source node is not a mapping")
    direct = node.get("inspect")
    if direct is not None and (not isinstance(direct, str) or not direct):
        raise Unsupported("Invalid source inspect capability")
    composed = [op for op in SET_OPS if op in node]
    if len(composed) > 1 or (composed and "from" in node):
        raise Unsupported("Competing source composition forms")
    derived = []
    if "from" in node:
        ref = node["from"]
        if isinstance(ref, dict):
            derived.append(infer_type(ref, sources, active))
        elif isinstance(ref, str) and ref in sources:
            if ref in active:
                raise Unsupported("Source reference cycle: " + " -> ".join((*active, ref)))
            derived.append(infer_type(sources[ref], sources, (*active, ref)))
        else:
            raise Unsupported(f"Source reference does not resolve: {ref!r}")
    if composed:
        operands = node[composed[0]]
        if not isinstance(operands, list) or not operands:
            raise Unsupported("Set operands must be a nonempty sequence")
        derived.extend(infer_type(item, sources, active) for item in operands)
    observed = {x for x in derived}
    if len(observed) > 1:
        raise Unsupported(f"Mixed-capability source composition: {sorted(observed)}")
    if direct and observed and direct != next(iter(observed)):
        raise Unsupported("Declared source capability differs from operand capabilities")
    if direct:
        return direct
    if observed:
        return next(iter(observed))
    raise Unsupported("Source capability cannot be inferred")


def transform(doc: dict) -> tuple[dict, int]:
    if not isinstance(doc, dict):
        raise Unsupported("Assessment must be a YAML mapping")
    sources = doc.get("sources", {})
    checks = doc.get("checks")
    if not isinstance(sources, dict) or not isinstance(checks, dict):
        raise Unsupported("Expected named sources and checks mappings")
    out = copy.deepcopy(doc)
    removed = 0
    for name, check in out["checks"].items():
        if not isinstance(check, dict):
            raise Unsupported(f"{name}: check is not a mapping")
        if "from" not in check:
            continue  # Inline, objectless and collector checks remain unchanged.
        if "gather" in check or "collect" in check or "where" in check:
            raise Unsupported(f"{name}: named source combined with competing acquisition")
        source_id = check["from"]
        if not isinstance(source_id, str) or source_id not in sources:
            raise Unsupported(f"{name}: source does not resolve: {source_id!r}")
        actual = check.get("inspect")
        expected = infer_type(sources[source_id], sources, (source_id,))
        if actual != expected:
            raise Unsupported(f"{name}: source capability mismatch {actual!r} != {expected!r}")
        del check["inspect"]
        removed += 1
    return out, removed


def restore(compact: dict) -> dict:
    out = copy.deepcopy(compact)
    for name, check in out["checks"].items():
        if "from" in check:
            source_id = check["from"]
            if source_id not in out["sources"]:
                raise Unsupported(f"{name}: source type cannot be restored")
            if "inspect" in check:
                raise Unsupported(f"{name}: compact check repeats inspect")
            check["inspect"] = infer_type(out["sources"][source_id], out["sources"], (source_id,))
    return out


def audit(path: Path) -> dict:
    original = yaml.safe_load(path.read_text(encoding="utf-8"))
    compact, removed = transform(original)
    rebuilt = restore(compact)
    if rebuilt != original:
        raise Unsupported("Full Assessment dictionary changed after round-trip")
    return {
        "file": str(path),
        "checks": len(original["checks"]),
        "inherited_inspect_removed": removed,
        "exact_dictionary_round_trip": True,
    }


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("files", nargs="+", type=Path)
    args = p.parse_args(argv)
    results = []
    for path in args.files:
        try:
            results.append(audit(path))
        except (Unsupported, OSError, yaml.YAMLError) as exc:
            print(json.dumps({"file": str(path), "error": str(exc)}), file=sys.stderr)
            return 1
    print(json.dumps({
        "status": "EXACT DICTIONARY ROUND TRIP; NOT SCANNER PARITY",
        "results": results,
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
