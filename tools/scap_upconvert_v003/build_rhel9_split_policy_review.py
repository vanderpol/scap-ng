#!/usr/bin/env python3
"""Build a non-destructive complete RHEL9 split Benchmark/Rule/Policy/Assessment review.

This is an authoring-layout prototype, NOT a semantic refactor, reference
scanner, or independently packaged executable artifact. Preserve the source
assessment payload and policy selection definitions unchanged.
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
import yaml

def load(path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def dump(path, doc):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=110), encoding="utf-8")

def resolve_source_ref(package_root, source_file, reference, document_kind, expected_id):
    """Resolve explicit relative authoring path inside the source package.

    Logical identity comes from document contents, never from filename.
    Reject absolute/missing/escaping/ambiguous references rather than guessing.
    """
    if not isinstance(reference, str) or not reference or Path(reference).is_absolute():
        raise ValueError(f"Invalid {document_kind} source path: {reference!r}")
    if "\\\\" in reference or "\\x00" in reference:
        raise ValueError(f"Invalid portable source path: {reference!r}")
    root = package_root.resolve()
    target = (source_file.parent / reference).resolve()
    if not target.is_relative_to(root):
        raise ValueError(f"Reference escapes benchmark package: {reference!r}")
    if not target.is_file():
        raise ValueError(f"Missing referenced source file: {target}")
    doc = load(target)
    if not isinstance(doc, dict) or not isinstance(doc.get(document_kind), dict):
        raise ValueError(f"Wrong referenced document type: {target}")
    if doc[document_kind].get("id") != expected_id:
        raise ValueError(f"Referenced {document_kind} identity mismatch: {target}")
    return target


def rule_ids_in_groups(groups):
    ids = []
    def visit(item):
        ids.extend(item.get("rules") or [])
        for child in item.get("groups") or []:
            visit(child)
    for group in groups:
        visit(group)
    return ids

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source",default="research/iterations/003/source/split-rule-assessment/rhel9-full")
    parser.add_argument("--output",default="research/iterations/003/source/split-policy-assessment/rhel9-full")
    parser.add_argument("--report",default="research/iterations/003/evidence/rhel9-split-policy-review.json")
    args=parser.parse_args()
    source=Path(args.source)
    output=Path(args.output)
    if not (source/"benchmark.yaml").is_file():
        raise SystemExit("Missing source benchmark")

    benchmark_doc=load(source/"benchmark.yaml")
    benchmark=benchmark_doc["benchmark"]
    rule_paths=sorted((source/"rules").glob("*.rule.yaml"))
    if not rule_paths:
        raise SystemExit("No source Rules to convert")

    # Work from clean destination so orphan Rules or Assessments cannot survive.
    if output.exists(): shutil.rmtree(output)
    output.mkdir(parents=True)
    shutil.copy2(source/"benchmark.yaml",output/"benchmark.yaml")
    shutil.copy2(source/"applicability.yaml",output/"applicability.yaml")
    shutil.copytree(source/"assessments",output/"assessments")

    source_rule_ids=set()
    policy_ids=set()
    selected_assessments=set()
    validated_source_paths=0
    issues=[]
    variants={"automated":0,"manual_only":0,"both":0,"other":0}
    for path in rule_paths:
        document=load(path)
        rule=document["rule"]
        rid=rule["id"]
        if rid in source_rule_ids:
            raise ValueError(f"Duplicate Rule ID: {rid}")
        source_rule_ids.add(rid)
        checks=rule.pop("checks",None)
        default=rule.pop("default_check",None)
        if not isinstance(checks,dict) or not checks:
            raise ValueError(f"Missing check selector mapping: {rid}")
        if not isinstance(default,str) or default not in checks:
            raise ValueError(f"Unresolved default selector: {rid}: {default!r}")
        if default=="default" and checks.get("default") not in checks.values():
            raise ValueError(f"Missing default implementation: {rid}")
        typed_checks={}
        for selector, target in checks.items():
            if not isinstance(target,str) or not target:
                raise ValueError(f"Invalid check target: {rid} {selector}")
            assessment_file=output/"assessments"/("manual" if target.endswith(".manual") else "automated")/(target+".assessment.yaml")
            # Existing applicability and mixed-mode cases are tracked as review issues
            # rather than silently inventing an implementation.
            if not assessment_file.is_file():
                matches=list((output/"assessments").rglob(target+".assessment.yaml"))
                if len(matches)!=1:
                    raise ValueError(f"Unresolved or ambiguous selector target: {rid}:{selector} -> {target}")
                assessment_file=matches[0]
            assessment=load(assessment_file)["assessment"]
            if assessment["id"]!=target:
                raise ValueError(f"Assessment identity mismatch: {rid}:{selector}")
            selected_assessments.add(target)
            # Input is the old ID-only review source. Output authoring
            # references must be explicit paths relative to Policy.
            explicit="../"+assessment_file.relative_to(output).as_posix()
            typed_checks[selector]={"assessment":explicit}
        variant=("both" if "automated" in checks and "manual" in checks
                 else "automated" if "automated" in checks
                 else "manual_only" if "manual" in checks else "other")
        variants[variant]+=1
        policy_id="policy.rhel9."+rid
        if policy_id in policy_ids:
            raise ValueError(f"Duplicate Policy ID: {policy_id}")
        policy_ids.add(policy_id)
        policy={
            "id": policy_id,
            "version":rule.get("version"),
            "title": rule.get("title"),
            "checks":typed_checks,
            "default_check":default,
        }
        policy_file=output/"policies"/(rid+".policy.yaml")
        rule_file=output/"rules"/path.name
        dump(policy_file,{"policy":policy})
        rule["policy"] = "../policies/"+rid+".policy.yaml"
        dump(rule_file,document)
        resolve_source_ref(output,rule_file,rule["policy"],"policy",policy_id)
        validated_source_paths+=1
        for selector, ref in typed_checks.items():
            resolve_source_ref(output,policy_file,ref["assessment"],
                               "assessment",checks[selector])
            validated_source_paths+=1

    if len(source_rule_ids)!=445:
        raise ValueError(f"Expected 445 source Rules; observed {len(source_rule_ids)}")
    # Groups and Benchmark.rules may redundantly express membership; both must
    # resolve to the exact same Rule identities.
    group_ids=rule_ids_in_groups(benchmark.get("groups") or [])
    if len(group_ids)!=len(set(group_ids)):
        issues.append({"code":"DUPLICATE_GROUP_MEMBERSHIP","count":len(group_ids)-len(set(group_ids))})
    if set(group_ids)!=source_rule_ids:
        raise ValueError(f"Group membership mismatch: missing={sorted(source_rule_ids-set(group_ids))}; extras={sorted(set(group_ids)-source_rule_ids)}")
    benchmark_ids=benchmark.get("rules")
    if benchmark_ids is not None:
        if set(benchmark_ids)!=source_rule_ids:
            raise ValueError("Benchmark Rule ID membership mismatch")

    app=load(output/"applicability.yaml")
    for condition in app.get("applicability") or []:
        f=output/condition["assessment"]
        if not f.is_file():
            raise ValueError(f"Unresolved applicability Assessment: {f}")

    for profile in benchmark.get("profiles") or []:
        unknown=set(profile.get("disabled_rules") or [])-source_rule_ids
        if unknown:
            raise ValueError(f"Profile {profile.get('id')} references unknown Rules: {sorted(unknown)}")

    output_report={
        "status":"review_candidate_not_execution_equivalent",
        "source":str(source),
        "output":str(output),
        "rule_count":len(source_rule_ids),
        "policy_count":len(policy_ids),
        "validated_explicit_paths":validated_source_paths,
        "assessment_file_count":len(list((output/"assessments").rglob("*.assessment.yaml"))),
        "referenced_check_assessment_count":len(selected_assessments),
        "groups_membership_unique":len(set(group_ids)),
        "profiles":len(benchmark.get("profiles") or []),
        "check_variants":variants,
        "issues":issues,
        "limits":[
            "Policy files are one-per-Rule transitional ownership objects; no unproven cross-platform policy reuse.",
            "Assessments copied byte-for-byte from tested baseline; no independent runtime parity claim.",
            "No compiled split-policy package yet; benchmark/Rule/Policy/Assessment review source only.",
            "All generated Rule-to-Policy and Policy-to-Assessment authoring paths are explicit and resolved.",
        ]
    }
    rp=Path(args.report);rp.parent.mkdir(parents=True,exist_ok=True)
    rp.write_text(json.dumps(output_report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(output_report,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
