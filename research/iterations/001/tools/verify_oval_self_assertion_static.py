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
import decimal
import ipaddress
import re
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
            "operation":operation,
        }
    return out


def rpmvercmp(left, right):
    """Compare RPM version/release strings using rpmvercmp-style segments."""
    a=str(left)
    b=str(right)
    ia=ib=0

    while True:
        while ia<len(a) and not a[ia].isalnum() and a[ia] not in "~^":
            ia+=1
        while ib<len(b) and not b[ib].isalnum() and b[ib] not in "~^":
            ib+=1

        # Tilde sorts before everything, including end-of-string.
        if (ia<len(a) and a[ia]=="~") or (ib<len(b) and b[ib]=="~"):
            if not (ia<len(a) and a[ia]=="~"):
                return 1
            if not (ib<len(b) and b[ib]=="~"):
                return -1
            ia+=1; ib+=1
            continue

        # Caret sorts after end-of-string but before any other following segment.
        if (ia<len(a) and a[ia]=="^") or (ib<len(b) and b[ib]=="^"):
            if ia>=len(a):
                return -1
            if ib>=len(b):
                return 1
            if a[ia]!="^":
                return 1
            if b[ib]!="^":
                return -1
            ia+=1; ib+=1
            continue

        enda=ia>=len(a)
        endb=ib>=len(b)
        if enda or endb:
            if enda and endb:
                return 0
            return -1 if enda else 1

        a_numeric=a[ia].isdigit()
        b_numeric=b[ib].isdigit()

        ja=ia
        while ja<len(a) and a[ja].isalnum() and a[ja].isdigit()==a_numeric:
            ja+=1
        jb=ib
        while jb<len(b) and b[jb].isalnum() and b[jb].isdigit()==b_numeric:
            jb+=1

        sa=a[ia:ja]
        sb=b[ib:jb]
        ia,ib=ja,jb

        if a_numeric and not b_numeric:
            return 1
        if b_numeric and not a_numeric:
            return -1

        if a_numeric:
            na=sa.lstrip("0") or "0"
            nb=sb.lstrip("0") or "0"
            if len(na)!=len(nb):
                return 1 if len(na)>len(nb) else -1
            if na!=nb:
                return 1 if na>nb else -1
        else:
            if sa!=sb:
                return 1 if sa>sb else -1


def split_evr(value):
    text=str(value)
    epoch_text,sep,rest=text.partition(":")
    if not sep:
        epoch_text="0"
        rest=text
    epoch=int(epoch_text or "0",10)
    version,sep,release=rest.rpartition("-")
    if not sep:
        version=rest
        release=""
    return epoch,version,release


def compare_evr(left,right):
    le,lv,lr=split_evr(left)
    re_,rv,rr=split_evr(right)
    if le!=re_:
        return 1 if le>re_ else -1
    version_cmp=rpmvercmp(lv,rv)
    if version_cmp:
        return version_cmp
    return rpmvercmp(lr,rr)


def cast_value(value, datatype):
    text=str(value)
    if datatype=="string":
        return text
    if datatype=="int":
        return int(text,10)
    if datatype=="float":
        return decimal.Decimal(text)
    if datatype=="boolean":
        lowered=text.strip().lower()
        if lowered in {"true","1"}:
            return True
        if lowered in {"false","0"}:
            return False
        raise ValueError(f"invalid boolean {text!r}")
    if datatype=="binary":
        cleaned=text.strip().lower()
        if len(cleaned)%2 or any(ch not in "0123456789abcdef" for ch in cleaned):
            raise ValueError(f"invalid binary {text!r}")
        return bytes.fromhex(cleaned)
    if datatype=="version":
        parts=[int(x) for x in re.findall(r"[0-9]+",text)]
        if not parts:
            raise ValueError(f"invalid version {text!r}")
        return tuple(parts)
    if datatype=="ipv4_address":
        address,prefix=(text.split("/",1)+[None])[:2] if "/" in text else (text,None)
        octets=address.split(".")
        if len(octets)!=4:
            raise ValueError(f"invalid IPv4 address {text!r}")
        normalized=".".join(str(int(x,10)) for x in octets)
        if prefix is None:
            prefix="32"
        elif "." in prefix:
            mask_octets=prefix.split(".")
            if len(mask_octets)!=4:
                raise ValueError(f"invalid IPv4 netmask {text!r}")
            mask_norm=".".join(str(int(x,10)) for x in mask_octets)
            prefix=str(ipaddress.IPv4Network(f"0.0.0.0/{mask_norm}").prefixlen)
        return ipaddress.IPv4Network(f"{normalized}/{prefix}",strict=False)
    if datatype=="ipv6_address":
        value=text if "/" in text else text+"/128"
        return ipaddress.IPv6Network(value,strict=False)
    raise NotImplementedError(datatype)


