#!/usr/bin/env python3
"""Regression tests for XCCDF complex-check preservation and OVAL seeding."""
from __future__ import annotations

import importlib.util
from pathlib import Path

from lxml import etree

HERE=Path(__file__).resolve().parent

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

splitter=load("splitter",HERE/"scap14_rule_splitter.py")
benchmark_ir=load("benchmark_ir",HERE/"scap14_benchmark_ir.py")

xml=b"""<Benchmark xmlns="http://checklists.nist.gov/xccdf/1.2" id="b">
 <status>draft</status><title>b</title>
 <Rule id="r1">
  <title>complex</title>
  <complex-check operator="AND" negate="false">
   <check system="http://oval.mitre.org/XMLSchema/oval-definitions-5">
    <check-content-ref href="a.xml" name="oval:example:def:1"/>
   </check>
   <complex-check operator="OR" negate="true">
    <check system="http://oval.mitre.org/XMLSchema/oval-definitions-5">
     <check-content-ref href="a.xml" name="oval:example:def:2"/>
    </check>
    <check system="http://scap.nist.gov/schema/ocil/2">
     <check-content-ref href="q.xml" name="ocil:example:questionnaire:1"/>
    </check>
   </complex-check>
  </complex-check>
 </Rule>
</Benchmark>"""
benchmark=etree.fromstring(xml)
rule=next(x for x in benchmark if splitter.local(x.tag)=="Rule")

nodes=splitter.effective_rule_check_nodes(rule)
assert len(nodes)==3
rows=splitter.rule_oval_refs(benchmark)
assert len(rows)==1
assert [x["name"] for x in rows[0]["checks"]]==[
    "oval:example:def:1",
    "oval:example:def:2",
    "ocil:example:questionnaire:1",
]

model=benchmark_ir.rule_check_model(rule)
assert model["kind"]=="complex_check"
assert model["operator"]=="AND"
assert model["negate"] is False
assert model["children"][0]["kind"]=="check"
nested=model["children"][1]
assert nested["kind"]=="complex_check"
assert nested["operator"]=="OR"
assert nested["negate"] is True
assert [x["kind"] for x in nested["children"]]==["check","check"]

flat=benchmark_ir.flatten_check_model(model)
assert len(flat)==3
assert flat[0]["content_refs"][0]["name"]=="oval:example:def:1"
assert flat[1]["content_refs"][0]["name"]=="oval:example:def:2"

print("PASS: XCCDF complex-check Boolean tree and nested OVAL references")
