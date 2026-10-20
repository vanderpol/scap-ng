#!/usr/bin/env python3
"""Fault-inject all four real original-OVAL 0.4 roundtrip cases.

Change one emitted OVAL semantic field at a time (without touching original
source, native Assessment, or the other three exported files) and recompute
the changed output's SHA. A meaningful semantic comparator MUST report a
different reachable Definition each time. This is not runtime scanner parity.
Refs #248 #229.
"""
from __future__ import annotations

from copy import deepcopy
import argparse,hashlib,json
from pathlib import Path
import xml.etree.ElementTree as ET

from audit_v04_oval_xml_roundtrip import audit,FORMAT

OD="http://oval.mitre.org/XMLSchema/oval-definitions-5"
IND=OD+"#independent"
WIN=OD+"#windows"


def mutate(root,case):
    if "bluetooth" in case.lower():
        fil=next(root.iter("{"+OD+"}filter"),None)
        if fil is None or fil.get("action")!="include":
            raise ValueError("Original-source Bluetooth Filter is not available")
        fil.set("action","exclude")
        return "reversed_filter_action"
    if "camera" in case.lower():
        e=next(root.iter("{"+IND+"}stdout_line"),None)
        if e is None or e.text!="Camera":
            raise ValueError("Original-source Camera observed predicate not available")
        e.text="NotCamera"
        return "changed_filter_state_value"
    if "SV-253291" in case:
        e=next(root.iter("{"+WIN+"}value"),None)
        if e is None or e.text!="0":
            raise ValueError("Expected original registry State value 0")
        e.text="1"
        return "changed_registry_state_value"
    if "SV-253350" in case:
        e=next(root.iter("{"+WIN+"}hive"),None)
        if e is None or e.text!="HKEY_LOCAL_MACHINE":
            raise ValueError("Expected original registry hive selector")
        e.text="HKEY_USERS"
        return "changed_registry_selector"
    raise ValueError("Unrecognized source-bound roundtrip case: "+case)


def verify(root,manifest):
    if manifest.get("format")!=FORMAT or len(manifest.get("cases") or [])!=4:
        raise ValueError("Four original-v0.4 pinned cases required")
    clean=audit(manifest,root,expected=4)
    if clean["status"]!="PASS":
        raise ValueError("Original unmutated roundtrip cases did not all pass")
    outcomes=[]
    directory=root/"mutated-oval"
    directory.mkdir(exist_ok=True)
    for i,row in enumerate(manifest["cases"]):
        candidate=deepcopy(manifest)
        emitted=root/row["regenerated"]
        tree=ET.parse(emitted)
        why=mutate(tree.getroot(),row["case_id"])
        altered=directory/("altered-"+str(i)+".xml")
        tree.write(altered,encoding="utf-8",xml_declaration=True)
        rec=candidate["cases"][i]
        rec["regenerated"]=str(altered.relative_to(root))
        rec["regenerated_sha256"]=hashlib.sha256(altered.read_bytes()).hexdigest()
        result=audit(candidate,root,expected=4)
        changes=[x for x in result["cases"] if x["status"]!="EQUAL"]
        if (result["status"]!="FAIL" or len(changes)!=1 or
                changes[0]["case_id"]!=row["case_id"] or
                changes[0]["status"]!="DIFFERENT"):
            raise ValueError("Semantic fault injection escaped OVAL comparator: "+why)
        outcomes.append({"case_id":row["case_id"],"injected_change":why,
                         "classification":"EXPECTED_DIFFERENT"})
    return {"status":"PASS_EXPECTED_ALL_FOUR_MUTANTS_REJECTED",
            "source_cases":len(manifest["cases"]),
            "mutations":outcomes,"scanner_runtime_tested":False}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root",type=Path,required=True)
    p.add_argument("--manifest",type=Path,required=True)
    p.add_argument("--report",type=Path,required=True)
    a=p.parse_args()
    result=verify(a.root,json.loads(a.manifest.read_text()))
    a.report.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))


if __name__=="__main__":
    main()
