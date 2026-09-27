#!/usr/bin/env python3
"""Render iteration 001 assessments in an Ansible-inspired SCAP-NG YAML style.

This is an authoring-syntax experiment only. It does not import Ansible or
Jinja and does not change canonical assessment semantics.

Current input is the iteration 001 native split-assessment prototype. The
long-term conversion pipeline will feed this renderer from the common faithful
SCAP 1.4 semantic IR.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import re
import shutil

import yaml

SOURCE_ROOT = Path("research/iterations/001/prototypes/oval-migration-cases")
OUTPUT_ROOT = Path("research/iterations/001/prototypes/ansible-inspired-authoring")
REF_RE = re.compile(r"^\\$(?:derived\\.)?([A-Za-z_][A-Za-z0-9_-]*)")


def references(value, candidates: set[str]) -> set[str]:
    found: set[str] = set()
    if isinstance(value, str):
        m = REF_RE.match(value)
        if m and m.group(1) in candidates:
            found.add(m.group(1))
    elif isinstance(value, dict):
        for v in value.values():
            found |= references(v, candidates)
    elif isinstance(value, list):
        for v in value:
            found |= references(v, candidates)
    return found


def clean_reference(value):
    if isinstance(value, str) and value.startswith("$"):
        value = value[1:]
        if value.startswith("derived."):
            value = value[len("derived."):]
        return value
    if isinstance(value, dict):
        return {k: clean_reference(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_reference(v) for v in value]
    return value


def fqcn_capability(value: str) -> str:
    if value.startswith("scapng."):
        return value
    return "scapng." + value.replace("-", "_")


def ordered_nodes(assessment: dict) -> list[tuple[str, str, object]]:
    collect = assessment.get("collect", {}) or {}
    derive = assessment.get("derive", {}) or {}
    source_order = [
        *[("collect", k, v) for k, v in collect.items()],
        *[("derive", k, v) for k, v in derive.items()],
    ]
    candidates = {k for _, k, _ in source_order}
    deps = {
        key: references(body, candidates) - {key}
        for _, key, body in source_order
    }

    emitted: set[str] = set()
    result: list[tuple[str, str, object]] = []
    remaining = list(source_order)

    while remaining:
        progressed = False
        for idx, (kind, key, body) in enumerate(remaining):
            if deps[key] <= emitted:
                result.append((kind, key, body))
                emitted.add(key)
                remaining.pop(idx)
                progressed = True
                break
        if not progressed:
            cycle = {key: sorted(deps[key] - emitted) for _, key, _ in remaining}
            raise ValueError(f"dependency cycle/unresolved reference: {cycle}")

    return result


def transform_assessment(doc: dict, source_rel: str) -> dict:
    source = doc["assessment"]
    out_assessment = {}

    for key in ("id", "version", "description", "parameters"):
        if key in source:
            out_assessment[key] = copy.deepcopy(source[key])

    out_assessment["name"] = source.get(
        "description",
        source.get("id", "SCAP-NG assessment"),
    )

    steps = []
    for kind, key, body in ordered_nodes(source):
        converted = clean_reference(copy.deepcopy(body))
        if kind == "collect" and isinstance(converted, dict):
            cap = converted.get("capability")
            if isinstance(cap, str):
                converted["capability"] = fqcn_capability(cap)
        steps.append({
            "name": f"{'Collect' if kind == 'collect' else 'Derive'} "
                    f"{key.replace('-', ' ').replace('_', ' ')}",
            kind: converted,
            "register": key,
        })
    out_assessment["steps"] = steps

    if "applies_when" in source:
        out_assessment["applies_when"] = clean_reference(
            copy.deepcopy(source["applies_when"])
        )

    if "assert" in source:
        out_assessment["assert"] = {
            "that": clean_reference(copy.deepcopy(source["assert"]))
        }

    for key in ("diagnostics", "evidence", "evaluation"):
        if key in source:
            out_assessment[key] = clean_reference(copy.deepcopy(source[key]))

    return {
        "scap_ng": doc.get("scap_ng", "0.1-prototype"),
        "prototype": True,
        "authoring_style": "ansible-inspired",
        "runtime_dependency": "none",
        "source_assessment": source_rel,
        "assessment": out_assessment,
    }


def transform_bindings(doc: dict) -> dict:
    out = copy.deepcopy(doc)
    for binding in out.get("bindings", []):
        if "parameters" in binding:
            binding["vars"] = binding.pop("parameters")
    out["authoring_style"] = "ansible-inspired"
    return out


README = """# Ansible-Inspired SCAP-NG Authoring Experiment

