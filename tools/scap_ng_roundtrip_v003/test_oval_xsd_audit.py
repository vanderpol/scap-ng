#!/usr/bin/env python3
"""Synthetic 45-file contract check for pinned XSD audit reference accounting."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from xsd_effective_defaults import inventory as resolve_type_defaults

SCRIPT = Path(__file__).with_name("audit_oval_xsd_defaults.py")
SCHEMA = """<?xml version="1.0"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
 xmlns:t="urn:scap-ng:audit-test" targetNamespace="urn:scap-ng:audit-test">
 <xs:attributeGroup name="attrs">
  <xs:attribute name="flag" type="xs:string" default="yes"/>
 </xs:attributeGroup>
 <xs:complexType name="base">
  <xs:attributeGroup ref="t:attrs"/>
 </xs:complexType>
 <xs:complexType name="derived">
  <xs:complexContent><xs:extension base="t:base">
   <xs:attribute name="fixedFlag" type="xs:string" fixed="set"/>
  </xs:extension></xs:complexContent>
 </xs:complexType>
 <xs:complexType name="broken">
  <xs:complexContent><xs:extension base="t:missing"/></xs:complexContent>
 </xs:complexType>
 <xs:complexType name="builtin">
  <xs:simpleContent><xs:extension base="xs:string"/></xs:simpleContent>
 </xs:complexType>
</xs:schema>"""
EMPTY = '<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema" targetNamespace="urn:test:empty"/>'


class SchemaAuditTests(unittest.TestCase):
    def test_named_links_and_unresolved_reference_are_distinct(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            schemas = root / "schemas"
            schemas.mkdir()
            (schemas / "00.xsd").write_text(SCHEMA, encoding="utf-8")
            for number in range(1, 45):
                (schemas / f"{number:02}.xsd").write_text(EMPTY, encoding="utf-8")
            target = root / "out"
            subprocess.run(
                [sys.executable, str(SCRIPT), "--schemas", str(schemas),
                 "--out", str(target)], check=True, capture_output=True, text=True
            )
            summary = json.loads((target / "summary.json").read_text())
            counts = summary["named_reference_resolution"]
            self.assertEqual(summary["upstream_xsd_files"], 45)
            self.assertEqual(summary["explicit_defaults"], 1)
            self.assertEqual(summary["fixed_values"], 1)
            self.assertEqual(counts["resolved_global"], 2)
            self.assertEqual(counts["builtin_xsd"], 1)
            self.assertEqual(counts["unresolved_global"], 1)
            transitive = json.loads((target / "transitive-type-defaults.json").read_text())
            by_type = {row["type"]: row for row in transitive["types"]}
            self.assertEqual(by_type["base"]["defaults"]["flag"]["value"], "yes")
            self.assertEqual(by_type["derived"]["defaults"]["flag"]["value"], "yes")
            self.assertEqual(by_type["derived"]["defaults"]["fixedFlag"]["value"], "set")
            self.assertEqual(by_type["derived"]["status"], "resolved")
            self.assertEqual(by_type["broken"]["status"], "incomplete")
            self.assertTrue(any(b["reason"] == "not_found"
                                for b in by_type["broken"]["blockers"]))
            self.assertEqual(by_type["builtin"]["status"], "resolved")
            rows = json.loads((target / "named-reference-resolution.json").read_text())
            self.assertTrue(any(row["status"] == "unresolved_global"
                                and row["reference"] == "t:missing" for row in rows))

    def test_simple_content_base_can_be_a_named_simple_type(self):
        schema = """<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
          xmlns:t="urn:example" targetNamespace="urn:example">
          <xs:simpleType name="SchemaVersionPattern">
            <xs:restriction base="xs:string"/>
          </xs:simpleType>
          <xs:complexType name="SchemaVersionType">
            <xs:simpleContent>
              <xs:extension base="t:SchemaVersionPattern">
                <xs:attribute name="platform" type="xs:string" default="X"/>
              </xs:extension>
            </xs:simpleContent>
          </xs:complexType>
        </xs:schema>"""
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / "one.xsd").write_text(schema, encoding="utf-8")
            report = resolve_type_defaults(folder)
            self.assertEqual(report["summary"]["incomplete_types"], 0)
            self.assertEqual(report["summary"]["resolved_types"], 1)
            self.assertEqual(report["types"][0]["defaults"]["platform"]["value"], "X")



if __name__ == "__main__":
    unittest.main()
