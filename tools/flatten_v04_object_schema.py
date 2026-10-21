#!/usr/bin/env python3
"""Remove 0.4 generic Object select/collect wrapper levels in generated schemas.

Accept only capability-declared direct selector and acquisition parameter keys;
retain original selector alternative constraints, acquisition requirements,
for_each, filesystem, Set and Filter behavior. Refs #248 #239 #232.
"""
from __future__ import annotations
from copy import deepcopy

RESERVED = frozenset({
    "object", "object_title", "capability", "collect", "set", "filters",
    "traversal", "filesystem", "for_each", "foreach", "behaviors",
})


class UnsafeObjectSchema(ValueError):
    pass


def required_choice(names):
    names = tuple(sorted(set(names)))
    if not names:
        raise UnsafeObjectSchema("Empty selector/parameter alternative")
    return {"anyOf": [{"required": [name]} for name in names]}


def flatten_schema(obj, native, *, capability):
    """Return a new generated Object schema, or raise without changing input."""
    source = deepcopy(obj)
    props = source.get("properties", {})
    selectors = set((native.get("selector_map") or {}).values())
    parameters = set((native.get("collection_parameters") or {}).keys())
    if (selectors & parameters or (selectors | parameters) & RESERVED
            or "select" in selectors):
        raise UnsafeObjectSchema(f"{capability}: flat Object property collision")
    if "select" in parameters and capability != "windows.cmdlet":
        raise UnsafeObjectSchema(f"{capability}: unreviewed native select parameter")
    sel_schema = props.pop("select", None) if selectors else None
    col_schema = props.pop("collect", None) if parameters else None
    if selectors and not isinstance(sel_schema, dict):
        raise UnsafeObjectSchema(f"{capability}: missing selector grammar")
    if parameters and not isinstance(col_schema, dict):
        raise UnsafeObjectSchema(f"{capability}: missing parameter grammar")
    if not selectors and "select" in props and capability != "windows.cmdlet":
        raise UnsafeObjectSchema(f"{capability}: unexpected generic select")
    if not parameters and "collect" in props:
        raise UnsafeObjectSchema(f"{capability}: unexpected generic collect")
    if selectors and set((sel_schema.get("properties") or {})) != selectors:
        raise UnsafeObjectSchema(f"{capability}: selector catalog mismatch")
    if parameters and set((col_schema.get("properties") or {})) != parameters:
        raise UnsafeObjectSchema(f"{capability}: parameter catalog mismatch")
    if selectors and not isinstance(sel_schema.get("oneOf"), list):
        raise UnsafeObjectSchema(f"{capability}: no selector alternatives")
    if "oneOf" not in source or not isinstance(source["oneOf"], list):
        raise UnsafeObjectSchema(f"{capability}: missing direct-versus-Set choice")

    # Preserve exact generated native field validation, including typed
    # comparisons, nullable entity values, Variables and foreach bindings.
    for name, selector in (sel_schema or {}).get("properties", {}).items():
        if name in props:
            raise UnsafeObjectSchema(f"{capability}: direct selector {name} collides")
        props[name] = selector
    for name, parameter in (col_schema or {}).get("properties", {}).items():
        if name in props:
            raise UnsafeObjectSchema(f"{capability}: direct parameter {name} collides")
        props[name] = parameter

    collection_required = set((col_schema or {}).get("required", []))
    if not collection_required <= parameters:
        raise UnsafeObjectSchema(f"{capability}: unknown required parameter")
    selector_alternatives = []
    for alternative in (sel_schema or {}).get("oneOf", []):
        requirements = set(alternative.get("required", []))
        if not requirements or not requirements <= selectors:
            raise UnsafeObjectSchema(f"{capability}: invalid selector alternative")
        selector_alternatives.append(requirements)

    old_variants = source.pop("oneOf")
    had_select = False
    had_collect = False
    had_set = False
    for variant in old_variants:
        required = set(variant.get("required", []))
        if "set" in required:
            had_set = True
        elif "select" in required:
            had_select = True
            had_collect |= "collect" in required
        elif "collect" in required:
            had_collect = True
        else:
            raise UnsafeObjectSchema(f"{capability}: unexpected Object variant")
    if had_select != bool(selectors):
        raise UnsafeObjectSchema(f"{capability}: direct selector variant mismatch")
    if had_collect and not parameters:
        raise UnsafeObjectSchema(f"{capability}: no acquisition fields for required collect")
    if not had_set:
        raise UnsafeObjectSchema(f"{capability}: Set alternative unexpectedly missing")

    variants = []
    if selectors:
        for alternative in selector_alternatives:
            required = alternative | collection_required
            branch = {"required": sorted(required), "not": {"required": ["set"]}}
            if had_collect and not collection_required:
                # The old grammar required an explicit collect mapping even
                # when all individual parameters were optional. Preserve the
                # acquisition presence constraint in the flat grammar.
                branch["allOf"] = [required_choice(parameters)]
            variants.append(branch)
    elif parameters:
        if collection_required:
            variants.append({"required": sorted(collection_required),
                             "not": {"required": ["set"]}})
        else:
            variants.append({"allOf": [required_choice(parameters)],
                             "not": {"required": ["set"]}})

    # A Set uses its own constituent Object(s). Native acquisition selectors
    # and parameters cannot be silently combined with an enclosing Set.
    mixed_fields = sorted(selectors | parameters | {"for_each"})
    variants.append({"required": ["set"],
                     "not": {"anyOf": [
                         {"required": [name]} for name in mixed_fields]}})
    source["oneOf"] = variants

    # The old file-scope rule targets generic select.full_path/directory;
    # flatten it to precisely the same resource selection condition.
    all_of = source.get("allOf", [])
    for rule in all_of:
        premise = rule.get("if", {})
        if (premise.get("required") == ["select"] and
                "select" in premise.get("properties", {})):
            clause = premise["properties"]["select"]
            alternatives = clause.get("anyOf")
            if (not isinstance(alternatives, list) or not alternatives
                    or any(not set(item.get("required", [])) <= selectors
                           for item in alternatives)):
                raise UnsafeObjectSchema(f"{capability}: unsupported filesystem selector rule")
            rule["if"] = {"anyOf": deepcopy(alternatives)}
        consequence = rule.get("then", {})
        if consequence.get("required") == ["select"]:
            consequence["required"] = []
            consequence["allOf"] = [
                {"anyOf": [{"required": sorted(c)} for c in selector_alternatives]}
            ]
    source["description"] = (
        f"{capability} native flat Object; legal selector and acquisition keys "
        "are capability-defined. Generic select/collect wrappers are invalid."
    )
    return source
