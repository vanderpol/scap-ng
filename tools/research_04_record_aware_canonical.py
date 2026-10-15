#!/usr/bin/env python3
"""Research-only 0.4 one-grammar candidate for nested record quantifiers.

Proves the 0.3 source identity for scalar/record field-key authoring with a
single require: vocabulary. No checker truth or scanner parity is assumed.
"""
from collections import Counter,defaultdict
from copy import deepcopy
from pathlib import Path
import argparse,json,zipfile

import research_04_rhel9_compact_preview as p
from research_04_compiled_authoring_macros import simplify_predicate,expand_predicate

FIVE={
    ("all","all"):"all_exist_all_match",
    ("optional","all"):"optional_all_match",
}
# These are EXACT pair labels, not semantic rewrites. Names not adopted.
RESIDUAL={
    ("one","all"):"exactly_one_all_match",
    ("one_or_more","one"):"at_least_one_exactly_one_match",
    ("one","one"):"exactly_one_exactly_one_match",
    ("optional","none"):"optional_none_match",
    ("all","none"):"all_exist_none_match",
    ("one_or_more","none"):"at_least_one_none_match",
    ("optional","one_or_more"):"optional_some_match",
}
LOGIC={"all","any","one","odd"}

def each_leaf(expr):
    if p.is_logic_group(expr):
        for v in next(iter(expr.values())):
            yield from each_leaf(v)
    elif isinstance(expr,dict) and len(expr)==1:
        value=next(iter(expr.values()))
        if isinstance(value,dict):
            yield value

def change_records(compact, *, encode, count, scope):
    out=deepcopy(compact)
    for t in (out["assessment"].get("tests") or {}).values():
        if not isinstance(t,dict):continue
        for state in t.get("states") or []:
            for payload in each_leaf(state):
                rec=payload.get("record")
                if not isinstance(rec,dict):continue
                count["record_wrappers"]+=1
                if encode:
                    # The wrapper has field+record, but NO standalone pair.
                    # It is incorrectly counted as missing pair by the early
                    # generic compiler; measure nested semantics instead.
                    if "existence" in rec and "match" in rec:
                        rec=p.maybe_require(rec,"field",count)
                    fields=rec.get("fields")
                    if isinstance(fields,dict):
                        for field,child in fields.items():
                            count["record_subfields"]+=1
                            if not isinstance(child,dict):
                                raise ValueError("Expected record field predicate mapping")
                            child=p.maybe_require(child,"field",count)
                            child,changed=simplify_predicate(child)
                            if changed:count["record_comparison_alias"]+=1
                            rec["fields"][field]=child
                    payload["record"]=rec
                else:
                    fields=rec.get("fields")
                    if isinstance(fields,dict):
                        rec["fields"]={
                            key:p.expand_require(expand_predicate(value),scope="field")
                            for key,value in fields.items()
                        }
                    payload["record"]=p.expand_require(rec,scope="field")
    return out

