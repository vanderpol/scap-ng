#!/usr/bin/env python3
"""Research-only 0.4 RHEL9: complete benchmark + Rule + Assessment authoring preview.

Baseline: immutable 0.3 published six-STIG authoring ZIP. No change to
scanning bundles or canonical Assessment semantics.

Stage 1: only State field-name keys and distinct-scope require quantifier aliases.
Stage 2: also use scalar comparison aliases equals/matches_regex.
Revert each to identical parsed baseline assessment; leave manual/rule/benchmark
bytes unchanged. Classify every Rule including manual-only.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from copy import deepcopy
import csv
import hashlib
import io
import json
from pathlib import Path
import zipfile
import yaml

from research_04_field_key_authoring import fold_document, unfold_document
from research_04_compiled_authoring_macros import simplify_predicate, expand_predicate
from research_04_quantifier_aliases import shorten_pair, expand_pair

SOURCE_PREFIX="authoring/rhel_9/"
FORMAT="scap-ng-compact-research/0.4"
PAIR_ALIASES={
    ("one_or_more","all"):"at_least_one_all_match",
    ("one_or_more","one_or_more"):"at_least_one_some_match",
}
PAIR_INVERSE={value:{"existence":k[0],"match":k[1]}
              for k,value in PAIR_ALIASES.items()}
ABSENCE="none_exist"
# Research sensitivity toggle only. The published RHEL9 preview keeps this off.
# At field scope none/all means no observed entities of the named field,
# NOT zero collected Items. Exact pair lowering, not Test-level no-State proof.
FIELD_ABSENCE_ENABLED=False
# Scoped human-language research aliases for Test existence: one / match: all.
# With no State, there is nothing to compare; do not say 'matches'.
EXACT_ONE_NATURAL_ENABLED=False
EXACT_ONE_BARE="only_one_exists"
EXACT_ONE_WITH_STATE="only_one_exists_and_matches"
LOGICAL={"all","any","one","odd"}

def pair_of(node):
    if not isinstance(node,dict):
        return ("<not_mapping>","<not_mapping>")
    return (node.get("existence","<missing>"),node.get("match","<missing>"))

def maybe_require(node, scope, counts, *, state_free=False):
    pair=pair_of(node)
    counts[f"{scope}_pair:{pair[0]}/{pair[1]}"]+=1
    counts[f"{scope}_scope_total"]+=1
    label=PAIR_ALIASES.get(pair)
    if scope=="test" and state_free and pair==("none","all"):
        label=ABSENCE
    elif scope=="field" and FIELD_ABSENCE_ENABLED and pair==("none","all"):
        label=ABSENCE
    elif scope=="test" and EXACT_ONE_NATURAL_ENABLED and pair==("one","all"):
        label=EXACT_ONE_BARE if state_free else EXACT_ONE_WITH_STATE
    if label is not None:
        out=deepcopy(node)
        if "require" in out:
            raise ValueError("require collision")
        out["require"]=label
        del out["existence"]
        del out["match"]
        counts[f"{scope}_require:{label}"]+=1
        return out
    counts[f"{scope}_explicit_pair"]+=1
    return deepcopy(node)

def expand_require(node, *, scope, state_free=False):
    if not isinstance(node,dict) or "require" not in node:
        return deepcopy(node)
    label=node["require"]
    if "existence" in node or "match" in node:
        raise ValueError("Cannot mix shorthand and explicit quantifiers")
    if label in (EXACT_ONE_BARE, EXACT_ONE_WITH_STATE):
        if not EXACT_ONE_NATURAL_ENABLED or scope!="test":
            raise ValueError("Human-language exact-one aliases available only on Tests in research")
        if label==EXACT_ONE_BARE and not state_free:
            raise ValueError("only_one_exists requires a Test without States")
        if label==EXACT_ONE_WITH_STATE and state_free:
            raise ValueError("only_one_exists_and_matches requires at least one State")
        pair={"existence":"one","match":"all"}
    elif label==ABSENCE:
        if scope=="test":
            if not state_free:
                raise ValueError("none_exist requires a Test without States")
        elif scope=="field":
            if not FIELD_ABSENCE_ENABLED:
                raise ValueError("none_exist at State-field scope not enabled in this research version")
        else:
            raise ValueError("none_exist requires an explicit Test or field scope")
        pair={"existence":"none","match":"all"}
    elif label in PAIR_INVERSE:
        pair=PAIR_INVERSE[label]
    else:
        raise ValueError(f"Unrecognized require shorthand: {label}")
    out=deepcopy(node)
    out.pop("require")
    out.update(pair)
    return out

def is_logic_group(entry):
    return (isinstance(entry,dict) and len(entry)==1
            and next(iter(entry)) in LOGICAL
            and isinstance(next(iter(entry.values())),list))

def state_shorten(entry,counts,stage):
    if is_logic_group(entry):
        key=next(iter(entry))
        counts[f"logic_group:{key}"]+=1
        return {key:[state_shorten(child,counts,stage) for child in entry[key]]}
    if not isinstance(entry,dict) or len(entry)!=1:
        counts["state_other_nonfield"]+=1
        return deepcopy(entry)
    name,payload=next(iter(entry.items()))
    if not isinstance(payload,dict) or not payload:
        counts["state_nonpredicate_payload"]+=1
        return deepcopy(entry)
    payload=maybe_require(payload,"field",counts)
    if stage==2:
        payload,changed=simplify_predicate(payload)
        if changed:
            counts["state_comparison_alias"]+=1
        elif "operation" in payload:
            counts["state_explicit_comparison"]+=1
    return {name:payload}

def state_expand(entry):
    if is_logic_group(entry):
        key=next(iter(entry))
        return {key:[state_expand(child) for child in entry[key]]}
    if not isinstance(entry,dict) or len(entry)!=1:
        return deepcopy(entry)
    name,payload=next(iter(entry.items()))
    if not isinstance(payload,dict):
        return deepcopy(entry)
    val=expand_predicate(payload)
    val=expand_require(val,scope="field")
    return {name:val}

def compact_assessment(doc,stage):
    out,field_counts=fold_document(doc)
    a=out["assessment"]
    if a.get("mode")!="automated":
        raise ValueError("Only automated Assessment can be compacted")
    if "authoring_format" in out:
        raise ValueError("Existing authoring format collision")
    counts=Counter(field_counts)
    out["authoring_format"]=FORMAT
    for tid,test in (a.get("tests") or {}).items():
        if not isinstance(test,dict):
            counts["nonmapping_test"]+=1
            continue
        if isinstance(test.get("states"),list):
            test["states"]=[state_shorten(x,counts,stage) for x in test["states"]]
        # Test None existence is an explicit *absence-only* macro.
        state_free="states" not in test or test["states"] is None
        if state_free:
            counts["state_free_tests"]+=1
        compact_test=maybe_require(test,"test",counts,state_free=state_free)
        # Since Test identity is meaningful for evaluate, retain named Tests.
        a["tests"][tid]=compact_test
        if stage==2:
            obj=compact_test.get("object")
            if isinstance(obj,dict):
                sel=obj.get("select")
                if isinstance(sel,dict):
                    for field,pred in list(sel.items()):
                        compact,changed=simplify_predicate(pred)
                        if changed:
                            sel[field]=compact
                            counts["selector_comparison_alias"]+=1
                        elif isinstance(pred,dict) and "operation" in pred:
                            counts["selector_explicit_comparison"]+=1
    return out,counts

def canonical_assessment(short):
    out=deepcopy(short)
    if out.pop("authoring_format",None)!=FORMAT:
        raise ValueError("Not an opted-in research authoring format")
    a=out["assessment"]
    for tid,test in (a.get("tests") or {}).items():
        if not isinstance(test,dict):
            continue
        has_states="states" in test and test["states"] is not None
        test=expand_require(test,scope="test",state_free=not has_states)
        obj=test.get("object")
        if isinstance(obj,dict) and isinstance(obj.get("select"),dict):
            for field,pred in list(obj["select"].items()):
                obj["select"][field]=expand_predicate(pred)
        if isinstance(test.get("states"),list):
            test["states"]=[state_expand(x) for x in test["states"]]
        a["tests"][tid]=test
    return unfold_document(out)

def archive_contents(z):
    # Preserve all RHEL9 Benchmark/Rule/manual/applicability files, plus only
    # shared automated Assessments actually referenced by RHEL9 Rules.
    # Manual source files are fallbacks available via tailoring, not default
    # manual execution counts.
    docs={}
    raw={}
    archive_names=z.namelist()
    for name in archive_names:
        if not name.startswith(SOURCE_PREFIX) or name.endswith("/"):
            continue
        raw[name]=z.read(name)
        if name.endswith((".yaml",".yml")):
            docs[name]=yaml.safe_load(raw[name])
    refs=set()
    for name,doc in docs.items():
        if "/rules/" not in name:
            continue
        rule=(doc or {}).get("rule") or {}
        choice=(rule.get("assessment_choices") or {}).get("automated")
        if isinstance(choice,dict) and choice.get("assessment"):
            refs.add(choice["assessment"])
    locally_available={
        (doc or {}).get("assessment",{}).get("id")
        for doc in docs.values() if isinstance(doc,dict)
        and isinstance(doc.get("assessment"),dict)
    }
    wanted=refs-locally_available
    matched=set()
    for name in archive_names:
        if not name.startswith("authoring/shared/") or not name.endswith((".yaml",".yml")):
            continue
        body=z.read(name)
        doc=yaml.safe_load(body)
        assessment=(doc or {}).get("assessment") if isinstance(doc,dict) else None
        if not isinstance(assessment,dict) or assessment.get("id") not in wanted:
            continue
        if assessment["id"] in matched:
            raise ValueError(f"Duplicate shared Assessment id: {assessment['id']}")
        matched.add(assessment["id"])
        docs[name]=doc
        raw[name]=body
    missing=wanted-matched
    if missing:
        raise ValueError(f"Unresolved RHEL9 shared automated Assessments: {sorted(missing)[:12]}")
    return docs,raw

def benchmark_rule_paths(docs):
    rules={}
    for path,doc in docs.items():
        if "/rules/" in path:
            rule=(doc or {}).get("rule") or {}
            ident=rule.get("id")
            if not ident or ident in rules:
                raise ValueError("Missing or duplicate Rule ID")
            rules[ident]=(path,rule)
    return rules

def info_for_rule(rid,rule,automated_metrics):
    selected=rule.get("assessment_choices") or {}
    choices=selected.get("automated")
    manual=bool(selected.get("manual"))
    default_choice=rule.get("default_assessment_choice")
    if default_choice not in {"automated","manual"}:
        raise ValueError(f"Rule {rid} has unknown default Assessment choice: {default_choice}")
    if default_choice not in selected:
        raise ValueError(f"Rule {rid} default does not exist in choices: {default_choice}")
    row={"rule_id":rid,"rule_title":rule.get("title"),
         "default_assessment_choice":default_choice,
         "automated_by_default":default_choice=="automated",
         "manual_by_default":default_choice=="manual",
         "automated_choice":bool(choices),
         "manual_choice":manual,
         "classification":"manual_only" if not choices else "automated_assessment_missing",
         "automated_assessment_id":"",
         "original_test_count":0,
         "original_field_count":0,
         "quantifier_preset_count":0,
         "quantifier_longhand_count":0,
         "field_key_count":0,
         "comparison_alias_count":0,
         "comparison_longhand_count":0,
         "original_evaluate_complex":False,
         "reason":""}
    if not choices:
        row["reason"]="No automated Assessment selected by Rule; manual content is unchanged"
        return row
    aid=choices.get("assessment")
    if not aid:
        raise ValueError(f"Rule {rid} missing automated choice id")
    row["automated_assessment_id"]=aid
    if aid not in automated_metrics:
        raise ValueError(f"Rule {rid} references unavailable automated Assessment {aid}")
    metrics=automated_metrics[aid]
    row["original_test_count"]=metrics["tests"]
    row["original_field_count"]=metrics["canonical_field_nodes"]
    row["quantifier_preset_count"]=metrics["preset_count"]
    row["quantifier_longhand_count"]=metrics["remaining_pairs"]
    row["field_key_count"]=metrics["field_key_compacted"]
    row["comparison_alias_count"]=metrics["comparison_aliases"]
    row["comparison_longhand_count"]=metrics["comparison_longhand"]
    row["original_evaluate_complex"]=metrics["evaluate_complex"]
    if metrics["remaining_pairs"]:
        row["classification"]="requires_explicit_quantifier_pairs"
        row["reason"]="Not all Test/field quantifier combinations belong to proposed presets"
    else:
        row["classification"]="all_quantifiers_use_presets"
        row["reason"]="All explicit Test/field quantifier pairs were replaced by named presets"
    return row

def metrics_for_assessment(original,compact,counts):
    a=original["assessment"]
    t=a.get("tests") or {}
    roots=a.get("evaluate")
    eval_simple=(len(t)==1 and isinstance(roots,dict)
                 and roots=={"test":next(iter(t))})
    return {
        "tests":len(t),
        "canonical_field_nodes":counts["canonical_field_nodes"],
        "field_key_compacted":counts["field_key_compacted"],
        "preset_count":sum(v for k,v in counts.items() if k.startswith(("field_require:","test_require:"))),
        "remaining_pairs":counts["test_explicit_pair"]+counts["field_explicit_pair"],
        "comparison_aliases":counts["state_comparison_alias"]+counts["selector_comparison_alias"],
        "comparison_longhand":counts["state_explicit_comparison"]+counts["selector_explicit_comparison"],
        "evaluate_complex":not eval_simple,
    }

def single_stage(docs,stage):
    transformed={}
    metrics={}
    by_assessment={}
    total=Counter()
    for path,doc in sorted(docs.items()):
        if not path.endswith((".yaml",".yml")) or not isinstance(doc,dict):
            continue
        a=doc.get("assessment")
        if not isinstance(a,dict) or a.get("mode")!="automated":
            continue
        short,c=compact_assessment(doc,stage)
        if canonical_assessment(short)!=doc:
            raise ValueError(f"Not exact after round-trip: {path}")
        total["assessments_exact"]+=1
        total.update(c)
        aid=a.get("id")
        if aid in metrics:
            raise ValueError(f"Duplicate automated Assessment id {aid}")
        metrics[aid]=metrics_for_assessment(doc,short,c)
        by_assessment[path]=short
    return by_assessment,metrics,total

def yaml_output(value):
    return yaml.safe_dump(value,sort_keys=False,allow_unicode=True,width=98).encode("utf-8")

def make_report(docs,raw,stage1,stage2):
    rule_docs=benchmark_rule_paths(docs)
    if len(rule_docs)!=445:
        raise ValueError(f"Expected 445 released RHEL 9 Rule files, got {len(rule_docs)}")
    comp1,m1,c1=stage1
    comp2,m2,c2=stage2
    if set(comp1)!=set(comp2):
        raise ValueError("Stage sets differ")
    actual_auto={name:(doc or {}).get("assessment",{}).get("id")
                 for name,doc in docs.items()
                 if "/assessments/automated/" in name}
    if len(actual_auto)!=50:
        raise ValueError(f"Expected 50 RHEL9 automatic Assessments, got {len(actual_auto)}")
    rows=[]
    for rid,(path,rule) in sorted(rule_docs.items()):
        rows.append(info_for_rule(rid,rule,m2))
    aggregate=Counter(row["classification"] for row in rows)
    auto=[row for row in rows if row["automated_choice"]]
    if len(auto)!=417:
        raise ValueError(f"RHEL9 source has 417 automated Rule choices; got {len(auto)}")
    if sum(row["classification"]=="manual_only" for row in rows)!=28:
        raise ValueError("RHEL9 expected 28 manual-only Rules")
    if not all(row["manual_choice"] for row in rows):
        raise ValueError("Some Rules lost their manual tailoring choice")
    stage1_pair_residuals=sum(m["remaining_pairs"] for m in m1.values())
    stage2_pair_residuals=sum(m["remaining_pairs"] for m in m2.values())
    if stage1_pair_residuals!=stage2_pair_residuals:
        raise AssertionError("A comparison alias changed cardinality coverage")
    app={key:metric for key,metric in m2.items() if "condition." in key or "platform." in key}
    unused={k for k in m2 if k not in {r["automated_assessment_id"] for r in auto}}
    return {
        "provenance":{
            "source_release_tag":"v0.3.0-six-stig-typed-operators-5796d016b12f",
            "source_asset":"scap-ng-0.3-six-stig-authoring.zip",
            "research_format":FORMAT,
            "status":"research-only; canonical NG 0.3 remains unchanged",
            "scope":"Full released RHEL9 Benchmark, Rule, Assessment authoring tree",
        },
        "rules":{
            "total":len(rows),
            "automated_choices":len(auto),
            "automated_default":sum(row["automated_by_default"] for row in rows),
            "manual_default":sum(row["manual_by_default"] for row in rows),
            "manual_choices":sum(row["manual_choice"] for row in rows),
            "manual_only":aggregate["manual_only"],
            "both_automated_and_manual_choices":sum(row["manual_choice"] and row["automated_choice"] for row in rows),
            "automated_all_quantifiers_compact":aggregate["all_quantifiers_use_presets"],
            "automated_needing_explicit_quantifier_pairs":aggregate["requires_explicit_quantifier_pairs"],
            "automated_presets_not_full_language_compaction":True,
            "multi_test_evaluate_among_automated":sum(bool(row["original_evaluate_complex"]) for row in auto),
            "automated_with_unsupported_comparison_aliases":sum(bool(row["comparison_longhand_count"]) for row in auto),
            "automated_no_pair_or_comparison_longhand":sum(
                row["quantifier_longhand_count"]==0 and row["comparison_longhand_count"]==0
                for row in auto),
            "automated_no_pair_or_comparison_longhand_and_simple_evaluate":sum(
                row["quantifier_longhand_count"]==0 and row["comparison_longhand_count"]==0
                and not row["original_evaluate_complex"] for row in auto),
            "automated_any_pair_or_comparison_longhand":sum(
                row["quantifier_longhand_count"]>0 or row["comparison_longhand_count"]>0
                for row in auto),
            "classification_counts":dict(aggregate),
        },
        "assessments":{
            "automated":len(actual_auto),
            "applicability":len([p for p in comp2 if "/assessments/applicability/" in p]),
            "total_research_automated_reversible":len(comp2),
            "stage1_field_key_plus_require":dict(c1),
            "stage2_plus_scalar_comparison":dict(c2),
        },
        "source_file_inventory":{
            "rhel9_rule_files":len(rule_docs),
            "rhel9_local_automated_files":len(actual_auto),
            "rhel9_manual_files":sum("/assessments/manual/" in p and p.startswith(SOURCE_PREFIX) for p in raw),
            "rhel9_applicability_files":sum("/assessments/applicability/" in p and p.startswith(SOURCE_PREFIX) for p in raw),
            "included_shared_assessment_files":sum(p.startswith("authoring/shared/") and "/assessments/" in p for p in raw),
        },
        "limited_claims":[
            "Every automated and applicability Assessment compiles to exactly the original parsed 0.3 YAML document.",
            "All Rule and Benchmark source YAML files are copied byte-for-byte; manual Assessments copied untouched, and shared automated Assessments are included by resolved ID.",
            "Only existence+match pairs exactly included in the three named research presets are shortened.",
            "Uncovered pair does not mean Rule must be manually assessed; it means some automated YAML remains explicit.",
            "Only scalar equals and regex comparisons may use short comparisons; typed, Variable, array and other comparisons remain canonical.",
            "Array value_match is independent from Item and field require, must be preserved.",
            "This is not a scanner differential or full canonical binary bundle rebuild/byte-identity test.",
        ],
        "rule_classifications":rows,
    }

def make_readme(report):
    rules=report["rules"]
    totals=report["assessments"]["stage2_plus_scalar_comparison"]
    return f"""# RHEL 9 — research-only 0.4 compact authoring preview

