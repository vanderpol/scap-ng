#!/usr/bin/env python3
"""Strict, source-independent OVAL 5.12.3 -> SCAP-NG 0.4.0 leaf importer.

This is the FIRST native 0.4.0 XML ingest pilot, distinct from both the
published six-STIG converter and the independent native->OVAL exporter.
It emits actual NG 0.4.0 JSON from pinned ORIGINAL OVAL XML, without reading
the published 0.4.0 candidate or source-lowering/provenance ledgers.

Supported only:
 - one direct independent.shellcommand Test/Object/include Filter State
 - one direct windows.registry Test/Object/State equality
Anything else MUST produce an explicit error (not "compatible" output).
This is a focused importer subset, not OVAL language conformance.
Refs #248 #229.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

OD="http://oval.mitre.org/XMLSchema/oval-definitions-5"
IND=OD+"#independent"
WIN=OD+"#windows"


def q(ns,name):
    return "{"+ns+"}"+name

def child_name(el):
    return el.tag.rsplit("}",1)[-1]

def need(test,msg):
    if not test:
        raise ValueError("Original OVAL source is outside approved native 0.4 importer subset: "+msg)

def find_id(root,ident):
    nodes=[n for n in root.iter() if n.get("id")==ident]
    need(len(nodes)==1,"missing or duplicated OVAL ID "+str(ident))
    return nodes[0]

def slug(value):
    label=re.sub(r"[^a-z0-9]+","-",value.lower()).strip("-")
    need(bool(label),"empty Test title")
    return label[:90].rstrip("-")+"-test"

def only(node,tag=None):
    nodes=list(node)
    need(len(nodes)==1 and (tag is None or child_name(nodes[0])==tag),
         "expected one "+str(tag)+" child at "+child_name(node))
    return nodes[0]

def plain(node):
    need(not list(node),"source leaf cannot contain nested entities/Variable references")
    need(node.get("var_ref") is None,"source Variable reference not in pilot")
    return node.text or ""

def convert(source_xml,source_definition_id,*,assessment_id=None):
    root=ET.fromstring(source_xml)
    need(root.tag==q(OD,"oval_definitions"),"expected OVAL Definitions XML")
    definition=find_id(root,source_definition_id)
    need(definition.tag==q(OD,"definition"),"source is not an OVAL Definition")
    need(definition.get("version") and definition.get("class") in ("compliance","inventory"),
         "source Definition version/class unhandled")
    need(definition.get("deprecated","false")=="false","deprecated OVAL Definition")
    version=int(definition.get("version"))
    metadata=definition.find(q(OD,"metadata"))
    title_node=metadata.find(q(OD,"title")) if metadata is not None else None
    need(title_node is not None and (title_node.text or "").strip(),
         "source Definition title missing")
    criteria=definition.find(q(OD,"criteria"))
    need(criteria is not None and not criteria.attrib,
         "only unmodified OVAL single criterion is supported")
    criterion=only(criteria,"criterion")
    need(set(criterion.attrib) <= {"test_ref","comment"},"unknown criterion evaluation flags")
    test=find_id(root,criterion.get("test_ref"))
    kind=child_name(test)
    need(kind in ("shellcommand_test","registry_test"),
         "capability not implemented by 0.4 importer: "+kind)
    need(test.get("version")==str(version),"OVAL Test version differs from its Definition")
    need(test.get("check_existence","at_least_one_exists")=="at_least_one_exists",
         "unsupported existence boundary")
    need(set(test.attrib) <= {"id","version","comment","check_existence","check"},
         "unexpected original Test attributes")
    comment=test.get("comment")
    need(isinstance(comment,str) and comment.strip(),
         "source OVAL Test comment required")
    cap="independent.shellcommand" if kind=="shellcommand_test" else "windows.registry"
    expect_children=["object"] if kind=="shellcommand_test" else ["object","state"]
    refs=list(test)
    need([child_name(n) for n in refs]==expect_children,
         "source Test's Object/State cardinality or order changed")
    ob=find_id(root,refs[0].get("object_ref"))
    need(ob.tag==q(IND if kind=="shellcommand_test" else WIN,
                   "shellcommand_object" if kind=="shellcommand_test" else "registry_object"),
         "Test/Object capability mismatch")
    need(ob.get("version")==str(version)
         and set(ob.attrib) <= {"id","version","comment"},
         "original Object version or attributes unhandled")
    object_title=ob.get("comment")
    need(isinstance(object_title,str) and object_title.strip(),
         "original Object title/comment required")
    need(not any(child_name(n)=="set" for n in ob.iter()),
         "original OVAL Set requires real Set representation; not a leaf")
    ns=IND if kind=="shellcommand_test" else WIN
    if kind=="shellcommand_test":
        need(test.get("check")=="all","shell Test matching not all")
        nodes=list(ob)
        need([child_name(n) for n in nodes]==["shell","command","filter"],
             "direct shell collection+Filter graph not recognized")
        sh,cmd,flt=nodes
        need(sh.tag==q(IND,"shell") and cmd.tag==q(IND,"command")
             and not sh.attrib and not cmd.attrib,
             "shell selector not a literal source")
        need(plain(sh)=="powershell" and plain(cmd),
             "unsupported shell or empty command")
        need(flt.tag==q(OD,"filter") and set(flt.attrib)=={"action"}
             and flt.get("action")=="include",
             "unsupported direct original OVAL Filter action")
        st=find_id(root,plain(flt).strip())
        need(st.tag==q(IND,"shellcommand_state") and st.get("version")==str(version)
             and set(st.attrib) <= {"id","version","comment"},
             "original Filter State capability/version/attributes mismatch")
        statefield=only(st,"stdout_line")
        need(statefield.tag==q(IND,"stdout_line")
             and set(statefield.attrib) <= {"operation","datatype"}
             and statefield.get("operation","equals")=="case insensitive equals"
             and statefield.get("datatype","string")=="string",
             "unsupported State predicate/datatype in Filter")
        test_payload={
            "test_title":comment,"capability":cap,
            "object":{"object_title":object_title,
                "collect":{"shell":plain(sh),"command":plain(cmd),
                           "error_if_exit_status_not_0":False,
                           "error_if_stderr_exists":False},
                "filters":[{"include":{"stdout_line":{
                    "require":"at_least_one_exists_and_all_match",
                    "case_insensitive_equals":plain(statefield)}}}]},
            "reported_elements":"all",
            "require":{"items":"one_or_more"},
        }
    else:
        need(test.get("check")=="only one","unsupported registry Test match")
        nodes=list(ob)
        need([child_name(n) for n in nodes]==["hive","key","name"]
             and all(not n.attrib for n in nodes),
             "registry Object selector not simple literal hive/key/name")
        hive,key,name=[plain(n) for n in nodes]
        need(hive=="HKEY_LOCAL_MACHINE" and bool(key and name),
             "unexpected original registry hive/key/name")
        st=find_id(root,refs[1].get("state_ref"))
        need(st.tag==q(WIN,"registry_state") and st.get("version")==str(version)
             and set(st.attrib) <= {"id","version","comment"},
             "original registry State capability/version/attributes differ")
        statefield=only(st,"value")
        need(statefield.tag==q(WIN,"value")
             and set(statefield.attrib) <= {"operation","datatype"}
             and statefield.get("operation","equals")=="equals"
             and statefield.get("datatype","string")=="string",
             "registry State value is not simple string equals")
        test_payload={
            "test_title":comment,"capability":cap,
            "object":{"object_title":object_title,
                "select":{"hive":{"equals":"local_machine"},
                          "key":{"equals":key},"name":{"equals":name}}},
            "states":[{"value":{
                "require":"at_least_one_exists_and_all_match",
                "equals":plain(statefield)}}],
            "reported_elements":"all",
            "require":"at_least_one_exists_and_only_one_matches",
        }
    test_id=slug(comment)
    ident=assessment_id or re.sub(r"[^a-z0-9]+","-",source_definition_id.lower()).strip("-")+".assessment"
    assessment={
        "id":ident,
        "version":version,
        "assessment_title":title_node.text.strip(),
        "mode":"automated",
        "class":definition.get("class"),
        "purpose":"applicability" if definition.get("class")=="inventory" else "assessment",
        "specification":{"id":"scap-ng.pre-alpha.assessment","version":"0.4.0"},
        "tests":{test_id:test_payload},
        "evaluate":{"test":test_id},
    }
    return {"assessment":assessment}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source-xml",type=Path,required=True)
    p.add_argument("--definition-id",required=True)
    p.add_argument("--assessment-id")
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    doc=convert(args.source_xml.read_bytes(),args.definition_id,
                assessment_id=args.assessment_id)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(doc,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":"CONVERTED_STRICT_040_LEAF_SUBSET_NOT_LANGUAGE_COVERAGE",
                      "assessment_id":doc["assessment"]["id"],
                      "capability":next(iter(doc["assessment"]["tests"].values()))["capability"],
                      "source_definition":args.definition_id}))


if __name__=="__main__":
    main()
