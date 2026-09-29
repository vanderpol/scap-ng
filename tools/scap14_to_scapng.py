#!/usr/bin/env python3
"""Compile unified SCAP 1.4 benchmark IR into candidate SCAP-NG source layouts.

This is the first generic migration compiler. It does not embed source XML as
runtime behavior. OVAL definitions/tests/objects/states/variables are lowered
to a structured SCAP-NG assessment graph. Until a collector/native mapping is
reviewed, automated assessments are marked legacy_compatible rather than
exact_native. Effectively deprecated OVAL tests are hard conversion blockers.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import shutil
from pathlib import Path

import yaml


SPEC = "0.1-prototype"


def safe_id(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_") or "unnamed"


def canonical_digest(value) -> str:
    data = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def load_catalog(path: Path | None) -> dict[str, dict]:
    if path is None:
        return {}
    doc = json.loads(path.read_text(encoding="utf-8"))
    return {
        f'{row.get("namespace","")}#{row.get("name","")}': row
        for row in doc.get("test_elements", [])
    }


def effective_deprecated_tests(ir: dict, catalog: dict[str, dict]) -> list[dict]:
    blocked = []
    for test in ir.get("tests", []):
        key = f'{test.get("namespace","")}#{test.get("type","")}'
        row = catalog.get(key)
        if not row:
            continue
        effective = row.get("effective_deprecated", row.get("deprecated", False))
        if effective:
            blocked.append({
                "test_id": test.get("id"),
                "qualified_type": key,
                "deprecation_evidence": row.get("deprecation_evidence"),
                "support_override": row.get("support_override"),
            })
    return blocked


def family(namespace: str) -> str:
    if "#" in namespace:
        return namespace.rsplit("#", 1)[-1]
    return namespace.rsplit("/", 1)[-1] or "core"


def strip_suffix(value: str, suffix: str) -> str:
    return value[:-len(suffix)] if value.endswith(suffix) else value


def collector_node(obj: dict) -> dict:
    fam = family(obj.get("namespace", ""))
    base = strip_suffix(obj.get("type", "object"), "_object")
    return {
        "capability": f"scapng.collect.{fam}.{base}",
        "source_object_id": obj.get("id"),
        "source_type": obj.get("type"),
        "source_namespace": obj.get("namespace"),
        "version": obj.get("version"),
        "object_title": obj.get("comment"),
        "query": copy.deepcopy(obj.get("children", [])),
    }


def predicate_node(state: dict) -> dict:
    return {
        "source_state_id": state.get("id"),
        "source_type": state.get("type"),
        "source_namespace": state.get("namespace"),
        "operator": state.get("operator", "AND"),
        "entities": copy.deepcopy(state.get("entities", [])),
        "state_title": state.get("comment"),
    }


def variable_node(variable: dict, ir: dict) -> dict:
    vid = variable.get("id")
    resolution = ir.get("variable_resolution", {}).get(vid)
    plan = ir.get("variable_evaluation_plans", {}).get(vid)
    return {
        "source_variable_id": vid,
        "source_type": variable.get("type"),
        "datatype": variable.get("datatype"),
        "variable_title": variable.get("comment"),
        "semantic_ast": copy.deepcopy(variable.get("semantic_ast")),
        "resolution": copy.deepcopy(resolution),
        "evaluation_plan": copy.deepcopy(plan),
    }


def test_node(test: dict) -> dict:
    return {
        "source_test_id": test.get("id"),
        "source_type": test.get("type"),
        "source_namespace": test.get("namespace"),
        "test_title": test.get("comment"),
        "check": test.get("check", "all"),
        "check_existence": test.get("check_existence", "at_least_one_exists"),
        "state_operator": test.get("state_operator", "AND"),
        "collections": [
            x.get("object_ref") for x in test.get("objects", []) if x.get("object_ref")
        ],
        "predicates": [
            x.get("state_ref") for x in test.get("states", []) if x.get("state_ref")
        ],
        "source_other": copy.deepcopy(test.get("other", [])),
    }


def definition_node(definition: dict) -> dict:
    return {
        "source_definition_id": definition.get("id"),
        "class": definition.get("class"),
        "version": definition.get("version"),
        "criteria": copy.deepcopy(definition.get("criteria")),
        "metadata": copy.deepcopy(definition.get("metadata")),
    }


def root_definitions(ir: dict) -> list[str]:
    refs = []
    for check in ir.get("xccdf_context", {}).get("checks", []):
        did = check.get("definition_id")
        if did and did not in refs:
            refs.append(did)
    return refs


def compile_oval_assessment(rule: dict, ir: dict, catalog: dict[str, dict]) -> tuple[dict | None, dict]:
    blocked = effective_deprecated_tests(ir, catalog)
    if blocked:
        return None, {
            "status": "unsupported",
            "reason": "deprecated_oval_test",
            "deprecated_tests": blocked,
            "message": (
                "Update the SCAP 1.4 source to supported OVAL tests before "
                "SCAP-NG conversion."
            ),
        }

    assessment = {
        "id": f"ng.scap14.{safe_id(rule['id'])}",
        "version": 1,
        "description": rule.get("title"),
        "semantic_model": "scap-ng-generic-assessment-graph-0.1",
        "collect": {
            obj["id"]: collector_node(obj)
            for obj in ir.get("objects", [])
            if obj.get("id")
        },
        "derive": {
            var["id"]: variable_node(var, ir)
            for var in ir.get("variables", [])
            if var.get("id")
        },
        "predicates": {
            state["id"]: predicate_node(state)
            for state in ir.get("states", [])
            if state.get("id")
        },
        "evaluate": {
            "tests": {
                test["id"]: test_node(test)
                for test in ir.get("tests", [])
                if test.get("id")
            },
            "definitions": {
                definition["id"]: definition_node(definition)
                for definition in ir.get("definitions", [])
                if definition.get("id")
            },
        },
        "assert": {
            "definition_results": root_definitions(ir),
            "combination": "xccdf_source_check_semantics",
        },
        "source_check_context": copy.deepcopy(ir.get("xccdf_context", {})),
        "source_check_logic": copy.deepcopy(rule.get("check_model")),
        "source_result_algebra": "xccdf-1.2-complex-check-eight-state",
        "migration": {
            "status": "legacy_compatible",
            "source": "SCAP 1.4 / OVAL 5.12.3",
            "source_rule": rule.get("id"),
            "semantic_ir_sha256": ir.get("semantic_ir_sha256"),
            "note": (
                "Faithful generic assessment graph. Native collector/capability "
                "mappings remain subject to reviewed promotion."
            ),
        },
    }
    assessment["semantic_fingerprint_sha256"] = canonical_digest({
        k: v for k, v in assessment.items()
        if k not in {"description", "source_check_context", "migration"}
    })
    return assessment, assessment["migration"]


def manual_assessment(rule: dict, checks: list[dict] | None = None) -> tuple[dict, dict]:
    checks = copy.deepcopy(checks if checks is not None else rule.get("checks", []))
    assessment = {
        "id": f"ng.manual.{safe_id(rule['id'])}",
        "version": 1,
        "description": rule.get("title"),
        "method": "manual_or_external_check",
        "source_checks": checks,
        "source_check_logic": copy.deepcopy(rule.get("check_model")),
        "source_result_algebra": "xccdf-1.2-complex-check-eight-state",
        "procedure": next(
            (
                check.get("inline_content")
                for check in checks
                if check.get("inline_content")
            ),
            None,
        ),
        "migration": {
            "status": "legacy_compatible",
            "source": "SCAP 1.4 XCCDF manual/external check",
            "source_rule": rule.get("id"),
            "note": (
                "The source Check Text/check reference is preserved. Dedicated "
                "OCIL questionnaire lowering is not required for manual execution."
            ),
        },
    }
    assessment["semantic_fingerprint_sha256"] = canonical_digest({
        "method": assessment["method"],
        "source_checks": assessment["source_checks"],
        "procedure": assessment["procedure"],
    })
    return assessment, assessment["migration"]


def normalized_check_selector(value) -> str:
    """Return the SCAP-NG selector name used for an XCCDF check candidate."""
    return value if value not in (None, "") else "default"


def check_implementation_kind(check: dict) -> str:
    """Classify one XCCDF check candidate by the implementation we can lower."""
    system = (check.get("system") or "").lower()
    if "oval" in system:
        return "automated"
    if "ocil" in system or check.get("inline_content"):
        return "manual"
    return "external"


def check_selection_plan(
    rule: dict,
    implementations: dict[str, dict | None],
) -> tuple[dict | None, dict | None]:
    """Lower XCCDF check-selector candidates without losing alternatives.

    Different selector names may resolve to the same Assessment implementation
    (for example, an empty/default OVAL check and an `automated` OVAL check).
    A manual selector may resolve to the Rule's Check Text Manual Assessment.
    Checking-system fallback *within the same selector* is blocked unless the
    candidates are semantically identical.
    """
    checks = copy.deepcopy(rule.get("checks", []))
    if not checks:
        return None, None

    grouped: dict[str, list[dict]] = {}
    source_selectors: dict[str, object] = {}
    for check in checks:
        source_selector = check.get("selector")
        selector = normalized_check_selector(source_selector)
        grouped.setdefault(selector, []).append(check)
        source_selectors.setdefault(selector, source_selector)

    rows = []
    for selector, candidates in grouped.items():
        kinds = {check_implementation_kind(x) for x in candidates}
        if len(kinds) != 1:
            return None, {
                "status": "unsupported",
                "reason": "check_system_fallback_not_lowered",
                "selector": selector,
                "systems": [x.get("system") for x in candidates],
                "message": (
                    "One XCCDF selector has multiple checking-system alternatives. "
                    "The source fallback order must be represented explicitly before "
                    "conversion may succeed."
                ),
            }

        # More than one candidate under the same selector is only safe to merge
        # when their source check semantics are identical.
        if len(candidates) > 1:
            semantic_keys = {
                canonical_digest({
                    "system": x.get("system"),
                    "negate": x.get("negate"),
                    "multi_check": x.get("multi_check"),
                    "exports": x.get("exports", []),
                    "content_refs": x.get("content_refs", []),
                    "inline_content": x.get("inline_content"),
                })
                for x in candidates
            }
            if len(semantic_keys) != 1:
                return None, {
                    "status": "unsupported",
                    "reason": "same_selector_alternatives_not_lowered",
                    "selector": selector,
                    "message": (
                        "Multiple non-equivalent XCCDF check candidates share one "
                        "selector. Their checking-system/fallback semantics must be "
                        "lowered explicitly before conversion may succeed."
                    ),
                }

        kind = next(iter(kinds))
        assessment = implementations.get(kind)
        if assessment is None:
            return None, {
                "status": "unsupported",
                "reason": "check_selector_without_assessment",
                "selector": selector,
                "implementation_kind": kind,
                "message": (
                    f"XCCDF selector {selector!r} cannot be bound to a converted "
                    f"{kind} Assessment."
                ),
            }
        rows.append({
            "selector": selector,
            "source_selector": source_selectors[selector],
            "assessment": assessment.get("id"),
            "assessment_version": assessment.get("version", 1),
        })

    default_check = (
        "default"
        if any(x.get("selector") in (None, "") for x in checks)
        else None
    )
    result = {"checks": rows}
    if default_check is not None:
        result["default_check"] = default_check
    return result, None


def native_profile_check_selectors(source: dict) -> list[dict]:
    """Project resolved XCCDF refine-rule selectors into native tailoring data."""
    out = []
    for profile in source.get("resolved_profiles", []):
        selections = {}
        for action in profile.get("effective_actions", []):
            if action.get("kind") != "refine-rule":
                continue
            selector = action.get("attributes", {}).get("selector")
            if selector in (None, ""):
                continue
            for target in action.get("targets", []):
                if target.get("kind") == "rule" and target.get("id"):
                    # XCCDF profile actions are ordered; later actions override.
                    selections[target["id"]] = selector
        out.append({
            "profile": profile.get("id"),
            "check_selectors": selections,
        })
    return out


def policy_rule(rule: dict) -> dict:
    fixes = [x for x in rule.get("fixes", []) if x.get("text")]
    return {
        "id": rule.get("id"),
        "title": rule.get("title"),
        "severity": rule.get("severity"),
        "weight": rule.get("weight"),
        "role": rule.get("role"),
        "selected": rule.get("selected"),
        "selected_default": rule.get("selected_default", True),
        "cluster_id": rule.get("cluster_id"),
        "extends": rule.get("extends"),
        "abstract": rule.get("abstract", False),
        "hidden": rule.get("hidden", False),
        "prohibit_changes": rule.get("prohibit_changes", False),
        "multiple": rule.get("multiple", False),
        "group_path": copy.deepcopy(rule.get("group_path", [])),
        "description": rule.get("description"),
        "discussion": rule.get("rationale"),
        "platforms": copy.deepcopy(rule.get("platforms", [])),
        "effective_platform_refs": copy.deepcopy(rule.get("effective_platform_refs", [])),
        "effective_platforms": copy.deepcopy(rule.get("effective_platforms", [])),
        "references": copy.deepcopy(rule.get("references", [])),
        "idents": copy.deepcopy(rule.get("idents", [])),
        "requires": copy.deepcopy(rule.get("requires", [])),
        "conflicts": copy.deepcopy(rule.get("conflicts", [])),
        "check": next(
            (
                c.get("inline_content")
                for c in rule.get("checks", [])
                if c.get("inline_content")
            ),
            None,
        ),
        "source_checks": copy.deepcopy(rule.get("checks", [])),
        "source_check_logic": copy.deepcopy(rule.get("check_model")),
        "fix": "\n\n".join(x["text"] for x in fixes) if fixes else None,
        "source_xccdf_tree": copy.deepcopy(rule.get("source_tree")),
    }


def dump_yaml(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(value, sort_keys=False, allow_unicode=True, width=120),
        encoding="utf-8",
    )


def dump_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def cpe_inventory_output(cpe_name: str | None) -> dict | None:
    if not cpe_name:
        return None
    part=None
    binding=None
    if cpe_name.startswith("cpe:/"):
        fields=cpe_name[5:].split(":")
        part=fields[0] if fields else None
        binding="uri"
    elif cpe_name.startswith("cpe:2.3:"):
        fields=cpe_name.split(":")
        part=fields[2] if len(fields)>2 else None
        binding="formatted_string"
    product_kind={
        "o":"operating_system",
        "a":"application",
        "h":"hardware",
    }.get(part)
    return {
        "emit_when":"platform_true",
        "role":"descriptive_target_inventory",
        "product_kind":product_kind,
        "identifiers":[{
            "scheme":"cpe",
            "binding":binding,
            "value":cpe_name,
        }],
    }


def compile_platform_inventory(source: dict, catalog: dict[str, dict]) -> list[dict]:
    out=[]
    for row in source.get("platform_inventory",[]):
        cpe_name=row.get("cpe_name")
        entry={
            "cpe_name":cpe_name,
            "definition_id":row.get("definition_id"),
            "source_status":row.get("status"),
            "source_path":row.get("path"),
            "source_component":row.get("oval_component"),
            "inventory_output":cpe_inventory_output(cpe_name),
        }
        if row.get("status")!="split_valid" or row.get("oval_ir") is None:
            entry["assessment"]=None
            entry["migration"]={
                "status":"unsupported",
                "reason":"cpe_inventory_source_not_split_valid",
                "source_status":row.get("status"),
                "message":"CPE product inventory source could not be compiled.",
            }
            out.append(entry)
            continue

        assessment,migration=compile_oval_assessment(
            {
                "id":f"platform.inventory.{cpe_name}",
                "title":f"Product inventory for {cpe_name}",
                "check_model":{"kind":"cpe_product_inventory"},
            },
            row["oval_ir"],
            catalog,
        )
        if assessment is not None:
            assessment["purpose"]="platform_inventory"
            assessment["inventory_output"]=cpe_inventory_output(cpe_name)
        entry["assessment"]=assessment
        entry["migration"]=migration
        out.append(entry)
    return out


def render_benchmark_doc(ir: dict, model: str) -> dict:
    benchmark = ir["benchmark"]
    return {
        "scap_ng": SPEC,
        "prototype": True,
        "model": model,
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
            "rules": [x["id"] for x in ir.get("rules", [])],
            "source": copy.deepcopy(ir.get("source")),
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("benchmark_ir", type=Path)
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--schema-catalog", type=Path)
    args = ap.parse_args()

    source = json.loads(args.benchmark_ir.read_text(encoding="utf-8"))
    catalog = load_catalog(args.schema_catalog)

    out = args.output_dir
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    canonical_rules = []
    blocked = []
    manual = []
    automated = []

    platform_inventory_assessments=compile_platform_inventory(source,catalog)

    applicability_source=source.get("applicability",{})
    applicability_assessment=None
    applicability_migration=None
    if applicability_source.get("oval_ir") is not None:
        applicability_assessment,applicability_migration=compile_oval_assessment(
            {
                "id":"applicability",
                "title":"SCAP 1.4 CPE applicability checks",
                "check_model":{"kind":"applicability_check_facts"},
            },
            applicability_source["oval_ir"],
            catalog,
        )

    combined_root = out / "combined-rule"
    split_root = out / "split-policy-assessment-binding"

    dump_yaml(combined_root / "benchmark.yaml", render_benchmark_doc(source, "combined-rule"))
    dump_yaml(split_root / "benchmark.yaml", render_benchmark_doc(source, "split-policy-assessment-binding"))
    if applicability_assessment is not None or applicability_migration is not None:
        applicability_doc={
            "scap_ng":SPEC,
            "prototype":True,
            "assessment":applicability_assessment,
            "migration":applicability_migration,
            "source_diagnostic":applicability_source.get("diagnostic"),
        }
        dump_yaml(combined_root/"applicability.yaml",applicability_doc)
        dump_yaml(split_root/"applicability.yaml",applicability_doc)

    dump_yaml(combined_root / "processing.yaml", {
        "scap_ng": SPEC,
        "prototype": True,
        "processing_plan": source.get("processing_plan"),
    })
    dump_yaml(combined_root / "platforms.yaml", {
        "scap_ng": SPEC,
        "prototype": True,
        "platform_definitions": source.get("platform_definitions", []),
        "inventory_assessments": copy.deepcopy(platform_inventory_assessments),
        "applicability_assessment": (
            applicability_assessment.get("id")
            if applicability_assessment is not None else None
        ),
    })
    dump_yaml(combined_root / "profiles.yaml", {
        "scap_ng": SPEC,
        "prototype": True,
        "profiles": source.get("profiles", []),
        "resolved_profiles": source.get("resolved_profiles", []),
        "check_selectors": native_profile_check_selectors(source),
    })
    dump_yaml(combined_root / "groups.yaml", {
        "scap_ng": SPEC, "prototype": True, "groups": source.get("groups", [])
    })
    dump_yaml(combined_root / "values.yaml", {
        "scap_ng": SPEC, "prototype": True, "values": source.get("values", [])
    })
    dump_yaml(split_root / "processing.yaml", {
        "scap_ng": SPEC,
        "prototype": True,
        "processing_plan": source.get("processing_plan"),
    })
    dump_yaml(split_root / "platforms.yaml", {
        "scap_ng": SPEC,
        "prototype": True,
        "platform_definitions": source.get("platform_definitions", []),
        "inventory_assessments": copy.deepcopy(platform_inventory_assessments),
        "applicability_assessment": (
            applicability_assessment.get("id")
            if applicability_assessment is not None else None
        ),
    })
    dump_yaml(split_root / "profiles.yaml", {
        "scap_ng": SPEC,
        "prototype": True,
        "profiles": source.get("profiles", []),
        "resolved_profiles": source.get("resolved_profiles", []),
        "check_selectors": native_profile_check_selectors(source),
    })
    dump_yaml(split_root / "groups.yaml", {
        "scap_ng": SPEC, "prototype": True, "groups": source.get("groups", [])
    })
    dump_yaml(split_root / "values.yaml", {
        "scap_ng": SPEC, "prototype": True, "values": source.get("values", [])
    })

    bindings = []

    for rule in source.get("rules", []):
        policy = policy_rule(rule)
        assessment_source = rule.get("assessment_source") or {}
        source_checks = copy.deepcopy(rule.get("checks", []))
        manual_checks = [
            x for x in source_checks if check_implementation_kind(x) == "manual"
        ]

        automated_assessment = None
        automated_migration = None
        if assessment_source.get("kind") == "oval_semantic_ir":
            automated_assessment, automated_migration = compile_oval_assessment(
                rule, assessment_source["ir"], catalog
            )

        manual_impl = None
        manual_migration = None
        if manual_checks or assessment_source.get("kind") != "oval_semantic_ir":
            manual_impl, manual_migration = manual_assessment(
                rule, manual_checks if manual_checks else source_checks
            )

        # A failure to lower any published automated alternative blocks the Rule
        # even when a manual alternative is available: Stage-1 conversion is
        # lossless across the complete selectable-check set.
        migration = automated_migration or manual_migration or {
            "status": "unsupported",
            "reason": "no_assessment_implementation",
            "source_rule": rule.get("id"),
        }

        implementations = {
            "automated": automated_assessment,
            "manual": manual_impl,
        }
        selection, selection_error = check_selection_plan(rule, implementations)
        if selection_error is not None and migration.get("status") != "unsupported":
            migration = {
                **selection_error,
                "source": "SCAP 1.4 XCCDF check selection",
                "source_rule": rule.get("id"),
            }
        elif selection is not None and migration.get("status") != "unsupported":
            policy = {**policy, **selection}

        rule_assessments = []
        for candidate in (automated_assessment, manual_impl):
            if candidate is not None and candidate.get("id") not in {
                x.get("id") for x in rule_assessments
            }:
                rule_assessments.append(candidate)

        primary_assessment = automated_assessment or manual_impl
        if migration.get("status") == "unsupported":
            primary_assessment = None
            rule_assessments = []

        canonical = {
            "policy": policy,
            "assessment": primary_assessment,
            "assessments": rule_assessments,
            "migration": migration,
            "source_split_diagnostic": copy.deepcopy(rule.get("split_diagnostic")),
        }
        canonical["semantic_fingerprint_sha256"] = canonical_digest({
            "policy": policy,
            "assessments": rule_assessments,
            "migration_status": migration.get("status"),
        })
        canonical_rules.append(canonical)

        if migration.get("status") == "unsupported":
            blocked.append({
                "rule_id": rule.get("id"),
                "title": rule.get("title"),
                "migration": migration,
            })
            combined_doc = {
                "scap_ng": SPEC,
                "prototype": True,
                "model": "combined-rule",
                "rule": {
                    **policy,
                    "migration": migration,
                },
            }
            dump_yaml(
                combined_root / "rules" / f"{safe_id(rule['id'])}.yaml",
                combined_doc,
            )
            dump_yaml(
                split_root / "policy" / "rules" / f"{safe_id(rule['id'])}.yaml",
                {"scap_ng": SPEC, "prototype": True, "rule": {
                    **policy, "migration": migration
                }},
            )
            continue

        if automated_assessment is not None:
            automated.append(rule["id"])
        else:
            manual.append(rule["id"])

        combined_doc = {
            "scap_ng": SPEC,
            "prototype": True,
            "model": "combined-rule",
            "rule": {
                **policy,
                "assessment": primary_assessment,
                "assessments": rule_assessments,
                "migration": migration,
            },
        }
        dump_yaml(
            combined_root / "rules" / f"{safe_id(rule['id'])}.yaml",
            combined_doc,
        )

        dump_yaml(
            split_root / "policy" / "rules" / f"{safe_id(rule['id'])}.yaml",
            {"scap_ng": SPEC, "prototype": True, "rule": policy},
        )
        for assessment in rule_assessments:
            aid = assessment["id"]
            dump_yaml(
                split_root / "automation" / "assessments" / f"{safe_id(aid)}.yaml",
                {
                    "scap_ng": SPEC,
                    "prototype": True,
                    "model": "split-policy-assessment-binding",
                    "assessment": assessment,
                },
            )

        binding = {
            "rule": rule["id"],
            "checks": copy.deepcopy(policy.get("checks", [])),
            "migration_status": migration.get("status"),
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
        elif primary_assessment is not None:
            # Compatibility field for prototype tooling. Runtime selection is
            # governed by the explicit checks list, not this field.
            binding["assessment"] = primary_assessment["id"]
            binding["assessment_version"] = primary_assessment.get("version", 1)
        bindings.append(binding)

    dump_yaml(
        split_root / "automation" / "bindings.yaml",
        {
            "scap_ng": SPEC,
            "prototype": True,
            "model": "split-policy-assessment-binding",
            "bindings": bindings,
        },
    )

    canonical_doc = {
        "format": "scap-ng-converted-benchmark-canonical-0.1",
        "source": source.get("source"),
        "benchmark": source.get("benchmark"),
        "applicability":{
            "assessment":applicability_assessment,
            "migration":applicability_migration,
            "source_diagnostic":applicability_source.get("diagnostic"),
        },
        "processing_plan": source.get("processing_plan"),
        "platform_definitions": source.get("platform_definitions", []),
        "platform_inventory_assessments": platform_inventory_assessments,
        "profiles": source.get("profiles", []),
        "resolved_profiles": source.get("resolved_profiles", []),
        "profile_check_selectors": native_profile_check_selectors(source),
        "groups": source.get("groups", []),
        "values": source.get("values", []),
        "rules": canonical_rules,
    }
    dump_json(out / "canonical-benchmark.json", canonical_doc)

    summary = {
        "source_rules": len(source.get("rules", [])),
        "applicability_definition_count":len(
            applicability_source.get("diagnostic",{}).get("definition_ids",[])
        ),
        "applicability_assessment_present":applicability_assessment is not None,
        "applicability_migration_status":(
            applicability_migration.get("status")
            if applicability_migration is not None else None
        ),
        "traversal_items":len((source.get("processing_plan") or {}).get("traversal",[])),
        "platform_definitions":len(source.get("platform_definitions",[])),
        "platform_inventory_assessments":len(platform_inventory_assessments),
        "platform_inventory_supported":sum(
            1 for x in platform_inventory_assessments
            if (x.get("migration") or {}).get("status")!="unsupported"
        ),
        "platform_inventory_blocked":sum(
            1 for x in platform_inventory_assessments
            if (x.get("migration") or {}).get("status")=="unsupported"
        ),
        "source_groups":len(source.get("groups",[])),
        "source_profiles":len(source.get("profiles",[])),
        "resolved_profiles":len(source.get("resolved_profiles",[])),
        "profile_resolution_requires_review":sum(
            1 for x in source.get("resolved_profiles",[])
            if x.get("resolution_status")!="resolved"
        ),
        "source_values":len(source.get("values",[])),
        "rules_with_complex_check":sum(
            1 for x in source.get("rules",[])
            if x.get("check_model",{}).get("kind")=="complex_check"
        ),
        "rules_with_item_extends":sum(1 for x in source.get("rules",[]) if x.get("extends")),
        "groups_with_item_extends":sum(1 for x in source.get("groups",[]) if x.get("extends")),
        "values_with_item_extends":sum(1 for x in source.get("values",[]) if x.get("extends")),
        "canonical_rules": len(canonical_rules),
        "automated_rules": len(automated),
        "manual_or_external_rules": len(manual),
        "blocked_rules": len(blocked),
        "combined_rule_files": len(canonical_rules),
        "split_policy_rule_files": len(canonical_rules),
        "split_assessment_files": sum(
            len(x.get("assessments", [])) for x in canonical_rules
        ),
        "bindings": len(bindings),
        "migration_status": {},
    }
    for item in canonical_rules:
        status = item["migration"]["status"]
        summary["migration_status"][status] = summary["migration_status"].get(status, 0) + 1

    if applicability_migration and applicability_migration.get("status")=="unsupported":
        blocked.append({
            "kind":"applicability",
            "migration":applicability_migration,
        })
        summary["applicability_blocked"]=True
    else:
        summary["applicability_blocked"]=False
    summary["blocked_rules"]=sum(1 for x in blocked if x.get("rule_id"))

    dump_json(out / "conversion-summary.json", summary)
    dump_json(out / "conversion-blockers.json", blocked)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
