#!/usr/bin/env python3
"""Audit OVAL 5.12.3 language-surface coverage against corpus + focused fixtures.

This proves representational/test coverage only. It does not claim that a future
NG interpreter implements datatype-specific comparison algorithms correctly.
"""
from __future__ import annotations
import argparse, json, sys
from collections import Counter
from pathlib import Path
from lxml import etree as E

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from inventory_oval_surface import inventory_file, merge

XS="http://www.w3.org/2001/XMLSchema"

ENUM_TYPES=[
    "SimpleDatatypeEnumeration",
    "OperationEnumeration",
    "CheckEnumeration",
    "ExistenceEnumeration",
    "OperatorEnumeration",
]
DEF_ENUM_TYPES=[
    "FilterActionEnumeration",
    "SetOperatorEnumeration",
]

def enum_values(doc,name):
    nodes=doc.xpath(
        f"//xsd:simpleType[@name='{name}']//xsd:enumeration",
        namespaces={"xsd":XS},
    )
    return [n.get("value") for n in nodes]

def empty_inventory():
    return {k:Counter() for k in [
        "test_types","object_types","state_types","variable_types","functions",
        "operations","check","check_existence","state_operator","criteria_operator",
        "set_operator","filter_action","var_check","entity_check","datatypes",
        "behaviors","criteria_nodes","attribute_values",
    ]}

def inventory_xmls(paths):
    total=empty_inventory()
    for p in paths:
        merge(total,inventory_file(p))
    return total

def covered_values(total,bucket):
    return set(total.get(bucket,{}))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--schema-dir",type=Path,required=True)
    ap.add_argument("--corpus-inventory",type=Path,required=True)
    ap.add_argument("--focused-source-dir",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args()

    common=E.parse(str(a.schema_dir/"oval-common-schema.xsd"))
    defs=E.parse(str(a.schema_dir/"oval-definitions-schema.xsd"))
    corpus=json.loads(a.corpus_inventory.read_text())
    corpus_totals={k:Counter(v) for k,v in corpus.get("totals",{}).items()}
    focused_paths=sorted(a.focused_source_dir.glob("*.xml"))
    focused=inventory_xmls(focused_paths)

    mapping={
        "SimpleDatatypeEnumeration":"datatypes",
        "OperationEnumeration":"operations",
        "CheckEnumeration":"check",
        "ExistenceEnumeration":"check_existence",
        "OperatorEnumeration":"criteria_operator",
        "FilterActionEnumeration":"filter_action",
        "SetOperatorEnumeration":"set_operator",
    }

    rows=[]
    for name in ENUM_TYPES:
        vals=enum_values(common,name)
        bucket=mapping[name]
        for value in vals:
            rows.append({
                "kind":name,
                "value":value,
                "rhel9":value in covered_values(corpus_totals,bucket),
                "focused":value in covered_values(focused,bucket),
            })
    for name in DEF_ENUM_TYPES:
        vals=enum_values(defs,name)
        bucket=mapping[name]
        for value in vals:
            rows.append({
                "kind":name,
                "value":value,
                "rhel9":value in covered_values(corpus_totals,bucket),
                "focused":value in covered_values(focused,bucket),
            })

    # Core variable functions are explicit XSD elements in FunctionGroup.
    function_names={
        "arithmetic","begin","concat","end","escape_regex","split","substring",
        "time_difference","regex_capture","unique","merge","count","glob_to_regex",
    }
    all_funcs=covered_values(corpus_totals,"functions")|covered_values(focused,"functions")
    function_rows=[{
        "function":x,
        "rhel9":x in covered_values(corpus_totals,"functions"),
        "focused":x in covered_values(focused,"functions"),
    } for x in sorted(function_names)]

    uncovered=[r for r in rows if not (r["rhel9"] or r["focused"])]
    uncovered_functions=[r for r in function_rows if not (r["rhel9"] or r["focused"])]

    out={
        "format":"oval-ng-language-surface-coverage-0.1",
        "scope_note":"Coverage means source/round-trip representation exercised; it does not prove interpreter comparison algorithms.",
        "focused_fixture_count":len(focused_paths),
        "enumerations":rows,
        "functions":function_rows,
        "uncovered_enumerations":uncovered,
        "uncovered_functions":uncovered_functions,
        "complete_for_tracked_surface":not uncovered and not uncovered_functions,
    }
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
        "focused_fixture_count":len(focused_paths),
        "uncovered_enumeration_count":len(uncovered),
        "uncovered_function_count":len(uncovered_functions),
        "complete_for_tracked_surface":out["complete_for_tracked_surface"],
        "uncovered_enumerations":uncovered,
        "uncovered_functions":uncovered_functions,
    },indent=2))
if __name__=="__main__": main()
