#!/usr/bin/env python3
"""Pinned OVAL 5.12.3 constant-Variable family_test -> canonical SCAP-NG 0.4.0.

Exactly one family_test, its no-selector family_object, a family_state with
pattern-match var_ref and var_check=all, and a single string constant_variable.
No source XML re-export occurs here. Unsupported differences fail closed.
Refs #248 #229 #232.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from v04_flat_object_authoring import dump_hybrid, digest

BASE="http://oval.mitre.org/XMLSchema/oval-definitions-5"
INDEPENDENT=BASE+"#independent"
OVAL_COMMON="http://oval.mitre.org/XMLSchema/oval-common-5"
SOURCE_REVISION="e3538595c5083b9c34d937a81d319234df9bbfaa"
SOURCE_PATH="agnostic/ind-def_family_test.xml"
NAME="supported-platform-families-variable"
TEST_NAME="system-family-matches-test"

def q(uri,name):
    return "{"+uri+"}"+name

def demand(ok,reason):
    if not ok:
        raise ValueError("Unsupported original OVAL family Variable case: "+reason)

def only(parent,name,uri):
    found=parent.findall(q(uri,name))
    demand(len(found)==1,name+" cardinality")
    return found[0]

def convert(path):
    data=Path(path).read_bytes()
    root=ET.fromstring(data)
    demand(root.tag==q(BASE,"oval_definitions"),"root namespace")
    defn=only(only(root,"definitions",BASE),"definition",BASE)
    did=defn.get("id")
    demand(did and defn.get("version") and
           defn.get("class")=="miscellaneous","Definition identity/class")
    metadata=only(defn,"metadata",BASE)
    title=only(metadata,"title",BASE).text
    demand(title and title.strip(),"missing title")
    criteria=only(defn,"criteria",BASE)
    demand(set(criteria.attrib)<= {"operator"} and
           criteria.get("operator","AND")=="AND","Boolean criteria")
    criterion=only(criteria,"criterion",BASE)
    demand(len(criteria)==1 and
           criterion.get("negate","false")=="false" and
           criterion.get("test_ref") and
           set(criterion.attrib)<={"comment","test_ref","negate"},
           "criterion reference or negation")
    src_test=only(only(root,"tests",BASE),"family_test",INDEPENDENT)
    test_id=src_test.get("id")
    demand(test_id==criterion.get("test_ref") and
           src_test.get("check")=="at least one" and
           src_test.get("check_existence")=="at_least_one_exists" and
           set(src_test.attrib)<={"id","version","comment","check_existence","check"},
           "OVAL Test check/check_existence or attrs")
    oval_object=only(src_test,"object",INDEPENDENT)
    oval_state=only(src_test,"state",INDEPENDENT)
    demand(len(src_test)==2 and
           bool(oval_object.get("object_ref")) and
           bool(oval_state.get("state_ref")),
           "Test Object/State references")
    obj=only(only(root,"objects",BASE),"family_object",INDEPENDENT)
    state=only(only(root,"states",BASE),"family_state",INDEPENDENT)
    var=only(only(root,"variables",BASE),"constant_variable",BASE)
    demand(obj.get("id")==oval_object.get("object_ref") and len(obj)==0,
           "family_object must be the singleton empty source")
    demand(state.get("id")==oval_state.get("state_ref") and len(state)==1,
           "family_state closure")
    field=only(state,"family",INDEPENDENT)
    demand(set(field.attrib)=={"operation","var_check","var_ref"} and
           field.get("operation")=="pattern match" and
           field.get("var_check")=="all" and
           field.get("var_ref")==var.get("id") and
           field.text in (None,""),
           "family State regex Variable operation and cardinality")
    demand(len(var)==1 and var.get("datatype")=="string" and
           set(var.attrib)<={"id","version","comment","datatype"},
           "constant string Variable semantics")
    literal=only(var,"value",BASE)
    demand(literal.text is not None and literal.text and
           set(literal.attrib)==set(),"source constant value/attrs")
    value=literal.text
    demand(test_id and var.get("id") and state.get("id") and obj.get("id") and
           len({test_id,state.get("id"),obj.get("id"),var.get("id"),did})==5,
           "OVAL source ID closure")
    assessment={
        "id":"oval-family-constant-variable-assessment",
        "version":int(defn.get("version")),
        "assessment_title":title,
        "mode":"automated",
        "class":"miscellaneous",
        "purpose":"assessment",
        "specification":{
            "id":"scap-ng.pre-alpha.assessment","version":"0.4.0"
        },
        "variables":{NAME:{
            "kind":"constant","datatype":"string",
            "title":var.get("comment") or "Family pattern",
            "expression":{"literal":value}
        }},
        "tests":{TEST_NAME:{
            "test_title":src_test.get("comment") or "System family",
            "capability":"independent.family",
            # family_object is an implicit singleton source in 0.4.0
            "states":[{
                "family":{
                    "matches_regex":{"variable":NAME},
                    "datatype":"string",
                    "value_match":"all",
                    "require":"at_least_one_exists_and_all_match"
                }
            }],
            "reported_elements":"all",
            "require":"at_least_one_exists_and_some_match"
        }},
        "evaluate":{"test":TEST_NAME}
    }
    report={
        "source_repository":"OVAL-Community/SCAP-Self-Assertion",
        "source_revision":SOURCE_REVISION,
        "source_path":SOURCE_PATH,
        "original_xml_sha256":sha256(data).hexdigest(),
        "original_definition_id":did,
        "original_test_id":test_id,
        "original_object_id":obj["id"],
        "original_state_id":state["id"],
        "original_variable_id":var["id"],
        "source_constant":value,
        "source_operation":"pattern match",
        "source_var_check":"all",
        "source_test_check":"at least one",
        "source_check_existence":"at_least_one_exists",
        "scap_ng_assessment_sha256":digest(assessment),
        "scap_ng_variable_name":NAME,
        "scap_ng_test_name":TEST_NAME,
        "source_xml_closure":"PASS_NO_SELECTORS_AND_ONE_CONSTANT",
        "native_040_schema":"PENDING",
        "independent_oval_5123_xml_semantics":"PENDING",
        "scanner_result_parity":"NOT_PROVEN"
    }
    return {"assessment":assessment},report

def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument("--source",type=Path,required=True)
    a.add_argument("--output",type=Path,required=True)
    a.add_argument("--report",type=Path,required=True)
    args=a.parse_args()
    doc,proof=convert(args.source)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(dump_hybrid(doc),encoding="utf-8")
    args.output.with_suffix(".json").write_text(json.dumps(doc,indent=2)+"\n",encoding="utf-8")
    args.report.write_text(json.dumps(proof,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in proof.items() if k!="source_constant"},indent=2))

if __name__=="__main__":
    main()
