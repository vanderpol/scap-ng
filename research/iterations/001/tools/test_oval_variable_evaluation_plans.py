#!/usr/bin/env python3
"""Regression tests for faithful OVAL variable evaluation plans."""
from pathlib import Path
import importlib.util

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("oval_ir", HERE / "oval_semantic_ir.py")
oval_ir = importlib.util.module_from_spec(spec)
spec.loader.exec_module(oval_ir)

variables = [
    {
        "id": "oval:x:var:1",
        "type": "local_variable",
        "datatype": "string",
        "semantic_ast": {
            "id": "oval:x:var:1",
            "type": "local_variable",
            "datatype": "string",
            "expression": {
                "op": "concat",
                "attributes": {},
                "args": [
                    {
                        "op": "object_component",
                        "object_ref": "oval:x:obj:1",
                        "item_field": "value",
                        "record_field": None,
                    },
                    {
                        "op": "variable_component",
                        "variable_ref": "oval:x:var:2",
                    },
                ],
            },
        },
    },
    {
        "id": "oval:x:var:2",
        "type": "constant_variable",
        "datatype": "string",
        "semantic_ast": {
            "id": "oval:x:var:2",
            "type": "constant_variable",
            "datatype": "string",
            "values": [{"value": "-suffix", "datatype": "string"}],
        },
    },
    {
        "id": "oval:x:var:3",
        "type": "external_variable",
        "datatype": "int",
        "semantic_ast": {
            "id": "oval:x:var:3",
            "type": "external_variable",
            "datatype": "int",
            "input": {"kind": "external", "datatype": "int"},
        },
    },
]

resolution = {
    "oval:x:var:1": {
        "status": "dynamic_object_dependency",
        "operation": "concat",
    },
    "oval:x:var:2": {
        "status": "exact_static",
        "values": ["-suffix"],
        "variable_type": "constant_variable",
        "datatype": "string",
    },
    "oval:x:var:3": {
        "status": "external_input",
        "variable_type": "external_variable",
        "datatype": "int",
    },
}

plans = oval_ir.build_variable_evaluation_plans(variables, resolution)

dynamic = plans["oval:x:var:1"]
assert dynamic["mode"] == "target_dependent", dynamic
assert dynamic["expression"]["op"] == "concat", dynamic
assert dynamic["dependencies"]["objects"] == ["oval:x:obj:1"], dynamic
assert dynamic["dependencies"]["variables"] == ["oval:x:var:2"], dynamic
assert dynamic["dependencies"]["operations"] == [
    "concat", "object_component", "variable_component"
], dynamic

static = plans["oval:x:var:2"]
assert static["mode"] == "static", static
assert static["values"] == ["-suffix"], static

external = plans["oval:x:var:3"]
assert external["mode"] == "external_input", external
assert external["input"] == {"kind": "external", "datatype": "int"}, external

print("PASS: static, external, and target-dependent variable plans preserved")
