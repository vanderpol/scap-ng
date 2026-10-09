#!/usr/bin/env python3
"""Render a complete research-only 0.3 candidate benchmark tree for human review.

This is deliberately separate from the faithful converter and frozen 0.2
Board build. It starts from a fresh faithful converted benchmark and applies
only the exact/proven research modernization stack currently used by the
full-corpus census.

The output is author-review material, not normative schema-valid 0.3 content.
Every structural locality transformation must mechanically re-expand to its
pre-locality input. Deferred post-0.3 features may be measured for reviewer
context but are not applied to the rendered candidate.
"""
from __future__ import annotations

import argparse
import copy
import json
import shutil
from pathlib import Path
from typing import Any

import yaml

from measure_full_modernization_census import (
    build_observation_plan,
    load_assessments,
    promote_to_research_03,
)
from research_inline_private_components import (
    first_difference,
    inline_private,
    reexpand,
)
from research_static_literal_collections import (
    inline_constants,
    reexpand_constants,
)
from scap_upconvert_v003.foreach_modernization import modernize_foreach_v1
from normalize_0_3_review_surface import normalize_tree
from scap_upconvert_v003.embed_predicates import embed_predicates, reexpand_predicates


def dump_yaml(value:Any)->str:
    return yaml.safe_dump(
        value,
        sort_keys=False,
        width=120,
        allow_unicode=True,
    )


def promote_tree_spec_versions(root:Path)->None:
    """Mark ordinary copied SCAP-NG documents as 0.3.0 review candidates."""
    for path in sorted(root.rglob("*.yaml")):
        try:
            doc=yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(doc,dict) or len(doc)!=1:
            continue
        _,payload=next(iter(doc.items()))
        if not isinstance(payload,dict):
            continue
        spec=payload.get("specification")
        if not isinstance(spec,dict):
            continue
        if isinstance(spec.get("id"),str) and spec["id"].startswith("scap-ng."):
            spec["version"]="0.3.0"
            path.write_text(dump_yaml(doc),encoding="utf-8")