def survey(zip_path,benchmark,extra,enable_field_none):
    old_prefix=p.SOURCE_PREFIX
    old_pairs=dict(p.PAIR_ALIASES)
    old_inverse=dict(p.PAIR_INVERSE)
    old_none=p.FIELD_ABSENCE_ENABLED
    try:
        with zipfile.ZipFile(zip_path) as z:
            available={x.split("/")[1] for x in z.namelist() if "/rules/" in x and x.startswith("authoring/")}
            names={"rhel_9":("rhel","9"),"windows_11":("windows","11"),"windows_server_2025":("windows","2025")}
            terms=names[benchmark]
            candidates=[n for n in available if all(term in n.lower() for term in terms)]
            if len(candidates)!=1:
                raise ValueError(f"Unresolved {benchmark} directory: {candidates}; available={available}")
            p.SOURCE_PREFIX="authoring/"+candidates[0]+"/"
            docs,raw=p.archive_contents(z)
        rules=p.benchmark_rule_paths(docs)
        refs={}
        for rid,(path,rule) in rules.items():
            ac=(rule.get("assessment_choices") or {}).get("automated")
            if ac:
                refs[rid]=ac["assessment"]
        p.PAIR_ALIASES.clear()
        p.PAIR_ALIASES.update(old_pairs)
        p.PAIR_ALIASES.update(FIVE)
        p.PAIR_ALIASES.update(extra)
        p.PAIR_INVERSE.clear()
        p.PAIR_INVERSE.update({alias:{"existence":pair[0],"match":pair[1]}
                              for pair,alias in p.PAIR_ALIASES.items()})
        p.FIELD_ABSENCE_ENABLED=enable_field_none
        mappings={}
        totals=Counter()
        exemplars=[]
        for path,original in sorted(docs.items()):
            if not isinstance(original,dict) or (original.get("assessment") or {}).get("mode")!="automated":
                continue
            short,c=p.compact_assessment(original,2)
            original_short=c.copy()
            amended=change_records(short,encode=True,count=c,scope="record")
            # stage 2 expander handles scalar/State/test and record payload is
            # independent; restore record internals before lowering field key.
            temp=change_records(amended,encode=False,count=Counter(),scope="record")
            if p.canonical_assessment(temp)!=original:
                raise ValueError(f"Non-reversible record/lowering: {path}")
            # Verify serialization too, as there may be typed scalar ambiguities
            # with PyYAML or the field named 'value'.
            if p.canonical_assessment(change_records(amended,encode=False,count=Counter(),scope="record"))!=original:
                raise ValueError(f"2nd record lowering mismatch: {path}")
            wrapper=c["record_wrappers"]
            # These are NOT missing pair settings. The real quantifiers reside
            # on rec and rec.fields subpredicates.
            remaining=c["test_explicit_pair"]+c["field_explicit_pair"]-wrapper
            if remaining<0:raise ValueError("Bad wrapper pair accounting")
            if c["field_explicit_pair"]<wrapper:raise ValueError("Wrapper source pair count mismatch")
            metrics={
                "explicit_pair_count":remaining,
                "record_wrappers":wrapper,
                "record_subfields":c["record_subfields"],
                "record_pair_aliases":sum(v for k,v in c.items() if k.startswith("field_require:"))-sum(
                    v for k,v in original_short.items() if k.startswith("field_require:")),
                "all_record_pairs_aliasable":c["record_wrappers"]==0 or remaining==0,
                "regular_aliases":sum(v for k,v in original_short.items() if k.startswith(("test_require:","field_require:"))),
                "total_test_fields":c["test_scope_total"]+c["field_scope_total"],
                "field_name_compactions":c["field_key_compacted"],
                "source_path":path,
            }
            totals.update({
                "files":1,
                "record_wrappers":wrapper,
                "record_subfields":c["record_subfields"],
                "explicit_quantifier_occurrences":remaining,
                "record_pair_aliases":metrics["record_pair_aliases"],
                "original_field_key_compactions":c["field_key_compacted"],
            })
            aid=original["assessment"].get("id")
            if aid in mappings:
                raise ValueError(f"Duplicate Assessment id: {aid}")
            mappings[aid]=metrics
            if wrapper and len(exemplars)<5:
                for t in (original["assessment"].get("tests") or {}).values():
                    for state in t.get("states") or []:
                        for node in each_leaf({"field_placeholder":state} if isinstance(state,dict) and "field" in state else state):
                            if "record" in node:
                                exemplars.append({"file":path,"source":node,"compact_record":(
                                    next((x.get("record") for test in (amended["assessment"].get("tests") or {}).values()
                                          for st in test.get("states") or [] for x in each_leaf(st)
                                          if "record" in x),None))})
                                break
                        if exemplars:break
                    if exemplars:break
        automated=[(rid,aid) for rid,aid in refs.items()]
        missing={aid for rid,aid in automated if aid not in mappings}
        if missing:raise ValueError(f"Unresolved Rule to Assessment references {sorted(missing)[:8]}")
        by_rule=[]
        for rid,aid in automated:
            metrics=mappings[aid]
            by_rule.append({
                "rule":rid,"assessment":aid,"explicit_pair_count":metrics["explicit_pair_count"],
                "record_wrappers":metrics["record_wrappers"],"record_subfields":metrics["record_subfields"],
            })
        return {
            "benchmark":benchmark,
            "rules":len(rules),
            "automated_rules":len(automated),
            "files_included":len(mappings),
            "shortened_scope":"test, State scalar field, record existence, record subfield",
            "record_aware_metrics":dict(totals),
            "automated_rules_all_quantifiers_abbreviated":sum(r["explicit_pair_count"]==0 for r in by_rule),
            "automated_rules_with_explicit_pairs":sum(r["explicit_pair_count"]>0 for r in by_rule),
            "residual_rule_pairs":[r for r in by_rule if r["explicit_pair_count"]>0],
            "record_examples":exemplars[:3],
        }
    finally:
        p.SOURCE_PREFIX=old_prefix
        p.PAIR_ALIASES.clear();p.PAIR_ALIASES.update(old_pairs)
        p.PAIR_INVERSE.clear();p.PAIR_INVERSE.update(old_inverse)
        p.FIELD_ABSENCE_ENABLED=old_none

def main():
    x=argparse.ArgumentParser()
    x.add_argument("--authoring-zip",type=Path,required=True)
    x.add_argument("--output",type=Path,required=True)
    args=x.parse_args()
    result={
        "provenance":"Immutable 0.3 six-STIG published authoring; source-exact research only",
        "five_presets_plus_field_none":{},
        "plus_direct_aliases_for_residual_pairs":{},
    }
    for name in ("rhel_9","windows_11","windows_server_2025"):
        result["five_presets_plus_field_none"][name]=survey(args.authoring_zip,name,{},True)
        result["plus_direct_aliases_for_residual_pairs"][name]=survey(args.authoring_zip,name,RESIDUAL,True)
        print("BENCHMARK",name,flush=True)
        for variant in ("five_presets_plus_field_none","plus_direct_aliases_for_residual_pairs"):
            v=result[variant][name]
            print("STATS",variant,json.dumps({
                k:v[k] for k in ("rules","automated_rules","files_included",
                    "record_aware_metrics","automated_rules_all_quantifiers_abbreviated",
                    "automated_rules_with_explicit_pairs")
            },sort_keys=True),flush=True)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
if __name__=="__main__":
    main()
