#!/usr/bin/env python3
"""Reproducible RHEL9, Windows 11, Windows Server 2025 0.4 research census.

Source: original *published* 0.3 six-STIG authoring ZIP. Resolves shared
automated Assessments, distinguishes manual alternatives and Rule default.
Runs three-presets, five-presets, and five+field-none independently; each
source-to-short-to-canonical document must be exact parsed YAML equality.
Residual evidence is sourced from original Tests and State fields, not inferred.
"""
from __future__ import annotations
import argparse
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import zipfile
import research_04_rhel9_compact_preview as p

BENCHMARKS=("rhel_9","windows_11","windows_server_2025")
EXTRA={("all","all"):"all_exist_all_match",("optional","all"):"optional_all_match"}

def leaf_fields(entry, location):
    if p.is_logic_group(entry):
        k=next(iter(entry))
        for idx,child in enumerate(entry[k]):
            yield from leaf_fields(child, f"{location}.{k}[{idx}]")
    elif isinstance(entry,dict) and "field" in entry:
        yield location,entry
    # Keep unusual / unknown source structures visible in separate counters.

def contextual_residuals(doc, selected_rule_ids, source_file):
    a=doc["assessment"]
    result=[]
    for tid,test in (a.get("tests") or {}).items():
        if not isinstance(test,dict):
            continue
        pair=p.pair_of(test)
        states=test.get("states")
        state_free="states" not in test or states is None
        supported_test = pair in p.PAIR_ALIASES or (state_free and pair==("none","all"))
        if not supported_test:
            result.append({
                "location":"test", "test":tid, "pair":list(pair),
                "state_free":state_free,
                "states_count":len(states) if isinstance(states,list) else None,
                "capability":test.get("capability"),
                "states_match":test.get("states_match"),
                "object_kind": ("set" if isinstance(test.get("object"),dict) and "set" in test["object"]
                                else "select" if isinstance(test.get("object"),dict) and "select" in test["object"]
                                else "other"),
                "test_sample":test,
            })
        if isinstance(states,list):
            for i,expr in enumerate(states):
                for location,node in leaf_fields(expr,f"states[{i}]"):
                    pair=p.pair_of(node)
                    if pair not in p.PAIR_ALIASES and not (
                        p.FIELD_ABSENCE_ENABLED and pair==("none","all")
                    ):
                        result.append({
                            "location":location,"test":tid,
                            "field":node.get("field"),"pair":list(pair),
                            "capability":test.get("capability"),
                            "state_predicate":node,
                            "states_match":test.get("states_match"),
                            "parent_test_pair":list(p.pair_of(test)),
                        })
    return {"file":source_file,"assessment_id":a.get("id"),
            "referenced_rule_ids":selected_rule_ids,
            "evaluate":a.get("evaluate"),
            "residuals":result}

