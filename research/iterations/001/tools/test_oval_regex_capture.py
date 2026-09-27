#!/usr/bin/env python3
"""Regression tests for OVAL regex_capture static semantics."""
from pathlib import Path
from tempfile import TemporaryDirectory
import importlib.util

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("oval_ir",HERE/"oval_semantic_ir.py")
oval_ir=importlib.util.module_from_spec(spec)
spec.loader.exec_module(oval_ir)

xml="""<?xml version="1.0" encoding="UTF-8"?>
<oval_definitions xmlns="http://oval.mitre.org/XMLSchema/oval-definitions-5">
 <generator/>
 <variables>
  <local_variable id="oval:x:var:1" version="1" datatype="string">
   <regex_capture pattern="(i..)+"><literal_component datatype="string">mississippi</literal_component></regex_capture>
  </local_variable>
  <local_variable id="oval:x:var:2" version="1" datatype="string">
   <regex_capture pattern="abc.*xyz"><literal_component datatype="string">abchelloxyz</literal_component></regex_capture>
  </local_variable>
  <local_variable id="oval:x:var:3" version="1" datatype="string">
   <regex_capture pattern="abc(.*)xyz"><literal_component datatype="string">abcHELLOxyz</literal_component></regex_capture>
  </local_variable>
 </variables>
</oval_definitions>
"""
with TemporaryDirectory() as td:
    p=Path(td)/"regex.xml"; p.write_text(xml,encoding="utf-8")
    ir=oval_ir.parse(p)
r=ir["variable_resolution"]
assert r["oval:x:var:1"]["values"]==["ipp"],r["oval:x:var:1"]
assert r["oval:x:var:2"]["values"]==[""],r["oval:x:var:2"]
assert r["oval:x:var:3"]["values"]==["HELLO"],r["oval:x:var:3"]
print("PASS: regex_capture first-capture and empty-result semantics preserved")
