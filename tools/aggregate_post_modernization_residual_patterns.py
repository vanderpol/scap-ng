#!/usr/bin/env python3
"""Aggregate post-modernization residual pattern reports across NIWC Current."""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

from aggregate_full_modernization_census import EXPECTED_BLOCKERS


def add_counts(target:Counter, value:dict):
    for k,v in (value or {}).items():
        target[k]+=int(v or 0)


def pattern_key(signature:dict)->str:
    return json.dumps(signature,sort_keys=True,separators=(",",":"))


def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("root",type=Path)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--markdown",type=Path,required=True)
    p.add_argument("--niwc-revision",required=True)
    args=p.parse_args()

    statuses=[
        json.loads(x.read_text(encoding="utf-8"))
        for x in sorted(args.root.rglob("status/*.json"))
    ]
    reports=[
        json.loads(x.read_text(encoding="utf-8"))
        for x in sorted(args.root.rglob("reports/*.json"))
    ]
    if len(statuses)!=65:
        raise SystemExit(f"expected 65 package statuses, found {len(statuses)}")

    generated=[x for x in statuses if x.get("status")=="generated"]
    blocked=[x for x in statuses if x.get("status")!="generated"]
    unexpected=[]
    for row in blocked:
        marker=EXPECTED_BLOCKERS.get(row["artifact"])
        if row.get("status")!="blocked" or not marker or marker not in row.get("log_tail",""):
            unexpected.append(row)
    if len(generated)!=61 or len(blocked)!=4 or unexpected:
        raise SystemExit(
            f"expected 61 generated + 4 known blockers; generated={len(generated)} "
            f"blocked={len(blocked)} unexpected={len(unexpected)}"
        )

    by_artifact={r.get("source_artifact"):r for r in reports}
    missing=[x["artifact"] for x in generated if x["artifact"] not in by_artifact]
    if len(reports)!=61 or missing:
        raise SystemExit(f"expected 61 reports; found {len(reports)} missing={missing}")

    totals=Counter()
    reasons=Counter()
    set_ops=Counter()
    filter_actions=Counter()
    derived_kinds=Counter()
    derived_funcs=Counter()
    set_patterns=defaultdict(lambda:{"count":0,"signature":None,"examples":[],"packages":Counter()})
    var_patterns=defaultdict(lambda:{"count":0,"signature":None,"examples":[],"packages":Counter()})
    joint_patterns=defaultdict(lambda:{"count":0,"signature":None,"examples":[],"packages":Counter()})
    package_rows=[]

    def merge_patterns(dest, rows, label):
        for row in rows or []:
            key=pattern_key(row["signature"])
            bucket=dest[key]
            bucket["count"]+=int(row["count"])
            bucket["signature"]=row["signature"]
            bucket["packages"][label]+=int(row["count"])
            for ex in row.get("examples") or []:
                if len(bucket["examples"])<20:
                    bucket["examples"].append(ex)

    for r in reports:
        label=r["label"]
        for k in (
            "complex_rules","set_filter_rules","derived_variable_rules",
            "set_filter_and_derived_variable_rules",
        ):
            totals[k]+=int(r.get(k,0) or 0)
        add_counts(reasons,r.get("residual_reason_counts"))
        add_counts(set_ops,r.get("set_operator_counts"))
        add_counts(filter_actions,r.get("filter_action_counts"))
        add_counts(derived_kinds,r.get("derived_expression_kind_counts"))
        add_counts(derived_funcs,r.get("derived_function_counts"))
        merge_patterns(set_patterns,r.get("set_filter_pattern_counts"),label)
        merge_patterns(var_patterns,r.get("derived_variable_pattern_counts"),label)
        merge_patterns(joint_patterns,r.get("joint_pattern_counts"),label)
        package_rows.append({
            "source_artifact":r.get("source_artifact"),
            "label":label,
            "complex_rules":r["complex_rules"],
            "set_filter_rules":r["set_filter_rules"],
            "derived_variable_rules":r["derived_variable_rules"],
            "set_filter_and_derived_variable_rules":r["set_filter_and_derived_variable_rules"],
            "unique_set_filter_pattern_signatures":r["unique_set_filter_pattern_signatures"],
            "unique_derived_variable_pattern_signatures":r["unique_derived_variable_pattern_signatures"],
        })

    def rank(src):
        rows=[]
        for key,b in src.items():
            rows.append({
                "count":b["count"],
                "percent_of_family":0.0,
                "signature":b["signature"],
                "examples":b["examples"],
                "packages":dict(b["packages"]),
            })
        rows.sort(key=lambda x:(-x["count"],json.dumps(x["signature"],sort_keys=True)))
        denom=sum(x["count"] for x in rows)
        for x in rows:
            x["percent_of_family"]=round(100.0*x["count"]/denom,2) if denom else 0.0
        return rows

    ranked_sets=rank(set_patterns)
    ranked_vars=rank(var_patterns)
    ranked_joint=rank(joint_patterns)
    summary={
        **dict(totals),
        "source_packages":65,
        "generated_packages":61,
        "known_blocked_packages":4,
        "residual_reason_counts":dict(reasons),
        "set_operator_counts":dict(set_ops),
        "filter_action_counts":dict(filter_actions),
        "derived_expression_kind_counts":dict(derived_kinds),
        "derived_function_counts":dict(derived_funcs),
        "unique_set_filter_pattern_signatures":len(ranked_sets),
        "unique_derived_variable_pattern_signatures":len(ranked_vars),
        "unique_joint_pattern_signatures":len(ranked_joint),
    }
    out={
        "format":"scap-ng-post-modernization-residual-patterns-aggregate-0.1",
        "status":"research_only_not_accepted_design",
        "niwc_revision":args.niwc_revision,
        "summary":summary,
        "top_set_filter_patterns":ranked_sets[:50],
        "top_derived_variable_patterns":ranked_vars[:50],
        "top_joint_patterns":ranked_joint[:50],
        "packages":sorted(package_rows,key=lambda x:x["source_artifact"] or ""),
        "known_blockers":blocked,
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")

    lines=[
        "# Post-modernization residual pattern census",
        "",
        "**Research only; no new syntax accepted.**",
        "",
        f"- complex Rule Assessments analyzed: **{summary['complex_rules']}**",
        f"- Set/Filter Rules: **{summary['set_filter_rules']}**",
        f"- derived-Variable Rules: **{summary['derived_variable_rules']}**",
        f"- overlap: **{summary['set_filter_and_derived_variable_rules']}**",
        f"- unique Set/Filter signatures: **{summary['unique_set_filter_pattern_signatures']}**",
        f"- unique derived-Variable signatures: **{summary['unique_derived_variable_pattern_signatures']}**",
        "",
        "## Top Set/Filter families",
        "",
    ]
    for row in ranked_sets[:15]:
        sig=row["signature"]["set_filter"]
        lines.append(
            f"- **{row['count']}** ({row['percent_of_family']}%): "
            f"operators={sig.get('operators')} filters={sig.get('filter_count')} "
            f"actions={sig.get('filter_actions')} operands={sig.get('operand_kinds')}; "
            f"examples={', '.join(row['examples'][:5])}"
        )
    lines += ["","## Top derived-Variable families",""]
    for row in ranked_vars[:15]:
        kinds=[
            v.get("expression_kind") for v in row["signature"].get("variables",[])
        ]
        lines.append(
            f"- **{row['count']}** ({row['percent_of_family']}%): "
            f"variables={kinds}; set/filter={row['signature'].get('has_set_filter')}; "
            f"examples={', '.join(row['examples'][:5])}"
        )
    args.markdown.write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps(summary,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
