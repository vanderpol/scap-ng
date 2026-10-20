#!/usr/bin/env python3
"""Source-gated 0.4.0 authoring migration for filtered leaf Objects (#248).

Only an exact structural wrapper whose original, pinned OVAL Object has a
unique direct Filter and no Set may be presented as Object-local filters.
Eight currently ambiguous cases stay unchanged. The inverse proves source
authoring graph identity, not scanner execution or six-state runtime parity.
"""
from __future__ import annotations

from collections import Counter
from copy import deepcopy

from audit_v04_synthetic_filter_unions import candidate


STATUS = "UNIQUE_DIRECT_OVAL_FILTER_NO_SET"
PENDING = "SOURCE_REVIEW_REQUIRED"


def canonical_path(path):
    if not path.startswith("authoring/") or not path.endswith((".yaml", ".json")):
        raise ValueError("Invalid Filter migration authoring path: " + repr(path))
    return path.rsplit(".", 1)[0] + ".json"


def index_provenance(report, *, assert_six=False):
    if report.get("status") != "STRUCTURAL_SOURCE_FILTER_AUDIT_NOT_RUNTIME_PARITY":
        raise ValueError("Unverified original OVAL Filter classification report")
    if report.get("scanner_semantics_verified") is not False:
        raise ValueError("Do not represent structural Filter proof as scanner parity")
    if len(report.get("source_archive_checksums") or {}) != 6:
        raise ValueError("All six original pinned source archives are required")
    entries = report.get("entries")
    if not isinstance(entries, list) or not entries:
        raise ValueError("Original OVAL classification ledger is missing")
    indexed = {}
    counts = Counter()
    for row in entries:
        status = row.get("status")
        if status not in (STATUS, PENDING):
            raise ValueError("Unrecognized original OVAL Filter classification")
        key = (canonical_path(row["path"]), row["test_id"])
        if key in indexed:
            raise ValueError("Duplicate source Filter classification for " + repr(key))
        if status == STATUS:
            originals = row.get("source_candidates")
            if (row.get("source_direct_filter_without_set_confirmed") is not True
                    or not isinstance(originals, list) or len(originals) != 1
                    or originals[0].get("source_has_set") is not False
                    or not originals[0].get("id")
                    or originals[0].get("direct_filter_actions") is None):
                raise ValueError("Unverified unique source Filter: " + repr(key))
        indexed[key] = row
        counts[status] += 1
    if assert_six and (len(entries), counts[STATUS], counts[PENDING]) != (36, 28, 8):
        raise ValueError("Pinned original OVAL Filter classification baseline changed")
    return indexed


def expected_direct(original_test, row):
    wrapper = original_test.get("object")
    found = candidate(wrapper)
    if found is None:
        raise ValueError("Proven Filter site is no longer the original wrapper")
    if found["object"].get("object_title") != row.get("source_title"):
        raise ValueError("Original OVAL Object title provenance changed")
    actions = [next(iter(item)) for item in found["filters"]]
    original = row["source_candidates"][0]
    if actions != original["direct_filter_actions"]:
        raise ValueError("Original OVAL Filter action or ordering changed")
    inner = deepcopy(found["object"])
    capability = inner.pop("capability", None)
    if capability != original_test.get("capability"):
        raise ValueError("Cannot inherit a different original Object capability")
    inner["filters"] = deepcopy(found["filters"])
    return inner


def migrate(doc, path, proof):
    """Return (candidate, stats); never mutate or drop an unsupported graph."""
    result = deepcopy(doc)
    a = result.get("assessment")
    counts = Counter()
    if not isinstance(a, dict) or a.get("mode") != "automated":
        return result, counts
    for test_id, test in (a.get("tests") or {}).items():
        row = proof.get((canonical_path(path), test_id))
        if row is None:
            continue
        if a.get("id") != row.get("assessment") or test.get("capability") != row.get("capability"):
            raise ValueError(f"{path} / {test_id}: original Test identity/capability mismatch")
        if row["status"] == PENDING:
            if candidate(test.get("object")) is None:
                raise ValueError(f"{path} / {test_id}: unresolved original Set/Filter shape changed")
            counts["source_review_required_unchanged"] += 1
            continue
        test["object"] = expected_direct(test, row)
        counts["source_proven_direct_filters"] += 1
    return result, counts


def recover_migration(migrated, promoted, path, proof):
    """Reconstitute exactly the pre-migration canonical document or fail."""
    restored = deepcopy(migrated)
    before = promoted.get("assessment")
    after = restored.get("assessment")
    if isinstance(before, dict) and before.get("mode") == "automated":
        for test_id, orig in (before.get("tests") or {}).items():
            row = proof.get((canonical_path(path), test_id))
            if row is None or row["status"] != STATUS:
                continue
            actual = after["tests"][test_id]["object"]
            if actual != expected_direct(orig, row):
                raise ValueError(f"{path} / {test_id}: direct Filter rewrite is not reversible")
            after["tests"][test_id]["object"] = deepcopy(orig["object"])
    if restored != promoted:
        raise ValueError(f"{path}: lossless source Filter reverse mapping failed")
    return True
