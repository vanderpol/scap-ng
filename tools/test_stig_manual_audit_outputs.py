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
from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
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

        audit = yaml.safe_load((native / "conversion-audit.json").read_text(encoding="utf-8"))
        assert audit["success"] is True
        assert audit["unhandled_constructs"] == {"benchmark_children": [], "rule_children": []}
        assert audit["counts"]["source_rules"] == 1
        assert audit["counts"]["native_rules"] == 1
        assert audit["schema_validation"]["valid"] is True

        benchmark = yaml.safe_load((native / "benchmark.yaml").read_text(encoding="utf-8"))
        benchmark_schema = yaml.safe_load((ROOT / "schema/v0.2.0/benchmark.schema.json").read_text(encoding="utf-8"))
        assert not list(Draft202012Validator(benchmark_schema).iter_errors(benchmark))
        assert benchmark["benchmark"]["rules"] == ["SV-243502"]
        assert benchmark["benchmark"]["profiles"][0]["disabled_rules"] == ["SV-243502"]

        rule_doc = yaml.safe_load((native / "rules" / "SV-243502.rule.yaml").read_text(encoding="utf-8"))
        rule_schema = yaml.safe_load((ROOT / "schema/v0.2.0/rule.schema.json").read_text(encoding="utf-8"))
        assert not list(Draft202012Validator(rule_schema).iter_errors(rule_doc))
        rule = rule_doc["rule"]
        assert any(x == {"scheme": "disa-vulnerability-id", "value": "V-243502"} for x in rule["identifiers"])
        assert rule["assessment_choices"]["manual"]["assessment"].endswith("SV-243502.manual.assessment.yaml")
        assert rule["discussion"] == "Privileged membership discussion."
        assert "<VulnDiscussion>" not in rule["discussion"]
        assert "CCI-000366" in str(rule["identifiers"])

        assessment_doc = yaml.safe_load(
            (native / "assessments" / "manual" / "SV-243502.manual.assessment.yaml").read_text(encoding="utf-8")
        )
        assessment_schema = yaml.safe_load((ROOT / "schema/v0.2.0/manual-assessment.schema.json").read_text(encoding="utf-8"))
        assert not list(Draft202012Validator(assessment_schema).iter_errors(assessment_doc))
        assessment = assessment_doc["assessment"]
        assert assessment["mode"] == "manual"
        assert assessment["class"] == "compliance"
        assert assessment["purpose"] == "assessment"
        assert assessment["response"]["type"] == "stig-manual-compliance"
        assert [choice["outcome"] for choice in assessment["response"]["choices"]] == [
            "true", "false", "unknown", "not_applicable"
        ]
        assert assessment["response"]["allow_comment"] is True
        assert assessment["response"]["allow_evidence"] is True
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
            assert "true" in lookup
            assert "false" in lookup
            assert "unknown" in lookup
            assert "Evidence / Notes" in sheet
            assert "Evaluator / Reviewer" in sheet

    print("STIG manual conversion + HTML/XLSX focused regression: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
