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
        "comment": obj.get("comment"),
        "query": copy.deepcopy(obj.get("children", [])),
    }


def predicate_node(state: dict) -> dict:
    return {
        "source_state_id": state.get("id"),
        "source_type": state.get("type"),
        "source_namespace": state.get("namespace"),
        "operator": state.get("operator", "AND"),
        "entities": copy.deepcopy(state.get("entities", [])),
        "comment": state.get("comment"),
    }


def variable_node(variable: dict, ir: dict) -> dict:
    vid = variable.get("id")
    resolution = ir.get("variable_resolution", {}).get(vid)
    plan = ir.get("variable_evaluation_plans", {}).get(vid)
    return {
        "source_variable_id": vid,
        "source_type": variable.get("type"),
        "datatype": variable.get("datatype"),
        "comment": variable.get("comment"),
        "semantic_ast": copy.deepcopy(variable.get("semantic_ast")),
        "resolution": copy.deepcopy(resolution),
        "evaluation_plan": copy.deepcopy(plan),
    }


def test_node(test: dict) -> dict:
    return {
        "source_test_id": test.get("id"),
        "source_type": test.get("type"),
        "source_namespace": test.get("namespace"),
        "comment": test.get("comment"),
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


def manual_assessment(rule: dict) -> tuple[dict, dict]:
    checks = copy.deepcopy(rule.get("checks", []))
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
                "The source check reference is preserved. Dedicated OCIL "
                "questionnaire lowering is a separate conversion layer."
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


def check_selection_plan(rule: dict, assessment: dict | None) -> tuple[dict | None, dict | None]:
    """Lower XCCDF check-selector candidates without silently collapsing alternatives.

    The current generic converter can bind one effective assessment implementation
    for a Rule. Multiple distinct XCCDF selector alternatives require separate
    assessment lowering and are therefore a hard migration blocker until that
    mapping exists.
    """
    checks = copy.deepcopy(rule.get("checks", []))
    if not checks:
        return None, None

    selector_rows = []
    seen = set()
    for check in checks:
        source_selector = check.get("selector")
        selector = normalized_check_selector(source_selector)
        if selector in seen:
            continue
        seen.add(selector)
        selector_rows.append({
            "selector": selector,
            "source_selector": source_selector,
        })

    if len(selector_rows) > 1:
        return None, {
            "status": "unsupported",
            "reason": "selectable_check_alternatives_not_lowered",
            "selectors": selector_rows,
            "message": (
                "The source Rule exposes multiple XCCDF check selectors. "
                "The converter SHALL lower each selector to a distinct SCAP-NG "
                "check alternative before conversion may succeed."
            ),
        }

    if assessment is None:
        return None, {
            "status": "unsupported",
            "reason": "check_selector_without_assessment",
            "selectors": selector_rows,
            "message": "The source check selector cannot be bound to an Assessment.",
        }

    row = selector_rows[0]
    return {
        "checks": [{
            "selector": row["selector"],
            "source_selector": row["source_selector"],
            "assessment": assessment.get("id"),
            "assessment_version": assessment.get("version", 1),
        }],
        "default_check": row["selector"],
    }, None


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

        if assessment_source.get("kind") == "oval_semantic_ir":
            assessment, migration = compile_oval_assessment(
                rule, assessment_source["ir"], catalog
            )
        else:
            assessment, migration = manual_assessment(rule)

        selection, selection_error = check_selection_plan(rule, assessment)
        if selection_error is not None and migration.get("status") != "unsupported":
            migration = {
                **selection_error,
                "source": "SCAP 1.4 XCCDF check selection",
                "source_rule": rule.get("id"),
            }
            assessment = None
        elif selection is not None:
            policy = {**policy, **selection}

        canonical = {
            "policy": policy,
            "assessment": assessment,
            "migration": migration,
            "source_split_diagnostic": copy.deepcopy(rule.get("split_diagnostic")),
        }
        canonical["semantic_fingerprint_sha256"] = canonical_digest({
            "policy": policy,
            "assessment": assessment,
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

        if assessment_source.get("kind") == "oval_semantic_ir":
            automated.append(rule["id"])
        else:
            manual.append(rule["id"])

        combined_doc = {
            "scap_ng": SPEC,
            "prototype": True,
            "model": "combined-rule",
            "rule": {
                **policy,
                "assessment": assessment,
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
            "assessment": aid,
            "assessment_version": assessment.get("version", 1),
            "migration_status": migration.get("status"),
        }
        if policy.get("default_check") is not None:
            binding["check_selector"] = policy["default_check"]
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
        "split_assessment_files": len(bindings),
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
