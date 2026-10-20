#!/usr/bin/env python3
"""Source-gated second pass for 0.4.0 direct Filter authoring (#248).

Migrates ONLY Test-local identity Unions for which a SHA-pinned source OVAL
Test has ONE object_ref leading to an original direct-Filter Object without a
Set, with identical ordered Filter actions. Parent Object titles must agree
with leaf titles. Genuine OVAL Sets, shared Objects and Variable acquisitions
stay untouched. Exact inverse proves lossless authoring source representation,
not full scanner equivalence.

The passed provenance report must be freshly rebuilt from all six immutable
OVAL sources and the unmodified first-pass 0.4.0 candidate.
"""
from __future__ import annotations

from collections import Counter
from copy import deepcopy


STATUS = "TEST_REFERENCES_ORIGINAL_DIRECT_FILTER"
EXPECTED_DIRECT_TESTS = 19
EXPECTED_BASELINE_SINGLETONS = 50


def canonical_path(name):
    if not name.startswith("authoring/") or not name.endswith((".json", ".yaml")):
        raise ValueError("Unexpected 0.4.0 authoring path: " + repr(name))
    return name.rsplit(".", 1)[0] + ".json"


def _site_key(row):
    route = row["site"]
    if (len(route) != 5 or route[:2] != ["assessment", "tests"]
            or route[3:] != ["object", "set"] or route[2] != row["test"]):
        raise ValueError("Source-proven Test Filter cannot be rewritten outside a Test-local Object")
    return canonical_path(row["path"]), route[2]


def index_source_proof(report, *, assert_six=False):
    if report.get("status") != "SOURCE_COMMENT_TRIAGE_NOT_SOURCE_IDENTITY_OR_SCANNER_PARITY":
        raise ValueError("Unrecognized original OVAL singleton triage report")
    if report.get("rewrites_authorized") is not False or report.get("scanner_semantics_verified") is not False:
        raise ValueError("Original OVAL triage must not claim scanner parity or bulk rewrite")
    if len(report.get("original_oval_source_zip_sha256") or {}) != 6:
        raise ValueError("Six independent immutable source OVAL ZIPs are required")
    rows = report.get("items")
    if not isinstance(rows, list):
        raise ValueError("Missing source-linked singleton ledger")
    if assert_six and (len(rows) != EXPECTED_BASELINE_SINGLETONS or
                       report.get("singleton_set_occurrences") != EXPECTED_BASELINE_SINGLETONS):
        raise ValueError("Pinned remaining-singleton-Set baseline changed")
    selected = {}
    allsites = set()
    for row in rows:
        route = row.get("site", [])
        if (not isinstance(route, list) or not route or route[-1] != "set"
                or not isinstance(row.get("path"), str)):
            raise ValueError("Invalid original OVAL provenance site")
        unique_site = (canonical_path(row["path"]), tuple(route))
        if unique_site in allsites:
            raise ValueError("Duplicate original OVAL provenance site")
        allsites.add(unique_site)
        if row.get("source_test_linked_object_status") != STATUS:
            continue
        key = _site_key(row)
        if key in selected:
            raise ValueError("Duplicate Test-local original OVAL source mapping")
        if (row.get("source_test_linkage") != "UNIQUE_OVAL_TEST_OBJECT_REF"
                or len(row.get("source_test_object_refs", [])) != 1):
            raise ValueError(f"{key}: ambiguous source Test-to-Object identity")
        linked = row.get("source_test_linked_object_candidates")
        if not isinstance(linked, list) or not linked:
            raise ValueError(f"{key}: missing original OVAL Test Object")
        if any(x.get("source_id") != row["source_test_object_refs"][0]
               or x.get("source_has_set") is not False
               for x in linked):
            raise ValueError(f"{key}: mismatched original OVAL Object or Set")
        shapes = {x.get("source_structure_sha256") for x in linked}
        if len(shapes) != 1 or not next(iter(shapes)):
            raise ValueError(f"{key}: divergent original OVAL XML")
        if (not isinstance(row.get("filter_actions"), list)
                or not row["filter_actions"]
                or any(x.get("source_direct_filter_actions") != row["filter_actions"]
                       for x in linked)
                or any(a not in ("include", "exclude") for a in row["filter_actions"])):
            raise ValueError(f"{key}: original OVAL direct Filter sequence differs")
        if row.get("operator") != "union":
            raise ValueError(f"{key}: identity Set operator is not UNION")
        selected[key] = row
    if assert_six and len(selected) != EXPECTED_DIRECT_TESTS:
        raise ValueError(f"Original source Filter migration population changed: {len(selected)}")
    return selected


def expected_direct(test, row):
    obj = test.get("object")
    if not isinstance(obj, dict) or set(obj) not in ({"set"}, {"object_title", "set"}):
        raise ValueError("Only identity Set wrapper at Test-level Object can be simplified")
    expr = obj["set"]
    if not isinstance(expr, dict) or set(expr) != {"operator", "operands"} or expr["operator"] != "union":
        raise ValueError("Unsupported or real OVAL Set expression")
    op = expr["operands"]
    if not isinstance(op, list) or len(op) != 1 or set(op[0]) != {"object", "filters"}:
        raise ValueError("Not a single leaf Object Filter Set")
    member = op[0]
    child = member["object"]
    actions = member["filters"]
    if (not isinstance(child, dict) or "set" in child or "filters" in child
            or not isinstance(actions, list) or not actions
            or [next(iter(f)) if isinstance(f, dict) and len(f) == 1 else None
                for f in actions] != row["filter_actions"]):
        raise ValueError("Original Filter predicates or Set shape changed")
    if obj.get("object_title") != child.get("object_title"):
        raise ValueError("Outer and inner Object title differ; require source review")
    if child.get("capability") != test.get("capability") or child.get("capability") != row.get("leaf_capability"):
        raise ValueError("Source Object capability differs from consuming Test")
    if row.get("test_capability") != test.get("capability"):
        raise ValueError("OVAL source provenance Test capability differs")
    lowered = deepcopy(child)
    lowered.pop("capability")
    lowered["filters"] = deepcopy(actions)
    return lowered


def migrate(doc, path, proof):
    result = deepcopy(doc)
    counts = Counter()
    a = result.get("assessment")
    if not isinstance(a, dict) or a.get("mode") != "automated":
        return result, counts
    for tid, test in (a.get("tests") or {}).items():
        row = proof.get((canonical_path(path), tid))
        if row is None:
            continue
        if a.get("id") != row.get("assessment") or test.get("test_title") != row.get("test_title"):
            raise ValueError("Original OVAL Test provenance identity changed")
        test["object"] = expected_direct(test, row)
        counts["source_linked_additional_direct_filters"] += 1
    return result, counts


def recover_migration(candidate, prior, path, proof):
    restored = deepcopy(candidate)
    a = prior.get("assessment")
    if isinstance(a, dict) and a.get("mode") == "automated":
        for tid, test in (a.get("tests") or {}).items():
            row = proof.get((canonical_path(path), tid))
            if row is None:
                continue
            actual = restored["assessment"]["tests"][tid]
            if actual.get("object") != expected_direct(test, row):
                raise ValueError(f"{path}/{tid}: original OVAL Filter authoring inverse mismatched")
            actual["object"] = deepcopy(test["object"])
    if restored != prior:
        raise ValueError(f"{path}: original Test, Object or Filter source AST mutated")
    return True
