#!/usr/bin/env python3
"""Audit OVAL 5.12.3 language-surface coverage against corpus + focused fixtures.

The authoritative inventory is derived from the OVAL 5.12.3 XSD bundle.
Coverage here proves that a construct is represented by the round-trip harness;
it does not prove a future NG interpreter's runtime algorithms.
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
OVAL_COMMON="http://oval.mitre.org/XMLSchema/oval-common-5"

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

FUNCTION_NAMES={
    "arithmetic","begin","concat","end","escape_regex","split","substring",
    "time_difference","regex_capture","unique","merge","count","glob_to_regex",
}

CORE_FEATURES={
    "variable_types":{"constant_variable","external_variable","local_variable"},
    "component_types":{"literal_component","object_component","variable_component"},
    "criteria_nodes":{"criteria","criterion","extend_definition"},
    "entity_features":{"record_field","xsi:nil=true"},
    "set_forms":{"leaf","nested"},
    # Explicit true values exercise the behaviorally meaningful non-default edge.
    "criteria_features":{
        "criteria@negate=true",
        "criteria@applicability_check=true",
        "criterion@negate=true",
        "criterion@applicability_check=true",
        "extend_definition@negate=true",
        "extend_definition@applicability_check=true",
    },
}

def oval_dir(schema_dir:Path)->Path:
    candidate=schema_dir/"oval_5.12.3"
    return candidate if candidate.exists() else schema_dir

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
        "behaviors","criteria_nodes","component_types","entity_features",
        "criteria_features","set_forms","attribute_values",
    ]}

def inventory_xmls(paths):
    total=empty_inventory()
    for p in paths:
        merge(total,inventory_file(p))
    return total

def covered_values(total,bucket):
    return set(total.get(bucket,{}))

def schema_family_surface(odir:Path):
    rows=[]
    for path in sorted(odir.glob("*-definitions-schema.xsd")):
        if path.name=="oval-definitions-schema.xsd":
            continue
        doc=E.parse(str(path))
        root=doc.getroot()
        target=root.get("targetNamespace") or ""
        family=target.split("#")[-1] if "#" in target else target
        for el in root.xpath("./xsd:element[@substitutionGroup]",namespaces={"xsd":XS}):
            sg=el.get("substitutionGroup")
            kind={"oval-def:test":"test_types","oval-def:object":"object_types",
                  "oval-def:state":"state_types"}.get(sg)
            if not kind:
                continue
            name=el.get("name")
            deprecated=bool(el.xpath(".//oval:deprecated_info",namespaces={"oval":OVAL_COMMON}))
            dep_version=el.xpath("string(.//oval:deprecated_info/oval:version)",namespaces={"oval":OVAL_COMMON}) or None
            dep_reason=el.xpath("string(.//oval:deprecated_info/oval:reason)",namespaces={"oval":OVAL_COMMON}) or None
            rows.append({
                "bucket":kind,
                "family":family,
                "name":name,
                "key":f"{family}.{name}",
                "deprecated":deprecated,
                "deprecated_version":dep_version,
                "deprecated_reason":dep_reason,
            })
    return rows

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--schema-dir",type=Path,required=True)
    ap.add_argument("--corpus-inventory",type=Path,required=True)
    ap.add_argument("--focused-source-dir",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args()

    odir=oval_dir(a.schema_dir)
    common=E.parse(str(odir/"oval-common-schema.xsd"))
    defs=E.parse(str(odir/"oval-definitions-schema.xsd"))
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

    enum_rows=[]
    for name in ENUM_TYPES:
        for value in enum_values(common,name):
            bucket=mapping[name]
            enum_rows.append({
                "kind":name,"value":value,
                "rhel9":value in covered_values(corpus_totals,bucket),
                "focused":value in covered_values(focused,bucket),
            })
    for name in DEF_ENUM_TYPES:
        for value in enum_values(defs,name):
            bucket=mapping[name]
            enum_rows.append({
                "kind":name,"value":value,
                "rhel9":value in covered_values(corpus_totals,bucket),
                "focused":value in covered_values(focused,bucket),
            })

    function_rows=[{
        "function":x,
        "rhel9":x in covered_values(corpus_totals,"functions"),
        "focused":x in covered_values(focused,"functions"),
    } for x in sorted(FUNCTION_NAMES)]

    core_rows=[]
    for bucket,values in CORE_FEATURES.items():
        for value in sorted(values):
            core_rows.append({
                "bucket":bucket,"value":value,
                "rhel9":value in covered_values(corpus_totals,bucket),
                "focused":value in covered_values(focused,bucket),
            })

    family_rows=schema_family_surface(odir)
    for row in family_rows:
        bucket=row["bucket"]; key=row["key"]
        row["rhel9"]=key in covered_values(corpus_totals,bucket)
        row["focused"]=key in covered_values(focused,bucket)
        row["coverage_status"]=(
            "deprecated_rejected" if row["deprecated"] else
            "covered" if (row["rhel9"] or row["focused"]) else
            "valid_not_yet_exercised"
        )

    uncovered_enums=[r for r in enum_rows if not (r["rhel9"] or r["focused"])]
    uncovered_funcs=[r for r in function_rows if not (r["rhel9"] or r["focused"])]
    uncovered_core=[r for r in core_rows if not (r["rhel9"] or r["focused"])]
    supported_families=[r for r in family_rows if not r["deprecated"]]
    deprecated_families=[r for r in family_rows if r["deprecated"]]
    uncovered_families=[r for r in supported_families if not (r["rhel9"] or r["focused"])]

    out={
        "format":"oval-ng-language-surface-coverage-0.2",
        "scope_note":"Coverage means source/round-trip representation exercised; it does not prove interpreter runtime algorithms.",
        "schema_directory":str(odir),
        "focused_fixture_count":len(focused_paths),
        "enumerations":enum_rows,
        "functions":function_rows,
        "core_features":core_rows,
        "schema_families":family_rows,
        "deprecated_policy":"Deprecated OVAL Test/Object/State families are inventoried explicitly and are NG conversion rejection targets, not support requirements.",
        "uncovered_enumerations":uncovered_enums,
        "uncovered_functions":uncovered_funcs,
        "uncovered_core_features":uncovered_core,
        "uncovered_supported_families":uncovered_families,
        "deprecated_families":deprecated_families,
        "tracked_core_complete":not uncovered_enums and not uncovered_funcs and not uncovered_core,
        "counts":{
            "schema_family_nodes":len(family_rows),
            "supported_family_nodes":len(supported_families),
            "deprecated_family_nodes":len(deprecated_families),
            "covered_supported_family_nodes":sum(1 for r in supported_families if r["rhel9"] or r["focused"]),
            "uncovered_supported_family_nodes":len(uncovered_families),
        },
    }
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
        "focused_fixture_count":len(focused_paths),
        "uncovered_enumeration_count":len(uncovered_enums),
        "uncovered_function_count":len(uncovered_funcs),
        "uncovered_core_feature_count":len(uncovered_core),
        "tracked_core_complete":out["tracked_core_complete"],
        "family_counts":out["counts"],
        "uncovered_enumerations":uncovered_enums,
        "uncovered_functions":uncovered_funcs,
        "uncovered_core_features":uncovered_core,
    },indent=2))
if __name__=="__main__": main()
