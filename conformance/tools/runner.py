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
from jsonschema import Draft202012Validator, ValidationError
from referencing import Registry, Resource
try:
    from .semantic import validate as semantic_validate
except ImportError:  # direct script execution
    from semantic import validate as semantic_validate

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


def schema_validator(name: str) -> Draft202012Validator:
    schema = json.loads((SCHEMA / name).read_text(encoding="utf-8"))
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
    contract = fixture.get("semantic_contract", {})
    if "positive" in variants and "negative" in variants:
        positive_items = variants["positive"].get("items", [])
        negative_items = variants["negative"].get("items", [])
        if positive_items == negative_items and variants["positive"].get("acquisition") == variants["negative"].get("acquisition"):
            errors.append("positive and negative evidence are identical with the same acquisition status")
        strategy = contract.get("negative_strategy")
        if strategy == "field-mismatch":
            field = contract.get("negative_field")
            if len(positive_items) != 1 or len(negative_items) != 1 or not field:
                errors.append("field-mismatch negative must retain exactly one Item")
            else:
                for selector in contract.get("selector_fields", []):
                    if positive_items[0].get("fields", {}).get(selector) != negative_items[0].get("fields", {}).get(selector):
                        errors.append(f"negative changed selector field {selector!r}")
                if positive_items[0].get("fields", {}).get(field) == negative_items[0].get("fields", {}).get(field):
                    errors.append(f"negative did not change comparison field {field!r}")
        elif strategy == "empty-collected-population":
            if positive_items == negative_items or negative_items:
                errors.append("empty-population negative must remove Items while retaining collected acquisition")
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



def check_semantic_witnesses(fixture: dict[str, Any], expected: dict[str, Any], label: str = "fixture") -> list[str]:
    """Ensure a declared semantic witness has a distinct, typed expected result.

    This is deliberately independent of vector labels: the witness names the
    variants and the result that its mapping rule justifies.
    """
    errors: list[str] = []
    semantic_witnesses = fixture.get("semantic_witnesses", [])
    if not semantic_witnesses:
        return errors
    fixture_rules = {w.get("rule") for w in semantic_witnesses}
    expected_rules = {w.get("id") for w in expected.get("semantic_rules", [])}
    if None in fixture_rules or fixture_rules != expected_rules:
        errors.append(f"{label}: semantic witness rules do not match independent expected rules")
    valid_outcomes = {"true", "false", "unknown", "error", "not_applicable", "not_evaluated"}
    for witness in semantic_witnesses:
        if witness.get("expected") not in valid_outcomes:
            errors.append(f"{label}: semantic witness has untyped expected outcome")
        for variant_key in ("positive_variant", "negative_variant"):
            variant_name = witness.get(variant_key)
            if variant_name not in fixture.get("variants", {}):
                errors.append(f"{label}: semantic witness references missing {variant_key}")
            elif expected.get("variants", {}).get(variant_name, {}).get("assessment_outcome") != witness.get("expected"):
                errors.append(f"{label}: semantic witness outcome disagrees with expected {variant_name} result")
    return errors

def family_digest() -> str:
    paths = sorted((*SCHEMA.glob("*.json"), *(SCHEMA / "capability-mappings").rglob("*.json")))
    checksum = hashlib.sha256()
    for path in paths:
        checksum.update(path.relative_to(SCHEMA).as_posix().encode() + b"\0")
        checksum.update(path.read_bytes())
    return checksum.hexdigest()


