#!/usr/bin/env python3
"""Audit flat-Object field collisions across every v0.4.0 native capability.

Fail closed before promoting Object select/collect flattening to native schemas.
Refs #248 #239 #232.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "schema/v0.4.0/capability-mappings/supported"
RESERVED = frozenset({
    "capability", "object", "object_title", "collect", "filters", "set",
    "traversal", "filesystem", "behaviors", "for_each", "foreach",
})
# 'select' deliberately NOT reserved: windows.cmdlet has a genuine *native*
# collection parameter named select for the output property selection record.
# In the flattened grammar, the generic wrapper object.select is abolished.
EXPECTED_NATIVE_SELECT = "windows.cmdlet"


class CollisionError(ValueError):
    pass


def inspect(mapping):
    cap = mapping.get("capability")
    native = mapping.get("native") or {}
    names = list((native.get("selector_map") or {}).values())
    params = list((native.get("collection_parameters") or {}).keys())
    if not isinstance(cap, str) or not cap:
        raise CollisionError("Missing capability name")
    if any(not isinstance(n, str) or not n for n in names + params):
        raise CollisionError(f"{cap}: empty/non-string field name")
    if len(set(names)) != len(names):
        raise CollisionError(f"{cap}: duplicate normalized selector")
    if len(set(params)) != len(params):
        raise CollisionError(f"{cap}: duplicate collection parameter")
    overlap = set(names) & set(params)
    blocked = (set(names) | set(params)) & RESERVED
    if "select" in names:
        blocked.add("select")
    if "select" in params and cap != EXPECTED_NATIVE_SELECT:
        blocked.add("select")
    if overlap or blocked:
        raise CollisionError(
            f"{cap}: duplicated selector/parameter {sorted(overlap)}; "
            f"reserved control keys {sorted(blocked)}")
    return {
        "capability": cap,
        "selector_count": len(names),
        "parameter_count": len(params),
        "native_select_parameter": "select" in params,
    }


def audit(directory=CATALOG, *, expected_count=100):
    paths = sorted(Path(directory).glob("*.json"))
    if len(paths) != expected_count:
        raise CollisionError(f"Expected {expected_count} mappings, saw {len(paths)}")
    records = []
    for path in paths:
        mapping = json.loads(path.read_text(encoding="utf-8"))
        if path.stem != mapping.get("capability"):
            raise CollisionError(f"{path}: capability does not match filename")
        records.append(inspect(mapping))
    return {
        "status": "PASS",
        "catalog_count": len(records),
        "with_selectors": sum(bool(r["selector_count"]) for r in records),
        "without_selectors": sum(not r["selector_count"] for r in records),
        "with_acquisition_parameters": sum(bool(r["parameter_count"]) for r in records),
        "native_select_acquisition_parameters": [
            r["capability"] for r in records if r["native_select_parameter"]],
        "collision_count": 0,
        "flat_object_promotion_approved_by_this_check_alone": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, default=CATALOG)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    result = audit(args.directory)
    output = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(output, encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
