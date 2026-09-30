#!/usr/bin/env python3
"""Compare native compact profile selections to pinned SCAP 1.4 XCCDF.

This check handles XCCDF Group/Rule selected inheritance, Rule and Group
profile select actions, cluster-id targeting and Profile extends chains.
It fails closed on unknown/ambiguous targets and duplicate identities. It
does NOT claim requires/conflicts, applicability, or runtime result parity.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from lxml import etree
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import scap14_rule_splitter as split
import scap14_benchmark_ir as ir


def native_rule_id(source_id):
    match = re.search(r"_rule_(SV-\d+)r\d+_rule$", source_id or "")
    if not match:
        raise ValueError(f"Unrecognized XCCDF Rule identity: {source_id}")
    return match.group(1)


def native_profile_id(source_id):
    if not source_id:
        raise ValueError("XCCDF Profile has no id")
    return source_id.rsplit("_profile_", 1)[-1]


def extract_selection(source_zip: Path):
    _member, _bytes, ds = split.find_datastream(source_zip)
    components, _ = split.embedded_components(ds)
    xccdf = [root for root in components.values()
             if split.component_kind(root) == "xccdf"]
    if len(xccdf) != 1:
        raise ValueError(f"Expected one XCCDF Benchmark, found {len(xccdf)}")
    root = xccdf[0]
    rules = []
    groups = []
    group_ancestors = {}
    def walk(parent, ancestors):
        for child in parent:
            if not isinstance(child.tag, str):
                continue
            name = split.local(child.tag)
            if name == "Group":
                id_ = child.get("id")
                if not id_:
                    raise ValueError("Unnamed XCCDF Group")
                groups.append({"id": id_,
                               "selected": ir.boolean_attribute(child.get("selected"), True),
                               "cluster_id": child.get("cluster-id")})
                walk(child, ancestors + [id_])
            elif name == "Rule":
                rid = native_rule_id(child.get("id"))
                rules.append({"id": child.get("id"), "native": rid,
                              "selected": ir.boolean_attribute(child.get("selected"), True),
                              "cluster_id": child.get("cluster-id")})
                group_ancestors[rid] = list(ancestors)
    walk(root, [])
    if len(rules) != len({x["id"] for x in rules}) or len(rules) != len({x["native"] for x in rules}):
        raise ValueError("Duplicate source/native Rule identities")
    if len(groups) != len({g["id"] for g in groups}):
        raise ValueError("Duplicate Group identities")
    profiles = [ir.profile_semantics(e) for e in root.iter()
                if isinstance(e.tag, str) and split.local(e.tag) == "Profile"]
    if len(profiles) != len({p["id"] for p in profiles}):
        raise ValueError("Duplicate Profile identities")
    resolved = ir.resolve_profiles(profiles, rules, groups, [])
    return rules, groups, group_ancestors, resolved


def expected_selections(rules, groups, ancestors, profiles):
    rule_defaults = {r["id"]: r["selected"] for r in rules}
    group_defaults = {g["id"]: g["selected"] for g in groups}

    def effective(rule_values, group_values):
        return {r["native"]: bool(rule_values[r["id"]])
                and all(group_values[g] for g in ancestors[r["native"]])
                for r in rules}

    baseline = effective(rule_defaults, group_defaults)
    results = {}
    for profile in profiles:
        actions = profile.get("effective_actions", [])
        selection = dict(rule_defaults)
        group_selection = dict(group_defaults)
        problems = []
        for action in actions:
            if action["kind"] != "select":
                continue
            if action.get("target_resolution") != "resolved":
                problems.append({"code": "UNRESOLVED_SELECT",
                                 "profile": profile["id"], "action": action})
                continue
            selected = action["attributes"].get("selected")
            if selected not in ("true", "false", "1", "0"):
                problems.append({"code": "INVALID_SELECTED", "action": action})
                continue
            enabled = selected in ("true", "1")
            targets = action.get("targets") or []
            if not targets:
                problems.append({"code": "EMPTY_SELECT_TARGET", "action": action})
            for target in targets:
                kind = target["kind"]
                if kind == "rule":
                    selection[target["id"]] = enabled
                elif kind == "group":
                    group_selection[target["id"]] = enabled
                else:
                    problems.append({"code": "WRONG_TARGET_TYPE", "action": action})
        results[native_profile_id(profile["id"])] = {
            "enabled": effective(selection, group_selection),
            "problems": problems,
            "source_profile_id": profile["id"],
            "inheritance_chain": profile.get("inheritance_chain"),
        }
    return baseline, results


def audit(source_zip: Path, native_benchmark: Path):
    rules, groups, ancestry, profiles = extract_selection(source_zip)
    benchmark = yaml.safe_load(native_benchmark.read_text(encoding="utf-8"))["benchmark"]
    native_rules = benchmark.get("rules") or []
    source_rule_ids = {r["native"] for r in rules}
    native_profile_rows = benchmark.get("profiles") or []
    native_profiles = {p["id"]: p for p in native_profile_rows}
    baseline, resolved = expected_selections(rules, groups, ancestry, profiles)
    issues = []
    if set(native_rules) != source_rule_ids or len(native_rules) != len(source_rule_ids):
        issues.append({"code": "RULE_SET_MISMATCH",
                       "missing": sorted(source_rule_ids-set(native_rules)),
                       "extra": sorted(set(native_rules)-source_rule_ids)})
    if set(native_profiles) != set(resolved) or len(native_profile_rows) != len(native_profiles):
        issues.append({"code": "PROFILE_SET_MISMATCH",
                       "missing": sorted(set(resolved)-set(native_profiles)),
                       "extra": sorted(set(native_profiles)-set(resolved))})
    # The current renderer implies baseline Rule selected=true unless
    # benchmark explicitly supplies baseline/default selection metadata.
    native_default = benchmark.get("default_selection")
    if native_default is None:
        native_baseline = {rid: True for rid in source_rule_ids}
    elif native_default is True:
        native_baseline = {rid: True for rid in source_rule_ids}
    elif native_default is False:
        native_baseline = {rid: False for rid in source_rule_ids}
    else:
        issues.append({"code": "UNSUPPORTED_NATIVE_DEFAULT_SELECTION", "value": native_default})
        native_baseline = {rid: True for rid in source_rule_ids}
    for rid in sorted(source_rule_ids):
        if native_baseline[rid] != baseline[rid]:
            issues.append({"code": "BASELINE_SELECTED_MISMATCH", "rule": rid,
                           "xccdf": baseline[rid], "native": native_baseline[rid]})
    comparison = []
    for pid in sorted(set(native_profiles)&set(resolved)):
        row = native_profiles[pid]
        unknown = (set(row.get("disabled_rules") or []) |
                   set(row.get("enabled_rules") or [])) - source_rule_ids
        for rid in sorted(unknown):
            issues.append({"code": "UNKNOWN_PROFILE_RULE", "profile": pid, "rule": rid})
        enabled = set(row.get("enabled_rules") or [])
        disabled = set(row.get("disabled_rules") or [])
        if enabled & disabled:
            issues.append({"code": "CONFLICTING_PROFILE_OVERRIDE", "profile": pid,
                           "rules": sorted(enabled & disabled)})
        expected = resolved[pid]
        issues.extend(expected["problems"])
        diff = []
        for rid in sorted(source_rule_ids):
            observed = True if rid in enabled else False if rid in disabled else native_baseline[rid]
            if observed != expected["enabled"][rid]:
                diff.append({"rule": rid, "xccdf": expected["enabled"][rid],
                             "native": observed})
        if diff:
            issues.append({"code": "PROFILE_SELECTION_MISMATCH",
                           "profile": pid, "count": len(diff), "examples": diff[:20]})
        comparison.append({"profile": pid, "source_profile": expected["source_profile_id"],
                           "mismatch_count": len(diff), "source_enabled":
                               sum(expected["enabled"].values())})
    return {
        "source_zip": str(source_zip), "native_benchmark": str(native_benchmark),
        "source_rules": len(rules), "source_groups": len(groups),
        "source_profiles": len(profiles), "native_rules": len(native_rules),
        "native_profiles": len(native_profile_rows),
        "baseline_disabled_source": sum(not value for value in baseline.values()),
        "profile_comparison": comparison, "issues": issues,
        "limitations": [
            "selection parity only: requires/conflicts, tailoring parameters, "
            "complex checks and actual evaluator behavior are not covered."
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    report = audit(args.source, args.native)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, sort_keys=True)+"\n",
                           encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "issues"}, indent=2))
    print("selection_issues:", len(report["issues"]))
    if report["issues"]:
        print(json.dumps(report["issues"][:20], indent=2))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
