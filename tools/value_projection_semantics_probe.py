#!/usr/bin/env python3
"""Focused semantic probes for OVAL object_component and NG value projection.

Research-only. This models the explicit ObjectComponentType rules stated by the
pinned OVAL 5.12.3 oval-definitions-schema.xsd. It is intentionally small and
does not claim to implement every collected-object status propagation rule.
"""
from __future__ import annotations

ERROR = "error"
OK = "ok"


def _values_comply(values, datatype):
    """Focused OVAL VariableType datatype compliance for current P1 proof types.

    OVAL 5.12.3 VariableType requires all values identified by a Variable to
    comply with its declared datatype or analysis reports error. The current
    corpus-proven P1 class contains only string and int Variables.
    """
    if datatype is None:
        return True
    if datatype == "string":
        return all(isinstance(v, str) for v in values)
    if datatype == "int":
        import re
        for value in values:
            if isinstance(value, bool):
                return False
            if isinstance(value, int):
                continue
            if not isinstance(value, str):
                return False
            if re.fullmatch(r"[+-]?\d+", value.strip()) is None:
                return False
        return True
    raise ValueError(f"datatype not covered by focused P1 proof: {datatype}")


def oval_object_component(items, item_field, record_field=None, datatype=None):
    """Resolve the value collection for a successful referenced Object.

    Each item is represented as a mapping from entity name to a list of values.
    A record entity value is represented as a mapping from record-field name to
    a list of values.

    OVAL 5.12.3 ObjectComponentType requires:
    - zero referenced Items -> error;
    - missing item_field on any considered Item -> error;
    - one or more same-name entities -> collect all their values;
    - requested record_field missing from a record entity -> error.

    The returned value collection is flattened and does not retain source Item
    identity. That loss of row identity is intentional OVAL semantics.
    """
    items = list(items)
    if not items:
        return {"status": ERROR, "values": []}

    out = []
    for item in items:
        entities = item.get(item_field)
        if not entities:
            return {"status": ERROR, "values": []}

        if record_field is None:
            out.extend(entities)
            continue

        for record in entities:
            if not isinstance(record, dict):
                return {"status": ERROR, "values": []}
            fields = record.get(record_field)
            if not fields:
                return {"status": ERROR, "values": []}
            out.extend(fields)

    if not _values_comply(out, datatype):
        return {"status": ERROR, "values": []}
    return {"status": OK, "values": out}


def inline_projection(items, item_field, record_field=None, datatype=None):
    """Candidate native P1 projection.

    A P1 direct Collection-field projection is safe only if it deliberately
    uses the same semantic primitive as migrated object_component, including
    error behavior and flattening. It must not introduce lexical Item binding.
    """
    return oval_object_component(items, item_field, record_field, datatype)


def prove_inline_projection_equivalence(items, item_field, record_field=None, datatype=None):
    source = oval_object_component(items, item_field, record_field, datatype)
    target = inline_projection(items, item_field, record_field, datatype)
    return {
        "source": source,
        "target": target,
        "equivalent": source == target,
    }


def same_item_binding_projection(items, item_field):
    """Illustrate the semantic difference from lexical binding.

    This retains Item identity and therefore is NOT a lossless replacement for
    object_component when more than one source Item is possible.
    """
    out = []
    for idx, item in enumerate(items):
        values = item.get(item_field) or []
        for value in values:
            out.append({"source_item": idx, "value": value})
    return out
