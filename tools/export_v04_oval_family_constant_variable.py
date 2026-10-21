#!/usr/bin/env python3
"""Independent canonical 0.4 independent.family constant-Variable OVAL exporter.

Reads ONLY authored 0.4.0 Assessment. No original OVAL XML, importer,
or source/provenance crosswalk is accepted by the exporter.
One family_state matches_regex Variable with var_check=all;
one constant literal Variable; one family singleton source.
Refs #248 #229 #232.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from convert_v04_oval_family_constant_variable import (
    BASE, INDEPENDENT, OVAL_COMMON, NAME, TEST_NAME, q
)

def require(yes,reason):
    if not yes:
        raise ValueError("Unsupported 0.4 independent.family OVAL export: "+reason)

def emit(doc):
    a=doc.get("assessment")
    require(isinstance(a,dict),"assessment required")
    require(set(a)=={"id","version","assessment_title","mode","class","purpose",
                    "specification","variables","tests","evaluate"},
            "unreviewed Assessment keys")
    require(a["specification"]=={"id":"scap-ng.pre-alpha.assessment","version":"0.4.0"},
            "version mismatch")
    require(a["mode"]=="automated" and a["class"]=="miscellaneous" and
            a["purpose"]=="assessment" and type(a["version"]) is int,
            "nonmatching family Definition class/mode/version")
    require(a["evaluate"]=={"test":TEST_NAME} and
            set(a["tests"])=={TEST_NAME} and set(a["variables"])=={NAME},
            "incomplete Test/Variable closure")
    variable=a["variables"][NAME]
    require(set(variable)=={"kind","datatype","title","expression"} and
            variable["kind"]=="constant" and variable["datatype"]=="string" and
            set(variable["expression"])=={"literal"} and
            isinstance(variable["expression"]["literal"],str) and
            bool(variable["expression"]["literal"]),
            "nonliteral, nonconstant or multiple Variable values")
    test=a["tests"][TEST_NAME]
    require(set(test)=={"test_title","capability","states","reported_elements","require"}
            and test["capability"]=="independent.family" and
            test["reported_elements"]=="all" and
            test["require"]=="at_least_one_exists_and_some_match" and
            isinstance(test["test_title"],str),
            "unsupported Test cardinality or capability")
    require(len(test["states"])==1 and set(test["states"][0])=={"family"},
            "unsupported number/shape of family State fields")
    predicate=test["states"][0]["family"]
    require(predicate=={
        "matches_regex":{"variable":NAME},
        "datatype":"string",
        "value_match":"all",
        "require":"at_least_one_exists_and_all_match"
    },"state regex, variable matching and field scope changed")
    for prefix,namespace in (("oval-def",BASE),("oval",OVAL_COMMON),
                             ("ind-def",INDEPENDENT)):
        ET.register_namespace(prefix,namespace)
    root=ET.Element(q(BASE,"oval_definitions"))
    generator=ET.SubElement(root,q(BASE,"generator"))
    ET.SubElement(generator,q(OVAL_COMMON,"product_name")).text="SCAP-NG native 0.4 family Variable exporter"
    ET.SubElement(generator,q(OVAL_COMMON,"schema_version")).text="5.12.3"
    ET.SubElement(generator,q(OVAL_COMMON,"timestamp")).text="2026-10-21T00:00:00Z"
    prefix="oval:scap-ng.v04.family.variable:"
    defid=prefix+"def:1";tid=prefix+"tst:1"
    oid=prefix+"obj:1";sid=prefix+"ste:1";vid=prefix+"var:1"
    defs=ET.SubElement(root,q(BASE,"definitions"))
    d=ET.SubElement(defs,q(BASE,"definition"),{
        "id":defid,"version":str(a["version"]),"class":"miscellaneous"})
    meta=ET.SubElement(d,q(BASE,"metadata"))
    ET.SubElement(meta,q(BASE,"title")).text=a["assessment_title"]
    ET.SubElement(meta,q(BASE,"description")).text="System family equals a publisher supplied pattern"
    criteria=ET.SubElement(d,q(BASE,"criteria"),{"operator":"AND"})
    ET.SubElement(criteria,q(BASE,"criterion"),{"test_ref":tid})
    tests=ET.SubElement(root,q(BASE,"tests"))
    family_test=ET.SubElement(tests,q(INDEPENDENT,"family_test"),{
        "id":tid,"version":str(a["version"]),"comment":test["test_title"],
        "check":"at least one","check_existence":"at_least_one_exists"
    })
    ET.SubElement(family_test,q(INDEPENDENT,"object"),{"object_ref":oid})
    ET.SubElement(family_test,q(INDEPENDENT,"state"),{"state_ref":sid})
    objs=ET.SubElement(root,q(BASE,"objects"))
    ET.SubElement(objs,q(INDEPENDENT,"family_object"),{"id":oid,"version":str(a["version"])})
    states=ET.SubElement(root,q(BASE,"states"))
    state=ET.SubElement(states,q(INDEPENDENT,"family_state"),{
        "id":sid,"version":str(a["version"])})
    ET.SubElement(state,q(INDEPENDENT,"family"),{
        "operation":"pattern match","var_check":"all","var_ref":vid})
    variables=ET.SubElement(root,q(BASE,"variables"))
    var=ET.SubElement(variables,q(BASE,"constant_variable"),{
        "id":vid,"version":str(a["version"]),"datatype":"string",
        "comment":variable["title"]
    })
    ET.SubElement(var,q(BASE,"value")).text=variable["expression"]["literal"]
    return ET.ElementTree(root),defid


def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--native",type=Path,required=True)
    cli.add_argument("--output",type=Path,required=True)
    args=cli.parse_args()
    authored=json.loads(args.native.read_text(encoding="utf-8"))
    tree,_=emit(authored)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    tree.write(args.output,xml_declaration=True,encoding="utf-8")

if __name__=="__main__":
    main()
