#!/usr/bin/env python3
"""#237: registry-selector original OVAL 5.12.3 vs converted Assessment audit.

Windows Server 2025 SV-278138 real original XML and historically converted
SCAP-NG 0.1 source, not a scanner or source-equivalent collection proof.
In particular a missing registry behaviors element is NOT a 64-bit guess.
"""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import yaml

ROOT=Path(__file__).resolve().parents[1]
XML=ROOT/("research/assessment-simplification/evidence/"
          "ms_windows_server_2025/SV-278138/source-oval.xml")
CONVERTED=ROOT/("research/assessment-simplification/samples/"
           "ms_windows_server_2025/assessments/automated/"
           "niwc.ms_windows_server_2025.SV-278138.automated.assessment.yaml")
NS="http://oval.mitre.org/XMLSchema/oval-definitions-5#windows"


def compare(original_xml,converted):
    root=ET.fromstring(original_xml)
    a=converted.get("assessment")
    if not isinstance(a,dict) or not a.get("id","").endswith("SV-278138.automated"):
        raise ValueError("converted source Assessment identity not SV-278138")
    objects=a.get("objects")
    if not isinstance(objects,dict):raise ValueError("missing converted source Object table")
    original=root.findall(".//{"+NS+"}registry_object")
    # Two file-path sources plus the DSA Working Directory source: the
    # pinned original XML contains three distinct registry collections.
    # Preserve the complete source set rather than silently ignoring one.
    if len(original)!=3:
        raise ValueError("expected exactly three original registry path discovery Objects")
    checked=[]
    for obj in original:
        comment=obj.get("comment")
        children={}
        for name in ("hive","key","name"):
            element=obj.find("{"+NS+"}"+name)
            if element is None or element.text is None:
                raise ValueError("original registry selector missing "+name)
            children[name]={
                "value":element.text,
                "operation":element.get("operation","equals"),
                "datatype":element.get("datatype","string"),
            }
        # This source XML does not declare registry behaviors. That is a
        # separate default-view semantics question under OVAL 5.12.3.
        behaviors=obj.find("{"+NS+"}behaviors")
        if behaviors is not None:
            raise ValueError("unexpected original registry behaviors/view present")
        found=[(key,val) for key,val in objects.items()
               if isinstance(val,dict) and val.get("capability")=="windows.registry"
               and val.get("object_title")==comment]
        if len(found)!=1:
            raise ValueError("original registry Object comment not uniquely mapped")
        converted_id,converted_obj=found[0]
        select=converted_obj.get("select")
        if not isinstance(select,dict) or set(select)!={"hive","key","name"}:
            raise ValueError("converted registry selector keys or view changed")
        for name in ("hive","key","name"):
            entity=select[name]
            if not isinstance(entity,dict):
                raise ValueError("converted registry entity shape invalid: "+name)
            original_sel=children[name]
            if (entity.get("operation")!=original_sel["operation"] or
                entity.get("datatype")!=original_sel["datatype"] or
                entity.get("value")!=original_sel["value"]):
                raise ValueError("source registry selector semantics lost: "+name)
        if children["key"]["operation"]!="case insensitive equals" or (
            children["name"]["operation"]!="case insensitive equals"):
            raise ValueError("source case-insensitive registry selector not preserved")
        checked.append({
            "original_object_id":obj.get("id"),
            "converted_object_id":converted_id,
            "original_key_selector":children["key"],
            "original_value_name_selector":children["name"],
            "original_registry_behaviors_declared":False,
            "view_default_source_parity_verified":False,
            "selector_source_parity_for_checked_fields":True,
        })
    return {
        "format":"scap-ng-b-windows-registry-original-oval-crosswalk/0.1",
        "source_rule":"SV-278138",
        "original_xml_sha256":sha256(original_xml).hexdigest(),
        "source_registries":len(original),
        "converted_registries_checked":len(checked),
        "case_insensitive_selectors_required":True,
        "source_registry_view_default_verified":False,
        "scanner_execution_verified":False,
        "converted_source_generation":"0.1 historical research, not B",
        "registry_objects":checked,
    }


def main():
    result=compare(XML.read_bytes(),yaml.safe_load(CONVERTED.read_text()))
    path=ROOT/("research/requirements-first-language/contract-candidate/corpus/"
               "windows-registry-original-crosswalk.json")
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"registry_objects":len(result["registry_objects"]),
                      "view_default_parity":False,"scanner_executable":False}))


if __name__=="__main__":
    main()
