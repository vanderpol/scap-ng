#!/usr/bin/env python3
"""Measure proven SCAP-NG 0.3 modernization opportunities on one fresh Benchmark.

This is a research census, not a converter and not an accepted 0.3 authoring
implementation. It starts from the faithful current conversion and applies only
bounded transformations with existing exact proof contracts:
- foreach v1 for its fail-closed proven class;
- consumer-local Object/State/Set/Variable-Object presentation with exact
  structural re-expansion.

Deferred/non-0.3 features such as shared Observation, broader conditional/case
authoring, and linux.fstab are measured separately and are not applied to the
accepted 0.3 candidate stack.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import yaml

from measure_evaluate_shapes import analyze_assessment
from prove_apache_observation import (
    observation_document as apache_observation_document,
    extract as apache_extract,
    flatten as apache_flatten,
)
from prove_windows_domainrole_observation import (
    candidate_object as windows_candidate_object,
    observation_document as windows_observation_document,
    extract as windows_extract,
    flatten as windows_flatten,
)
from prove_rhel_dconf_observation import (
    observation_document as dconf_observation_document,
    extract as dconf_extract,
    flatten as dconf_flatten,
)
from research_inline_private_components import (
    inline_private,
    reexpand,
    metrics,
    first_difference,
    context_signature,
)
from research_static_literal_collections import (
    inline_constants,
    reexpand_constants,
)
from scap_upconvert_v003.foreach_modernization import modernize_foreach_v1


OBSERVATION_TYPES=("apache_httpd","windows_domain_role","dconf_databases")


def canonical(value:Any)->str:
    return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False)


def fingerprint(value:Any)->str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def load_assessments(root:Path):
    rows=[]
    for path in sorted(root.rglob("*.assessment.yaml")):
        try:
            doc=yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception as exc:
            raise ValueError(f"cannot parse {path}: {exc}") from exc
        if not isinstance(doc,dict) or not isinstance(doc.get("assessment"),dict):
            continue
        a=doc["assessment"]
        if a.get("mode")!="automated":
            continue
        rel=path.relative_to(root)
        parts=rel.parts
        kind=(
            "rule"
            if len(parts)>=2 and parts[0]=="assessments" and parts[1]=="automated"
            else "applicability"
            if len(parts)>=2 and parts[0]=="assessments" and parts[1]=="applicability"
            else "other_automated"
        )
        rows.append({
            "path":path,
            "relative_path":rel.as_posix(),
            "kind":kind,
            "doc":doc,
        })
    return rows


def observation_candidate(kind:str,doc:dict):
    a=doc["assessment"]
    if kind=="apache_httpd":
        return apache_observation_document(a)
    if kind=="windows_domain_role":
        candidate=windows_candidate_object(a)
        if candidate is None:
            return None
        _,payload=candidate
        return windows_observation_document(payload)
    if kind=="dconf_databases":
        return dconf_observation_document(a)
    raise ValueError(kind)


def apply_observation(kind:str,doc:dict,observation:dict):
    if kind=="apache_httpd":
        extracted,refs=apache_extract(doc,observation)
        restored=apache_flatten(extracted,observation)
        ref_count=sum(refs.values())
        return extracted,restored,{
            "export_reference_count":ref_count,
            "export_reference_counts":dict(refs),
        }
    if kind=="windows_domain_role":
        extracted,object_name,refs=windows_extract(doc,observation)
        restored=windows_flatten(extracted,observation,object_name)
        return extracted,restored,{
            "export_reference_count":refs,
            "export_reference_counts":{"computer_system":refs},
        }
    if kind=="dconf_databases":
        extracted,object_name,variable_name,refs=dconf_extract(doc,observation)
        restored=dconf_flatten(extracted,observation,object_name,variable_name)
        return extracted,restored,{
            "export_reference_count":sum(refs.values()),
            "export_reference_counts":dict(refs),
        }
    raise ValueError(kind)


def build_observation_plan(rows):
    """Return exact within-package shared-artifact groups.

    A candidate shape is extracted only when at least two consumers have the
    exact same Observation payload. A type with multiple payload fingerprints is
    intentionally left faithful and reported for review rather than guessed.
    """
    by_type={kind:defaultdict(list) for kind in OBSERVATION_TYPES}
    candidate_errors=[]
    for index,row in enumerate(rows):
        for kind in OBSERVATION_TYPES:
            try:
                obs=observation_candidate(kind,row["doc"])
            except ValueError as exc:
                candidate_errors.append({
                    "assessment_id":row["doc"]["assessment"].get("id"),
                    "observation_type":kind,
                    "reason":str(exc),
                })
                continue
            if obs is not None:
                by_type[kind][fingerprint(obs)].append((index,obs))

    plan={}
    summary={}
    for kind,groups in by_type.items():
        group_rows=[]
        applicable=[]
        variant_count=len(groups)
        for fp,members in sorted(groups.items()):
            consumers=len(members)
            obs=members[0][1]
            contract=obs["observation"]
            group={
                "fingerprint":fp,
                "consumers":consumers,
                "observation_id":contract.get("id"),
                "objects":len(contract.get("objects") or {}),
                "variables":len(contract.get("variables") or {}),
                "exports":len(contract.get("exports") or {}),
                "applied":False,
            }
            # Fail closed on payload variants. The research proof establishes a
            # single reusable artifact, not automatic semantic clone splitting.
            if variant_count==1 and consumers>=2:
                group["applied"]=True
                applicable.append((fp,members))
            elif consumers<2:
                group["reason"]="single_consumer_not_worth_shared_artifact"
            else:
                group["reason"]="payload_variants_require_review"
            group_rows.append(group)
        summary[kind]={
            "candidate_consumers":sum(len(v) for v in groups.values()),
            "payload_variants":variant_count,
            "groups":group_rows,
        }
        for fp,members in applicable:
            obs=members[0][1]
            for index,_ in members:
                plan[index]=(kind,obs,fp)
    return plan,summary,candidate_errors


def evaluate_metrics(path:Path,doc:dict):
    a=doc["assessment"]
    if "evaluate" not in a:
        return {
            "test_count":len(a.get("tests") or {}),
            "evaluate_depth":0,
            "evaluate_nodes":0,
            "trivial_single_test_evaluate":False,
            "flat_test_operator":False,
            "repeated_test_ref_occurrences":0,
        }
    row=analyze_assessment(path,doc)
    return {
        "test_count":row["test_count"],
        "evaluate_depth":row["evaluate_depth"],
        "evaluate_nodes":row["evaluate_nodes"],
        "trivial_single_test_evaluate":row["trivial_single_test_evaluate"],
        "flat_test_operator":row["flat_test_operator"],
        "repeated_test_ref_occurrences":row["repeated_test_ref_occurrences"],
    }


def contains_key(value:Any,keys:set[str])->bool:
    if isinstance(value,dict):
        if any(k in value for k in keys):
            return True
        return any(contains_key(v,keys) for v in value.values())
    if isinstance(value,list):
        return any(contains_key(v,keys) for v in value)
    return False


def promote_to_research_03(doc:dict)->dict:
    out=copy.deepcopy(doc)
    a=out["assessment"]
    spec=a.setdefault("specification",{
        "id":"scap-ng.pre-alpha.assessment",
        "version":"0.3.0",
    })
    spec["version"]="0.3.0"
    return out


def variable_kind_counts(a:dict)->Counter:
    counts=Counter()
    for payload in (a.get("variables") or {}).values():
        if not isinstance(payload,dict):
            counts["unknown"]+=1
            continue
        counts[str(payload.get("kind") or "unknown")]+=1
    return counts


def residual_reasons(rendered:dict,identity:dict,evalm:dict):
    a=rendered["assessment"]
    reasons=[]
    retained=identity.get("retained_object_reasons") or {}
    if any(reason in {
        "multiple_tests","multiple_tests_and_graph","test_and_graph"
    } for reason in retained.values()):
        reasons.append("shared_acquisition")
    variable_kinds=variable_kind_counts(a)
    if variable_kinds.get("local",0) or variable_kinds.get("unknown",0):
        reasons.append("derived_variable_graph")
    if variable_kinds.get("external",0):
        reasons.append("external_input_binding")
    if variable_kinds.get("constant",0):
        reasons.append("constant_binding")
    if contains_key(a,{"set","filters","filter"}):
        reasons.append("set_filter_semantics")
    if evalm["test_count"]>1:
        reasons.append("multiple_tests_evaluate")
    if evalm["evaluate_depth"]>2:
        reasons.append("nested_boolean_logic")
    if evalm["repeated_test_ref_occurrences"]:
        reasons.append("repeated_test_reference")
    if a.get("states"):
        reasons.append("named_state_reuse")
    if a.get("objects") and "shared_acquisition" not in reasons:
        reasons.append("named_object_graph")
    return reasons


def classify(rendered:dict,identity:dict,evalm:dict,*,observation_applied:bool,foreach_applied:int):
    if observation_applied:
        return "shared_observation_consumer"
    if foreach_applied:
        return "bounded_dataflow"
    reasons=residual_reasons(rendered,identity,evalm)
    structural={
        "shared_acquisition","derived_variable_graph","set_filter_semantics",
        "nested_boolean_logic","repeated_test_reference","named_state_reuse",
        "named_object_graph",
    }
    if structural.intersection(reasons):
        return "meaningfully_complex"
    return "local_simple"


def sum_metrics(target:Counter,m:dict,prefix:str=""):
    for key,value in m.items():
        if isinstance(value,(int,float)) and not isinstance(value,bool):
            target[prefix+key]+=value


def build_report(root:Path,*,label:str,source_artifact:str|None=None):
    rows=load_assessments(root)
    observation_plan,observation_summary,candidate_errors=build_observation_plan(rows)

    totals=Counter()
    classes=Counter()
    classes_by_kind=defaultdict(Counter)
    residuals=Counter()
    residuals_by_kind=defaultdict(Counter)
    complex_residuals_by_kind=defaultdict(Counter)
    foreach_review=Counter()
    observation_types=Counter()
    observation_exports=Counter()
    retained_object_reasons=Counter()
    retained_object_contexts=Counter()
    retained_object_context_signatures=Counter()
    assessment_rows=[]

    applied_artifacts=set()
    applied_artifact_contracts={}

    for index,row in enumerate(rows):
        original=row["doc"]
        aid=original["assessment"].get("id")
        before=metrics(original)
        eval_before=evaluate_metrics(row["path"],original)
        sum_metrics(totals,before,"baseline_")
        totals["automated_assessments"]+=1
        totals[f"{row['kind']}_assessments"]+=1
        if eval_before["trivial_single_test_evaluate"]:
            totals["single_test_explicit_root_authoring_opportunities"]+=1

        working=copy.deepcopy(original)
        observation_applied=False
        observation_info=None

        planned=observation_plan.get(index)
        if planned is not None:
            # Observation is deferred from normative 0.3. Preserve the exact
            # proof/census as a future opportunity, but do not rewrite accepted
            # candidate content through an Observation artifact.
            kind,obs,fp=planned
            extracted,restored,info=apply_observation(kind,working,obs)
            if restored!=working:
                detail=first_difference(working,restored) or "unknown difference"
                raise ValueError(
                    f"Observation round-trip mismatch for {row['relative_path']}: {detail}"
                )
            observation_types[kind]+=1
            totals["deferred_observation_candidate_assessments"]+=1
            totals["deferred_observation_export_references"]+=info["export_reference_count"]
            for export,count in info["export_reference_counts"].items():
                observation_exports[f"{kind}:{export}"]+=count
            artifact_key=(kind,fp)
            if artifact_key not in applied_artifacts:
                applied_artifacts.add(artifact_key)
                contract=obs["observation"]
                applied_artifact_contracts[f"{kind}:{fp[:12]}"]={
                    "type":kind,
                    "fingerprint":fp,
                    "observation_id":contract.get("id"),
                    "objects":len(contract.get("objects") or {}),
                    "variables":len(contract.get("variables") or {}),
                    "exports":len(contract.get("exports") or {}),
                }
                totals["deferred_observation_candidate_artifacts"]+=1
                totals["deferred_observation_unique_objects"]+=len(contract.get("objects") or {})
                totals["deferred_observation_unique_variables"]+=len(contract.get("variables") or {})
            contract=obs["observation"]
            totals["deferred_observation_object_occurrences"]+=len(contract.get("objects") or {})
            totals["deferred_observation_variable_occurrences"]+=len(contract.get("variables") or {})
            observation_info={
                "type":kind,
                "fingerprint":fp,
                "status":"deferred_post_0_3",
                **info,
            }

        # Measure only the already-proven foreach v1 rewrite class. The frozen
        # faithful conversion says 0.2.0, so clone it into the research 0.3
        # authoring context before asking the fail-closed modernizer to match.
        foreach_input=promote_to_research_03(working)
        foreach_doc,foreach_report=modernize_foreach_v1(foreach_input,enabled=True)
        fstats=foreach_report["stats"]
        foreach_applied=int(fstats.get("rewrites_applied",0) or 0)
        totals["foreach_variables_total"]+=int(fstats.get("variables_total",0) or 0)
        totals["foreach_direct_projection_variables_examined"]+=int(
            fstats.get("direct_projection_variables_examined",0) or 0
        )
        totals["foreach_rewrite_candidates_proven"]+=int(
            fstats.get("rewrite_candidates_proven",0) or 0
        )
        totals["foreach_rewrites_applied"]+=foreach_applied
        totals["foreach_review_required_variables"]+=int(
            fstats.get("review_required_variables",0) or 0
        )
        if foreach_applied:
            totals["foreach_rewritten_assessments"]+=1
        for reason,count in (fstats.get("review_reason_counts") or {}).items():
            foreach_review[reason]+=int(count)

        static_doc,static_proof=inline_constants(foreach_doc)
        static_restored=reexpand_constants(static_doc,static_proof)
        if static_restored!=foreach_doc:
            detail=first_difference(foreach_doc,static_restored) or "unknown difference"
            raise ValueError(
                f"static-literal round-trip mismatch for {row['relative_path']}: {detail}"
            )
        static_variables={entry["variable"] for entry in static_proof}
        totals["static_constant_variables_removed"]+=len(static_variables)
        totals["static_literal_references_replaced"]+=len(static_proof)
        if static_variables:
            totals["static_literal_changed_assessments"]+=1

        rendered,identity=inline_private(
            static_doc,
            inline_private_set_operands=True,
            inline_private_filtered_set_operands=True,
            inline_state_consumers=True,
            inline_variable_object_consumers=True,
            inline_private_object_consumers=True,
            inline_private_variables=True,
            inline_private_local_variables=True,
        )
        expanded=reexpand(rendered,identity)
        if expanded!=static_doc:
            detail=first_difference(static_doc,expanded) or "unknown difference"
            raise ValueError(
                f"locality round-trip mismatch for {row['relative_path']}: {detail}"
            )
        after=metrics(rendered)
        eval_after=evaluate_metrics(row["path"],rendered)
        sum_metrics(totals,after,"modernized_")
        localized_variables=identity.get("inlined_variables") or []

        object_reason_counts=Counter(identity.get("retained_object_reasons",{}).values())
        object_context_counts=Counter()
        object_context_signature_counts=Counter()
        for object_context in (identity.get("retained_object_contexts") or {}).values():
            object_context_signature_counts[context_signature(object_context)]+=1
            object_context_counts.update(object_context)
        retained_object_reasons.update(object_reason_counts)
        retained_object_contexts.update(object_context_counts)
        retained_object_context_signatures.update(object_context_signature_counts)

        totals["recursive_object_graph_objects_localized"]+=len(
            identity.get("inlined_object_graph_objects") or []
        )
        totals["private_binding_variables_localized"]+=len(localized_variables)
        totals["private_external_variables_localized"]+=sum(
            row.get("kind")=="external" for row in localized_variables
        )
        totals["private_constant_variables_localized"]+=sum(
            row.get("kind")=="constant" for row in localized_variables
        )
        totals["private_local_variables_localized"]+=sum(
            row.get("kind")=="local" for row in localized_variables
        )

        category=classify(
            rendered,identity,eval_after,
            observation_applied=observation_applied,
            foreach_applied=foreach_applied,
        )
        classes[category]+=1
        classes_by_kind[row["kind"]][category]+=1
        reasons=residual_reasons(rendered,identity,eval_after)
        residuals.update(reasons)
        residuals_by_kind[row["kind"]].update(reasons)
        if category=="meaningfully_complex":
            complex_residuals_by_kind[row["kind"]].update(reasons)

        assessment_rows.append({
            "assessment_id":aid,
            "path":row["relative_path"],
            "kind":row["kind"],
            "classification":category,
            "observation":observation_info,
            "foreach_rewrites":foreach_applied,
            "static_literals":{
                "constant_variables_removed":len(static_variables),
                "references_replaced":len(static_proof),
            },
            "before":{
                "objects":before["objects"],
                "states":before["states"],
                "variables":before["variables"],
                "tests":before["tests"],
                "named_refs":before["named_component_cross_references"],
            },
            "after":{
                "objects":after["objects"],
                "states":after["states"],
                "variables":after["variables"],
                "tests":after["tests"],
                "named_refs":after["named_component_cross_references"],
            },
            "evaluate":{
                "depth":eval_after["evaluate_depth"],
                "nodes":eval_after["evaluate_nodes"],
                "repeated_test_refs":eval_after["repeated_test_ref_occurrences"],
                "single_test_explicit_root":eval_before["trivial_single_test_evaluate"],
            },
            "residual_reasons":reasons,
            "locality":{
                "inlined_objects":len(identity.get("inlined_objects") or {}),
                "retained_object_reason_counts":dict(object_reason_counts),
                "retained_object_context_counts":dict(object_context_counts),
                "retained_object_context_signature_counts":dict(object_context_signature_counts),
                "inlined_set_operand_objects":len(identity.get("inlined_set_operand_objects") or []),
                "inlined_variable_objects":len(identity.get("inlined_variable_objects") or []),
                "inlined_variables":len(identity.get("inlined_variables") or []),
                "inlined_external_variables":sum(
                    row.get("kind")=="external"
                    for row in (identity.get("inlined_variables") or [])
                ),
                "inlined_constant_variables":sum(
                    row.get("kind")=="constant"
                    for row in (identity.get("inlined_variables") or [])
                ),
                "inlined_local_variables":sum(
                    row.get("kind")=="local"
                    for row in (identity.get("inlined_variables") or [])
                ),
                "inlined_states":len(identity.get("inlined_states") or {}),
                "inlined_state_consumer_occurrences":len(
                    identity.get("inlined_state_consumer_occurrences") or []
                ),
            },
        })

    def reduction(before_key,after_key):
        before=totals[before_key]
        after=totals[after_key]
        return round(100.0*(before-after)/before,2) if before else 0.0

    summary=dict(totals)
    summary.update({
        "classification_counts":dict(classes),
        "classification_counts_by_kind":{
            kind:dict(counts) for kind,counts in sorted(classes_by_kind.items())
        },
        "residual_reason_counts":dict(residuals),
        "residual_reason_counts_by_kind":{
            kind:dict(counts) for kind,counts in sorted(residuals_by_kind.items())
        },
        "meaningfully_complex_residual_reason_counts_by_kind":{
            kind:dict(counts)
            for kind,counts in sorted(complex_residuals_by_kind.items())
        },
        "foreach_review_reason_counts":dict(foreach_review),
        "deferred_observation_candidate_counts":dict(observation_types),
        "deferred_observation_export_reference_counts":dict(observation_exports),
        "retained_object_reason_counts":dict(retained_object_reasons),
        "retained_object_context_counts":dict(retained_object_contexts),
        "retained_object_context_signature_counts":dict(retained_object_context_signatures),
        "object_scope_reduction_pct":reduction("baseline_objects","modernized_objects"),
        "state_scope_reduction_pct":reduction("baseline_states","modernized_states"),
        "variable_reduction_pct":reduction("baseline_variables","modernized_variables"),
        "named_reference_reduction_pct":reduction(
            "baseline_named_component_cross_references",
            "modernized_named_component_cross_references",
        ),
        "normalized_line_reduction_pct":reduction(
            "baseline_normalized_lines","modernized_normalized_lines"
        ),
        "normalized_byte_reduction_pct":reduction(
            "baseline_normalized_bytes","modernized_normalized_bytes"
        ),
    })

    return {
        "format":"scap-ng-full-modernization-package-census-0.1",
        "status":"research_only_not_accepted_design",
        "label":label,
        "source_artifact":source_artifact,
        "source_root":str(root),
        "modernization_scope":{
            "applied_exact":[
                "consumer-local Object/State presentation",
                "private Set-operand locality",
                "Variable-local Object locality",
                "single-use external/constant Variable locality",
                "single-use leaf derived Variable locality",
                "foreach.direct-object-component.at-least-one.v1",
            ],
            "measured_not_applied":[
                "single-Test evaluate-root authoring ceremony",
                "proven shared Observation extraction shapes (deferred post-0.3)",
            ],
            "intentionally_not_rewritten":[
                "conditional/case native authoring",
                "linux.fstab typed native capability",
                "violation-query positive spelling",
                "general concat/multi-source foreach",
                "domain-specific semantic changes",
            ],
        },
        "observation_plan":observation_summary,
        "observation_candidate_errors":candidate_errors,
        "deferred_observation_candidates":applied_artifact_contracts,
        "summary":summary,
        "assessments":assessment_rows,
    }


def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("root",type=Path)
    p.add_argument("--label",required=True)
    p.add_argument("--source-artifact")
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    report=build_report(
        args.root,label=args.label,source_artifact=args.source_artifact
    )
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(report["summary"],indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
