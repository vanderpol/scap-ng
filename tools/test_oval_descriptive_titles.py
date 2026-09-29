#!/usr/bin/env python3
"""Regression tests for descriptive OVAL labels in native SCAP-NG Assessment nodes."""
from __future__ import annotations

import importlib.util
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("converter",HERE/"scap14_to_scapng.py")
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

obj=mod.collector_node({
    "id":"oval:example:obj:1",
    "type":"file_object",
    "namespace":"http://oval.mitre.org/XMLSchema/oval-definitions-5#unix",
    "version":"1",
    "comment":"Collect the SSH server configuration file",
    "children":[],
})
assert obj["object_title"]=="Collect the SSH server configuration file"
assert "comment" not in obj

state=mod.predicate_node({
    "id":"oval:example:ste:1",
    "type":"file_state",
    "namespace":"http://oval.mitre.org/XMLSchema/oval-definitions-5#unix",
    "operator":"AND",
    "comment":"Require root ownership",
    "entities":[],
})
assert state["state_title"]=="Require root ownership"
assert "comment" not in state

variable=mod.variable_node({
    "id":"oval:example:var:1",
    "type":"constant_variable",
    "datatype":"string",
    "comment":"Expected configuration path",
    "semantic_ast":{},
}, {"variable_resolution":{},"variable_evaluation_plans":{}})
assert variable["variable_title"]=="Expected configuration path"
assert "comment" not in variable

test=mod.test_node({
    "id":"oval:example:tst:1",
    "type":"file_test",
    "namespace":"http://oval.mitre.org/XMLSchema/oval-definitions-5#unix",
    "comment":"Verify the configuration is owned by root",
    "objects":[],
    "states":[],
})
assert test["test_title"]=="Verify the configuration is owned by root"
assert "comment" not in test

print("PASS: OVAL descriptive comments become typed SCAP-NG node titles")
