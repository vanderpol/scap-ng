#!/usr/bin/env python3
"""Regression tests for XCCDF 1.2 profile/selection semantics used by migration."""
from __future__ import annotations

import importlib.util
from pathlib import Path

from lxml import etree

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("benchmark_ir",HERE/"scap14_benchmark_ir.py")
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

rules=[
    {"id":"rule-1","cluster_id":"cluster-a"},
    {"id":"rule-2","cluster_id":"cluster-a"},
    {"id":"rule-3","cluster_id":None},
]
groups=[
    {"id":"group-1","cluster_id":"cluster-a"},
]
values=[
    {"id":"value-1","cluster_id":"cluster-v"},
]
profiles=[
    {
        "id":"profile-base",
        "extends":None,
        "actions":[
            {
                "kind":"select",
                "attributes":{"idref":"cluster-a","selected":"false"},
                "value":None,
                "source_tree":{},
            },
            {
                "kind":"refine-rule",
                "attributes":{"idref":"rule-2","selector":"automated"},
                "value":None,
                "source_tree":{},
            },
        ],
    },
    {
        "id":"profile-child",
        "extends":"profile-base",
        "actions":[
            {
                "kind":"select",
                "attributes":{"idref":"rule-1","selected":"true"},
                "value":None,
                "source_tree":{},
            },
            {
                "kind":"set-value",
                "attributes":{"idref":"cluster-v"},
                "value":"42",
                "source_tree":{},
            },
        ],
    },
]

resolved={x["id"]:x for x in mod.resolve_profiles(profiles,rules,groups,values)}
child=resolved["profile-child"]
assert child["resolution_status"]=="resolved",child
assert child["inheritance_chain"]==["profile-base","profile-child"],child
assert [x["effective_order"] for x in child["effective_actions"]]==[0,1,2,3]

first=child["effective_actions"][0]
assert first["source_profile_id"]=="profile-base"
assert {(x["kind"],x["id"]) for x in first["targets"]}=={
    ("rule","rule-1"),
    ("rule","rule-2"),
    ("group","group-1"),
}

third=child["effective_actions"][2]
assert third["source_profile_id"]=="profile-child"
assert third["targets"]==[{"kind":"rule","id":"rule-1","match":"id"}]

fourth=child["effective_actions"][3]
assert fourth["targets"]==[{"kind":"value","id":"value-1","match":"cluster-id"}]

# XCCDF requires semantics are OR within one requires element, AND across
# multiple requires elements; conflicts are single idrefs.
node=etree.fromstring(
    b"""<Rule xmlns="http://checklists.nist.gov/xccdf/1.2">
      <requires idref="rule-a rule-b"/>
      <requires idref="group-c"/>
      <conflicts idref="rule-d"/>
    </Rule>"""
)
assert mod.requires_conditions(node)==[["rule-a","rule-b"],["group-c"]]
assert mod.idrefs(node,"conflicts")==["rule-d"]

# Profile extension cycles must fail loudly.
cyclic=[
    {"id":"a","extends":"b","actions":[]},
    {"id":"b","extends":"a","actions":[]},
]
try:
    mod.resolve_profiles(cyclic,[],[],[])
except ValueError as exc:
    assert "cycle" in str(exc)
else:
    raise AssertionError("profile extension cycle was not rejected")

print("PASS: XCCDF profile inheritance, cluster targeting, and requires grouping")
