#!/usr/bin/env python3
"""Refs #245: pinned ORIGINAL OVAL basic Linux/Windows C authoring gate.

Two COMPLETE original Definitions must compile in the established C frontend:
Linux sestatus (3 source Tests) and Windows passwordpolicy (7 source Tests).
Separately, one original Windows registry Test from a 15-Test Definition is
isolated from the A-compatible source review and compiled without fabricating
a value comparison. This is NOT a full Registry Definition conversion,
a scanner, or runtime six-state evidence.
"""
from __future__ import annotations
import argparse
from copy import deepcopy
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import yaml

from research_c_original_oval_to_authored_c import compile_one_original_definition

PIN="e3538595c5083b9c34d937a81d319234df9bbfaa"
WIN_REG="windows/win-def_registry_test.xml"
REG_DEF="oval:org.mitre.oval.test:def:38"
REG_TEST="oval:org.mitre.oval.test:tst:1020"
COMPLETE={
    "linux/linux-def_sestatus_test.xml":("linux",3),
    "windows/win-def_passwordpolicy_test.xml":("windows",7),
}
HIVE_CROSSWALK={"HKEY_LOCAL_MACHINE":"local_machine"}

def require(condition, message):
    if not condition:
        raise ValueError(message)

def one(elements, reason):
    elements=list(elements)
    require(len(elements)==1,reason+": expected one, got "+str(len(elements)))
    return elements[0]

def field_rows(elem):
    return [(x.tag.rsplit("}",1)[-1], x.get("operation","equals"),
             (x.text or "").strip()) for x in elem]

def original_xml(corpus, rel):
    path=corpus/rel
    require(path.is_file(),"pinned original OVAL XML missing: "+rel)
    return ET.parse(path).getroot()

def original_tests(root):
    tests=root.find("{*}tests")
    require(tests is not None,"no source OVAL Tests")
    return {node.get("id"):node for node in tests if node.get("id")}

def verify_complete_platform_definitions(corpus,review,native):
    manifest=json.loads((native/"conversion-manifest.json").read_text(encoding="utf-8"))
    require(manifest.get("stage")=="SOURCE_BACKED_NATIVE_C_SUBSET_NOT_SCANNER_PARITY",
            "C manifest lacks pinned source compilation classification")
    rows=manifest.get("native_C_converted")
    require(isinstance(rows,list),"missing native C conversion list")
    report={}
    for rel,(platform,count) in COMPLETE.items():
        selected=one((r for r in rows if r.get("file")==rel),
                     "complete original "+platform+" OVAL Definition")
        require(selected.get("native_C_compilation_passed") is True and
                selected.get("A_projection_equivalence_checked") is True,
                "full "+platform+" Definition lacks C-vs-A structural gate")
        require(selected.get("C_source_test_count")==count,
                "source Test count changed in native C manifest")
        root=original_xml(corpus,rel)
        tests=original_tests(root)
        require(len(tests)==count,
                "original "+platform+" OVAL Test inventory changed")
        file=selected["c_source"]
        require(type(file) is str and Path(file).name==file,
                "unsafe generated C artifact path")
        authored=yaml.safe_load((native/file).read_text(encoding="utf-8"))
        checks=authored.get("checks")
        require(isinstance(checks,dict) and len(checks)==count,
                "C Test count differs from original OVAL")
        test_ids=[c.get("source_test") for c in checks.values()]
        matched=[]
        for file in review.glob("*.review.json"):
            source=json.loads(file.read_text(encoding="utf-8"))
            origin=source.get("source",{})
            if origin.get("file")==rel and origin.get("definition_id")==selected["definition_id"]:
                matched.append(source)
        original_A=one(matched,"original "+platform+" A-compatible Definition")
        imported_ids=set(original_A["A_source_compatibility_fallback"]["tests"])
        source_documentation=original_A["source"]["original_test_documentation"]
        doc_ids={entry["id"] for entry in source_documentation}
        require(doc_ids==set(tests) and len(source_documentation)==count,
                "original XML Test IDs missing from A source-provenance review")
        require(len(set(test_ids))==count and set(test_ids)==imported_ids,
                "generated C dropped or added original A source Test identities")
        for alias,c in checks.items():
            require("must" in c and ("observation" in c or "from" in c),
                    "C check lacks explicit acquisition/requirement: "+alias)
        report[platform]={
            "source":rel,"full_definition_source_id":selected["definition_id"],
            "original_tests":count,"A_test_identity_crosswalk_equal":True,
            "original_OVAL_test_ids_verified_in_provenance":True,
            "full_definition_compiles":True,
            "A_source_projection_equivalence_checked":True,
        }
    return report

