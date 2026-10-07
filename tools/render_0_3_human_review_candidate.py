#!/usr/bin/env python3
"""Render a complete research-only 0.3 candidate benchmark tree for human review.

This is deliberately separate from the faithful converter and frozen 0.2
Board build. It starts from a fresh faithful converted benchmark and applies
only the exact/proven research modernization stack currently used by the
full-corpus census.

The output is author-review material, not normative schema-valid 0.3 content.
Every structural locality transformation must mechanically re-expand to its
pre-locality input. Observation extraction must flatten exactly to the faithful
input before any later modernization is applied.
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
    apply_observation,
    build_observation_plan,
    load_assessments,
    promote_to_research_03,
)
from research_inline_private_components import (
    first_difference,
    inline_private,
    reexpand,
)
from scap_upconvert_v003.foreach_modernization import modernize_foreach_v1


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


def resolve_observation_target(
    candidate_root:Path,
    assessment_relative_path:Path,
    extracted:dict,
)->list[Path]:
    targets=[]
    bindings=(extracted.get("assessment") or {}).get("observations") or {}
    for binding in bindings.values():
        if not isinstance(binding,dict):
            continue
        source=binding.get("source")
        if not isinstance(source,str):
            continue
        target=(candidate_root/assessment_relative_path.parent/source).resolve()
        root_resolved=candidate_root.resolve()
        try:
            target.relative_to(root_resolved)
        except ValueError as exc:
            raise ValueError(f"Observation source escapes candidate root: {source}") from exc
        targets.append(target)
    return targets


def render(source_root:Path,output_root:Path,evidence_dir:Path,label:str)->dict:
    if output_root.exists():
        shutil.rmtree(output_root)
    shutil.copytree(source_root,output_root)
    promote_tree_spec_versions(output_root)

    rows=load_assessments(source_root)
    observation_plan,observation_summary,candidate_errors=build_observation_plan(rows)
    if candidate_errors:
        raise ValueError(f"Observation candidate errors: {candidate_errors}")

    observation_targets={}
    assessment_rows=[]
    totals={
        "automated_assessments":0,
        "observation_consumers":0,
        "foreach_rewrites":0,
        "localized_set_operand_objects":0,
        "localized_variable_objects":0,
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
        observation_applied=False
        observation_type=None

        planned=observation_plan.get(index)
        if planned is not None:
            kind,observation,_=planned
            extracted,restored,_=apply_observation(kind,working,observation)
            if restored!=working:
                detail=first_difference(working,restored) or "unknown difference"
                raise ValueError(
                    f"Observation flatten mismatch for {relative}: {detail}"
                )
            targets=resolve_observation_target(output_root,relative,extracted)
            if not targets:
                raise ValueError(f"Observation consumer has no source binding: {relative}")
            for target in targets:
                prior=observation_targets.get(target)
                if prior is not None and prior!=observation:
                    raise ValueError(f"Observation payload collision at {target}")
                observation_targets[target]=copy.deepcopy(observation)
            working=extracted
            observation_applied=True
            observation_type=kind
            totals["observation_consumers"]+=1

        research=promote_to_research_03(working)
        foreach_doc,foreach_report=modernize_foreach_v1(research,enabled=True)
        rewrites=int(foreach_report["stats"].get("rewrites_applied",0) or 0)
        totals["foreach_rewrites"]+=rewrites

        rendered,identity=inline_private(
            foreach_doc,
            inline_private_set_operands=True,
            inline_private_filtered_set_operands=True,
            inline_state_consumers=True,
            inline_variable_object_consumers=True,
            inline_private_variables=True,
            inline_private_local_variables=True,
        )
        expanded=reexpand(rendered,identity)
        if expanded!=foreach_doc:
            detail=first_difference(foreach_doc,expanded) or "unknown difference"
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
            "observation":observation_type,
            "foreach_rewrites":rewrites,
            "localized":{
                "test_objects":len(identity.get("inlined_objects") or {}),
                "test_states":len(identity.get("inlined_states") or {}),
                "set_operand_objects":len(identity.get("inlined_set_operand_objects") or []),
                "variable_objects":len(identity.get("inlined_variable_objects") or []),
                "variables":len(localized_vars),
                "state_consumer_occurrences":len(
                    identity.get("inlined_state_consumer_occurrences") or []
                ),
            },
        })

    for target,observation in observation_targets.items():
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(dump_yaml(observation),encoding="utf-8")

    evidence_dir.mkdir(parents=True,exist_ok=True)
    report={
        "format":"scap-ng-0.3-human-review-render-0.1",
        "status":"research_only_not_accepted_design",
        "label":label,
        "source_root":str(source_root),
        "candidate_root":str(output_root),
        "proof":{
            "observation_flatten_exact":True,
            "locality_reexpand_exact":True,
            "foreach_only_proven_v1":True,
        },
        "observation_plan":observation_summary,
        "observation_artifacts":[
            str(path.relative_to(output_root))
            for path in sorted(observation_targets)
        ],
        "summary":totals,
        "assessments":assessment_rows,
    }
    (evidence_dir/"render-report.json").write_text(
        json.dumps(report,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    (output_root/"CANDIDATE-STATUS.md").write_text(
        "# SCAP-NG 0.3 human-review candidate\n\n"
        "**Research-only. Not a released schema or Board-approved format.**\n\n"
        "This tree starts from the pinned faithful SCAP 1.4 conversion and applies "
        "only the currently proven modernization stack: consumer locality, private "
        "Set operands, Variable-local Objects, single-use external/constant and "
        "leaf-derived Variable locality, bounded foreach v1, and proven shared "
        "Observation extraction.\n\n"
        "The accompanying scorecard explains what changed and what deliberately "
        "remains complex. Human acceptance is required before these forms become "
        "normative 0.3 schema/specification semantics.\n",
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
