#!/usr/bin/env python3
"""Strict comparison of scanner-neutral receipts with the issue #87 oracle.

This module validates receipt identity and provenance before comparing any
outcome. It is deliberately independent of RI implementation code.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

ALLOWED = {"true", "false", "unknown", "error", "not_applicable", "not_evaluated"}
RECEIPT_FORMAT = "scap-ng-conformance-receipt-0.1"
EXPECTED_FORMAT = "scap-ng-conformance-expected-0.1"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _typed_outcome(value: Any, where: str, errors: list[str]) -> None:
    if value not in ALLOWED:
        errors.append(f"{where} is not a typed canonical outcome")


def _expected_reason(expected: dict[str, Any], assertion: dict[str, Any]) -> str | None:
    return assertion.get("reason") or expected.get("reason")


def _check_evidence(receipt: dict[str, Any], fixture: dict[str, Any], variant: str, errors: list[str]) -> None:
    evidence = receipt.get("evidence")
    if not isinstance(evidence, list):
        errors.append("evidence must be an array")
        return
    items = fixture.get("variants", {}).get(variant, {}).get("items", [])
    by_id = {item.get("id"): item for item in items if isinstance(item, dict)}
    seen: set[tuple[Any, Any]] = set()
    for index, witness in enumerate(evidence):
        if not isinstance(witness, dict):
            errors.append(f"evidence[{index}] is not an object")
            continue
        required = {"item_id", "field", "datatype", "status", "value"}
        missing = required - set(witness)
        if missing:
            errors.append(f"evidence[{index}] missing {sorted(missing)}")
            continue
        item = by_id.get(witness["item_id"])
        if item is None:
            errors.append(f"evidence[{index}] references an Item outside the fixture")
            continue
        field = witness["field"]
        if field is None:
            if witness["datatype"] != "record" or witness["value"] != item.get("fields", {}):
                errors.append(f"evidence[{index}] item-level witness is not a typed record")
            expected_status = item.get("status")
            key = (witness["item_id"], None)
        else:
            field_value = item.get("fields", {}).get(field)
            if field_value is None:
                errors.append(f"evidence[{index}] references an absent field")
                continue
            for key_name in ("datatype", "status", "value"):
                if witness[key_name] != field_value.get(key_name):
                    errors.append(f"evidence[{index}] {key_name} disagrees with fixture")
            expected_status = field_value.get("status")
            key = (witness["item_id"], field)
        if expected_status != witness["status"]:
            errors.append(f"evidence[{index}] status disagrees with fixture")
        if key in seen:
            errors.append(f"duplicate evidence witness {key!r}")
        seen.add(key)
    expected_keys = set()
    for item in items:
        if not item.get("fields"):
            expected_keys.add((item.get("id"), None))
        else:
            expected_keys.update((item.get("id"), field) for field in item["fields"])
    if seen != expected_keys:
        errors.append(f"evidence does not exactly cover fixture witnesses: expected {sorted(expected_keys)!r}, got {sorted(seen)!r}")


def compare(
    expected: dict[str, Any],
    receipt: dict[str, Any],
    *,
    manifest: dict[str, Any] | None = None,
    fixture: dict[str, Any] | None = None,
    fixture_sha256: str | None = None,
    expected_sha256: str | None = None,
    test_names: Iterable[str] | None = None,
) -> list[str]:
    """Return all receipt/oracle mismatches; an empty list means accepted.

    ``manifest``, fixture bytes, and test names are required for production
    adapter comparisons. Keeping them keyword-only makes incomplete test calls
    fail closed instead of silently accepting a weak receipt.
    """
    errors: list[str] = []
    if expected.get("format") != EXPECTED_FORMAT:
        errors.append("expected document has the wrong format")
    required_context = {manifest is not None, fixture is not None, fixture_sha256 is not None, expected_sha256 is not None, test_names is not None}
    if required_context != {True}:
        errors.append("manifest, fixture, fixture_sha256, expected_sha256, and test_names are required")
        return errors
    assert manifest is not None and fixture is not None and fixture_sha256 is not None and expected_sha256 is not None and test_names is not None
    test_names = list(test_names)
    required_receipt = {"format", "schema_version", "schema_commit", "case_id", "variant", "fixture_sha256", "expected_sha256", "assessment_outcome", "test_outcomes", "decisive_reason", "evidence", "provenance"}
    missing = required_receipt - set(receipt)
    if missing:
        errors.append(f"receipt missing required fields: {sorted(missing)}")
    if receipt.get("format") != RECEIPT_FORMAT:
        errors.append(f"receipt format must be {RECEIPT_FORMAT}")
    if receipt.get("schema_version") != manifest.get("schema_version") or receipt.get("schema_version") != expected.get("schema_version"):
        errors.append("receipt schema_version does not match manifest and expected oracle")
    if receipt.get("schema_commit") != manifest.get("schema_commit"):
        errors.append("receipt schema_commit does not match the pinned manifest")
    if receipt.get("case_id") != expected.get("case_id"):
        errors.append("receipt case_id does not match expected case")
    if receipt.get("fixture_sha256") != fixture_sha256:
        errors.append("receipt fixture_sha256 does not match fixture bytes")
    if receipt.get("expected_sha256") != expected_sha256:
        errors.append("receipt expected_sha256 does not match expected bytes")
    variant = receipt.get("variant")
    assertion = expected.get("variants", {}).get(variant)
    if assertion is None:
        errors.append(f"receipt variant {variant!r} is not present in expected oracle")
        return errors
    _typed_outcome(receipt.get("assessment_outcome"), "assessment_outcome", errors)
    test_outcomes = receipt.get("test_outcomes")
    if not isinstance(test_outcomes, dict):
        errors.append("test_outcomes must be an object")
        test_outcomes = {}
    if set(test_outcomes) != set(test_names):
        errors.append("test_outcomes keys do not exactly match Assessment Tests")
    for name in test_names:
        if name in test_outcomes:
            _typed_outcome(test_outcomes[name], f"test_outcomes[{name!r}]", errors)
            if test_outcomes[name] != assertion.get("test_outcome"):
                errors.append(f"test_outcomes[{name!r}] does not match expected test outcome")
    if "test_outcome" in receipt:
        _typed_outcome(receipt["test_outcome"], "test_outcome", errors)
        if receipt["test_outcome"] != assertion.get("test_outcome"):
            errors.append("test_outcome does not match expected test outcome")
    if receipt.get("assessment_outcome") != assertion.get("assessment_outcome"):
        errors.append("assessment_outcome does not match expected outcome")
    for key in ("items_found", "items_satisfying"):
        if key in assertion:
            if key not in receipt:
                errors.append(f"receipt missing {key}")
            elif receipt[key] != assertion[key]:
                errors.append(f"{key}: expected {assertion[key]!r}, got {receipt[key]!r}")
    reason = _expected_reason(expected, assertion)
    if not _nonempty(receipt.get("decisive_reason")):
        errors.append("decisive_reason must be non-empty")
    elif reason is not None and receipt["decisive_reason"] != reason:
        errors.append("decisive_reason does not match the independent oracle explanation")
    provenance = receipt.get("provenance")
    if not isinstance(provenance, dict):
        errors.append("provenance must be an object")
    else:
        required_provenance = {"source", "fixture_variant", "fixture_sha256", "expected_sha256", "schema_commit"}
        missing_provenance = required_provenance - set(provenance)
        if missing_provenance:
            errors.append(f"provenance missing required fields: {sorted(missing_provenance)}")
        if provenance.get("source") != "deterministic-fixture":
            errors.append("provenance.source must be deterministic-fixture")
        if provenance.get("fixture_variant") != variant:
            errors.append("provenance.fixture_variant does not match receipt variant")
        if provenance.get("fixture_sha256") != fixture_sha256 or provenance.get("expected_sha256") != expected_sha256:
            errors.append("provenance hashes do not match receipt identity")
        if provenance.get("schema_commit") != manifest.get("schema_commit"):
            errors.append("provenance schema_commit does not match manifest")
    _check_evidence(receipt, fixture, variant, errors)
    return errors


def compare_files(expected_path: Path, receipt_path: Path, *, manifest_path: Path | None = None) -> int:
    """Compare a receipt using its manifest row and sibling fixture."""
    expected = json.loads(expected_path.read_text(encoding="utf-8"))
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if manifest_path is None:
        manifest_path = expected_path.parents[1] / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    conformance = manifest_path.parent
    relative = expected_path.relative_to(conformance).as_posix()
    row = next((row for row in manifest.get("capabilities", []) if row.get("expected") == relative), None)
    if row is None:
        raise SystemExit(f"no capability manifest row for {relative}")
    fixture_path = conformance / row["fixture"]
    assessment_path = conformance / row["assessment"]
    import yaml
    assessment = yaml.safe_load(assessment_path.read_text(encoding="utf-8"))
    test_names = assessment["assessment"]["tests"].keys()
    errors = compare(expected, receipt, manifest=manifest, fixture=json.loads(fixture_path.read_text(encoding="utf-8")), fixture_sha256=_sha256(fixture_path), expected_sha256=_sha256(expected_path), test_names=test_names)
    if errors:
        raise SystemExit("\n".join(errors))
    return 0
