#!/usr/bin/env python3
"""Check cross-field truthfulness of SCAP-NG 0.3 Assessment Result evidence.

JSON Schema checks structural shapes, but cannot compare per-Test result counts
with retained arrays, Item identities or effective scanner retention limits.
This validator deliberately does NOT re-evaluate the Assessment's logical truth.
"""
from __future__ import annotations


def validate_assessment_result_semantics(document: dict) -> list[dict]:
    """Return deterministic diagnostics for contradictory evidence accounting.

    This supplements (never replaces) the v0.3 Assessment Result JSON Schema.
    Run after structural validation; malformed fields may produce diagnostics.
    """
    a = document.get("assessment_result", {})
    if not isinstance(a, dict):
        return [{"code": "assessment_result.invalid", "path": "assessment_result"}]
    errors = []

    def report(code, path):
        errors.append({"code": code, "path": path})

    policy = a.get("evidence_retention") or {}
    maximum = policy.get("maximum_items") if isinstance(policy, dict) else None
    if isinstance(maximum, bool) or (maximum is not None and
                                     (not isinstance(maximum, int) or maximum < 0)):
        report("retention.invalid_maximum", "evidence_retention.maximum_items")
        maximum = None

    for index, test in enumerate(a.get("tests") or []):
        if not isinstance(test, dict):
            report("test.invalid", f"tests[{index}]")
            continue
        prefix = f"tests[{index}]"
        summary = test.get("item_summary")
        details = test.get("per_item_results") or []
        if not isinstance(summary, dict):
            report("test.missing_item_summary", f"{prefix}.item_summary")
            continue
        if not isinstance(details, list):
            report("test.invalid_per_item_results", f"{prefix}.per_item_results")
            continue

        returned = summary.get("returned_items")
        evaluated = summary.get("evaluated_items")
        observed = summary.get("observed_mismatches")
        actual = summary.get("actual_mismatches")
        if returned != len(details):
            report("test.returned_count_mismatch", f"{prefix}.item_summary.returned_items")
        if maximum is not None and len(details) > maximum:
            report("test.exceeds_retention_limit", f"{prefix}.per_item_results")
        if isinstance(evaluated, int) and not isinstance(evaluated, bool):
            if evaluated < len(details):
                report("test.more_retained_than_evaluated", f"{prefix}.item_summary.evaluated_items")
            if isinstance(observed, int) and not isinstance(observed, bool) and observed > evaluated:
                report("test.more_mismatches_than_evaluated", f"{prefix}.item_summary.observed_mismatches")
            if isinstance(actual, int) and not isinstance(actual, bool) and actual > evaluated:
                report("test.more_actual_mismatches_than_evaluated", f"{prefix}.item_summary.actual_mismatches")
        if (isinstance(actual, int) and not isinstance(actual, bool)
                and isinstance(observed, int) and not isinstance(observed, bool)
                and actual < observed):
            report("test.actual_below_observed", f"{prefix}.item_summary.actual_mismatches")

        referenced = set(test.get("item_refs") or [])
        retained_failures = 0
        for j, entry in enumerate(details):
            if not isinstance(entry, dict):
                report("item.invalid", f"{prefix}.per_item_results[{j}]")
                continue
            item_ref = entry.get("item_ref")
            item = entry.get("item") or {}
            item_id = item.get("id") if isinstance(item, dict) else None
            if item_ref != item_id:
                report("item.identity_mismatch", f"{prefix}.per_item_results[{j}].item")
            if item_ref not in referenced:
                report("item.ref_not_listed", f"{prefix}.per_item_results[{j}].item_ref")
            if entry.get("outcome") == "false":
                retained_failures += 1
        if isinstance(observed, int) and not isinstance(observed, bool):
            if observed < retained_failures:
                report("test.observed_below_retained_failures", f"{prefix}.item_summary.observed_mismatches")
            # A reporting cap is not an evaluation cap. If any observed failing
            # Items were omitted, this Test's detailed evidence is truncated.
            if observed > retained_failures and summary.get("truncated_evidence") is False:
                report("test.omitted_failures_not_marked", f"{prefix}.item_summary.truncated_evidence")

    evidence = a.get("evidence_summary")
    if isinstance(evidence, dict):
        prefix = "evidence_summary"
        observed, actual = evidence.get("observed_failures"), evidence.get("actual_failures")
        maximum_evidence, returned = evidence.get("maximum"), evidence.get("returned")
        if isinstance(returned, int) and isinstance(maximum_evidence, int) and returned > maximum_evidence:
            report("evidence.exceeds_maximum", f"{prefix}.returned")
        if isinstance(observed, int) and isinstance(returned, int) and returned > observed:
            report("evidence.returned_exceeds_observed", f"{prefix}.returned")
        if isinstance(actual, int) and isinstance(observed, int) and actual < observed:
            report("evidence.actual_below_observed", f"{prefix}.actual_failures")
        if (isinstance(observed, int) and isinstance(returned, int)
                and returned < observed and evidence.get("truncated_population") is False):
            report("evidence.omission_not_marked", f"{prefix}.truncated_population")
    return errors
