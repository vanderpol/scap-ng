#!/usr/bin/env python3
"""Verify equivalence and accounting of a SCAP 1.4 -> SCAP-NG conversion tree."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def canonicalize_ansible_assessment(rendered: dict) -> dict:
    """Recover canonical assessment semantics from the Ansible-inspired view."""
    out={}
    for key in ("id","version","description","semantic_model"):
        if key in rendered:
            out[key]=rendered[key]

    collect={}
    derive={}
    for step in rendered.get("steps",[]) or []:
        register=step.get("register")
        if not register:
            continue
        if "collect" in step:
            collect[register]=step["collect"]
        elif "derive" in step:
            derive[register]=step["derive"]
    if rendered.get("semantic_model")=="scap-ng-generic-assessment-graph-0.1":
        # The Ansible-inspired spelling intentionally omits empty step groups,
        # but the canonical generic graph retains collect/derive as explicit
        # (possibly empty) semantic sections.
        out["collect"]=collect
        out["derive"]=derive
    else:
        if collect:
            out["collect"]=collect
        if derive:
            out["derive"]=derive

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
        if key in rendered:
            out[key]=rendered[key]

    if "assert" in rendered:
        block=rendered["assert"]
        out["assert"]=block.get("that") if isinstance(block,dict) else block

    for key in ("diagnostics","evidence","evaluation","migration"):
        if key in rendered:
            out[key]=rendered[key]
    if "semantic_fingerprint_sha256" in rendered:
        out["semantic_fingerprint_sha256"]=rendered["semantic_fingerprint_sha256"]
    return out


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("conversion_dir",type=Path)
    ap.add_argument("--expected-rules",type=int)
    ap.add_argument("--expected-automated",type=int)
    ap.add_argument("--expected-manual",type=int)
    ap.add_argument("--expected-applicability-definitions",type=int)
    ap.add_argument("--expected-blocked-rules",type=int)
    ap.add_argument("--ansible-inspired-dir",type=Path)
    args=ap.parse_args()

    root=args.conversion_dir
    summary=json.loads((root/"conversion-summary.json").read_text(encoding="utf-8"))
    canonical=json.loads((root/"canonical-benchmark.json").read_text(encoding="utf-8"))

    failures=[]
    if args.expected_rules is not None and summary["source_rules"]!=args.expected_rules:
        failures.append(f'expected {args.expected_rules} rules, got {summary["source_rules"]}')
    if args.expected_automated is not None and summary["automated_rules"]!=args.expected_automated:
        failures.append(
            f'expected {args.expected_automated} automated rules, got {summary["automated_rules"]}'
        )
    if args.expected_manual is not None and summary["manual_or_external_rules"]!=args.expected_manual:
        failures.append(
            f'expected {args.expected_manual} manual rules, got {summary["manual_or_external_rules"]}'
        )
    if (
        args.expected_applicability_definitions is not None
        and summary.get("applicability_definition_count")!=args.expected_applicability_definitions
    ):
        failures.append(
            "expected "
            f"{args.expected_applicability_definitions} applicability definitions, "
            f"got {summary.get('applicability_definition_count')}"
        )
    if summary.get("applicability_blocked"):
        failures.append("applicability conversion is blocked")
    if (
        args.expected_blocked_rules is not None
        and summary.get("blocked_rules")!=args.expected_blocked_rules
    ):
        failures.append(
            f'expected {args.expected_blocked_rules} blocked rules, '
            f'got {summary.get("blocked_rules")}'
        )

    rules=canonical["rules"]
    if len(rules)!=summary["source_rules"]:
        failures.append("canonical rule count differs from summary")

    combined_applicability_path=root/"combined-rule"/"applicability.yaml"
    split_applicability_path=root/"split-policy-assessment-binding"/"applicability.yaml"
    expected_applicability=canonical.get("applicability",{})
    if expected_applicability.get("assessment") is not None:
        if not combined_applicability_path.exists():
            failures.append("combined applicability assessment missing")
        if not split_applicability_path.exists():
            failures.append("split applicability assessment missing")
        if combined_applicability_path.exists() and split_applicability_path.exists():
            combined_applicability=load_yaml(combined_applicability_path)
            split_applicability=load_yaml(split_applicability_path)
            expected_assessment=expected_applicability.get("assessment")
            if combined_applicability.get("assessment")!=expected_assessment:
                failures.append("combined applicability assessment differs from canonical")
            if split_applicability.get("assessment")!=expected_assessment:
                failures.append("split applicability assessment differs from canonical")

    combined_processing=load_yaml(root/"combined-rule"/"processing.yaml")
    split_processing=load_yaml(root/"split-policy-assessment-binding"/"processing.yaml")
    expected_processing=canonical.get("processing_plan")
    if combined_processing.get("processing_plan")!=expected_processing:
        failures.append("combined processing plan differs from canonical")
    if split_processing.get("processing_plan")!=expected_processing:
        failures.append("split processing plan differs from canonical")

    combined_platforms=load_yaml(root/"combined-rule"/"platforms.yaml")
    split_platforms=load_yaml(root/"split-policy-assessment-binding"/"platforms.yaml")
    expected_platform_definitions=canonical.get("platform_definitions",[])
    if combined_platforms.get("platform_definitions")!=expected_platform_definitions:
        failures.append("combined platform definitions differ from canonical")
    if split_platforms.get("platform_definitions")!=expected_platform_definitions:
        failures.append("split platform definitions differ from canonical")

    combined_profiles=load_yaml(root/"combined-rule"/"profiles.yaml")
    split_profiles=load_yaml(root/"split-policy-assessment-binding"/"profiles.yaml")
    for name,doc in (("combined",combined_profiles),("split",split_profiles)):
        if doc.get("profiles")!=canonical.get("profiles",[]):
            failures.append(f"{name} raw profiles differ from canonical")
        if doc.get("resolved_profiles")!=canonical.get("resolved_profiles",[]):
            failures.append(f"{name} resolved profiles differ from canonical")

    combined_benchmark=load_yaml(root/"combined-rule"/"benchmark.yaml")["benchmark"]
    split_benchmark=load_yaml(root/"split-policy-assessment-binding"/"benchmark.yaml")["benchmark"]
    expected_platforms=canonical.get("benchmark",{}).get("platforms",[])
    expected_effective_platforms=canonical.get("benchmark",{}).get("effective_platforms",[])
    if combined_benchmark.get("platforms",[])!=expected_platforms:
        failures.append("combined benchmark platforms differ from canonical")
    if split_benchmark.get("platforms",[])!=expected_platforms:
        failures.append("split benchmark platforms differ from canonical")
    if combined_benchmark.get("effective_platforms",[])!=expected_effective_platforms:
        failures.append("combined benchmark effective platforms differ from canonical")
    if split_benchmark.get("effective_platforms",[])!=expected_effective_platforms:
        failures.append("split benchmark effective platforms differ from canonical")

    combined_groups=load_yaml(root/"combined-rule"/"groups.yaml")
    split_groups=load_yaml(root/"split-policy-assessment-binding"/"groups.yaml")
    if combined_groups.get("groups")!=canonical.get("groups",[]):
        failures.append("combined groups differ from canonical")
    if split_groups.get("groups")!=canonical.get("groups",[]):
        failures.append("split groups differ from canonical")

    bindings_doc=load_yaml(root/"split-policy-assessment-binding"/"automation"/"bindings.yaml")
    bindings={x["rule"]:x for x in bindings_doc.get("bindings",[])}

    ansible_root=args.ansible_inspired_dir
    ansible_bindings={}
    if ansible_root is not None:
        ansible_processing=load_yaml(ansible_root/"processing.yaml")
        if ansible_processing.get("processing_plan")!=expected_processing:
            failures.append("ansible-inspired processing plan differs from canonical")

        ansible_platforms=load_yaml(ansible_root/"platforms.yaml")
        if ansible_platforms.get("platform_definitions")!=expected_platform_definitions:
            failures.append("ansible-inspired platform definitions differ from canonical")
        expected_app_assessment=(canonical.get("applicability") or {}).get("assessment")
        rendered_app=ansible_platforms.get("applicability_assessment")
        if expected_app_assessment is not None:
            if canonicalize_ansible_assessment(rendered_app or {})!=expected_app_assessment:
                failures.append("ansible-inspired applicability differs from canonical")

        ansible_profiles=load_yaml(ansible_root/"profiles.yaml")
        if ansible_profiles.get("profiles")!=canonical.get("profiles",[]):
            failures.append("ansible-inspired raw profiles differ from canonical")
        if ansible_profiles.get("resolved_profiles")!=canonical.get("resolved_profiles",[]):
            failures.append("ansible-inspired resolved profiles differ from canonical")

        ansible_groups=load_yaml(ansible_root/"groups.yaml")
        if ansible_groups.get("groups")!=canonical.get("groups",[]):
            failures.append("ansible-inspired groups differ from canonical")

        ansible_values=load_yaml(ansible_root/"values.yaml")
        if ansible_values.get("values")!=canonical.get("values",[]):
            failures.append("ansible-inspired values differ from canonical")

        ansible_benchmark=load_yaml(ansible_root/"benchmark.yaml")["benchmark"]
        if ansible_benchmark.get("platforms",[])!=expected_platforms:
            failures.append("ansible-inspired benchmark platforms differ from canonical")
        if ansible_benchmark.get("effective_platforms",[])!=expected_effective_platforms:
            failures.append("ansible-inspired benchmark effective platforms differ from canonical")

        ansible_bindings_doc=load_yaml(ansible_root/"automation"/"bindings.yaml")
        ansible_bindings={x["rule"]:x for x in ansible_bindings_doc.get("bindings",[])}

    checked=0
    for entry in rules:
        policy=entry["policy"]
        rid=policy["id"]
        safe="".join(c if c.isalnum() or c in "._-" else "_" for c in rid).strip("_") or "unnamed"

        combined_path=root/"combined-rule"/"rules"/f"{safe}.yaml"
        split_policy_path=root/"split-policy-assessment-binding"/"policy"/"rules"/f"{safe}.yaml"
        if not combined_path.exists():
            failures.append(f"{rid}: missing combined rule")
            continue
        if not split_policy_path.exists():
            failures.append(f"{rid}: missing split policy rule")
            continue

        combined=load_yaml(combined_path)["rule"]
        split_policy=load_yaml(split_policy_path)["rule"]
        migration=entry["migration"]

        combined_policy={
            k:v for k,v in combined.items()
            if k not in {"assessment","migration"}
        }
        split_policy_clean={
            k:v for k,v in split_policy.items()
            if k!="migration"
        }
        if combined_policy!=policy:
            failures.append(f"{rid}: combined policy differs from canonical")
        if split_policy_clean!=policy:
            failures.append(f"{rid}: split policy differs from canonical")

        if ansible_root is not None:
            ansible_policy_path=ansible_root/"policy"/"rules"/f"{safe}.yaml"
            if not ansible_policy_path.exists():
                failures.append(f"{rid}: missing ansible-inspired policy rule")
            else:
                ansible_policy=load_yaml(ansible_policy_path).get("rule")
                if ansible_policy!=policy:
                    failures.append(f"{rid}: ansible-inspired policy differs from canonical")

        if migration["status"]=="unsupported":
            if rid in bindings:
                failures.append(f"{rid}: unsupported rule unexpectedly has binding")
            continue

        binding=bindings.get(rid)
        if not binding:
            failures.append(f"{rid}: missing split assessment binding")
            continue
        aid=binding["assessment"]
        apath=root/"split-policy-assessment-binding"/"automation"/"assessments"/(
            "".join(c if c.isalnum() or c in "._-" else "_" for c in aid).strip("_")+".yaml"
        )
        if not apath.exists():
            failures.append(f"{rid}: missing split assessment file {aid}")
            continue
        split_assessment=load_yaml(apath)["assessment"]
        if combined.get("assessment")!=entry.get("assessment"):
            failures.append(f"{rid}: combined assessment differs from canonical")
        if split_assessment!=entry.get("assessment"):
            failures.append(f"{rid}: split assessment differs from canonical")

        if ansible_root is not None:
            abinding=ansible_bindings.get(rid)
            if not abinding:
                failures.append(f"{rid}: missing ansible-inspired assessment binding")
            else:
                ansible_aid=abinding["assessment"]
                aansible=ansible_root/"automation"/"assessments"/(
                    "".join(c if c.isalnum() or c in "._-" else "_" for c in ansible_aid).strip("_")+".yaml"
                )
                if not aansible.exists():
                    failures.append(f"{rid}: missing ansible-inspired assessment file {ansible_aid}")
                else:
                    rendered=load_yaml(aansible).get("assessment",{})
                    recovered=canonicalize_ansible_assessment(rendered)
                    if recovered!=entry.get("assessment"):
                        failures.append(f"{rid}: ansible-inspired assessment differs from canonical")
        checked+=1

    if len(bindings)!=summary["bindings"]:
        failures.append(
            f'bindings count mismatch: file={len(bindings)} summary={summary["bindings"]}'
        )
    if ansible_root is not None and len(ansible_bindings)!=summary["bindings"]:
        failures.append(
            "ansible-inspired bindings count mismatch: "
            f'file={len(ansible_bindings)} summary={summary["bindings"]}'
        )

    result={
        "status":"PASS" if not failures else "FAIL",
        "rules":len(rules),
        "assessment_equivalence_checked":checked,
        "blocked_rules":summary["blocked_rules"],
        "applicability_definition_count":summary.get("applicability_definition_count",0),
        "applicability_migration_status":summary.get("applicability_migration_status"),
        "migration_status":summary["migration_status"],
        "ansible_inspired_verified":ansible_root is not None,
        "failures":failures[:100],
    }
    print(json.dumps(result,indent=2,sort_keys=True))
    if failures:
        return 1
    return 0


if __name__=="__main__":
    raise SystemExit(main())
