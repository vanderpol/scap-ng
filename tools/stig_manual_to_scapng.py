#!/usr/bin/env python3
"""Convert standalone DISA STIG manual XCCDF into current native SCAP-NG authoring YAML.

The source adapter accepts older DISA standalone XCCDF without assuming XCCDF
1.2 ID constraints. Legacy identities and source-only metadata are retained in
provenance; native Rule/Assessment documents follow the current file-backed
Benchmark -> Rule -> Assessment model.
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
from jsonschema import Draft202012Validator

from scap_upconvert_v003.build_rhel9_review_slice import functional_group_from_text


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


def prose_text(node: ET.Element | None) -> str | None:
    if node is None:
        return None
    raw = "".join(node.itertext()).replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.strip() for line in raw.split("\n")]
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    normalized: list[str] = []
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
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "-", raw).strip("-.")
    return cleaned or fallback


def dump_yaml(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(value, sort_keys=False, allow_unicode=True, width=100),
        encoding="utf-8",
    )


def dump_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def extract_xccdf(source: Path, work: Path) -> tuple[Path, dict]:
    if source.suffix.lower() != ".zip":
        return source, {
            "source_file": source.name,
            "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "archive_sha256": None,
        }
    sha = hashlib.sha256(source.read_bytes()).hexdigest()
    with zipfile.ZipFile(source) as zf:
        candidates = [
            n for n in zf.namelist()
            if n.lower().endswith(".xml") and "xccdf" in n.lower()
        ]
        manual = [n for n in candidates if "manual" in n.lower()]
        selected = manual or candidates
        if not selected:
            raise SystemExit("No XCCDF XML found in source ZIP")
        name = sorted(selected, key=lambda x: (len(x), x.lower()))[0]
        data = zf.read(name)
    work.mkdir(parents=True, exist_ok=True)
    target = work / Path(name).name
    target.write_bytes(data)
    return target, {
        "source_file": source.name,
        "source_sha256": sha,
        "archive_member": name,
        "archive_sha256": sha,
    }


def xccdf_namespace(root: ET.Element) -> str | None:
    if root.tag.startswith("{"):
        return root.tag[1:].split("}", 1)[0]
    return None


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


def rule_check(rule: ET.Element) -> str | None:
    for check_node in children(rule, "check"):
        content = descendant(check_node, "check-content")
        value = prose_text(content)
        if value:
            return value
    return None


def rule_fix(rule: ET.Element) -> str | None:
    fixes = [prose_text(x) for x in children(rule, "fixtext")]
    return "\n\n".join(x for x in fixes if x) or None


def normalized_fixes(rule: ET.Element) -> list[dict]:
    system_map = {
        "urn:xccdf:fix:script:sh": "shell",
        "urn:xccdf:fix:script:ansible": "ansible",
        "urn:xccdf:fix:script:powershell": "powershell",
        "urn:xccdf:fix:script:batch": "batch",
    }
    values = []
    for node in children(rule, "fix"):
        if list(node):
            raise SystemExit(
                f"Rule {rule.get('id')!r} has an XCCDF fix with substitution/child elements; "
                "conversion support is required before it can be emitted losslessly."
            )
        content = prose_text(node)
        if not content:
            continue
        source_system = node.get("system")
        item = {"content": content}
        if source_system:
            fix_type = system_map.get(source_system)
            if not fix_type:
                raise SystemExit(
                    f"Rule {rule.get('id')!r} uses unsupported XCCDF fix system {source_system!r}."
                )
            item["type"] = fix_type
        for source_name in ("reboot", "disruption", "complexity", "strategy"):
            value = node.get(source_name)
            if value is not None:
                item[source_name] = value.lower() == "true" if source_name == "reboot" else value
        values.append(item)
    return values


def profile_description(profile: ET.Element) -> str | None:
    desc = child(profile, "description")
    if desc is None:
        return None
    raw = "".join(desc.itertext()).strip()
    if raw.startswith("<ProfileDescription>") and raw.endswith("</ProfileDescription>"):
        try:
            return prose_text(ET.fromstring(raw))
        except ET.ParseError:
            pass
    return prose_text(desc)


def source_profile_rows(root: ET.Element) -> list[dict]:
    rows = []
    for profile in children(root, "Profile"):
        rows.append({
            "id": profile.get("id"),
            "title": text(child(profile, "title")),
            "description": profile_description(profile),
            "extends": profile.get("extends"),
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
    rows = []
    for profile in source_profile_rows(root):
        disabled: list[str] = []
        for action in profile["select"]:
            if str(action.get("selected")).lower() != "false":
                continue
            target = str(action.get("idref") or "")
            expanded = (
                [source_rule_to_native[target]]
                if target in source_rule_to_native
                else source_group_to_native_rules.get(target, [])
            )
            for rule_id in expanded:
                if rule_id not in disabled:
                    disabled.append(rule_id)
        row = {
            "id": safe_id(profile.get("id"), "profile"),
            "title": profile.get("title"),
            "description": profile.get("description"),
            "disabled_rules": disabled,
            "parameters": {},
        }
        if profile.get("extends"):
            row["extends"] = safe_id(str(profile["extends"]), str(profile["extends"]))
        rows.append(row)
    return rows


def iter_rules(node: ET.Element, group_path: list[dict] | None = None):
    group_path = group_path or []
    for item in list(node):
        kind = lname(item.tag)
        if kind == "Rule":
            yield item, group_path
        elif kind == "Group":
            g = {"id": item.get("id"), "title": text(child(item, "title"))}
            yield from iter_rules(item, group_path + [g])


def native_identity(rule: ET.Element, path: list[dict], index: int) -> tuple[str, str]:
    source_rule_id = rule.get("id") or ""
    match = re.search(r"(SV-\d+)(r\d+)?", source_rule_id, re.I)
    if match:
        return match.group(1).upper(), (match.group(2) or "1")
    vuln = str(path[-1].get("id") or "") if path else ""
    match = re.fullmatch(r"V-(\d+)", vuln, re.I)
    if match:
        return f"SV-{match.group(1)}", "1"
    return safe_id(source_rule_id, f"rule-{index}"), "1"


def identifiers(rule: ET.Element, path: list[dict]) -> list[dict]:
    out: list[dict] = []
    stig_id = text(child(rule, "version"))
    if stig_id:
        out.append({"scheme": "disa-stig-id", "value": stig_id})
    if path and path[-1].get("id"):
        out.append({"scheme": "disa-vulnerability-id", "value": path[-1]["id"]})
    for node in children(rule, "ident"):
        value = text(node)
        if not value:
            continue
        system = str(node.get("system") or "").lower()
        scheme = "cci" if "cci" in system or value.upper().startswith("CCI-") else "source-ident"
        item = {"scheme": scheme, "value": value}
        if scheme == "source-ident" and node.get("system"):
            item["system"] = node.get("system")
        out.append(item)
    unique = []
    seen = set()
    for item in out:
        key = (item.get("scheme"), item.get("value"), item.get("system"))
        if key not in seen:
            unique.append(item)
            seen.add(key)
    return unique


def references(rule: ET.Element) -> list[dict]:
    out = []
    for ref in children(rule, "reference"):
        entry = {}
        for node in list(ref):
            value = text(node)
            if value:
                entry[lname(node.tag).lower()] = value
        if not entry and text(ref):
            entry["text"] = text(ref)
        if entry:
            out.append(entry)
    return out


def metadata(root: ET.Element) -> dict:
    result: dict[str, list[str]] = {}
    for block in children(root, "metadata"):
        for node in list(block):
            value = text(node)
            if value:
                result.setdefault(lname(node.tag).lower(), []).append(value)
    return result


def localized(node: ET.Element | None) -> list[dict]:
    value = prose_text(node)
    if not value:
        return []
    language = None if node is None else (
        node.get("{http://www.w3.org/XML/1998/namespace}lang") or node.get("lang")
    )
    return [{"text": value, "language": language}]


def benchmark_status(root: ET.Element) -> list[dict]:
    return [
        {"value": text(node), "date": node.get("date")}
        for node in children(root, "status") if text(node)
    ]


def benchmark_notices(root: ET.Element) -> list[dict]:
    values = []
    for node in children(root, "notice"):
        values.append({
            "id": safe_id(node.get("id"), "notice"),
            "text": prose_text(node) or "",
            "language": node.get("{http://www.w3.org/XML/1998/namespace}lang"),
        })
    return values


def benchmark_references(root: ET.Element) -> list[dict]:
    values = []
    for node in children(root, "reference"):
        item = {"text": text(node)}
        if node.get("href"):
            item["url"] = node.get("href")
        values.append(item)
    return values


def benchmark_text_blocks(root: ET.Element) -> list[dict]:
    return [
        {"id": safe_id(node.get("id"), "text"), "text": prose_text(node) or ""}
        for node in children(root, "plain-text")
    ]


def benchmark_scoring(root: ET.Element) -> list[dict]:
    values = []
    for node in children(root, "model"):
        item = {"system": text(node), "parameters": {}}
        for param in children(node, "param"):
            if param.get("name"):
                item["parameters"][param.get("name")] = param.get("value") or text(param)
        values.append(item)
    return values


def source_inventory(root: ET.Element) -> dict:
    top: dict[str, int] = {}
    rule_children: dict[str, int] = {}
    check_children: dict[str, int] = {}
    profile_children: dict[str, int] = {}
    for node in list(root):
        name = lname(node.tag)
        top[name] = top.get(name, 0) + 1
        if name == "Profile":
            for nested in list(node):
                nested_name = lname(nested.tag)
                profile_children[nested_name] = profile_children.get(nested_name, 0) + 1
    for rule, _ in iter_rules(root):
        for node in list(rule):
            name = lname(node.tag)
            rule_children[name] = rule_children.get(name, 0) + 1
            if name == "check":
                for nested in list(node):
                    nested_name = lname(nested.tag)
                    check_children[nested_name] = check_children.get(nested_name, 0) + 1
    return {
        "benchmark_children": top,
        "profile_children": profile_children,
        "rule_children": rule_children,
        "check_children": check_children,
    }


def unhandled_source_elements(inventory: dict) -> dict:
    handled_benchmark = {
        "status", "title", "description", "notice", "front-matter", "rear-matter",
        "reference", "plain-text", "platform", "model", "Profile", "Group", "Rule",
        "version", "metadata",
    }
    handled_profile = {"title", "description", "select"}
    handled_rule = {
        "status", "version", "title", "description", "reference", "ident",
        "check", "fixtext", "fix", "rationale", "warning",
    }
    handled_check = {"check-content", "check-content-ref"}
    return {
        "benchmark_children": sorted(
            name for name in inventory["benchmark_children"] if name not in handled_benchmark
        ),
        "profile_children": sorted(
            name for name in inventory["profile_children"] if name not in handled_profile
        ),
        "rule_children": sorted(
            name for name in inventory["rule_children"] if name not in handled_rule
        ),
        "check_children": sorted(
            name for name in inventory["check_children"] if name not in handled_check
        ),
    }


def schema_validation_report(output: Path) -> dict:
    repo_root = Path(__file__).resolve().parent.parent
    schema_root = repo_root / "schema" / "v0.2.0"
    checks = [
        ("benchmark", output / "benchmark.yaml", schema_root / "benchmark.schema.json"),
    ]
    checks.extend(
        ("rule", path, schema_root / "rule.schema.json")
        for path in sorted((output / "rules").glob("*.rule.yaml"))
    )
    checks.extend(
        ("manual_assessment", path, schema_root / "manual-assessment.schema.json")
        for path in sorted((output / "assessments" / "manual").glob("*.assessment.yaml"))
    )
    results = []
    for kind, doc_path, schema_path in checks:
        doc = yaml.safe_load(doc_path.read_text(encoding="utf-8"))
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        errors = sorted(
            Draft202012Validator(schema).iter_errors(doc),
            key=lambda e: list(e.absolute_path),
        )
        results.append({
            "kind": kind,
            "path": str(doc_path.relative_to(output)),
            "valid": not errors,
            "errors": [
                {
                    "path": "/".join(str(x) for x in err.absolute_path),
                    "message": err.message,
                }
                for err in errors
            ],
        })
    return {
        "valid": all(item["valid"] for item in results),
        "documents": results,
    }


def benchmark_platform(root: ET.Element, benchmark_id: str, title: str) -> tuple[dict, list[str]]:
    source_ids = [
        x.get("idref") for x in children(root, "platform") if x.get("idref")
    ]
    platform_id = safe_id(source_ids[0] if source_ids else benchmark_id, benchmark_id)
    return {
        "id": platform_id,
        "title": title,
        # Standalone STIG manuals normally state scope but do not provide an
        # executable platform assessment. Do not invent one.
        "applicability": {},
    }, source_ids


def convert(source: Path, output: Path, *, auto_map_groups: bool = False) -> dict:
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    xml_path, archive_meta = extract_xccdf(source, output / ".source-work")
    root = ET.parse(xml_path).getroot()
    if lname(root.tag) != "Benchmark":
        raise SystemExit(f"Expected XCCDF Benchmark root, got {lname(root.tag)!r}")

    namespace = xccdf_namespace(root)
    inventory = source_inventory(root)
    unhandled = unhandled_source_elements(inventory)
    source_benchmark_id = root.get("id")
    if any(unhandled.values()):
        failure_audit = {
            "format": "scap-ng-stig-manual-conversion-audit-0.1",
            "source": {
                **archive_meta,
                "xccdf_namespace": namespace,
                "benchmark_id": source_benchmark_id,
                "benchmark_version": text(child(root, "version")),
            },
            "counts": {
                "source_rules": sum(1 for _ in iter_rules(root)),
                "native_rules": 0,
                "native_manual_assessments": 0,
                "profiles": len(source_profile_rows(root)),
                "benchmark_source_elements": inventory["benchmark_children"],
                "profile_source_elements": inventory["profile_children"],
                "rule_source_elements": inventory["rule_children"],
                "check_source_elements": inventory["check_children"],
            },
            "mapped_constructs": {},
            "intentional_transformations": [],
            "source_only_provenance": [],
            "unhandled_constructs": unhandled,
            "schema_validation": {
                "valid": False,
                "not_run_reason": "Source contains unhandled XCCDF constructs.",
                "documents": [],
            },
            "success": False,
        }
        dump_json(output / "conversion-audit.json", failure_audit)
        shutil.rmtree(output / ".source-work", ignore_errors=True)
        raise SystemExit(
            "Unhandled XCCDF source elements would be dropped; "
            "see conversion-audit.json: "
            + json.dumps(unhandled, sort_keys=True)
        )
    benchmark_id = safe_id(source_benchmark_id, "stig-manual")
    benchmark_title = text(child(root, "title")) or benchmark_id
    benchmark_version = text(child(root, "version"))
    platform, source_platform_ids = benchmark_platform(root, benchmark_id, benchmark_title)

    converted_rules: list[str] = []
    provenance_rules: list[dict] = []
    source_rule_to_native: dict[str, str] = {}
    source_group_to_native_rules: dict[str, list[str]] = {}
    used_ids: set[str] = set()
    group_candidates: list[dict] = []

    for idx, (rule, path) in enumerate(iter_rules(root), start=1):
        source_rule_id = rule.get("id")
        native_id, native_version = native_identity(rule, path, idx)
        if native_id in used_ids:
            raise SystemExit(f"Duplicate native Rule identity {native_id!r}")
        used_ids.add(native_id)
        if source_rule_id:
            source_rule_to_native[source_rule_id] = native_id
        for group in path:
            if group.get("id"):
                source_group_to_native_rules.setdefault(str(group["id"]), []).append(native_id)

        procedure = rule_check(rule)
        if not procedure:
            raise SystemExit(
                f"Rule {source_rule_id or native_id!r} has no human-readable Check Text; "
                "refusing to invent a Manual Assessment procedure."
            )
        fields = stig_description_fields(rule)
        discussion = fields.get("discussion") or ""
        fix = rule_fix(rule)
        fix_implementations = normalized_fixes(rule)
        group_candidates.append({
            "rule": native_id,
            "title": text(child(rule, "title")) or native_id,
            "discussion": discussion,
            "remediation": fix or "",
        })
        assessment_id = f"{native_id}.manual"
        assessment_rel = f"../assessments/manual/{assessment_id}.assessment.yaml"

        extension_fields = {
            k: v for k, v in fields.items() if k != "discussion"
        }
        if "documentable" in extension_fields and isinstance(extension_fields["documentable"], str):
            value = extension_fields["documentable"].strip().lower()
            if value in ("true", "false"):
                extension_fields["documentable"] = value == "true"

        role_explicit = rule.get("role")
        weight_explicit = rule.get("weight")
        effective_role = role_explicit or "full"
        effective_weight = float(weight_explicit) if weight_explicit is not None else 1.0

        rule_doc = {
            "rule": {
                "id": native_id,
                "version": native_version,
                "title": text(child(rule, "title")) or native_id,
                "severity": rule.get("severity") or "unknown",
                "role": effective_role,
                "weight": effective_weight,
                "discussion": discussion,
                "rationale": prose_text(child(rule, "rationale")),
                "extensions": {"disa_stig": extension_fields},
                "warnings": [
                    prose_text(node) for node in children(rule, "warning") if prose_text(node)
                ],
                "identifiers": identifiers(rule, path),
                "references": references(rule),
                "requires": [],
                "conflicts": [],
                "applicability": [],
                "parameters": {},
                "remediation": {
                    **({"guidance": fix} if fix else {}),
                    **({"implementations": fix_implementations} if fix_implementations else {}),
                },
                "organizational_input_requirements": {},
                "assessment_choices": {
                    "manual": {"assessment": assessment_rel}
                },
                "default_assessment_choice": "manual",
            }
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
                    "type": "stig-manual-compliance",
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
                "references": [],
                "evidence_guidance": None,
            }
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
            "source_group_ancestry": path,
            "source_stig_id": text(child(rule, "version")),
            "source_description_fields": fields,
            "source_attributes": {
                "role": {"explicit": role_explicit, "effective": effective_role},
                "weight": {"explicit": weight_explicit, "effective": effective_weight},
            },
            "source_status": [
                {"value": text(node), "date": node.get("date")}
                for node in children(rule, "status") if text(node)
            ],
            "source_check_systems": [
                node.get("system") for node in children(rule, "check") if node.get("system")
            ],
            "source_check_content_refs": [
                {
                    "href": nested.get("href"),
                    "name": nested.get("name"),
                }
                for check_node in children(rule, "check")
                for nested in children(check_node, "check-content-ref")
            ],
            "source_fix_attributes": [
                dict(node.attrib) for node in children(rule, "fix") if node.attrib
            ],
            "source_fixtext_attributes": [
                dict(node.attrib) for node in children(rule, "fixtext") if node.attrib
            ],
        })

    profiles = native_profile_rows(root, source_rule_to_native, source_group_to_native_rules)
    groups = []
    grouping_rows = []
    if auto_map_groups:
        buckets: dict[str, dict] = {}
        for candidate in group_candidates:
            topic_id, topic_title = functional_group_from_text(
                candidate["title"],
                candidate["discussion"],
                candidate["remediation"],
            )
            if topic_id == "needs-grouping":
                grouping_rows.append({
                    "rule": candidate["rule"],
                    "functional_group": None,
                    "method": "heuristic",
                    "mapped": False,
                    "reason": "no_high_confidence_topic",
                })
                continue
            group_id = f"manual-or-managerial.{topic_id}"
            bucket = buckets.setdefault(
                group_id,
                {"id": group_id, "title": topic_title, "rules": []},
            )
            bucket["rules"].append(candidate["rule"])
            grouping_rows.append({
                "rule": candidate["rule"],
                "functional_group": group_id,
                "method": "heuristic",
                "mapped": True,
            })
        if buckets:
            groups = [{
                "id": "manual-or-managerial",
                "title": "Manual or Managerial",
                "groups": list(buckets.values()),
            }]
    else:
        grouping_rows = [
            {
                "rule": candidate["rule"],
                "functional_group": None,
                "method": "disabled",
                "mapped": False,
                "reason": "auto_map_groups_not_requested",
            }
            for candidate in group_candidates
        ]
    grouping = {
        "auto_map_groups": auto_map_groups,
        "method": "heuristic" if auto_map_groups else "disabled",
        "mapped_rules": sum(1 for row in grouping_rows if row.get("mapped")),
        "unmapped_rules": sum(1 for row in grouping_rows if not row.get("mapped")),
        "rules": grouping_rows,
    }

    benchmark_doc = {
        "benchmark": {
            "id": benchmark_id,
            "ng_schema_version": None,
            "use_case": "compliance",
            "assessment_specifications": [],
            "title": localized(child(root, "title")),
            "description": localized(child(root, "description")),
            "language": root.get("{http://www.w3.org/XML/1998/namespace}lang"),
            "status": benchmark_status(root),
            "version": {
                "value": benchmark_version,
                "time": child(root, "version").get("time") if child(root, "version") is not None else None,
                "update": child(root, "version").get("update") if child(root, "version") is not None else None,
            },
            "metadata": metadata(root),
            "notices": benchmark_notices(root),
            "front_matter": localized(child(root, "front-matter")),
            "rear_matter": localized(child(root, "rear-matter")),
            "references": benchmark_references(root),
            "text_blocks": benchmark_text_blocks(root),
            "platform": platform,
            "applicability_catalog": "applicability.yaml",
            "scoring": benchmark_scoring(root),
            "parameters": [],
            "default_selection": True,
            # Legacy DISA vulnerability wrapper Groups are not meaningful NG
            # authoring taxonomy. Optional grouping is inferred only when the
            # caller explicitly requests it and a high-confidence topic matches.
            "groups": groups,
            "profiles": profiles,
            "rules": converted_rules,
        }
    }
    dump_yaml(output / "benchmark.yaml", benchmark_doc)
    dump_yaml(output / "applicability.yaml", {"applicability": {}})

    provenance = {
        "format": "scap-ng-stig-manual-conversion-provenance-0.2",
        "source": {
            **archive_meta,
            "xccdf_namespace": namespace,
            "benchmark_id": source_benchmark_id,
            "benchmark_version": benchmark_version,
            "platform_ids": source_platform_ids,
            "profiles": source_profile_rows(root),
            "inventory": inventory,
            "unhandled_elements": unhandled,
        },
        "native": {
            "benchmark_id": benchmark_id,
            "rules": len(converted_rules),
            "manual_assessments": len(converted_rules),
        },
        "grouping": grouping,
        "rules": provenance_rules,
    }
    dump_json(output / "provenance.json", provenance)

    validation = schema_validation_report(output)
    conversion_audit = {
        "format": "scap-ng-stig-manual-conversion-audit-0.1",
        "source": {
            **archive_meta,
            "xccdf_namespace": namespace,
            "benchmark_id": source_benchmark_id,
            "benchmark_version": benchmark_version,
        },
        "counts": {
            "source_rules": len(provenance_rules),
            "native_rules": len(converted_rules),
            "native_manual_assessments": len(converted_rules),
            "profiles": len(profiles),
            "benchmark_source_elements": inventory["benchmark_children"],
            "profile_source_elements": inventory["profile_children"],
            "rule_source_elements": inventory["rule_children"],
            "check_source_elements": inventory["check_children"],
        },
        "mapped_constructs": {
            "benchmark": sorted(inventory["benchmark_children"]),
            "rule": sorted(inventory["rule_children"]),
        },
        "intentional_transformations": [
            {
                "source": "legacy DISA vulnerability wrapper Group",
                "native": "Rule disa-vulnerability-id identifier plus provenance ancestry",
                "reason": "One-wrapper-Group-per-Rule is not recreated as native NG taxonomy.",
            },
            {
                "source": "legacy XCCDF Profile select directives",
                "native": "native Profile disabled_rules",
                "reason": "Group and Rule references are resolved to native Rule identities.",
            },
            {
                "source": "escaped DISA STIG fields inside xccdf:description",
                "native": "Rule discussion plus extensions.disa_stig",
                "reason": "Preserves meaning without carrying XML wrapper syntax into native source.",
            },
            {
                "source": "XCCDF check-content",
                "native": "Manual Assessment procedure",
                "reason": "Standalone STIG manual checks are human procedures, not fabricated automation.",
            },
        ],
        "source_only_provenance": [
            "original XCCDF Rule id",
            "source Group ancestry",
            "source Rule status",
            "source check system and check-content-ref bindings",
            "source fix/fixtext attributes",
            "source role/weight explicit-vs-effective values",
            "source Profile select directives",
        ],
        "grouping": grouping,
        "unhandled_constructs": unhandled,
        "schema_validation": validation,
        "success": (
            not any(unhandled.values())
            and validation["valid"]
            and len(converted_rules) == len(provenance_rules)
        ),
    }
    dump_json(output / "conversion-audit.json", conversion_audit)
    if not conversion_audit["success"]:
        raise SystemExit(
            "Conversion audit failed; see conversion-audit.json for loss/validation details."
        )
    shutil.rmtree(output / ".source-work", ignore_errors=True)

    summary = {
        "benchmark_id": benchmark_id,
        "title": benchmark_title,
        "source_xccdf_namespace": namespace,
        "source_version": benchmark_version,
        "rules": len(converted_rules),
        "manual_assessments": len(converted_rules),
        "profiles": len(profiles),
        "auto_map_groups": auto_map_groups,
        "grouped_rules": grouping["mapped_rules"],
        "ungrouped_rules": grouping["unmapped_rules"],
        "conversion_audit": "conversion-audit.json",
        "audit_success": conversion_audit["success"],
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
    ap.add_argument(
        "--auto-map-groups",
        action="store_true",
        help=(
            "Opt in to heuristic functional grouping. Default conversion leaves "
            "Rules ungrouped; uncertain Rules remain ungrouped even when enabled."
        ),
    )
    args = ap.parse_args()
    print(json.dumps(
        convert(args.source, args.output_dir, auto_map_groups=args.auto_map_groups),
        indent=2,
        sort_keys=True,
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
