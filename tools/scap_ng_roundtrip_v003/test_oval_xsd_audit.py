#!/usr/bin/env python3
"""Synthetic 45-file contract check for pinned XSD audit reference accounting."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

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
            rows = json.loads((target / "named-reference-resolution.json").read_text())
            self.assertTrue(any(row["status"] == "unresolved_global"
                                and row["reference"] == "t:missing" for row in rows))


if __name__ == "__main__":
    unittest.main()
