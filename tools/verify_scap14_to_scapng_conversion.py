#!/usr/bin/env python3
"""Verify equivalence and accounting of a SCAP 1.4 -> SCAP-NG conversion tree."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("conversion_dir",type=Path)
    ap.add_argument("--expected-rules",type=int)
    ap.add_argument("--expected-automated",type=int)
    ap.add_argument("--expected-manual",type=int)
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

    rules=canonical["rules"]
    if len(rules)!=summary["source_rules"]:
        failures.append("canonical rule count differs from summary")

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
    if combined_benchmark.get("platforms",[])!=expected_platforms:
        failures.append("combined benchmark platforms differ from canonical")
    if split_benchmark.get("platforms",[])!=expected_platforms:
        failures.append("split benchmark platforms differ from canonical")

    combined_groups=load_yaml(root/"combined-rule"/"groups.yaml")
    split_groups=load_yaml(root/"split-policy-assessment-binding"/"groups.yaml")
    if combined_groups.get("groups")!=canonical.get("groups",[]):
        failures.append("combined groups differ from canonical")
    if split_groups.get("groups")!=canonical.get("groups",[]):
        failures.append("split groups differ from canonical")

    bindings_doc=load_yaml(root/"split-policy-assessment-binding"/"automation"/"bindings.yaml")
    bindings={x["rule"]:x for x in bindings_doc.get("bindings",[])}

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
        checked+=1

    if len(bindings)!=summary["bindings"]:
        failures.append(
            f'bindings count mismatch: file={len(bindings)} summary={summary["bindings"]}'
        )

    result={
        "status":"PASS" if not failures else "FAIL",
        "rules":len(rules),
        "assessment_equivalence_checked":checked,
        "blocked_rules":summary["blocked_rules"],
        "migration_status":summary["migration_status"],
        "failures":failures[:100],
    }
    print(json.dumps(result,indent=2,sort_keys=True))
    if failures:
        return 1
    return 0


if __name__=="__main__":
    raise SystemExit(main())
