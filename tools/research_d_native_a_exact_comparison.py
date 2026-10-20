#!/usr/bin/env python3
"""Refs #246: independently construct *native base 0.4-A* from original OVAL Set.

Do not confuse pinned v003 roundtrip source IR with authored 0.4-A.
The conversion here is explicit/reviewable and every generated Test is checked
against the actual version-local 0.4-A native schema. Source runtime parity
is not established by passing a JSON Schema gate. The 0.4-A and 0.4-D
implementation/code is not modified.
"""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import argparse
import json
import yaml

from research_04_native_deep_content_census import (
    ROOT_ASSESSMENT_VALIDATOR, validator_for, SUPPORTED)
from research_04_one_grammar_proof import CODES, EXISTS
from research_04_field_key_authoring import fold_node

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"research/assessment-simplification/04d-lossless-oval-set/original-source-compatible-a.json"
SOURCE_EXISTENCE={
    "only_one_exists":"one", "at_least_one_exists":"one_or_more",
    "none_exist":"none", "all_exist":"all", "any_exist":"optional"}
OPS={"equals":"equals","pattern_match":"matches_regex"}
CAP="unix.file"


def _fail(message):
    raise ValueError("Native 0.4-A UNIX Set conversion: "+message)


def _state(original):
    if original["capability"]!=CAP:
        _fail("source State capability differs")
    state=original["state"]
    if state.get("field")!="path" or state.get("operation")!="equals":
        _fail("unproven original State datatype/operation")
    if state.get("datatype")!="string" or (
        state.get("entity_existence")!="at_least_one_exists" or
        state.get("entity_check")!="all"):
        _fail("original field entity quantifier not accounted for")
    result={"directory":{
        "require":"at_least_one_exists_and_all_match",
        "equals":deepcopy(state["value"]),
        "datatype":"string"
    }}
    if isinstance(state["value"],dict):
        if set(state["value"])!={"variable"} or state.get("variable_check")!="only one":
            _fail("unproven multivalue value_check")
        result["directory"]["value_match"]="one"
    elif "variable_check" in state:
        _fail("scalar literal State value_check unsupported")
    return result


def _leaf_object(raw):
    if set(raw)!={"capability","object_title","select","behaviors"} or raw["capability"]!=CAP:
        _fail("unexpected original typed leaf Object")
    select=raw["select"]
    if not isinstance(select,dict) or set(select)!={"path","filename"}:
        _fail("source path/filename selectors unsupported")
    path,filename=select["path"],select["filename"]
    if path!={"datatype":"string","operation":"equals","value":path.get("value")} or not isinstance(path["value"],str):
        _fail("original directory selector unsupported")
    if filename!={"datatype":"string","operation":"equals","nil":True,"value":""}:
        _fail("source nil filename cannot be guessed")
    old=raw["behaviors"]
    if set(old)!={"max_depth","recurse_direction","recurse_file_system"} or (
        old["max_depth"]!="-1" or
        old["recurse_direction"] not in ("down","none") or
        old["recurse_file_system"]!="local"):
        _fail("unproven original traversal behavior")
    result={"capability":CAP,
            "object_title":raw["object_title"],
            "select":{"directory":{"equals":path["value"]},"name":None},
            # Input provenance exact; whether this source OVAL behavior maps
            # natively in 0.4-A is separately capability-schema checked.
            "behaviors":deepcopy(old)}
    return result


def _set_member(raw,states,depth=0):
    if depth>30 or not isinstance(raw,dict) or len(raw)!=1:
        _fail("unsupported original nested Set member")
    if "object" in raw:
        return {"object":raw["object"],"filters":[]}
    if "set" in raw:
        return {"set":_set_expr(raw["set"],states,depth+1)}
    _fail("unrecognized original Set member")


def _set_expr(raw,states,depth=0):
    if depth>30 or not isinstance(raw,dict) or set(raw) not in (
        {"operator","members"},{"operator","members","filters"}):
        _fail("unsupported source Set shape")
    mapping={"union":"union","intersection":"intersection",
             "complement":"difference"}
    op=mapping.get(raw["operator"])
    if not op:
        _fail("unrecognized OVAL Set operator")
    operands=[_set_member(x,states,depth+1) for x in raw["members"]]
    if not operands:
        _fail("empty Set operands")
    if "filters" in raw:
        # The one source filter Set has one raw Object member. This is
        # a single-operand Set, so the original filter is correlated to
        # that one operand and is not silently applied to a later union.
        if len(operands)!=1 or set(operands[0])!={"object","filters"}:
            _fail("cannot relocate multi-operand filter")
        for entry in raw["filters"]:
            if set(entry)!={"action","state"} or entry["action"] not in ("include","exclude"):
                _fail("unknown Filter action/State")
            if entry["state"] not in states:
                _fail("unresolved source Filter State")
            operands[0]["filters"].append({
                entry["action"]:_state(states[entry["state"]])})
    return {"operator":op,"operands":operands}


