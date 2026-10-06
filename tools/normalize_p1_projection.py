#!/usr/bin/env python3
"""Research-only P1 normalizer for single-use flattened Object-field projections.

This prototype demonstrates the first proposed automatic SCAP-NG 0.3.0
structural normalization class. It removes only a named local Variable whose
entire expression is one flattened Object-field projection and whose only
semantic consumer is one Object/State value position.

It deliberately does NOT create Binding/for_each scope.
"""
from __future__ import annotations

import copy


class ProjectionNormalizationError(ValueError):
    pass


def _walk(node, path=()):
    if isinstance(node, dict):
        yield path, node
        for key, value in node.items():
            yield from _walk(value, path + (key,))
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from _walk(value, path + (index,))


def _variable_ref_dict(node):
    return (
        isinstance(node, dict)
        and set(node) == {"variable"}
        and isinstance(node.get("variable"), str)
        and bool(node["variable"])
    )


def _projection_from_variable(var):
    if not isinstance(var, dict):
        return None
    if var.get("kind") != "local":
        return None
    datatype = var.get("datatype")
    if not isinstance(datatype, str) or not datatype:
        return None

    expr = var.get("expression")
    if not isinstance(expr, dict) or set(expr) != {"values"}:
        return None
    values = expr.get("values")
    if not isinstance(values, dict):
        return None
    if not {"object", "field"} <= set(values):
        return None
    if set(values) - {"object", "field", "record_field"}:
        return None
    if not isinstance(values.get("object"), str) or not values["object"]:
        return None
    if not isinstance(values.get("field"), str) or not values["field"]:
        return None
    if "record_field" in values and (
        not isinstance(values["record_field"], str) or not values["record_field"]
    ):
        return None

    return {
        "datatype": datatype,
        "projection": dict(values),
    }


def _semantic_variable_references(assessment, variable_id):
    """Return exact variable-reference locations outside the declaration itself."""
    refs = []
    for path, node in _walk(assessment):
        if len(path) >= 2 and path[0] == "variables" and path[1] == variable_id:
            continue
        if _variable_ref_dict(node) and node["variable"] == variable_id:
            refs.append(path)
    return refs


def _consumer_info(assessment, path):
    """Resolve a variable-ref path to one supported Object/State value consumer.

    Expected layout:
      objects.<id>....value -> {variable: X}
      states.<id>....value  -> {variable: X}

    The immediate parent containing 'value' must also carry datatype so the
    Variable datatype can be compared before normalization.
    """
    if not path:
        return None
    if path[0] not in {"objects", "states"}:
        return None

    cur = assessment
    for part in path[:-1]:
        cur = cur[part]
    # path points to the {variable: X} value, so the parent should be an entity
    # dictionary only when the final key is "value".
    if path[-1] != "value" or not isinstance(cur, dict):
        return None

    datatype = cur.get("datatype")
    variable_check = cur.get("variable_check")
    return {
        "section": path[0],
        "datatype": datatype,
        "variable_check": variable_check,
        "entity": cur,
    }


def plan_p1_projection_normalization(document):
    """Return a fail-closed P1 plan without changing the input document."""
    if not isinstance(document, dict) or not isinstance(document.get("assessment"), dict):
        raise ProjectionNormalizationError("expected document.assessment")

    assessment = document["assessment"]
    variables = assessment.get("variables") or {}
    objects = assessment.get("objects") or {}
    plan = []

    for variable_id, var in variables.items():
        parsed = _projection_from_variable(var)
        if parsed is None:
            continue

        projection = parsed["projection"]
        if projection["object"] not in objects:
            continue

        refs = _semantic_variable_references(assessment, variable_id)
        if len(refs) != 1:
            continue

        consumer = _consumer_info(assessment, refs[0])
        if consumer is None:
            continue

        # Exact type compatibility is deliberately conservative for the first
        # P1 class. Future type-normalization rules may widen this only with
        # independent proof.
        if consumer["datatype"] != parsed["datatype"]:
            continue

        # OVAL var_check/default semantics must remain visible at the consumer.
        # Current converted content represents that as variable_check.
        if not isinstance(consumer["variable_check"], str) or not consumer["variable_check"]:
            continue

        plan.append({
            "variable": variable_id,
            "source_variable": copy.deepcopy(var),
            "consumer_path": list(refs[0]),
            "projection": copy.deepcopy(projection),
            "datatype": parsed["datatype"],
            "variable_check": consumer["variable_check"],
            "classification": "P1_flattened_projection",
        })

    return plan


def apply_p1_projection_normalization(document):
    """Return (normalized_document, provenance_report).

    Only entries returned by plan_p1_projection_normalization() are rewritten.
    The source Variable definition is removed from executable content and copied
    into the provenance report.
    """
    normalized = copy.deepcopy(document)
    plan = plan_p1_projection_normalization(document)
    assessment = normalized["assessment"]

    applied = []
    for row in plan:
        path = tuple(row["consumer_path"])
        parent = assessment
        for part in path[:-1]:
            parent = parent[part]
        parent[path[-1]] = {
            "projection": copy.deepcopy(row["projection"]),
        }
        assessment["variables"].pop(row["variable"], None)
        applied.append(copy.deepcopy(row))

    if not assessment.get("variables"):
        assessment.pop("variables", None)

    report = {
        "normalization": "P1_flattened_projection",
        "semantic_effect": "none",
        "creates_binding_scope": False,
        "applied": applied,
    }
    return normalized, report
