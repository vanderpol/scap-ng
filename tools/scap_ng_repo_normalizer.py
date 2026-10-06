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


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def readable_slug(value: str | None, *, maximum: int = 72) -> str:
    """Return a short deterministic human-readable filename/id component."""
    tokens = re.findall(r"[a-z0-9]+", (value or "").lower())
    slug = "-".join(tokens).strip("-")
    if len(slug) > maximum:
        slug = slug[:maximum].rstrip("-")
    return slug or "shared-assessment"


def neutralize_shared_title(value: str, benchmark_labels: set[str]) -> str:
    """Remove source-benchmark branding from a cross-benchmark shared filename label.

    This changes only the generated shared filename/ID. Authored Assessment and
    Test titles remain unchanged. A cross-benchmark shared filename should describe
    the reusable check rather than whichever source benchmark supplied the title.
    """
    text = value.strip()
    labels = {x.lower() for x in benchmark_labels}
    if len(labels) < 2:
        return text

    windows_family = all("windows" in x for x in labels)
    linux_family = all(("linux" in x) or x.startswith("rhel") for x in labels)

    if windows_family:
        text = re.sub(r"^\s*WN\d+(?:-[A-Z]{2})?-\d+\s*[-:]?\s*", "", text, flags=re.I)
        text = re.sub(r"\bWindows\s+Server\s+20\d{2}\b", "Windows", text, flags=re.I)
        text = re.sub(r"\bWindows\s+(?:10|11)\b", "Windows", text, flags=re.I)

    if linux_family:
        text = re.sub(r"\bRed\s+Hat\s+Enterprise\s+Linux\s+\d+\b", "Linux", text, flags=re.I)
        text = re.sub(r"\bRHEL\s*\d+\b", "Linux", text, flags=re.I)
        text = re.sub(r"\bOracle\s+Linux\s+\d+\b", "Linux", text, flags=re.I)

    return re.sub(r"\s+", " ", text).strip()


def shared_assessment_base_name(assessment: dict, benchmark_labels: set[str] | None = None) -> str:
    """Derive a meaningful shared name from semantic/native authoring text.

    Prefer a single Test title because Test titles participate in the exact
    semantic fingerprint. Fall back to the Assessment title for manual or
    title-only content, then capability names, and finally a generic label.
    Cross-benchmark source branding is removed from the filename label only.
    """
    benchmark_labels = benchmark_labels or set()
    tests = assessment.get("tests") or {}
    test_titles = sorted({
        str(row.get("test_title")).strip()
        for row in tests.values()
        if isinstance(row, dict) and row.get("test_title")
    }) if isinstance(tests, dict) else []
    if len(test_titles) == 1:
        return readable_slug(neutralize_shared_title(test_titles[0], benchmark_labels))

    assessment_title = assessment.get("assessment_title")
    if isinstance(assessment_title, str) and assessment_title.strip():
        return readable_slug(neutralize_shared_title(assessment_title, benchmark_labels))

    if test_titles:
        return readable_slug(neutralize_shared_title(test_titles[0], benchmark_labels))

    capabilities = sorted({
        str(row.get("capability")).strip()
        for registry in ("tests", "objects", "states")
        for row in (assessment.get(registry) or {}).values()
        if isinstance(row, dict) and row.get("capability")
    })
    if capabilities:
        return readable_slug("-".join(capabilities))

    return "shared-assessment"

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