**Not approved, not SCAP-NG 0.4 conformance content, not scanning bundles.**
Source: immutable published 0.3 six-STIG authoring ZIP.
Source Rule + Benchmark YAML are **byte-for-byte unchanged**, as are all manual Assessments.
Every automated/applicability Assessment has `authoring_format: {FORMAT}`, so there is no hidden grammar.
The research compiler removes that marker and restores the exact parsed 0.3 Assessment.

## Coverage

- **{rules["total"]}** Rule files in the released RHEL 9 Benchmark
- **{rules["automated_default"]}** Rules default to automated assessment
- **{rules["manual_default"]}** Rules default to manual assessment
- **{rules["automated_choices"]}** Rules offer an automated choice
- **{rules["manual_choices"]}** Rules offer a manual fallback via tailoring
- **{rules["manual_only"]}** Rules offer only manual assessment; *not* counted as 'requiring longhand'
- **{rules["automated_all_quantifiers_compact"]}** automated Rules: all Test+State existence/match pairs expressible by the available three presets
- **{rules["automated_needing_explicit_quantifier_pairs"]}** automated Rules: at least one pair remains in original longhand
- **{rules["multi_test_evaluate_among_automated"]}** automated Rules have complex/multi-Test evaluation that remains explicit and unchanged
- **{rules["automated_with_unsupported_comparison_aliases"]}** automated Rules contain comparison operations not eligible for simple scalar equals/regex aliases
- **{rules["automated_no_pair_or_comparison_longhand"]}** automated Rules have **no longhand quantifier pairs or comparison operations** after both research transformations (other complex YAML may remain)
- **{rules["automated_no_pair_or_comparison_longhand_and_simple_evaluate"]}** of those also have a direct single-Test `evaluate` expression
- **{totals.get("field_key_compacted",0)}** field predicates authored as their actual field name
- **{totals.get("test_explicit_pair",0)+totals.get("field_explicit_pair",0)}** exact quantifier-pair instances not covered by proposed presets