def convert(original):
    if original["specification"]!={"id":"scap-ng.pre-alpha.assessment","version":"0.3.0"}:
        _fail("source is not the pinned v003 imported OVAL")
    if (len(original["tests"]),len(original["objects"]),
        len(original["states"]),len(original["variables"]))!=(7,11,4,3):
        _fail("pinned original OVAL inventory changed")
    test_ids={sid:sid.replace("test-test-that-","").replace("test-test-","")+
               "-test" for sid in original["tests"]}
    if len(set(test_ids.values()))!=7:
        _fail("duplicate renamed Test ID")
    native={
        "id":original["id"],"version":original["version"],
        "assessment_title":original["assessment_title"],
        "mode":original["mode"],"class":original["class"],
        "purpose":original["purpose"],
        "specification":{"id":"scap-ng.pre-alpha.assessment","version":"0.4.0"},
        "variables":deepcopy(original["variables"]),
        "shared_objects":{},
        "tests":{},
        "evaluate":deepcopy(original["evaluate"]),
    }
    for oid,raw in original["objects"].items():
        if "set" in raw:
            ob={"capability":CAP,"object_title":raw["object_title"],
                "set":_set_expr(raw["set"],original["states"])}
        else:
            ob=_leaf_object(raw)
        native["shared_objects"][oid]=ob
    for sid,t in original["tests"].items():
        if set(t)-{"capability","check","check_existence","object",
                   "reported_elements","states","test_title"}:
            _fail("unknown original Test feature "+sid)
        if t["capability"]!=CAP or t["check"]!="all":
            _fail("unsupported Test capability/check")
        existence=SOURCE_EXISTENCE.get(t["check_existence"])
        if existence is None:_fail("unknown OVAL check_existence")
        old_refs=t.get("states",[])
        if old_refs:
            token=CODES[(existence,"all")]
        else:
            token=EXISTS[existence]
        output={"test_title":t["test_title"],
                "reported_elements":t["reported_elements"],
                "capability":CAP,"object":t["object"],
                "require":token}
        if old_refs:
            output["states"]=[_state(original["states"][ref]) for ref in old_refs]
            if len(old_refs)>1:output["states_match"]="all"
        native["tests"][test_ids[sid]]=output
    def rewrite(node):
        if isinstance(node,list):return [rewrite(x) for x in node]
        if not isinstance(node,dict):return deepcopy(node)
        if set(node)=={"test"}:
            return {"test":test_ids[node["test"]]}
        return {k:rewrite(v) for k,v in node.items()}
    native["evaluate"]=rewrite(original["evaluate"])
    return {"assessment":native},test_ids


def audit(original):
    doc,ids=convert(original)
    errors=list(ROOT_ASSESSMENT_VALIDATOR.iter_errors(doc))
    cap_errors={}
    v=validator_for(CAP,{})
    for tid,test in doc["assessment"]["tests"].items():
        err=list(v.iter_errors(test))
        if err:
            cap_errors[tid]=[
                {"path":list(x.absolute_path),"message":x.message[:420]}
                for x in err[:5]]
    report={
      "real_04a_base_assessment_schema_validation":not bool(errors),
      "real_04a_unix_file_test_schema_validation":not bool(cap_errors),
      "assessment_schema_errors":[{"path":list(e.absolute_path),"message":e.message[:420]}
                                  for e in errors[:12]],
      "native_capability_test_errors":cap_errors,
      "original_source_tests":7,"original_objects":11,
      "original_states":4,"original_variables":3,
      "compiled_04a_tests":len(doc["assessment"]["tests"]),
      "compiled_04a_shared_objects":len(doc["assessment"]["shared_objects"]),
      "original_v003_source_graph_deep_equal_to_04a":False,
      "runtime_oracle_equivalence_proven":False,
      "source_test_id_crosswalk":ids,
      "basis":"Pinned v003 original OVAL source re-authored against actual v0.4.0 schemas",
    }
    return doc,report


def export(output):
    source=json.loads(SOURCE.read_text(encoding="utf-8"))
    candidate,report=audit(source)
    output.mkdir(parents=True,exist_ok=True)
    (output/"unix-set-seven-tests.native-0.4-A-comparison.yaml").write_text(
        "# 0.4-A attempt from original OVAL def 276; see explicit validator report.\n"
        +yaml.safe_dump(candidate,sort_keys=False,allow_unicode=True),
        encoding="utf-8")
    (output/"a-validation-proof.json").write_text(
        json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return report


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    print(json.dumps(export(args.out),sort_keys=True))
