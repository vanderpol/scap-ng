#!/usr/bin/env python3
"""Validate experimental 0.4 inline examples against original 0.3 authoring.

This is a *presentation round-trip* test, NOT a valid 0.4 compiler or runtime
semantic-equivalence proof: restoring the original Variable's datatype, kind,
metadata, and original identity requires the paired 0.3 witness file.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml


def exact_variable_refs(value: Any, variable: str, path=()):
    if isinstance(value, dict):
        if set(value) == {"variable"} and value.get("variable") == variable:
            yield path
        else:
            for key, child in value.items():
                yield from exact_variable_refs(child, variable, path + (key,))
    elif isinstance(value, list):
        for i, child in enumerate(value):
            yield from exact_variable_refs(child, variable, path + (i,))


def at(value: Any, path: tuple[Any, ...]) -> Any:
    result = value
    for key in path:
        result = result[key]
    return result


def restore_with_original_witness(current: dict, sketch: dict) -> dict:
    """Prove the sketch changed only one inlined reference and no other field.

    The witness is necessary because the draft inline shape is incomplete:
    it carries the expression, but not all Variable attributes or derivation
    metadata. Do not mistake this verification for compiler-lowering evidence.
    """
    current_a = current["assessment"]
    sketch_a = sketch["assessment"]
    original_variables = current_a.get("variables") or {}
    markers = []
    def walk(value, path=()):
        if isinstance(value, dict):
            if set(value) == {"expression", "research_inline_source_variable"}:
                markers.append((path, value))
            else:
                for key, child in value.items():
                    walk(child, path + (key,))
        elif isinstance(value, list):
            for i, child in enumerate(value):
                walk(child, path + (i,))
    walk(sketch_a)
    if len(markers) != 1:
        raise ValueError("expected exactly one research inline marker")
    path, inline = markers[0]
    varid = inline["research_inline_source_variable"]
    if not isinstance(varid, str) or varid not in original_variables:
        raise ValueError("missing original Variable witness")
    variable = original_variables[varid]
    if variable.get("kind") != "local" or inline["expression"] != variable.get("expression"):
        raise ValueError("inline expression altered the original Variable")
    # Only one reference to the original Variable can be hoisted.
    surface = {k: v for k, v in current_a.items() if k != "variables"}
    refs = list(exact_variable_refs(surface, varid))
    if refs != [path]:
        raise ValueError(f"expected one original Variable consumer at {path}, got {refs}")
    restored = deepcopy(sketch)
    parent = at(restored["assessment"], path[:-1])
    parent[path[-1]] = {"variable": varid}
    names = restored["assessment"].setdefault("variables", {})
    if varid in names:
        raise ValueError("Variable was not removed from the draft")
    names[varid] = deepcopy(variable)
    if restored != current:
        raise ValueError("round trip changed fields other than the intended private Variable")
    return restored


def validate_pairs(root: Path) -> dict:
    stats = json.loads((root / "STATS.json").read_text(encoding="utf-8"))
    successes = 0
    retained = 0
    for row in stats["examples"]:
        folder = root / row["folder"]
        current_file = folder / "current-0.3.assessment.yaml"
        original_file = folder / "original-1.4.oval.xml"
        sketch_file = folder / "proposed-0.4.RESEARCH.yaml"
        if not (current_file.is_file() and original_file.is_file()):
            raise ValueError(f"missing source pair: {folder}")
        if hashlib.sha256(original_file.read_bytes()).hexdigest() != row["oval_sha256"]:
            raise ValueError(f"OVAL source checksum mismatch: {folder}")
        if row["proposed_sketch"]:
            if not sketch_file.is_file():
                raise ValueError(f"missing proposed sketch: {folder}")
            current = yaml.safe_load(current_file.read_text(encoding="utf-8"))
            sketch = yaml.safe_load(sketch_file.read_text(encoding="utf-8"))
            restore_with_original_witness(current, sketch)
            successes += 1
        else:
            if sketch_file.exists():
                raise ValueError(f"unexpected proposed sketch for retained case: {folder}")
            retained += 1
    return {
        "source_pairs": len(stats["examples"]),
        "presentation_round_trips_with_original_witness": successes,
        "no_rewrite_examples": retained,
        "runtime_semantic_equivalence_proven": False,
        "self_contained_compiler_lowering_proven": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    print(json.dumps(validate_pairs(args.root), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