def analyze_benchmark(archive,benchmark):
    original_prefix=p.SOURCE_PREFIX
    previous=p.PAIR_ALIASES.copy()
    previous_inverse=p.PAIR_INVERSE.copy()
    previous_none=p.FIELD_ABSENCE_ENABLED
    try:
        p.SOURCE_PREFIX=f"authoring/{benchmark}/"
        with zipfile.ZipFile(archive) as z:
            docs,raw=p.archive_contents(z)
        rules=p.benchmark_rule_paths(docs)
        if not rules:
            raise ValueError(f"No Rule entries for {benchmark}, check the released authoring ZIP")
        by_rule={}
        selected=Counter()
        by_assessment= {}
        for rid,(path,rule) in rules.items():
            choices=rule.get("assessment_choices") or {}
            default=rule.get("default_assessment_choice")
            selected[f"default:{default}"]+=1
            for choice in choices:
                selected[f"choice:{choice}"]+=1
            aid=(choices.get("automated") or {}).get("assessment")
            if default=="automated" and not aid:
                raise ValueError(f"Automated default missing Assessment: {rid}")
            if default not in choices:
                raise ValueError(f"Rule default {default} not in choices: {rid}")
            by_rule[rid]={"default":default,"automated":bool(aid),"manual":"manual" in choices,
                          "assessment_id":aid}
            if aid:
                by_assessment.setdefault(aid,[]).append(rid)
        baseline=p.single_stage(docs,2)
        outputs={}
        config=(("three",{},False),("five",EXTRA,False),("five_with_field_none",EXTRA,True))
        for name,extra,enable_none in config:
            p.PAIR_ALIASES.clear();p.PAIR_ALIASES.update(previous);p.PAIR_ALIASES.update(extra)
            p.PAIR_INVERSE.clear();p.PAIR_INVERSE.update(previous_inverse)
            p.PAIR_INVERSE.update({v:{"existence":q[0],"match":q[1]} for q,v in extra.items()})
            p.FIELD_ABSENCE_ENABLED=enable_none
            stage=p.single_stage(docs,2)
            m=stage[1]
            out=Counter()
            automated_rules=[]
            for rid,row in by_rule.items():
                if not row["automated"]:
                    continue
                aid=row["assessment_id"]
                if aid not in m:
                    raise ValueError(f"Shared Assessment missing from source: {rid}: {aid}")
                metrics=m[aid]
                long_pair=metrics["remaining_pairs"]
                long_comp=metrics["comparison_longhand"]
                automated_rules.append({
                    "rule_id":rid,
                    "assessment_id":aid,
                    "default":row["default"],
                    "explicit_quantifier_pairs":long_pair,
                    "explicit_comparisons":long_comp,
                    "field_key_predicates":metrics["field_key_compacted"],
                    "complex_evaluate":metrics["evaluate_complex"],
                })
                out["automated_rules"]+=1
                if row["default"]=="automated":
                    out["automated_default_rules"]+=1
                if not long_pair: out["all_pairs_abbreviated"]+=1
                if long_pair: out["needs_explicit_pair"]+=1
                if not long_pair and not long_comp: out["no_explicit_pairs_or_comparisons"]+=1
                if not long_pair and not long_comp and not metrics["evaluate_complex"]:
                    out["no_explicit_pairs_or_comparisons_simple_evaluate"]+=1
                if long_comp: out["needs_explicit_comparison"]+=1
                if metrics["evaluate_complex"]: out["complex_evaluate"]+=1
            out.update({k:v for k,v in stage[2].items() if k in (
                "assessments_exact","field_key_compacted","test_scope_total",
                "field_scope_total","test_explicit_pair","field_explicit_pair",
                "state_comparison_alias","selector_comparison_alias",
                "state_explicit_comparison","selector_explicit_comparison",
                "field_require:none_exist","test_require:none_exist"
            )})
            out["explicit_pair_occurrences"]=stage[2]["test_explicit_pair"]+stage[2]["field_explicit_pair"]
            out["shortened_pair_occurrences"]=sum(
                val for k,val in stage[2].items() if k.startswith(("test_require:","field_require:"))
            )
            outputs[name]={"counts":dict(out),"per_automated_rule":automated_rules}
        # Extract full residual sources at final scope, including overlapping shared Rules.
        residuals=[]
        for filepath,doc in sorted(docs.items()):
            a=doc.get("assessment") if isinstance(doc,dict) else None
            if not isinstance(a,dict) or a.get("mode")!="automated":
                continue
            aid=a.get("id")
            if aid not in by_assessment:
                continue
            residual=contextual_residuals(doc,sorted(by_assessment[aid]),filepath)
            if residual["residuals"]:
                residuals.append(residual)
        return {
            "benchmark":benchmark,
            "rules":len(rules),
            "default_choices":dict(selected),
            "three_five_field_none":outputs,
            "residual_source_assessments":residuals,
            "residual_unique_assessments":len(residuals),
            "stage_proof":"Exact parsed original 0.3 Assessment for every stage and all included auto/applicability YAML.",
        }
    finally:
        p.SOURCE_PREFIX=original_prefix
        p.FIELD_ABSENCE_ENABLED=previous_none
        p.PAIR_ALIASES.clear();p.PAIR_ALIASES.update(previous)
        p.PAIR_INVERSE.clear();p.PAIR_INVERSE.update(previous_inverse)

def summarize(report):
    lines=["# 0.4 three-benchmark cardinality shorthand, source-lowering proof","",
           "**Research only.** Unmodified published six-STIG 0.3 authoring source; not a scanner-equivalence proof.",
           "RHEL9, Windows 11 and Server 2025 default selection is taken from each Rule, not guessed.",""]
    lines.extend(["| Benchmark | Rules | Default automated | Three presets complete | Five presets complete | Five + field-none complete | Remaining pair occurrences |",
                  "|---|---:|---:|---:|---:|---:|---:|"])
    for b,record in report["benchmarks"].items():
        stages=record["three_five_field_none"]
        def cnt(stage,k):return stages[stage]["counts"].get(k,0)
        lines.append(f"| {b} | {record['rules']} | {record['default_choices'].get('default:automated',0)} | "
                     f"{cnt('three','all_pairs_abbreviated')} | {cnt('five','all_pairs_abbreviated')} | "
                     f"{cnt('five_with_field_none','all_pairs_abbreviated')} | "
                     f"{cnt('five_with_field_none','explicit_pair_occurrences')} |")
    lines.extend(["","All counts for shorthand completeness in this table apply to **all Rules with an automated choice**, not just default automated. The full JSON breaks out default automated separately. Each pair occurrence is a Test or State-field, and shared Assessments count once for the occurrence totals.",
                  "Remaining longhand is not necessarily a candidate for semantic rewriting. Inspect details in `residual_source_assessments`, including full original Test/State source excerpts.",
                  "The same `none_exist` string has a distinct explicit scope at Test (no Items and no States) versus at State field (no entity instances); `match: none` is *not* an absence assertion.",""])
    return "\n".join(lines)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--authoring-zip",type=Path,required=True)
    parser.add_argument("--benchmarks",nargs="+",default=list(BENCHMARKS))
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--markdown",type=Path)
    args=parser.parse_args()
    results={"source_tag":"v0.3.0-six-stig-typed-operators-5796d016b12f",
             "benchmarks":{},"research_only":True}
    for name in args.benchmarks:
        results["benchmarks"][name]=analyze_benchmark(args.authoring_zip,name)
        print(name,json.dumps({stage:record["counts"] for stage,record in
             results["benchmarks"][name]["three_five_field_none"].items()},sort_keys=True),flush=True)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(results,indent=2,sort_keys=True)+"\n")
    if args.markdown:
        args.markdown.parent.mkdir(parents=True,exist_ok=True)
        args.markdown.write_text(summarize(results)+"\n")
    print("SUMMARIZED")
    print(summarize(results))
if __name__=="__main__":
    main()