def applicability_refs(applicability_path: Path) -> list[tuple[str, Path]]:
    """Return condition -> Assessment references from a native applicability catalog."""
    doc = load_yaml(applicability_path)
    root = doc.get("applicability") or {}
    conditions = root.get("conditions") or {}
    out = []
    if isinstance(conditions, dict):
        iterator = conditions.items()
    elif isinstance(conditions, list):
        iterator = (
            (str(index), row)
            for index, row in enumerate(conditions)
        )
    else:
        raise ValueError(f"{applicability_path}: applicability conditions must be mapping or list")
    for condition_id, row in iterator:
        if not isinstance(row, dict) or not isinstance(row.get("assessment"), str):
            continue
        target = (applicability_path.parent / row["assessment"]).resolve()
        out.append((str(condition_id), target))
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
                    uses[target].append({
                        **row,
                        "consumer_kind": "rule",
                        "selector": selector,
                    })

        applicability_path = benchmark_dir / "applicability.yaml"
        if applicability_path.is_file():
            for condition_id, target in applicability_refs(applicability_path):
                if target.exists():
                    uses[target].append({
                        "consumer_kind": "applicability",
                        "benchmark": label,
                        "benchmark_id": benchmark_doc.get("id"),
                        "condition_id": condition_id,
                        "applicability_path": applicability_path,
                    })

        benchmarks.append(
            {
                "label": label,
                "benchmark_id": benchmark_doc.get("id"),
                "path": benchmark_dir,
                "rules": rules,
            }
        )
    return benchmarks, uses




def validate_normalized_repository(root: Path) -> dict:
    """Validate rewritten Rule references and logical Assessment-ID consistency."""
    unresolved=[]
    assessment_ids: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    assessment_files=0

    for path in sorted(root.rglob("*.assessment.yaml")):
        doc=load_yaml(path)
        assessment=doc.get("assessment")
        if not isinstance(assessment,dict):
            continue
        assessment_files += 1
        assessment_id=assessment.get("id")
        if isinstance(assessment_id,str) and assessment_id:
            normalized=normalize_value(copy.deepcopy(assessment))
            fingerprint=digest(normalized)
            assessment_ids[assessment_id][fingerprint].append(
                path.relative_to(root).as_posix()
            )

    for rule_path in sorted(root.rglob("*.rule.yaml")):
        try:
            refs=rule_refs(rule_path)
        except Exception as exc:
            unresolved.append({
                "consumer_kind":"rule",
                "source":rule_path.relative_to(root).as_posix(),
                "error":str(exc),
            })
            continue
        for selector,target in refs:
            if not target.exists():
                unresolved.append({
                    "consumer_kind":"rule",
                    "source":rule_path.relative_to(root).as_posix(),
                    "selector":selector,
                    "missing_assessment":str(target),
                })

    for applicability_path in sorted(root.rglob("applicability.yaml")):
        try:
            refs=applicability_refs(applicability_path)
        except Exception as exc:
            unresolved.append({
                "consumer_kind":"applicability",
                "source":applicability_path.relative_to(root).as_posix(),
                "error":str(exc),
            })
            continue
        for condition_id,target in refs:
            if not target.exists():
                unresolved.append({
                    "consumer_kind":"applicability",
                    "source":applicability_path.relative_to(root).as_posix(),
                    "condition_id":condition_id,
                    "missing_assessment":str(target),
                })

    identity_conflicts={
        assessment_id: {
            fingerprint: sorted(paths)
            for fingerprint,paths in sorted(variants.items())
        }
        for assessment_id,variants in sorted(assessment_ids.items())
        if len(variants)>1
    }
    if unresolved or identity_conflicts:
        details={
            "unresolved_rule_references": unresolved,
            "assessment_identity_conflicts": identity_conflicts,
        }
        raise ValueError(
            "normalized repository validation failed: "
            f"{len(unresolved)} unresolved reference(s), "
            f"{len(identity_conflicts)} Assessment identity conflict(s)\n"
            + json.dumps(details, indent=2, sort_keys=True)
        )
    return {
        "assessment_files":assessment_files,
        "assessment_ids":len(assessment_ids),
        "unresolved_rule_references":0,
        "assessment_identity_conflicts":0,
    }

