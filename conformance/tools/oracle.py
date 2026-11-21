#!/usr/bin/env python3
"""Compare an adapter receipt with the independent expected-result oracle."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ALLOWED = {"true", "false", "unknown", "error", "not_applicable", "not_evaluated"}


def compare(expected: dict[str, Any], receipt: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if receipt.get("format") != "scap-ng-conformance-receipt-0.1":
        errors.append("receipt format is not scap-ng-conformance-receipt-0.1")
    if receipt.get("schema_version") != expected.get("schema_version"):
        errors.append("receipt schema version differs from expected")
    for key in ("assessment_outcome", "test_outcome"):
        if key in receipt and receipt[key] not in ALLOWED:
            errors.append(f"{key} is not a typed canonical outcome")
    expected_variants = expected.get("variants", {})
    variant = receipt.get("variant")
    assertion = expected_variants.get(variant)
    if assertion is None:
        errors.append(f"variant {variant!r} is not present in expected oracle")
        return errors
    for key in ("assessment_outcome", "test_outcome", "items_found", "items_satisfying"):
        if key in assertion and receipt.get(key) != assertion[key]:
            errors.append(f"{key}: expected {assertion[key]!r}, got {receipt.get(key)!r}")
    return errors


def compare_files(expected_path: Path, receipt_path: Path) -> int:
    expected = json.loads(expected_path.read_text())
    receipt = json.loads(receipt_path.read_text())
    errors = compare(expected, receipt)
    if errors:
        raise SystemExit("\n".join(errors))
    return 0
