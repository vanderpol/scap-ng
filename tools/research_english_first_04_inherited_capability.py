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
        source = sources[source_id]
        if not isinstance(source, dict) or not isinstance(source.get("inspect"), str):
            raise Unsupported(f"{name}: source capability cannot be proven")
        actual = check.get("inspect")
        expected = source["inspect"]
        if actual != expected:
            raise Unsupported(f"{name}: source capability mismatch {actual!r} != {expected!r}")
        del check["inspect"]
        removed += 1
    return out, removed


def restore(compact: dict) -> dict:
    out = copy.deepcopy(compact)
    for name, check in out["checks"].items():
        if "from" in check:
            source = out["sources"].get(check["from"])
            if not isinstance(source, dict) or not isinstance(source.get("inspect"), str):
                raise Unsupported(f"{name}: source type cannot be restored")
            if "inspect" in check:
                raise Unsupported(f"{name}: compact check repeats inspect")
            check["inspect"] = source["inspect"]
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
