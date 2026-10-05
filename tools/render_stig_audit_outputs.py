#!/usr/bin/env python3
"""Render optional human-facing STIG review outputs from native SCAP-NG YAML.

The renderer reads only native SCAP-NG YAML.  It never re-opens the legacy
XCCDF source.  HTML and XLSX are optional edge outputs; native NG remains the
primary artifact.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

import yaml


RESULT_OPTIONS = [
    ("Pass", "pass"),
    ("Fail", "fail"),
    ("Not Applicable", "not_applicable"),
    ("Not Evaluated", "not_evaluated"),
]

COLUMNS = [
    "Vulnerability ID",
    "Rule ID",
    "STIG ID",
    "Title",
    "Severity",
    "Group",
    "Discussion",
    "Check Procedure",
    "Fix / Remediation",
    "CCI / References",
    "Result",
    "Evidence / Notes",
    "Finding / Comments",
    "Evaluator / Reviewer",
    "Review Date",
]


def load_yaml(path: Path) -> dict:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    return value if isinstance(value, dict) else {}


def discover_rules(native_root: Path) -> list[dict]:
    candidates = []
    for pattern in ("rules/*.yaml", "policy/rules/*.yaml"):
        candidates.extend(native_root.glob(pattern))
    if not candidates:
        raise SystemExit(f"No native Rule YAML found under {native_root}")
    rules = []
    for path in sorted(set(candidates)):
        doc = load_yaml(path)
        rule = doc.get("rule", doc)
        if isinstance(rule, dict) and rule.get("id"):
            rules.append(rule)
    return rules


def discover_assessments(native_root: Path) -> dict[str, dict]:
    found = {}
    for path in sorted(native_root.rglob("*.yaml")):
        if "assessment" not in path.as_posix().lower():
            continue
        doc = load_yaml(path)
        assessment = doc.get("assessment")
        if isinstance(assessment, dict) and assessment.get("id"):
            found[str(assessment["id"])] = assessment
    return found


def benchmark(native_root: Path) -> dict:
    doc = load_yaml(native_root / "benchmark.yaml")
    value = doc.get("benchmark", doc)
    if not isinstance(value, dict):
        raise SystemExit("benchmark.yaml does not contain a Benchmark mapping")
    return value


def localized_text(value) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        for row in value:
            if isinstance(row, dict) and row.get("text") is not None:
                return str(row["text"])
    return ""


def version_text(value) -> str:
    if isinstance(value, dict):
        return str(value.get("value") or "")
    return str(value or "")


def identifier_value(rule: dict, scheme: str) -> str:
    for ident in rule.get("identifiers", []) or []:
        if isinstance(ident, dict) and ident.get("scheme") == scheme and ident.get("value"):
            return str(ident["value"])
    return ""


def first_stig_id(rule: dict) -> str:
    return identifier_value(rule, "disa-stig-id")


def cci_and_references(rule: dict) -> str:
    values = []
    for ident in rule.get("identifiers", []) or []:
        if isinstance(ident, dict):
            value = ident.get("value")
            if value:
                values.append(str(value))
    for ref in rule.get("references", []) or []:
        if isinstance(ref, dict):
            bits = [str(v) for v in ref.values() if v not in (None, "")]
            if bits:
                values.append(" | ".join(bits))
        elif ref not in (None, ""):
            values.append(str(ref))
    return "; ".join(dict.fromkeys(values))


def group_map(bench: dict) -> dict[str, str]:
    out = {}
    def walk(groups):
        for group in groups or []:
            if not isinstance(group, dict):
                continue
            label = str(group.get("title") or group.get("id") or "")
            for rid in group.get("rules", []) or []:
                out.setdefault(str(rid), label)
            walk(group.get("groups", []))
    walk(bench.get("groups", []))
    return out


def procedure_for(rule: dict, assessments: dict[str, dict]) -> str:
    if rule.get("check"):
        return str(rule["check"])
    for choice in (rule.get("assessment_choices") or {}).values():
        if not isinstance(choice, dict):
            continue
        aid = Path(str(choice.get("assessment") or "")).name.replace(".assessment.yaml", "")
        assessment = assessments.get(aid)
        if assessment and assessment.get("mode") == "manual":
            return str(assessment.get("procedure") or "")
    return ""


def row_for(rule: dict, assessments: dict[str, dict], groups: dict[str, str]) -> list[str]:
    return [
        identifier_value(rule, "disa-vulnerability-id"),
        str(rule.get("id") or ""),
        first_stig_id(rule),
        str(rule.get("title") or ""),
        str(rule.get("severity") or ""),
        groups.get(str(rule.get("id") or ""), ""),
        str(rule.get("discussion") or rule.get("description") or ""),
        procedure_for(rule, assessments),
        str((rule.get("remediation") or {}).get("guidance") or ""),
        cci_and_references(rule),
        "",
        "",
        "",
        "",
        "",
    ]


def render_html(native_root: Path, output: Path) -> None:
    bench = benchmark(native_root)
    assessments = discover_assessments(native_root)
    rules = discover_rules(native_root)
    groups = group_map(bench)
    title = localized_text(bench.get("title")) or str(bench.get("id") or "SCAP-NG STIG Review")
    nav = []
    sections = []
    for idx, rule in enumerate(rules, start=1):
        rid = str(rule.get("id") or f"rule-{idx}")
        anchor = re.sub(r"[^A-Za-z0-9_-]+", "-", rid)
        label = str(rule.get("title") or rid)
        nav.append(f'<li><a href="#{html.escape(anchor)}">{html.escape(rid)} — {html.escape(label)}</a></li>')
        fields = [
            ("Vulnerability ID", identifier_value(rule, "disa-vulnerability-id")),
            ("STIG ID", first_stig_id(rule)),
            ("Severity", str(rule.get("severity") or "")),
            ("Group", groups.get(rid, "")),
            ("CCI / References", cci_and_references(rule)),
        ]
        meta = "".join(
            f"<dt>{html.escape(k)}</dt><dd>{html.escape(v)}</dd>"
            for k, v in fields if v
        )
        sections.append(
            f"""<article class="rule" id="{html.escape(anchor)}">
