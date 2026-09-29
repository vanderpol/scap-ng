"""First-pass XCCDF benchmark/policy semantic extraction for iteration 003.

This module intentionally does not import the iteration-001/002 converter.
It extracts only understood policy semantics into the versioned IR and writes
source identity into a separate provenance structure.
"""

from __future__ import annotations

import hashlib
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

from . import IR_VERSION


XCCDF_NS = "http://checklists.nist.gov/xccdf/1.2"
NS = {"x": XCCDF_NS}


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _text(node: ET.Element | None) -> str | None:
    if node is None:
        return None
    value = " ".join("".join(node.itertext()).split())
    return value or None


def _native_id(source_id: str, fallback: str) -> str:
    """Create a readable converter-local ID without legacy namespace prefixes."""
    s = source_id
    s = re.sub(r"^xccdf_[^_]+(?:\.[^_]+)*_", "", s, flags=re.I)
    s = re.sub(r"^(benchmark|rule|group|profile|value)_", "", s, flags=re.I)
    s = re.sub(r"_(benchmark|rule|group|profile|value)$", "", s, flags=re.I)
    s = s.strip("_-. ")
    if not s:
        s = fallback
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", s)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@dataclass
class Diagnostic:
    severity: str
    code: str
    message: str
    source_kind: str
    provenance_key: str


@dataclass
class CheckAlternative:
    selector: str
    mode: str
    negate: bool
    multi_check: bool
    resolver_key: str
    inline_procedure: str | None = None


@dataclass
class RuleIR:
    id: str
    title: str | None
    severity: str | None
    weight: str | None
    role: str | None
    group: str | None
    applicability: list[str] = field(default_factory=list)
    requires: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)
    checks: list[CheckAlternative] = field(default_factory=list)


@dataclass
class GroupIR:
    id: str
    title: str | None
    parent: str | None
    rules: list[str] = field(default_factory=list)
    groups: list[str] = field(default_factory=list)


@dataclass
class ProfileIR:
    id: str
    title: str | None
    extends: str | None
    selections: dict[str, bool] = field(default_factory=dict)
    check_selectors: dict[str, str] = field(default_factory=dict)
    parameter_bindings: dict[str, str] = field(default_factory=dict)


@dataclass
class ParameterIR:
    id: str
    title: str | None
    datatype: str | None
    interactive: bool | None
    default_value: str | None


def _check_mode(system: str | None, inline: str | None) -> str:
    s = (system or "").lower()
    if "ocil" in s:
        return "manual"
    if "oval" in s:
        return "automated"
    if inline:
        return "manual"
    return "external"