Counts classify YAML **presentation** only, not correctness or automatic scan coverage.
`research/RULE-CLASSIFICATION.csv` identifies each Rule and any remaining longhand.

## Layout

`authoring/rhel_9/` — complete original RHEL9 Benchmark, Rules, manual, automated and applicability files.
`authoring/shared/assessments/` — only the original reusable Assessments actually referenced by RHEL9 automated choices, compacted in this research preview.
`research/REPORT.json` — raw counts, pair distributions, and per-Rule classifications.
`research/RULE-CLASSIFICATION.csv` — every Rule, explicit vs preset presence.
`research/EXAMPLES.md` — source-derived examples with exact original and compact forms.

## Proposed syntax and constraints

```yaml
authoring_format: {FORMAT}
assessment:
  tests:
    example-test:
      ...
      states:
        - owner_uid:
            equals: 0
            require: at_least_one_all_match
      require: at_least_one_all_match
```

This format uses a field name key, `require: at_least_one_all_match` (exists one_or_more + match all), `require: at_least_one_some_match` (exists one_or_more + match one_or_more), and `require: none_exist` (State-free Test, explicitly none/all only). Comparators `equals:` and `matches_regex:` are an additional independently measured second stage.

Literal arrays *continue to require* explicit `value_match` and `datatype` where canonical 0.3 needs them. Arrays are not shorthand for quantifier pairs. Repeated State fields stay ordered list items, not duplicate YAML object keys. No semantic default or OVAL evaluator behavior is introduced.

