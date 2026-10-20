#!/usr/bin/env python3
"""Check 0.4.0 candidate filtered-Unions against six exact source OVAL ZIPs.

No rewriting: filter-order, action, original Object identity and whether the
source actually contained a Set are recorded separately. Names alone are never
accepted as full semantic equivalence. Refs #229 #232.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

PINS = {
    "apache_server_2-4_unix_server": (
        "U_Apache_Server_2-4_UNIX_Server_V3R2_STIG_SCAP_1-4_Benchmark-enhancedV2-signed.zip",
        "01b08ac54811cc190c4b677f9cf3d26613e3a4b7"),
    "ms_windows_11": (
        "U_MS_Windows_11_V2R10_STIG_SCAP_1-4_Benchmark-enhancedV18-signed.zip",
        "712cc3176b1e44616aaf2f3ba5e62b299ad0643c"),
    "ms_windows_server_2025": (
        "U_MS_Windows_Server_2025_V1R1_STIG_SCAP_1-4_Benchmark-enhancedV1-signed.zip",
        "f6ba90413cd8a6ab3f9f5acc82603d9b52aca9cf"),
    "ms_windows_server_dns": (
        "U_MS_Windows_Server_DNS_V2R3_STIG_SCAP_1-4_Benchmark-enhancedV8-signed.zip",
        "eca2b802a66f5ba103bd180db5f7ec8279e00709"),
    "oracle_linux_9": (
        "U_Oracle_Linux_9_V1R4_STIG_SCAP_1-4_Benchmark-enhancedV5-signed.zip",
        "4250e3eae3b1a15ad5db270b1f28db71007c64ff"),
    "rhel_9": (
        "U_RHEL_9_V2R9_STIG_SCAP_1-4_Benchmark-enhancedV13-signed.zip",
        "349b8e162696717079bd05139afe30d789c80f6a"),
}

def local(node):
    return node.tag.rsplit("}",1)[-1]

def source_objects(xml):
    root = ET.fromstring(xml)
    return [e for e in root.iter() if local(e).endswith("_object") and e.get("id")]

def inspect_candidate(candidate, objects):
    matches = [obj for obj in objects if obj.get("comment") == candidate["outer_title"]]
    matching = []
    for obj in matches:
        direct_filters = [child for child in obj if local(child) == "filter"]
        sets = [child for child in obj if local(child) == "set"]
        actions = [f.get("action","exclude") for f in direct_filters]
        matching.append({
            "id": obj.get("id"), "source_object_tag": local(obj),
            "direct_filter_actions": actions, "direct_filter_states": [(f.text or "").strip() for f in direct_filters],
            "source_has_set": bool(sets),
            "source_command": next(((c.text or "").strip() for c in obj if local(c)=="command"),None),
        })
    confirmed = (len(matching)==1 and not matching[0]["source_has_set"]
                 and matching[0]["direct_filter_actions"] == candidate["filters"])
    return {
        "assessment":candidate["assessment"],"test_id":candidate["test_id"],
        "capability":candidate["capability"],"path":candidate["path"],
        "match_count":len(matching),
        "source_candidates":matching,
        "source_direct_filter_without_set_confirmed":confirmed,
        "status":("UNIQUE_DIRECT_OVAL_FILTER_NO_SET" if confirmed
                  else "SOURCE_REVIEW_REQUIRED"),
    }

def git_blob_digest(data):
    return hashlib.sha1(b"blob "+str(len(data)).encode("ascii")+b"\0"+data).hexdigest()

def audit(census, zip_dir, *, assert_six=False):
    if not isinstance(census.get("candidate_entries"),list):
        raise ValueError("candidate census missing")
    sources = {}
    for namespace,(name,git_sha) in PINS.items():
        raw=(zip_dir/name).read_bytes()
        if git_blob_digest(raw)!=git_sha:
            raise ValueError("original source archive changed: "+name)
        with zipfile.ZipFile(zip_dir/name) as archive:
            xml_paths=[p for p in archive.namelist() if p.endswith(".xml")]
            if len(xml_paths)!=1: raise ValueError("expected one exact SCAP XML for "+name)
            sources[namespace]={
                "objects":source_objects(archive.read(xml_paths[0])),
                "source_zip_sha256":hashlib.sha256(raw).hexdigest(),
                "source_xml":xml_paths[0],
            }
    result=[]
    for candidate in census["candidate_entries"]:
        parts=candidate["path"].split("/")
        if len(parts)<3 or parts[0]!="authoring" or parts[1] not in sources:
            raise ValueError("unmapped candidate authoring source: "+candidate["path"])
        result.append(inspect_candidate(candidate,sources[parts[1]]["objects"]))
    observed=Counter(x["status"] for x in result)
    bluetooth=[x for x in result if x["assessment"]=="condition.bluetooth-installation.assessment"]
    if assert_six and (len(result)!=36 or len(bluetooth)!=1
                       or bluetooth[0]["status"]!="UNIQUE_DIRECT_OVAL_FILTER_NO_SET"
                       or bluetooth[0]["source_candidates"][0]["id"]!="oval:navy.navwar.niwcatlantic.scc.windows:obj:101"):
        raise ValueError("pinned Bluetooth or corpus provenance baseline changed")
    return {
        "status":"STRUCTURAL_SOURCE_FILTER_AUDIT_NOT_RUNTIME_PARITY",
        "candidate_test_object_instances":len(result),
        "by_source_classification":dict(sorted(observed.items())),
        "source_archive_checksums":{k:{"zip_sha256":v["source_zip_sha256"],"xml":v["source_xml"]}
                                    for k,v in sources.items()},
        "entries":result,
        "can_bulk_migrate_without_additional_parity_proof":False,
        "scanner_semantics_verified":False,
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--census",type=Path,required=True)
    p.add_argument("--source-dir",type=Path,required=True)
    p.add_argument("--report",type=Path,required=True)
    p.add_argument("--assert-six",action="store_true")
    a=p.parse_args()
    report=audit(json.loads(a.census.read_text()),a.source_dir,assert_six=a.assert_six)
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(report,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps({k:v for k,v in report.items() if k not in ("entries","source_archive_checksums")},indent=2))

if __name__=="__main__":
    main()
