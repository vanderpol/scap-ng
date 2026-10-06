#!/usr/bin/env python3
"""Build a conservative SCAP-NG scoped-iteration migration plan from audit evidence.

This tool never rewrites OVAL. It classifies whether source semantics must be
preserved as value-set dataflow or whether a rule should receive scoped-
iteration review. It intentionally has no "automatic for_each rewrite" outcome
until equivalence proof rules are ratified and executable conformance exists.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path

def classify(row):
    risks=set(row.get("rewrite_risk") or [])
    edges=row.get("dependent_object_edges") or []
    if row.get("intra_variable_multi_field_sources"):
        return {
            "disposition":"review_same_item_projection",
            "automatic_rewrite":False,
            "reason":"multiple fields from the same source Item participate in one Variable expression; OVAL value collection semantics can lose row identity",
        }
    if row.get("correlated_candidates"):
        return {
            "disposition":"review_possible_correlation",
            "automatic_rewrite":False,
            "reason":"source graph reuses values derived from one population in selector/state contexts; lexical correlation must not be inferred",
        }
    if row.get("nested_dependency_paths"):
        return {
            "disposition":"review_nested_value_dataflow",
            "automatic_rewrite":False,
            "reason":"multi-level dependent collection graph is representable as OVAL value-set dataflow; scoped rewrite needs explicit flattening/error equivalence proof",
        }
    if "nontrivial_var_check" in risks:
        return {
            "disposition":"preserve_quantified_value_set",
            "automatic_rewrite":False,
            "reason":"OVAL var_check is behaviorally significant and must be preserved until a proven NG equivalent exists",
        }
    if "variable_function" in risks or "multi_projection" in risks:
        return {
            "disposition":"preserve_variable_expression",
            "automatic_rewrite":False,
            "reason":"OVAL Variable functions/projections operate on value collections and may use Cartesian-product semantics",
        }
    if edges:
        return {
            "disposition":"preserve_dependent_value_set",
            "automatic_rewrite":False,
            "reason":"dependent Object selection is valid value-set dataflow; per-parent iteration would add grouping/correlation semantics not proven in source",
        }
    return {
        "disposition":"no_iteration_signal",
        "automatic_rewrite":False,
        "reason":"no scoped-iteration migration signal detected",
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("oval_audit")
    ap.add_argument("--manual-audit")
    ap.add_argument("--output",required=True)
    args=ap.parse_args()
    oval=json.loads(Path(args.oval_audit).read_text())
    rows=[]
    for row in oval.get("candidates",[]):
        decision=classify(row)
        rows.append({
            "rule_id":row.get("rule_id"),
            "title":row.get("title"),
            **decision,
            "source_signals":{
                "dependent_object_edges":len(row.get("dependent_object_edges") or []),
                "nested_dependency_paths":len(row.get("nested_dependency_paths") or []),
                "same_item_field_sources":len(row.get("intra_variable_multi_field_sources") or []),
                "multi_projection_sources":len(row.get("multi_projection_sources") or []),
                "variable_functions":row.get("variable_functions") or [],
                "rewrite_risk":row.get("rewrite_risk") or [],
            },
        })
    manual=[]
    if args.manual_audit:
        m=json.loads(Path(args.manual_audit).read_text())
        for row in m.get("candidates",[]):
            manual.append({
                "rule_id":row.get("rule_id"),
                "title":row.get("title"),
                "disposition":"manual_native_automation_candidate",
                "automatic_rewrite":False,
                "reason":"manual policy/check text may require per-parent correlation; native automation is a new implementation and cannot be labeled lossless conversion",
                "signals":row.get("signals") or [],
            })
    summary={}
    for row in rows+manual:
        summary[row["disposition"]]=summary.get(row["disposition"],0)+1
    report={
        "label":oval.get("label"),
        "policy":{
            "automatic_for_each_rewrites_enabled":False,
            "principle":"Preserve source value-set semantics unless scoped iteration equivalence is mechanically proven.",
        },
        "summary":summary,
        "oval_candidates":rows,
        "manual_candidates":manual,
    }
    out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({"label":report["label"],"summary":summary},indent=2))

if __name__=="__main__":
    main()
