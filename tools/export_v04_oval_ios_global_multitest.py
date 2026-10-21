#!/usr/bin/env python3
"""Strict independent canonical SCAP-NG 0.4.0 -> OVAL 5.12.3 IOS/IOS-XE global exporter.

Independent of source OVAL, source-side importer, and provenance/ledger.
Supports exactly two or more state-free global Tests joined by an AND;
direct string/regex collection selectors, no State/Set/Filter/Variable.
A source-XSD+semantic comparator is a separate CI gate.
Refs #248 #229 #232; this does NOT redesign Cisco capabilities (#249).
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET

OD="http://oval.mitre.org/XMLSchema/oval-definitions-5"
OC="http://oval.mitre.org/XMLSchema/oval-common-5"
OPS={"equals":"equals","matches_regex":"pattern match"}
PLATFORMS={"ios.global":"ios","iosxe.global":"iosxe"}


def q(ns,local):
    return "{"+ns+"}"+local


def must(test,reason):
    if not test:
        raise ValueError("Unsupported canonical 0.4 OVAL global multi-Test export: "+reason)


def emit(document):
    assessment=document.get("assessment") if isinstance(document,dict) else None
    must(isinstance(assessment,dict),"not an Assessment")
    a=assessment
    must(set(a)=={"id","version","assessment_title","mode","class","purpose",
                 "specification","tests","evaluate"},"unexpected Assessment fields")
    must(a["mode"]=="automated" and a["purpose"]=="assessment" and
         a["class"]=="compliance" and type(a["version"]) is int,
         "not a source-trusted automated compliance Assessment")
    must(a["specification"]=={"id":"scap-ng.pre-alpha.assessment","version":"0.4.0"},
         "wrong version or specification")
    must(isinstance(a["assessment_title"],str) and a["assessment_title"].strip(),
         "missing human-readable source Test Content title")
    tests=a["tests"]
    must(isinstance(tests,dict) and 2<=len(tests)<=15,
         "multi-Test subset requires two or more Tests")
    caps={t.get("capability") for t in tests.values()}
    must(len(caps)==1 and next(iter(caps)) in PLATFORMS,
         "IOS/IOS-XE global only (no mixed capability)")
    platform=PLATFORMS[next(iter(caps))]
    expression=a["evaluate"]
    must(isinstance(expression,dict) and set(expression)=={"and"} and
         isinstance(expression["and"],list) and
         len(expression["and"])==len(tests),"only complete Test-result AND")
    sequence=[]
    for branch in expression["and"]:
        must(isinstance(branch,dict) and set(branch)=={"test"} and
             branch["test"] in tests and branch["test"] not in sequence,
             "not an exact, unique Test reference")
        sequence.append(branch["test"])
    for prefix,uri in (("oval-def",OD),("oval",OC),("cisco-def",OD+"#"+platform)):
        ET.register_namespace(prefix,uri)
    root=ET.Element(q(OD,"oval_definitions"))
    generator=ET.SubElement(root,q(OD,"generator"))
    ET.SubElement(generator,q(OC,"product_name")).text="SCAP-NG 0.4 IOS global semantic round-trip exporter"
    ET.SubElement(generator,q(OC,"schema_version")).text="5.12.3"
    ET.SubElement(generator,q(OC,"timestamp")).text="2026-10-21T00:00:00Z"
    ident="oval:scap-ng.v04.oval.multitest."+platform+":"
    definition_id=ident+"def:1"
    defs=ET.SubElement(root,q(OD,"definitions"))
    definition=ET.SubElement(defs,q(OD,"definition"),{
        "id":definition_id,"version":str(a["version"]),"class":a["class"]})
    metadata=ET.SubElement(definition,q(OD,"metadata"))
    ET.SubElement(metadata,q(OD,"title")).text=a["assessment_title"]
    ET.SubElement(metadata,q(OD,"description")).text="Native SCAP-NG 0.4 global collection Test round-trip"
    criteria=ET.SubElement(definition,q(OD,"criteria"))
    xtests=ET.SubElement(root,q(OD,"tests"))
    xobjs=ET.SubElement(root,q(OD,"objects"))
    for index,name in enumerate(sequence,1):
        t=tests[name]
        must(set(t)=={"test_title","capability","object","reported_elements","require"},
             "unexpected fields in Test")
        must(t["capability"] in PLATFORMS and PLATFORMS[t["capability"]]==platform,
             "capability drift")
        must(t["reported_elements"]=="all" and t["require"]=={"items":"one_or_more"},
             "unsupported Test cardinality or Item matching")
        must(isinstance(t["test_title"],str) and t["test_title"].strip(),
             "Test documentation missing")
        ob=t["object"]
        must(isinstance(ob,dict) and set(ob) in ({"global_command"},
             {"global_command","object_title"}),
             "only direct flat global_command selector")
        if "object_title" in ob:
            must(ob["object_title"] is None or isinstance(ob["object_title"],str),
                 "Object title malformed")
        command=ob["global_command"]
        must(isinstance(command,dict) and len(command)==1 and
             next(iter(command)) in OPS and
             isinstance(next(iter(command.values())),str),
             "direct string equality/regex selector only")
        operator,value=next(iter(command.items()))
        must(bool(value.strip()),"blank IOS command")
        test_id=ident+"tst:"+str(index)
        obj_id=ident+"obj:"+str(index)
        ET.SubElement(criteria,q(OD,"criterion"),{"test_ref":test_id})
        xtest=ET.SubElement(xtests,q(OD+"#"+platform,"global_test"),{
            "id":test_id,"version":str(a["version"]),
            "comment":t["test_title"],"check":"all",
            "check_existence":"at_least_one_exists"
        })
        ET.SubElement(xtest,q(OD+"#"+platform,"object"),{"object_ref":obj_id})
        obj_attrs={"id":obj_id,"version":str(a["version"])}
        if ob.get("object_title"):
            obj_attrs["comment"]=ob["object_title"]
        xobj=ET.SubElement(xobjs,q(OD+"#"+platform,"global_object"),obj_attrs)
        attrs={} if operator=="equals" else {"operation":OPS[operator]}
        ET.SubElement(xobj,q(OD+"#"+platform,"global_command"),attrs).text=value
    return ET.ElementTree(root),definition_id


def main():
    arg=argparse.ArgumentParser(description=__doc__)
    arg.add_argument("--native",type=Path,required=True)
    arg.add_argument("--output",type=Path,required=True)
    arg.add_argument("--report",type=Path,required=True)
    a=arg.parse_args()
    source=json.loads(a.native.read_text(encoding="utf-8"))
    xml,did=emit(source)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    xml.write(a.output,encoding="utf-8",xml_declaration=True)
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps({
        "source":"canonical SCAP-NG 0.4 only, independent of original OVAL",
        "native_assessment":str(a.native),
        "exported_oval_xml":str(a.output),
        "regenerated_definition_id":did,
        "original_source_consulted":False,
        "scanner_runtime_parity_proven":False
    },indent=2)+"\n",encoding="utf-8")


if __name__=="__main__":
    main()
