#!/usr/bin/env python3
"""Research #235/#229: observable semantic traps in readable SCAP-NG patterns.

Fixed, independently asserted boundary cases for Object/State Variables,
collection filtering and records. These do not replace scanner-evidence tests.
The corresponding source fixtures include Windows 11 SV-253495 and
Windows Server 2025 SV-278138, plus DNS source-dependent Variables.
"""
import argparse
import json
from pathlib import Path
from itertools import product
from oval_result_truth_tables import (
    TRUE,FALSE,ERROR,UNKNOWN,NOT_EVALUATED,NOT_APPLICABLE,
    resolve_variable_reference,apply_variable_reference_context,
    apply_filter_state_result,evaluate_record_field,evaluate_record_entity,
    evaluate_variable_entity_reference,
    aggregate_many_to_many,combine_set_flags,SET_FLAGS,SET_FLAG_TABLES,
)
from research_english_first_04_evaluate import reject_naive_wmi_alternative_merge

def require(actual,expected,name):
    if actual!=expected:
        raise AssertionError(f"{name}: expected {expected!r}, got {actual!r}")

def run():
    cases={}
    empty=resolve_variable_reference([])
    for context, expected in [
        ("object","does_not_exist"),("state",ERROR),("direct_test",ERROR)
    ]:
        require(apply_variable_reference_context(empty,context),expected,"empty "+context)
        cases["empty_variable_"+context]=expected
    for action in ("include","exclude"):
        for state, expected in {
            TRUE:action=="include", FALSE:action=="exclude",
            ERROR:ERROR, UNKNOWN:ERROR,
            NOT_EVALUATED:ERROR, NOT_APPLICABLE:ERROR,
        }.items():
            require(apply_filter_state_result(action,state),expected,
                    f"{action} filter on {state}")
            cases[f"filter_{action}_{state.replace(' ','_')}"]=str(expected).lower()
    require(evaluate_record_field("tpmpresent",[]),ERROR,"missing record field")
    require(evaluate_record_field("domainrole",[TRUE,FALSE]),FALSE,
            "multi-valued record field all-match")
    require(evaluate_record_entity([TRUE,FALSE]),FALSE,"record all-fields")
    require(evaluate_record_entity([TRUE,UNKNOWN]),UNKNOWN,"record unknown")
    cases["missing_expected_record_field"]=ERROR
    cases["multi_field_record_mixed"]=FALSE
    cases["multi_field_record_unknown"]=UNKNOWN
    rows=[[TRUE,FALSE],[FALSE,TRUE]]
    require(aggregate_many_to_many(var_check="at least one",entity_check="all",
                                   comparison_rows=rows),TRUE,
            "many-to-many row-major var_check then entity_check")
    require(aggregate_many_to_many(var_check="all",entity_check="at least one",
                                   comparison_rows=rows),FALSE,
            "many-to-many all variable values per entity")
    cases["cross_value_aggregation"]=["row-major at-least-one/all => true",
                                     "row-major all/at-least-one => false"]
    require(evaluate_variable_entity_reference(variable_status=ERROR,
                       var_check="at least one",entity_check="all"),ERROR,
            "unresolved State Variable cannot evaluate as a match")
    cases["unresolved_variable_propagation"]=ERROR
    set_cases=0
    for operator, rows in SET_FLAG_TABLES.items():
        for first,second in product(SET_FLAGS,repeat=2):
            expected=rows[second][SET_FLAGS.index(first)]
            require(combine_set_flags(operator,first,second),expected,
                    f"{operator}({first},{second})")
            set_cases+=1
    wmi=reject_naive_wmi_alternative_merge()
    if not wmi.get("counterexample_record_values"):
        raise AssertionError("WMI State alternative false-equivalence not detected")
    cases["wmi_two_record_counterexample"]=wmi["counterexample_record_values"]
    return {
        "status":"PASS: SCAP-NG English-first semantic boundary guards; not independent scanner parity",
        "case_count":len(cases),
        "set_flag_combinations_checked":set_cases,
        "cases":cases,
        "source_notes":{
            "WMI":"Windows 11 SV-253495 has independent whole-State alternatives, not one per-record membership condition",
            "Windows file rights":"Windows Server 2025 SV-278138 has ordered Set exclude filters and many permission fields",
            "Variables":"DNS SV-259345 and Apache SV-214228 use derived Variables whose missing-value context matters"
        },
        "limitations":"Does not collect target data; underlying reference functions are the repository's OVAL generic model, not an independent certified SCAP 1.4 scanner."
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output")
    a=p.parse_args()
    r=run()
    if a.output:Path(a.output).write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":r["status"],"case_count":r["case_count"],
                      "set_flag_combinations_checked":r["set_flag_combinations_checked"]},indent=2))

if __name__=="__main__":main()
