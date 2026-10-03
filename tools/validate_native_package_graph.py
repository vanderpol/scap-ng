#!/usr/bin/env python3
"""Validate cross-document graph semantics for native SCAP-NG benchmark packages, including corpus-level shared Assessment references."""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
import yaml


def load_yaml(path: Path):
    value=yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value,dict) or len(value)!=1:
        raise ValueError(f"{path}: expected exactly one top-level native document")
    return value


def build_document_index(reference_root: Path):
    """Load the corpus once so multi-package validation does not repeatedly parse every YAML file."""
    reference_root=reference_root.resolve()
    documents={}
    for path in sorted(reference_root.rglob("*.yaml")):
        doc=load_yaml(path)
        kind=next(iter(doc))
        payload=doc[kind]
        documents[path.resolve()]=(kind,payload)
    return documents


def validate_package(root: Path, reference_root: Path | None = None, documents=None):
    # A normalized corpus MAY hoist exact duplicate Assessments into a corpus-level
    # shared/ tree. Keep package membership local, but resolve document references
    # against the containing corpus root so those shared Assessments remain legal.
    root = root.resolve()
    reference_root = (reference_root or root).resolve()
    if documents is None:
        documents=build_document_index(reference_root)

    diagnostics=[]
    identities={}
    for resolved,(kind,payload) in documents.items():
        # Package-local identities determine Benchmark Rule membership. Shared
        # corpus documents are available for reference resolution but SHALL NOT
        # pollute the package's local identity namespace.
        try:
            rel=resolved.relative_to(root)
        except ValueError:
            continue
        identity=payload.get("id") if isinstance(payload,dict) else None
        if identity:
            if identity in identities:
                diagnostics.append({"code":"duplicate_identity","id":identity,"paths":[identities[identity],rel.as_posix()]})
            else:
                identities[identity]=rel.as_posix()

    bench_path=(root/"benchmark.yaml").resolve()
    if bench_path not in documents or documents[bench_path][0]!="benchmark":
        return [{"code":"benchmark_missing","message":"benchmark.yaml is missing or wrong document type"}]
    benchmark=documents[bench_path][1]

    def owner_display(owner: Path):
        try:
            return owner.relative_to(root).as_posix()
        except ValueError:
            return owner.relative_to(reference_root).as_posix()

    def resolve(owner: Path, ref, expected_kind):
        if not isinstance(ref,str) or not ref:
            diagnostics.append({"code":"reference_invalid","owner":owner_display(owner),"reference":ref,"expected_kind":expected_kind})
            return None
        target=(owner.parent/ref).resolve()
        try:
            target.relative_to(reference_root)
        except ValueError:
            diagnostics.append({"code":"reference_escape","owner":owner_display(owner),"reference":ref})
            return None
        found=documents.get(target)
        if found is None:
            diagnostics.append({"code":"reference_missing","owner":owner_display(owner),"reference":ref,"expected_kind":expected_kind})
            return None
        kind,payload=found
        if kind!=expected_kind:
            diagnostics.append({"code":"reference_wrong_type","owner":owner_display(owner),"reference":ref,"expected_kind":expected_kind,"actual_kind":kind})
            return None
        return payload

    rule_ids=benchmark.get("rules") or []
    if len(rule_ids)!=len(set(rule_ids)):
        diagnostics.append({"code":"benchmark_duplicate_rule","message":"Benchmark rules list contains duplicate IDs"})

    app_ref=benchmark.get("applicability_catalog")
    registry=resolve(bench_path,app_ref,"applicability") if app_ref else None
    conditions=(registry or {}).get("conditions") or {}

    if registry:
        reg_path=(bench_path.parent/app_ref).resolve()
        for cid,binding in conditions.items():
            if not isinstance(binding,dict):
                diagnostics.append({"code":"applicability_binding_invalid","condition":cid})
                continue
            resolve(reg_path,binding.get("assessment"),"assessment")

    for rid in rule_ids:
        rel=identities.get(rid)
        if rel is None:
            diagnostics.append({"code":"benchmark_rule_missing","rule":rid})
            continue
        path=(root/rel).resolve()
        kind,rule=documents[path]
        if kind!="rule":
            diagnostics.append({"code":"benchmark_rule_wrong_type","rule":rid,"actual_kind":kind})
            continue
        choices=rule.get("assessment_choices") or {}
        default=rule.get("default_assessment_choice")
        if default not in choices:
            diagnostics.append({"code":"rule_default_choice_missing","rule":rid,"default":default})
        for selector,choice in choices.items():
            if not isinstance(choice,dict):
                diagnostics.append({"code":"rule_choice_invalid","rule":rid,"selector":selector})
                continue
            resolve(path,choice.get("assessment"),"assessment")
        unresolved=set(rule.get("applicability") or [])-set(conditions)
        if unresolved:
            diagnostics.append({"code":"rule_applicability_missing","rule":rid,"conditions":sorted(unresolved)})
        for key in ("requires","conflicts"):
            unknown=set(rule.get(key) or [])-set(rule_ids)
            if unknown:
                diagnostics.append({"code":f"rule_{key}_missing","rule":rid,"rules":sorted(unknown)})

    platform=((benchmark.get("platform") or {}).get("applicability") or {})
    missing_platform=set(platform.get("conditions") or [])-set(conditions)
    if missing_platform:
        diagnostics.append({"code":"benchmark_applicability_missing","conditions":sorted(missing_platform)})

    grouped=[]
    seen_groups=set()
    def collect(groups):
        for group in groups or []:
            marker=id(group)
            if marker in seen_groups:
                diagnostics.append({"code":"benchmark_group_cycle","message":"Benchmark group nesting contains a cycle"})
                continue
            seen_groups.add(marker)
            grouped.extend(group.get("rules") or [])
            collect(group.get("groups"))
    collect(benchmark.get("groups"))
    if Counter(grouped)!=Counter(rule_ids):
        diagnostics.append({
            "code":"benchmark_group_membership_mismatch",
            "missing":sorted((Counter(rule_ids)-Counter(grouped)).elements()),
            "extra":sorted((Counter(grouped)-Counter(rule_ids)).elements()),
        })
    return diagnostics


def find_packages(root: Path):
    if (root/"benchmark.yaml").exists():
        return [root]
    return sorted({p.parent for p in root.rglob("benchmark.yaml")})


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("corpus_root",type=Path)
    ap.add_argument("--report",type=Path)
    args=ap.parse_args()
    results=[]
    corpus_root=args.corpus_root.resolve()
    documents=build_document_index(corpus_root)
    for package in find_packages(args.corpus_root):
        diagnostics=validate_package(package, reference_root=corpus_root, documents=documents)
        results.append({
            "package":package.relative_to(args.corpus_root).as_posix() or ".",
            "valid":not diagnostics,
            "diagnostics":diagnostics,
        })
    summary={
        "packages_checked":len(results),
        "valid":sum(x["valid"] for x in results),
        "invalid":sum(not x["valid"] for x in results),
        "results":results,
    }
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in summary.items() if k!="results"},indent=2))
    return 1 if summary["invalid"] else 0

if __name__=="__main__":
    raise SystemExit(main())
