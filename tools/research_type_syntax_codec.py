#!/usr/bin/env python3
"""Research-only reversible SCAP-NG datatype authoring prototype (#200).

Not an adopted v0.3 schema, normative compiler, or runtime evaluator.
Typed canonical AST equality is a structural result, NOT OVAL scanner parity.
Variable/Input types, arrays, records and dynamic operands remain explicit.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
import zipfile
import yaml

DATATYPES = frozenset({
    "string", "boolean", "integer", "float", "binary", "version",
    "ipv4", "ipv6", "rpm_evr", "debian_evr", "fileset_revision",
    "ios_version", "record",
})
OPERATIONS = frozenset({
    "equals", "not_equal", "case_insensitive_equals",
    "case_insensitive_not_equal", "greater_than", "greater_than_or_equal",
    "less_than", "less_than_or_equal", "bitwise_and", "bitwise_or",
    "pattern_match", "subset_of", "superset_of",
})
EQUALITY = frozenset({"equals", "not_equal"})
ORDERED = EQUALITY | frozenset({
    "greater_than", "greater_than_or_equal", "less_than", "less_than_or_equal"
})
TYPE_OPERATIONS = {
    "string": EQUALITY | frozenset({
        "case_insensitive_equals", "case_insensitive_not_equal", "pattern_match",
    }),
    "boolean": EQUALITY,
    "integer": ORDERED | frozenset({"bitwise_and", "bitwise_or"}),
    "float": ORDERED,
    "binary": EQUALITY,
    "version": ORDERED,
    "ipv4": ORDERED | frozenset({"subset_of", "superset_of"}),
    "ipv6": ORDERED | frozenset({"subset_of", "superset_of"}),
    "rpm_evr": ORDERED,
    "debian_evr": ORDERED,
    "fileset_revision": ORDERED,
    "ios_version": ORDERED,
    "record": frozenset({"equals"}),
}
SPECIAL_TYPES = DATATYPES - {"string", "boolean", "integer", "float", "record"}
STRATEGIES = frozenset({"hybrid", "typed-operators", "compare-as"})


class TypeSyntaxError(ValueError):
    """A comparison is ambiguous, unsupported or inconsistent."""


def inferred_scalar_type(value):
    # bool subclasses int in Python; exact type identity matters.
    if type(value) is bool:
        return "boolean"
    if type(value) is int:
        return "integer"
    if type(value) is float and math.isfinite(value):
        return "float"
    if type(value) is str:
        return "string"
    return None


def _validate_typed_comparison(node, path):
    datatype = node["datatype"]
    operation = node["operation"]
    if datatype not in TYPE_OPERATIONS:
        raise TypeSyntaxError(f"{path}: unknown datatype {datatype!r}")
    if operation not in TYPE_OPERATIONS[datatype]:
        raise TypeSyntaxError(f"{path}: {operation!r} is not legal for {datatype!r}")
    value = node["value"]
    if isinstance(value, (dict, list)):
        return
    inferred = inferred_scalar_type(value)
    if datatype in {"boolean", "integer", "string"} and inferred != datatype:
        raise TypeSyntaxError(f"{path}: {datatype} literal cannot be {inferred}")
    if datatype == "float" and inferred not in {"integer", "float"}:
        raise TypeSyntaxError(
            f"{path}: float literal cannot be {inferred}; "
            "special float representation unresolved"
        )
    if datatype in SPECIAL_TYPES and inferred != "string":
        raise TypeSyntaxError(f"{path}: {datatype} requires a string scalar")
    if datatype == "record":
        raise TypeSyntaxError(f"{path}: record must be a typed structure")


def _walk(value, transform, path="$", stats=None):
    if isinstance(value, list):
        return [_walk(v, transform, f"{path}[{i}]", stats)
                for i, v in enumerate(value)]
    if not isinstance(value, dict):
        return deepcopy(value)
    node = {key: _walk(val, transform, f"{path}.{key}", stats)
            for key, val in value.items()}
    return transform(node, path, stats)


def to_authoring(canonical, strategy="hybrid", *, stats=None):
    """Full typed v0.3 AST -> candidate compact authoring AST."""
    if strategy not in STRATEGIES:
        raise ValueError(f"unknown strategy {strategy!r}")
    stats = Counter() if stats is None else stats

    def convert(node, path, stats):
        if not {"datatype", "operation", "value"}.issubset(node):
            if "datatype" in node:
                stats["retained_noncomparison_type"] += 1
            return node
        if "compare_as" in node:
            raise TypeSyntaxError(f"{path}: canonical includes compare_as")
        value = node["value"]
        if isinstance(value, (dict, list)) or value is None:
            stats["retained_dynamic_or_collection_type"] += 1
            return node
        _validate_typed_comparison(node, path)
        effective = node["datatype"]
        inferred = inferred_scalar_type(value)
        if inferred == effective:
            del node["datatype"]
            stats["inferred_scalar"] += 1
        elif effective in SPECIAL_TYPES and strategy in {"hybrid", "typed-operators"} and (
            strategy == "typed-operators" or effective == "version"
        ):
            del node["datatype"]
            node["operation"] = f"{effective}_{node['operation']}"
            stats["typed_operator"] += 1
        else:
            del node["datatype"]
            node["compare_as"] = effective
            stats["explicit_compare_as"] += 1
        return node

    return _walk(canonical, convert, stats=stats)


def to_canonical(authoring, *, stats=None):
    """Candidate compact AST -> fully typed original v0.3 comparison AST."""
    stats = Counter() if stats is None else stats

    def convert(node, path, stats):
        typed = "datatype" in node
        compare_as = "compare_as" in node
        operation = node.get("operation")
        if compare_as and typed:
            raise TypeSyntaxError(f"{path}: datatype and compare_as conflict")
        if compare_as:
            if not ("value" in node and isinstance(operation, str)):
                raise TypeSyntaxError(f"{path}: compare_as requires a comparison")
            datatype = node.pop("compare_as")
            if datatype not in DATATYPES or datatype == "record":
                raise TypeSyntaxError(f"{path}: invalid compare_as {datatype!r}")
            if isinstance(node["value"], (dict, list)) or node["value"] is None:
                raise TypeSyntaxError(f"{path}: compare_as on non-scalar not proved")
            node["datatype"] = datatype
            _validate_typed_comparison(node, path)
            stats["expanded_compare_as"] += 1
            return node
        if typed:
            if ("value" in node and isinstance(operation, str)
                    and not isinstance(node["value"], (dict, list))):
                _validate_typed_comparison(node, path)
            return node
        if not isinstance(operation, str) or "value" not in node:
            return node
        if operation in OPERATIONS:
            inferred = inferred_scalar_type(node["value"])
            if inferred is None:
                raise TypeSyntaxError(
                    f"{path}: cannot infer type from variable/list/null; "
                    "use explicit datatype"
                )
            node["datatype"] = inferred
            _validate_typed_comparison(node, path)
            stats["expanded_inferred"] += 1
            return node
        for datatype in sorted(SPECIAL_TYPES, key=len, reverse=True):
            prefix = datatype + "_"
            if operation.startswith(prefix):
                node["operation"] = operation[len(prefix):]
                node["datatype"] = datatype
                _validate_typed_comparison(node, path)
                stats["expanded_typed_operator"] += 1
                return node
        raise TypeSyntaxError(f"{path}: unknown typed operation {operation!r}")

    return _walk(authoring, convert, stats=stats)


def census_zip(path: Path, strategy="hybrid"):
    """Verify full authoring archive (not only four hand-picked examples)."""
    stats = Counter()
    kinds = Counter()
    mismatches = []
    with zipfile.ZipFile(path) as archive:
        failed = archive.testzip()
        if failed:
            raise ValueError(f"bad ZIP member {failed}")
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError("duplicate ZIP member path")
        for name in names:
            if not name.endswith(".yaml"):
                continue
            canonical = yaml.safe_load(archive.read(name))
            kinds[next(iter(canonical))] += 1
            simplified = to_authoring(canonical, strategy, stats=stats)
            restored = to_canonical(simplified, stats=stats)
            if restored != canonical:
                mismatches.append(name)
    if mismatches:
        raise ValueError(f"typed AST mismatch: {mismatches[:10]}")
    return {
        "zip_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "strategy": strategy,
        "documents_by_kind": dict(sorted(kinds.items())),
        "counts": dict(sorted(stats.items())),
        "roundtrip_mismatches": len(mismatches),
        "caveat": "Typed AST reconstruction only; runtime conformance not proved",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("zip", type=Path)
    parser.add_argument("--strategy", choices=sorted(STRATEGIES),
                        default="hybrid")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    report = census_zip(args.zip, args.strategy)
    data = json.dumps(report, sort_keys=True, indent=2) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(data, encoding="utf-8")
    print(data, end="")


if __name__ == "__main__":
    main()
