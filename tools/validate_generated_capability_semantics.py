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


def validate_unix_file_object(obj):
    """Return deterministic semantic diagnostics for one native unix.file Object."""
    if obj.get("capability") != "unix.file":
        return []

    diagnostics=[]
    select=obj.get("select") or {}
    behaviors=obj.get("behaviors") or {}

    filepath=select.get("filepath")
    if isinstance(filepath, dict):
        forbidden=[key for key in ("max_depth","recurse","recurse_direction")
                   if key in behaviors]
        if forbidden:
            diagnostics.append({
                "code":"unix.file.filepath_no_recursion_behaviors",
                "fields":forbidden,
                "message":"filepath selection does not permit recursion depth/type/direction behaviors",
            })
        if (
            filepath.get("operation") != "equals"
            and behaviors.get("recurse_file_system") == "defined"
        ):
            diagnostics.append({
                "code":"unix.file.filepath_pattern_defined_filesystem",
                "fields":["recurse_file_system"],
                "message":"filepath non-equality selection cannot use recurse_file_system=defined",
            })

    path=select.get("path")
    if isinstance(path, dict) and path.get("operation") != "equals":
        forbidden=[]
        for key in ("max_depth","recurse_direction","recurse"):
            if key in behaviors:
                forbidden.append(key)
        if behaviors.get("recurse_file_system") == "defined":
            forbidden.append("recurse_file_system")
        if forbidden:
            diagnostics.append({
                "code":"unix.file.path_pattern_no_recursion_behaviors",
                "fields":forbidden,
                "message":"path non-equality selection cannot use recursion behaviors or recurse_file_system=defined",
            })

    filename=select.get("filename")
    if isinstance(filename, dict):
        value=filename.get("value")
        variable=_is_variable_value(value)
        nil=filename.get("nil") is True
        pattern=filename.get("operation") == "pattern match"
        if value == "" and not (variable or nil or pattern):
            diagnostics.append({
                "code":"unix.file.filename_empty",
                "fields":["filename"],
                "message":"empty filename requires Variable, nil directory selection, or pattern-match semantics",
            })

    return diagnostics


def validate_assessment_capability_semantics(document):
    """Validate current native Assessment cross-node capability semantics."""
    assessment=document.get("assessment",document)
    diagnostics=[]

    objects=assessment.get("objects") or {}
    states=assessment.get("states") or {}
    tests=assessment.get("tests") or {}

    for object_id,obj in objects.items():
        for row in validate_unix_file_object(obj):
            diagnostics.append({"object":object_id,**row})

        for flt in obj.get("filters") or []:
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
