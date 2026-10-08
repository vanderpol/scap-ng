#!/usr/bin/env python3
"""Check cross-field truthfulness of embedded SCAP-NG 0.3 Rule findings.

Run after JSON Schema validation. This checks instance binding, bounded
population summaries and obvious fabricated values; it is not a reference
scanner or an independent source of assessment truth.
"""
from __future__ import annotations


def validate_rule_result_semantics(rule: dict) -> list[dict]:
    errors = []

    def report(code: str, path: str):
        errors.append({"code": code, "path": path})

    if not isinstance(rule, dict):
        return [{"code": "rule.invalid", "path": "rule"}]

    raw_instances = rule.get("instances", [])
    instances = {entry["id"]: entry for entry in raw_instances
                 if isinstance(entry, dict) and isinstance(entry.get("id"), str)}
    if len(instances) != len(raw_instances):
        report("rule.duplicate_or_invalid_instance", "instances")

    reported_ids = set()
    for index, finding in enumerate(rule.get("findings", [])):
        path = f"findings[{index}]"
        if finding["instance_id"] not in instances:
            report("finding.unbound_instance", f"{path}.instance_id")
        if finding["kind"] == "comparison":
            observed = finding["observed"]
            expected = finding["expected"]
            for name, value in (("observed", observed), ("expected", expected)):
                if value.get("redacted") and "value" in value:
                    report("finding.redacted_value_leak", f"{path}.{name}")
                if value["status"] != "exists" and "value" in value:
                    report("finding.fabricated_value", f"{path}.{name}")
            if "item_ref" in finding:
                reported_ids.add((finding["instance_id"], finding["item_ref"]))
        elif finding["kind"] == "missing" and "item_ref" in finding:
            report("finding.fabricated_missing_item", f"{path}.item_ref")

    counts = rule.get("finding_counts")
    if counts is not None:
        evaluated = counts["evaluated_items"]
        observed = counts["observed_violations"]
        actual = counts["actual_violations"]
        retained = counts["reported_items"]
        if observed > evaluated:
            report("counts.observed_exceeds_evaluated", "finding_counts.observed_violations")
        if actual != "unknown" and (actual < observed or actual > evaluated):
            report("counts.invalid_actual_total", "finding_counts.actual_violations")
        if not counts["population_complete"] and actual != "unknown":
            report("counts.incomplete_claims_exact_total", "finding_counts.actual_violations")
        if retained != len(reported_ids):
            report("counts.retained_mismatch", "finding_counts.reported_items")
        if retained > evaluated:
            report("counts.retained_exceeds_evaluated", "finding_counts.reported_items")
        if observed > retained and not counts["sample_truncated"]:
            report("counts.omission_not_marked", "finding_counts.sample_truncated")
    return errors
