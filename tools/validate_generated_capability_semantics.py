#!/usr/bin/env python3
"""Semantic validation that complements generated capability JSON Schemas.

JSON Schema handles structural/native vocabulary constraints. This module
handles source-backed cross-field and cross-reference rules that are clearer or
safer as semantic validation. Rules are intentionally narrow and capability
specific until proven reusable.
"""
from __future__ import annotations


class CapabilitySemanticError(ValueError):
    pass


def _is_variable_value(value):
    return (
        isinstance(value, dict)
        and set(value) == {"variable"}
        and isinstance(value.get("variable"), str)
        and bool(value["variable"])
    )


FILE_SELECTION_CAPABILITIES={"unix.file","file.hash","windows.file"}


def validate_file_selection_object(obj):
    """Return semantic diagnostics for native capabilities using file selection."""
    capability=obj.get("capability")
    if capability not in FILE_SELECTION_CAPABILITIES:
        return []

    diagnostics=[]
    select=obj.get("select") or {}
    traversal=obj.get("traversal")

    full_path=select.get("full_path")
    if full_path is not None and traversal is not None:
        diagnostics.append({
            "code":f"{capability}.full_path_no_traversal",
            "fields":["traversal"],
            "message":"full_path selection does not permit directory traversal",
        })

    directory=select.get("directory")
    if (
        isinstance(directory, dict)
        and directory.get("operation") != "equal"
        and traversal is not None
    ):
        diagnostics.append({
            "code":f"{capability}.pattern_directory_no_traversal",
            "fields":["traversal"],
            "message":"non-equality directory selection cannot use traversal",
        })

    name=select.get("name", ...)
    if name is None:
        # null intentionally selects the directory itself.
        pass
    elif isinstance(name, dict):
        value=name.get("value")
        variable=_is_variable_value(value)
        pattern=name.get("operation") == "match"
        if value == "" and not (variable or pattern):
            diagnostics.append({
                "code":f"{capability}.name_empty",
                "fields":["name"],
                "message":"empty name requires a Variable reference or match semantics; use null to select the directory itself",
            })
        if (
            capability == "windows.file"
            and isinstance(value, str)
            and not pattern
            and any(ch in value for ch in '\\/:*?>|<"')
        ):
            diagnostics.append({
                "code":"windows.file.literal_name_characters",
                "fields":["name"],
                "message":"literal Windows file name contains path separator or reserved filename characters",
            })

    return diagnostics


def validate_unix_file_object(obj):
    """Backward-compatible focused helper for unix.file tests."""
    if obj.get("capability") != "unix.file":
        return []
    return validate_file_selection_object(obj)


def _iter_set_filters(expression):
    """Yield State filters from a native recursive Set expression."""
    if not isinstance(expression, dict):
        return
    for operand in expression.get("operands") or []:
        if not isinstance(operand, dict):
            continue
        if isinstance(operand.get("object"), str):
            for flt in operand.get("filters") or []:
                if isinstance(flt, dict):
                    yield flt
        nested=operand.get("set")
        if isinstance(nested, dict):
            yield from _iter_set_filters(nested)


def _iter_set_object_refs(expression):
    """Yield Object IDs referenced by a native recursive Set expression."""
    if not isinstance(expression, dict):
        return
    for operand in expression.get("operands") or []:
        if not isinstance(operand, dict):
            continue
        object_id=operand.get("object")
        if isinstance(object_id,str):
            yield object_id
        nested=operand.get("set")
        if isinstance(nested,dict):
            yield from _iter_set_object_refs(nested)


def validate_assessment_capability_semantics(document):
    """Validate current native Assessment cross-node capability semantics."""
    assessment=document.get("assessment",document)
    diagnostics=[]

    objects=assessment.get("objects") or {}
    states=assessment.get("states") or {}
    tests=assessment.get("tests") or {}

    for object_id,obj in objects.items():
        for row in validate_file_selection_object(obj):
            diagnostics.append({"object":object_id,**row})

        for referenced_object_id in _iter_set_object_refs(obj.get("set")):
            referenced_object=objects.get(referenced_object_id)
            if referenced_object is None:
                diagnostics.append({
                    "object":object_id,
                    "code":"object.set_object_missing",
                    "referenced_object":referenced_object_id,
                    "message":"Set references an unknown Object",
                })
            elif referenced_object.get("capability") != obj.get("capability"):
                diagnostics.append({
                    "object":object_id,
                    "code":"object.set_object_capability",
                    "referenced_object":referenced_object_id,
                    "message":"Set Object capability must match parent Object capability",
                })

        for flt in _iter_set_filters(obj.get("set")):
            state_id=flt.get("state")
            state=states.get(state_id)
            if state is None:
                diagnostics.append({
                    "object":object_id,
                    "code":"object.filter_state_missing",
                    "state":state_id,
                    "message":"Object filter references an unknown State",
                })
                continue
            if state.get("capability") != obj.get("capability"):
                diagnostics.append({
                    "object":object_id,
                    "code":"object.filter_state_capability",
                    "state":state_id,
                    "message":"Object filter State capability must match Object capability",
                })

    for test_id,test in tests.items():
        object_id=test.get("object")
        obj=objects.get(object_id)
        if obj is None:
            diagnostics.append({
                "test":test_id,
                "code":"test.object_missing",
                "object":object_id,
                "message":"Test references an unknown Object",
            })
        elif obj.get("capability") != test.get("capability"):
            diagnostics.append({
                "test":test_id,
                "code":"test.object_capability",
                "object":object_id,
                "message":"Test and Object capabilities must match",
            })

        for state_id in test.get("states") or []:
            state=states.get(state_id)
            if state is None:
                diagnostics.append({
                    "test":test_id,
                    "code":"test.state_missing",
                    "state":state_id,
                    "message":"Test references an unknown State",
                })
            elif state.get("capability") != test.get("capability"):
                diagnostics.append({
                    "test":test_id,
                    "code":"test.state_capability",
                    "state":state_id,
                    "message":"Test and State capabilities must match",
                })

    return diagnostics


def assert_assessment_capability_semantics(document):
    diagnostics=validate_assessment_capability_semantics(document)
    if diagnostics:
        raise CapabilitySemanticError(
            "capability semantic validation failed: " + repr(diagnostics)
        )
    return document
