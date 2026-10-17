#!/usr/bin/env python3
"""#235/#229: six-STIG all_exist proof under an existing-Item-only proposal.

The known OVAL generic result combiner is the local reference, NOT an
independent scanner. Keep original files immutable, identify any lost outcomes.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from itertools import product
from pathlib import Path
import argparse, hashlib, json, zipfile
import yaml

from oval_result_truth_tables import (
    TRUE, FALSE, ERROR, UNKNOWN, NOT_EVALUATED, NOT_APPLICABLE,
    evaluate_collected_object_test, aggregate_existence,
)
from research_04_all_exist_intent_census import (
    PINNED, resolved_source, describe_object,
)

FLAGS = ("complete", "incomplete", "error", "not collected",
         "not applicable", "does not exist")
OUTCOMES = (TRUE, FALSE, ERROR, UNKNOWN, NOT_EVALUATED, NOT_APPLICABLE)
MATCH_MODE = {
    "all_exist": None,
    "all_exist_and_all_match": "all",
    "all_exist_and_none_match": "none satisfy",
}
CHECKS = {"all": "all", "none satisfy": "none satisfy"}

def fixtures():
    """All bounded permitted result populations; root Item status is exists."""
    for flag in FLAGS:
        for n in range(4):
            for mode in (None, "all", "none satisfy"):
                # An Item has a State result only if a source State exists.
                for outcomes in (product(OUTCOMES, repeat=n) if mode else [()]):
                    yield flag, n, mode, outcomes

def evaluate(flag, n, mode, outcomes, existence):
    return evaluate_collected_object_test(
        flag,
        existence=existence,
        check=CHECKS.get(mode,"all"),
        item_results=list(outcomes) if mode else None,
        has_state=bool(mode),
        exists=n,
    )

def audit(archive):
    digest=hashlib.sha256(Path(archive).read_bytes()).hexdigest()
    if digest!=PINNED:raise AssertionError("source archive does not match pinned r3 SHA")
    tests=[]
    with zipfile.ZipFile(archive) as z:
        if z.testzip():raise AssertionError("corrupt corpus archive")
        for path in sorted(z.namelist()):
            if not(path.startswith("authoring/") and "/assessments/" in path
                   and path.endswith(".yaml")): continue
            assessment=(yaml.safe_load(z.read(path)) or {}).get("assessment") or {}
            test_defs=assessment.get("tests")
            if assessment.get("mode")!="automated" or not isinstance(test_defs,dict):
                continue
            for tid,test in test_defs.items():
                source_mode=test.get("collected_items_require")
                if source_mode not in MATCH_MODE:continue
                mode=MATCH_MODE[source_mode]
                has_state=bool(test.get("states"))
                if has_state != (mode is not None):
                    raise AssertionError("source state/Item-mode disagreement "+path+":"+tid)
                obj,origin=resolved_source(assessment,test)
                tests.append({
                    "source":path,"test":tid,
                    "title":test.get("test_title"),
                    "capability":test.get("capability"),
                    "source_mode":source_mode,
                    "has_state":has_state,
                    "check":mode or "state_free",
                    "selection":describe_object(obj)["potential_expected_population"],
                    "collection":describe_object(obj)["shape"],
                    "object_origin":origin,
                })
    if len(tests)!=201 or sum(t["has_state"] for t in tests)!=74:
        raise AssertionError("unexpected 201-Test population")

    cases=Counter()
    divergence=defaultdict(list)
    for flag,n,mode,outcomes in fixtures():
        a=evaluate(flag,n,mode,outcomes,"all_exist")
        b=evaluate(flag,n,mode,outcomes,"at_least_one_exists")
        cases["vectors_total"]+=1
        if a!=b:
            key=f"{flag}:{mode or 'state_free'}"
            cases["divergences_total"]+=1
            cases[f"divergence_{key}"]+=1
            if len(divergence[key])<4:
                divergence[key].append({
                    "flag":flag,"existing_items":n,
                    "states":list(outcomes),"all_exist":a,
                    "at_least_one_exists":b})
        elif flag=="complete":
            cases["complete_existing_only_agree"]+=1

    # Test-level proof classification uses the same generic check as the source.
    # The independent State comparator is not modified in this experiment.
    per_test=Counter()
    by_folder=defaultdict(Counter)
    by_cap=defaultdict(Counter)
    for t in tests:
        per_test["source_tests"]+=1
        per_test["with_state" if t["has_state"] else "state_free"]+=1
        per_test["equivalent_when_complete_and_only_existing_items"]+=1
        if not t["has_state"]:
            per_test["also_equivalent_with_incomplete_under_real_items_only"]+=1
        else:
            per_test["incomplete_decisive_result_risk"]+=1
        by_folder[t["source"].split("/")[1]][t["check"]]+=1
        by_cap[t["capability"]][t["check"]]+=1

    # All root Items would have status exists in the proposed native result
    # profile; the current OVAL generic reference still permits error and
    # not_collected root statuses. Document remaining differences explicitly.
    status_counterexamples=[]
    for extra in ("does_not_exist","error","not_collected"):
        kwargs={"exists":1,extra:1}
        status_counterexamples.append({
            "one_existing_plus":extra,
            "all_exist":aggregate_existence("all_exist",**kwargs),
            "at_least_one_exists":aggregate_existence("at_least_one_exists",**kwargs),
            "native_proposal":(
                "forbidden phantom root Item" if extra=="does_not_exist"
                else "status must move into collector/field semantics before any full equivalence claim"
            )
        })

    return {
        "status":"SOURCE-GROUNDED GENERIC RESULT SEMANTIC ANALYSIS, NOT SCANNER PARITY",
        "pinned_source_sha256":digest,
        "test_counts":dict(per_test),
        "generic_result_vectors":dict(cases),
        "bounded_divergence_examples":dict(divergence),
        "mixed_item_status_counterexamples":status_counterexamples,
        "by_source_folder":{k:dict(v) for k,v in sorted(by_folder.items())},
        "by_capability":{k:dict(v) for k,v in sorted(by_cap.items())},
        "all_201_test_classifications":tests,
        "constraints":[
            "Test results are computed by the checked-in OVAL 5.12.3 generic model, not a scanner.",
            "Complete flags with root Items limited to exists give equal behavior for all 201, not general migration parity.",
            "State-free (127) cases agree on the modeled complete/incomplete/error/not-collected flags, under the existing-only Item restriction.",
            "State-bearing (74) may differ when incomplete scans contain a decisive per-Item failure; preserving original source results remains required.",
            "Mixed root Item statuses error and not_collected remain a difference unless native schema defines their representation in collection/field status.",
            "A native test cannot infer that every *named selector value* exists from all observed Items matching.",
            "No automatic OVAL XML rewriting, STIG normalization, or schema decisions were made.",
        ]
    }

def report_md(result):
    c=result["test_counts"]
    lines=[
        "# Can the 201 Test-level `all_exist` requirements be simplified?",
        "",
        "**Research evidence only; no adopted 0.4 authoring or result schema.**",
        "",
        "Pinned 2026-10-15 r3 six-STIG source; imported source Tests stay unchanged.",
        "",
        "| Classification | Tests | Meaning |",
        "| --- | ---: | --- |",
        f"| `all_exist` Tests audited | {c['source_tests']} | Six-STIG distinct named Tests |",
        f"| State-free | {c['state_free']} | Check only Item presence |",
        f"| State-bearing | {c['with_state']} | Also evaluate Item State conditions |",
        f"| Equivalent under **complete**, existing-root-Item-only collection | {c['equivalent_when_complete_and_only_existing_items']} | Same presence and State results, including error/unknown **State results** |",
        f"| Also equivalent on modeled **incomplete** collection under existing-only Items | {c['also_equivalent_with_incomplete_under_real_items_only']} | **State-free only**; no decisive State comparison |",
        f"| Cases needing incomplete-scan policy | {c['incomplete_decisive_result_risk']} | State-bearing; at-least-one may yield decisive failure whereas all-exist remains unknown |",
        "",
        "## What the reference actually proves",
        "",
        "- Existing Items alone give identical existence outcomes for `all_exist` and `at_least_one_exists` in a complete collection.",
        "- Empty and missing collections are handled through collection flags/zero Items, not fabricated Item identities.",
        "- The two choices differ in OVAL's generic tables with a mixed Item-status collection: a real Item plus error/not-collected/does-not-exist Item.",
        "- **Banning fabricated does-not-exist Items resolves only one of those differences.** Failures must be represented without corrupting the six result outcomes.",
        "- The local generic reference treats incomplete State-bearing scans specially; normalizing them without a new native semantic contract changes results.",
        "",
        "## Generic result counterexamples",
        "",
    ]
    for k,rows in result["bounded_divergence_examples"].items():
        lines.append(f"### {k}")
        lines.append("")
        for row in rows[:2]:
            lines.append(
                f"- existing={row['existing_items']}, State outcomes={row['states']}: "
                f"all_exist→`{row['all_exist']}`, at_least_one→`{row['at_least_one_exists']}`")
        lines.append("")
    lines+=["## Example source-folder distribution", "",
            "The shared folder is reused across benchmarks and is not a seventh STIG.",
            "", "| Folder | Presence only | All State matches | No State matches |",
            "| --- | ---: | ---: | ---: |"]
    for folder,modes in result["by_source_folder"].items():
        lines.append(f"| {folder} | {modes.get('state_free',0)} | {modes.get('all',0)} | {modes.get('none satisfy',0)} |")
    lines+=["", "## Remaining owner-facing design choices", "",
        "1. Decide whether all native root Items must have `exists` status, with missing/unreadable/not-collected represented through collection or field results; preserve all the required six-state outcomes.",
        "2. For State-bearing source `all_exist` Tests, decide what native tests do on incomplete observations. Preserve existing OVAL meaning in the importer until differential parity is demonstrated.",
        "3. Represent mandatory expected identities separately from `all *collected* Items` (e.g., every listed audit-tool path must exist versus every found path must match).",
        "4. Retain a source-exact compatibility path or a precise conversion blocker for OVAL partial missing Items, with actual original XML/source provenance.",
        "",
        "## Provenance and boundaries", "",
    ]
    lines.extend("- "+x for x in result["constraints"])
    lines.append("")
    return "\n".join(lines)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--archive",required=True)
    p.add_argument("--json",required=True)
    p.add_argument("--markdown",required=True)
    args=p.parse_args()
    result=audit(args.archive)
    Path(args.json).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    Path(args.markdown).write_text(report_md(result))
    print(json.dumps({"tests":result["test_counts"],
                      "vectors":result["generic_result_vectors"],
                      "counterexamples":result["mixed_item_status_counterexamples"]},indent=2))
