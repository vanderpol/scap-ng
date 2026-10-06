#!/usr/bin/env python3
"""Research helpers for proving direct foreach collection-expansion equivalence.

These helpers model only the value-selection identity needed by the first
foreach modernization class. They do not model target acquisition status or
replace the OVAL result truth tables.

For an Object entity using var_check="at least one":

    match(item, projected_values)
      == OR(match(item, value) for value in projected_values)

Therefore the Object population selected by one multi-valued selector equals
the set-union of populations selected independently for each projected value,
provided the same comparison predicate and source value semantics are used.

The analogous identity is deliberately false for var_check="all".
"""
from __future__ import annotations

from collections.abc import Callable, Iterable
import json


def canonical(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def unique(values: Iterable):
    seen = set()
    out = []
    for value in values:
        key = canonical(value)
        if key not in seen:
            seen.add(key)
            out.append(value)
    return out


def faithful_at_least_one_selection(items, projected_values, predicate: Callable):
    """Select Items exactly as an at-least-one multi-valued Object entity."""
    values = list(projected_values)
    if not values:
        return []
    return unique(
        item
        for item in items
        if any(predicate(item, value) for value in values)
    )


def foreach_union_selection(items, projected_values, predicate: Callable):
    """Conceptual foreach expansion: select per value, then set-union Items."""
    selected = []
    for value in projected_values:
        selected.extend(item for item in items if predicate(item, value))
    return unique(selected)


def faithful_all_selection(items, projected_values, predicate: Callable):
    """Select Items under var_check=all for a non-empty projected value set."""
    values = list(projected_values)
    if not values:
        return []
    return unique(
        item
        for item in items
        if all(predicate(item, value) for value in values)
    )


def equivalent_population(left, right) -> bool:
    """Compare Object populations as sets, independent of collection order."""
    return {canonical(x) for x in left} == {canonical(x) for x in right}


def direct_at_least_one_equivalent(items, projected_values, predicate: Callable) -> bool:
    return equivalent_population(
        faithful_at_least_one_selection(items, projected_values, predicate),
        foreach_union_selection(items, projected_values, predicate),
    )


def project_object_component_complete(items, item_field):
    """Model the explicit OVAL ObjectComponentType rules for a complete source.

    The pinned OVAL schema states:
    * zero collected Items => error determining the ObjectComponent value;
    * each collected Item must contain the requested item_field, otherwise error;
    * one or more matching entities contribute all of their values.

    Record-field projection and non-complete collected-object flags are separate
    proof classes and intentionally not guessed here.
    """
    rows = list(items)
    if not rows:
        return {"status": "error", "values": [], "reason": "source_object_has_no_items"}

    values = []
    for item in rows:
        if item_field not in item:
            return {
                "status": "error",
                "values": [],
                "reason": f"item_field_missing:{item_field}",
            }
        raw = item[item_field]
        if isinstance(raw, list):
            if not raw:
                return {
                    "status": "error",
                    "values": [],
                    "reason": f"item_field_has_no_entities:{item_field}",
                }
            values.extend(raw)
        else:
            values.append(raw)
    return {"status": "values", "values": values}


DIRECT_FOREACH_REWRITE_ID = "foreach.direct-object-component.at-least-one.v1"


def direct_foreach_desugaring(
    *,
    source_object,
    item_field,
    target_object,
    target_entity,
    operation,
    datatype,
):
    """Return the normative semantic graph for the first foreach candidate.

    This deliberately does not define a second execution model. The native
    authoring shorthand is equivalent by definition to the same semantic nodes
    used by faithful OVAL conversion:

        source Object
          -> object_component(item_field)
          -> local Variable
          -> target Object entity var_ref(var_check=at least one)

    Runtime collection/component flags, value status, provenance and downstream
    Test aggregation therefore remain properties of those existing semantic
    nodes. A scanner may optimize execution but may not change this graph's
    observable semantics.
    """
    variable = {
        "kind": "local_variable",
        "expression": {
            "kind": "object_component",
            "object_ref": source_object,
            "item_field": item_field,
        },
    }
    selector = {
        "object_ref": target_object,
        "entity": target_entity,
        "operation": operation,
        "datatype": datatype,
        "variable": variable,
        "var_check": "at least one",
    }
    return {
        "rewrite_id": DIRECT_FOREACH_REWRITE_ID,
        "source_object": source_object,
        "variable": variable,
        "selector": selector,
        "aggregation_boundary": "target_object_population",
    }


def direct_foreach_preconditions(candidate):
    """Check semantic preconditions for the first reviewed rewrite family."""
    reasons = []
    if candidate.get("candidate_family") != "collection_expansion_at_least_one":
        reasons.append("candidate_family_not_at_least_one_collection_expansion")

    expression = candidate.get("expression", {})
    if expression.get("kind") != "direct_object_projection":
        reasons.append("projection_is_not_direct_object_component")

    targets = candidate.get("targets", [])
    if not targets:
        reasons.append("no_target_object_selector")
    if len(targets) != 1:
        reasons.append("first_proof_class_requires_single_target_consumer")

    variable_id = candidate.get("variable_id")
    for target in targets:
        if target.get("var_check") != "at least one":
            reasons.append("target_var_check_not_at_least_one")
        if target.get("context") != "object_selector":
            reasons.append("consumer_is_not_object_selector")
        variable_entities = target.get("object_features", {}).get("variable_entities", [])
        independent = [
            entity for entity in variable_entities
            if entity.get("var_ref") != variable_id
        ]
        if independent:
            reasons.append("target_has_additional_variable_selectors")
        if not target.get("tests"):
            reasons.append("first_proof_class_requires_directly_tested_target")

    if expression.get("record_field") is not None:
        # The OVAL behavior is well defined, but record-field extraction has not
        # yet been included in this first equivalence fixture family.
        reasons.append("record_field_not_in_first_proof_class")

    return {
        "rewrite_id": DIRECT_FOREACH_REWRITE_ID,
        "eligible": not reasons,
        "reasons": sorted(set(reasons)),
    }


def _typed_value_key(value):
    """Normalize a result typed_value or primitive without losing datatype."""
    if isinstance(value, dict) and "value" in value:
        return (
            value.get("datatype"),
            json.dumps(value.get("value"), sort_keys=True, separators=(",", ":"), ensure_ascii=False),
        )
    return (
        None,
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False),
    )