def render(source_root:Path,output_root:Path,evidence_dir:Path,label:str)->dict:
    if output_root.exists():
        shutil.rmtree(output_root)
    shutil.copytree(source_root,output_root)
    promote_tree_spec_versions(output_root)

    rows=load_assessments(source_root)
    observation_plan,observation_summary,candidate_errors=build_observation_plan(rows)
    if candidate_errors:
        raise ValueError(f"Observation candidate errors: {candidate_errors}")

    assessment_rows=[]
    totals={
        "automated_assessments":0,
        "deferred_observation_opportunities":0,
        "foreach_rewrites":0,
        "static_constant_variables_removed":0,
        "static_literal_references_replaced":0,
        "localized_set_operand_objects":0,
        "localized_variable_objects":0,
        "localized_object_graph_objects":0,
        "localized_variables":0,
        "localized_external_variables":0,
        "localized_constant_variables":0,
        "localized_local_variables":0,
        "localized_state_occurrences":0,
    }

    for index,row in enumerate(rows):
        original=copy.deepcopy(row["doc"])
        relative=Path(row["relative_path"])
        working=copy.deepcopy(original)
        observation_type=None

        planned=observation_plan.get(index)
        if planned is not None:
            # Observation is intentionally deferred beyond normative 0.3.
            # Keep the opportunity visible in review evidence but do not
            # rewrite the accepted candidate tree.
            kind,_,_=planned
            observation_type=kind
            totals["deferred_observation_opportunities"]+=1

        research=promote_to_research_03(working)
        foreach_doc,foreach_report=modernize_foreach_v1(research,enabled=True)
        rewrites=int(foreach_report["stats"].get("rewrites_applied",0) or 0)
        totals["foreach_rewrites"]+=rewrites

        static_doc,static_proof=inline_constants(foreach_doc)
        static_restored=reexpand_constants(static_doc,static_proof)
        if static_restored!=foreach_doc:
            detail=first_difference(foreach_doc,static_restored) or "unknown difference"
            raise ValueError(
                f"static-literal round-trip mismatch for {relative}: {detail}"
            )
        static_variables={row["variable"] for row in static_proof}
        totals["static_constant_variables_removed"]+=len(static_variables)
        totals["static_literal_references_replaced"]+=len(static_proof)

        rendered,identity=inline_private(
            static_doc,
            inline_private_set_operands=True,
            inline_private_filtered_set_operands=True,
            inline_state_consumers=True,
            inline_variable_object_consumers=True,
            inline_private_object_consumers=True,
            # Named Variables remain first-class for genuine runtime/expression
            # dataflow. Only the exact compile-time static-literal pass above may
            # remove Variables in the accepted 0.3 review candidate.
            inline_private_variables=False,
            inline_private_local_variables=False,
        )
        expanded=reexpand(rendered,identity)
        if expanded!=static_doc:
            detail=first_difference(static_doc,expanded) or "unknown difference"
            raise ValueError(f"locality round-trip mismatch for {relative}: {detail}")

        outpath=output_root/relative
        outpath.parent.mkdir(parents=True,exist_ok=True)
        outpath.write_text(dump_yaml(rendered),encoding="utf-8")

        localized_vars=identity.get("inlined_variables") or []
        totals["localized_set_operand_objects"]+=len(
            identity.get("inlined_set_operand_objects") or []
        )
        totals["localized_variable_objects"]+=len(
            identity.get("inlined_variable_objects") or []
        )
        totals["localized_object_graph_objects"]+=len(
            identity.get("inlined_object_graph_objects") or []
        )
        totals["localized_variables"]+=len(localized_vars)
        totals["localized_external_variables"]+=sum(
            x.get("kind")=="external" for x in localized_vars
        )
        totals["localized_constant_variables"]+=sum(
            x.get("kind")=="constant" for x in localized_vars
        )
        totals["localized_local_variables"]+=sum(
            x.get("kind")=="local" for x in localized_vars
        )
        totals["localized_state_occurrences"]+=len(
            identity.get("inlined_state_consumer_occurrences") or []
        )
        totals["automated_assessments"]+=1

        assessment_rows.append({
            "assessment_id":rendered["assessment"].get("id"),
            "path":relative.as_posix(),
            "kind":row["kind"],
            "deferred_observation_opportunity":observation_type,
            "foreach_rewrites":rewrites,
            "static_literals":{
                "constant_variables_removed":len(static_variables),
                "references_replaced":len(static_proof),
            },
            "localized":{
                "test_objects":len(identity.get("inlined_objects") or {}),
                "test_states":len(identity.get("inlined_states") or {}),
                "set_operand_objects":len(identity.get("inlined_set_operand_objects") or []),
                "variable_objects":len(identity.get("inlined_variable_objects") or []),
                "object_graph_objects":len(identity.get("inlined_object_graph_objects") or []),
                "variables":len(localized_vars),
                "state_consumer_occurrences":len(
                    identity.get("inlined_state_consumer_occurrences") or []
                ),
            },
        })

    # Final presentation-only 0.3 review surface. This does not participate in
    # semantic equivalence claims above; it reconciles known 0.3 terminology
    # and redundant benchmark-local naming for human review.
    surface_report=normalize_tree(output_root)

    # #208: compile the 0.3 review surface to local predicates, retaining
    # a non-executable, independently verifiable migration record. Do this
    # after vocabulary normalization so the authored surface is the final form.
    evidence_dir.mkdir(parents=True,exist_ok=True)
    embedded_summary={"assessments":0,"replaced_uses":0,"removed_named_states":0}
    for assessment_path in sorted(output_root.rglob("*.yaml")):
        doc=yaml.safe_load(assessment_path.read_text(encoding="utf-8"))
        if not isinstance(doc,dict) or not isinstance(doc.get("assessment"),dict):
            continue
        if doc["assessment"].get("mode")!="automated":
            continue
        embedded,ledger=embed_predicates(doc)
        if reexpand_predicates(embedded,ledger)!=doc:
            raise ValueError(f"predicate re-expansion mismatch for {assessment_path}")
        assessment_path.write_text(dump_yaml(embedded),encoding="utf-8")
        embedded_summary["assessments"]+=1
        embedded_summary["replaced_uses"]+=len(ledger["changes"])
        embedded_summary["removed_named_states"]+=len(ledger["named_states"] or {})
        if ledger["changes"] or ledger["named_states"]:
            relative=assessment_path.relative_to(output_root)
            ledger_path=evidence_dir/"embedded-predicate-ledgers"/relative.with_suffix(".ledger.json")
            ledger_path.parent.mkdir(parents=True,exist_ok=True)
            ledger_path.write_text(json.dumps(ledger,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    (evidence_dir/"embedded-predicate-summary.json").write_text(
        json.dumps(embedded_summary,indent=2,sort_keys=True)+"\n",
        encoding="utf-8"
    )

    (evidence_dir/"review-surface-normalization.json").write_text(
        json.dumps(surface_report,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    report={
        "format":"scap-ng-0.3-human-review-render-0.1",
        "status":"accepted_0_3_requirements_review_candidate",
        "label":label,
        "source_root":str(source_root),
        "candidate_root":str(output_root),
        "proof":{
            "deferred_observation_not_applied":True,
            "locality_reexpand_exact":True,
            "foreach_only_proven_v1":True,
            "static_literal_roundtrip_exact":True,
            "static_literal_folding_atomic_fail_closed":True,
            "review_surface_is_presentation_only":True,
        },
        "embedded_predicate_migration":embedded_summary,
        "review_surface_normalization":{
            "renamed_assessment_files":len(surface_report.get("renames") or []),
            "assessment_ids_shortened":len(surface_report.get("assessment_id_map") or {}),
            "documents_changed":len(surface_report.get("document_changes") or []),
            "candidate_vocabulary":surface_report.get("candidate_vocabulary"),
        },
        "deferred_observation_opportunity_plan":observation_summary,
        "summary":totals,
        "assessments":assessment_rows,
    }
    (evidence_dir/"render-report.json").write_text(
        json.dumps(report,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    (output_root/"CANDIDATE-STATUS.md").write_text(
        "# SCAP-NG 0.3 human-review candidate\n\n"
        "**Pre-alpha Board-review candidate. Not a released or Board-approved standard.**\n\n"
        "This tree starts from the pinned faithful SCAP 1.4 conversion and applies "
        "only the currently proven modernization stack: consumer locality, private "
        "Set operands, Variable-local Objects, compile-time static literal "
        "folding while genuine computed Variables remain named, recursive private "
        "Object locality, and bounded foreach v1. Shared "
        "Observation opportunities are measured "
        "separately but are deferred beyond normative 0.3 and are not rendered.\n\n"
        "The accompanying scorecard explains what changed and what deliberately "
        "remains complex. The review surface also applies the candidate 0.3 "
        "terminology/naming normalization tracked by issues #151-#156: shorter "
        "benchmark-local Assessment names, Test existence/match field names, "
        "one_or_more at-least-one spelling, full-word snake_case comparison "
        "operations, and all/local/same filesystem scope. These are accepted "
        "0.3 requirements and remain subject to Board review before any final "
        "standardization claim.\n",
        encoding="utf-8",
    )
    return report


def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("source_root",type=Path)
    p.add_argument("--output-root",type=Path,required=True)
    p.add_argument("--evidence-dir",type=Path,required=True)
    p.add_argument("--label",required=True)
    args=p.parse_args()
    report=render(args.source_root,args.output_root,args.evidence_dir,args.label)
    print(json.dumps(report["summary"],indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
