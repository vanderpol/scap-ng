#!/usr/bin/env python3
"""Refs #246 exact *native* 0.4-A comparator for seven-Test original OVAL Set.

Import the actual source-compatible 0.3 graph, use the existing reviewed
0.4-A converter/validator and report unsupported source shapes. Never
relabel 0.3 as 0.4-A or weaken schemas to make the comparison pass.
Does not modify A, D, or their existing schemas.
"""
from __future__ import annotations
import argparse
from copy import deepcopy
import json
from pathlib import Path
import yaml

from research_04_one_grammar_proof import (
    make_single, lower_single, normalize_inert_source_checks,
    check_no_parallel_comparison_or_cardinality_grammar)
from migrate_v04_enum_selectors import migrate,restore
from research_04_native_deep_content_census import (
    ROOT_ASSESSMENT_VALIDATOR, SUPPORTED_MAPPING_DATA, SUPPORTED, validator_for)

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"research/assessment-simplification/04d-lossless-oval-set/original-source-compatible-a.json"


def transform():
    original=json.loads(SOURCE.read_text(encoding="utf-8"))
    if (original.get("specification")!={
        "id":"scap-ng.pre-alpha.assessment","version":"0.3.0"} or
        len(original["tests"])!=7 or len(original["objects"])!=11 or
        len(original["states"])!=4 or len(original["variables"])!=3):
        raise ValueError("pinned source graph changed: refuse A conversion")
    original_wrapper={"assessment":deepcopy(original)}
    compact,counts,notes=make_single(original_wrapper)
    recovered=lower_single(compact)
    if recovered!=normalize_inert_source_checks(original_wrapper,notes):
        raise ValueError("reviewed native A grammar conversion is not reversible")
    check_no_parallel_comparison_or_cardinality_grammar(compact)
    converted,migrations=migrate(compact,SUPPORTED_MAPPING_DATA)
    if restore(converted,migrations)!=compact:
        raise ValueError("A selector migration is not reversible")
    converted["assessment"]["specification"]["version"]="0.4.0"
    report={
      "source":"pinned original OVAL 5.12.3 Self-Assertion UNIX Set Definition 276",
      "source_tests":7,"source_objects":11,"source_states":4,"source_variables":3,
      "reviewed_a_reversible_grammar_conversion":True,
      "state_free_normalization_count":len(notes),
      "selector_migrations":len(migrations),
      "normative_04a_schema_validated":False,
      "all_native_capability_tests_validated":False,
      "scanner_runtime_parity_proven":False,
      "converted_04a_source_prototype":True,
    }
    errors=list(ROOT_ASSESSMENT_VALIDATOR.iter_errors(converted))
    report["base_assessment_errors"]=[
        {"path":list(e.path),"error":e.message[:550]} for e in errors[:15]]
    report["normative_04a_schema_validated"]=not bool(errors)
    caperrors={}
    for name,test in converted["assessment"]["tests"].items():
        cap=test.get("capability")
        if cap not in SUPPORTED:
            caperrors[name]=["Unsupported capability: "+str(cap)]
            continue
        found=list(validator_for(cap,{}).iter_errors(test))
        if found:
            caperrors[name]=[
                {"path":list(e.path),"error":e.message[:400]} for e in found[:3]]
    report["capability_test_errors"]=caperrors
    report["all_native_capability_tests_validated"]=not bool(caperrors)
    return converted,report


def export(out):
    authored,proof=transform()
    out.mkdir(parents=True,exist_ok=True)
    (out/"unix-set-seven-tests.0.4-A-conversion-candidate.yaml").write_text(
        "# Experimental direct 0.4-A conversion; native schema status in proof.\n"
        "# Original source OVAL 5.12.3 UNIX Set def 276; source-compatible v003 IR.\n"
        +yaml.safe_dump(authored,sort_keys=False,allow_unicode=True),encoding="utf-8")
    (out/"a-conversion-proof.json").write_text(
        json.dumps(proof,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return proof

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    print(json.dumps(export(a.out),sort_keys=True))
