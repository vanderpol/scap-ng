#!/usr/bin/env python3
"""Read-only survey of explicit compile-time convenience opportunities in six-STIG 0.3 authoring.

Counts structural shapes, not semantic equivalence of invented macros.
Never changes the release, and never considers missing explicit properties defaultable.
"""
from collections import Counter, defaultdict
from pathlib import Path
import argparse
import json
import zipfile
import yaml


def record_predicates(value, ctr):
    if isinstance(value, list):
        for child in value:
            record_predicates(child, ctr)
    elif isinstance(value, dict):
        if "operation" in value and "value" in value:
            op=value.get("operation")
            if isinstance(op, str):
                ctr["operations"][op]+=1
                ctr["predicate_shapes"][tuple(sorted(value.keys()))]+=1
                if op=="equals":
                    ctr["equality_count"]+=1
                if op=="pattern_match":
                    ctr["regex_count"]+=1
        for child in value.values():
            record_predicates(child, ctr)


def audit(path):
    counts=Counter()
    by_benchmark=defaultdict(Counter)
    operations=Counter()
    selector_ops=Counter()
    state_ops=Counter()
    report_modes=Counter()
    capabilities=Counter()
    selectors=Counter()
    test_counts=Counter()
    state_counts=Counter()
    equality_examples=[]
    simple_single_examples=[]
    no_state_examples=[]
    selector_examples=[]
    object_repetitions=[]
    with zipfile.ZipFile(path) as z:
        if z.testzip() is not None:
            raise ValueError("Corrupt release authoring zip")
        for filename in sorted(z.namelist()):
            if not filename.startswith("authoring/") or not filename.endswith(".automated.yaml"):
                continue
            doc=yaml.safe_load(z.read(filename))
            a=(doc or {}).get("assessment")
            if not isinstance(a, dict) or a.get("mode")!="automated":
                continue
            key=filename.split("/")[1]
            counts["automated_assessment_files"]+=1
            by_benchmark[key]["automated_assessment_files"]+=1
            tests=a.get("tests") or {}
            if not isinstance(tests, dict):
                raise ValueError(f"Invalid tests in {filename}")
            test_counts[str(len(tests))]+=1
            counts["named_tests"]+=len(tests)
            by_benchmark[key]["named_tests"]+=len(tests)
            if len(tests)==1:
                counts["single_test_assessments"]+=1
                tid=next(iter(tests))
                ev=a.get("evaluate")
                if ev=={"test":tid}:
                    counts["single_test_direct_evaluate"]+=1
                    if len(simple_single_examples)<8:
                        simple_single_examples.append({"file":filename,"test":tid,"evaluate":ev})
                else:
                    counts["single_test_nondirect_evaluate"]+=1
            for tid,t in tests.items():
                if not isinstance(t,dict):
                    continue
                if isinstance(t.get("capability"),str):
                    capabilities[t["capability"]]+=1
                states=t.get("states") or []
                state_counts[str(len(states))]+=1
                if len(states)==1:
                    counts["one_state_tests"]+=1
                if not states:
                    counts["zero_state_tests"]+=1
                    if len(no_state_examples)<6:
                        no_state_examples.append({"file":filename,"test":tid,
                                                  "existence":t.get("existence"),
                                                  "match":t.get("match")})
                if "reported_elements" in t:
                    counts["tests_with_reported_elements"]+=1
                    report_modes[str(t["reported_elements"])]+=1
                ob=t.get("object")
                if isinstance(ob,dict) and isinstance(ob.get("capability"),str):
                    counts["tests_with_private_inline_object_capability"]+=1
                    if ob["capability"]==t.get("capability"):
                        counts["repeated_same_capability_test_and_inline_object"]+=1
                        if len(object_repetitions)<7:
                            object_repetitions.append({"file":filename,"test":tid,"capability":t["capability"]})
                    else:
                        counts["mismatched_capability_private_object"]+=1
                    selection=ob.get("select") or {}
                    if isinstance(selection,dict):
                        for sk,sv in selection.items():
                            if isinstance(sv,dict) and "operation" in sv and "value" in sv:
                                selector_ops[str(sv["operation"])]+=1
                                selectors[str(sk)]+=1
                                counts["selector_scalar_predicates"]+=1
                                if sv["operation"]=="equals":
                                    counts["selector_equality_predicates"]+=1
                                    if len(selector_examples)<7:
                                        selector_examples.append({"file":filename,"test":tid,
                                                                  "field":sk,"value":sv["value"]})
                                if sv["operation"]=="pattern_match":
                                    counts["selector_regex_predicates"]+=1
                for state in states:
                    if not isinstance(state,dict):
                        continue
                    if "field" in state and "value" in state and "operation" in state:
                        op=str(state["operation"])
                        state_ops[op]+=1
                        counts["direct_field_predicates"]+=1
                        if op=="equals":
                            counts["direct_field_equal_predicates"]+=1
                            if len(equality_examples)<7:
                                equality_examples.append({"file":filename,"test":tid,
                                                           "field":state["field"],"value":state["value"]})
            all_ops={"operations":Counter(),"predicate_shapes":Counter()}
            record_predicates(a, all_ops)
            operations.update(all_ops["operations"])
    return {
        "source_release":path.name,
        "metrics":dict(counts),
        "per_benchmark":{k:dict(v) for k,v in sorted(by_benchmark.items())},
        "named_tests_per_assessment":dict(sorted(test_counts.items(),key=lambda x:int(x[0]))),
        "states_per_test":dict(sorted(state_counts.items(),key=lambda x:int(x[0]))),
        "all_predicate_operations":dict(operations.most_common()),
        "direct_field_operations":dict(state_ops.most_common()),
        "inline_object_selector_operations":dict(selector_ops.most_common()),
        "inline_object_selector_fields":dict(selectors.most_common()),
        "reported_elements_values":dict(report_modes.most_common()),
        "capabilities":dict(capabilities.most_common(20)),
        "examples":{
            "single_direct_evaluate":simple_single_examples,
            "inline_duplicate_capability":object_repetitions,
            "direct_field_equality":equality_examples,
            "selector_equality":selector_examples,
            "zero_state":no_state_examples,
        },
        "limits":[
            "Counts are based only on six released 0.3 authoring STIGs, not all OVAL.",
            "Counts refer to independent presentation candidates and may overlap. Do not sum them as distinct lines saved.",
            "Most proposed shortcuts have not been proved valid or complete; these are frequency metrics only.",
            "All candidate source macros must expand to complete explicit 0.3 schema-valid longhand before packaging.",
            "A quoted scalar or typed operator can be required for special version/address and regex semantics.",
        ],
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--authoring-zip",type=Path,required=True)
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    result=audit(args.authoring_zip)
    output=json.dumps(result,indent=2,sort_keys=True,default=str)
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(output+"\n")
    print(output)

if __name__=="__main__":
    main()
