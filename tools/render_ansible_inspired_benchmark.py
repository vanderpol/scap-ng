#!/usr/bin/env python3
"""Render a converted canonical SCAP-NG benchmark in Ansible-inspired YAML.

This is an authoring-style rendering only. It preserves the same canonical
policy and assessment semantics used by the combined-rule and split
policy/assessment/binding renderings. There is no Ansible runtime dependency.
"""
from __future__ import annotations

import argparse
import copy
import json
import re
import shutil
from pathlib import Path

import yaml


SPEC = "0.1-prototype"


def safe_id(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_") or "unnamed"


def dump_yaml(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(value, sort_keys=False, allow_unicode=True, width=120),
        encoding="utf-8",
    )


def fqcn_capability(value: str) -> str:
    if value.startswith("scapng."):
        return value
    return "scapng." + value.replace("-", "_")


def transform_collect(name: str, body: dict) -> dict:
    converted = copy.deepcopy(body)
    capability = converted.get("capability")
    if isinstance(capability, str):
        converted["capability"] = fqcn_capability(capability)
    return {
        "name": f"Collect {name}",
        "collect": converted,
        "register": name,
    }


def transform_derive(name: str, body: dict) -> dict:
    return {
        "name": f"Derive {name}",
        "derive": copy.deepcopy(body),
        "register": name,
    }


def transform_assessment(source: dict) -> dict:
    if source is None:
        return None

    out = {}
    for key in ("id", "version", "description", "semantic_model"):
        if key in source:
            out[key] = copy.deepcopy(source[key])

    out["name"] = source.get("description") or source.get("id") or "SCAP-NG assessment"

    steps = []
    for key, body in (source.get("collect") or {}).items():
        steps.append(transform_collect(key, body))
    for key, body in (source.get("derive") or {}).items():
        steps.append(transform_derive(key, body))
    if steps:
        out["steps"] = steps

    # These are semantic sections, not Ansible task syntax. Preserve them
    # explicitly rather than translating them into string expressions.
    for key in (
        "predicates",
        "evaluate",
        "source_check_context",
        "source_check_logic",
        "source_result_algebra",
        "method",
        "source_checks",
        "procedure",
    ):
        if key in source:
            out[key] = copy.deepcopy(source[key])

    if "assert" in source:
        out["assert"] = {"that": copy.deepcopy(source["assert"])}

    for key in ("diagnostics", "evidence", "evaluation", "migration"):
        if key in source:
            out[key] = copy.deepcopy(source[key])

    if "semantic_fingerprint_sha256" in source:
        out["semantic_fingerprint_sha256"] = source["semantic_fingerprint_sha256"]

    return out


def benchmark_doc(canonical: dict) -> dict:
    benchmark = canonical.get("benchmark", {})
    return {
        "scap_ng": SPEC,
        "prototype": True,
        "authoring_style": "ansible-inspired",
        "runtime_dependency": "none",
        "benchmark": {
            "id": benchmark.get("id"),
            "title": benchmark.get("title"),
            "version": benchmark.get("version"),
            "status": "converted-research-prototype",
            "source_component": benchmark.get("component_id"),
            "rule_count": benchmark.get("rule_count"),
            "group_count": benchmark.get("group_count"),
            "profile_count": benchmark.get("profile_count"),
            "value_count": benchmark.get("value_count"),
            "platforms": copy.deepcopy(benchmark.get("platforms", [])),
            "effective_platforms": copy.deepcopy(benchmark.get("effective_platforms", [])),
            "references": copy.deepcopy(benchmark.get("references", [])),
            "source_status": copy.deepcopy(benchmark.get("status", [])),
            "rules": [
                row.get("policy", {}).get("id")
                for row in canonical.get("rules", [])
                if row.get("policy", {}).get("id")
            ],
            "source": copy.deepcopy(canonical.get("source")),
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("canonical_benchmark", type=Path)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()

    canonical = json.loads(args.canonical_benchmark.read_text(encoding="utf-8"))
    out = args.output_dir
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    dump_yaml(out / "benchmark.yaml", benchmark_doc(canonical))
    dump_yaml(out / "processing.yaml", {
        "scap_ng": SPEC,
        "prototype": True,
        "authoring_style": "ansible-inspired",
        "runtime_dependency": "none",
        "processing_plan": canonical.get("processing_plan"),
    })
    dump_yaml(out / "platforms.yaml", {
        "scap_ng": SPEC,
        "prototype": True,
        "authoring_style": "ansible-inspired",
        "runtime_dependency": "none",
        "platform_definitions": canonical.get("platform_definitions", []),
        "inventory_assessments": [
            {
                **copy.deepcopy(row),
                "assessment": transform_assessment(row.get("assessment")),
            }
            for row in canonical.get("platform_inventory_assessments", [])
        ],
        "applicability_assessment": (
            transform_assessment(
                (canonical.get("applicability") or {}).get("assessment")
            )
        ),
        "applicability_migration": (
            (canonical.get("applicability") or {}).get("migration")
        ),
    })
    dump_yaml(out / "profiles.yaml", {
        "scap_ng": SPEC,
        "prototype": True,
        "authoring_style": "ansible-inspired",
        "runtime_dependency": "none",
        "profiles": canonical.get("profiles", []),
        "resolved_profiles": canonical.get("resolved_profiles", []),
        "check_selectors": canonical.get("profile_check_selectors", []),
    })
    dump_yaml(out / "groups.yaml", {
        "scap_ng": SPEC,
        "prototype": True,
        "authoring_style": "ansible-inspired",
        "runtime_dependency": "none",
        "groups": canonical.get("groups", []),
    })
    dump_yaml(out / "values.yaml", {
        "scap_ng": SPEC,
        "prototype": True,
        "authoring_style": "ansible-inspired",
        "runtime_dependency": "none",
        "values": canonical.get("values", []),
    })

    bindings = []
    summary = {
        "rules": 0,
        "assessments": 0,
        "blocked_rules": 0,
        "runtime_dependency": "none",
        "authoring_style": "ansible-inspired",
    }

    for row in canonical.get("rules", []):
        policy = copy.deepcopy(row.get("policy"))
        migration = copy.deepcopy(row.get("migration"))
        assessments = row.get("assessments")
        if assessments is None:
            assessments = [row.get("assessment")] if row.get("assessment") else []
        rid = policy["id"]

        dump_yaml(
            out / "policy" / "rules" / f"{safe_id(rid)}.yaml",
            {
                "scap_ng": SPEC,
                "prototype": True,
                "authoring_style": "ansible-inspired",
                "rule": policy,
                "migration": migration,
            },
        )
        summary["rules"] += 1

        if migration and migration.get("status") == "unsupported":
            summary["blocked_rules"] += 1
            continue

        rendered_by_id = {}
        for assessment in assessments:
            rendered = transform_assessment(assessment)
            if rendered is None:
                continue
            aid = rendered["id"]
            rendered_by_id[aid] = rendered
            dump_yaml(
                out / "automation" / "assessments" / f"{safe_id(aid)}.yaml",
                {
                    "scap_ng": SPEC,
                    "prototype": True,
                    "authoring_style": "ansible-inspired",
                    "runtime_dependency": "none",
                    "assessment": rendered,
                },
            )
            summary["assessments"] += 1

        binding = {
            "rule": rid,
            "checks": copy.deepcopy(policy.get("checks", [])),
            "migration_status": migration.get("status") if migration else None,
        }
        if policy.get("default_check") is not None:
            binding["default_check"] = policy["default_check"]
            default_row = next(
                x for x in policy.get("checks", [])
                if x.get("selector") == policy["default_check"]
            )
            binding["assessment"] = default_row["assessment"]
            binding["assessment_version"] = default_row.get("assessment_version", 1)
            binding["check_selector"] = policy["default_check"]
        elif row.get("assessment") is not None:
            binding["assessment"] = row["assessment"]["id"]
            binding["assessment_version"] = row["assessment"].get("version", 1)
        bindings.append(binding)

    dump_yaml(
        out / "automation" / "bindings.yaml",
        {
            "scap_ng": SPEC,
            "prototype": True,
            "authoring_style": "ansible-inspired",
            "runtime_dependency": "none",
            "bindings": bindings,
        },
    )
    dump_yaml(
        out / "README.yaml",
        {
            "scap_ng": SPEC,
            "prototype": True,
            "authoring_style": "ansible-inspired",
            "runtime_dependency": "none",
            "purpose": (
                "Alternative human-facing YAML syntax generated from the same "
                "canonical SCAP-NG benchmark semantics. It does not require or "
                "execute Ansible."
            ),
            "semantic_contract": (
                "Must round-trip to the same canonical benchmark semantics as "
                "combined-rule and split policy/assessment/binding renderings."
            ),
        },
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