def report_consumer(consumer: dict, source: Path) -> dict:
    row = {
        "consumer_kind": consumer.get("consumer_kind"),
        "benchmark": consumer.get("benchmark"),
        "benchmark_id": consumer.get("benchmark_id"),
    }
    if consumer.get("consumer_kind") == "applicability":
        row.update({
            "condition_id": consumer.get("condition_id"),
            "applicability_path": consumer["applicability_path"].relative_to(source).as_posix(),
        })
    else:
        row.update({
            "rule_id": consumer.get("rule_id"),
            "title": consumer.get("title"),
            "selector": consumer.get("selector"),
            "rule_path": consumer["rule_path"].relative_to(source).as_posix(),
        })
    return row

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
            if consumer.get("consumer_kind") != "rule":
                continue
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


def rewrite_applicability(
    output_root: Path,
    input_root: Path,
    replacements: dict[Path, Path],
    uses: dict[Path, list[dict]],
) -> int:
    rewritten_paths=set()
    for original_target, shared_target in replacements.items():
        by_catalog: dict[Path, list[str]] = defaultdict(list)
        for consumer in uses.get(original_target, []):
            if consumer.get("consumer_kind") != "applicability":
                continue
            by_catalog[consumer["applicability_path"]].append(consumer["condition_id"])
        for applicability_path, condition_ids in by_catalog.items():
            out_path = output_root / applicability_path.relative_to(input_root)
            doc = load_yaml(out_path)
            conditions = (doc.get("applicability") or {}).get("conditions") or {}
            rel = Path(os.path.relpath(shared_target, out_path.parent)).as_posix()
            changed=False
            if isinstance(conditions, dict):
                for condition_id in condition_ids:
                    row=conditions.get(condition_id)
                    if isinstance(row,dict) and row.get("assessment") != rel:
                        row["assessment"]=rel
                        changed=True
            elif isinstance(conditions, list):
                for condition_id in condition_ids:
                    try:
                        row=conditions[int(condition_id)]
                    except (ValueError,IndexError):
                        continue
                    if isinstance(row,dict) and row.get("assessment") != rel:
                        row["assessment"]=rel
                        changed=True
            if changed:
                dump_yaml(out_path,doc)
                rewritten_paths.add(out_path)
    return len(rewritten_paths)




def semantic_differences(left: Any, right: Any, path: str = "$", limit: int = 20) -> list[dict]:
    """Return bounded, human-reviewable semantic differences."""
    out=[]
    def walk(a,b,p):
        if len(out)>=limit:
            return
        if type(a) is not type(b):
            out.append({"path":p,"left":a,"right":b,"kind":"type_or_value"})
            return
        if isinstance(a,dict):
            for key in sorted(set(a)|set(b)):
                child=f"{p}.{key}"
                if key not in a:
                    out.append({"path":child,"left":None,"right":b[key],"kind":"right_only"})
                elif key not in b:
                    out.append({"path":child,"left":a[key],"right":None,"kind":"left_only"})
                else:
                    walk(a[key],b[key],child)
                if len(out)>=limit:
                    return
        elif isinstance(a,list):
            if len(a)!=len(b):
                out.append({"path":p+".length","left":len(a),"right":len(b),"kind":"length"})
            for i,(av,bv) in enumerate(zip(a,b)):
                walk(av,bv,f"{p}[{i}]")
                if len(out)>=limit:
                    return
        elif a!=b:
            out.append({"path":p,"left":a,"right":b,"kind":"value"})
    walk(left,right,path)
    return out


def _tokens(value: str | None) -> list[str]:
    if not value:
        return []
    return re.findall(r"[a-z0-9]+", value.lower())


def _normalized_title(value: str | None) -> str:
    return " ".join(_tokens(value))