def registry_from_original_A(corpus,review,published):
    root=original_xml(corpus,WIN_REG)
    definitions=root.find("{*}definitions")
    defined=one((d for d in definitions if d.get("id")==REG_DEF),
                "pinned Registry Definition")
    source_tests=original_tests(root)
    require(len(source_tests)==15,"original Registry Definition no longer has 15 Tests")
    test=source_tests[REG_TEST]
    require(test.get("check")=="only one" and
            test.get("check_existence")=="at_least_one_exists",
            "Registry original OVAL Test quantifiers changed")
    objref=one(test.findall("{*}object"),"Registry Test source Object").get("object_ref")
    stref=one(test.findall("{*}state"),"Registry Test source State").get("state_ref")
    source_obj=one((x for x in root.find("{*}objects") if x.get("id")==objref),
                   "Registry Object identity")
    source_state=one((x for x in root.find("{*}states") if x.get("id")==stref),
                     "Registry State identity")
    original_select=field_rows(source_obj)
    original_state=field_rows(source_state)
    names=["hive","key","name"]
    require([x[0] for x in original_select]==names and
            [x[0] for x in original_state]==names,
            "Registry hive/key/name original selector/State order changed")
    require(all(op=="equals" for _,op,_ in original_select),
            "unexpected original Registry selector operation")
    require([op for _,op,_ in original_state]==[
        "equals","case insensitive equals","equals"],
        "source Registry case-insensitive key State missing")
    require(original_select[0][2] in HIVE_CROSSWALK,
            "source OVAL Registry hive not in reviewed A native crosswalk")
    require("value" not in [row[0] for row in original_state],
            "source Registry Test unexpectedly checks a Registry value")
    review_files=[]
    for file in review.glob("*.review.json"):
        row=json.loads(file.read_text(encoding="utf-8"))
        src=row.get("source",{})
        if src.get("file")==WIN_REG and src.get("definition_id")==REG_DEF:
            review_files.append(row)
    record=one(review_files,"source-approved A Registry fallback")
    require(any(x.get("id")==REG_TEST for x in
                record["source"]["original_test_documentation"]),
            "original Registry Test ID not documented in source review")
    a=record["A_source_compatibility_fallback"]
    # Name supplied by source-backed A v003 import; NOT inferred from OVAL
    # opaque tst number. No other Test from the 15-Test Definition is emitted.
    source_tid="test-test-if-registry-object-hive-key-name-supported"
    source_test=a["tests"].get(source_tid)
    require(isinstance(source_test,dict),"single original Registry Test absent from A")
    require(source_test["check"]==test.get("check") and
            source_test["check_existence"]==test.get("check_existence"),
            "imported A Registry quantifiers differ from pinned OVAL")
    oid=source_test["object"]
    state_ids=source_test["states"]
    require(len(state_ids)==1,"original Registry Test has unexpected States")
    sid=state_ids[0]
    aobj=deepcopy(a["objects"][oid])
    ast=deepcopy(a["states"][sid])
    require(list(aobj["select"])==names and
            [x["field"] for x in ast["state"]["all"]]==names,
            "source A Registry field order differs from original OVAL")
    for (field,op,value) in original_select:
        require(aobj["select"][field]["operation"]==op and
                aobj["select"][field]["value"]==value,
                "source A Registry selector does not match original XML: "+field)
    for (field,op,value),entry in zip(original_state,ast["state"]["all"]):
        require(entry["operation"]==op and entry["value"]==value,
                "source A Registry State differs from source XML: "+field)
    # The existing A capability enum uses local_machine, not the OVAL string.
    # Narrow, source-verified normalization; no second C Registry model.
    hive_native=HIVE_CROSSWALK[original_select[0][2]]
    aobj["select"]["hive"]["value"]=hive_native
    ast["state"]["all"][0]["value"]=hive_native
    isolated={"id":a["id"]+".original-registry-single-test",
              "mode":"automated","evaluate":{"test":source_tid},
              "objects":{oid:aobj},"states":{sid:ast},
              "tests":{source_tid:deepcopy(source_test)}}
    result=compile_one_original_definition(isolated)
    authored=yaml.safe_load(published.read_text(encoding="utf-8"))
    require(result["authored_c"]==authored,
            "published C Registry Test no longer matches exact source-backed A")
    emitted=result["native_c_compiled_test"]
    require(emitted["require"]=="at_least_one_exists_and_only_one_matches" and
            emitted["states_match"]=="all","Registry cardinality drift")
    require(list(emitted["object"]["select"])==names and
            [next(iter(x)) for x in emitted["states"]]==names,
            "Registry native C reordered/lost original fields")
    require(emitted["states"][1]["key"]["case_insensitive_equals"]==
            original_state[1][2],"Registry key matching algorithm changed")
    require("value" not in authored["must"]["one_matching_item"],
            "invented Registry value comparison")
    return {
        "source":WIN_REG,"definition_id":REG_DEF,"original_definition_tests":15,
        "selected_original_test":REG_TEST,"selected_test_compiles":True,
        "whole_registry_definition_compiles":False,
        "A_native_hive_crosswalk":"HKEY_LOCAL_MACHINE -> local_machine",
        "State_key_case_insensitive":True,"registry_value_not_checked":True,
        "A_source_projection_equivalence_checked":True,
    }

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus",type=Path,required=True)
    parser.add_argument("--review",type=Path,required=True)
    parser.add_argument("--native",type=Path,required=True)
    parser.add_argument("--published",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    full=verify_complete_platform_definitions(args.corpus,args.review,args.native)
    registry=registry_from_original_A(args.corpus,args.review,args.published)
    report={"stage":"PINNED_OVAL_C_BASIC_PLATFORM_GATE_NOT_SCANNER_PARITY",
            "pinned_source_commit":PIN,
            "full_definition_cases":full,
            "partial_definition_single_test":registry,
            "source_import_and_C_compiler_proven":True,
            "live_linux_or_windows_collector_executed":False,
            "OVAL_scanner_six_state_parity_proven":False}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",
                        encoding="utf-8")
    print(json.dumps(report,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
