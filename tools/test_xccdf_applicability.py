#!/usr/bin/env python3
"""Regression tests for XCCDF/CPE applicability migration semantics."""
from __future__ import annotations

import importlib.util
from pathlib import Path

from lxml import etree

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("benchmark_ir",HERE/"scap14_benchmark_ir.py")
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

xml=b"""<Benchmark xmlns="http://checklists.nist.gov/xccdf/1.2"
 xmlns:cpe="http://cpe.mitre.org/language/2.0"
 id="bench">
 <status>draft</status><title>test</title>
 <platform idref="#platform-a"/>
 <cpe:platform-specification>
  <cpe:platform id="platform-a">
   <cpe:title>Platform A</cpe:title>
   <cpe:logical-test operator="AND" negate="false">
    <cpe:fact-ref name="cpe:2.3:o:example:os:1:*:*:*:*:*:*:*"/>
    <cpe:logical-test operator="OR" negate="true">
     <cpe:fact-ref name="cpe:2.3:a:example:app:2:*:*:*:*:*:*:*"/>
     <cpe:check-fact-ref system="http://oval.mitre.org/XMLSchema/oval-definitions-5"
       href="applicability-oval.xml" id-ref="oval:example:def:1"/>
    </cpe:logical-test>
   </cpe:logical-test>
  </cpe:platform>
  <cpe:platform id="platform-b">
   <cpe:logical-test operator="OR" negate="false">
    <cpe:fact-ref name="cpe:2.3:o:example:other:1:*:*:*:*:*:*:*"/>
   </cpe:logical-test>
  </cpe:platform>
 </cpe:platform-specification>
 <Group id="g1">
  <title>g1</title>
  <Rule id="r1"><title>r1</title></Rule>
 </Group>
 <Group id="g2">
  <title>g2</title>
  <platform idref="#platform-b"/>
  <Rule id="r2"><title>r2</title></Rule>
  <Rule id="r3"><title>r3</title><platform idref="cpe:2.3:o:direct:os:1:*:*:*:*:*:*:*"/></Rule>
 </Group>
</Benchmark>"""

benchmark=etree.fromstring(xml)
defs=mod.cpe_platform_definitions(benchmark)
assert [x["id"] for x in defs]==["platform-a","platform-b"]

expr=defs[0]["expression"]
assert expr["kind"]=="logical_test"
assert expr["operator"]=="AND"
assert expr["negate"] is False
assert expr["children"][0]["kind"]=="cpe_name"
nested=expr["children"][1]
assert nested["operator"]=="OR"
assert nested["negate"] is True
assert nested["children"][1]=={
    "kind":"check_fact",
    "system":"http://oval.mitre.org/XMLSchema/oval-definitions-5",
    "href":"applicability-oval.xml",
    "id_ref":"oval:example:def:1",
}

bound=mod.bind_platform_refs(
    ["#platform-a","cpe:2.3:o:direct:os:1:*:*:*:*:*:*:*"],defs
)
assert bound[0]["kind"]=="local_cpe_expression"
assert bound[0]["platform_id"]=="platform-a"
assert bound[1]["kind"]=="cpe_name"

rules={x["id"]:x for x in mod.walk_rules(
    benchmark,
    inherited_platforms=mod.platforms(benchmark),
)}
assert rules["r1"]["effective_platform_refs"]==["#platform-a"]
assert rules["r2"]["effective_platform_refs"]==["#platform-b"]
assert rules["r3"]["effective_platform_refs"]==[
    "cpe:2.3:o:direct:os:1:*:*:*:*:*:*:*"
]

groups={x["id"]:x for x in mod.walk_groups(
    benchmark,
    inherited_platforms=mod.platforms(benchmark),
)}
assert groups["g1"]["effective_platform_refs"]==["#platform-a"]
assert groups["g2"]["effective_platform_refs"]==["#platform-b"]

print("PASS: XCCDF CPE Boolean applicability and nearest-ancestor inheritance")
