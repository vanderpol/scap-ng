#!/usr/bin/env python3
"""Regression tests for OVAL time_difference semantics."""
from pathlib import Path
from tempfile import TemporaryDirectory
import importlib.util

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("oval_ir", HERE/"oval_semantic_ir.py")
oval_ir=importlib.util.module_from_spec(spec)
spec.loader.exec_module(oval_ir)

xml="""<?xml version="1.0" encoding="UTF-8"?>
<oval_definitions xmlns="http://oval.mitre.org/XMLSchema/oval-definitions-5">
 <generator/>
 <variables>
  <local_variable id="oval:x:var:1" version="1" datatype="string">
   <time_difference format_1="year_month_day" format_2="year_month_day">
    <literal_component>2009-02-04 12:23:43</literal_component>
    <literal_component>2004/02/04 05:41:21</literal_component>
   </time_difference>
  </local_variable>
  <local_variable id="oval:x:var:2" version="1" datatype="string">
   <time_difference format_1="month_day_year" format_2="win_filetime">
    <literal_component>January, 01 1970</literal_component>
    <literal_component>19db1ded53e8000</literal_component>
   </time_difference>
  </local_variable>
  <local_variable id="oval:x:var:3" version="1" datatype="int">
   <time_difference format_2="seconds_since_epoch">
    <literal_component>1238506200</literal_component>
   </time_difference>
  </local_variable>
 </variables>
</oval_definitions>
"""
with TemporaryDirectory() as td:
    p=Path(td)/"time.xml"; p.write_text(xml,encoding="utf-8")
    ir=oval_ir.parse(p)

r=ir["variable_resolution"]
assert r["oval:x:var:1"]["status"]=="exact_static",r["oval:x:var:1"]
assert r["oval:x:var:1"]["values"]==["157876942"],r["oval:x:var:1"]
assert r["oval:x:var:2"]["values"]==["0"],r["oval:x:var:2"]
assert r["oval:x:var:3"]["status"]=="runtime_time_dependency",r["oval:x:var:3"]
assert ir["variable_evaluation_plans"]["oval:x:var:3"]["mode"]=="runtime_dependent"
print("PASS: two-input time_difference and current-time dependency modeled")