This is a source-language preview, not a new specification. The research interpreter and unit tests are in this repository, and Board deliberation is still required.
"""

def examples_markdown(docs,stage1,stage2,report):
    out=["# RHEL9 research: real source examples (not synthetic rules)",
         "",f"Exactly equivalent after expanding macros. Suggested format: `{FORMAT}`.",
         "The snippet includes Assessment source only; the unchanged Rule and Benchmark are in the authoring tree.",""]
    # Show one simple, one multi-test, and one with an inline literal collection if available.
    preferred=["SV-257923","SV-257777","SV-257794"]
    paths=list(stage2)
    for rule_id in preferred:
        path=SOURCE_PREFIX+f"assessments/automated/{rule_id}.automated.yaml"
        if path not in stage2:
            continue
        original=docs[path]
        modified=stage2[path]
        out.extend([f"## {rule_id}", "",
                    f"**Assessment:** `{path}`. The original content is reconstructed exactly.",
                    "", "**Canonical 0.3:**","", "```yaml",
                    yaml.safe_dump({"assessment":{"tests":original["assessment"].get("tests"),
                                                   "evaluate":original["assessment"].get("evaluate")}},
                                   sort_keys=False,width=92).strip(),
                    "```","",
                    "**Research 0.4 compact:**","", "```yaml",
                    yaml.safe_dump({"authoring_format":FORMAT,
                                    "assessment":{"tests":modified["assessment"].get("tests"),
                                                  "evaluate":modified["assessment"].get("evaluate")}},
                                   sort_keys=False,width=92).strip(),
                    "```",""])
    return "\n".join(out)+"\n"

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--authoring-zip",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--report-out",type=Path)
    args=p.parse_args()
    if args.authoring_zip.resolve()==args.output.resolve():
        raise ValueError("Do not overwrite source archive")
    with zipfile.ZipFile(args.authoring_zip) as z:
        if z.testzip():
            raise ValueError("Corrupted source ZIP")
        docs,raw=archive_contents(z)
    stage1=single_stage(docs,1)
    stage2=single_stage(docs,2)
    report=make_report(docs,raw,stage1,stage2)
    if args.report_out:
        args.report_out.parent.mkdir(parents=True,exist_ok=True)
        args.report_out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    args.output.parent.mkdir(parents=True,exist_ok=True)
    # Preserve all source bytes except changed Automated/Applicability Assessment YAML.
    with zipfile.ZipFile(args.output,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=8) as z:
        for name,source_bytes in sorted(raw.items()):
            changed=stage2[0].get(name)
            if changed is not None:
                blob=yaml_output(changed)
                if canonical_assessment(yaml.safe_load(blob))!=docs[name]:
                    raise ValueError(f"Serialized round-trip mismatch: {name}")
                z.writestr(name,blob)
            else:
                z.writestr(name,source_bytes)
        z.writestr("research/README.md",make_readme(report))
        z.writestr("research/REPORT.json",json.dumps(report,indent=2,sort_keys=True)+"\n")
        with io.StringIO() as buf:
            fields=list(report["rule_classifications"][0])
            writer=csv.DictWriter(buf,fieldnames=fields)
            writer.writeheader()
            writer.writerows(report["rule_classifications"])
            z.writestr("research/RULE-CLASSIFICATION.csv",buf.getvalue())
        z.writestr("research/EXAMPLES.md",examples_markdown(docs,stage1[0],stage2[0],report))
    # Independently ensure copied human/Rule/Benchmark files and path set match exactly.
    with zipfile.ZipFile(args.output) as z:
        if {name for name in z.namelist() if name.startswith("authoring/")} != set(raw):
            raise AssertionError("Preview omitted or added source authoring files")
        for name,source_bytes in raw.items():
            contents=z.read(name)
            if name in stage2[0]:
                if canonical_assessment(yaml.safe_load(contents))!=docs[name]:
                    raise AssertionError(f"Preview self-check failed: {name}")
            elif contents!=source_bytes:
                raise AssertionError(f"Unchanged file mutated: {name}")
    print("RHEL9_RULES",json.dumps(report["rules"]))
    print("STAGE1",json.dumps(dict(stage1[2])))
    print("STAGE2",json.dumps(dict(stage2[2])))
    print("PREVIEW_ZIP",args.output,args.output.stat().st_size)

if __name__=="__main__":
    main()
