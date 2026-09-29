#!/usr/bin/env python3
"""Regression tests for CPE product inventory reporting from platform tests."""
from __future__ import annotations

import importlib.util
from pathlib import Path

from lxml import etree

HERE = Path(__file__).resolve().parent

spec_split = importlib.util.spec_from_file_location(
    "splitter", HERE / "scap14_rule_splitter.py"
)
splitter = importlib.util.module_from_spec(spec_split)
spec_split.loader.exec_module(splitter)

spec_ir = importlib.util.spec_from_file_location(
    "benchmark_ir", HERE / "scap14_benchmark_ir.py"
)
benchmark_ir = importlib.util.module_from_spec(spec_ir)
spec_ir.loader.exec_module(benchmark_ir)

cpe_xml = etree.fromstring(b"""<cpe-list xmlns="http://cpe.mitre.org/dictionary/2.0"
 xmlns:xlink="http://www.w3.org/1999/xlink">
  <cpe-item name="cpe:/o:example:os:9">
    <title>Example OS 9</title>
    <check system="http://oval.mitre.org/XMLSchema/oval-definitions-5"
           href="inventory-oval.xml">oval:example:def:9</check>
  </cpe-item>
  <cpe-item name="cpe:2.3:a:example:app:1:*:*:*:*:*:*:*">
    <check system="http://oval.mitre.org/XMLSchema/oval-definitions-5"
           href="app-oval.xml">oval:example:def:10</check>
  </cpe-item>
</cpe-list>
""")

refs = splitter.cpe_dictionary_oval_refs({"component-cpe": cpe_xml})
assert refs == [
    {
        "source_kind": "cpe_dictionary",
        "cpe_name": "cpe:/o:example:os:9",
        "cpe_component": "component-cpe",
        "system": "http://oval.mitre.org/XMLSchema/oval-definitions-5",
        "definition_id": "oval:example:def:9",
        "href": "inventory-oval.xml",
    },
    {
        "source_kind": "cpe_dictionary",
        "cpe_name": "cpe:2.3:a:example:app:1:*:*:*:*:*:*:*",
        "cpe_component": "component-cpe",
        "system": "http://oval.mitre.org/XMLSchema/oval-definitions-5",
        "definition_id": "oval:example:def:10",
        "href": "app-oval.xml",
    },
], refs

resolved = [
    {
        **refs[0],
        "status": "resolved",
        "oval_component": "component-oval",
    },
    {
        **refs[1],
        "status": "resolved",
        "oval_component": "component-app-oval",
    },
]

bound = benchmark_ir.bind_platform_refs(
    [
        "cpe:/o:example:os:9",
        "cpe:2.3:a:example:app:1:*:*:*:*:*:*:*",
    ],
    [],
    resolved,
)

os_platform = bound[0]
assert os_platform["kind"] == "cpe_name"
assert os_platform["inventory_bindings"][0]["definition_id"] == "oval:example:def:9"
assert os_platform["inventory_output"] == {
    "emit_when": "platform_true",
    "role": "descriptive_target_inventory",
    "product_kind": "operating_system",
    "identifiers": [
        {
            "scheme": "cpe",
            "binding": "uri",
            "value": "cpe:/o:example:os:9",
        }
    ],
}, os_platform

app_platform = bound[1]
assert app_platform["inventory_output"]["product_kind"] == "application"
assert app_platform["inventory_output"]["identifiers"][0]["binding"] == "formatted_string"

# Inventory reporting is side-output metadata. It must not create or alter an
# executable platform expression.
for row in bound:
    assert "expression" not in row
    assert row["inventory_output"]["role"] == "descriptive_target_inventory"

print("PASS: source CPE dictionary bindings become non-decisional target inventory outputs")