def suite_index_errors(index: dict[str, Any], schema_commit: str,
                       directory: Path = CONFORMANCE) -> list[str]:
    errors: list[str] = []
    if index.get("schema_commit") != schema_commit:
        errors.append("supplemental suite index uses a different schema pin")
    suite_ids = [suite["id"] for suite in index["suites"]]
    if len(suite_ids) != len(set(suite_ids)):
        errors.append("supplemental suite index contains duplicate IDs")
    root = directory.resolve()
    for suite in index["suites"]:
        digests = suite["artifact_sha256"]
        if suite["entrypoint"] not in digests:
            errors.append(f"{suite['id']}: suite entry point is missing its digest")
        for artifact, expected in digests.items():
            path = (root / artifact).resolve()
            if not path.is_relative_to(root) or not path.is_file():
                errors.append(f"{suite['id']}: missing or out-of-scope artifact {artifact}")
                continue
            if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
                errors.append(f"{suite['id']}: suite artifact digest differs for {artifact}")
    return errors


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
            fixture = load(fixture_path)
            expected = load(expected_path)
            errors.extend(check_semantic_witnesses(fixture, expected, row["fixture"]))
            if expected.get("format") != "scap-ng-conformance-expected-0.1":
                errors.append(f"{row['expected']}: wrong expected-result format")
            if set(expected.get("variants", {})) != set(row["vectors"]):
                errors.append(f"{row['expected']}: expected vectors do not match manifest")
            for vector, assertion in expected.get("variants", {}).items():
                if assertion.get("assessment_outcome") not in {"true", "false", "unknown", "error", "not_applicable", "not_evaluated"}:
                    errors.append(f"{row['expected']}:{vector}: untyped outcome")
                if vector in fixture.get("variants", {}):
                    actual_items = len(fixture["variants"][vector].get("items", []))
                    if assertion.get("items_found") != actual_items:
                        errors.append(f"{row['expected']}:{vector}: items_found does not match fixture")
        except Exception as exc:
            errors.append(f"{row['fixture']} / {row['expected']}: {exc}")
    inventory = load(CONFORMANCE / "schema-coverage.json")
    for row in manifest["core_cases"]:
        assessment = CONFORMANCE / row["assessment"]
        try:
            v.validate(load(assessment))
            expected = load(CONFORMANCE / row["expected"])
            if row["id"] == "core-comparison-operators":
                expected_ops = set(expected.get("operators", {}))
                active_ops = set(inventory["operator_inventory"]["field_predicate_properties"])
                if expected_ops != active_ops:
                    errors.append("comparison operator suite does not cover the active 67-operator surface")
            if row["id"] == "core-selector-alternatives":
                declared = sum(len(c.get("selector_alternatives", [])) for c in inventory["capabilities"])
                if len(expected.get("alternatives", {})) != declared:
                    errors.append("selector suite does not cover every declared selector alternative")
            if row["id"] == "core-cardinalities":
                required = {"item-exactly-one", "item-none", "item-zero-or-more", "field-exactly-one", "field-none", "field-zero-or-more"}
                if set(expected.get("cardinalities", {})) != required:
                    errors.append("cardinality suite is incomplete")
            if row["id"] == "core-approved-decisions":
                fixture = load(CONFORMANCE / row["fixture"])
                expected = load(CONFORMANCE / row["expected"])
                if fixture.get("decision_witnesses") != expected.get("decision_witnesses"):
                    errors.append("approved decision fixture and expected proof differ")
                if not any(w.get("rule") == "variable.value.state_var_ref_guard" and w.get("identity_entailed") is False and w.get("expected") == "not_losslessly_representable" for w in fixture.get("decision_witnesses", [])):
                    errors.append("Variable State-reference decision lacks a concrete nonredundant counterexample")
                if not any(w.get("rule") == "windows.cmdlet.select_no_wildcard" and w.get("wildcard_selection") == "rejected-before-collection" for w in fixture.get("decision_witnesses", [])):
                    errors.append("cmdlet wildcard decision lacks a pre-collection rejection witness")
            if row["id"] == "core-semantic-boundaries":
                fixture = load(CONFORMANCE / row["fixture"])
                witness_rules = {rule for witness in fixture.get("semantic_witnesses", []) for rule in witness.get("rules", [])}
                if witness_rules != set(expected.get("rules", [])):
                    errors.append("semantic boundary expected rules do not match fixture witnesses")
                declared_rules = {rule for mapping in inventory.get("capabilities", []) for rule in mapping.get("semantic_validator_rules", [])}
                if witness_rules - declared_rules:
                    errors.append("semantic boundary contains unknown mapping rule IDs")
                tests = load(assessment).get("assessment", {}).get("tests", {})
                assertions = expected.get("assertions", {})
                declared_rejections = fixture.get("semantic_rejections", {})
                actual_rejections = {
                    error["test"]: error["rule"]
                    for error in semantic_validate(load(assessment))
                }
                if actual_rejections != declared_rejections:
                    errors.append("semantic boundary semantic-validator rejections do not match the independent witness")
                if actual_rejections != expected.get("semantic_rejections", {}):
                    errors.append("semantic boundary expected semantic-validator rejections do not match the fixture")
                for test_name, assertion in assertions.items():
                    evidence = fixture.get("evidence", {}).get(test_name, {})
                    if evidence.get("items_found") != assertion.get("items_found") or evidence.get("items_satisfying") != assertion.get("items_satisfying"):
                        errors.append(f"semantic boundary evidence cardinality disagrees: {test_name}")
                    if assertion.get("outcome") == "true":
                        items = evidence.get("items", [])
                        if len(items) != 1 or evidence.get("status") != "collected":
                            errors.append(f"semantic boundary positive lacks collected Item evidence: {test_name}")
                        for field_value in items[0].get("fields", {}).values() if items else []:
                            if not {"datatype", "value", "status"}.issubset(field_value) or field_value["status"] != "collected":
                                errors.append(f"semantic boundary evidence is not typed: {test_name}")
                    elif evidence.get("status") != "not_run" or evidence.get("items"):
                        errors.append(f"semantic boundary rejected case fabricated collection evidence: {test_name}")
                for witness in fixture.get("semantic_witnesses", []):
                    test_name = witness.get("test")
                    if test_name not in tests:
                        errors.append(f"semantic boundary witness references missing Test: {test_name}")
                    if test_name not in assertions or assertions[test_name].get("outcome") != witness.get("expected"):
                        errors.append(f"semantic boundary witness outcome is not independently recorded: {test_name}")
                if any(assertion.get("outcome") == "error" for assertion in assertions.values()) and not witness_rules:
                    errors.append("semantic boundary suite has ERROR without a rule witness")
        except Exception as exc:
            errors.append(f"{row['assessment']}: {exc.message if hasattr(exc, 'message') else exc}")
    for row in manifest.get("status_cases", []):
        path = CONFORMANCE / row.get("assessment", row.get("case"))
        try:
            schema_validator(row["schema"]).validate(load(path))
            if not (CONFORMANCE / row["expected"]).is_file():
                errors.append(f"{row['id']}: missing expected status/profile oracle")
        except Exception as exc:
            errors.append(f"{row['id']}: {exc.message if hasattr(exc, 'message') else exc}")
    for row in manifest.get("authoring_cases", []):
        try:
            document = load(CONFORMANCE / row["assessment"])
            schema_validator(row["schema"]).validate(document)
            expected = load(CONFORMANCE / row["expected"])
            if expected.get("case_id") != row["id"]:
                errors.append(f"{row['id']}: expected case_id does not match manifest")
            if document.get("assessment", {}).get("id") != row["id"]:
                errors.append(f"{row['id']}: Assessment id does not match manifest")
            if expected.get("mode") != document.get("assessment", {}).get("mode") or expected.get("class") != document.get("assessment", {}).get("class"):
                errors.append(f"{row['id']}: expected authoring enum metadata disagrees with Assessment")
            if not expected.get("reason", "").strip(): errors.append(f"{row['id']}: expected enum reason is empty")
        except Exception as exc:
            errors.append(f"{row['id']}: {exc.message if hasattr(exc, 'message') else exc}")
    for invalid_case in manifest["invalid_cases"]:
        invalid = CONFORMANCE / invalid_case["assessment"]
        try:
            v.validate(load(invalid))
        except ValidationError:
            pass
        except (ValueError, OSError, yaml.YAMLError) as exc:
            errors.append(f"{invalid_case['id']}: could not load invalid-authoring witness: {exc}")
        else:
            errors.append(f"{invalid_case['id']} unexpectedly passed schema validation")
    index = load(CONFORMANCE / manifest["suite_index"])
    errors.extend(suite_index_errors(index, source_commit))
    supplemental = load(CONFORMANCE / manifest["supplemental_manifest"])
    if supplemental["schema_commit"] != manifest["schema_commit"]:
        errors.append("supplemental corpus schema pin differs from the canonical corpus")
    for row in supplemental["cases"]:
        try:
            document = load(CONFORMANCE / row["source"])
            value = next(iter(document.values()))
            if value.get("id", value.get("execution_id")) != row["id"]:
                errors.append(f"{row['id']}: document identity differs from the supplemental manifest")
            actual = schema_validator(row["schema"]).is_valid(document)
            if actual != row["valid"]:
                errors.append(f"{row['id']}: expected schema validity {row['valid']}, got {actual}")
            receipt_paths = row["artifact_sha256"]
            required_paths = {row[key] for key in ("source", "fixture", "expected") if key in row}
            if required_paths - receipt_paths.keys():
                errors.append(f"{row['id']}: supplemental inputs are missing digests")
            for name, expected_sha in receipt_paths.items():
                if hashlib.sha256((CONFORMANCE / name).read_bytes()).hexdigest() != expected_sha:
                    errors.append(f"{row['id']}: stale supplemental artifact digest for {name}")
        except (ValueError, KeyError, OSError, yaml.YAMLError) as exc:
            errors.append(f"{row['id']}: {exc}")
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
    audit = load(CONFORMANCE / "coverage-audit.json")
    print(json.dumps({"schema_commit": inventory["schema_commit"], "capabilities": len(expected), "base_vectors_per_capability": 7, "expanded_capability_vectors_total": audit["vectors"]["expanded_capability_vectors_total"], "missing_capabilities": missing, "schema_validated": not missing, "semantic_complete": audit["schema_branches"]["direct_executable_branch_coverage"]}, indent=2))
    return 1 if missing else 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["validate", "coverage"])
    args = parser.parse_args()
    return validate() if args.command == "validate" else coverage()


if __name__ == "__main__":
    raise SystemExit(main())
