#!/usr/bin/env python3
"""Normalize a generated SCAP-NG authoring corpus by proven Assessment equivalence.

This utility operates on current native authoring trees.  It automatically
promotes only exact semantic duplicates.  Near-duplicate/parameterizable
Assessment shapes are reported for human review and are never merged.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import shutil
from difflib import SequenceMatcher
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml

ROOT_NONSEMANTIC_ASSESSMENT_KEYS = {
    "id",
    "version",
    "assessment_title",
    "provenance",
    "migration_provenance",
    "reuse_provenance",
}
RECURSIVE_NONSEMANTIC_KEYS = {
    "source_id",
    "source_definition_id",
    "source_test_id",
    "source_object_id",
    "source_state_id",
    "source_variable_id",
}


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def load_yaml(path: Path) -> dict:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected mapping")
    return value


def dump_yaml(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(value, sort_keys=False, allow_unicode=True, width=120),
        encoding="utf-8",
    )


def normalize_value(
    value: Any,
    *,
    abstract_literals: bool = False,
    parent: str | None = None,
    depth: int = 0,
) -> Any:
    if isinstance(value, dict):
        out = {}
        for key, child in value.items():
            if key in RECURSIVE_NONSEMANTIC_KEYS:
                continue
            if depth == 0 and key in ROOT_NONSEMANTIC_ASSESSMENT_KEYS:
                continue
            if abstract_literals and key == "value":
                # Keep surrounding datatype/operation/cardinality semantics while
                # abstracting only literal values for manual-review candidates.
                out[key] = None if child is None else "<PARAM>"
            else:
                out[key] = normalize_value(
                    child,
                    abstract_literals=abstract_literals,
                    parent=key,
                    depth=depth + 1,
                )
        return out
    if isinstance(value, list):
        return [
            normalize_value(
                x,
                abstract_literals=abstract_literals,
                parent=parent,
                depth=depth + 1,
            )
            for x in value
        ]
    return value


def assessment_fingerprints(path: Path) -> tuple[str, str]:
    doc = load_yaml(path)
    assessment = copy.deepcopy(doc.get("assessment") or {})
    exact = normalize_value(assessment)
    shape = normalize_value(assessment, abstract_literals=True)
    return digest(exact), digest(shape)


def safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("_") or "unnamed"


def rule_refs(rule_path: Path) -> list[tuple[str, Path]]:
    doc = load_yaml(rule_path)
    rule = doc.get("rule") or {}
    out = []
    for selector, choice in (rule.get("assessment_choices") or {}).items():
        if not isinstance(choice, dict) or not isinstance(choice.get("assessment"), str):
            continue
        target = (rule_path.parent / choice["assessment"]).resolve()
        out.append((selector, target))
    return out


def collect_corpus(root: Path) -> tuple[list[dict], dict[Path, list[dict]]]:
    benchmarks = []
    uses: dict[Path, list[dict]] = defaultdict(list)
    for benchmark_path in sorted(root.rglob("benchmark.yaml")):
        benchmark_dir = benchmark_path.parent
        rules_dir = benchmark_dir / "rules"
        assessments_dir = benchmark_dir / "assessments"
        if not rules_dir.is_dir() or not assessments_dir.is_dir():
            continue
        benchmark_doc = load_yaml(benchmark_path).get("benchmark") or {}
        label = benchmark_dir.name
        rules = []
        for rule_path in sorted(rules_dir.glob("*.yaml")):
            rule = load_yaml(rule_path).get("rule") or {}
            row = {
                "benchmark": label,
                "benchmark_id": benchmark_doc.get("id"),
                "rule_id": rule.get("id"),
                "title": rule.get("title"),
                "rule_path": rule_path,
            }
            rules.append(row)
            for selector, target in rule_refs(rule_path):
                if target.exists():
                    uses[target].append({**row, "selector": selector})
        benchmarks.append(
            {
                "label": label,
                "benchmark_id": benchmark_doc.get("id"),
                "path": benchmark_dir,
                "rules": rules,
            }
        )
    return benchmarks, uses



def report_consumer(consumer: dict, source: Path) -> dict:
    return {
        "benchmark": consumer.get("benchmark"),
        "benchmark_id": consumer.get("benchmark_id"),
        "rule_id": consumer.get("rule_id"),
        "title": consumer.get("title"),
        "selector": consumer.get("selector"),
        "rule_path": consumer["rule_path"].relative_to(source).as_posix(),
    }

def rewrite_rules(
    output_root: Path,
    input_root: Path,
    replacements: dict[Path, Path],
    uses: dict[Path, list[dict]],
) -> int:
    rewritten_paths=set()
    for original_target, shared_target in replacements.items():
        by_rule: dict[Path, list[str]] = defaultdict(list)
        for consumer in uses.get(original_target, []):
            by_rule[consumer["rule_path"]].append(consumer["selector"])
        for rule_path, selectors in by_rule.items():
            out_rule = output_root / rule_path.relative_to(input_root)
            doc = load_yaml(out_rule)
            choices = (doc.get("rule") or {}).get("assessment_choices") or {}
            rel = Path(os.path.relpath(shared_target, out_rule.parent)).as_posix()
            changed = False
            for selector in selectors:
                if selector in choices and choices[selector].get("assessment") != rel:
                    choices[selector]["assessment"] = rel
                    changed = True
            if changed:
                dump_yaml(out_rule, doc)
                rewritten_paths.add(out_rule)
    return len(rewritten_paths)



def _tokens(value: str | None) -> list[str]:
    if not value:
        return []
    return re.findall(r"[a-z0-9]+", value.lower())


def _normalized_title(value: str | None) -> str:
    return " ".join(_tokens(value))


def near_rule_candidates(benchmarks: list[dict], *, limit: int = 500) -> list[dict]:
    """Find cross-benchmark Rule text candidates for manual overlap review.

    This is advisory only.  It intentionally does not claim policy equivalence.
    Candidate blocking uses title token trigrams so the corpus scan stays bounded.
    """
    rules=[]
    for benchmark in benchmarks:
        for row in benchmark["rules"]:
            doc=load_yaml(row["rule_path"])
            rule=doc.get("rule") or {}
            title=rule.get("title") or ""
            tokens=_tokens(title)
            rules.append({
                "benchmark":row["benchmark"],
                "benchmark_id":row.get("benchmark_id"),
                "rule_id":row.get("rule_id"),
                "title":title,
                "discussion":rule.get("discussion") or "",
                "remediation":((rule.get("remediation") or {}).get("guidance") or ""),
                "identifiers":rule.get("identifiers") or [],
                "tokens":tokens,
                "normalized_title":" ".join(tokens),
            })

    inverted: dict[tuple[str,...], list[int]] = defaultdict(list)
    for idx,row in enumerate(rules):
        toks=row["tokens"]
        shingles={tuple(toks[i:i+3]) for i in range(max(0,len(toks)-2))}
        if not shingles and toks:
            shingles={tuple(toks)}
        for shingle in shingles:
            inverted[shingle].append(idx)

    candidates=set()
    for ids in inverted.values():
        # Avoid pathological generic shingles while retaining useful overlap.
        if len(ids)>200:
            continue
        for pos,left in enumerate(ids):
            for right in ids[pos+1:]:
                if rules[left]["benchmark"]==rules[right]["benchmark"]:
                    continue
                candidates.add((min(left,right),max(left,right)))

    out=[]
    for left_idx,right_idx in candidates:
        left,right=rules[left_idx],rules[right_idx]
        lt=set(left["tokens"]); rt=set(right["tokens"])
        union=lt|rt
        jaccard=(len(lt&rt)/len(union)) if union else 0.0
        title_ratio=SequenceMatcher(None,left["normalized_title"],right["normalized_title"]).ratio()
        discussion_ratio=SequenceMatcher(
            None,
            " ".join(_tokens(left["discussion"]))[:4000],
            " ".join(_tokens(right["discussion"]))[:4000],
        ).ratio()
        score=0.55*title_ratio+0.30*jaccard+0.15*discussion_ratio
        if score < 0.62:
            continue
        left_ids={(x.get("scheme"),x.get("value")) for x in left["identifiers"] if isinstance(x,dict)}
        right_ids={(x.get("scheme"),x.get("value")) for x in right["identifiers"] if isinstance(x,dict)}
        shared_ids=sorted(
            [{"scheme":s,"value":v} for s,v in left_ids & right_ids],
            key=lambda x:(x["scheme"] or "",x["value"] or ""),
        )
        out.append({
            "similarity_score":round(score,4),
            "title_similarity":round(title_ratio,4),
            "title_token_jaccard":round(jaccard,4),
            "discussion_similarity":round(discussion_ratio,4),
            "shared_identifiers":shared_ids,
            "left":{k:left[k] for k in ("benchmark","benchmark_id","rule_id","title")},
            "right":{k:right[k] for k in ("benchmark","benchmark_id","rule_id","title")},
            "classification":"manual_overlap_review_only",
        })
    out.sort(key=lambda x:(-x["similarity_score"],x["left"]["benchmark"],x["left"]["rule_id"] or ""))
    return out[:limit]

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("corpus_root", type=Path)
    ap.add_argument("--output-root", type=Path, required=True)
    ap.add_argument("--report", type=Path, required=True)
    ap.add_argument("--top-near", type=int, default=250)
    args = ap.parse_args()

    source = args.corpus_root.resolve()
    output = args.output_root.resolve()
    if output.exists():
        shutil.rmtree(output)
    shutil.copytree(source, output)

    benchmarks, uses = collect_corpus(source)
    rows = []
    for path, consumers in sorted(uses.items(), key=lambda x: x[0].as_posix()):
        exact, shape = assessment_fingerprints(path)
        rows.append(
            {
                "path": path,
                "exact": exact,
                "shape": shape,
                "consumers": consumers,
            }
        )

    exact_groups: dict[str, list[dict]] = defaultdict(list)
    shape_groups: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        exact_groups[row["exact"]].append(row)
        shape_groups[row["shape"]].append(row)

    duplicate_groups = [
        group for group in exact_groups.values()
        if len(group) > 1
    ]

    shared_dir = output / "shared" / "assessments"
    replacements: dict[Path, Path] = {}
    exact_report = []
    duplicate_instances_avoided = 0

    for group in sorted(
        duplicate_groups,
        key=lambda g: (-len(g), g[0]["exact"]),
    ):
        fingerprint = group[0]["exact"]
        shared_id = f"ng.shared.{fingerprint[:24]}"
        shared_path = shared_dir / f"{safe_name(shared_id)}.assessment.yaml"

        representative = load_yaml(group[0]["path"])
        assessment = copy.deepcopy(representative.get("assessment") or {})
        assessment["id"] = shared_id
        assessment["reuse_provenance"] = [
            {
                "source": str(row["path"].relative_to(source)),
                "consumers": [
                    {
                        "benchmark": c["benchmark"],
                        "rule_id": c["rule_id"],
                        "selector": c["selector"],
                    }
                    for c in row["consumers"]
                ],
            }
            for row in group
        ]
        dump_yaml(shared_path, {"assessment": assessment})

        members = []
        for row in group:
            replacements[row["path"]] = shared_path
            members.append(
                {
                    "source": str(row["path"].relative_to(source)),
                    "consumers": [
                        report_consumer(consumer, source)
                        for consumer in row["consumers"]
                    ],
                }
            )
            duplicate_instances_avoided += 1
        duplicate_instances_avoided -= 1
        exact_report.append(
            {
                "fingerprint": fingerprint,
                "shared_assessment": str(shared_path.relative_to(output)),
                "instance_count": len(group),
                "members": members,
            }
        )

    rewritten_rule_files = rewrite_rules(output, source, replacements, uses)

    # Remove promoted local duplicates after references in the copied tree point
    # to the shared canonical Assessment.
    for source_path in replacements:
        copied = output / source_path.relative_to(source)
        if copied.exists():
            copied.unlink()

    # Near duplicates are same semantic shape after only literal values are
    # abstracted, but have >1 exact semantic fingerprint.  They are advisory.
    near_groups = []
    for shape, group in shape_groups.items():
        exacts = {row["exact"] for row in group}
        if len(group) < 2 or len(exacts) < 2:
            continue
        consumers = [
            {
                "source": str(row["path"].relative_to(source)),
                "exact_fingerprint": row["exact"],
                "consumers": [
                    report_consumer(consumer, source)
                    for consumer in row["consumers"]
                ],
            }
            for row in group
        ]
        benchmark_count = len(
            {
                c["benchmark"]
                for row in group
                for c in row["consumers"]
            }
        )
        near_groups.append(
            {
                "shape_fingerprint": shape,
                "assessment_instances": len(group),
                "exact_variants": len(exacts),
                "benchmark_count": benchmark_count,
                "members": consumers,
            }
        )
    near_groups.sort(
        key=lambda x: (
            -x["assessment_instances"],
            -x["benchmark_count"],
            x["shape_fingerprint"],
        )
    )
    rule_candidates = near_rule_candidates(benchmarks, limit=args.top_near)

    before_assessment_instances = len(rows)
    after_assessment_definitions = before_assessment_instances - duplicate_instances_avoided
    reduction_pct = (
        round(100.0 * duplicate_instances_avoided / before_assessment_instances, 2)
        if before_assessment_instances else 0.0
    )

    report = {
        "format": "scap-ng-repository-normalizer-report-0.1",
        "mode": "exact-rewrite-plus-near-duplicate-review",
        "summary": {
            "benchmarks": len(benchmarks),
            "rules": sum(len(x["rules"]) for x in benchmarks),
            "referenced_assessment_instances_before": before_assessment_instances,
            "assessment_definitions_after_exact_normalization": after_assessment_definitions,
            "exact_duplicate_groups": len(exact_report),
            "duplicate_assessment_definitions_avoided": duplicate_instances_avoided,
            "exact_definition_reduction_pct": reduction_pct,
            "rule_files_rewritten": rewritten_rule_files,
            "near_duplicate_review_groups": len(near_groups),
            "near_duplicate_rule_candidates_reported": len(rule_candidates),
        },
        "exact_groups": exact_report,
        "near_duplicate_review_groups": near_groups[: args.top_near],
        "near_duplicate_groups_total": len(near_groups),
        "near_duplicate_rule_candidates": rule_candidates,
        "safety": {
            "automatic_merge_basis": "exact normalized Assessment semantics only",
            "near_duplicates_merged": False,
            "literal_abstraction_used_only_for_review_candidates": True,
        },
    }

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
