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


def validate_benchmark_organizational_input_links(document: dict) -> list[dict]:
    """Verify Rule-level summaries against authoritative Benchmark registry.

    Run after JSON Schema validation. The input's actual use by a specific
    Assessment invocation is validated separately when Assessment Results
    are available; this guards the published Benchmark/Rule result boundary.
    """
    root = document.get("benchmark_result", {})
    if not isinstance(root, dict):
        return [{"code": "benchmark.invalid", "path": "benchmark_result"}]
    registry = (root.get("effective_policy") or {}).get("organizational_inputs") or {}
    errors = []
    for rule_index, rule in enumerate(root.get("rule_results") or []):
        if not isinstance(rule, dict):
            continue
        seen = set()
        for input_index, entry in enumerate(rule.get("organizational_inputs") or []):
            path = f"rule_results[{rule_index}].organizational_inputs[{input_index}]"
            if not isinstance(entry, dict):
                errors.append({"code":"organizational_input.invalid", "path":path})
                continue
            ref = entry.get("organizational_input_ref")
            if ref in seen:
                errors.append({"code":"organizational_input.duplicate_ref",
                               "path":path+".organizational_input_ref"})
            seen.add(ref)
            canonical = registry.get(ref)
            if canonical is None:
                errors.append({"code":"organizational_input.unknown_ref",
                               "path":path+".organizational_input_ref"})
                continue
            if entry.get("parameter") != canonical.get("parameter"):
                errors.append({"code":"organizational_input.parameter_mismatch",
                               "path":path+".parameter"})
            typed = entry.get("effective_value") or {}
            if canonical.get("redacted") is True:
                if typed.get("redacted") is not True or "value" in typed:
                    errors.append({"code":"organizational_input.redacted_registry_leak",
                                   "path":path+".effective_value"})
            elif "value" in canonical and "value" in typed:
                if typed["value"] != canonical["value"]:
                    errors.append({"code":"organizational_input.value_mismatch",
                                   "path":path+".effective_value.value"})
            authority = entry.get("authority_summary") or {}
            canonical_provenance = canonical.get("provenance") or {}
            for key in ("organization", "authorization_reference"):
                if key in authority and key in canonical_provenance:
                    if authority[key] != canonical_provenance[key]:
                        errors.append({"code":"organizational_input.authority_mismatch",
                                       "path":path+".authority_summary."+key})
    return errors
