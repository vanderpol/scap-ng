#!/usr/bin/env python3
"""#235 B research: normalize externally captured Windows registry evidence.

Pure, offline adapter; it DOES NOT read Windows registry, attest snapshot
completeness, implement original OVAL registry Item semantics, or prove parity.
It makes query identity, WOW64 view, numeric kind, unsupported types and
partial/error observations explicit before native B fixture evaluation.
"""
from __future__ import annotations

PROVIDER = "windows.registry_value"
VERSION = "snapshot-normalizer-0.1-research"
VIEWS = {"32bit", "64bit"}
NUMERIC_KINDS = {"REG_DWORD": 0xffffffff, "REG_QWORD": 0xffffffffffffffff}
STATUSES = {"complete", "incomplete", "error", "not collected", "not applicable"}


def _bad(using, reason):
    return {"provider": PROVIDER, "version": VERSION, "using": using,
            "status": "error", "items": [], "diagnostics": [{"reason": reason}]}


def normalize(snapshot, *, hive, key, name, view):
    """Normalize a fully identified *external* registry-query snapshot.

    snapshot: {"status": ..., "query": exact using mapping,
               "records": [{"value_kind": "REG_DWORD", "raw_value": 0}, ...]}
    A complete zero-record snapshot means observed absence *only if* the
    external collector has independently established completeness. No
    missing-key or type coercion is inferred here.
    """
    using = {"hive": hive, "key": key, "name": name, "view": view}
    if hive != "HKLM" or not all(isinstance(x, str) and x for x in (key, name)) or not isinstance(view, str) or view not in VIEWS:
        raise ValueError("registry query requires HKLM, nonempty key/name and an explicit WOW64 view")
    if not isinstance(snapshot, dict):
        return _bad(using, "snapshot_not_a_mapping")
    if set(snapshot) != {"status", "query", "records"}:
        return _bad(using, "missing_or_unexpected_snapshot_fields")
    if snapshot["query"] != using:
        return _bad(using, "wrong_registry_acquisition_identity")
    if not isinstance(snapshot["status"], str) or snapshot["status"] not in STATUSES or not isinstance(snapshot["records"], list):
        return _bad(using, "unknown_collection_status_or_record_shape")
    status = snapshot["status"]
    if status in {"error", "not collected", "not applicable"}:
        if snapshot["records"]:
            return _bad(using, "terminal_collection_status_with_unverified_items")
        return {"provider": PROVIDER, "version": VERSION, "using": using,
                "status": status, "items": [], "diagnostics": []}
    items = []
    diagnostics = []
    for i, record in enumerate(snapshot["records"]):
        if not isinstance(record, dict) or set(record) != {"value_kind", "raw_value"}:
            return _bad(using, "malformed_registry_record")
        kind, raw = record["value_kind"], record["raw_value"]
        if not isinstance(kind, str) or not kind:
            return _bad(using, "missing_registry_value_kind")
        # Unsupported types remain visible, not cast or treated as absent.
        maximum = NUMERIC_KINDS.get(kind)
        if maximum is not None and type(raw) is int and 0 <= raw <= maximum:
            value = raw
        else:
            value = {"field_status": "error"}
            diagnostics.append({"reason": "unsupported_or_invalid_registry_value_type",
                                "index": i, "value_kind": kind})
        items.append({"id": f"registry:{hive}:{view}:{key}:{name}:record:{i}",
                      "fields": {"name": name, "value": value,
                                 "value_kind": kind}})
    return {"provider": PROVIDER, "version": VERSION, "using": using,
            "status": status, "items": items, "diagnostics": diagnostics}
