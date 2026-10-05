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
    """Compact text for identifiers, titles, and short metadata."""
    if node is None:
        return None
    value = " ".join(" ".join(node.itertext()).split())
    return value or None


def prose_text(node: ET.Element | None) -> str | None:
    """Human prose with meaningful source line/paragraph boundaries retained."""
    if node is None:
        return None
    raw = "".join(node.itertext()).replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.strip() for line in raw.split("\n")]
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    normalized = []
    blank = False
    for line in lines:
        if not line:
            if normalized and not blank:
                normalized.append("")
            blank = True
        else:
            normalized.append(line)
            blank = False
    value = "\n".join(normalized).strip()
    return value or None


def safe_id(value: str | None, fallback: str) -> str:
    raw = value or fallback
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", raw).strip("_.-")
    return cleaned or fallback


def native_rule_id(source_rule_id: str | None, vulnerability_id: str | None, fallback: str) -> str:
    for value in (source_rule_id, vulnerability_id):
        if not value:
            continue
        match = re.search(r"SV-\d+", value, flags=re.I)
        if match:
            return match.group(0).upper()
    if vulnerability_id and re.fullmatch(r"V-\d+", vulnerability_id, flags=re.I):
        return "SV-" + vulnerability_id.split("-", 1)[1]
    return safe_id(source_rule_id or vulnerability_id, fallback)


def native_rule_version(source_rule_id: str | None) -> str:
    match = re.search(r"(r\d+)", source_rule_id or "", flags=re.I)
    return match.group(1).lower() if match else "1"


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


STIG_DESCRIPTION_FIELDS = {
    "VulnDiscussion": "discussion",
    "FalsePositives": "false_positives",
    "FalseNegatives": "false_negatives",
    "Documentable": "documentable",
    "Mitigations": "mitigations",
    "SeverityOverrideGuidance": "severity_override_guidance",
    "PotentialImpacts": "potential_impacts",
    "ThirdPartyTools": "third_party_tools",
    "MitigationControl": "mitigation_control",
    "Responsibility": "responsibility",
    "IAControls": "ia_controls",
}


def stig_description_fields(rule: ET.Element) -> dict[str, str | None]:
    """Parse DISA's escaped XML fragment carried inside xccdf:description."""
    desc = child(rule, "description")
    if desc is None:
        return {}
    raw = "".join(desc.itertext()).strip()
    if not raw:
        return {}
    try:
        wrapper = ET.fromstring(f"<root>{raw}</root>")
    except ET.ParseError:
        return {"discussion": prose_text(desc)}
    result: dict[str, str | None] = {}
    for node in list(wrapper):
        key = STIG_DESCRIPTION_FIELDS.get(lname(node.tag))
        if key:
            result[key] = prose_text(node)
    return result or {"discussion": prose_text(desc)}


def rule_discussion(rule: ET.Element) -> str | None:
    return stig_description_fields(rule).get("discussion")


def rule_check(rule: ET.Element) -> str | None:
    for check_node in children(rule, "check"):
        content = descendant(check_node, "check-content")
        if content is not None and prose_text(content):
            return prose_text(content)
    return None


def rule_fix(rule: ET.Element) -> str | None:
    fixes = [prose_text(x) for x in children(rule, "fixtext")]
    fixes = [x for x in fixes if x]
    return "\n\n".join(fixes) if fixes else None


def identifiers(rule: ET.Element, stig_id: str | None, vulnerability_id: str | None) -> list[dict]:
    out = []
    for node in children(rule, "ident"):
        value = text(node)
        if not value:
            continue
        system = (node.get("system") or "").lower()
        if "cci" in system:
            scheme = "cci"
        elif "legacy" in system:
            scheme = "disa-legacy-id"
        else:
            scheme = "source-ident"
        out.append({"scheme": scheme, "value": value})
    if stig_id:
        out.append({"scheme": "disa-stig-id", "value": stig_id})
    if vulnerability_id:
        out.append({"scheme": "disa-vulnerability-id", "value": vulnerability_id})
    seen = set()
    unique = []
    for row in out:
        key = (row["scheme"], row["value"])
        if key not in seen:
            seen.add(key)
            unique.append(row)
    return unique


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


def profile_description(profile: ET.Element) -> str | None:
    desc = child(profile, "description")
    if desc is None:
        return None
    raw = "".join(desc.itertext()).strip()
    if raw == "<ProfileDescription></ProfileDescription>":
        return None
    if raw.startswith("<ProfileDescription>") and raw.endswith("</ProfileDescription>"):
        try:
            return text(ET.fromstring(raw))
        except ET.ParseError:
            pass
    return text(desc)


def source_profile_rows(root: ET.Element) -> list[dict]:
    rows = []
    for profile in children(root, "Profile"):
        rows.append({
            "id": profile.get("id"),
            "title": text(child(profile, "title")),
            "description": profile_description(profile),
            "select": [
                {"idref": x.get("idref"), "selected": x.get("selected")}
                for x in children(profile, "select")
            ],
        })
    return rows


