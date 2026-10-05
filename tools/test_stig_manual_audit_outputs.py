#!/usr/bin/env python3
"""Focused regression for STIG-manual conversion and optional audit outputs."""
from __future__ import annotations

import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

import yaml

HERE = Path(__file__).resolve().parent
CONVERTER = HERE / "stig_manual_to_scapng.py"
RENDERER = HERE / "render_stig_audit_outputs.py"

XCCDF = """<?xml version="1.0" encoding="UTF-8"?>
<Benchmark xmlns="http://checklists.nist.gov/xccdf/1.1" id="Active_Directory_Forest_STIG">
  <title>Active Directory Forest Test STIG</title>
  <description>Small regression fixture.</description>
  <version>3.2</version>
  <Profile id="test-profile">
    <title>Test Profile</title>
    <select idref="V-243502" selected="false"/>
  </Profile>
  <Group id="V-243502">
    <title>V-243502</title>
    <Rule id="SV-243502r1026198_rule" severity="medium">
      <version>AD.0017</version>
      <title>Membership &amp; schema &lt;admins&gt; must be limited.</title>
      <description><VulnDiscussion xmlns="">Privileged membership discussion.</VulnDiscussion></description>
      <ident system="http://cyber.mil/cci">CCI-000366</ident>
      <check system="http://checklists.nist.gov/xccdf/1.1">
        <check-content>Inspect Schema Admins.
Run the administrative review command.

If unauthorized accounts exist, this is a finding.</check-content>
      </check>
      <fixtext>Remove unauthorized members.</fixtext>
    </Rule>
  </Group>
</Benchmark>
"""


def run(*args: str) -> None:
    subprocess.run([sys.executable, *args], check=True)


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        source = root / "manual.xml"
        native = root / "native"
        html = root / "audit.html"
        xlsx = root / "audit.xlsx"
        source.write_text(XCCDF, encoding="utf-8")

        run(str(CONVERTER), str(source), "--output-dir", str(native))

        benchmark = yaml.safe_load((native / "benchmark.yaml").read_text(encoding="utf-8"))
        assert benchmark["benchmark"]["rules"] == ["AD.0017"]
        assert benchmark["benchmark"]["profiles"][0]["disabled_rules"] == ["AD.0017"]

        rule_doc = yaml.safe_load((native / "rules" / "AD.0017.yaml").read_text(encoding="utf-8"))
        rule = rule_doc["rule"]
        assert rule["vulnerability_id"] == "V-243502"
        assert rule["assessment_choices"][0]["name"] == "manual"
        assert rule["discussion"] == "Privileged membership discussion."
        assert "<VulnDiscussion>" not in rule["discussion"]
        assert "CCI-000366" in str(rule["idents"])

        assessment = yaml.safe_load(
            (native / "assessments" / "manual" / "AD.0017.manual.yaml").read_text(encoding="utf-8")
        )["assessment"]
        assert assessment["mode"] == "manual"
        assert "Schema Admins" in assessment["procedure"]
        assert "\n" in assessment["procedure"]
        assert "\n\n" in assessment["procedure"]

        run(
            str(RENDERER),
            str(native),
            "--html",
            str(html),
            "--xlsx",
            str(xlsx),
        )

        html_text = html.read_text(encoding="utf-8")
        assert "Active Directory Forest Test STIG" in html_text
        assert "Check Procedure" in html_text
        assert "&lt;admins&gt;" in html_text
        assert "<admins>" not in html_text

        with zipfile.ZipFile(xlsx) as zf:
            workbook = zf.read("xl/workbook.xml").decode("utf-8")
            sheet = zf.read("xl/worksheets/sheet1.xml").decode("utf-8")
            lookup = zf.read("xl/worksheets/sheet2.xml").decode("utf-8")
            ET.fromstring(workbook)
            ET.fromstring(sheet)
            ET.fromstring(lookup)
            assert 'name="Result Options"' in workbook
            assert 'state="hidden"' in workbook
            assert "<dataValidations count=\"1\">" in sheet
            assert "'Result Options'!$A$2:$A$5" in sheet
            assert "Pass" in lookup
            assert "not_evaluated" in lookup
            assert "Evidence / Notes" in sheet
            assert "Evaluator / Reviewer" in sheet

    print("STIG manual conversion + HTML/XLSX focused regression: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
