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


def inspect_file(path):
    data=path.read_bytes()
    root=etree.fromstring(data)
    ir=oval_ir.parse(path)
    obj_values=static_variable_object_values(root,ir)
    state_values=expected_state_values(root,ir)

    tests_section=root.find("{http://oval.mitre.org/XMLSchema/oval-definitions-5}tests")
    results=[]
    if tests_section is None:
        return results
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

        # Self-Assertion test content is authored so definitions/tests evaluate
        # true unless otherwise specified. For this focused static subset, a
        # false entity result is therefore a semantic mismatch to investigate.
        results.append({
            "test_id":test_id,
            "status":"pass" if outcome else "semantic_mismatch",
            "object_ref":object_ref,
            "state_ref":state_ref,
            "actual_values":actual,
            "expected_values":state_values[state_ref]["values"],
        })
    return results


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("root",type=Path)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()

    files=[]
    all_results=[]
    for path in sorted(args.root.rglob("*.xml")):
        rel=path.relative_to(args.root).as_posix()
        try:
            results=inspect_file(path)
        except Exception as exc:
            files.append({"path":rel,"status":"error","error":f"{type(exc).__name__}: {exc}"})
            continue
        counts=Counter(x["status"] for x in results)
        files.append({"path":rel,"status":"ok","test_counts":dict(sorted(counts.items()))})
        for result in results:
            all_results.append({"path":rel,**result})

    counts=Counter(x["status"] for x in all_results)
    report={
        "format":"scap-ng-oval-self-assertion-static-verification-0.1",
        "role":"offline_language_conformance",
        "counts":dict(sorted(counts.items())),
        "semantic_mismatches":[x for x in all_results if x["status"]=="semantic_mismatch"],
        "skipped_reasons":dict(sorted(Counter(
            x.get("reason","unknown") for x in all_results if x["status"]=="skipped"
        ).items())),
        "files":files,
        "results":all_results,
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        "counts":report["counts"],
        "skipped_reasons":report["skipped_reasons"],
        "semantic_mismatch_count":len(report["semantic_mismatches"]),
    },indent=2,sort_keys=True))
    return 1 if report["semantic_mismatches"] else 0


if __name__=="__main__":
    raise SystemExit(main())
