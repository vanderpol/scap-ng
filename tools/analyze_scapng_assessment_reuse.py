#!/usr/bin/env python3
"""Measure reusable SCAP-NG assessment semantics across converted benchmarks.

The analyzer deliberately separates:
1. exact semantic reuse: identical technical assessment behavior after removing
   source identifiers/provenance; and
2. parameterization candidates: identical semantic shape after abstracting
   literal values.

The second class is an upper-bound candidate set and MUST NOT be presented as
proven reusable automation until reviewed.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


DROP_KEYS = {
    "id",
    "comment",
    "metadata",
    "version",
    "source_object_id",
    "source_variable_id",
    "source_state_id",
    "source_test_id",
    "source_definition_id",
}


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def benchmark_arg(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("benchmark must be LABEL=PATH")
    label, raw = value.split("=", 1)
    if not label:
        raise argparse.ArgumentTypeError("benchmark label may not be empty")
    return label, Path(raw)


class AssessmentNormalizer:
    def __init__(self, assessment: dict, abstract_literals: bool = False):
        self.assessment = assessment
        self.abstract_literals = abstract_literals
        evaluate = assessment.get("evaluate") or {}
        self.nodes = {
            "object": assessment.get("collect") or {},
            "variable": assessment.get("derive") or {},
            "state": assessment.get("predicates") or {},
            "test": evaluate.get("tests") or {},
            "definition": evaluate.get("definitions") or {},
        }
        self.id_kind = {
            node_id: kind
            for kind, rows in self.nodes.items()
            for node_id in rows
        }
        self.memo: dict[str, Any] = {}

    def semantic_body(self, kind: str, body: dict) -> dict:
        if kind == "object":
            return {
                "capability": body.get("capability"),
                "source_type": body.get("source_type"),
                "source_namespace": body.get("source_namespace"),
                "query": copy.deepcopy(body.get("query", [])),
            }
        if kind == "variable":
            return {
                "source_type": body.get("source_type"),
                "datatype": body.get("datatype"),
                "semantic_ast": copy.deepcopy(body.get("semantic_ast")),
            }
        if kind == "state":
            return {
                "source_type": body.get("source_type"),
                "source_namespace": body.get("source_namespace"),
                "operator": body.get("operator", "AND"),
                "entities": copy.deepcopy(body.get("entities", [])),
            }
        if kind == "test":
            return {
                "source_type": body.get("source_type"),
                "source_namespace": body.get("source_namespace"),
                "check": body.get("check", "all"),
                "check_existence": body.get("check_existence", "at_least_one_exists"),
                "state_operator": body.get("state_operator", "AND"),
                "collections": copy.deepcopy(body.get("collections", [])),
                "predicates": copy.deepcopy(body.get("predicates", [])),
                "source_other": copy.deepcopy(body.get("source_other", [])),
            }
        if kind == "definition":
            return {
                "class": body.get("class"),
                "criteria": copy.deepcopy(body.get("criteria")),
            }
        raise ValueError(f"unknown node kind: {kind}")

    def normalize_scalar(self, value: Any, parent_key: str | None, stack: tuple[str, ...]) -> Any:
        if isinstance(value, str) and value in self.id_kind:
            return self.expand_node(value, stack)
        if self.abstract_literals and parent_key == "value":
            if value is None:
                return None
            # Preserve datatype through surrounding fields, abstract only the literal.
            return "<PARAM>"
        return value

    def normalize_value(
        self,
        value: Any,
        parent_key: str | None = None,
        stack: tuple[str, ...] = (),
    ) -> Any:
        if isinstance(value, dict):
            out = {}
            for key, child in value.items():
                if key in DROP_KEYS:
                    continue
                out[key] = self.normalize_value(child, key, stack)

            # AND/OR children are commutative in the definition criteria model.
            if (
                out.get("kind") == "boolean"
                and out.get("operator") in {"AND", "OR"}
                and isinstance(out.get("children"), list)
            ):
                out["children"] = sorted(
                    out["children"],
                    key=canonical_json,
                )
            return out

        if isinstance(value, list):
            normalized = [self.normalize_value(x, parent_key, stack) for x in value]
            # These references and predicate/entity conjunctions are order-insensitive.
            if parent_key in {"collections", "predicates", "definition_results"}:
                normalized = sorted(normalized, key=canonical_json)
            return normalized

        return self.normalize_scalar(value, parent_key, stack)

    def expand_node(self, node_id: str, stack: tuple[str, ...] = ()) -> Any:
        if node_id in self.memo:
            return copy.deepcopy(self.memo[node_id])
        kind = self.id_kind[node_id]
        if node_id in stack:
            # Valid OVAL is expected to be acyclic here; retain category if a cycle
            # appears so identifiers still do not contaminate the fingerprint.
            return {"$cycle": kind}
        body = self.nodes[kind][node_id]
        semantic = self.semantic_body(kind, body)
        expanded = {
            "$kind": kind,
            "body": self.normalize_value(semantic, stack=stack + (node_id,)),
        }
        self.memo[node_id] = expanded
        return copy.deepcopy(expanded)

    def normalized(self) -> dict:
        root_ids = ((self.assessment.get("assert") or {}).get("definition_results") or [])
        roots = [
            self.expand_node(node_id)
            for node_id in root_ids
            if node_id in self.id_kind
        ]
        roots = sorted(roots, key=canonical_json)
        return {
            "semantic_model": self.assessment.get("semantic_model"),
            "roots": roots,
        }


def assessment_fingerprints(assessment: dict) -> tuple[str, str]:
    exact = AssessmentNormalizer(assessment, abstract_literals=False).normalized()
    shape = AssessmentNormalizer(assessment, abstract_literals=True).normalized()
    return digest(exact), digest(shape)


def rule_instance(label: str, row: dict) -> dict | None:
    migration = row.get("migration") or {}
    assessment = row.get("assessment")
    if migration.get("status") == "unsupported" or not assessment:
        return None
    if assessment.get("semantic_model") != "scap-ng-generic-assessment-graph-0.1":
        return None

    exact, shape = assessment_fingerprints(assessment)
    policy = row.get("policy") or {}
    check_text=normalize_check_text(policy.get("check"))
    return {
        "benchmark": label,
        "rule_id": policy.get("id"),
        "title": policy.get("title"),
        "check_text": check_text,
        "check_text_fingerprint": digest(check_text) if check_text else None,
        "migration_status": migration.get("status"),
        "exact_fingerprint": exact,
        "shape_fingerprint": shape,
    }


def group_instances(instances: list[dict], key: str) -> list[dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in instances:
        grouped[row[key]].append(row)

    out = []
    for fingerprint, rows in grouped.items():
        benchmarks = sorted({x["benchmark"] for x in rows})
        out.append({
            "fingerprint": fingerprint,
            "instance_count": len(rows),
            "benchmark_count": len(benchmarks),
            "benchmarks": benchmarks,
            "cross_benchmark": len(benchmarks) > 1,
            "instances": sorted(
                rows,
                key=lambda x: (
                    x["benchmark"],
                    x.get("rule_id") or "",
                ),
            ),
        })
    return sorted(
        out,
        key=lambda x: (
            -x["instance_count"],
            -x["benchmark_count"],
            x["fingerprint"],
        ),
    )


def normalize_check_text(value: str | None) -> str | None:
    if not value:
        return None
    # Check Text comparisons intentionally normalize presentation whitespace only.
    # Wording, punctuation, commands, paths, thresholds, and other content remain
    # significant so this does not become a fuzzy semantic claim.
    normalized=" ".join(value.split())
    return normalized or None


def alignment_groups(
    policy_instances: list[dict],
    assessment_instances: list[dict],
) -> tuple[list[dict], list[dict], list[dict]]:
    by_check: dict[str,list[dict]]=defaultdict(list)
    by_oval: dict[str,list[dict]]=defaultdict(list)
    for row in policy_instances:
        check_fp=row.get("check_text_fingerprint")
        if check_fp:
            by_check[check_fp].append(row)
    for row in assessment_instances:
        by_oval[row["exact_fingerprint"]].append(row)

    def cross(groups: dict[str,list[dict]], fingerprint_kind: str) -> list[dict]:
        out=[]
        for fp,rows in groups.items():
            benchmarks=sorted({x["benchmark"] for x in rows})
            if len(benchmarks)<2:
                continue
            out.append({
                "fingerprint":fp,
                "fingerprint_kind":fingerprint_kind,
                "instance_count":len(rows),
                "benchmark_count":len(benchmarks),
                "benchmarks":benchmarks,
                "instances":sorted(
                    rows,key=lambda x:(x["benchmark"],x.get("rule_id") or "")
                ),
            })
        return sorted(
            out,
            key=lambda x:(-x["instance_count"],-x["benchmark_count"],x["fingerprint"]),
        )

    check_groups=cross(by_check,"normalized_check_text")
    oval_groups=cross(by_oval,"equivalent_oval_semantics")

    # Build pair-level evidence so a review can see how rules were aligned.
    pair_evidence={}
    def add_pairs(groups: list[dict], basis: str):
        for group in groups:
            rows=group["instances"]
            for i,left in enumerate(rows):
                for right in rows[i+1:]:
                    if left["benchmark"]==right["benchmark"]:
                        continue
                    ordered=sorted(
                        [left,right],
                        key=lambda x:(x["benchmark"],x.get("rule_id") or ""),
                    )
                    key=(
                        ordered[0]["benchmark"],ordered[0].get("rule_id"),
                        ordered[1]["benchmark"],ordered[1].get("rule_id"),
                    )
                    item=pair_evidence.setdefault(key,{
                        "left":{
                            "benchmark":ordered[0]["benchmark"],
                            "rule_id":ordered[0].get("rule_id"),
                            "title":ordered[0].get("title"),
                        },
                        "right":{
                            "benchmark":ordered[1]["benchmark"],
                            "rule_id":ordered[1].get("rule_id"),
                            "title":ordered[1].get("title"),
                        },
                        "evidence":[],
                    })
                    if basis not in item["evidence"]:
                        item["evidence"].append(basis)

    add_pairs(check_groups,"same_normalized_check_text")
    add_pairs(oval_groups,"equivalent_oval_semantics")
    pairs=sorted(
        pair_evidence.values(),
        key=lambda x:(
            x["left"]["benchmark"],x["right"]["benchmark"],
            x["left"].get("rule_id") or "",x["right"].get("rule_id") or "",
        ),
    )
    return check_groups,oval_groups,pairs


def pair_summaries(
    benchmark_summaries: list[dict],
    instances: list[dict],
    alignment_pairs: list[dict],
    exact_groups: list[dict],
) -> list[dict]:
    totals={
        row["benchmark"]:row["generic_automated_assessments"]
        for row in benchmark_summaries
    }
    labels=sorted(totals)
    out=[]
    for i,left in enumerate(labels):
        for right in labels[i+1:]:
            pair_name={left,right}
            pairs=[
                x for x in alignment_pairs
                if {x["left"]["benchmark"],x["right"]["benchmark"]}==pair_name
            ]
            same_check=[x for x in pairs if "same_normalized_check_text" in x["evidence"]]
            same_oval=[x for x in pairs if "equivalent_oval_semantics" in x["evidence"]]
            both=[x for x in pairs if len(x["evidence"])==2]

            left_reused=set()
            right_reused=set()
            exact_pair_groups=0
            exact_pair_instances=0
            duplicate_units_avoided=0
            for group in exact_groups:
                members=[
                    x for x in group["instances"]
                    if x["benchmark"] in pair_name
                ]
                benches={x["benchmark"] for x in members}
                if benches!=pair_name:
                    continue
                exact_pair_groups+=1
                exact_pair_instances+=len(members)
                duplicate_units_avoided+=len(members)-1
                for member in members:
                    if member["benchmark"]==left:
                        left_reused.add(member["rule_id"])
                    elif member["benchmark"]==right:
                        right_reused.add(member["rule_id"])

            out.append({
                "left":left,
                "right":right,
                "left_generic_automated_assessments":totals[left],
                "right_generic_automated_assessments":totals[right],
                "aligned_rule_pairs_union":len(pairs),
                "same_check_text_rule_pairs":len(same_check),
                "equivalent_oval_rule_pairs":len(same_oval),
                "alignment_pairs_supported_by_both":len(both),
                "exact_reuse_groups":exact_pair_groups,
                "exact_reuse_instances":exact_pair_instances,
                "duplicate_assessment_definitions_avoided":duplicate_units_avoided,
                "left_rules_reusing_exact_assessment":len(left_reused),
                "right_rules_reusing_exact_assessment":len(right_reused),
                "left_exact_reuse_coverage_pct":pct(len(left_reused),totals[left]),
                "right_exact_reuse_coverage_pct":pct(len(right_reused),totals[right]),
            })
    return out


def pct(numerator: int, denominator: int) -> float:
    return round(100.0 * numerator / denominator, 2) if denominator else 0.0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "benchmarks",
        nargs="+",
        type=benchmark_arg,
        help="LABEL=path/to/canonical-benchmark.json",
    )
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    instances = []
    policy_instances = []
    benchmark_summaries = []
    for label, path in args.benchmarks:
        doc = json.loads(path.read_text(encoding="utf-8"))
        supported = 0
        blocked = 0
        generic = 0
        for row in doc.get("rules", []):
            policy=row.get("policy") or {}
            check_text=normalize_check_text(policy.get("check"))
            policy_instances.append({
                "benchmark":label,
                "rule_id":policy.get("id"),
                "title":policy.get("title"),
                "check_text":check_text,
                "check_text_fingerprint":digest(check_text) if check_text else None,
            })

            migration = row.get("migration") or {}
            if migration.get("status") == "unsupported":
                blocked += 1
                continue
            supported += 1
            instance = rule_instance(label, row)
            if instance:
                generic += 1
                instances.append(instance)
        benchmark_summaries.append({
            "benchmark": label,
            "path": path.as_posix(),
            "rules": len(doc.get("rules", [])),
            "supported_rules": supported,
            "blocked_rules": blocked,
            "generic_automated_assessments": generic,
        })

    exact_groups = group_instances(instances, "exact_fingerprint")
    shape_groups = group_instances(instances, "shape_fingerprint")
    check_alignment_groups,oval_alignment_groups,alignment_pairs=alignment_groups(
        policy_instances,
        instances,
    )

    exact_unique = len(exact_groups)
    shape_unique = len(shape_groups)
    total = len(instances)
    exact_avoided = max(0, total - exact_unique)
    shape_avoided = max(0, total - shape_unique)

    exact_cross = [x for x in exact_groups if x["cross_benchmark"]]
    pair_summary=pair_summaries(
        benchmark_summaries,
        instances,
        alignment_pairs,
        exact_cross,
    )
    shape_cross = [
        x for x in shape_groups
        if x["cross_benchmark"]
        and len({i["exact_fingerprint"] for i in x["instances"]}) > 1
    ]

    result = {
        "format": "scap-ng-assessment-reuse-analysis-0.1",
        "classification": {
            "rule_alignment": (
                "Rules are treated as corresponding when either normalized XCCDF Check "
                "Text is identical or their complete normalized OVAL assessment semantics "
                "are equivalent. OVAL equivalence compares the full logic graph, not merely "
                "test-family names."
            ),
            "exact_reuse": (
                "Same normalized technical assessment semantics after removing "
                "source identifiers, provenance, comments, metadata, and versions."
            ),
            "parameterization_candidate": (
                "Same normalized semantic shape after literal values are abstracted. "
                "This is an upper-bound candidate classification and requires human/"
                "conformance review before claiming reusable automation."
            ),
        },
        "benchmarks": benchmark_summaries,
        "summary": {
            "benchmarks": len(benchmark_summaries),
            "generic_automated_assessment_instances": total,
            "exact_unique_assessments": exact_unique,
            "exact_duplicate_instances_avoided": exact_avoided,
            "exact_maintenance_unit_reduction_pct": pct(exact_avoided, total),
            "exact_cross_benchmark_reuse_groups": len(exact_cross),
            "exact_cross_benchmark_instances": sum(x["instance_count"] for x in exact_cross),
            "shape_unique_assessments": shape_unique,
            "parameterization_candidate_instances_avoided_upper_bound": shape_avoided,
            "parameterization_candidate_reduction_pct_upper_bound": pct(shape_avoided, total),
            "cross_benchmark_parameterization_candidate_groups": len(shape_cross),
            "cross_benchmark_same_check_text_groups": len(check_alignment_groups),
            "cross_benchmark_equivalent_oval_groups": len(oval_alignment_groups),
            "cross_benchmark_aligned_rule_pairs": len(alignment_pairs),
            "aligned_pairs_by_evidence": {
                "same_check_text_only": sum(
                    1 for x in alignment_pairs
                    if x["evidence"]==["same_normalized_check_text"]
                ),
                "equivalent_oval_only": sum(
                    1 for x in alignment_pairs
                    if x["evidence"]==["equivalent_oval_semantics"]
                ),
                "both": sum(1 for x in alignment_pairs if len(x["evidence"])==2),
            },
        },
        "benchmark_pair_summary": pair_summary,
        "maintenance_cost_model": {
            "baseline_definition_units": total,
            "exact_reuse_definition_units": exact_unique,
            "exact_definition_units_avoided": exact_avoided,
            "parameterized_candidate_definition_units_upper_bound": shape_unique,
            "parameterized_candidate_units_avoided_upper_bound": shape_avoided,
            "formulas": {
                "one_time_migration_review_hours_avoided": (
                    "exact_definition_units_avoided * average_review_hours_per_assessment"
                ),
                "annual_maintenance_hours_avoided": (
                    "exact_definition_units_avoided * average_change_events_per_year "
                    "* average_review_hours_per_change"
                ),
                "annual_labor_cost_avoided": (
                    "annual_maintenance_hours_avoided * loaded_hourly_labor_rate"
                ),
            },
            "note": (
                "No labor-rate or effort assumptions are embedded. Apply organization-"
                "specific values to measured units rather than presenting speculative "
                "dollar savings as observed fact."
            ),
        },
        "rule_alignment": {
            "cross_benchmark_same_check_text_groups": check_alignment_groups,
            "cross_benchmark_equivalent_oval_groups": oval_alignment_groups,
            "aligned_rule_pairs": alignment_pairs,
        },
        "exact_reuse_groups": [x for x in exact_groups if x["instance_count"] > 1],
        "cross_benchmark_exact_reuse_groups": exact_cross,
        "cross_benchmark_parameterization_candidates": shape_cross,
        "policy_instances": sorted(
            policy_instances,
            key=lambda x: (x["benchmark"], x.get("rule_id") or ""),
        ),
        "instances": sorted(
            instances,
            key=lambda x: (x["benchmark"], x.get("rule_id") or ""),
        ),
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
