#!/usr/bin/env python3
"""Independent, strict SCAP-NG 0.4 Windows registry -> OVAL 5.12.3 pilot.

Reads only the authored NG Assessment. It does not consult source OVAL XML,
provenance, prior source AST or an earlier v003 exporter. Supports one simple
registry Test with one string equality State, no Sets/Variables. Anything
outside this proven subset MUST hard fail. Refs #248 #229.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import xml.etree.ElementTree as ET

OD="http://oval.mitre.org/XMLSchema/oval-definitions-5"
OC="http://oval.mitre.org/XMLSchema/oval-common-5"
WIN=OD+"#windows"
for prefix,ns in (("oval-def",OD),("oval",OC),("win-def",WIN)):
    ET.register_namespace(prefix,ns)


def q(ns,name):
    return "{"+ns+"}"+name


def need(ok,desc):
    if not ok:
        raise ValueError("Unsupported 0.4 Windows registry OVAL export: "+desc)


def emit(document):
    a=document.get("assessment") if isinstance(document,dict) else None
    need(isinstance(a,dict) and a.get("mode")=="automated",
         "automated Assessment missing")
    spec=a.get("specification") or {}
    need(spec.get("version")=="0.4.0","native 0.4.0 source is required")
    need(a.get("class")=="compliance" and type(a.get("version")) is int,
         "compliance Definition class and version required")
    need(set(a) <= {"id","version","assessment_title","mode","class","purpose",
                   "specification","tests","evaluate"},"unexpected Assessment fields")
    tests=a.get("tests") or {}
    need(isinstance(tests,dict) and len(tests)==1,"single registry Test pilot")
    test_id,t=next(iter(tests.items()))
    need(a.get("evaluate")=={"test":test_id},"single criterion")
    need(t.get("capability")=="windows.registry","not a windows.registry Test")
    need(set(t)=={"test_title","capability","object","states",
                  "reported_elements","require"},"unexpected registry Test fields")
    need(t["reported_elements"]=="all","unexpected reported_elements")
    need(t["require"]=="at_least_one_exists_and_only_one_matches",
         "unexpected OVAL Test check/existence")
    need(isinstance(t.get("test_title"),str) and t["test_title"].strip(),
         "OVAL requires original human Test comment")
    ob=t["object"]
    need(isinstance(ob,dict) and set(ob)=={"select","object_title"},
         "only a direct registry Object selector (no Set/Filter)")
    select=ob["select"]
    need(isinstance(select,dict) and set(select)=={"hive","key","name"},
         "original ordered hive/key/name selector required")
    fields={}
    for name in ("hive","key","name"):
        field=select[name]
        need(isinstance(field,dict) and set(field)=={"equals"}
             and isinstance(field["equals"],str),
             "non-literal registry selector "+name)
        fields[name]=field["equals"]
    need(fields["hive"]=="local_machine","only HKEY_LOCAL_MACHINE in pilot")
    need(bool(fields["key"] and fields["name"]),"empty registry key or name")
    states=t["states"]
    need(isinstance(states,list) and len(states)==1,"one State in pilot")
    state=states[0]
    need(isinstance(state,dict) and set(state)=={"value"},
         "only one direct value predicate")
    predicate=state["value"]
    need(isinstance(predicate,dict) and set(predicate)=={"require","equals"}
         and predicate["require"]=="at_least_one_exists_and_all_match"
         and isinstance(predicate["equals"],str),
         "original string-valued equality predicate required")
    ids={kind:f"oval:scap-ng.v04.registry.pilot:{kind}:1"
         for kind in ("def","tst","obj","ste")}

    root=ET.Element(q(OD,"oval_definitions"))
    g=ET.SubElement(root,q(OD,"generator"))
    ET.SubElement(g,q(OC,"product_name")).text="SCAP-NG 0.4 independent registry pilot exporter"
    ET.SubElement(g,q(OC,"schema_version")).text="5.12.3"
    ET.SubElement(g,q(OC,"timestamp")).text="2026-10-20T00:00:00Z"

    d=ET.SubElement(ET.SubElement(root,q(OD,"definitions")),q(OD,"definition"),
        {"id":ids["def"],"version":str(a["version"]),"class":a["class"]})
    metadata=ET.SubElement(d,q(OD,"metadata"))
    ET.SubElement(metadata,q(OD,"title")).text=a.get("assessment_title") or a["id"]
    ET.SubElement(metadata,q(OD,"description")).text="Native 0.4.0 Windows registry Test exporter"
    ET.SubElement(ET.SubElement(d,q(OD,"criteria")),q(OD,"criterion"),
                  {"test_ref":ids["tst"]})

    oval_test=ET.SubElement(ET.SubElement(root,q(OD,"tests")),q(WIN,"registry_test"),{
        "id":ids["tst"],"version":str(a["version"]),"comment":t["test_title"],
        "check_existence":"at_least_one_exists","check":"only one"})
    ET.SubElement(oval_test,q(WIN,"object"),{"object_ref":ids["obj"]})
    ET.SubElement(oval_test,q(WIN,"state"),{"state_ref":ids["ste"]})

    attrs={"id":ids["obj"],"version":str(a["version"])}
    if ob["object_title"] is not None:
        need(isinstance(ob["object_title"],str),"invalid Object title")
        attrs["comment"]=ob["object_title"]
    obj=ET.SubElement(ET.SubElement(root,q(OD,"objects")),q(WIN,"registry_object"),attrs)
    for name in ("hive","key","name"):
        value="HKEY_LOCAL_MACHINE" if name=="hive" else fields[name]
        ET.SubElement(obj,q(WIN,name)).text=value

    st=ET.SubElement(ET.SubElement(root,q(OD,"states")),q(WIN,"registry_state"),{
        "id":ids["ste"],"version":str(a["version"])})
    ET.SubElement(st,q(WIN,"value"),{"operation":"equals"}).text=predicate["equals"]
    return ET.ElementTree(root),ids["def"]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--native",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--definition-id-output",type=Path)
    a=p.parse_args()
    tree,ident=emit(json.loads(a.native.read_text()))
    ET.indent(tree)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    tree.write(a.output,encoding="utf-8",xml_declaration=True)
    if a.definition_id_output:
        a.definition_id_output.write_text(ident+"\n")
    print(json.dumps({"status":"EMITTED_STRICT_REGISTRY_PILOT_NOT_FULL_COVERAGE",
                      "definition":ident}))


if __name__=="__main__":
    main()
