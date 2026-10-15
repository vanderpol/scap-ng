#!/usr/bin/env python3
"""Research-only sensitivity analysis of RHEL9 quantifier shorthand coverage.

Does NOT adopt syntax or modify any 0.3 benchmark/content. Compare previously
tested three-preset vocabulary with two additional exact pair aliases, using
immutable released RHEL9 source and whole-Assessment structural reversibility.
"""
import argparse
import json
from pathlib import Path
import zipfile

import research_04_rhel9_compact_preview as preview

ADDITIONAL={
    ("all","all"): "all_exist_all_match",
    ("optional","all"): "optional_all_match",
}

def source_sensitivity(path):
    with zipfile.ZipFile(path) as z:
        docs,raw=preview.archive_contents(z)
    first=preview.single_stage(docs,2)
    first_report=preview.make_report(docs,raw,first,first)
    previous=dict(preview.PAIR_ALIASES)
    inverse=dict(preview.PAIR_INVERSE)
    earlier_field_absence=preview.FIELD_ABSENCE_ENABLED
    earlier_exact_one=preview.EXACT_ONE_NATURAL_ENABLED
    try:
        preview.PAIR_ALIASES.update(ADDITIONAL)
        preview.PAIR_INVERSE.update({
            v:{"existence":p[0],"match":p[1]} for p,v in ADDITIONAL.items()
        })
        second=preview.single_stage(docs,2)
        second_report=preview.make_report(docs,raw,second,second)
        # A third research-only scenario. Absence of State-field entities is
        # NOT the same semantic scope as zero Items in a State-free Test.
        # Both lower to the exact original none/all pair, however.
        preview.FIELD_ABSENCE_ENABLED=True
        third=preview.single_stage(docs,2)
        third_report=preview.make_report(docs,raw,third,third)
        # Preserve explicit OVAL cardinality "only one exists" rather than
        # trying to make exact-one collection equivalent to one-or-more.
        preview.EXACT_ONE_NATURAL_ENABLED=True
        fourth=preview.single_stage(docs,2)
        fourth_report=preview.make_report(docs,raw,fourth,fourth)
    finally:
        preview.FIELD_ABSENCE_ENABLED=earlier_field_absence
        preview.EXACT_ONE_NATURAL_ENABLED=earlier_exact_one
        preview.PAIR_ALIASES.clear();preview.PAIR_ALIASES.update(previous)
        preview.PAIR_INVERSE.clear();preview.PAIR_INVERSE.update(inverse)
    a=first_report["rules"]
    b=second_report["rules"]
    first_rows={x["rule_id"]:x for x in first_report["rule_classifications"]}
    second_rows={x["rule_id"]:x for x in second_report["rule_classifications"]}
    changed=[
        {"rule_id":rid,
         "before_explicit_pairs":first_rows[rid]["quantifier_longhand_count"],
         "after_explicit_pairs":second_rows[rid]["quantifier_longhand_count"]}
        for rid in sorted(first_rows)
        if first_rows[rid]["quantifier_longhand_count"] !=
           second_rows[rid]["quantifier_longhand_count"]
    ]
    def classify_metric(report):
        rules=report["rules"]
        counts=report["assessments"]["stage2_plus_scalar_comparison"]
        return {
            "automated_default":rules["automated_default"],
            "automated_all_quantifiers_compact":rules["automated_all_quantifiers_compact"],
            "automated_needing_explicit_quantifier_pairs":rules["automated_needing_explicit_quantifier_pairs"],
            "automated_no_pair_or_comparison_longhand":rules["automated_no_pair_or_comparison_longhand"],
            "automated_no_pair_or_comparison_longhand_and_simple_evaluate":rules["automated_no_pair_or_comparison_longhand_and_simple_evaluate"],
            "remaining_explicit_test_pairs":counts["test_explicit_pair"],
            "remaining_explicit_field_pairs":counts["field_explicit_pair"],
            "shortened_test_pairs":sum(v for k,v in counts.items() if k.startswith("test_require:")),
            "shortened_field_pairs":sum(v for k,v in counts.items() if k.startswith("field_require:")),
        }
    return {
        "research_only":True,
        "source_release":"v0.3.0-six-stig-typed-operators-5796d016b12f",
        "baseline_presets":{str(k):v for k,v in previous.items()},
        "added_presets":{str(k):v for k,v in ADDITIONAL.items()},
        "initial":classify_metric(first_report),
        "after_two_new_exact_presets":classify_metric(second_report),
        "after_field_none_exist_alias":classify_metric(third_report),
        "after_exactly_one_exists_alias":classify_metric(fourth_report),
        "exactly_one_added_occurrences":(
            fourth[2]["test_require:only_one_exists"] +
            fourth[2]["test_require:only_one_exists_and_matches"]
        ),
        "exact_one_state_free_tests":fourth[2]["test_require:only_one_exists"],
        "exact_one_with_state_tests":fourth[2]["test_require:only_one_exists_and_matches"],
        "field_none_exist_added_occurrences":(
            third[2]["field_require:none_exist"] - second[2]["field_require:none_exist"]
        ),
        "field_none_exist_relevant_assessments":sum(
            1 for a in third[0].values()
            if any(
                isinstance(test,dict) and any(
                    isinstance(entry,dict) and len(entry)==1 and
                    isinstance(next(iter(entry.values())),dict) and
                    next(iter(entry.values())).get("require")=="none_exist"
                    for entry in (test.get("states") or [])
                )
                for test in (a["assessment"].get("tests") or {}).values()
            )
        ),
        "changed_rule_count":len(changed),
        "changed_rule_sample":changed[:24],
        "proof":"Both stages exactly round-trip each Assessment to original parsed 0.3; no runtime evaluator equivalence claimed.",
        "interpretation_limits":[
            "The extra two presets are a deliberately narrow sensitivity test, not approved new language features.",
            "all_exist_all_match and optional_all_match must be explicitly taught: they have distinct empty-collection outcomes.",
            "Field-level none_exist is an exact none/all alias for missing entities of a collected Item. Test-level none_exist remains restricted to State-free zero-Item checks, and match:none is a different meaning.",
            "Full compact grammar still includes other complex Object/Set/Variable, operation and evaluation structures.",
            "Numbers count Rule-level selected Assessments, including resolved shared definitions, not a declaration of fully simplified grammar."
        ]
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--authoring-zip",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    args=p.parse_args()
    r=source_sensitivity(args.authoring_zip)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(r,sort_keys=True,indent=2)+"\n")
    print(json.dumps(r,sort_keys=True,indent=2))
if __name__=="__main__":
    main()