def near_rule_candidates(benchmarks: list[dict], *, limit: int | None = None) -> list[dict]:
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

    # Count shared title trigrams first.  This avoids running expensive fuzzy
    # comparisons over the combinatorial set produced by generic STIG wording.
    pair_hits: dict[tuple[int,int], int] = defaultdict(int)
    for ids in inverted.values():
        # Very common shingles ("must be configured", etc.) are poor blockers.
        if len(ids)>80:
            continue
        for pos,left in enumerate(ids):
            for right in ids[pos+1:]:
                if rules[left]["benchmark"]==rules[right]["benchmark"]:
                    continue
                pair=(min(left,right),max(left,right))
                pair_hits[pair]+=1

    out=[]
    for (left_idx,right_idx), shared_trigrams in pair_hits.items():
        left,right=rules[left_idx],rules[right_idx]
        lt=set(left["tokens"]); rt=set(right["tokens"])
        union=lt|rt
        jaccard=(len(lt&rt)/len(union)) if union else 0.0
        # Require meaningful cheap token overlap before SequenceMatcher.
        # One shared trigram alone is intentionally insufficient for long titles.
        if jaccard < 0.40 and shared_trigrams < 2:
            continue
        title_ratio=SequenceMatcher(
            None,left["normalized_title"],right["normalized_title"],autojunk=False
        ).ratio()
        if title_ratio < 0.58 and jaccard < 0.50:
            continue
        left_disc=set(_tokens(left["discussion"]))
        right_disc=set(_tokens(right["discussion"]))
        disc_union=left_disc|right_disc
        discussion_ratio=(
            len(left_disc&right_disc)/len(disc_union)
            if disc_union else 0.0
        )
        score=0.55*title_ratio+0.30*jaccard+0.15*discussion_ratio
        left_ids={(x.get("scheme"),x.get("value")) for x in left["identifiers"] if isinstance(x,dict)}
        right_ids={(x.get("scheme"),x.get("value")) for x in right["identifiers"] if isinstance(x,dict)}
        shared_ids=sorted(
            [{"scheme":s,"value":v} for s,v in left_ids & right_ids],
            key=lambda x:(x["scheme"] or "",x["value"] or ""),
        )

        # A review queue should be evidence-rich, not a dump of generic STIG
        # wording.  Shared identifiers are strong evidence.  Without them,
        # require very strong title overlap plus meaningful policy-text support.
        strong_text=(
            (title_ratio >= 0.86 and jaccard >= 0.65)
            or (score >= 0.82 and discussion_ratio >= 0.45)
        )
        if not shared_ids and not strong_text:
            continue

        confidence=(
            "high"
            if shared_ids or (title_ratio >= 0.94 and jaccard >= 0.80)
            else "medium"
        )
        reasons=[]
        if shared_ids:
            reasons.append("shared_identifier")
        if title_ratio >= 0.94:
            reasons.append("near_identical_title")
        elif title_ratio >= 0.86:
            reasons.append("strong_title_similarity")
        if discussion_ratio >= 0.65:
            reasons.append("strong_discussion_similarity")
        elif discussion_ratio >= 0.45:
            reasons.append("supporting_discussion_similarity")

        distinctive_stop={
            "the","a","an","and","or","to","of","for","in","on","with",
            "must","shall","should","be","is","are","configured","configuration",
            "system","systems","server","application","ensure","only"
        }
        left_only=sorted((lt-rt)-distinctive_stop)
        right_only=sorted((rt-lt)-distinctive_stop)
        out.append({
            "similarity_score":round(score,4),
            "confidence":confidence,
            "review_reasons":reasons,
            "title_similarity":round(title_ratio,4),
            "title_token_jaccard":round(jaccard,4),
            "discussion_token_jaccard":round(discussion_ratio,4),
            "shared_title_trigrams":shared_trigrams,
            "shared_identifiers":shared_ids,
            "distinctive_title_tokens_left_only":left_only[:12],
            "distinctive_title_tokens_right_only":right_only[:12],
            "left":{k:left[k] for k in ("benchmark","benchmark_id","rule_id","title")},
            "right":{k:right[k] for k in ("benchmark","benchmark_id","rule_id","title")},
            "classification":"manual_overlap_review_only",
        })
    out.sort(key=lambda x:(0 if x["confidence"]=="high" else 1,-x["similarity_score"],x["left"]["benchmark"],x["left"]["rule_id"] or ""))
    return out if not limit else out[:limit]

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("corpus_root", type=Path)
    ap.add_argument("--rewrite", action="store_true",
                    help="Write a normalized repository copy. Default is dry-run/report-only.")
    ap.add_argument("--output-root", type=Path,
                    help="Destination for --rewrite. Required only when --rewrite is used.")
    ap.add_argument("--report", type=Path, required=True)
    ap.add_argument(
        "--change-manifest",
        type=Path,
        help="Optional standalone machine-readable rewrite/change manifest.",
    )
    ap.add_argument("--top-near", type=int, default=250,
                    help="Maximum near-duplicate Assessment groups retained")
    ap.add_argument("--max-rule-candidates", type=int, default=0,
                    help="Maximum similar-Rule candidates; 0 retains all")
    ap.add_argument(
        "--fingerprint-cache",
        type=Path,
        help="Optional persistent cache for exact/shape fingerprints of unchanged Assessment files.",
    )
    ap.add_argument(
        "--advisory",
        choices=("all","assessments","rules","none"),
        default="all",
        help="Advisory similarity analysis to run. Exact equivalence is always computed.",
    )
    args = ap.parse_args()

    source = args.corpus_root.resolve()
    if args.rewrite and args.output_root is None:
        ap.error("--output-root is required with --rewrite")
    if not args.rewrite and args.output_root is not None:
        ap.error("--output-root is only valid with --rewrite")
    destination = args.output_root.resolve() if args.output_root is not None else None
    output = None
    staging = None
    if destination is not None:
        if destination == source:
            ap.error("--output-root must differ from corpus_root")
        staging = destination.with_name(destination.name + ".normalizer-tmp")
        if staging.exists():
            shutil.rmtree(staging)
        shutil.copytree(source, staging)
        output = staging

    benchmarks, uses = collect_corpus(source)

    prior_cache = {}
    if args.fingerprint_cache is not None and args.fingerprint_cache.exists():
        loaded=json.loads(args.fingerprint_cache.read_text(encoding="utf-8"))
        if loaded.get("format")=="scap-ng-normalizer-fingerprint-cache-0.1":
            prior_cache=loaded.get("entries") or {}
    next_cache={}
    cache_hits=0
    cache_misses=0

    rows = []
    for path, consumers in sorted(uses.items(), key=lambda x: x[0].as_posix()):
        rel=path.relative_to(source).as_posix()
        source_sha=file_sha256(path)
        cached=prior_cache.get(rel)
        if (
            isinstance(cached,dict)
            and cached.get("file_sha256")==source_sha
            and isinstance(cached.get("exact"),str)
            and isinstance(cached.get("shape"),str)
        ):
            exact=cached["exact"]
            shape=cached["shape"]
            cache_hits += 1
        else:
            exact, shape = assessment_fingerprints(path)
            cache_misses += 1
        next_cache[rel]={
            "file_sha256":source_sha,
            "exact":exact,
            "shape":shape,
        }
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

    shared_rel_dir = Path("shared") / "assessments"
    shared_dir = (output / shared_rel_dir) if output is not None else None
    replacements: dict[Path, Path] = {}
    exact_report = []
    duplicate_instances_avoided = 0

    # Human-readable names are part of the review/authoring contract. Derive a
    # stable semantic label for each exact group first, then add a short digest
    # only when two distinct semantic groups would otherwise collide.
    group_base_names: dict[str, str] = {}
    base_fingerprints: dict[str, set[str]] = defaultdict(set)
    for group in duplicate_groups:
        fingerprint = group[0]["exact"]
        representative = load_yaml(group[0]["path"])
        assessment = copy.deepcopy(representative.get("assessment") or {})
        benchmark_labels = {
            str(consumer.get("benchmark"))
            for row in group
            for consumer in row.get("consumers", [])
            if consumer.get("benchmark")
        }
        base = shared_assessment_base_name(assessment, benchmark_labels)
        group_base_names[fingerprint] = base
        base_fingerprints[base].add(fingerprint)

    for group in sorted(
        duplicate_groups,
        key=lambda g: (-len(g), g[0]["exact"]),
    ):
        fingerprint = group[0]["exact"]
        representative = load_yaml(group[0]["path"])
        assessment = copy.deepcopy(representative.get("assessment") or {})
        base = group_base_names[fingerprint]
        shared_name = (
            base
            if len(base_fingerprints[base]) == 1
            else f"{base}-{fingerprint[:8]}"
        )
        shared_id = f"ng.shared.{shared_name}"
        mode = assessment.get("mode")
        # Preserve the document-kind suffix because schema selection is intentionally filename-based.
        suffix = ".manual.assessment.yaml" if mode == "manual" else ".assessment.yaml"
        shared_rel_path = shared_rel_dir / f"{shared_name}{suffix}"
        shared_path = (output / shared_rel_path) if output is not None else None

        assessment["id"] = shared_id
        # This is a new canonical Assessment identity, not a continuation of
        # whichever source file sorts first.
        assessment["version"] = 1
        # Complete source/consumer lineage is emitted only in the separate
        # normalizer report below; it is intentionally not native Assessment data.
        if shared_path is not None:
            dump_yaml(shared_path, {"assessment": assessment})

        members = []
        for row in group:
            if shared_path is not None:
                replacements[row["path"]] = shared_path
            members.append(
                {
                    "source": row["path"].relative_to(source).as_posix(),
                    "source_assessment": {
                        "id": (load_yaml(row["path"]).get("assessment") or {}).get("id"),
                        "version": (load_yaml(row["path"]).get("assessment") or {}).get("version"),
                        "title": (load_yaml(row["path"]).get("assessment") or {}).get("assessment_title"),
                    },
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
                "shared_assessment": shared_rel_path.as_posix(),
                "instance_count": len(group),
                "members": members,
            }
        )

    rewritten_rule_files = (
        rewrite_rules(output, source, replacements, uses)
        if output is not None else 0
    )
    rewritten_applicability_files = (
        rewrite_applicability(output, source, replacements, uses)
        if output is not None else 0
    )

    # Remove promoted local duplicates only in explicit rewrite mode, after all
    # copied Rule references point to the shared canonical Assessment.
    removed_local_assessments = 0
    if output is not None:
        for source_path in replacements:
            copied = output / source_path.relative_to(source)
            if copied.exists():
                copied.unlink()
                removed_local_assessments += 1

    # Near duplicates are same semantic shape after only literal values are
    # abstracted, but have >1 exact semantic fingerprint.  They are advisory.
    near_groups = []
    if args.advisory in {"all","assessments"}:
        for shape, group in shape_groups.items():
            exacts = {row["exact"] for row in group}
            if len(group) < 2 or len(exacts) < 2:
                continue
            consumers = [
                {
                    "source": row["path"].relative_to(source).as_posix(),
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
            variants={}
            for row in group:
                variants.setdefault(row["exact"], row)
            ordered_variants=sorted(variants.items(), key=lambda item:item[0])
            baseline_fp,baseline_row=ordered_variants[0]
            baseline_doc=normalize_value(
                copy.deepcopy((load_yaml(baseline_row["path"]).get("assessment") or {}))
            )
            variant_differences=[]
            for variant_fp,variant_row in ordered_variants[1:]:
                variant_doc=normalize_value(
                    copy.deepcopy((load_yaml(variant_row["path"]).get("assessment") or {}))
                )
                variant_differences.append({
                    "baseline_exact_fingerprint":baseline_fp,
                    "variant_exact_fingerprint":variant_fp,
                    "baseline_source":baseline_row["path"].relative_to(source).as_posix(),
                    "variant_source":variant_row["path"].relative_to(source).as_posix(),
                    "differences":semantic_differences(baseline_doc,variant_doc,limit=20),
                })
            near_groups.append(
                {
                    "shape_fingerprint": shape,
                    "assessment_instances": len(group),
                    "exact_variants": len(exacts),
                    "benchmark_count": benchmark_count,
                    "members": consumers,
                    "variant_differences": variant_differences,
                }
            )
    near_groups.sort(
        key=lambda x: (
            -x["assessment_instances"],
            -x["benchmark_count"],
            x["shape_fingerprint"],
        )
    )
    rule_candidates = (
        near_rule_candidates(
            benchmarks,
            limit=(args.max_rule_candidates or None),
        )
        if args.advisory in {"all","rules"}
        else []
    )

    before_assessment_instances = len(rows)
    after_assessment_definitions = before_assessment_instances - duplicate_instances_avoided
    reduction_pct = (
        round(100.0 * duplicate_instances_avoided / before_assessment_instances, 2)
        if before_assessment_instances else 0.0
    )

    repository_validation = None
    if output is not None:
        repository_validation = validate_normalized_repository(output)
        # Publish only after the staged repository passes validation.  An
        # existing destination remains untouched if normalization/validation fails.
        if destination.exists():
            shutil.rmtree(destination)
        output.rename(destination)
        output = destination


    change_manifest = {
        "format": "scap-ng-repository-normalizer-change-manifest-0.1",
        "rewrite_requested": args.rewrite,
        "shared_assessments": [
            {
                "shared_assessment": group["shared_assessment"],
                "fingerprint": group["fingerprint"],
                "sources_replaced": [member["source"] for member in group["members"]],
                "consumers": [
                    consumer
                    for member in group["members"]
                    for consumer in member["consumers"]
                ],
            }
            for group in exact_report
        ],
    }

    normalizer_stats = {
        "format": "scap-ng-normalizer-stats-0.1",
        "tool": "scap_ng_repo_normalizer",
        "mode": "exact-rewrite" if args.rewrite else "dry-run-exact-plan",
        "examined": {
            "benchmarks": len(benchmarks),
            "rules": sum(len(x["rules"]) for x in benchmarks),
            "referenced_assessment_instances": before_assessment_instances,
            "exact_semantic_fingerprints": len(exact_groups),
            "shape_fingerprints": len(shape_groups),
        },
        "changed": {
            "exact_duplicate_groups_promoted": len(exact_report),
            "duplicate_assessment_definitions_avoided": duplicate_instances_avoided,
            "rule_files_rewritten": rewritten_rule_files,
            "applicability_files_rewritten": rewritten_applicability_files,
            "local_assessment_files_removed": removed_local_assessments,
        },
        "unchanged_or_review": {
            "assessment_definitions_after_exact_normalization": after_assessment_definitions,
            "near_duplicate_review_groups": len(near_groups),
            "near_duplicate_rule_candidates_reported": len(rule_candidates),
        },
        "rates": {
            "exact_definition_reduction_pct": reduction_pct,
            "cache_hit_pct": (
                round(100.0 * cache_hits / (cache_hits + cache_misses), 2)
                if (cache_hits + cache_misses) else 0.0
            ),
        },
        "reasons": {
            "automatic_change_exact_semantic_duplicate_groups": len(exact_report),
            "review_only_near_duplicate_groups": len(near_groups),
            "review_only_rule_overlap_candidates": len(rule_candidates),
        },
        "cache": {
            "hits": cache_hits,
            "misses": cache_misses,
        },
    }

    report = {
        "format": "scap-ng-repository-normalizer-report-0.1",
        "mode": (
            "exact-rewrite"
            if args.rewrite else
            "dry-run-exact-plan"
        ),
        "advisory_mode": args.advisory,
        "stats": normalizer_stats,
        "summary": {
            "benchmarks": len(benchmarks),
            "rules": sum(len(x["rules"]) for x in benchmarks),
            "referenced_assessment_instances_before": before_assessment_instances,
            "assessment_definitions_after_exact_normalization": after_assessment_definitions,
            "exact_duplicate_groups": len(exact_report),
            "duplicate_assessment_definitions_avoided": duplicate_instances_avoided,
            "exact_definition_reduction_pct": reduction_pct,
            "rule_files_rewritten": rewritten_rule_files,
            "applicability_files_rewritten": rewritten_applicability_files,
            "local_assessment_files_removed": removed_local_assessments,
            "near_duplicate_review_groups": len(near_groups),
            "near_duplicate_rule_candidates_reported": len(rule_candidates),
            "fingerprint_cache_hits": cache_hits,
            "fingerprint_cache_misses": cache_misses,
        },
        "stats": {
            "scope": {
                "benchmarks_examined": len(benchmarks),
                "rules_examined": sum(len(x["rules"]) for x in benchmarks),
                "referenced_assessment_instances_examined": before_assessment_instances,
            },
            "exact_normalization": {
                "duplicate_groups_found": len(exact_report),
                "duplicate_assessment_definitions_avoided": duplicate_instances_avoided,
                "definitions_before": before_assessment_instances,
                "definitions_after": after_assessment_definitions,
                "definition_reduction_pct": reduction_pct,
                "shared_assessments_created_or_planned": len(exact_report),
            },
            "rewrite": {
                "requested": bool(args.rewrite),
                "rule_files_rewritten": rewritten_rule_files,
                "applicability_files_rewritten": rewritten_applicability_files,
                "local_assessment_files_removed": removed_local_assessments,
            },
            "review": {
                "near_duplicate_groups": len(near_groups),
                "near_duplicate_rule_candidates": len(rule_candidates),
                "near_duplicates_merged": False,
            },
            "cache": {
                "hits": cache_hits,
                "misses": cache_misses,
                "hit_rate_pct": (
                    round(100.0 * cache_hits / (cache_hits + cache_misses), 2)
                    if cache_hits + cache_misses else 0.0
                ),
            },
            "validation": repository_validation,
        },
        "repository_validation": repository_validation,
        "change_manifest": change_manifest,
        "planned_changes": {
            "shared_assessments_to_create": len(exact_report),
            "local_assessment_instances_to_replace": sum(x["instance_count"] for x in exact_report),
            "duplicate_assessment_definitions_to_remove": duplicate_instances_avoided,
            "rewrite_requested": args.rewrite,
        },
        "exact_groups": exact_report,
        "near_duplicate_review_groups": near_groups[: args.top_near],
        "near_duplicate_groups_total": len(near_groups),
        "near_duplicate_rule_candidates": rule_candidates,
        "safety": {
            "automatic_merge_basis": "exact normalized Assessment semantics only",
            "near_duplicates_merged": False,
            "literal_abstraction_used_only_for_review_candidates": True,
            "advisory_similarity_changes_exact_merge_decisions": False,
        },
    }

    if args.fingerprint_cache is not None:
        args.fingerprint_cache.parent.mkdir(parents=True, exist_ok=True)
        args.fingerprint_cache.write_text(
            json.dumps(
                {
                    "format":"scap-ng-normalizer-fingerprint-cache-0.1",
                    "entries":next_cache,
                },
                indent=2,
                sort_keys=True,
            ) + "\n",
            encoding="utf-8",
        )

    if args.change_manifest is not None:
        args.change_manifest.parent.mkdir(parents=True, exist_ok=True)
        args.change_manifest.write_text(
            json.dumps(change_manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "summary": report["summary"],
        "stats": report["stats"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