def native_profile_rows(
    root: ET.Element,
    source_rule_to_native: dict[str, str],
    source_group_to_native_rules: dict[str, list[str]],
) -> list[dict]:
    """Resolve old XCCDF profile selections into NG's subtractive profile model."""
    rows = []
    for profile in source_profile_rows(root):
        disabled: list[str] = []
        for action in profile["select"]:
            if str(action.get("selected")).lower() != "false":
                continue
            target = action.get("idref")
            expanded = []
            if target in source_rule_to_native:
                expanded = [source_rule_to_native[target]]
            else:
                expanded = source_group_to_native_rules.get(str(target), [])
            for rule_id in expanded:
                if rule_id not in disabled:
                    disabled.append(rule_id)
        rows.append({
            "id": profile.get("id"),
            "title": profile.get("title"),
            "description": profile.get("description"),
            "disabled_rules": disabled,
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
    source_rule_to_native: dict[str, str] = {}
    source_group_to_native_rules: dict[str, list[str]] = {}
    used_ids: set[str] = set()

    for idx, (rule, path) in enumerate(iter_rules(root), start=1):
        source_rule_id = rule.get("id")
        stig_id = text(child(rule, "version"))
        vuln_id = path[-1].get("id") if path else None
        base_id = native_rule_id(source_rule_id, vuln_id, f"rule-{idx}")
        native_id = base_id
        if native_id in used_ids:
            native_id = safe_id(f"{base_id}-{vuln_id or idx}", f"rule-{idx}")
        used_ids.add(native_id)
        if source_rule_id:
            source_rule_to_native[source_rule_id] = native_id
        for group in path:
            group_id = group.get("id")
            if group_id:
                source_group_to_native_rules.setdefault(group_id, []).append(native_id)

        procedure = rule_check(rule)
        if not procedure:
            raise SystemExit(
                f"Rule {source_rule_id or native_id!r} has no human-readable Check Text; "
                "refusing to invent a Manual Assessment procedure."
            )
        description_fields = stig_description_fields(rule)
        assessment_id = f"{native_id}.manual"
        extensions = {
            key: value for key, value in description_fields.items()
            if key != "discussion"
        }
        if "documentable" in extensions and extensions["documentable"] is not None:
            extensions["documentable"] = str(extensions["documentable"]).lower() == "true"

        assessment_path = f"../assessments/manual/{assessment_id}.assessment.yaml"
        rule_doc = {
            "rule": {
                "id": native_id,
                "version": native_rule_version(source_rule_id),
                "title": text(child(rule, "title")) or "",
                "severity": rule.get("severity") or "unknown",
                "role": rule.get("role") or "full",
                "weight": float(rule.get("weight") or 10.0),
                "discussion": description_fields.get("discussion") or "",
                "rationale": None,
                "extensions": {"disa_stig": extensions},
                "warnings": [],
                "identifiers": identifiers(rule, stig_id, vuln_id),
                "references": references(rule),
                "requires": [],
                "conflicts": [],
                "applicability": [],
                "parameters": {},
                "remediation": {"guidance": rule_fix(rule) or ""},
                "organizational_input_requirements": {},
                "assessment_choices": {
                    "manual": {"assessment": assessment_path}
                },
                "default_assessment_choice": "manual",
            },
        }
        dump_yaml(output / "rules" / f"{native_id}.rule.yaml", rule_doc)

        assessment_doc = {
            "assessment": {
                "id": assessment_id,
                "version": 1,
                "assessment_title": None,
                "mode": "manual",
                "class": "compliance",
                "purpose": "assessment",
                "procedure": procedure,
                "response": {
                    "type": "compliance",
                    "choices": [
                        {"value": "pass", "label": "Pass", "outcome": "true"},
                        {"value": "fail", "label": "Fail", "outcome": "false"},
                        {"value": "unknown", "label": "Unknown", "outcome": "unknown"},
                        {
                            "value": "not_applicable",
                            "label": "Not Applicable",
                            "outcome": "not_applicable",
                        },
                    ],
                    "allow_comment": True,
                    "allow_evidence": True,
                },
            },
        }
        dump_yaml(
            output / "assessments" / "manual" / f"{assessment_id}.assessment.yaml",
            assessment_doc,
        )

        converted_rules.append(native_id)
        provenance_rules.append({
            "native_rule_id": native_id,
            "native_assessment_id": assessment_id,
            "source_rule_id": source_rule_id,
            "source_group_id": vuln_id,
            "source_stig_id": stig_id,
            "source_description_fields": description_fields,
        })

    native_groups = []
    for group in group_rows(root):
        gid = group.get("id")
        native_groups.append({
            "id": gid,
            "title": group.get("title"),
            "rules": source_group_to_native_rules.get(str(gid), []),
        })

    benchmark_doc = {
        "benchmark": {
            "id": benchmark_id,
            "ng_schema_version": "0.2.0",
            "use_case": "compliance",
            "assessment_specifications": [],
            "title": [{"text": benchmark_title, "language": None}],
            "description": [{"text": benchmark_description(root) or "", "language": None}],
            "language": "en",
            "status": [],
            "version": {"value": benchmark_version},
            "metadata": {},
            "notices": [],
            "front_matter": [],
            "rear_matter": [],
            "references": [],
            "text_blocks": [],
            "platform": {
                "id": "active-directory-forest",
                "title": "Active Directory Forest",
                "applicability": {},
            },
            "applicability_catalog": "applicability.yaml",
            "scoring": [],
            "parameters": [],
            "default_selection": True,
            "groups": native_groups,
            "profiles": native_profile_rows(
                root,
                source_rule_to_native,
                source_group_to_native_rules,
            ),
            "rules": converted_rules,
        },
    }
    dump_yaml(output / "benchmark.yaml", benchmark_doc)
    dump_yaml(output / "applicability.yaml", {"applicability": []})

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
            "ng_schema_version": "0.2.0",
        },
        "profiles": source_profile_rows(root),
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
