#!/usr/bin/env python3
"""Regression tests for OVAL glob_to_regex and natural merge semantics."""
from pathlib import Path
from tempfile import TemporaryDirectory
import importlib.util

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("oval_ir", HERE/"oval_semantic_ir.py")
oval_ir=importlib.util.module_from_spec(spec)
spec.loader.exec_module(oval_ir)

cases = {
    "abcd": r"^(?=[^\.])abcd$",
    "*.txt": r"^(?=[^\.])[^/]*\.txt$",
    "x?": r"^(?=[^\.])x[^/]$",
    r"\*": r"^(?=[^\.])\*$",
    "~/files/*.txt": r"^(?=[^\.])~/(?=[^\.])files/(?=[^\.])[^/]*\.txt$",
    "": r"^$",
}
for pattern, expected in cases.items():
    actual=oval_ir.oval_glob_to_regex(pattern, noescape=False)
    assert actual==expected,(pattern,actual,expected)

assert oval_ir.oval_glob_to_regex(r"\*", noescape=True) == r"^(?=[^\.])\\[^/]*$"
assert oval_ir.oval_glob_to_regex(r"\?", noescape=True) == r"^(?=[^\.])\\[^/]$"
assert oval_ir.oval_glob_to_regex("x[[:digit:]]\\*", noescape=False) == r"^(?=[^\.])x[[:digit:]]\*$"

xml="""<?xml version="1.0" encoding="UTF-8"?>
<oval_definitions xmlns="http://oval.mitre.org/XMLSchema/oval-definitions-5">
 <generator/>
 <variables>
  <local_variable id="oval:x:var:1" version="1" datatype="string">
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
    p=Path(td)/"natural.xml"; p.write_text(xml,encoding="utf-8")
    ir=oval_ir.parse(p)
assert ir["variable_resolution"]["oval:x:var:1"]["values"] == ["1:2:3:4:5"]
print("PASS: glob_to_regex and natural merge semantics preserved")
