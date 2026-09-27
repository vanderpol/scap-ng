#!/usr/bin/env python3
"""Regression tests for OVAL decimal arithmetic and escape_regex semantics."""
from pathlib import Path
from tempfile import TemporaryDirectory
import importlib.util

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("oval_ir", HERE/"oval_semantic_ir.py")
oval_ir=importlib.util.module_from_spec(spec)
spec.loader.exec_module(oval_ir)

xml=r"""<?xml version="1.0" encoding="UTF-8"?>
<oval_definitions xmlns="http://oval.mitre.org/XMLSchema/oval-definitions-5">
 <generator/>
 <variables>
  <local_variable id="oval:x:var:1" version="1" datatype="float">
   <arithmetic arithmetic_operation="multiply">
    <literal_component datatype="float">1.1</literal_component>
    <literal_component datatype="float">1.1</literal_component>
   </arithmetic>
  </local_variable>
  <local_variable id="oval:x:var:2" version="1" datatype="string">
   <escape_regex>
    <literal_component datatype="string">\^.$|()[]{}*+?</literal_component>
   </escape_regex>
  </local_variable>
 </variables>
</oval_definitions>
"""

with TemporaryDirectory() as td:
    p=Path(td)/"exact.xml"; p.write_text(xml,encoding="utf-8")
    ir=oval_ir.parse(p)

r=ir["variable_resolution"]
assert r["oval:x:var:1"]["values"]==["1.21"],r["oval:x:var:1"]
assert r["oval:x:var:2"]["values"]==[r"\\\^\.\$\|\(\)\[\]\{\}\*\+\?"],r["oval:x:var:2"]
print("PASS: exact decimal arithmetic and OVAL regex escaping preserved")
