#!/usr/bin/env python3
"""Regression tests for target-independent OVAL variable functions."""
from pathlib import Path
from tempfile import TemporaryDirectory
import importlib.util

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("oval_ir", HERE / "oval_semantic_ir.py")
oval_ir = importlib.util.module_from_spec(spec)
spec.loader.exec_module(oval_ir)

xml = """<?xml version="1.0" encoding="UTF-8"?>
<oval_definitions xmlns="http://oval.mitre.org/XMLSchema/oval-definitions-5">
  <generator/>
  <variables>
    <local_variable id="oval:x:var:1" version="1" datatype="string">
      <merge delimiter="," sort="lexical" order="descending">
        <literal_component datatype="string">alpha</literal_component>
        <literal_component datatype="string">charlie</literal_component>
        <literal_component datatype="string">bravo</literal_component>
      </merge>
    </local_variable>
    <local_variable id="oval:x:var:2" version="1" datatype="string">
      <merge delimiter="|" sort="document">
        <literal_component datatype="string">first</literal_component>
        <literal_component datatype="string">second</literal_component>
      </merge>
    </local_variable>
  </variables>
</oval_definitions>
"""

with TemporaryDirectory() as td:
    path = Path(td) / "merge.xml"
    path.write_text(xml, encoding="utf-8")
    ir = oval_ir.parse(path)

r1 = ir["variable_resolution"]["oval:x:var:1"]
assert r1["status"] == "exact_static", r1
assert r1["values"] == ["charlie,bravo,alpha"], r1

r2 = ir["variable_resolution"]["oval:x:var:2"]
assert r2["status"] == "exact_static", r2
assert r2["values"] == ["first|second"], r2

assert ir["variable_evaluation_plans"]["oval:x:var:1"]["mode"] == "static"
assert "merge" in ir["variable_function_model"]["static_evaluator_operations"]

print("PASS: static OVAL merge document/lexical ordering preserved")
