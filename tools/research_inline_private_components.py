#!/usr/bin/env python3
"""Research-only inline-private-component renderer.

This does NOT define SCAP-NG syntax. It tests one presentation hypothesis:
an Object or State referenced only by one Test may be colocated inside that
Test, while genuinely shared components remain Assessment-scoped and named.

The renderer preserves the complete component payload and writes an identity
map. It then mechanically re-expands the research form and requires structural
identity with the normalized source Assessment.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

import yaml


RESEARCH_HEADER = """# RESEARCH ONLY — NOT AN ACCEPTED SCAP-NG FORMAT.
# Locality experiment: single-use Objects/States are inlined into their Test.
# Shared/referenced components remain Assessment-scoped and named.
"""


def scalar_reference_counts(node: Any, candidates: set[str]) -> dict[str, int]:
    counts={name:0 for name in candidates}
    def visit(value: Any):
        if isinstance(value, dict):
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)
        elif isinstance(value, str) and value in counts:
            counts[value]+=1
    visit(node)
    return counts


def direct_test_reference_counts(
    tests: dict[str, Any],
    object_ids: set[str],
    state_ids: set[str],
) -> tuple[dict[str, int], dict[str, int]]:
    """Count only the direct Test -> Object/State edges.

    The difference between these counts and scalar_reference_counts() is graph
    plumbing: Variable, Set, Filter, or other non-Test references.
    """
    object_counts={name:0 for name in object_ids}
    state_counts={name:0 for name in state_ids}
    for test in tests.values():
        if not isinstance(test,dict):
            continue
        obj=test.get("object")
        if isinstance(obj,str) and obj in object_counts:
            object_counts[obj]+=1
        states=test.get("states")
        if isinstance(states,str):
            states=[states]
        if isinstance(states,list):
            for state in states:
                if isinstance(state,str) and state in state_counts:
                    state_counts[state]+=1
    return object_counts,state_counts


def retention_reason(total_refs: int, direct_test_refs: int) -> str:
    """Explain why a named component cannot be Test-local under the v1 rule."""
    graph_refs=max(0,total_refs-direct_test_refs)
    if direct_test_refs >= 2 and graph_refs:
        return "multiple_tests_and_graph"
    if direct_test_refs >= 2:
        return "multiple_tests"
    if direct_test_refs == 1 and graph_refs:
        return "test_and_graph"
    if direct_test_refs == 0 and graph_refs:
        return "graph_only"
    if direct_test_refs == 1:
        # A one-Test-only node should have been inlined. Keeping this category
        # makes the census fail visibly if a later transform leaves one behind.
        return "unexpected_single_test_only"
    return "unreferenced_or_other"


def scalar_reference_contexts(node: Any, candidates: set[str]) -> dict[str, dict[str, int]]:
    """Count candidate scalar references by broad semantic consumer context."""
    counts={name:{} for name in candidates}

    def classify(path: tuple[str, ...]) -> str:
        if len(path)>=3 and path[0]=="tests":
            if path[2]=="object":
                return "test_object"
            if path[2]=="states":
                return "test_state"
            return "test_other"
        if "filters" in path or "filter" in path:
            return "filter"
        if path and path[0]=="variables":
            return "variable"
        if path and path[0]=="objects":
            return "object_graph"
        if path and path[0]=="states":
            return "state_graph"
        if path and path[0]=="evaluate":
            return "evaluate"
        return "other"

    def visit(value: Any, path: tuple[str, ...]=()):
        if isinstance(value,dict):
            for key,child in value.items():
                visit(child,path+(str(key),))
        elif isinstance(value,list):
            for i,child in enumerate(value):
                visit(child,path+(str(i),))
        elif isinstance(value,str) and value in counts:
            context=classify(path)
            bucket=counts[value]
            bucket[context]=bucket.get(context,0)+1

    visit(node)
    return counts


def context_signature(contexts: dict[str, int]) -> str:
    if not contexts:
        return "unreferenced"
    return "+".join(
        f"{name}:{count}"
        for name,count in sorted(contexts.items())
        if count
    ) or "unreferenced"


def normalized_text(doc: dict) -> str:
    return yaml.safe_dump(doc, sort_keys=False, width=120, allow_unicode=True)


def first_difference(expected: Any, actual: Any, path: str="$") -> str | None:
    if type(expected) is not type(actual):
        return f"{path}: type {type(expected).__name__} != {type(actual).__name__}"
    if isinstance(expected,dict):
        if set(expected) != set(actual):
            missing=sorted(set(expected)-set(actual))
            extra=sorted(set(actual)-set(expected))
            return f"{path}: keys missing={missing} extra={extra}"
        for key in expected:
            found=first_difference(expected[key],actual[key],f"{path}.{key}")
            if found:
                return found
        return None
    if isinstance(expected,list):
        if len(expected)!=len(actual):
            return f"{path}: list length {len(expected)} != {len(actual)}"
        for index,(left,right) in enumerate(zip(expected,actual)):
            found=first_difference(left,right,f"{path}[{index}]")
            if found:
                return found
        return None
    if expected != actual:
        return f"{path}: expected={expected!r} actual={actual!r}"
    return None


def metrics(doc: dict) -> dict:
    a=doc.get("assessment",{})
    tests=a.get("tests") or {}
    objects=a.get("objects") or {}
    states=a.get("states") or {}
    variables=a.get("variables") or {}
    refs=0
    for test in tests.values():
        if isinstance(test.get("object"),str):
            refs+=1
        st=test.get("states")
        if isinstance(st,list):
            refs+=sum(isinstance(x,str) for x in st)
        elif isinstance(st,str):
            refs+=1
    named_candidates=set(objects)|set(states)
    named_refs=sum(scalar_reference_counts(a,named_candidates).values())
    text=normalized_text(doc)
    return {
        "objects":len(objects),
        "states":len(states),
        "tests":len(tests),
        "variables":len(variables),
        "test_component_cross_references":refs,
        "named_component_cross_references":named_refs,
        "normalized_lines":len(text.splitlines()),
        "normalized_bytes":len(text.encode("utf-8")),
    }


def inline_private(
    doc: dict,
    *,
    inline_private_set_operands: bool = False,
    inline_private_filtered_set_operands: bool = False,
    inline_state_consumers: bool = False,
) -> tuple[dict, dict]:
    out=copy.deepcopy(doc)
    a=out["assessment"]
    objects=a.get("objects") or {}
    states=a.get("states") or {}
    tests=a.get("tests") or {}
    candidates=set(objects)|set(states)
    refs=scalar_reference_counts(a,candidates)
    contexts=scalar_reference_contexts(a,candidates)
    direct_object_refs,direct_state_refs=direct_test_reference_counts(
        tests,set(objects),set(states)
    )

    identity={
        "status":"research_only_not_accepted_design",
        "assessment_id":a.get("id"),
        "original_sections_present":{
            "objects":"objects" in a,
            "states":"states" in a,
        },
        "inlined_objects":{},
        "inlined_set_operand_objects":[],
        "inlined_states":{},
        "inlined_state_consumer_occurrences":[],
        "shared_objects":[],
        "shared_states":[],
        "retained_object_reasons":{},
        "retained_state_reasons":{},
        "retained_object_contexts":{},
        "retained_state_contexts":{},
    }

    remove_objects=set()
    remove_states=set()

    if inline_private_set_operands:
        # Bounded v2 locality experiment: inline only leaf Objects that are used
        # exactly once as an unfiltered Set operand of another top-level Object.
        # Do not recurse through nested Sets, filters, Variables, or other graph
        # edges. This specifically tests whether common union-of-private-sources
        # layouts can become local without changing Set semantics.
        for parent_id,parent in list(objects.items()):
            if not isinstance(parent,dict):
                continue
            set_node=parent.get("set")
            if not isinstance(set_node,dict):
                continue
            operands=set_node.get("operands")
            if not isinstance(operands,list):
                continue
            for index,operand in enumerate(operands):
                if not isinstance(operand,dict):
                    continue
                child_id=operand.get("object")
                filters=operand.get("filters")
                if (
                    not isinstance(child_id,str)
                    or child_id not in objects
                    or refs.get(child_id)!=1
                    or (
                        not inline_private_filtered_set_operands
                        and isinstance(filters,list)
                        and filters
                    )
                    or (filters not in (None,[]) and not isinstance(filters,list))
                ):
                    continue
                child=objects[child_id]
                if not isinstance(child,dict) or isinstance(child.get("set"),dict):
                    continue
                operand["object"]=copy.deepcopy(child)
                identity["inlined_set_operand_objects"].append({
                    "object":child_id,
                    "parent_object":parent_id,
                    "operand_index":index,
                    "filter_count":len(filters) if isinstance(filters,list) else 0,
                })
                remove_objects.add(child_id)

    for test_id,test in tests.items():
        obj=test.get("object")
        if isinstance(obj,str) and obj in objects and refs.get(obj)==1:
            test["object"]=copy.deepcopy(objects[obj])
            identity["inlined_objects"][obj]=f"assessment.tests.{test_id}.object"
            remove_objects.add(obj)

        st=test.get("states")
        if isinstance(st,str):
            st=[st]
            test["states"]=st
        if isinstance(st,list):
            rendered=[]
            for idx,entry in enumerate(st):
                if isinstance(entry,str) and entry in states and refs.get(entry)==1:
                    rendered.append(copy.deepcopy(states[entry]))
                    identity["inlined_states"][entry]=f"assessment.tests.{test_id}.states[{idx}]"
                    remove_states.add(entry)
                else:
                    rendered.append(entry)
            test["states"]=rendered

    for name in remove_objects:
        objects.pop(name,None)
    for name in remove_states:
        states.pop(name,None)

    if inline_state_consumers and states:
        occurrences=identity["inlined_state_consumer_occurrences"]

        # Inline remaining named States into Test consumers. Single-use Test
        # States were already handled above; this covers reused States.
        for test_id,test in tests.items():
            values=test.get("states")
            if isinstance(values,str):
                values=[values]
                test["states"]=values
            if not isinstance(values,list):
                continue
            for index,entry in enumerate(list(values)):
                if isinstance(entry,str) and entry in states:
                    values[index]=copy.deepcopy(states[entry])
                    occurrences.append({
                        "state":entry,
                        "path":["tests",test_id,"states",index],
                        "consumer":"test",
                    })

        # Set Filters are the other production consumer observed by the census.
        # Keep this deliberately structural: only {state:<id>, action:...}
        # filter references are localized.
        def inline_filter_states(value: Any, path: list[Any]):
            if isinstance(value,dict):
                if (
                    isinstance(value.get("state"),str)
                    and value["state"] in states
                    and "action" in value
                ):
                    original=value["state"]
                    value["state"]=copy.deepcopy(states[original])
                    occurrences.append({
                        "state":original,
                        "path":path+["state"],
                        "consumer":"filter",
                    })
                for key,child in list(value.items()):
                    if key=="state" and isinstance(child,dict) and "action" in value:
                        continue
                    inline_filter_states(child,path+[key])
            elif isinstance(value,list):
                for index,child in enumerate(value):
                    inline_filter_states(child,path+[index])

        inline_filter_states(a,[])

        # Remove a State only when every surviving scalar reference to it was
        # localized. Unsupported reference contexts therefore fail closed by
        # leaving the State named.
        remaining=scalar_reference_counts(a,set(states))
        localized={row["state"] for row in occurrences}
        for name in sorted(localized):
            if remaining.get(name,0)==0:
                states.pop(name,None)

    if objects:
        a["objects"]=objects
        identity["shared_objects"]=sorted(objects)
        identity["retained_object_reasons"]={
            name:retention_reason(refs.get(name,0),direct_object_refs.get(name,0))
            for name in sorted(objects)
        }
        identity["retained_object_contexts"]={
            name:contexts.get(name,{})
            for name in sorted(objects)
        }
    else:
        a.pop("objects",None)

    if states:
        a["states"]=states
        identity["shared_states"]=sorted(states)
        identity["retained_state_reasons"]={
            name:retention_reason(refs.get(name,0),direct_state_refs.get(name,0))
            for name in sorted(states)
        }
        identity["retained_state_contexts"]={
            name:contexts.get(name,{})
            for name in sorted(states)
        }
    else:
        a.pop("states",None)

    return out,identity


def reexpand(research_doc: dict, identity: dict) -> dict:
    out=copy.deepcopy(research_doc)
    a=out["assessment"]
    tests=a.get("tests") or {}
    states=copy.deepcopy(a.get("states") or {})

    def path_parent(root: Any, path: list[Any]):
        current=root
        for segment in path[:-1]:
            current=current[segment]
        return current,path[-1]

    # Restore consumer-local copies before moving any inline Objects back to
    # Assessment scope, because recorded paths describe the rendered tree.
    for row in identity.get("inlined_state_consumer_occurrences",[]):
        parent,last=path_parent(a,row["path"])
        payload=copy.deepcopy(parent[last])
        original=row["state"]
        if original in states and states[original] != payload:
            raise ValueError(f"consumer-local State payload mismatch for {original!r}")
        states.setdefault(original,payload)
        parent[last]=original

    # Copy top-level Objects only after consumer-local State references have
    # been restored. Otherwise a stale pre-restoration copy can reintroduce
    # inline Filter-State payloads when the Object map is written back.
    objects=copy.deepcopy(a.get("objects") or {})

    for original,path in identity.get("inlined_objects",{}).items():
        parts=path.split(".")
        test_id=parts[2]
        payload=copy.deepcopy(tests[test_id]["object"])
        objects[original]=payload
        tests[test_id]["object"]=original

    # Restore bounded private Set-operand Objects after their parent Object
    # has been restored from a Test, if applicable.
    for row in identity.get("inlined_set_operand_objects",[]):
        child_id=row["object"]
        parent_id=row["parent_object"]
        index=row["operand_index"]
        parent=objects.get(parent_id)
        if not isinstance(parent,dict):
            raise ValueError(f"missing restored Set parent {parent_id!r}")
        operands=((parent.get("set") or {}).get("operands") or [])
        operand=operands[index]
        payload=copy.deepcopy(operand["object"])
        objects[child_id]=payload
        operand["object"]=child_id

    # Restore states in test-order without depending on dict insertion order.
    by_test={}
    for original,path in identity.get("inlined_states",{}).items():
        prefix="assessment.tests."
        rest=path[len(prefix):]
        test_id,tail=rest.rsplit(".states[",1)
        idx=int(tail[:-1])
        by_test.setdefault(test_id,[]).append((idx,original))

    for test_id,entries in by_test.items():
        vals=tests[test_id].get("states") or []
        for idx,original in sorted(entries):
            states[original]=copy.deepcopy(vals[idx])
            vals[idx]=original
        tests[test_id]["states"]=vals

    # Recreate original section order convention used by converter: objects,
    # variables, states, tests. Python equality ignores mapping order.
    present=identity.get("original_sections_present",{})
    if objects or present.get("objects"):
        a["objects"]=objects
    else:
        a.pop("objects",None)
    if states or present.get("states"):
        a["states"]=states
    else:
        a.pop("states",None)
    return out


def complexity(row: tuple[Path,dict]) -> tuple[int,str]:
    path,doc=row
    m=metrics(doc)
    score=m["tests"] + m["objects"] + m["states"] + 2*m["variables"]
    return score,path.name


def select_evenly(rows: list[tuple[Path,dict]], count: int) -> list[tuple[Path,dict]]:
    rows=sorted(rows,key=complexity)
    if len(rows)<=count:
        return rows
    indexes=[]
    for i in range(count):
        idx=round(i*(len(rows)-1)/(count-1)) if count>1 else 0
        if idx not in indexes:
            indexes.append(idx)
    # Rounding can theoretically collide; fill deterministically.
    if len(indexes)<count:
        for idx in range(len(rows)):
            if idx not in indexes:
                indexes.append(idx)
            if len(indexes)==count:
                break
    return [rows[i] for i in sorted(indexes[:count])]


def load_assessments(root: Path) -> list[tuple[Path,dict]]:
    rows=[]
    for path in sorted(root.rglob("*.yaml")):
        try:
            doc=yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(doc,dict) or "assessment" not in doc:
            continue
        a=doc["assessment"]
        assessment_id=str(a.get("id") or "")
        if a.get("mode")!="automated" or not isinstance(a.get("tests"),dict) or not a["tests"]:
            continue
        # This experiment compares STIG Rule Assessments, not platform/applicability
        # helper Assessments that happen to use the same automated vocabulary.
        if ".SV-" not in assessment_id and not assessment_id.startswith("SV-"):
            continue
        rows.append((path,doc))
    return rows


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("input_root",type=Path)
    ap.add_argument("--output",type=Path,required=True)
    ap.add_argument("--count",type=int,default=10)
    ap.add_argument("--all-assessments",action="store_true",
                    help="Measure every eligible STIG Rule Assessment instead of a diverse sample.")
    ap.add_argument("--metrics-only",action="store_true",
                    help="Write only report.json; do not emit transformed YAML/identity files.")
    ap.add_argument(
        "--inline-private-set-operands",
        action="store_true",
        help=(
            "Research v2: also inline single-use unfiltered leaf Objects that "
            "serve only as Set operands."
        ),
    )
    ap.add_argument(
        "--inline-private-filtered-set-operands",
        action="store_true",
        help=(
            "Research extension: allow a single-use leaf Object to localize "
            "inside its Set operand even when that operand has Filters. The "
            "Set and Filters remain unchanged."
        ),
    )
    ap.add_argument(
        "--inline-state-consumers",
        action="store_true",
        help=(
            "Research v3: also localize every referenced State into its Test "
            "or Set Filter consumer; retain unsupported/unreferenced States."
        ),
    )
    ap.add_argument("--label",required=True)
    args=ap.parse_args()

    rows=load_assessments(args.input_root)
    selected=rows if args.all_assessments else select_evenly(rows,args.count)
    if not args.all_assessments and len(selected)<args.count:
        raise SystemExit(f"{args.label}: requested {args.count} assessments, found {len(selected)}")

    args.output.mkdir(parents=True,exist_ok=True)
    report={
        "format":(
            "scap-ng-inline-private-components-research-0.3"
            if args.inline_state_consumers
            else (
                "scap-ng-inline-private-components-research-0.2"
                if args.inline_private_set_operands
                else "scap-ng-inline-private-components-research-0.1"
            )
        ),
        "status":"research_only_not_accepted_design",
        "label":args.label,
        "inline_private_set_operands":bool(args.inline_private_set_operands),
        "inline_private_filtered_set_operands":bool(args.inline_private_filtered_set_operands),
        "inline_state_consumers":bool(args.inline_state_consumers),
        "source_root":str(args.input_root),
        "selected":[],
        "summary":{},
    }
    totals={
        "objects_before":0,"objects_after":0,
        "states_before":0,"states_after":0,
        "cross_refs_before":0,"cross_refs_after":0,
        "named_refs_before":0,"named_refs_after":0,
        "lines_before":0,"lines_after":0,
        "bytes_before":0,"bytes_after":0,
        "inlined_objects":0,"inlined_set_operand_objects":0,"inlined_states":0,
        "inlined_state_consumer_occurrences":0,
        "retained_object_reason_counts":{},
        "retained_state_reason_counts":{},
        "retained_object_context_counts":{},
        "retained_state_context_counts":{},
        "retained_object_context_signature_counts":{},
    }

    for path,doc in selected:
        before=metrics(doc)
        rendered,identity=inline_private(
            doc,
            inline_private_set_operands=args.inline_private_set_operands,
            inline_private_filtered_set_operands=args.inline_private_filtered_set_operands,
            inline_state_consumers=args.inline_state_consumers,
        )
        expanded=reexpand(rendered,identity)
        if expanded != doc:
            detail=first_difference(doc,expanded) or "unknown structural difference"
            raise SystemExit(f"round-trip structural mismatch: {path}: {detail}")
        after=metrics(rendered)

        relname=path.stem.replace(".assessment","")+".inline-private.yaml"
        outpath=args.output/relname
        if not args.metrics_only:
            outpath.write_text(RESEARCH_HEADER+normalized_text(rendered),encoding="utf-8")
            (args.output/(relname+".identity.json")).write_text(
                json.dumps(identity,indent=2,sort_keys=True)+"\n",encoding="utf-8"
            )

        row={
            "source":str(path),
            "output":str(outpath) if not args.metrics_only else None,
            "assessment_id":doc["assessment"].get("id"),
            "before":before,
            "after":after,
            "inlined_objects":len(identity["inlined_objects"]),
            "inlined_set_operand_objects":len(identity["inlined_set_operand_objects"]),
            "inlined_states":len(identity["inlined_states"]),
            "inlined_state_consumer_occurrences":len(identity["inlined_state_consumer_occurrences"]),
            "shared_objects":len(identity["shared_objects"]),
            "shared_states":len(identity["shared_states"]),
            "retained_object_reason_counts":{},
            "retained_state_reason_counts":{},
            "retained_object_context_counts":{},
            "retained_state_context_counts":{},
            "retained_object_context_signature_counts":{},
            "roundtrip_structural_identity":"passed",
        }
        for reason in identity["retained_object_reasons"].values():
            row["retained_object_reason_counts"][reason]=row["retained_object_reason_counts"].get(reason,0)+1
        for reason in identity["retained_state_reasons"].values():
            row["retained_state_reason_counts"][reason]=row["retained_state_reason_counts"].get(reason,0)+1
        for contexts_for_object in identity["retained_object_contexts"].values():
            signature=context_signature(contexts_for_object)
            row["retained_object_context_signature_counts"][signature]=(
                row["retained_object_context_signature_counts"].get(signature,0)+1
            )
            for context,count in contexts_for_object.items():
                row["retained_object_context_counts"][context]=row["retained_object_context_counts"].get(context,0)+count
        for contexts_for_state in identity["retained_state_contexts"].values():
            for context,count in contexts_for_state.items():
                row["retained_state_context_counts"][context]=row["retained_state_context_counts"].get(context,0)+count
        report["selected"].append(row)
        for k in ("objects","states"):
            totals[k+"_before"]+=before[k]
            totals[k+"_after"]+=after[k]
        totals["cross_refs_before"]+=before["test_component_cross_references"]
        totals["cross_refs_after"]+=after["test_component_cross_references"]
        totals["named_refs_before"]+=before["named_component_cross_references"]
        totals["named_refs_after"]+=after["named_component_cross_references"]
        totals["lines_before"]+=before["normalized_lines"]
        totals["lines_after"]+=after["normalized_lines"]
        totals["bytes_before"]+=before["normalized_bytes"]
        totals["bytes_after"]+=after["normalized_bytes"]
        totals["inlined_objects"]+=row["inlined_objects"]
        totals["inlined_set_operand_objects"]+=row["inlined_set_operand_objects"]
        totals["inlined_states"]+=row["inlined_states"]
        totals["inlined_state_consumer_occurrences"]+=row["inlined_state_consumer_occurrences"]
        for reason,count in row["retained_object_reason_counts"].items():
            totals["retained_object_reason_counts"][reason]=totals["retained_object_reason_counts"].get(reason,0)+count
        for reason,count in row["retained_state_reason_counts"].items():
            totals["retained_state_reason_counts"][reason]=totals["retained_state_reason_counts"].get(reason,0)+count
        for context,count in row["retained_object_context_counts"].items():
            totals["retained_object_context_counts"][context]=totals["retained_object_context_counts"].get(context,0)+count
        for context,count in row["retained_state_context_counts"].items():
            totals["retained_state_context_counts"][context]=totals["retained_state_context_counts"].get(context,0)+count
        for signature,count in row["retained_object_context_signature_counts"].items():
            totals["retained_object_context_signature_counts"][signature]=(
                totals["retained_object_context_signature_counts"].get(signature,0)+count
            )

    def reduction(before,after):
        return round(100*(before-after)/before,1) if before else 0.0

    report["summary"]={
        **totals,
        "assessments":len(selected),
        "cross_reference_reduction_percent":reduction(totals["cross_refs_before"],totals["cross_refs_after"]),
        "named_component_reference_reduction_percent":reduction(
            totals["named_refs_before"],totals["named_refs_after"]
        ),
        "line_reduction_percent":reduction(totals["lines_before"],totals["lines_after"]),
        "byte_reduction_percent":reduction(totals["bytes_before"],totals["bytes_after"]),
        "object_scope_reduction_percent":reduction(totals["objects_before"],totals["objects_after"]),
        "state_scope_reduction_percent":reduction(totals["states_before"],totals["states_after"]),
    }
    (args.output/"report.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(report["summary"],indent=2,sort_keys=True))


if __name__=="__main__":
    main()
