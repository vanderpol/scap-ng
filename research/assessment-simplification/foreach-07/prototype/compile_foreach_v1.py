#!/usr/bin/env python3
"""Context-aware research compiler for foreach v1.

This is deliberately outside frozen schema/v0.2.0. It validates the authoring
binding against the current capability mappings and lowers it to the same
faithful semantic graph used by the equivalence proof.
"""
from __future__ import annotations

import json
from pathlib import Path

from lower_foreach_v1 import ForeachV1Error, lower_foreach_v1


ROOT = Path(__file__).resolve().parents[4]
DEFAULT_MAPPING_DIR = ROOT / "schema" / "v0.2.0" / "capability-mappings" / "supported"


def load_capabilities(mapping_dir: Path = DEFAULT_MAPPING_DIR) -> dict[str, dict]:
    out = {}
    for path in sorted(mapping_dir.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        capability = data.get("capability")
        if capability:
            out[capability] = data
    return out


def _field_types(mapping: dict, field: str) -> set[str]:
    return set(mapping.get("native", {}).get("field_datatypes", {}).get(field, []))


def compile_foreach_object(
    *,
    object_id: str,
    obj: dict,
    objects: dict,
    capabilities: dict[str, dict],
) -> dict:
    """Validate and lower one foreach Object in Assessment context."""
    binding = obj.get("for_each")
    if not isinstance(binding, dict):
        raise ForeachV1Error(f"{object_id}: missing for_each")

    source_id = binding.get("in")
    if source_id not in objects:
        raise ForeachV1Error(
            f"{object_id}: source Object {source_id!r} does not exist"
        )
    source_obj = objects[source_id]

    source_cap = source_obj.get("capability")
    target_cap = obj.get("capability")
    if source_cap not in capabilities:
        raise ForeachV1Error(
            f"{object_id}: unsupported source capability {source_cap!r}"
        )
    if target_cap not in capabilities:
        raise ForeachV1Error(
            f"{object_id}: unsupported target capability {target_cap!r}"
        )

    lowered = lower_foreach_v1(object_id, obj)
    source_mapping = capabilities[source_cap]
    target_mapping = capabilities[target_cap]

    bound = [
        (entity, spec["from"])
        for entity, spec in obj["select"].items()
        if isinstance(spec, dict) and "from" in spec
    ]
    if len(bound) != 1:
        raise ForeachV1Error(
            f"{object_id}: foreach v1 requires exactly one bound selector"
        )
    target_field, from_ref = bound[0]
    _, source_field = from_ref.split(".", 1)

    source_types = _field_types(source_mapping, source_field)
    target_types = _field_types(target_mapping, target_field)
    if not source_types:
        raise ForeachV1Error(
            f"{object_id}: {source_cap}.{source_field} is not a known typed field"
        )
    if not target_types:
        raise ForeachV1Error(
            f"{object_id}: {target_cap}.{target_field} is not a known typed selector"
        )

    compatible = sorted(source_types & target_types)
    if not compatible:
        raise ForeachV1Error(
            f"{object_id}: incompatible binding {source_cap}.{source_field} "
            f"{sorted(source_types)} -> {target_cap}.{target_field} "
            f"{sorted(target_types)}"
        )

    # v1 is intentionally lossless and non-transforming: there must be one
    # unambiguous compatible datatype. If a future field pair has several
    # possible common datatypes, that requires a separate design decision.
    if len(compatible) != 1:
        raise ForeachV1Error(
            f"{object_id}: v1 requires one unambiguous common datatype; "
            f"got {compatible}"
        )

    datatype = compatible[0]
    lowered_selector = lowered["target_object"]["select"][target_field]
    lowered_selector["datatype"] = datatype

    return {
        "object_id": object_id,
        "source_object": source_id,
        "source_capability": source_cap,
        "source_field": source_field,
        "target_capability": target_cap,
        "target_field": target_field,
        "datatype": datatype,
        "lowered": lowered,
    }


def compile_assessment_foreach(
    assessment: dict,
    *,
    mapping_dir: Path = DEFAULT_MAPPING_DIR,
) -> dict:
    """Compile all research foreach v1 Objects in an Assessment-shaped mapping."""
    objects = assessment.get("objects", {})
    if not isinstance(objects, dict):
        raise ForeachV1Error("assessment objects must be a mapping")
    capabilities = load_capabilities(mapping_dir)

    compiled = {}
    for object_id, obj in objects.items():
        if isinstance(obj, dict) and "for_each" in obj:
            compiled[object_id] = compile_foreach_object(
                object_id=object_id,
                obj=obj,
                objects=objects,
                capabilities=capabilities,
            )
    return compiled
