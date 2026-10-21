#!/usr/bin/env python3
"""Independent native 0.4.0 family/constant Variable -> OVAL 5.12.3 XML.

Never loads original XML or the source-review fallback. This exporter supports
the narrow native independent.family singleton collection Test and one string
constant Variable; all other syntax fails closed. Refs #248 #229 #232.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET

OD="http://oval.mitre.org/XMLSchema/oval-definitions-5"
OC="http://oval.mitre.org/XMLSchema/oval-common-5"
IND=OD+"#independent"


def q(ns,name):
    return "{"+ns+"}"+name


def require(cond,problem):
    if not cond:
        raise ValueError("Unsupported native 0.4 family OVAL exporter: "+problem)


def export(native):
    a=native.get("assessment") if isinstance(native,dict) else None
    require(isinstance(a,dict) and set(a)=={
        "id","version","assessment_title","mode","class","purpose",
        "specification","variables","tests","evaluate"},
        "not a single canonical 0.4 automated Assessment")
    require(a["mode"]=="automated" and a["class"]=="miscellaneous" and
            a["purpose"]=="assessment" and a["version"]==1 and
            a["specification"]=={
                "id":"scap-ng.pre-alpha.assessment","version":"0.4.0"},
            "Assessment class/version/source changed")
    tests=a["tests"]
    variables=a["variables"]
    require(isinstance(tests,dict) and len(tests)==1 and
            isinstance(variables,dict) and len(variables)==1,
            "only one family Test and one constant Variable")
    test_name,test=next(iter(tests.items()))
    variable_name,variable=next(iter(variables.items()))
    require(a["evaluate"]=={"test":test_name} and
            test_name.endswith("-test") and variable_name.endswith("-variable"),
            "unproven Test or Variable binding")
    require(set(test)=={"test_title","capability","reported_elements","states","require"} and
            test["capability"]=="independent.family" and
            test["reported_elements"]=="all" and
            test["require"]=="at_least_one_exists_and_some_match" and
            isinstance(test["test_title"],str) and
            test["test_title"].strip(),
            "Test Item/matching semantics unsupported")
    state=test["states"]
    require(isinstance(state,list) and len(state)==1 and
            isinstance(state[0],dict) and set(state[0])=={"family"},
            "not one family State")
    field=state[0]["family"]
    require(isinstance(field,dict) and set(field)=={
        "matches_regex","datatype","value_match","require"} and
            field["datatype"]=="string" and field["value_match"]=="all" and
            field["require"]=="at_least_one_exists_and_all_match" and
            field["matches_regex"]=={"variable":variable_name},
            "family match/Variable cardinality not source-equivalent")
    require(isinstance(variable,dict) and
            variable.get("kind")=="constant" and
            variable.get("datatype")=="string" and
            isinstance(variable.get("title"),str) and
            isinstance(variable.get("expression"),dict) and
            set(variable["expression"])=={"literal"} and
            isinstance(variable["expression"]["literal"],str) and
            variable["expression"]["literal"] and
            set(variable)=={"kind","datatype","title","expression"},
            "not exactly one typed string constant")
    require(isinstance(a["assessment_title"],str) and a["assessment_title"].strip(),
            "missing source Definition title")
    prefix="oval:scap-ng.v04.family.variable.pilot:"
    did=prefix+"def:1"
    tid=prefix+"tst:1"
    oid=prefix+"obj:1"
    sid=prefix+"ste:1"
    vid=prefix+"var:1"
    for key,ns in (("oval-def",OD),("oval",OC),("ind-def",IND)):
        ET.register_namespace(key,ns)
    root=ET.Element(q(OD,"oval_definitions"))
    generator=ET.SubElement(root,q(OD,"generator"))
    ET.SubElement(generator,q(OC,"product_name")).text="Independent SCAP-NG 0.4 family OVAL XML exporter"
    ET.SubElement(generator,q(OC,"schema_version")).text="5.12.3"
    ET.SubElement(generator,q(OC,"timestamp")).text="2026-10-21T00:00:00Z"
    defs=ET.SubElement(root,q(OD,"definitions"))
    definition=ET.SubElement(defs,q(OD,"definition"),{
        "id":did,"version":str(a["version"]),"class":a["class"]})
    metadata=ET.SubElement(definition,q(OD,"metadata"))
    ET.SubElement(metadata,q(OD,"title")).text=a["assessment_title"]
    ET.SubElement(metadata,q(OD,"description")).text="Source-equivalent independent family Variable check."
    criteria=ET.SubElement(definition,q(OD,"criteria"),{"operator":"AND"})
    ET.SubElement(criteria,q(OD,"criterion"),{
        "comment":test["test_title"],"test_ref":tid})
    tests=ET.SubElement(root,q(OD,"tests"))
    xtest=ET.SubElement(tests,q(IND,"family_test"),{
        "id":tid,"version":str(a["version"]),"comment":test["test_title"],
        "check":"at least one","check_existence":"at_least_one_exists"})
    ET.SubElement(xtest,q(IND,"object"),{"object_ref":oid})
    ET.SubElement(xtest,q(IND,"state"),{"state_ref":sid})
    objects=ET.SubElement(root,q(OD,"objects"))
    ET.SubElement(objects,q(IND,"family_object"),{"id":oid,"version":"1"})
    states=ET.SubElement(root,q(OD,"states"))
    xs=ET.SubElement(states,q(IND,"family_state"),{"id":sid,"version":"1"})
    ET.SubElement(xs,q(IND,"family"),{
        "operation":"pattern match","var_check":"all","var_ref":vid})
    values=ET.SubElement(root,q(OD,"variables"))
    v=ET.SubElement(values,q(OD,"constant_variable"),{
        "id":vid,"version":"2","comment":variable["title"],"datatype":"string"})
    ET.SubElement(v,q(OD,"value")).text=variable["expression"]["literal"]
    return ET.ElementTree(root),did


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--native",type=Path,required=True)
    parser.add_argument("--oval-xml",type=Path,required=True)
    a=parser.parse_args()
    doc=json.loads(a.native.read_text())
    tree,_=export(doc)
    a.oval_xml.parent.mkdir(parents=True,exist_ok=True)
    tree.write(a.oval_xml,encoding="utf-8",xml_declaration=True)
    print("PASS: reverse-exported family OVAL Test/Object/State/Variable")


if __name__=="__main__":
    main()