Iteration: 001
Status: Generated parallel syntax experiment
Ansible runtime dependency: NONE

This directory is generated from the same native assessment semantics used by
the existing real-world OVAL migration cases. The original prototypes under
../oval-migration-cases/ are not modified.

The experiment tests whether familiar Ansible authoring conventions improve
readability or instead add ceremony.

Conventions tested:
- name for human-readable steps
- ordered steps
- register for typed evidence/derived-value bindings
- vars in bindings for declared parameter values
- assert/that assertion blocks
- FQCN-like capability names such as scapng.linux.audit.effective_rules

SCAP-NG-specific semantics remain explicit:
- every, any, and none
- cardinality
- typed comparison operators
- applies_when
- deterministic if/elif/else
- diagnostic/evidence limits

Not supported:
- Jinja2
- template expressions
- arbitrary string condition expressions
- handlers
- mutable facts
- task side effects
- Python execution
- Ansible inventory/plugins/runtime

This is not a second scanner format. Both authoring spellings must compile to
the same canonical SCAP-NG semantic model.

Long-term hard requirement:
SCAP 1.4 -> faithful semantic IR -> both authoring renderings -> equivalent canonical NG

See comparison-metrics.json for descriptive size/line comparisons.
"""


def main() -> int:
    if OUTPUT_ROOT.exists():
        shutil.rmtree(OUTPUT_ROOT)
    OUTPUT_ROOT.mkdir(parents=True)
    (OUTPUT_ROOT / "README.md").write_text(README, encoding="utf-8")

    metrics = []
    for src in sorted(SOURCE_ROOT.glob("*/split/assessment.yaml")):
        case = src.parents[1].name
        case_out = OUTPUT_ROOT / case
        case_out.mkdir(parents=True, exist_ok=True)

        doc = yaml.safe_load(src.read_text(encoding="utf-8"))
        rendered = transform_assessment(doc, src.as_posix())
        text = yaml.safe_dump(
            rendered,
            sort_keys=False,
            allow_unicode=True,
            width=100,
        )
        target = case_out / "assessment.yaml"
        target.write_text(text, encoding="utf-8")

        binding_src = src.parent / "bindings.yaml"
        if binding_src.exists():
            binding_doc = yaml.safe_load(binding_src.read_text(encoding="utf-8"))
            binding_text = yaml.safe_dump(
                transform_bindings(binding_doc),
                sort_keys=False,
                allow_unicode=True,
                width=100,
            )
            (case_out / "bindings.yaml").write_text(binding_text, encoding="utf-8")

        source_text = src.read_text(encoding="utf-8")
        metrics.append({
            "case": case,
            "original_path": src.as_posix(),
            "ansible_inspired_path": target.as_posix(),
            "original_bytes": len(source_text.encode("utf-8")),
            "ansible_inspired_bytes": len(text.encode("utf-8")),
            "original_lines": len(source_text.splitlines()),
            "ansible_inspired_lines": len(text.splitlines()),
            "byte_ratio_ansible_to_original": round(
                len(text.encode("utf-8")) / max(1, len(source_text.encode("utf-8"))), 3
            ),
            "line_ratio_ansible_to_original": round(
                len(text.splitlines()) / max(1, len(source_text.splitlines())), 3
            ),
        })

    (OUTPUT_ROOT / "comparison-metrics.json").write_text(
        json.dumps(metrics, indent=2, sort_keys=True) + "\\n",
        encoding="utf-8",
    )
    print(f"Generated {len(metrics)} Ansible-inspired assessment renderings")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