def _field_values(item, item_field):
    fields = item.get("fields", {})
    if item_field not in fields:
        raise ValueError(f"source Item {item.get('id')} lacks field {item_field}")
    raw = fields[item_field]
    return raw if isinstance(raw, list) else [raw]


def faithful_direct_evidence(
    *,
    source_object_ref,
    variable_result,
    items_by_id,
    item_field,
    target_item_refs,
):
    """Canonical evidence view for faithful object_component plumbing.

    The view intentionally includes only relationships the faithful result can
    establish without inference:
      * source Object identity;
      * source Item identities consumed by the Variable;
      * projected source field/value pairs;
      * the Variable status;
      * the combined target Object/Test Item population.

    It does not infer which target Item came from which projected source value.
    """
    source_item_refs = list(variable_result.get("item_refs", []))
    projections = []
    flattened = []
    for item_ref in source_item_refs:
        item = items_by_id[item_ref]
        for value in _field_values(item, item_field):
            key = _typed_value_key(value)
            projections.append((item_ref, key))
            flattened.append(key)

    reported = [_typed_value_key(v) for v in variable_result.get("values", [])]
    if sorted(flattened) != sorted(reported):
        raise ValueError(
            "Variable values do not match values reconstructable from source item_refs"
        )

    return {
        "source_object_ref": source_object_ref,
        "source_item_refs": tuple(sorted(source_item_refs)),
        "projected": tuple(sorted(projections)),
        "status": variable_result.get("status"),
        "target_item_refs": tuple(sorted(set(target_item_refs))),
    }


def foreach_direct_evidence(
    *,
    source_object_ref,
    bindings,
    target_item_refs,
    status,
):
    """Canonical evidence view for native foreach binding evidence.

    Each binding contains a source_item_ref and one or more projected_values.
    Child target correlation is deliberately not required; target_item_refs are
    compared as one combined population, matching the preserved Test boundary.
    """
    source_item_refs = []
    projections = []
    for binding in bindings:
        item_ref = binding["source_item_ref"]
        source_item_refs.append(item_ref)
        for value in binding.get("projected_values", []):
            projections.append((item_ref, _typed_value_key(value)))

    return {
        "source_object_ref": source_object_ref,
        "source_item_refs": tuple(sorted(source_item_refs)),
        "projected": tuple(sorted(projections)),
        "status": status,
        "target_item_refs": tuple(sorted(set(target_item_refs))),
    }


def evidence_equivalent(left, right):
    return left == right
