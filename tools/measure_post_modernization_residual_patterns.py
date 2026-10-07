#!/usr/bin/env python3
"""Classify residual Set/Filter and derived-Variable patterns after exact modernization.

Research only. This applies the same proven transformations as the full 0.3
modernization census, then describes the Rules that remain meaningfully complex.
It does not introduce or apply a new semantic rewrite.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from measure_full_modernization_census import (
    apply_observation,
    build_observation_plan,
    classify,
    evaluate_metrics,
    load_assessments,
    promote_to_research_03,
    residual_reasons,
)
from measure_residual_complexity_patterns import (
    FUNCTION_KEYS,
    expression_variable_kind,
    walk,
)
from research_inline_private_components import (
    first_difference,
    inline_private,
    reexpand,
)
from scap_upconvert_v003.foreach_modernization import modernize_foreach_v1


def fingerprint(value: Any) -> str:
    raw=json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def scalar_shape(value: Any) -> Any:
    """Keep semantic structure while abstracting IDs and literal payloads."""
    if isinstance(value,dict):
        out={}
        for key,child in value.items():
            if key in {
                "id","version","assessment_title","test_title","object_title",
                "state_title","variable_title","title","provenance",
                "migration_provenance","reuse_provenance",
            }:
                continue
            if key in {"value","pattern","command"} and not isinstance(child,(dict,list)):
                out[key]="<LITERAL>"
            elif key in {"object","state","test","variable"} and isinstance(child,str):
                out[key]=f"<{key.upper()}_REF>"
            else:
                out[key]=scalar_shape(child)
        return out
    if isinstance(value,list):
        return [scalar_shape(x) for x in value]
    return value


def derived_variable_shape(variable: dict) -> dict:
    expr=variable.get("expression")
    funcs=Counter()
    for node in walk(expr):
        if isinstance(node,dict):
            for key in node:
                if key in FUNCTION_KEYS:
                    funcs[key]+=1
    return {
        "kind":variable.get("kind"),
        "datatype":variable.get("datatype"),
        "expression_kind":expression_variable_kind(variable),
        "functions":dict(sorted(funcs.items())),
    }


def filter_shape(filter_node: dict) -> dict:
    state=filter_node.get("state")
    if isinstance(state,dict):
        state_kind="inline"
        state_payload=scalar_shape(state)
    elif isinstance(state,str):
        state_kind="ref"
        state_payload=None
    else:
        state_kind="missing"
        state_payload=None
    return {
        "action":filter_node.get("action"),
        "state_kind":state_kind,
        "state_shape":state_payload,
    }


def set_shapes(value: Any, parent_capability: str|None=None, path=()) -> list[dict]:
    rows=[]
    if isinstance(value,dict):
        capability=value.get("capability") if isinstance(value.get("capability"),str) else parent_capability
        set_node=value.get("set")
        if isinstance(set_node,dict):
            operands=set_node.get("operands")
            if not isinstance(operands,list):
                operands=set_node.get("members")
            if not isinstance(operands,list):
                operands=[]
            operand_rows=[]
            for operand in operands:
                if not isinstance(operand,dict):
                    operand_rows.append({"kind":"other","filters":[]})
                    continue
                obj=operand.get("object")
                if isinstance(obj,str):
                    kind="object_ref"
                    object_capability=None
                    nested_set=False
                elif isinstance(obj,dict):
                    kind="inline_object"
                    object_capability=obj.get("capability")
                    nested_set=isinstance(obj.get("set"),dict)
                elif isinstance(operand.get("collect"),dict):
                    kind="inline_collect"
                    object_capability=operand["collect"].get("capability")
                    nested_set=False
                else:
                    kind="other"
                    object_capability=None
                    nested_set=False
                filters=operand.get("filters")
                if filters is None:
                    filters=[]
                elif not isinstance(filters,list):
                    filters=[filters]
                operand_rows.append({
                    "kind":kind,
                    "object_capability":object_capability,
                    "nested_set":nested_set,
                    "filters":[
                        filter_shape(f) if isinstance(f,dict) else {"kind":"other"}
                        for f in filters
                    ],
                })
            rows.append({
                "capability":capability,
                "operator":set_node.get("operator"),
                "operand_count":len(operands),
                "operands":operand_rows,
                "path_depth":len(path),
            })
        for key,child in value.items():
            rows.extend(set_shapes(child,capability,path+(str(key),)))
    elif isinstance(value,list):
        for index,child in enumerate(value):
            rows.extend(set_shapes(child,parent_capability,path+(str(index),)))
    return rows


def direct_filter_shapes(value: Any) -> list[dict]:
    """Describe Filter entries even when no Set wrapper is present."""
    rows=[]
    for node in walk(value):
        if not isinstance(node,dict):
            continue
        filters=node.get("filters")
        if isinstance(filters,list):
            rows.extend(filter_shape(f) for f in filters if isinstance(f,dict))
        elif isinstance(filters,dict):
            rows.append(filter_shape(filters))
        single=node.get("filter")
        if isinstance(single,list):
            rows.extend(filter_shape(f) for f in single if isinstance(f,dict))
        elif isinstance(single,dict):
            rows.append(filter_shape(single))
    return rows


def evaluate_shape(evalm: dict) -> dict:
    return {
        "test_count":evalm["test_count"],
        "evaluate_depth":evalm["evaluate_depth"],
        "evaluate_nodes":evalm["evaluate_nodes"],
        "repeated_test_ref_occurrences":evalm["repeated_test_ref_occurrences"],
    }


def coarse_set_signature(set_rows:list[dict],filter_rows:list[dict]) -> dict:
    operators=Counter(str(row.get("operator")) for row in set_rows)
    operand_counts=Counter(str(row.get("operand_count")) for row in set_rows)
    kinds=Counter()
    actions=Counter()
    inline_states=0
    ref_states=0
    nested_sets=0
    capabilities=Counter()
    for row in set_rows:
        if row.get("capability"):
            capabilities[str(row["capability"])]+=1
        for operand in row.get("operands") or []:
            kinds[operand.get("kind","other")]+=1
            nested_sets+=int(bool(operand.get("nested_set")))
            for f in operand.get("filters") or []:
                if f.get("action") is not None:
                    actions[str(f.get("action"))]+=1
                inline_states+=int(f.get("state_kind")=="inline")
                ref_states+=int(f.get("state_kind")=="ref")
    # direct_filter_shapes counts the same Set filters too; use it only for
    # total Filter cardinality and action distribution outside topology.
    all_actions=Counter(
        str(f.get("action")) for f in filter_rows if f.get("action") is not None
    )
    return {
        "set_count":len(set_rows),
        "operators":dict(sorted(operators.items())),
        "operand_count_histogram":dict(sorted(operand_counts.items())),
        "operand_kinds":dict(sorted(kinds.items())),
        "filter_count":len(filter_rows),
        "filter_actions":dict(sorted(all_actions.items())),
        "inline_filter_states":inline_states,
        "referenced_filter_states":ref_states,
        "nested_set_operands":nested_sets,
        "capabilities":dict(sorted(capabilities.items())),
    }


def build_report(root:Path,label:str,top:int=40)->dict:
    rows=load_assessments(root)
    observation_plan,_,_=build_observation_plan(rows)

    complex_rules=0
    set_filter_rules=0
    derived_variable_rules=0
    both_rules=0
    set_clusters=defaultdict(list)
    variable_clusters=defaultdict(list)
    joint_clusters=defaultdict(list)
    reason_counts=Counter()
    set_operator_counts=Counter()
    filter_action_counts=Counter()
    derived_kind_counts=Counter()
    derived_function_counts=Counter()

    for index,row in enumerate(rows):
        if row["kind"]!="rule":
            continue
        working=copy.deepcopy(row["doc"])
        observation_applied=False
        planned=observation_plan.get(index)
        if planned is not None:
            kind,obs,_=planned
            extracted,restored,_=apply_observation(kind,working,obs)
            if restored!=working:
                detail=first_difference(working,restored) or "unknown"
                raise ValueError(f"Observation round-trip mismatch {row['relative_path']}: {detail}")
            working=extracted
            observation_applied=True

        foreach_input=promote_to_research_03(working)
        foreach_doc,foreach_report=modernize_foreach_v1(foreach_input,enabled=True)
        foreach_applied=int(foreach_report["stats"].get("rewrites_applied",0) or 0)

        rendered,identity=inline_private(
            foreach_doc,
            inline_private_set_operands=True,
            inline_private_filtered_set_operands=True,
            inline_state_consumers=True,
            inline_variable_object_consumers=True,
            inline_private_variables=True,
        )
        expanded=reexpand(rendered,identity)
        if expanded!=foreach_doc:
            detail=first_difference(foreach_doc,expanded) or "unknown"
            raise ValueError(f"locality round-trip mismatch {row['relative_path']}: {detail}")

        evalm=evaluate_metrics(row["path"],rendered)
        category=classify(
            rendered,identity,evalm,
            observation_applied=observation_applied,
            foreach_applied=foreach_applied,
        )
        if category!="meaningfully_complex":
            continue
        complex_rules+=1
        reasons=residual_reasons(rendered,identity,evalm)
        reason_counts.update(reasons)

        a=rendered["assessment"]
        set_rows=set_shapes(a)
        filter_rows=direct_filter_shapes(a)
        variables=a.get("variables") or {}
        derived=[
            derived_variable_shape(v)
            for v in variables.values()
            if isinstance(v,dict) and v.get("kind")=="local"
        ]

        has_set_filter=bool(set_rows or filter_rows)
        has_derived=bool(derived)
        if has_set_filter:
            set_filter_rules+=1
        if has_derived:
            derived_variable_rules+=1
        if has_set_filter and has_derived:
            both_rules+=1

        set_sig=coarse_set_signature(set_rows,filter_rows)
        for op,count in set_sig["operators"].items():
            set_operator_counts[op]+=count
        for action,count in set_sig["filter_actions"].items():
            filter_action_counts[action]+=count
        for var in derived:
            derived_kind_counts[var["expression_kind"]]+=1
            derived_function_counts.update(var["functions"])

        common={
            "assessment_id":a.get("id"),
            "path":row["relative_path"],
            "reasons":reasons,
            "evaluate":evaluate_shape(evalm),
        }

        if has_set_filter:
            sig={
                "set_filter":set_sig,
                "derived_variable_kinds":sorted(v["expression_kind"] for v in derived),
                "evaluate":evaluate_shape(evalm),
            }
            set_clusters[fingerprint(sig)].append({**common,"signature":sig})
        if has_derived:
            var_sig={
                "variables":sorted(
                    derived,
                    key=lambda x:json.dumps(x,sort_keys=True,separators=(",",":"))
                ),
                "has_set_filter":has_set_filter,
                "evaluate":evaluate_shape(evalm),
            }
            variable_clusters[fingerprint(var_sig)].append({**common,"signature":var_sig})
        if has_set_filter or has_derived:
            joint_sig={
                "set_filter":set_sig if has_set_filter else None,
                "variables":sorted(
                    derived,
                    key=lambda x:json.dumps(x,sort_keys=True,separators=(",",":"))
                ),
                "evaluate":evaluate_shape(evalm),
            }
            joint_clusters[fingerprint(joint_sig)].append({**common,"signature":joint_sig})

    def ranked(clusters):
        out=[]
        for fp,members in sorted(clusters.items(),key=lambda kv:(-len(kv[1]),kv[0]))[:top]:
            out.append({
                "fingerprint":fp,
                "count":len(members),
                "signature":members[0]["signature"],
                "examples":[
                    {
                        "assessment_id":m["assessment_id"],
                        "reasons":m["reasons"],
                    }
                    for m in members[:12]
                ],
            })
        return out

    return {
        "format":"scap-ng-post-modernization-residual-patterns-0.1",
        "status":"research_only_not_accepted_design",
        "label":label,
        "complex_rules":complex_rules,
        "set_filter_rules":set_filter_rules,
        "derived_variable_rules":derived_variable_rules,
        "set_filter_and_derived_variable_rules":both_rules,
        "residual_reason_counts":dict(reason_counts),
        "set_operator_counts":dict(set_operator_counts),
        "filter_action_counts":dict(filter_action_counts),
        "derived_expression_kind_counts":dict(derived_kind_counts),
        "derived_function_counts":dict(derived_function_counts),
        "unique_set_filter_pattern_signatures":len(set_clusters),
        "unique_derived_variable_pattern_signatures":len(variable_clusters),
        "unique_joint_pattern_signatures":len(joint_clusters),
        "set_filter_pattern_counts":[
            {
                "fingerprint":fp,
                "count":len(members),
                "signature":members[0]["signature"],
                "examples":[m["assessment_id"] for m in members[:12]],
            }
            for fp,members in sorted(
                set_clusters.items(),key=lambda kv:(-len(kv[1]),kv[0])
            )
        ],
        "derived_variable_pattern_counts":[
            {
                "fingerprint":fp,
                "count":len(members),
                "signature":members[0]["signature"],
                "examples":[m["assessment_id"] for m in members[:12]],
            }
            for fp,members in sorted(
                variable_clusters.items(),key=lambda kv:(-len(kv[1]),kv[0])
            )
        ],
        "joint_pattern_counts":[
            {
                "fingerprint":fp,
                "count":len(members),
                "signature":members[0]["signature"],
                "examples":[m["assessment_id"] for m in members[:12]],
            }
            for fp,members in sorted(
                joint_clusters.items(),key=lambda kv:(-len(kv[1]),kv[0])
            )
        ],
        "top_set_filter_patterns":ranked(set_clusters),
        "top_derived_variable_patterns":ranked(variable_clusters),
        "top_joint_patterns":ranked(joint_clusters),
    }


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("root",type=Path)
    ap.add_argument("--label",required=True)
    ap.add_argument("--output",type=Path,required=True)
    ap.add_argument("--top",type=int,default=40)
    args=ap.parse_args()
    report=build_report(args.root,args.label,args.top)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        key:report[key] for key in (
            "label","complex_rules","set_filter_rules","derived_variable_rules",
            "set_filter_and_derived_variable_rules",
            "unique_set_filter_pattern_signatures",
            "unique_derived_variable_pattern_signatures",
        )
    },indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
