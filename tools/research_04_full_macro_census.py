#!/usr/bin/env python3
"""0.4 research-only shorthand census over fresh, pinned SCAP 1.4 conversions.

Every candidate is examined *after* the existing (proven, reversible) 0.3
modernizations. No release content or scanner semantics are changed.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from copy import deepcopy
import json
from pathlib import Path
import re

from measure_full_modernization_census import (
    load_assessments, promote_to_research_03, first_difference,
)
from research_inline_private_components import inline_private, reexpand
from research_static_literal_collections import inline_constants, reexpand_constants
from scap_upconvert_v003.foreach_modernization import modernize_foreach_v1
from research_04_compiled_authoring_macros import simplify_doc, expand_doc

SHELL_CAPABILITIES = {
    "independent.shellcommand", "independent.shellcommand54",
}
MACOS_RE = re.compile(r"(?:mac[_ .-]?os|macos|os[_-]?x|apple)", re.I)
ALIAS_PAIRS = {
    ("one_or_more", "all"): "at_least_one_all_match",
    ("one_or_more", "one_or_more"): "at_least_one_some_match",
    ("none", "all"): "none_exist",
}


def category(capability: str | None, source_artifact: str) -> str:
    """Mutually exclusive: atypical macOS first, then opaque commands."""
    if MACOS_RE.search(source_artifact):
        return "macos_atypical"
    if capability in SHELL_CAPABILITIES or (
        isinstance(capability, str) and "shellcommand" in capability.lower()
    ):
        return "shell_command"
    if not isinstance(capability, str) or not capability:
        return "missing_capability"
    return "structured_other"


def add_counters(dst: dict[str, Counter], cat: str, local: Counter) -> None:
    dst.setdefault(cat,Counter()).update(local)
    dst.setdefault("all_included",Counter()).update(local)
    if cat == "structured_other":
        dst.setdefault("primary_structured",Counter()).update(local)


def scan_test(test: dict, local: Counter, examples: dict, label: str) -> None:
    local["tests"]+=1
    capability=test.get("capability")
    local[f"capability:{capability}"]+=1
    pair=(str(test.get("existence", "<missing>")),
          str(test.get("match", "<missing>")))
    local[f"items_pair:{pair[0]}/{pair[1]}"]+=1
    if pair in ALIAS_PAIRS:
        local[f"items_alias_candidate:{ALIAS_PAIRS[pair]}"]+=1
    states=test.get("states") or []
    if not states:
        local["no_states_tests"]+=1
        if test.get("existence")=="none" and "states" not in test:
            local["state_free_absence_tests"]+=1
            examples.setdefault("state_free_absence",label)
    elif isinstance(states,list):
        local["state_count_total"]+=len(states)
        if len(states)==1:
            local["one_state_tests"]+=1
            examples.setdefault("one_state",label)
    if test.get("reported_elements")=="all":
        local["reported_elements_all"]+=1
    ob=test.get("object")
    if isinstance(ob,dict):
        local["private_inline_object"]+=1
        if ob.get("capability")==capability:
            local["private_same_capability"]+=1
        for field,pred in (ob.get("select") or {}).items():
            if not isinstance(pred,dict):
                continue
            op=pred.get("operation")
            if op in ("equals","pattern_match") and type(pred.get("value")) in (str,int,float,bool):
                local[f"selector_macro:{op}"]+=1
                examples.setdefault("selector_comparison",label)
    if isinstance(states,list):
        for state in states:
            if not isinstance(state,dict) or "field" not in state:
                continue
            local["state_fields"]+=1
            field_pair=(str(state.get("existence","<missing>")),
                        str(state.get("match","<missing>")))
            local[f"field_pair:{field_pair[0]}/{field_pair[1]}"]+=1
            if field_pair in ALIAS_PAIRS:
                local[f"field_alias_candidate:{ALIAS_PAIRS[field_pair]}"]+=1
            op=state.get("operation")
            if op in ("equals","pattern_match") and type(state.get("value")) in (str,int,float,bool):
                local[f"state_macro:{op}"]+=1
                examples.setdefault("state_comparison",label)


def measure(root: Path, source_artifact: str, key: str) -> dict:
    rows=load_assessments(root)
    categories: dict[str,Counter]={}
    examples:dict[str,dict[str,str]]={}
    summary=Counter()
    capabilities=Counter()
    for row in rows:
        original=row["doc"]
        # Mirror exactly the accepted bounded 0.3 research modernization path.
        promoted=promote_to_research_03(original)
        foreach_doc,foreach_report=modernize_foreach_v1(promoted,enabled=True)
        static_doc,static_proof=inline_constants(foreach_doc)
        if reexpand_constants(static_doc,static_proof)!=foreach_doc:
            raise ValueError(f"Static literal reverse mismatch: {row['relative_path']}")
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
        if reexpand(rendered,identity)!=static_doc:
            raise ValueError(f"Locality reverse mismatch: {row['relative_path']}")
        short,shorthand_stats=simplify_doc(rendered)
        if expand_doc(short)!=rendered:
            detail=first_difference(rendered,expand_doc(short))
            raise ValueError(f"Macro reverse mismatch: {row['relative_path']}: {detail}")
        summary["assessments_exact_reverse"]+=1
        summary[f"kind:{row['kind']}"]+=1
        a=rendered["assessment"]
        tests=a.get("tests") or {}
        local_by_cat=defaultdict(Counter)
        for tid,test in tests.items():
            if not isinstance(test,dict):
                continue
            cat=category(test.get("capability"),source_artifact)
            capabilities[(cat,str(test.get("capability")))]+=1
            label=f"{row['relative_path']} :: {tid}"
            local=local_by_cat[cat]
            slots=examples.setdefault(cat,{})
            scan_test(test,local,slots,label)
            # Snapshot meaningful authoring examples with proven exact reexpansion.
        assessment_cats=set(local_by_cat)
        for cat in assessment_cats:
            local_by_cat[cat]["assessments_with_category"]+=1
        if len(tests)==1 and a.get("evaluate")=={"test":next(iter(tests))}:
            cat=next(iter(assessment_cats),"missing_capability")
            local_by_cat[cat]["sole_test_direct_evaluate"]+=1
            examples.setdefault(cat,{}).setdefault("sole_test",row['relative_path'])
        # Count proposed syntax opportunities per capability class at the original scope.
        # These counts are *not* additive lines saved.
        for cat,ctr in local_by_cat.items():
            add_counters(categories,cat,ctr)
        summary["tests_examined"]+=len(tests)
    return {
        "format":"scap-ng-04-full-corpus-shorthand-research-v1",
        "source_artifact":source_artifact,
        "benchmark_key":key,
        "source_content_type":"macos_atypical" if MACOS_RE.search(source_artifact) else "regular",
        "modernization":"foreach_v1+static_literal+private_locality (exact reverse verified)",
        "totals":dict(summary),
        "categories":{k:dict(v) for k,v in sorted(categories.items())},
        "capabilities":{f"{c} / {cap}":v for (c,cap),v in sorted(capabilities.items())},
        "examples":examples,
        "semantic_proof_scope":"exact parsed NG structural reverse; not OVAL scanner differential",
    }


def aggregate(root:Path)->dict:
    reports=[json.loads(p.read_text()) for p in sorted(root.rglob("reports/*.json"))]
    statuses=[json.loads(p.read_text()) for p in sorted(root.rglob("status/*.json"))]
    if len(statuses)!=65 or len({x["source_artifact"] for x in statuses})!=65:
        raise ValueError(f"Expected 65 unique status records, got {len(statuses)}")
    generated=[s for s in statuses if s["status"]=="generated"]
    blocked=[s for s in statuses if s["status"]=="blocked"]
    if len(reports)!=len(generated):
        raise ValueError(f"Missing report(s): {len(reports)} for {len(generated)} generated")
    if {x["source_artifact"] for x in generated}!={r["source_artifact"] for r in reports}:
        raise ValueError("Report and generated source identities differ")
    known_sql=(
        "U_MS_SQL_Server_2016_Database_", "U_MS_SQL_Server_2016_Instance_",
        "U_MS_SQL_Server_2022_Database_", "U_MS_SQL_Server_2022_Instance_",
    )
    for s in blocked:
        if not any(s["source_artifact"].startswith(p) for p in known_sql) or (
            "independent.sqlext" not in s.get("failure_tail","")
        ):
            raise ValueError(f"Unexpected conversion blocker: {s['source_artifact']}")
    sums=Counter()
    categories=defaultdict(Counter)
    per_package=[]
    for report in reports:
        sums.update(report["totals"])
        for cat,metrics in report["categories"].items():
            categories[cat].update(metrics)
        per_package.append({
            "source_artifact":report["source_artifact"],
            "source_content_type":report["source_content_type"],
            "assessments":report["totals"]["assessments_exact_reverse"],
            "tests":report["totals"]["tests_examined"],
            "structured_tests":report["categories"].get("primary_structured",{}).get("tests",0),
            "shell_command_tests":report["categories"].get("shell_command",{}).get("tests",0),
            "macos_atypical_tests":report["categories"].get("macos_atypical",{}).get("tests",0),
        })
    return {
        "format":"scap-ng-04-full-corpus-shorthand-research-aggregate-v1",
        "source_rev":"8c8e5dff860af6b1290ee9273a282db24278f8d5",
        "benchmarks_total":len(statuses),
        "benchmarks_generated":len(generated),
        "benchmarks_expected_sql_blockers":len(blocked),
        "totals":dict(sums),
        "categories":{k:dict(v) for k,v in sorted(categories.items())},
        "per_package":sorted(per_package,key=lambda x:x["source_artifact"]),
        "blocked":blocked,
        "limitations":[
            "Counts across 61 generated and four expected SQL-extension blockers, not 65 complete outputs.",
            "macOS shell-command-heavy converted sources are counted separately and excluded from primary structured rankings.",
            "Shell-command capabilities are separated on other platforms too.",
            "Census is based on exactly reversible 0.3 research-modernized Assessments, not a scanner-execution differential.",
            "Applicability and Rule Assessments are both included, and repeated Test definitions across benchmarks count per occurrence.",
            "Candidate counts overlap; presence alone is not a claim of authoring readability.",
        ],
    }


def cli():
    p=argparse.ArgumentParser()
    sp=p.add_subparsers(dest="command",required=True)
    one=sp.add_parser("measure")
    one.add_argument("root",type=Path)
    one.add_argument("--source-artifact",required=True)
    one.add_argument("--key",required=True)
    one.add_argument("--output",type=Path,required=True)
    allp=sp.add_parser("aggregate")
    allp.add_argument("root",type=Path)
    allp.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    result=(measure(args.root,args.source_artifact,args.key)
            if args.command=="measure" else aggregate(args.root))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
        "source":getattr(args,"source_artifact","all"),
        "totals":result.get("totals"),
        "category_counts":{k:{"tests":v.get("tests",0),"assessments":v.get("assessments_with_category",0)}
                           for k,v in result.get("categories",{}).items()},
        "status":"exact_reverse_verified" if args.command=="measure" else "complete_65_source_accounting"
    }))
if __name__=="__main__":
    cli()
