#!/usr/bin/env python3
"""Build one compact modernization scorecard for human benchmark review."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def pct_reduction(before,after):
    return round(100.0*(before-after)/before,2) if before else 0.0


def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--modernization-report",type=Path,required=True)
    p.add_argument("--residual-report",type=Path,required=True)
    p.add_argument("--label",required=True)
    p.add_argument("--source-revision",required=True)
    p.add_argument("--workflow-url",required=True)
    p.add_argument("--output-json",type=Path,required=True)
    p.add_argument("--output-markdown",type=Path,required=True)
    args=p.parse_args()

    m=json.loads(args.modernization_report.read_text(encoding="utf-8"))
    r=json.loads(args.residual_report.read_text(encoding="utf-8"))
    s=m["summary"]
    rule_rows=[
        row for row in m.get("assessments",[])
        if row.get("kind")=="rule"
    ]
    eval_counts={
        "single_test_explicit_root":sum(
            bool((row.get("evaluate") or {}).get("single_test_explicit_root"))
            for row in rule_rows
        ),
        "multi_test":0,
        "nested_depth_gt_2":sum(
            int((row.get("evaluate") or {}).get("depth",0))>2
            for row in rule_rows
        ),
        "repeated_test_ref_rules":sum(
            int((row.get("evaluate") or {}).get("repeated_test_refs",0))>0
            for row in rule_rows
        ),
    }
    # The per-assessment row does not persist test_count, so use residual
    # reasons to count real multi-Test composition.
    eval_counts["multi_test"]=sum(
        "multiple_tests_evaluate" in (row.get("residual_reasons") or [])
        for row in rule_rows
    )

    baseline={
        "objects":s.get("baseline_objects",0),
        "states":s.get("baseline_states",0),
        "variables":s.get("baseline_variables",0),
        "named_references":s.get("baseline_named_component_cross_references",0),
        "lines":s.get("baseline_normalized_lines",0),
        "bytes":s.get("baseline_normalized_bytes",0),
    }
    candidate={
        "objects":s.get("modernized_objects",0),
        "states":s.get("modernized_states",0),
        "variables":s.get("modernized_variables",0),
        "named_references":s.get("modernized_named_component_cross_references",0),
        "lines":s.get("modernized_normalized_lines",0),
        "bytes":s.get("modernized_normalized_bytes",0),
    }
    reductions={
        key:pct_reduction(baseline[key],candidate[key])
        for key in baseline
    }

    score={
        "format":"scap-ng-modernization-scorecard-0.1",
        "status":"research_review_evidence",
        "benchmark":args.label,
        "source_artifact":m.get("source_artifact"),
        "source_revision":args.source_revision,
        "workflow_url":args.workflow_url,
        "proof_status":{
            "modernization_report":m.get("status"),
            "residual_report":r.get("status"),
            "exact_roundtrip_required":True,
        },
        "assessment_counts":{
            "automated":s.get("automated_assessments",0),
            "rules":s.get("rule_assessments",0),
            "applicability":s.get("applicability_assessments",0),
        },
        "baseline":baseline,
        "candidate":candidate,
        "reduction_percent":reductions,
        "locality":{
            "binding_variables_localized":s.get("private_binding_variables_localized",0),
            "external_variables_localized":s.get("private_external_variables_localized",0),
            "constant_variables_localized":s.get("private_constant_variables_localized",0),
            "leaf_derived_variables_localized":s.get("private_local_variables_localized",0),
        },
        "foreach":{
            "rewrites":s.get("foreach_rewrites_applied",0),
            "rewritten_assessments":s.get("foreach_rewritten_assessments",0),
            "review_required_variables":s.get("foreach_review_required_variables",0),
            "review_reason_counts":s.get("foreach_review_reason_counts",{}),
        },
        "observations":{
            "artifacts":s.get("observation_artifacts",0),
            "consumer_assessments":s.get("observation_consumer_assessments",0),
            "consumer_counts":s.get("observation_consumer_counts",{}),
            "export_references":s.get("observation_export_references",0),
            "object_occurrences_factored":s.get("observation_object_occurrences_factored",0),
            "variable_occurrences_factored":s.get("observation_variable_occurrences_factored",0),
        },
        "evaluate":eval_counts,
        "rule_classifications":(
            s.get("classification_counts_by_kind",{}).get("rule",{})
        ),
        "rule_residual_reasons":(
            s.get("meaningfully_complex_residual_reason_counts_by_kind",{})
            .get("rule",{})
        ),
        "post_modernization_patterns":{
            "complex_rules":r.get("complex_rules",0),
            "set_filter_rules":r.get("set_filter_rules",0),
            "derived_variable_rules":r.get("derived_variable_rules",0),
            "set_filter_and_derived_variable_rules":r.get(
                "set_filter_and_derived_variable_rules",0
            ),
            "set_operator_counts":r.get("set_operator_counts",{}),
            "filter_action_counts":r.get("filter_action_counts",{}),
            "derived_expression_kind_counts":r.get(
                "derived_expression_kind_counts",{}
            ),
        },
    }

    args.output_json.parent.mkdir(parents=True,exist_ok=True)
    args.output_json.write_text(
        json.dumps(score,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )

    cls=score["rule_classifications"]
    lines=[
        f"# {args.label} modernization scorecard",
        "",
        "**Review evidence — not a quality score.**",
        "",
        f"- Source artifact: `{score['source_artifact']}`",
        f"- Source revision: `{args.source_revision}`",
        f"- Workflow: {args.workflow_url}",
        f"- Rule Assessments: **{score['assessment_counts']['rules']}**",
        "",
        "## Structural modernization",
        "",
        "| Measure | Faithful | Candidate | Reduction |",
        "| --- | ---: | ---: | ---: |",
    ]
    labels={
        "objects":"Top-level Objects",
        "states":"Top-level States",
        "variables":"Named Variables",
        "named_references":"Named component references",
        "lines":"Normalized lines",
        "bytes":"Normalized bytes",
    }
    for key in labels:
        lines.append(
            f"| {labels[key]} | {baseline[key]} | {candidate[key]} | "
            f"{reductions[key]}% |"
        )
    lines += [
        "",
        "## Applied modernization",
        "",
        f"- localized external/constant bindings: **{score['locality']['binding_variables_localized']}** "
        f"(external {score['locality']['external_variables_localized']}, "
        f"constant {score['locality']['constant_variables_localized']})",
        f"- localized leaf derived Variables: **{score['locality']['leaf_derived_variables_localized']}**",
        f"- bounded foreach rewrites: **{score['foreach']['rewrites']}**; "
        f"review-required Variables: **{score['foreach']['review_required_variables']}**",
        f"- Observation artifacts: **{score['observations']['artifacts']}**; "
        f"consumers: **{score['observations']['consumer_assessments']}**; "
        f"export refs: **{score['observations']['export_references']}**",
        "",
        "## Rule outcome",
        "",
        f"- local/simple: **{cls.get('local_simple',0)}**",
        f"- bounded dataflow: **{cls.get('bounded_dataflow',0)}**",
        f"- Observation consumer: **{cls.get('shared_observation_consumer',0)}**",
        f"- meaningfully complex: **{cls.get('meaningfully_complex',0)}**",
        "",
        "## Composition and residual semantics",
        "",
        f"- single-Test explicit evaluate roots: **{eval_counts['single_test_explicit_root']}**",
        f"- real multi-Test composition: **{eval_counts['multi_test']}**",
        f"- evaluate depth > 2: **{eval_counts['nested_depth_gt_2']}**",
        f"- repeated Test-reference Rules: **{eval_counts['repeated_test_ref_rules']}**",
        f"- Set/Filter residual Rules: **{r.get('set_filter_rules',0)}**",
        f"- derived-Variable residual Rules: **{r.get('derived_variable_rules',0)}**",
        "",
        "### Residual reasons",
        "",
    ]
    for reason,count in sorted(
        score["rule_residual_reasons"].items(),
        key=lambda kv:(-kv[1],kv[0]),
    ):
        lines.append(f"- {reason}: **{count}**")
    lines.append("")
    args.output_markdown.parent.mkdir(parents=True,exist_ok=True)
    args.output_markdown.write_text("\n".join(lines),encoding="utf-8")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
