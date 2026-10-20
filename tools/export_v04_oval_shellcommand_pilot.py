#!/usr/bin/env python3
"""Minimal *independent* 0.4.0-native OVAL 5.12.3 emitter for a real pilot.

The exporter reads only its NG Assessment input, NEVER an original OVAL XML
source or saved source AST. This first slice intentionally supports a *single*
shellcommand Test, a direct-filtered leaf Object, and one simple predicate.
Unsupported assessments fail closed, rather than silently being counted as
roundtrip successes. Original OVAL->NG conversion for the six-STIG candidate
is covered by a separate source-pinned generation workflow. Refs #248 #229.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET

OD="http://oval.mitre.org/XMLSchema/oval-definitions-5"
OC="http://oval.mitre.org/XMLSchema/oval-common-5"
IND=OD+"#independent"
NS={"oval-def":OD, "oval":OC, "ind-def":IND}
for prefix,uri in NS.items():
    ET.register_namespace(prefix,uri)


def q(ns,name):
    return "{"+ns+"}"+name


def required(condition,why):
    if not condition:
        raise ValueError("Unsupported native 0.4 OVAL export: "+why)


def emit(doc):
    a=doc.get("assessment") if isinstance(doc,dict) else None
    required(isinstance(a,dict),"Assessment root missing")
    spec=a.get("specification") or {}
    required(spec.get("version")=="0.4.0","not official 0.4.0 authoring")
    required(a.get("mode")=="automated","manual source not executable OVAL")
    tests=a.get("tests") or {}
    required(isinstance(tests,dict) and len(tests)==1,"single-Test pilot only")
    test_id,test=next(iter(tests.items()))
    required(a.get("evaluate")=={"test":test_id},"single root criterion only")
    required(test.get("capability")=="independent.shellcommand",
             "only independent.shellcommand is supported in pilot")
    required(set(test) <= {"test_title","capability","object","reported_elements","require"},
             "unknown Test authoring attributes")
    required(test.get("reported_elements","all")=="all","reported_elements other than all")
    req=test.get("require")
    required(req=={"items":"one_or_more"},"Test existence or States outside pilot")
    obj=test.get("object")
    required(isinstance(obj,dict) and set(obj) <= {"object_title","collect","filters"}
             and "set" not in obj and "filters" in obj,
             "requires a direct-filtered leaf Object, not any Set")
    collect=obj.get("collect")
    required(isinstance(collect,dict) and set(collect) ==
             {"shell","command","error_if_exit_status_not_0","error_if_stderr_exists"},
             "unexpected shellcommand collector")
    required(collect.get("shell")=="powershell" and
             isinstance(collect.get("command"),str) and collect["command"],
             "unexpected shell or command")
    required(collect["error_if_exit_status_not_0"] is False and
             collect["error_if_stderr_exists"] is False,
             "non-default error collection behavior")
    filters=obj.get("filters")
    required(isinstance(filters,list) and len(filters)==1,
             "only a single direct filter in pilot")
    fil=filters[0]
    required(isinstance(fil,dict) and set(fil)=={"include"},"only include filter")
    fields=fil["include"]
    required(isinstance(fields,dict) and set(fields)=={"stdout_line"},
             "unsupported observed Item predicate field")
    predicate=fields["stdout_line"]
    required(isinstance(predicate,dict) and set(predicate)=={
             "require","case_insensitive_equals"},"unsupported predicate operator or quantifier")
    required(predicate["require"]=="at_least_one_exists_and_all_match",
             "unsupported predicate cardinality")
    required(isinstance(predicate["case_insensitive_equals"],str),
             "expected string Filter comparator")
    required(a.get("class")=="inventory" and isinstance(a.get("version"),int),
             "OVAL Definition class/version mismatch")
    required(set(a) <= {"id","version","assessment_title","mode","class",
                        "purpose","specification","tests","evaluate"},
             "unexpected Assessment attributes")

    ids={s:f"oval:scap-ng.v04.pilot:{s}:1" for s in ("def","tst","obj","ste")}
    root=ET.Element(q(OD,"oval_definitions"))
    generator=ET.SubElement(root,q(OD,"generator"))
    ET.SubElement(generator,q(OC,"product_name")).text="SCAP-NG 0.4.0 independent pilot exporter"
    ET.SubElement(generator,q(OC,"schema_version")).text="5.12.3"
    ET.SubElement(generator,q(OC,"timestamp")).text="2026-10-20T00:00:00Z"

    defs=ET.SubElement(root,q(OD,"definitions"))
    definition=ET.SubElement(defs,q(OD,"definition"),
        {"id":ids["def"],"version":str(a["version"]),"class":a["class"]})
    metadata=ET.SubElement(definition,q(OD,"metadata"))
    ET.SubElement(metadata,q(OD,"title")).text=a.get("assessment_title") or a.get("id")
    ET.SubElement(metadata,q(OD,"description")).text="SCAP-NG generated native OVAL-compatible test"
    criteria=ET.SubElement(definition,q(OD,"criteria"))
    ET.SubElement(criteria,q(OD,"criterion"),{"test_ref":ids["tst"]})

    all_tests=ET.SubElement(root,q(OD,"tests"))
    required(isinstance(test.get("test_title"),str) and test["test_title"].strip(),
             "OVAL 5.12.3 requires a nonempty Test comment from original Test title")
    oval_test=ET.SubElement(all_tests,q(IND,"shellcommand_test"),{
        "id":ids["tst"],"version":str(a["version"]),
        "comment":test["test_title"],
        "check_existence":"at_least_one_exists","check":"all"})
    ET.SubElement(oval_test,q(IND,"object"),{"object_ref":ids["obj"]})

    all_objects=ET.SubElement(root,q(OD,"objects"))
    oval_obj=ET.SubElement(all_objects,q(IND,"shellcommand_object"),
                          {"id":ids["obj"],"version":str(a["version"])})
    ET.SubElement(oval_obj,q(IND,"shell")).text=collect["shell"]
    ET.SubElement(oval_obj,q(IND,"command")).text=collect["command"]
    ET.SubElement(oval_obj,q(OD,"filter"),{"action":"include"}).text=ids["ste"]

    all_states=ET.SubElement(root,q(OD,"states"))
    state=ET.SubElement(all_states,q(IND,"shellcommand_state"),
                        {"id":ids["ste"],"version":str(a["version"])})
    ET.SubElement(state,q(IND,"stdout_line"),
                  {"operation":"case insensitive equals"}).text=predicate["case_insensitive_equals"]
    return ET.ElementTree(root),ids["def"]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--native",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--definition-id-output",type=Path)
    a=p.parse_args()
    doc=json.loads(a.native.read_text())
    tree,root=emit(doc)
    ET.indent(tree)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    tree.write(a.output,encoding="utf-8",xml_declaration=True)
    if a.definition_id_output:
        a.definition_id_output.write_text(root+"\n")
    print(json.dumps({"status":"EMITTED_PILOT_NOT_FULL_LANGUAGE_COVERAGE",
                     "native_profile":"0.4.0","root_definition":root,
                     "output":str(a.output)}))


if __name__=="__main__":
    main()
