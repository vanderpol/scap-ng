#!/usr/bin/env python3
"""Deterministic core SCAP-NG Rule-result messages.

These helpers render concise messages from structured authoritative result data.
They are intentionally non-heuristic and do not replace the machine-readable
reason/evidence fields.
"""
from __future__ import annotations

from typing import Any


def _count(value: Any, name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError(f"{name} must be a non-negative integer")
    return value


def render_core_message(reason: dict[str, Any]) -> str:
    code = reason.get("code")

    if code == "unexpected_existence":
        observed = _count(reason.get("observed_count"), "observed_count")
        noun = "item" if observed == 1 else "items"
        return f"Expected no matching items; observed {observed} matching {noun}."

    if code == "required_item_missing":
        expected = reason.get("requirement") or "required item"
        return f"Required item was not found: {expected}."

    if code == "required_match_missing":
        expected = reason.get("requirement") or "required condition"
        return f"No collected item satisfied the required condition: {expected}."

    if code == "value_mismatch":
        field = reason.get("field") or "value"
        observed = reason.get("observed")
        expected = reason.get("expected")
        if "observed" not in reason or "expected" not in reason:
            raise ValueError("value_mismatch requires observed and expected")
        return f"{field}: observed {observed!r}; expected {expected!r}."

    if code == "cardinality_mismatch":
        observed = _count(reason.get("observed_count"), "observed_count")
        expected = reason.get("expected")
        if expected is None:
            raise ValueError("cardinality_mismatch requires expected")
        return f"Observed {observed} matching items; expected cardinality {expected}."

    if code == "collection_error":
        capability = reason.get("capability")
        if capability:
            return f"Collection failed for capability {capability}."
        return "Collection failed before the requirement could be evaluated."

    if code == "missing_organizational_input":
        name = reason.get("input") or "required organizational input"
        return f"Required organizational input is missing: {name}."

    if code == "invalid_organizational_input":
        name = reason.get("input") or "organizational input"
        return f"Organizational input is invalid: {name}."

    if code == "unsupported_organizational_input":
        name = reason.get("input")
        if name:
            return f"Scanner does not support required organizational input: {name}."
        return "Scanner does not support required organizational input."

    raise ValueError(f"unsupported core reason code: {code!r}")