<h2>{html.escape(rid)} — {html.escape(label)}</h2>
<dl>{meta}</dl>
<h3>Discussion</h3><pre>{html.escape(str(rule.get("discussion") or rule.get("description") or ""))}</pre>
<h3>Check Procedure</h3><pre>{html.escape(procedure_for(rule, assessments))}</pre>
<h3>Fix / Remediation</h3><pre>{html.escape(str((rule.get("remediation") or {}).get("guidance") or ""))}</pre>
</article>"""
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>{html.escape(title)}</title>
<style>
body{{font-family:system-ui,-apple-system,Segoe UI,sans-serif;max-width:1100px;margin:2rem auto;padding:0 1rem;line-height:1.45}}
header{{border-bottom:1px solid #999;margin-bottom:1.5rem}} nav{{margin:1rem 0 2rem}}
.rule{{border-top:2px solid #555;padding-top:1rem;margin-top:2rem}}
dl{{display:grid;grid-template-columns:max-content 1fr;gap:.25rem 1rem}}
dt{{font-weight:700}} dd{{margin:0}} pre{{white-space:pre-wrap;font:inherit;background:#f6f6f6;padding:1rem;border-radius:.35rem}}
a{{color:inherit}} small{{color:#555}}
</style></head><body>
<header><h1>{html.escape(title)}</h1>
<p><strong>Version:</strong> {html.escape(version_text(bench.get("version")))}</p>
<p>{html.escape(localized_text(bench.get("description")))}</p>
<small>Generated from native SCAP-NG authoring content.</small></header>
<nav><h2>Rules</h2><ol>{"".join(nav)}</ol></nav>
{"".join(sections)}
</body></html>""",
        encoding="utf-8",
    )


def col_letter(n: int) -> str:
    out = ""
    while n:
        n, rem = divmod(n - 1, 26)
        out = chr(65 + rem) + out
    return out


def inline_cell(ref: str, value: str, style: int = 0) -> str:
    escaped = xml_escape(value or "")
    style_attr = f' s="{style}"' if style else ""
    preserve = ' xml:space="preserve"' if (value or "").strip() != (value or "") else ""
    return f'<c r="{ref}" t="inlineStr"{style_attr}><is><t{preserve}>{escaped}</t></is></c>'


