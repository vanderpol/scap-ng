#!/usr/bin/env python3
"""Verify importer-known OVAL defaults against the pinned 5.12.3 XSD.

Scope: generic Definition/Test/Object/State/Variable base types and the
two State Entity base types, not every collector/platform behavior.
Schema-valid structural defaults do not prove runtime execution equivalence.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

from xsd_effective_defaults import catalog, effective_type_attributes

NS = "http://oval.mitre.org/XMLSchema/oval-definitions-5"
SCOPES = {
    "definition": ("DefinitionType",),
    "test": ("TestType",),
    "object": ("ObjectType",),
    "state": ("StateType",),
    "variable": ("VariableType",),
    "state_entity": ("EntityStateSimpleBaseType", "EntityStateComplexBaseType"),
}


def load_importer(path: Path):
    spec = importlib.util.spec_from_file_location("oval_semantic_ir", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify(folder: Path, importer: Path) -> dict:
    model = load_importer(importer)
    declarations = catalog(folder)
    rows = []
    errors = []
    for scope, types in SCOPES.items():
        declared = model.KNOWN_ATTRIBUTE_DEFAULTS.get(scope, {})
        # The documented var_check fallback is conditional on var_ref and
        # deliberately absent from the schema-derived dictionary.
        for type_name in types:
            attrs, blockers = effective_type_attributes(declarations, NS, type_name)
            actual = {k: (v["value"], "xsd_default")
                      for k, v in attrs.items() if v["kind"] == "default"}
            for k, v in attrs.items():
                if v["kind"] == "fixed":
                    actual[k] = (v["value"], "xsd_fixed")
            missing = sorted(set(actual) - set(declared))
            extra = sorted(set(declared) - set(actual))
            differing = {
                key: {"schema": list(actual[key]), "importer": list(declared[key])}
                for key in set(declared) & set(actual)
                if tuple(declared[key]) != tuple(actual[key])
            }
            row = {
                "scope": scope, "type": type_name,
                "schema_attributes": sorted(actual),
                "missing_from_importer": missing,
                "not_declared_by_schema": extra,
                "different_values": differing,
                "inheritance_blockers": blockers,
            }
            rows.append(row)
            if missing or extra or differing or blockers:
                errors.append(row)
    return {
        "scope": "generic OVAL definition/test/object/state/variable + two state-entity bases",
        "checked_type_count": len(rows),
        "mismatch_count": len(errors),
        "results": rows,
        "mismatches": errors,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--schemas", required=True, type=Path)
    ap.add_argument("--importer", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    args = ap.parse_args()
    report = verify(args.schemas, args.importer)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n",
                           encoding="utf-8")
    print(json.dumps({"checked_type_count": report["checked_type_count"],
                      "mismatch_count": report["mismatch_count"],
                      "mismatches": report["mismatches"]}, indent=2))
    if report["mismatches"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
