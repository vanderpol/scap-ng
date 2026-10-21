#!/usr/bin/env python3
"""#237 six-STIG source Variable scheduling coverage, NOT execution coverage.

Each schedule preserves original source expression and shared Object closure.
Schedules do not count toward scanner-ready or parity-verified Assessments.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

from research_b_full_corpus_import import read_source,import_corpus
from research_b_variable_schedule import plan_source_variables


def coverage(capsules):
    entries=[]
    seen_assessment_ids=set()
    for capsule_key,cap in sorted(capsules.items()):
        a=cap["source_document"].get("assessment",{})
        if a.get("mode")!="automated" or not a.get("variables"):
            continue
        # Corpus capsule dictionary keys are transport identifiers, not
        # necessarily the publisher's stable Assessment logical identity.
        aid=a.get("id")
        if not isinstance(aid,str) or not aid.strip():
            raise ValueError("Variable Assessment is missing its logical ID")
        if aid in seen_assessment_ids:
            raise ValueError("Duplicate Variable Assessment logical ID: "+aid)
        seen_assessment_ids.add(aid)
        source=cap["source_path"]
        try:
            plan=plan_source_variables(a)
        except (ValueError,KeyError,TypeError) as exc:
            entries.append({
                "assessment_id":aid,"source_path":source,"status":"blocked",
                "reason":str(exc),"source_parity_verified":False,
                "scanner_executable":False})
            continue
        entries.append({
            "assessment_id":aid,"source_path":source,
            "status":"structural_plan_only",
            "source_variables_sha256":plan["source_variables_sha256"],
            "source_shared_objects_sha256":plan["source_shared_objects_sha256"],
            "variable_nodes":len(plan["nodes"]),
            "max_variable_depth":plan["max_variable_depth"],
            "operators":dict(sorted(Counter(n["operator"] for n in plan["nodes"]).items())),
            "shared_object_refs":plan["referenced_shared_object_ids"],
            "source_parity_verified":False,
            "scanner_executable":False,
        })
    counts=Counter(x["status"] for x in entries)
    return {
        "format":"scap-ng-b-six-stream-source-variable-plan-gate/0.1",
        "source_kind":"pinned_converted_0.3_not_raw_SCAP_1.4_XML",
        "source_parity_verified":False,
        "scanner_executable":False,
        "total_automated_assessments_with_variables":len(entries),
        "structurally_planned":counts["structural_plan_only"],
        "blocked":counts["blocked"],
        "assessments":entries,
    }


def markdown(r):
    lines=[
        "# B six-STIG source Variable graph scheduling coverage",
        "",
        "**Converted-0.3 structural planning only. No scanner execution, no original SCAP 1.4 parity.**",
        "",
        f"**Automated Assessments declaring Variables:** {r['total_automated_assessments_with_variables']}",
        f"**Closed topological source plans:** {r['structurally_planned']}",
        f"**Plan failures (source integrity and supported graph shape):** {r['blocked']}",
        "",
        "A structural plan preserves the source expressions and shared-Object",
        "references and ensures dependency closure. It does **not** implement",
        "the source expressions, execute commands, evaluate Rule results,",
        "or increase the six-STIG fixture IR conversion count.",
        "",
        "## Unplanned source Assessments",
        "",
        "| Assessment | Blocker |",
        "| --- | --- |",
    ]
    blockers=[x for x in r["assessments"] if x["status"]=="blocked"]
    for x in blockers[:100]:
        lines.append(f"| {x['assessment_id']} | {x['reason'].replace('|',r'\|')} |")
    if not blockers:lines.append("| None | All reference graphs structurally schedulable |")
    lines.extend([
        "",
        "The [full per-Assessment plan report](variable-plan-coverage.json)",
        "contains source SHA-256 values, declared operators and shared Object references.",
        "The [19-Variable Apache exemplar](apache-variable-plan.json) is separately",
        "published and explicitly marked execution_supported=false.",
        "",
    ])
    return "\n".join(lines)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--authoring-zip",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--markdown",type=Path,required=True)
    args=p.parse_args()
    docs,raw=read_source(args.authoring_zip)
    _,capsules=import_corpus(docs,raw,expected_benchmarks=6)
    result=coverage(capsules)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    args.markdown.parent.mkdir(parents=True,exist_ok=True)
    args.markdown.write_text(markdown(result))
    print(json.dumps({"variable_assessments":result["total_automated_assessments_with_variables"],
                      "planned":result["structurally_planned"],
                      "blocked":result["blocked"]},sort_keys=True))


if __name__=="__main__":
    main()
