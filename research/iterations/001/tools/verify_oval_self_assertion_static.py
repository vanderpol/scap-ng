#!/usr/bin/env python3
"""Verify statically reducible OVAL Self-Assertion variable_test cases offline.

This deliberately evaluates only cases whose object and state values can be
resolved without platform collection. Unsupported semantics are reported as
skipped, never treated as passing.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from collections import Counter
from pathlib import Path
from lxml import etree

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("oval_ir", HERE/"oval_semantic_ir.py")
oval_ir=importlib.util.module_from_spec(spec)
spec.loader.exec_module(oval_ir)


def local(tag):
    return etree.QName(tag).localname if isinstance(tag,str) else None


def static_variable_object_values(root, ir):
    resolutions=ir.get("variable_resolution",{})
    out={}
    objects=root.find("{http://oval.mitre.org/XMLSchema/oval-definitions-5}objects")
    if objects is None:
        return out
    for obj in objects:
        if local(obj.tag)!="variable_object":
            continue
        refs=[(c.text or "").strip() for c in obj if local(c.tag)=="var_ref"]
        if len(refs)!=1:
            continue
        resolved=resolutions.get(refs[0],{})
        if resolved.get("status")=="exact_static":
            out[obj.get("id")]={
                "variable_ref":refs[0],
                "values":[str(x) for x in resolved.get("values",[])],
            }
    return out


def expected_state_values(root, ir):
    resolutions=ir.get("variable_resolution",{})
    out={}
    states=root.find("{http://oval.mitre.org/XMLSchema/oval-definitions-5}states")
    if states is None:
        return out
    for state in states:
        if local(state.tag)!="variable_state":
            continue
        entities=[c for c in state if isinstance(c.tag,str)]
        if len(entities)!=1 or local(entities[0].tag)!="value":
            continue
        entity=entities[0]
        operation=entity.get("operation","equals")
        if operation!="equals":
            continue
        var_ref=entity.get("var_ref")
        if var_ref:
            resolved=resolutions.get(var_ref,{})
            if resolved.get("status")!="exact_static":
                continue
            values=[str(x) for x in resolved.get("values",[])]
            source="variable"
        else:
            values=[(entity.text or "").strip()]
            source="literal"
        out[state.get("id")]={
            "values":values,
            "source":source,
            "var_check":entity.get("var_check","all"),
            "entity_check":entity.get("entity_check","all"),
            "datatype":entity.get("datatype","string"),
        }
    return out


def evaluate_values(actual, state):
    expected=state["values"]
    var_check=state["var_check"]
    entity_check=state["entity_check"]

    def against_expected(value):
        matches=[value==candidate for candidate in expected]
        if var_check=="all":
            return all(matches)
        if var_check=="at least one":
            return any(matches)
        if var_check=="only one":
            return sum(matches)==1
        if var_check=="none satisfy":
            return not any(matches)
        return None

    results=[]
    for value in actual:
        r=against_expected(value)
        if r is None:
            return None,"unsupported_var_check"
        results.append(r)

    if entity_check=="all":
        return all(results),None
    if entity_check=="at least one":
        return any(results),None
    if entity_check=="only one":
        return sum(results)==1,None
    if entity_check=="none satisfy":
        return not any(results),None
    return None,"unsupported_entity_check"



def evaluate_criteria_node(node, test_outcomes, definition_lookup, definition_cache, stack):
    name=local(node.tag)
    negate=node.get("negate","false").lower()=="true"

    if name=="criterion":
        test_ref=node.get("test_ref")
        value=test_outcomes.get(test_ref)
        if value is None:
            return None
        return (not value) if negate else value

    if name=="extend_definition":
        definition_ref=node.get("definition_ref")
        value=evaluate_definition(
            definition_ref, definition_lookup, test_outcomes,
            definition_cache, stack
        )
        if value is None:
            return None
        return (not value) if negate else value

    if name!="criteria":
        return None

    children=[
        evaluate_criteria_node(
            child,test_outcomes,definition_lookup,definition_cache,stack
        )
        for child in node
        if local(child.tag) in {"criteria","criterion","extend_definition"}
    ]
    if any(value is None for value in children):
        return None

    operator=node.get("operator","AND")
    true_count=sum(bool(x) for x in children)
    if operator=="AND":
        value=all(children)
    elif operator=="OR":
        value=any(children)
    elif operator=="XOR":
        value=(true_count % 2)==1
    elif operator=="ONE":
        value=true_count==1
    else:
        return None
    return (not value) if negate else value


def evaluate_definition(definition_id, definition_lookup, test_outcomes, cache, stack):
    if definition_id in cache:
        return cache[definition_id]
    if definition_id in stack:
        return None
    definition=definition_lookup.get(definition_id)
    if definition is None:
        return None
    criteria=next((c for c in definition if local(c.tag)=="criteria"),None)
    if criteria is None:
        return None
    stack.add(definition_id)
    value=evaluate_criteria_node(criteria,test_outcomes,definition_lookup,cache,stack)
    stack.remove(definition_id)
    cache[definition_id]=value
    return value


def inspect_file(path):
    data=path.read_bytes()
    root=etree.fromstring(data)
    ir=oval_ir.parse(path)
    obj_values=static_variable_object_values(root,ir)
    state_values=expected_state_values(root,ir)

    tests_section=root.find("{http://oval.mitre.org/XMLSchema/oval-definitions-5}tests")
    results=[]
    if tests_section is not None:
        for test in tests_section:
            if local(test.tag)!="variable_test":
                continue
            test_id=test.get("id")
            object_nodes=[c for c in test if local(c.tag)=="object"]
            state_nodes=[c for c in test if local(c.tag)=="state"]
            if len(object_nodes)!=1 or len(state_nodes)!=1:
                results.append({"test_id":test_id,"status":"skipped","reason":"object_or_state_count"})
                continue
            object_ref=object_nodes[0].get("object_ref")
            state_ref=state_nodes[0].get("state_ref")
            if object_ref not in obj_values:
                results.append({"test_id":test_id,"status":"skipped","reason":"object_not_static_direct_variable_object"})
                continue
            if state_ref not in state_values:
                results.append({"test_id":test_id,"status":"skipped","reason":"state_not_simple_static_equals"})
                continue

            actual=obj_values[object_ref]["values"]
            outcome,reason=evaluate_values(actual,state_values[state_ref])
            if outcome is None:
                results.append({"test_id":test_id,"status":"skipped","reason":reason})
                continue

            results.append({
                "test_id":test_id,
                "status":"evaluated_true" if outcome else "evaluated_false",
                "object_ref":object_ref,
                "state_ref":state_ref,
                "actual_values":actual,
                "expected_values":state_values[state_ref]["values"],
            })

    definitions_section=root.find("{http://oval.mitre.org/XMLSchema/oval-definitions-5}definitions")
    definition_results=[]
    if definitions_section is not None:
        lookup={d.get("id"):d for d in definitions_section if local(d.tag)=="definition"}
        test_outcomes={
            result["test_id"]: (
                True if result["status"]=="evaluated_true"
                else False if result["status"]=="evaluated_false"
                else None
            )
            for result in results
        }
        cache={}
        for definition_id in lookup:
            value=evaluate_definition(definition_id,lookup,test_outcomes,cache,set())
            definition_results.append({
                "definition_id":definition_id,
                "status":(
                    "evaluated_true" if value is True
                    else "evaluated_false" if value is False
                    else "skipped"
                ),
            })

    return results,definition_results

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("root",type=Path)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()

    files=[]
    all_results=[]
    definition_results_all=[]
    for path in sorted(args.root.rglob("*.xml")):
        rel=path.relative_to(args.root).as_posix()
        try:
            results,definition_results=inspect_file(path)
        except Exception as exc:
            files.append({"path":rel,"status":"error","error":f"{type(exc).__name__}: {exc}"})
            continue
        counts=Counter(x["status"] for x in results)
        def_counts=Counter(x["status"] for x in definition_results)
        files.append({
            "path":rel,
            "status":"ok",
            "test_counts":dict(sorted(counts.items())),
            "definition_counts":dict(sorted(def_counts.items())),
        })
        for result in results:
            all_results.append({"path":rel,**result})
        for result in definition_results:
            result["path"]=rel
            definition_results_all.append(result)

    counts=Counter(x["status"] for x in all_results)
    definition_counts=Counter(x["status"] for x in definition_results_all)
    report={
        "format":"scap-ng-oval-self-assertion-static-verification-0.1",
        "role":"offline_language_conformance",
        "test_counts":dict(sorted(counts.items())),
        "definition_counts":dict(sorted(definition_counts.items())),
        "definition_mismatches":[
            x for x in definition_results_all if x["status"]=="evaluated_false"
        ],
        "skipped_reasons":dict(sorted(Counter(
            x.get("reason","unknown") for x in all_results if x["status"]=="skipped"
        ).items())),
        "files":files,
        "test_results":all_results,
        "definition_results":definition_results_all,
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        "test_counts":report["test_counts"],
        "definition_counts":report["definition_counts"],
        "skipped_reasons":report["skipped_reasons"],
        "definition_mismatch_count":len(report["definition_mismatches"]),
    },indent=2,sort_keys=True))
    return 1 if report["definition_mismatches"] else 0


if __name__=="__main__":
    raise SystemExit(main())
