#!/usr/bin/env python3
"""Extract original Bluetooth OVAL closure from a SHA-pinned Win11 SCAP ZIP.

This is a SOURCE-SIDE test fixture extractor only. The OVAL exporter is
independent and takes exclusively the generated SCAP-NG 0.4.0 Assessment.
Refs #248 #229.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

OD="http://oval.mitre.org/XMLSchema/oval-definitions-5"
SOURCE_ZIP_GIT_BLOB="712cc3176b1e44616aaf2f3ba5e62b299ad0643c"
SOURCE_CMD="(Get-PnpDevice -class bluetooth -status OK).class"
SOURCE_TEST="oval:navy.navwar.niwcatlantic.scc.windows:tst:101"
SOURCE_OBJ="oval:navy.navwar.niwcatlantic.scc.windows:obj:101"
SOURCE_STATE="oval:navy.navwar.niwcatlantic.scc.windows:ste:101"


def local(tag):
    return tag.rsplit("}",1)[-1]


def extract(archive_bytes):
    blob=hashlib.sha1(b"blob "+str(len(archive_bytes)).encode()+b"\0"+archive_bytes).hexdigest()
    if blob!=SOURCE_ZIP_GIT_BLOB:
        raise ValueError("Original pinned Win11 SCAP ZIP source bytes changed")
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as z:
        items=[name for name in z.namelist() if name.endswith(".xml")]
        if len(items)!=1:
            raise ValueError("Ambiguous XML members in original SCAP archive")
        payload=z.read(items[0])
    stream=ET.fromstring(payload)
    roots=[node for node in stream.iter() if node.tag=="{"+OD+"}oval_definitions"]
    matches=[]
    for root in roots:
        ids={e.get("id"):e for e in root.iter() if e.get("id")}
        if SOURCE_TEST not in ids:
            continue
        test=ids[SOURCE_TEST]
        obj=ids.get(SOURCE_OBJ)
        state=ids.get(SOURCE_STATE)
        if obj is None or state is None:
            raise ValueError("Original Bluetooth Test Object/Filter State missing")
        if not any(node.get("object_ref")==SOURCE_OBJ for node in test.iter()):
            raise ValueError("Original Bluetooth Test no longer refers to pinned Object")
        direct_filter=[node for node in obj if local(node.tag)=="filter"]
        original_sets=[node for node in obj.iter() if local(node.tag)=="set"]
        command=[node.text for node in obj.iter() if local(node.tag)=="command"]
        if (len(direct_filter)!=1 or direct_filter[0].get("action")!="include"
            or (direct_filter[0].text or "").strip()!=SOURCE_STATE
            or original_sets or command!=[SOURCE_CMD]):
            raise ValueError("Original Bluetooth direct Filter/Set/command graph changed")
        defs=[d for d in root.iter()
              if d.tag=="{"+OD+"}definition"
              and any(c.get("test_ref")==SOURCE_TEST for c in d.iter())]
        if not defs:
            raise ValueError("No original OVAL Definition directly refers to Bluetooth Test")
        exact=[d for d in defs if any(local(e.tag)=="title" and "bluetooth" in (e.text or "").lower()
                                      for e in d.iter())]
        if len(exact)==1:
            selected=exact[0]
        elif len(defs)==1:
            selected=defs[0]
        else:
            raise ValueError("Ambiguous original Bluetooth Definition: "+
                             repr([d.get("id") for d in defs]))
        matches.append((root,selected))
    if len(matches)!=1:
        raise ValueError("Expected one distinct OVAL component containing Bluetooth Test")
    root,definition=matches[0]
    # Only a copy of source XML is used as the comparator's source graph;
    # it is NEVER handed to the independent 0.4.0 exporter.
    return ET.ElementTree(root),{
        "source_definition":definition.get("id"),
        "source_test":SOURCE_TEST,
        "source_object":SOURCE_OBJ,
        "source_state":SOURCE_STATE,
        "source_xml_sha256":hashlib.sha256(payload).hexdigest(),
        "source_archive_sha256":hashlib.sha256(archive_bytes).hexdigest(),
        "source_original_set_count":0,
        "source_filter_actions":["include"],
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source-zip",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--proof",type=Path,required=True)
    a=p.parse_args()
    tree,proof=extract(a.source_zip.read_bytes())
    a.output.parent.mkdir(exist_ok=True,parents=True)
    tree.write(a.output,encoding="utf-8",xml_declaration=True)
    proof["extracted_oval_component_sha256"]=hashlib.sha256(a.output.read_bytes()).hexdigest()
    a.proof.write_text(json.dumps(proof,indent=2)+"\n")
    print(json.dumps(proof,indent=2))


if __name__=="__main__":
    main()
