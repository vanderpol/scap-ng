#!/usr/bin/env python3
"""Independent source OVAL XML -> authored 0.4.0 Test graph comparison.

This source-side oracle does NOT use the SCAP-NG converter that generated the
Assessment, nor does it reuse the native->OVAL exporter. It reads original
OVAL Definition, Test, Object and Filter State XML and independently derives
the supported semantics, then checks the real 0.4.0 authored Assessment fields.

Only two explicit, deliberately narrow kinds are implemented here:
independent.shellcommand direct-filter and windows.registry single-State
equality. Every other shape is UNSUPPORTED (not an equivalence success).
For a full exporter acceptance, this is an independent complement to the
native->XML semantic comparator, 5.12.3 XSD, and deliberate mutation checks.

Refs #248 #229.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import xml.etree.ElementTree as ET

OD="http://oval.mitre.org/XMLSchema/oval-definitions-5"
IND=OD+"#independent"
WIN=OD+"#windows"

def local(tag):
    return tag.rsplit("}",1)[-1]

def require(ok, reason):
    if not ok:
        raise ValueError("OVAL source to 0.4 Assessment mismatch/unsupported: "+reason)

def at(root,ident):
    matches=[node for node in root.iter() if node.get("id")==ident]
    require(len(matches)==1,"source ID missing or duplicated: "+str(ident))
    return matches[0]

def one_child(node, expected):
    found=list(node)
    require(len(found)==1 and local(found[0].tag)==expected,
            "expected sole original "+expected+" child in "+local(node.tag))
    return found[0]

def source_graph(source_xml, defid):
    root=ET.fromstring(source_xml)
    require(root.tag=="{"+OD+"}oval_definitions","source is not an OVAL Definitions document")
    definition=at(root,defid)
    require(definition.tag=="{"+OD+"}definition","OVAL source ID is not a Definition")
    crit=definition.find("{"+OD+"}criteria")
    require(crit is not None and not crit.attrib,"single unmodified criteria required")
    criterion=one_child(crit,"criterion")
    require(set(criterion.attrib) <= {"test_ref","comment"},"unsupported criterion attributes")
    source_test=at(root,criterion.get("test_ref"))
    require(source_test.tag in ("{"+IND+"}shellcommand_test","{"+WIN+"}registry_test"),
            "unsupported source Test family: "+source_test.tag)
    refs=list(source_test)
    capability="independent.shellcommand" if source_test.tag=="{"+IND+"}shellcommand_test" else "windows.registry"
    test_shape=["object"] if capability=="independent.shellcommand" else ["object","state"]
    require([local(n.tag) for n in refs]==test_shape,"unsupported original Test references")
    require(source_test.get("check_existence","at_least_one_exists")=="at_least_one_exists",
            "different original Test existence rule")
    test_check=source_test.get("check")
    require(test_check in ("all","only one"),"unexpected original Test check")
    require(source_test.get("comment") is not None,"original OVAL Test documentation missing")
    source_object=at(root,refs[0].get("object_ref"))
    require(not list(source_object.iter("{"+OD+"}set")),
            "genuine OVAL Set cannot be rewritten into a simple leaf")
    require(not any(local(n.tag)=="behaviors" for n in source_object),
            "source Object behaviors unsupported in simple Test pilot")
    objchildren=list(source_object)
    attrs={"id","version","comment"}
    require(set(source_object.attrib)<=attrs,"source Object attributes require independent handling")
    base={
        "source_definition":defid,"version":int(definition.get("version","1")),
        "class":definition.get("class"),
        "capability":capability,
        "test_title":source_test.get("comment"),
        "object_title":source_object.get("comment"),
        "source_check":test_check,
        "source_existence":"at_least_one_exists",
    }
    require(source_test.get("version")==definition.get("version")
            and source_object.get("version")==definition.get("version"),
            "source Test/Object version not aligned with Definition")
    if capability=="independent.shellcommand":
        require(source_object.tag=="{"+IND+"}shellcommand_object",
                "original OVAL Object family mismatch")
        require([local(n.tag) for n in objchildren]==["shell","command","filter"],
                "unexpected shellcommand Object field order/shape")
        shell,command,fil=objchildren
        require(fil.tag=="{"+OD+"}filter" and fil.get("action")=="include"
                and set(fil.attrib)=={"action"},
                "unsupported OVAL direct Filter action")
        orig_state=at(root,(fil.text or "").strip())
        require(orig_state.tag=="{"+IND+"}shellcommand_state"
                and orig_state.get("version")==definition.get("version"),
                "Filter State type/version mismatch")
        statefield=one_child(orig_state,"stdout_line")
        require(statefield.get("operation","equals")=="case insensitive equals"
                and set(statefield.attrib)<= {"operation","datatype"},
                "different source Filter predicate operation")
        require(statefield.get("datatype","string")=="string",
                "different source Filter predicate datatype")
        require(test_check=="all","shellcommand pilot checks must be all")
        base["object"]={
            "collect":{"shell":shell.text,"command":command.text,
                       "error_if_exit_status_not_0":False,
                       "error_if_stderr_exists":False},
            "filters":[{"include":{"stdout_line":{
                "require":"at_least_one_exists_and_all_match",
                "case_insensitive_equals":statefield.text}}}],
        }
        base["require"]={"items":"one_or_more"}
        base["states"]=[]
    else:
        require(source_object.tag=="{"+WIN+"}registry_object",
                "original registry Object family mismatch")
        require([local(n.tag) for n in objchildren]==["hive","key","name"],
                "different original ordered hive/key/name fields")
        require(all(not n.attrib for n in objchildren),
                "registry source Object selectors are not literals")
        hive=(objchildren[0].text or "").strip()
        require(hive=="HKEY_LOCAL_MACHINE","unapproved registry hive")
        state=at(root,refs[1].get("state_ref"))
        require(state.tag=="{"+WIN+"}registry_state"
                and state.get("version")==definition.get("version"),
                "source Registry State type/version mismatch")
        predicate=one_child(state,"value")
        require(set(predicate.attrib)<={"operation","datatype"}
                and predicate.get("operation","equals")=="equals"
                and predicate.get("datatype","string")=="string",
                "unsupported registry State predicate/dtype")
        require(test_check=="only one","registry pilot only supports 'only one' match")
        base["object"]={"select":{
            "hive":{"equals":"local_machine"},
            "key":{"equals":objchildren[1].text},
            "name":{"equals":objchildren[2].text}}}
        base["states"]=[{"value":{
            "require":"at_least_one_exists_and_all_match",
            "equals":predicate.text}}]
        base["require"]="at_least_one_exists_and_only_one_matches"
        require(not list(source_object.iter("{"+OD+"}filter")),
                "registry simple Object unexpectedly filtered")
    return base

def compare(source_xml, native_doc, defid):
    expected=source_graph(source_xml,defid)
    a=native_doc.get("assessment") if isinstance(native_doc,dict) else None
    require(isinstance(a,dict) and a.get("specification",{}).get("version")=="0.4.0",
            "not actual 0.4.0 Assessment source")
    require(a.get("mode")=="automated" and len(a.get("tests",{}))==1,
            "only one autogenerated Test with a single OVAL criterion supported")
    tid, t=next(iter(a["tests"].items()))
    require(a.get("evaluate")=={"test":tid},"native criterion differs from source")
    require(a.get("version")==expected["version"] and a.get("class")==expected["class"],
            "native OVAL Definition identity or class/version changed")
    for field in ("capability","test_title","reported_elements","require"):
        actual=t.get(field)
        orig=expected[field] if field!="reported_elements" else "all"
        require(actual==orig,f"native {field} is different from original OVAL")
    require(t.get("object",{}).get("object_title")==expected["object_title"],
            "native Object documentation/source identity changed")
    obj=t["object"]
    require(set(obj)==set(expected["object"])|{"object_title"},
            "Object contains missing/extra selectors, Set or Filter fields")
    for key,value in expected["object"].items():
        require(obj.get(key)==value,"native Object "+key+" differs from original OVAL")
    if expected["states"]:
        require(t.get("states")==expected["states"],
                "native registry State or equality value changed")
    else:
        require("states" not in t and "state" not in t,
                "source has no Test State but NG introduced one")
    allowed={"test_title","capability","object","reported_elements","require"}
    if expected["states"]:
        allowed.add("states")
    require(set(t)==allowed,"unaccounted authored Test attributes")
    return {"status":"SOURCE_TO_NATIVE_040_EXACT_FOR_SUPPORTED_TEST",
            "source_definition":defid,
            "native_assessment":a["id"],
            "capability":expected["capability"],
            "tested_source_graph_fields":sorted(expected),
            "original_set_count":0,
            "source_filter_count":len(expected["object"].get("filters",[])),
            "native_test_count":1,
            "current_native_schema_validated":False,
            "scanner_execution":False}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source-xml",type=Path,required=True)
    p.add_argument("--native",type=Path,required=True)
    p.add_argument("--definition-id",required=True)
    p.add_argument("--report",type=Path,required=True)
    args=p.parse_args()
    out=compare(args.source_xml.read_bytes(),
                json.loads(args.native.read_text()),args.definition_id)
    out.update({"source_sha256":sha256(args.source_xml.read_bytes()).hexdigest(),
                "native_sha256":sha256(args.native.read_bytes()).hexdigest()})
    args.report.parent.mkdir(exist_ok=True,parents=True)
    args.report.write_text(json.dumps(out,sort_keys=True,indent=2)+"\n")
    print(json.dumps(out,indent=2))

if __name__=="__main__":
    main()