def sheet_xml(rows: list[list[str]]) -> str:
    widths = [16, 22, 18, 42, 12, 28, 55, 65, 55, 36, 18, 35, 35, 24, 16]
    cols = "".join(
        f'<col min="{i}" max="{i}" width="{w}" customWidth="1"/>'
        for i, w in enumerate(widths, start=1)
    )
    row_xml = []
    all_rows = [COLUMNS] + rows
    for r_idx, row in enumerate(all_rows, start=1):
        cells = []
        style = 1 if r_idx == 1 else 2
        for c_idx, value in enumerate(row, start=1):
            cells.append(inline_cell(f"{col_letter(c_idx)}{r_idx}", str(value or ""), style))
        row_xml.append(f'<row r="{r_idx}">{"".join(cells)}</row>')
    last = max(2, len(all_rows))
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
<sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews>
<cols>{cols}</cols>
<sheetData>{"".join(row_xml)}</sheetData>
<autoFilter ref="A1:O{last}"/>
<dataValidations count="1"><dataValidation type="list" allowBlank="1" showErrorMessage="1" sqref="K2:K{last}"><formula1>'Result Options'!$A$2:$A$5</formula1></dataValidation></dataValidations>
</worksheet>'''


def lookup_sheet_xml() -> str:
    rows = [["Display Label", "SCAP-NG Outcome"]] + [[a, b] for a, b in RESULT_OPTIONS]
    out = []
    for r_idx, row in enumerate(rows, start=1):
        cells = [inline_cell(f"{col_letter(c_idx)}{r_idx}", value, 1 if r_idx == 1 else 0)
                 for c_idx, value in enumerate(row, start=1)]
        out.append(f'<row r="{r_idx}">{"".join(cells)}</row>')
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>{"".join(out)}</sheetData></worksheet>'''


def styles_xml() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
<fonts count="2"><font><sz val="11"/><name val="Calibri"/></font><font><b/><sz val="11"/><name val="Calibri"/></font></fonts>
<fills count="3"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill><fill><patternFill patternType="solid"><fgColor rgb="FFD9EAF7"/><bgColor indexed="64"/></patternFill></fill></fills>
<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>
<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
<cellXfs count="3"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/><xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyFill="1" applyFont="1" applyAlignment="1"><alignment wrapText="1" vertical="top"/></xf><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0" applyAlignment="1"><alignment wrapText="1" vertical="top"/></xf></cellXfs>
<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>
</styleSheet>'''


def write_xlsx(native_root: Path, output: Path) -> None:
    bench = benchmark(native_root)
    assessments = discover_assessments(native_root)
    groups = group_map(bench)
    rows = [row_for(rule, assessments, groups) for rule in discover_rules(native_root)]
    output.parent.mkdir(parents=True, exist_ok=True)
    files = {
        "[Content_Types].xml": '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/><Override PartName="/xl/worksheets/sheet2.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/><Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/></Types>''',
        "_rels/.rels": '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>''',
        "xl/workbook.xml": '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Audit Checklist" sheetId="1" r:id="rId1"/><sheet name="Result Options" sheetId="2" state="hidden" r:id="rId2"/></sheets></workbook>''',
        "xl/_rels/workbook.xml.rels": '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet2.xml"/><Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>''',
        "xl/styles.xml": styles_xml(),
        "xl/worksheets/sheet1.xml": sheet_xml(rows),
        "xl/worksheets/sheet2.xml": lookup_sheet_xml(),
    }
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name, value in files.items():
            zf.writestr(name, value)


def main() -> int:
    ap = argparse.ArgumentParser(description="Render optional HTML/XLSX from native SCAP-NG STIG content.")
    ap.add_argument("native_root", type=Path)
    ap.add_argument("--html", dest="html_path", type=Path)
    ap.add_argument("--xlsx", dest="xlsx_path", type=Path)
    args = ap.parse_args()
    if not args.html_path and not args.xlsx_path:
        ap.error("request at least one of --html or --xlsx")
    if args.html_path:
        render_html(args.native_root, args.html_path)
    if args.xlsx_path:
        write_xlsx(args.native_root, args.xlsx_path)
    print(json.dumps({
        "native_root": str(args.native_root),
        "html": str(args.html_path) if args.html_path else None,
        "xlsx": str(args.xlsx_path) if args.xlsx_path else None,
        "result_options": RESULT_OPTIONS,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
