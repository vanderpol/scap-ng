#!/usr/bin/env python3
"""Regression tests for offline object_component evaluation over variable_object data."""
from pathlib import Path
from tempfile import TemporaryDirectory
import importlib.util

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("oval_ir", HERE / "oval_semantic_ir.py")
oval_ir = importlib.util.module_from_spec(spec)
spec.loader.exec_module(oval_ir)

xml = """<?xml version="1.0" encoding="UTF-8"?>
<oval_definitions xmlns="http://oval.mitre.org/XMLSchema/oval-definitions-5"
 xmlns:ind="http://oval.mitre.org/XMLSchema/oval-definitions-5#independent">
 <generator/>
 <objects>
  <ind:variable_object id="oval:x:obj:1" version="1"><ind:var_ref>oval:x:var:1</ind:var_ref></ind:variable_object>
  <ind:variable_object id="oval:x:obj:2" version="1"><ind:var_ref>oval:x:var:2</ind:var_ref></ind:variable_object>
  <ind:variable_object id="oval:x:obj:3" version="1">
   <set set_operator="UNION">
    <object_reference>oval:x:obj:1</object_reference>
    <object_reference>oval:x:obj:2</object_reference>
   </set>
  </ind:variable_object>
 </objects>
 <variables>
  <constant_variable id="oval:x:var:1" version="1" datatype="string"><value>a</value><value>b</value></constant_variable>
  <constant_variable id="oval:x:var:2" version="1" datatype="string"><value>c</value></constant_variable>
  <local_variable id="oval:x:var:3" version="1" datatype="string">
   <object_component object_ref="oval:x:obj:3" item_field="value"/>
  </local_variable>
 </variables>
</oval_definitions>
"""

with TemporaryDirectory() as td:
    p=Path(td)/"object-component.xml"
    p.write_text(xml,encoding="utf-8")
    ir=oval_ir.parse(p)

r=ir["variable_resolution"]["oval:x:var:3"]
assert r["status"]=="exact_static", r
assert r["values"]==["a","b","c"], r
assert ir["variable_evaluation_plans"]["oval:x:var:3"]["mode"]=="static"
print("PASS: synthetic variable_object object_component evaluated offline")