def extract_xccdf(path: str | Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    source_path = Path(path)
    data = source_path.read_bytes()
    root = ET.fromstring(data)
    if _local(root.tag) != "Benchmark":
        raise ValueError("Input is not an XCCDF Benchmark document")

    provenance: dict[str, Any] = {
        "source": {
            "path": str(source_path),
            "sha256": _sha256(data),
            "format": "SCAP 1.4 XCCDF 1.2",
        },
        "entities": {},
    }
    diagnostics: list[Diagnostic] = []

    def provenance_key(kind: str, source_id: str) -> str:
        digest = hashlib.sha256(f"{kind}\0{source_id}".encode()).hexdigest()[:20]
        key = f"src-{digest}"
        provenance["entities"][key] = {"kind": kind, "source_id": source_id}
        return key

    benchmark_source_id = root.get("id") or "benchmark"
    benchmark_id = _native_id(benchmark_source_id, "benchmark")
    benchmark_key = provenance_key("benchmark", benchmark_source_id)

    title = _text(root.find("x:title", NS))
    version = _text(root.find("x:version", NS))
    status_node = root.find("x:status", NS)

    rules: list[RuleIR] = []
    groups: list[GroupIR] = []
    profiles: list[ProfileIR] = []
    parameters: list[ParameterIR] = []
    source_to_native: dict[str, str] = {}

    def visit_group(parent: ET.Element, parent_native: str | None = None) -> None:
        for group in parent.findall("x:Group", NS):
            source_id = group.get("id") or "group"
            native_id = _native_id(source_id, f"group-{len(groups)+1}")
            source_to_native[source_id] = native_id
            provenance_key("group", source_id)
            gir = GroupIR(
                id=native_id,
                title=_text(group.find("x:title", NS)),
                parent=parent_native,
            )
            groups.append(gir)

            for rule in group.findall("x:Rule", NS):
                parse_rule(rule, native_id)
                gir.rules.append(rules[-1].id)

            visit_group(group, native_id)
            gir.groups.extend(g.id for g in groups if g.parent == native_id)

    def parse_rule(rule: ET.Element, group_id: str | None) -> None:
        source_id = rule.get("id") or f"rule-{len(rules)+1}"
        native_id = _native_id(source_id, f"rule-{len(rules)+1}")
        source_to_native[source_id] = native_id
        rule_key = provenance_key("rule", source_id)

        checks: list[CheckAlternative] = []
        for check_index, check in enumerate(rule.findall("x:check", NS), start=1):
            selector = check.get("selector") or "default"
            inline = _text(check.find("x:check-content", NS))
            ref = check.find("x:check-content-ref", NS)
            resolver_key = f"{rule_key}-check-{check_index}"
            provenance["entities"][resolver_key] = {
                "kind": "check",
                "source_rule_id": source_id,
                "selector": selector,
                "system": check.get("system"),
                "href": ref.get("href") if ref is not None else None,
                "name": ref.get("name") if ref is not None else None,
            }
            checks.append(
                CheckAlternative(
                    selector=selector,
                    mode=_check_mode(check.get("system"), inline),
                    negate=(check.get("negate") or "false").lower() == "true",
                    multi_check=(check.get("multi-check") or "false").lower() == "true",
                    resolver_key=resolver_key,
                    inline_procedure=inline,
                )
            )

        applicability = [
            p.get("idref") for p in rule.findall("x:platform", NS) if p.get("idref")
        ]
        requires = [
            x for n in rule.findall("x:requires", NS) for x in (n.get("idref") or "").split()
        ]
        conflicts = [
            x for n in rule.findall("x:conflicts", NS) for x in (n.get("idref") or "").split()
        ]

        rules.append(
            RuleIR(
                id=native_id,
                title=_text(rule.find("x:title", NS)),
                severity=rule.get("severity"),
                weight=rule.get("weight"),
                role=rule.get("role"),
                group=group_id,
                applicability=applicability,
                requires=requires,
                conflicts=conflicts,
                checks=checks,
            )
        )

        known = {
            "title", "description", "warning", "question", "rationale", "reference",
            "ident", "profile-note", "fixtext", "fix", "check", "complex-check",
            "requires", "conflicts", "platform", "version", "metadata",
        }
        for child in rule:
            name = _local(child.tag)
            if name not in known:
                diagnostics.append(
                    Diagnostic(
                        severity="review",
                        code="unmodeled_rule_child",
                        message=f"Rule child {name!r} is not yet represented in the 003 IR",
                        source_kind="rule",
                        provenance_key=rule_key,
                    )
                )

    for rule in root.findall("x:Rule", NS):
        parse_rule(rule, None)

    visit_group(root)

    for value in root.findall(".//x:Value", NS):
        source_id = value.get("id") or f"value-{len(parameters)+1}"
        native_id = _native_id(source_id, f"parameter-{len(parameters)+1}")
        source_to_native[source_id] = native_id
        provenance_key("value", source_id)
        default = None
        value_nodes = value.findall("x:value", NS)
        if value_nodes:
            default = _text(value_nodes[0])
        parameters.append(
            ParameterIR(
                id=native_id,
                title=_text(value.find("x:title", NS)),
                datatype=value.get("type"),
                interactive=(
                    None if value.get("interactive") is None
                    else value.get("interactive", "").lower() == "true"
                ),
                default_value=default,
            )
        )

    for profile in root.findall("x:Profile", NS):
        source_id = profile.get("id") or f"profile-{len(profiles)+1}"
        native_id = _native_id(source_id, f"profile-{len(profiles)+1}")
        source_to_native[source_id] = native_id
        provenance_key("profile", source_id)
        selections: dict[str, bool] = {}
        for select in profile.findall("x:select", NS):
            ref = select.get("idref")
            if ref:
                selections[ref] = (select.get("selected") or "true").lower() == "true"
        check_selectors: dict[str, str] = {}
        for refine in profile.findall("x:refine-rule", NS):
            ref = refine.get("idref")
            selector = refine.get("selector")
            if ref and selector:
                check_selectors[ref] = selector
        bindings: dict[str, str] = {}
        for set_value in profile.findall("x:set-value", NS):
            ref = set_value.get("idref")
            if ref:
                bindings[ref] = _text(set_value) or ""
        profiles.append(
            ProfileIR(
                id=native_id,
                title=_text(profile.find("x:title", NS)),
                extends=profile.get("extends"),
                selections=selections,
                check_selectors=check_selectors,
                parameter_bindings=bindings,
            )
        )

    benchmark_platforms = [
        p.get("idref") for p in root.findall("x:platform", NS) if p.get("idref")
    ]

    ir = {
        "ir_version": IR_VERSION,
        "benchmark": {
            "id": benchmark_id,
            "title": title,
            "version": version,
            "status": _text(status_node),
            "platform_refs": benchmark_platforms,
            "rules": [asdict(x) for x in rules],
            "groups": [asdict(x) for x in groups],
            "profiles": [asdict(x) for x in profiles],
            "parameters": [asdict(x) for x in parameters],
        },
    }

    # Resolve source policy references to native IDs wherever the reference is
    # inside this Benchmark.  Cross-component assessment references intentionally
    # remain resolver keys until the assessment semantic stage.
    def resolve_ref(value: str) -> str:
        return source_to_native.get(value, value)

    ir["benchmark"]["platform_refs"] = [resolve_ref(x) for x in benchmark_platforms]
    for rule in ir["benchmark"]["rules"]:
        rule["applicability"] = [resolve_ref(x) for x in rule["applicability"]]
        rule["requires"] = [resolve_ref(x) for x in rule["requires"]]
        rule["conflicts"] = [resolve_ref(x) for x in rule["conflicts"]]
    for profile in ir["benchmark"]["profiles"]:
        profile["selections"] = {
            resolve_ref(k): v for k, v in profile["selections"].items()
        }
        profile["check_selectors"] = {
            resolve_ref(k): v for k, v in profile["check_selectors"].items()
        }
        profile["parameter_bindings"] = {
            resolve_ref(k): v for k, v in profile["parameter_bindings"].items()
        }
        if profile["extends"]:
            profile["extends"] = resolve_ref(profile["extends"])

    diag_doc = {
        "ir_version": IR_VERSION,
        "source_sha256": provenance["source"]["sha256"],
        "diagnostics": [asdict(x) for x in diagnostics],
    }
    return ir, provenance, diag_doc
