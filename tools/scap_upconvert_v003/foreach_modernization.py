#!/usr/bin/env python3
"""Fail-closed SCAP-NG 0.3.0 foreach v1 modernization.

This module operates only on faithful, OVAL-aligned, capability-mapped native
Assessments.  It removes a one-use local Variable only when the exact reviewed
collection-expansion proof class is present.  It never changes 0.2.0 content and
is not enabled automatically by the converter.
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import re

from capability_registry import load_mapping

REWRITE_ID = "foreach.direct-object-component.at-least-one.v1"
TARGET_VERSION = "0.3.0"
_BINDING_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]*$")


def _walk_variable_refs(value, variable_id, path=()):
    """Yield paths to exact native Variable references."""
    if isinstance(value, dict):
        if set(value) == {"variable"} and value.get("variable") == variable_id:
            yield path
        for key, child in value.items():
            yield from _walk_variable_refs(child, variable_id, path + (key,))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk_variable_refs(child, variable_id, path + (index,))


def _all_variable_refs(value, path=()):
    """Yield (variable_id, path) for all exact native Variable references."""
    if isinstance(value, dict):
        if (
            set(value) == {"variable"}
            and isinstance(value.get("variable"), str)
            and value["variable"]
        ):
            yield value["variable"], path
        for key, child in value.items():
            yield from _all_variable_refs(child, path + (key,))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _all_variable_refs(child, path + (index,))


def _binding_alias(source_object):
    capability = source_object.get("capability")
    if capability == "unix.password":
        return "user"
    if capability == "independent.textfilecontent54":
        return "match"
    if capability == "unix.shadow":
        return "shadow_entry"
    return "item"


def _field_contract(capability, field, *, selector):
    mapping = load_mapping(capability, TARGET_VERSION)
    native = mapping.get("native") or {}
    if selector:
        if field not in set((native.get("selector_map") or {}).values()):
            return None
        native_field = field
    else:
        native_field = (
            (native.get("state_field_map") or {}).get(field)
            or (native.get("item_only_field_map") or {}).get(field)
            or field
        )
    datatypes = set((native.get("field_datatypes") or {}).get(native_field, []))
    if not datatypes:
        return None
    return {
        "capability": capability,
        "field": native_field,
        "datatypes": sorted(datatypes),
    }


def _direct_projection(variable):
    if not isinstance(variable, dict) or variable.get("kind") != "local":
        return None
    expression = variable.get("expression")
    if not isinstance(expression, dict) or set(expression) != {"values"}:
        return None
    values = expression.get("values")
    if (
        not isinstance(values, dict)
        or set(values) != {"object", "field"}
        or not isinstance(values.get("object"), str)
        or not values["object"]
        or not isinstance(values.get("field"), str)
        or not values["field"]
    ):
        return None
    return {
        "source_object": values["object"],
        "source_field": values["field"],
    }


def _candidate(document, variable_id):
    assessment = document.get("assessment", document)
    variables = assessment.get("variables") or {}
    objects = assessment.get("objects") or {}
    tests = assessment.get("tests") or {}
    variable = variables.get(variable_id)
    projection = _direct_projection(variable)
    if projection is None:
        return None, ["not_direct_object_component_projection"]

    reasons = []
    source_id = projection["source_object"]
    source = objects.get(source_id)
    if not isinstance(source, dict):
        reasons.append("source_object_missing")
        return None, reasons

    # References outside the defining Variable must reduce to exactly one target
    # Object selector value.
    search_surface = {
        "objects": objects,
        "states": assessment.get("states") or {},
        "tests": tests,
        "evaluate": assessment.get("evaluate"),
        "variables": {
            key: value
            for key, value in variables.items()
            if key != variable_id
        },
    }
    refs = list(_walk_variable_refs(search_surface, variable_id))
    if len(refs) != 1:
        reasons.append("single_target_consumer_required")
        return None, reasons
    path = refs[0]
    if (
        len(path) != 5
        or path[0] != "objects"
        or path[2] != "select"
        or path[4] != "value"
    ):
        reasons.append("consumer_must_be_object_selector")
        return None, reasons

    target_id = path[1]
    target_field = path[3]
    target = objects.get(target_id)
    if not isinstance(target, dict):
        reasons.append("target_object_missing")
        return None, reasons
    if target_id == source_id:
        reasons.append("source_target_must_be_distinct")
        return None, reasons

    select = target.get("select")
    predicate = select.get(target_field) if isinstance(select, dict) else None
    if not isinstance(predicate, dict):
        reasons.append("target_selector_missing")
        return None, reasons
    allowed = {"value", "operation", "datatype", "variable_match"}
    if set(predicate) != allowed:
        reasons.append("target_selector_has_unproven_semantics")
    if predicate.get("value") != {"variable": variable_id}:
        reasons.append("target_selector_variable_mismatch")
    if predicate.get("operation") != "equal":
        reasons.append("target_operation_not_equal")
    if predicate.get("variable_match") != "any":
        reasons.append("target_variable_match_not_any")

    # v1 excludes any second Variable-fed selector/collector input on the target.
    target_refs = list(_all_variable_refs(target))
    if target_refs != [(variable_id, ("select", target_field, "value"))]:
        reasons.append("independent_additional_variable_selector")

    direct_tests = [
        test_id
        for test_id, test in tests.items()
        if isinstance(test, dict) and test.get("object") == target_id
    ]
    if not direct_tests:
        reasons.append("target_not_directly_tested")

    variable_datatype = variable.get("datatype")
    source_contract = None
    target_contract = None
    compatible = []
    try:
        source_contract = _field_contract(
            source.get("capability"),
            projection["source_field"],
            selector=False,
        )
        target_contract = _field_contract(
            target.get("capability"),
            target_field,
            selector=True,
        )
    except ValueError:
        reasons.append("capability_mapping_missing")
    if source_contract is None:
        reasons.append("source_field_contract_missing")
    if target_contract is None:
        reasons.append("target_selector_contract_missing")
    if source_contract and target_contract:
        compatible = sorted(
            set(source_contract["datatypes"]) & set(target_contract["datatypes"])
        )
        if len(compatible) != 1:
            reasons.append("exactly_one_compatible_datatype_required")
        else:
            datatype = compatible[0]
            if predicate.get("datatype") != datatype:
                reasons.append("target_datatype_mismatch")
            if variable_datatype != datatype:
                reasons.append("variable_datatype_mismatch")

    if reasons:
        return None, reasons

    return {
        "variable": variable_id,
        "variable_title": variable.get("variable_title", variable.get("title")),
        "source_object": source_id,
        "source_field": source_contract["field"],
        "source_capability": source_contract["capability"],
        "target_object": target_id,
        "target_field": target_field,
        "target_capability": target_contract["capability"],
        "datatype": compatible[0],
        "tests": sorted(direct_tests),
        "binding": _binding_alias(source),
    }, []


def _count_reasons(rows):
    counts = {}
    for row in rows:
        for reason in row.get("reasons", []):
            counts[reason] = counts.get(reason, 0) + 1
    return counts


def _finalize_stats(report):
    stats = report["stats"]
    stats["rewrites_applied"] = len(report["applied"])
    stats["review_required_variables"] = len(report["review_required"])
    direct = stats["direct_projection_variables_examined"]
    stats["rewrite_rate_pct_of_direct_projections"] = (
        round(100.0 * stats["rewrites_applied"] / direct, 2)
        if direct else 0.0
    )
    stats["review_rate_pct_of_direct_projections"] = (
        round(100.0 * stats["review_required_variables"] / direct, 2)
        if direct else 0.0
    )
    stats["review_reason_counts"] = _count_reasons(report["review_required"])
    return report


def modernize_foreach_v1(document, *, enabled=False):
    """Return (document, report), applying only exact v1 matches when enabled."""
    result = deepcopy(document)
    assessment = result.get("assessment", result)
    version = (assessment.get("specification") or {}).get("version")
    report = {
        "rewrite_id": REWRITE_ID,
        "target_version": TARGET_VERSION,
        "enabled": bool(enabled),
        "automatic_rewrite_enabled": False,
        "rewrite_performed": False,
        "stats": {
            "variables_total": 0,
            "direct_projection_variables_examined": 0,
            "rewrite_candidates_proven": 0,
            "rewrites_applied": 0,
            "review_required_variables": 0,
            "rewrite_rate_pct_of_direct_projections": 0.0,
            "review_rate_pct_of_direct_projections": 0.0,
            "review_reason_counts": {},
        },
        "applied": [],
        "review_required": [],
    }
    if not enabled:
        return result, _finalize_stats(report)
    if version != TARGET_VERSION:
        report["review_required"].append({
            "variable": None,
            "reasons": ["foreach_v1_requires_0.3.0"],
        })
        return result, _finalize_stats(report)

    variables = assessment.get("variables") or {}
    report["stats"]["variables_total"] = len(variables)
    # Analyze against the original faithful graph. Rewrites are collected first
    # so removing one Variable cannot change candidate detection for another.
    candidates = []
    for variable_id in sorted(variables):
        if _direct_projection(variables[variable_id]) is None:
            continue
        report["stats"]["direct_projection_variables_examined"] += 1
        candidate, reasons = _candidate(result, variable_id)
        if candidate is None:
            report["review_required"].append({
                "variable": variable_id,
                "reasons": reasons,
            })
        else:
            report["stats"]["rewrite_candidates_proven"] += 1
            candidates.append(candidate)

    # A target Object may only carry one v1 binding.
    by_target = {}
    for candidate in candidates:
        by_target.setdefault(candidate["target_object"], []).append(candidate)
    accepted = []
    for candidate in candidates:
        if len(by_target[candidate["target_object"]]) != 1:
            report["review_required"].append({
                "variable": candidate["variable"],
                "reasons": ["one_foreach_binding_per_target_object"],
            })
        else:
            accepted.append(candidate)

    objects = assessment.get("objects") or {}
    variables = assessment.get("variables") or {}
    for candidate in accepted:
        target_id = candidate["target_object"]
        target = objects[target_id]
        binding = candidate["binding"]
        if not _BINDING_RE.fullmatch(binding):
            raise ValueError(f"invalid generated foreach binding: {binding!r}")

        # Keep author presentation readable: capability, then foreach, then select.
        rebuilt = {}
        inserted = False
        for key, value in target.items():
            if key == "select" and not inserted:
                rebuilt["for_each"] = {
                    "item": binding,
                    "in": candidate["source_object"],
                }
                inserted = True
            rebuilt[key] = value
        if not inserted:
            raise ValueError("accepted foreach candidate lost target select")
        rebuilt["select"][candidate["target_field"]] = {
            "from": f"{binding}.{candidate['source_field']}",
        }
        objects[target_id] = rebuilt
        del variables[candidate["variable"]]
        report["applied"].append(candidate)

    if accepted:
        report["rewrite_performed"] = True
        if not variables:
            assessment.pop("variables", None)
        else:
            assessment["variables"] = variables
        assessment["objects"] = objects

    return result, _finalize_stats(report)
