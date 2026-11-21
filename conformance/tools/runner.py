#!/usr/bin/env python3
"""Offline schema gate and receipt-oriented runner for SCAP-NG conformance.

This runner validates authoring documents and fixture/expected contracts.  It is
not an evaluator and intentionally does not claim RI execution or PASS/FAIL
proof.  An RI adapter can consume the same manifest and compare its receipt with
``expected`` using the adapter contract in CONTRACT.md.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "schema"
CONFORMANCE = ROOT / "conformance"
PREFIX = "https://scap-ng.dev/schema/v0.4.1/"


def load(path: Path) -> Any:
    if path.suffix in {".yaml", ".yml"}:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    return json.loads(path.read_text(encoding="utf-8"))


def registry() -> Registry:
    resources = {}
    for path in sorted(SCHEMA.rglob("*.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        if "$schema" not in doc:
            continue
        resource = Resource.from_contents(doc)
        resources[PREFIX + path.relative_to(SCHEMA).as_posix()] = resource
        if "$id" in doc:
            resources[doc["$id"]] = resource
    return Registry().with_resources(resources.items())


def validator() -> Draft202012Validator:
    schema = json.loads((SCHEMA / "assessment.schema.json").read_text(encoding="utf-8"))
    return Draft202012Validator(schema, registry=registry())


def check_fixture(path: Path) -> list[str]:
    errors: list[str] = []
    fixture = load(path)
    if fixture.get("format") != "scap-ng-conformance-evidence-0.1":
        errors.append("wrong evidence format")
    if fixture.get("schema_version") != "0.4.1":
        errors.append("fixture is not pinned to 0.4.1")
    clock = fixture.get("clock", {})
    if clock != {"now_utc": "2026-01-01T00:00:00Z", "timezone": "UTC", "locale": "C", "ordering": "document"}:
        errors.append("fixture clock/timezone/locale/order is not deterministic")
    variants = fixture.get("variants", {})
    for name, variant in variants.items():
        if "items" in variant and not isinstance(variant["items"], list):
            errors.append(f"variant {name}: items must be an array")
        for item in variant.get("items", []):
            if not isinstance(item, dict) or not item.get("id") or not isinstance(item.get("fields", {}), dict):
                errors.append(f"variant {name}: malformed Item")
            for field, value in item.get("fields", {}).items():
                if not {"datatype", "value", "status"}.issubset(value):
                    errors.append(f"variant {name}: {field} is not a typed field witness")
    return errors


def family_digest() -> str:
    paths = sorted((*SCHEMA.glob("*.json"), *(SCHEMA / "capability-mappings").rglob("*.json")))
    checksum = hashlib.sha256()
    for path in paths:
        checksum.update(path.relative_to(SCHEMA).as_posix().encode() + b"\0")
        checksum.update(path.read_bytes())
    return checksum.hexdigest()


def validate() -> int:
    manifest = load(CONFORMANCE / "manifest.json")
    errors: list[str] = []
    if manifest.get("schema_version") != "0.4.1":
        errors.append("manifest is not pinned to schema version 0.4.1")
    source_commit = manifest.get("schema_commit", "")
    if len(source_commit) != 40:
        errors.append("manifest schema_commit is not an exact Git SHA")
    else:
        source_check = subprocess.run(["git", "cat-file", "-e", f"{source_commit}^{{commit}}"], cwd=ROOT, capture_output=True)
        if source_check.returncode:
            errors.append(f"manifest source commit is unavailable locally: {source_commit}")
    if manifest.get("schema_family_sha256") != family_digest():
        errors.append("manifest schema family digest does not match checked-out schema resources")
    v = validator()
    for row in manifest["capabilities"]:
        assessment = CONFORMANCE / row["assessment"]
        try:
            v.validate(load(assessment))
        except Exception as exc:  # jsonschema.ValidationError has useful paths
            errors.append(f"{assessment.relative_to(ROOT)}: {exc.message if hasattr(exc, 'message') else exc}")
        fixture_path = CONFORMANCE / row["fixture"]
        expected_path = CONFORMANCE / row["expected"]
        try:
            errors.extend(f"{row['fixture']}: {e}" for e in check_fixture(fixture_path))
            for kind, path in (("assessment", assessment), ("fixture", fixture_path), ("expected", expected_path)):
                actual_sha = hashlib.sha256(path.read_bytes()).hexdigest()
                if actual_sha != row["sha256"][kind]:
                    errors.append(f"{row[kind]}: SHA-256 differs from manifest")
            expected = load(expected_path)
            if expected.get("format") != "scap-ng-conformance-expected-0.1":
                errors.append(f"{row['expected']}: wrong expected-result format")
            if set(expected.get("variants", {})) != set(row["vectors"]):
                errors.append(f"{row['expected']}: expected vectors do not match manifest")
            for vector, assertion in expected.get("variants", {}).items():
                if assertion.get("assessment_outcome") not in {"true", "false", "unknown", "error", "not_applicable", "not_evaluated"}:
                    errors.append(f"{row['expected']}:{vector}: untyped outcome")
        except Exception as exc:
            errors.append(f"{row['fixture']} / {row['expected']}: {exc}")
    for row in manifest["core_cases"]:
        assessment = CONFORMANCE / row["assessment"]
        try:
            v.validate(load(assessment))
        except Exception as exc:
            errors.append(f"{row['assessment']}: {exc.message if hasattr(exc, 'message') else exc}")
    for invalid_case in manifest["invalid_cases"]:
        invalid = CONFORMANCE / invalid_case["assessment"]
        try:
            v.validate(load(invalid))
        except Exception:
            pass
        else:
            errors.append(f"{invalid_case['id']} unexpectedly passed schema validation")
    if errors:
        for error in errors:
            print("ERROR", error, file=sys.stderr)
        return 1
    print(f"validated {len(manifest['capabilities'])} capability Assessments and {len(manifest['core_cases'])} core Assessment")
    print("schema-valid only; no scanner execution claim")
    return 0


def coverage() -> int:
    manifest = load(CONFORMANCE / "manifest.json")
    inventory = load(CONFORMANCE / "schema-coverage.json")
    present = {r["capability"] for r in manifest["capabilities"]}
    expected = {r["capability"] for r in inventory["capabilities"]}
    missing = sorted(expected - present)
    print(json.dumps({"schema_commit": inventory["schema_commit"], "capabilities": len(expected), "vectors_per_capability": 7, "missing_capabilities": missing, "schema_validated": not missing}, indent=2))
    return 1 if missing else 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["validate", "coverage"])
    args = parser.parse_args()
    return validate() if args.command == "validate" else coverage()


if __name__ == "__main__":
    raise SystemExit(main())
