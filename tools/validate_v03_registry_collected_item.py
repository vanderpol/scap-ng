"""Research semantic checks for windows.registry / windows.ntuser Item values.

Canonical collected-item.schema.json permits typed scalar OR array per field.
OVAL 5.12.3 registry_item expresses REG_MULTI_SZ as repeated string value
entities in a single Item. This module prevents flattening that one case and
checks the common known Registry type/Item value representation pairs.

This is a separate source-backed collected-Item gate, not a new capability.
"""
from __future__ import annotations

TYPE_DATATYPE = {
    "binary": "binary",
    "dword": "integer",
    "dword_big_endian": "integer",
    "qword": "integer",
    "expand_string": "string",
    "link": "string",
    "multi_string": "string",
    "string": "string",
}


def diagnostics(item):
    if item.get("capability") not in ("windows.registry", "windows.ntuser"):
        return []
    if item.get("status") != "exists":
        return []
    fields=item.get("fields") or {}
    type_field=fields.get("type")
    values=fields.get("value")
    if not isinstance(type_field,dict) or type_field.get("status")!="exists":
        # Type may legitimately be uncollected; do not guess it.
        return []
    kind=type_field.get("value")
    if kind not in TYPE_DATATYPE:
        return []  # Other Registry type families require dedicated review.
    if values is None:
        return []  # Absence of a collected value has separate Item semantics.
    items=values if isinstance(values,list) else [values]
    problems=[]
    if kind=="multi_string" and not isinstance(values,list):
        problems.append({"code":"registry.multistring_requires_value_array",
                         "message":"REG_MULTI_SZ must preserve individual string elements"})
    if kind!="multi_string" and isinstance(values,list) and len(values)!=1:
        problems.append({"code":"registry.scalar_unexpected_multiple_values",
                         "message":"Scalar Registry type cannot contain multiple value entities"})
    for index,entry in enumerate(items):
        if not isinstance(entry,dict) or entry.get("status")!="exists":
            continue
        if entry.get("datatype")!=TYPE_DATATYPE[kind]:
            problems.append({"code":"registry.item_value_datatype","index":index,
                             "type":kind,"datatype":entry.get("datatype"),
                             "expected":TYPE_DATATYPE[kind]})
            continue
        value=entry.get("value")
        if kind in ("dword","dword_big_endian","qword") and type(value) is not int:
            problems.append({"code":"registry.item_integer_representation","index":index})
        if kind in ("string","multi_string","expand_string","link") and not isinstance(value,str):
            problems.append({"code":"registry.item_string_representation","index":index})
    return problems
