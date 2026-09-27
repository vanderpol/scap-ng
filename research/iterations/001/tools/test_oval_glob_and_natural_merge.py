#!/usr/bin/env python3
"""Regression tests for OVAL glob_to_regex and natural merge semantics."""
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
  <local_variable id="oval:x:var:1" version="1" datatype="string">
   <glob_to_regex><literal_component datatype="string">abcd</literal_component></glob_to_regex>
  </local_variable>
  <local_variable id="oval:x:var:2" version="1" datatype="string">
   <glob_to_regex><literal_component datatype="string">*.txt</literal_component></glob_to_regex>
  </local_variable>
  <local_variable id="oval:x:var:3" version="1" datatype="string">
   <glob_to_regex glob_noescape="false"><literal_component datatype="string">\*</literal_component></glob_to_regex>
  </local_variable>
  <local_variable id="oval:x:var:4" version="1" datatype="string">
   <glob_to_regex glob_noescape="true"><literal_component datatype="string">\*</literal_component></glob_to_regex>
  </local_variable>
  <local_variable id="oval:x:var:5" version="1" datatype="string">
   <glob_to_regex><literal_component datatype="string">~/files/*.txt</literal_component></glob_to_regex>
  </local_variable>
  <local_variable id="oval:x:var:6" version="1" datatype="string">
   <glob_to_regex><literal_component datatype="string"></literal_component></glob_to_regex>
  </local_variable>
  <local_variable id="oval:x:var:7" version="1" datatype="string">
   <merge delimiter=":" sort="natural">
    <literal_component datatype="string">1</literal_component>
    <literal_component datatype="string">4</literal_component>
    <literal_component datatype="string">5</literal_component>
    <literal_component datatype="string">2</literal_component>
    <literal_component datatype="string">3</literal_component>
   </merge>
  </local_variable>
 </variables>
</oval_definitions>
"""

with TemporaryDirectory() as td:
    p=Path(td)/"glob.xml"; p.write_text(xml,encoding="utf-8")
    ir=oval_ir.parse(p)

r=ir["variable_resolution"]
expected={
 "oval:x:var:1":r"^(?=[^\.])abcd$",
 "oval:x:var:2":r"^(?=[^\.])[^/]*\.txt$",
 "oval:x:var:3":r"^(?=[^\.])\*$",
 "oval:x:var:4":r"^(?=[^\.])\\[^/]*$",
 "oval:x:var:5":r"^(?=[^\.])~/(?=[^\.])files/(?=[^\.])[^/]*\.txt$",
 "oval:x:var:6":r"^$",
 "oval:x:var:7":"1:2:3:4:5",
}
for var_id,value in expected.items():
    assert r[var_id]["status"]=="exact_static",r[var_id]
    assert r[var_id]["values"]==[value],(var_id,r[var_id]["values"],value)

print("PASS: glob_to_regex and natural merge semantics preserved")
