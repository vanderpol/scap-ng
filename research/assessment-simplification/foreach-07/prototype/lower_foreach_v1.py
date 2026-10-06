#!/usr/bin/env python3
"""Research-only lowering for the proposed foreach v1 authoring form."""
from __future__ import annotations


class ForeachV1Error(ValueError):
    pass


def lower_foreach_v1(object_id: str, obj: dict) -> dict:
    """Lower author-facing foreach v1 into its faithful semantic graph.

    Input shape:
      for_each:
        item: user
        in: non-system-users
      select:
        path:
          from: user.home_dir

    Output is an abstract semantic graph, not production 0.3.0 syntax.
    """
    if "for_each" not in obj:
        raise ForeachV1Error("missing for_each")
    binding = obj["for_each"]
    item = binding.get("item")
    source = binding.get("in")
    if not item or not source:
        raise ForeachV1Error("for_each requires item and in")

    select = obj.get("select")
    if not isinstance(select, dict) or not select:
        raise ForeachV1Error("foreach target requires select")

    bound = []
    ordinary = {}
    for entity, spec in select.items():
        if not isinstance(spec, dict):
            raise ForeachV1Error(f"{entity}: selector must be an object")
        if "from" not in spec:
            ordinary[entity] = spec
            continue

        if set(spec) != {"from"}:
            raise ForeachV1Error(
                f"{entity}: from is a binding and cannot be combined with "
                "operation/datatype/value in foreach v1"
            )
        ref = spec["from"]
        if not isinstance(ref, str) or "." not in ref:
            raise ForeachV1Error(f"{entity}: invalid from binding")
        alias, field = ref.split(".", 1)
        if alias != item:
            raise ForeachV1Error(
                f"{entity}: binding alias {alias!r} does not match {item!r}"
            )
        if not field:
            raise ForeachV1Error(f"{entity}: projected field is empty")
        bound.append((entity, field))

    if len(bound) != 1:
        raise ForeachV1Error(
            "foreach v1 requires exactly one bound target selector"
        )

    target_entity, item_field = bound[0]
    synthetic_var = f"__foreach_{object_id}_{target_entity}"

    return {
        "rewrite_id": "foreach.direct-object-component.at-least-one.v1",
        "source_object": source,
        "binding": item,
        "synthetic_variable": {
            "id": synthetic_var,
            "kind": "local",
            "expression": {
                "object_component": {
                    "object": source,
                    "item_field": item_field,
                }
            },
        },
        "target_object": {
            "id": object_id,
            "select": {
                target_entity: {
                    "variable": synthetic_var,
                    "var_check": "at least one",
                    "operation": "equals",
                    "datatype": "source-compatible",
                },
                **ordinary,
            },
        },
        "aggregation_boundary": "target_object_population",
        "collection_combination": "union",
    }
