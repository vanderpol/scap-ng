#!/usr/bin/env python3
"""Convert standalone DISA STIG manual XCCDF into native SCAP-NG authoring YAML.

This is the older-XCCDF/manual source adapter tracked by issue #157.  It is
intentionally source-version-aware and does not assume XCCDF 1.2 ID prefixes.
Historical XCCDF identities are written to provenance.json, not required as
native execution semantics.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

import yaml

SCAP_NG_VERSION = "0.3.0-development"


def lname(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def child(node: ET.Element, name: str) -> ET.Element | None:
    return next((x for x in list(node) if lname(x.tag) == name), None)


def children(node: ET.Element, name: str) -> list[ET.Element]:
    return [x for x in list(node) if lname(x.tag) == name]


def descendant(node: ET.Element, name: str) -> ET.Element | None:
    return next((x for x in node.iter() if lname(x.tag) == name), None)


def text(node: ET.Element | None) -> str | None:
    if node is None:
        return None
    value = " ".join(" ".join(node.itertext()).split())
    return value or None


def safe_id(value: str | None, fallback: str) -> str:
    raw = value or fallback
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", raw).strip("_.-")
    return cleaned or fallback


def dump_yaml(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(value, sort_keys=False, allow_unicode=True, width=120),
        encoding="utf-8",
    )


def dump_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def extract_xccdf(source: Path, work: Path) -> tuple[Path, dict]:
    if source.suffix.lower() != ".zip":
        return source, {"source_file": source.name, "archive_sha256": None}

    sha = hashlib.sha256(source.read_bytes()).hexdigest()
    with zipfile.ZipFile(source) as zf:
        candidates = [
            n for n in zf.namelist()
            if n.lower().endswith(".xml") and "xccdf" in n.lower()
        ]
        manual = [n for n in candidates if "manual" in n.lower()]
        selected = (manual or candidates)
        if not selected:
            raise SystemExit("No XCCDF XML found in source ZIP")
        name = sorted(selected, key=lambda x: (len(x), x.lower()))[0]
        data = zf.read(name)
    work.mkdir(parents=True, exist_ok=True)
    target = work / Path(name).name
    target.write_bytes(data)
    return target, {
        "source_file": source.name,
        "archive_member": name,
        "archive_sha256": sha,
    }


def xccdf_namespace(root: ET.Element) -> str | None:
    if root.tag.startswith("{"):
        return root.tag[1:].split("}", 1)[0]
    return None


def benchmark_description(root: ET.Element) -> str | None:
    desc = child(root, "description")
    return text(desc)


def rule_discussion(rule: ET.Element) -> str | None:
    desc = child(rule, "description")
    if desc is None:
        return None
    vuln = descendant(desc, "VulnDiscussion")
    return text(vuln) or text(desc)


def rule_check(rule: ET.Element) -> str | None:
    for check_node in children(rule, "check"):
        content = descendant(check_node, "check-content")
        if content is not None and text(content):
            return text(content)
    return None


def rule_fix(rule: ET.Element) -> str | None:
    fixes = [text(x) for x in children(rule, "fixtext")]
    fixes = [x for x in fixes if x]
    return "\n\n".join(fixes) if fixes else None


def idents(rule: ET.Element) -> list[dict]:
    out = []
    for node in children(rule, "ident"):
        value = text(node)
        if value:
            out.append({"system": node.get("system"), "value": value})
    return out


def references(rule: ET.Element) -> list[dict]:
    out = []
    for ref in children(rule, "reference"):
        entry = {}
        for node in list(ref):
            value = text(node)
            if value:
                entry[lname(node.tag)] = value
        if not entry and text(ref):
            entry["text"] = text(ref)
        if entry:
            out.append(entry)
    return out


def profile_rows(root: ET.Element) -> list[dict]:
    rows = []
    for profile in children(root, "Profile"):
        rows.append({
            "id": profile.get("id"),
            "title": text(child(profile, "title")),
            "description": text(child(profile, "description")),
            "select": [
                {"idref": x.get("idref"), "selected": x.get("selected")}
                for x in children(profile, "select")
            ],
        })
    return rows


def iter_rules(node: ET.Element, group_path: list[dict] | None = None):
    group_path = group_path or []
    for item in list(node):
        kind = lname(item.tag)
        if kind == "Rule":
            yield item, group_path
        elif kind == "Group":
            g = {
                "id": item.get("id"),
                "title": text(child(item, "title")),
            }
            yield from iter_rules(item, group_path + [g])


def group_rows(root: ET.Element) -> list[dict]:
    rows = []
    def walk(node: ET.Element, parent: str | None = None):
        for item in children(node, "Group"):
            rows.append({
                "id": item.get("id"),
                "title": text(child(item, "title")),
                "parent": parent,
            })
            walk(item, item.get("id"))
    walk(root)
    return rows


def convert(source: Path, output: Path) -> dict:
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    xml_path, archive_meta = extract_xccdf(source, output / ".source-work")
    root = ET.parse(xml_path).getroot()
    if lname(root.tag) != "Benchmark":
        raise SystemExit(f"Expected XCCDF Benchmark root, got {lname(root.tag)!r}")

    namespace = xccdf_namespace(root)
    source_benchmark_id = root.get("id")
    benchmark_id = safe_id(source_benchmark_id, "stig-manual")
    benchmark_title = text(child(root, "title")) or benchmark_id
    benchmark_version = text(child(root, "version"))

    converted_rules = []
    provenance_rules = []
    used_ids: set[str] = set()

    for idx, (rule, path) in enumerate(iter_rules(root), start=1):
        source_rule_id = rule.get("id")
        stig_id = text(child(rule, "version"))
        vuln_id = path[-1].get("id") if path else None
        base_id = safe_id(stig_id or vuln_id or source_rule_id, f"rule-{idx}")
        native_id = base_id
        if native_id in used_ids:
            native_id = safe_id(f"{base_id}-{vuln_id or idx}", f"rule-{idx}")
        used_ids.add(native_id)

        procedure = rule_check(rule)
        assessment_id = f"{native_id}.manual"
        rule_doc = {
            "scap_ng": SCAP_NG_VERSION,
            "rule": {
                "id": native_id,
                "title": text(child(rule, "title")),
                "severity": rule.get("severity"),
                "version": stig_id,
                "vulnerability_id": vuln_id,
                "group_path": path,
                "discussion": rule_discussion(rule),
                "references": references(rule),
                "idents": idents(rule),
                "fix": rule_fix(rule),
                "assessment_choices": [
                    {"name": "manual", "assessment": assessment_id}
                ],
                "default_assessment_choice": "manual",
            },
        }
        dump_yaml(output / "rules" / f"{native_id}.yaml", rule_doc)

        assessment_doc = {
            "scap_ng": SCAP_NG_VERSION,
            "assessment": {
                "id": assessment_id,
                "mode": "manual",
                "procedure": procedure or "No manual check procedure was present in the source rule.",
            },
        }
        dump_yaml(
            output / "assessments" / "manual" / f"{assessment_id}.yaml",
            assessment_doc,
        )

        converted_rules.append(native_id)
        provenance_rules.append({
            "native_rule_id": native_id,
            "native_assessment_id": assessment_id,
            "source_rule_id": source_rule_id,
            "source_group_id": vuln_id,
            "source_stig_id": stig_id,
        })

    benchmark_doc = {
        "scap_ng": SCAP_NG_VERSION,
        "benchmark": {
            "id": benchmark_id,
            "title": benchmark_title,
            "version": benchmark_version,
            "description": benchmark_description(root),
            "status": "converted-stig-manual",
            "groups": group_rows(root),
            "profiles": profile_rows(root),
            "rules": converted_rules,
        },
    }
    dump_yaml(output / "benchmark.yaml", benchmark_doc)

    provenance = {
        "format": "scap-ng-stig-manual-conversion-provenance-0.1",
        "source": {
            **archive_meta,
            "xccdf_namespace": namespace,
            "benchmark_id": source_benchmark_id,
            "benchmark_version": benchmark_version,
        },
        "native": {
            "benchmark_id": benchmark_id,
            "scap_ng": SCAP_NG_VERSION,
        },
        "rules": provenance_rules,
    }
    dump_json(output / "provenance.json", provenance)
    shutil.rmtree(output / ".source-work", ignore_errors=True)

    summary = {
        "benchmark_id": benchmark_id,
        "title": benchmark_title,
        "source_xccdf_namespace": namespace,
        "source_version": benchmark_version,
        "rules": len(converted_rules),
        "manual_assessments": len(converted_rules),
        "output_dir": str(output),
    }
    dump_json(output / "conversion-summary.json", summary)
    return summary


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Convert standalone STIG manual XCCDF/ZIP to native SCAP-NG YAML."
    )
    ap.add_argument("source", type=Path, help="Manual XCCDF XML or DISA STIG ZIP")
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    summary = convert(args.source, args.output_dir)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