def compare_value(actual, expected, datatype, operation):
    if datatype=="evr_string":
        try:
            cmp=compare_evr(actual,expected)
        except ValueError:
            return None,"datatype_cast_error:evr_string"
        if operation=="equals":
            return cmp==0,None
        if operation=="not equal":
            return cmp!=0,None
        if operation=="greater than":
            return cmp>0,None
        if operation=="greater than or equal":
            return cmp>=0,None
        if operation=="less than":
            return cmp<0,None
        if operation=="less than or equal":
            return cmp<=0,None
        return None,f"unsupported_operation:{operation}"

    try:
        if operation=="pattern match":
            if datatype!="string":
                return None,"pattern_match_non_string"
            return re.search(str(expected),str(actual)) is not None,None

        left=cast_value(actual,datatype)
        right=cast_value(expected,datatype)
    except NotImplementedError:
        return None,f"unsupported_datatype:{datatype}"
    except (ValueError,decimal.InvalidOperation):
        return None,f"datatype_cast_error:{datatype}"

    if datatype=="version":
        size=max(len(left),len(right))
        left=left+(0,)*(size-len(left))
        right=right+(0,)*(size-len(right))

    if datatype in {"ipv4_address","ipv6_address"}:
        if operation=="subset of":
            return left.subnet_of(right),None
        if operation=="superset of":
            return left.supernet_of(right),None
        if operation in {"greater than","greater than or equal","less than","less than or equal"}:
            if left.prefixlen!=right.prefixlen:
                return None,"ip_prefix_mismatch_requires_error_semantics"
            left_key=int(left.network_address)
            right_key=int(right.network_address)
            if operation=="greater than":
                return left_key>right_key,None
            if operation=="greater than or equal":
                return left_key>=right_key,None
            if operation=="less than":
                return left_key<right_key,None
            return left_key<=right_key,None

    if operation=="equals":
        return left==right,None
    if operation=="not equal":
        return left!=right,None
    if operation=="case insensitive equals":
        if datatype!="string":
            return None,"case_insensitive_non_string"
        return str(left).casefold()==str(right).casefold(),None
    if operation=="case insensitive not equal":
        if datatype!="string":
            return None,"case_insensitive_non_string"
        return str(left).casefold()!=str(right).casefold(),None
    if operation=="greater than":
        return left>right,None
    if operation=="greater than or equal":
        return left>=right,None
    if operation=="less than":
        return left<right,None
    if operation=="less than or equal":
        return left<=right,None
    if operation=="bitwise and":
        if datatype!="int":
            return None,"bitwise_non_int"
        return (left & right)==right,None
    if operation=="bitwise or":
        if datatype!="int":
            return None,"bitwise_non_int"
        return (left | right)==right,None
    return None,f"unsupported_operation:{operation}"


def evaluate_values(actual, state):
    expected=state["values"]
    var_check=state["var_check"]
    entity_check=state["entity_check"]
    datatype=state["datatype"]
    operation=state["operation"]

    def against_expected(value):
        matches=[]
        for candidate in expected:
            comparison,reason=compare_value(value,candidate,datatype,operation)
            if comparison is None:
                return None,reason
            matches.append(comparison)
        if var_check=="all":
            return all(matches),None
        if var_check=="at least one":
            return any(matches),None
        if var_check=="only one":
            return sum(matches)==1,None
        if var_check=="none satisfy":
            return not any(matches),None
        return None,"unsupported_var_check"

    results=[]
    for value in actual:
        r,reason=against_expected(value)
        if r is None:
            return None,reason
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

            existence=test.get("check_existence","at_least_one_exists")
            if existence in {"all_exist","any_exist","at_least_one_exists","only_one_exists"}:
                existence_result=True
            elif existence=="none_exist":
                existence_result=False
            else:
                results.append({"test_id":test_id,"status":"skipped","reason":"unsupported_check_existence"})
                continue

            check=test.get("check","all")
            if check in {"all","at least one","only one"}:
                state_result=outcome
            elif check=="none satisfy":
                state_result=not outcome
            else:
                results.append({"test_id":test_id,"status":"skipped","reason":"unsupported_test_check"})
                continue

            test_outcome=existence_result and state_result
            results.append({
                "test_id":test_id,
                "status":"evaluated_true" if test_outcome else "evaluated_false",
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
        for definition_id,definition in lookup.items():
            value=evaluate_definition(definition_id,lookup,test_outcomes,cache,set())
            metadata=next((c for c in definition if local(c.tag)=="metadata"),None)
            title=""
            if metadata is not None:
                title_node=next((c for c in metadata if local(c.tag)=="title"),None)
                if title_node is not None:
                    title=(title_node.text or "").strip()
            expected=False if title.lower().startswith("evaluate to false") else True
            if value is None:
                status="skipped"
            elif value==expected:
                status="matches_expected"
            else:
                status="semantic_mismatch"
            definition_results.append({
                "definition_id":definition_id,
                "status":status,
                "actual":value,
                "expected":expected,
                "title":title,
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
            x for x in definition_results_all if x["status"]=="semantic_mismatch"
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
