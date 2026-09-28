#!/usr/bin/env python3
"""Regression tests for the emitted XCCDF assessment processing plan."""
from __future__ import annotations

import importlib.util
from pathlib import Path

from lxml import etree

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("benchmark_ir",HERE/"scap14_benchmark_ir.py")
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

xml=b"""<Benchmark xmlns="http://checklists.nist.gov/xccdf/1.2" id="b">
 <status>draft</status><title>b</title>
 <platform idref="cpe:2.3:o:example:os:1:*:*:*:*:*:*:*"/>
 <Rule id="r0" selected="true"><title>r0</title></Rule>
 <Group id="g1" selected="true">
  <title>g1</title>
  <Rule id="r1" selected="true">
   <title>r1</title>
   <requires idref="r0 r2"/>
   <conflicts idref="r3"/>
  </Rule>
  <Rule id="r2" selected="false"><title>r2</title></Rule>
 </Group>
 <Rule id="r3" selected="true"><title>r3</title></Rule>
</Benchmark>"""
benchmark=etree.fromstring(xml)
platforms=mod.platforms(benchmark)
rules=list(mod.walk_rules(benchmark,inherited_platforms=platforms))
groups=list(mod.walk_groups(benchmark,inherited_platforms=platforms))
plan=mod.build_traversal_plan(benchmark,rules,groups)

assert [(x["kind"],x["id"]) for x in plan]==[
    ("rule","r0"),
    ("group","g1"),
    ("rule","r1"),
    ("rule","r2"),
    ("rule","r3"),
]
assert [x["source_order"] for x in plan]==list(range(5))
r1=next(x for x in plan if x["id"]=="r1")
assert r1["parent_path"]==["g1"]
assert r1["requires"]==[["r0","r2"]]
assert r1["conflicts"]==["r3"]
assert r1["effective_platform_refs"]==[
    "cpe:2.3:o:example:os:1:*:*:*:*:*:*:*"
]

model=mod.policy_processing_model(plan)
assert model["item_traversal"]["requires"]["within_clause"]=="OR"
assert model["item_traversal"]["requires"]["across_clauses"]=="AND"
assert model["item_traversal"]["selection_transition"]==(
    "requires_conflicts_may_only_change_selected_true_to_false"
)
assert model["applicability"]["platform_skip_does_not_mutate_selected_state"] is True
assert model["check_processing"]["backtracking"] is False

print("PASS: XCCDF source-order assessment processing plan")
