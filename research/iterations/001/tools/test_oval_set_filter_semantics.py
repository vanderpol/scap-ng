#!/usr/bin/env python3
"""Regression tests for OVAL 5.12.3 set/filter semantics."""
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
    <ind:file_object id="oval:x:obj:1" version="1">
      <set set_operator="INTERSECTION">
        <object_reference>oval:x:obj:2</object_reference>
        <object_reference>oval:x:obj:3</object_reference>
        <filter>oval:x:ste:1</filter>
        <filter action="include">oval:x:ste:2</filter>
      </set>
    </ind:file_object>
    <ind:file_object id="oval:x:obj:2" version="1">
      <set set_operator="COMPLEMENT">
        <set>
          <object_reference>oval:x:obj:4</object_reference>
        </set>
        <set>
          <object_reference>oval:x:obj:5</object_reference>
        </set>
      </set>
    </ind:file_object>
    <ind:file_object id="oval:x:obj:3" version="1"/>
    <ind:file_object id="oval:x:obj:4" version="1"/>
    <ind:file_object id="oval:x:obj:5" version="1"/>
  </objects>
  <states>
    <ind:file_state id="oval:x:ste:1" version="1"/>
    <ind:file_state id="oval:x:ste:2" version="1"/>
  </states>
</oval_definitions>
"""

with TemporaryDirectory() as td:
    path = Path(td) / "sets.xml"
    path.write_text(xml, encoding="utf-8")
    ir = oval_ir.parse(path)

objects = {x["id"]: x for x in ir["objects"]}
top = objects["oval:x:obj:1"]["children"][0]
assert top["kind"] == "set", top
assert top["operator"] == "INTERSECTION", top
assert top["evaluation_semantics"]["filters_apply_before_set_operator"] is True, top
assert top["evaluation_semantics"]["filter_default_action"] == "exclude", top

filters = [x for x in top["children"] if x["kind"] == "filter"]
assert filters == [
    {"kind": "filter", "state_ref": "oval:x:ste:1", "action": "exclude"},
    {"kind": "filter", "state_ref": "oval:x:ste:2", "action": "include"},
], filters

nested = objects["oval:x:obj:2"]["children"][0]
assert nested["operator"] == "COMPLEMENT", nested
assert nested["evaluation_semantics"]["complement_is_relative"] is True, nested
assert len([x for x in nested["children"] if x["kind"] == "set"]) == 2, nested

attrs = ir["features"]["attributes"]
assert attrs["set_operator"]["COMPLEMENT"] == 1, attrs
assert attrs["set_operator"]["INTERSECTION"] == 1, attrs
assert attrs["action"]["include"] == 1, attrs

print("PASS: OVAL set/filter defaults, ordering, and recursive operators preserved")
