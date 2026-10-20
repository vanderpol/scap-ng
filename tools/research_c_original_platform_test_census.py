#!/usr/bin/env python3
"""Refs #245: source-pinned basic OVAL Test-level compilation census.

Intentionally separates per-Test C compiler success from whole OVAL Definition
success. Each Test is isolated from the original A-compatible import, with
its source Object, referenced State(s) and check semantics unmodified.
Cannot claim a Definition compiles when only one of its Tests does.
In particular cannot upgrade a source Variable, Set or Filter silently.
"""
from __future__ import annotations

import argparse
from collections import Counter,defaultdict
from copy import deepcopy
import json
from pathlib import Path

from research_c_original_oval_to_authored_c import (
    NotNativeCConvertible, compile_one_original_definition,
)

FAMILIES=("linux","unix","windows")

def check(ok,reason):
    if not ok:
        raise ValueError(reason)

def isolate(a,tid):
    tests=a.get("tests")
    check(isinstance(tests,dict) and tid in tests,"source Test missing")
    t=tests[tid]
    check(isinstance(t,dict),"bad imported source Test")
    # A source tests may consume Variables even if the Test node itself
    # does not mention them. A per-Test dataflow closure is not proved here.
    if a.get("variables"):
        raise NotNativeCConvertible("SOURCE_VARIABLE_GRAPH_NOT_TEST_ISOLATABLE")
    oid=t.get("object")
    objects=a.get("objects") or {}
    if type(oid) is not str or oid not in objects:
        raise NotNativeCConvertible("SOURCE_TEST_NO_EXCLUSIVE_OBJECT")
    refs=t.get("states",[])
    if not isinstance(refs,list) or len(refs)>1:
        raise NotNativeCConvertible("SOURCE_TEST_MULTIPLE_OR_INVALID_STATES")
    src_states=a.get("states") or {}
    if any(sid not in src_states for sid in refs):
        raise NotNativeCConvertible("SOURCE_TEST_STATE_NOT_FOUND")
    return {
        "id":a["id"]+".isolated-"+tid,
        "mode":"automated",
        "evaluate":{"test":tid},
        "tests":{tid:deepcopy(t)},
        "objects":{oid:deepcopy(objects[oid])},
        "states":{sid:deepcopy(src_states[sid]) for sid in refs},
    }

def census(review,manifest):
    m=json.loads(Path(manifest).read_text(encoding="utf-8"))
    check(m.get("stage")=="SOURCE_BACKED_NATIVE_C_SUBSET_NOT_SCANNER_PARITY",
          "not an accepted pinned-C manifest")
    bykey={(x["file"],x["definition_id"]) for x in m["native_C_converted"]}
    blocked={(x["file"],x["definition_id"]) for x in m["unsupported"]}
    allkey=bykey|blocked
    check(len(allkey)==m["A_compatible_Definitions_seen"],
          "native C manifest identity accounting incomplete")
    families={}
    detail=[]
    seen=set()
    for path in sorted(Path(review).glob("*.review.json")):
        source=json.loads(path.read_text(encoding="utf-8"))
        rel=source["source"]["file"]
        family=rel.split("/",1)[0]
        if family not in FAMILIES:
            continue
        key=(rel,source["source"]["definition_id"])
        check(key in allkey and key not in seen,
              "review and pinned native C manifest mismatch "+repr(key))
        seen.add(key)
        check(source.get("status")=="C_READ_ONLY_SOURCE_REVIEW_A_COMPATIBILITY_FALLBACK",
              "untrusted original OVAL source review")
        a=source["A_source_compatibility_fallback"]
        original_tests=a.get("tests") or {}
        check(isinstance(original_tests,dict) and original_tests,
              "source-compatible Definition has no imported Tests")
        rows=[]
        for tid,t in sorted(original_tests.items()):
            cap=t.get("capability") if isinstance(t,dict) else "invalid"
            row={"A_source_test_id":tid,"capability":cap}
            try:
                isolated=isolate(a,tid)
                result=compile_one_original_definition(isolated)
                check(result["A_source_semantic_projection_passed"] is True and
                      result["source_test_id"]==tid and
                      result["OVAL_actual_scanner_parity_proven"] is False,
                      "per-Test original source projection proof absent")
                row["C_native_single_Test_compilation"]=True
            except NotNativeCConvertible as exc:
                row["C_native_single_Test_compilation"]=False
                row["rejection"]=str(exc).split(":")[0]
            # Internal failures (KeyError etc.) MUST fail CI, not counted
            # as content compatibility blockers.
            rows.append(row)
        full=key in bykey
        if full:
            check(all(x["C_native_single_Test_compilation"] for x in rows),
                  "complete native Definition contains failed isolated Test")
        detail.append({"source":rel,"definition_id":key[1],
                       "full_native_C_Definition":full,
                       "original_imported_Tests":len(rows),"tests":rows})
    expected={x for x in allkey if x[0].split("/",1)[0] in FAMILIES}
    check(seen==expected,"source-compatible platform Definitions missing in review")
    for family in FAMILIES:
        source=[x for x in detail if x["source"].startswith(family+"/")]
        tests=[y for x in source for y in x["tests"]]
        pass_rows=[x for x in tests if x["C_native_single_Test_compilation"]]
        failures=Counter(x["rejection"] for x in tests
                         if not x["C_native_single_Test_compilation"])
        caps=defaultdict(lambda:{"total":0,"native_C":0})
        for x in tests:
            caps[x["capability"]]["total"]+=1
            caps[x["capability"]]["native_C"]+=int(x["C_native_single_Test_compilation"])
        families[family]={
            "source_compatible_definitions":len(source),
            "native_C_full_definitions":sum(x["full_native_C_Definition"] for x in source),
            "imported_Tests":len(tests),
            "isolated_Tests_native_C_compiled":len(pass_rows),
            "isolated_Tests_not_C_compiled":len(tests)-len(pass_rows),
            "capability_counts":dict(sorted(caps.items())),
            "isolation_rejections":dict(sorted(failures.items())),
        }
    return {"stage":"PINNED_SOURCE_TEST_LEVEL_C_COMPILER_GAP_CENSUS",
            "whole_definition_conversion_claim_from_isolated_test":False,
            "actual_live_collector_execution_proven":False,
            "scanner_6_state_result_parity_proven":False,
            "families":families,"definitions":detail}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--review",type=Path,required=True)
    p.add_argument("--manifest",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    result=census(a.review,a.manifest)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",
                     encoding="utf-8")
    priority={
        "linux/unix-def_sysctl_test.xml",
        "linux/linux-def_partition_test.xml",
        "linux/linux-def_systemdunitproperty_test.xml",
        "linux/linux-def_kernelmodule_test.xml",
        "windows/win-def_service_test.xml",
        "windows/win-def_registry_test.xml",
        "unix/unix-def_file_test.xml",
    }
    selected=[]
    for row in result["definitions"]:
        if row["source"] in priority:
            failed=[{"source_test":x["A_source_test_id"],
                     "reason":x["rejection"]}
                    for x in row["tests"] if not x["C_native_single_Test_compilation"]]
            selected.append({"source":row["source"],
                             "full_native_C_Definition":row["full_native_C_Definition"],
                             "source_Tests":row["original_imported_Tests"],
                             "single_C_Tests_passed":row["original_imported_Tests"]-len(failed),
                             "first_Test_rejections":failed})
    print(json.dumps({"stage":result["stage"],"families":result["families"],
                      "priority_Definition_diagnostics":selected},
                     indent=2,sort_keys=True))

if __name__=="__main__":
    main()
