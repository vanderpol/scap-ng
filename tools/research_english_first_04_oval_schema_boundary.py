#!/usr/bin/env python3
"""Pinned OVAL 5.12.3 Schematron source-validation boundary, issue #229/#235.

Distinguishes *a malformed inherited source pattern* from any necessary new
human authoring feature. Does not silently edit/reinterpret source content;
original OVAL XML must still be compared with the published conversion.
"""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET
import yaml

SCHEMA=Path("third_party/scap-1.4-schemas/oval_5.12.3/oval-definitions-schema.xsd")
PIN="03d64157ee295b81defe6f96cf7a3123410010ef4422d76bf5b7bb3ddbf30c9d"
TARGET="authoring/shared/assessments/linux/files/verify-boot-loader-root-admin-adminstrator.assessment.yaml"
RULE="oval-def:oval_definitions/oval-def:tests/*[@check_existence='none_exist']"
ASSERT="not(*[local-name()='state'])"
NS={"sch":"http://purl.oclc.org/dsdl/schematron"}

def audit(archive):
    root=ET.parse(SCHEMA).getroot()
    rules=root.findall(".//sch:rule",NS)
    matched=[el for el in rules if el.attrib.get("context")==RULE]
    if len(matched)!=1:raise AssertionError("Pinned 5.12.3 Schematron rule absent")
    checks=matched[0].findall("sch:assert",NS)
    if len(checks)!=1 or checks[0].attrib.get("test")!=ASSERT:
        raise AssertionError("Pinned 5.12.3 none_exist State restriction changed")
    forbidden={}
    if hashlib.sha256(Path(archive).read_bytes()).hexdigest()!=PIN:
        raise ValueError("Pinned source ZIP changed")
    tests=0
    with zipfile.ZipFile(archive) as z:
        for name in sorted(z.namelist()):
            if not (name.startswith("authoring/") and "/assessments/" in name and name.endswith(".yaml")):
                continue
            ass=(yaml.safe_load(z.read(name)) or {}).get("assessment") or {}
            if ass.get("mode")!="automated" or not ass.get("tests"):continue
            for test_id,test in ass["tests"].items():
                tests+=1
                if test.get("collected_items_require")=="none_exist" and test.get("states"):
                    forbidden.setdefault(name,[]).append({
                      "id":test_id,"state_count":len(test["states"]),
                      "capability":test.get("capability"),
                    })
    if set(forbidden)!={TARGET} or len(forbidden[TARGET])!=1:
        raise AssertionError("Source exception census changed: "+repr(forbidden)[:500])
    return {
      "result":"OVAL 5.12.3 SCHEMATRON RULE VERIFIED; NATIVE SOURCE PATTERN CONTRADICTS THIS RULE",
      "source_archive_sha256":PIN,
      "schema":str(SCHEMA),
      "schematron_context":RULE,
      "schematron_assertion":ASSERT,
      "tests_examined":tests,
      "native_source_violations":forbidden,
      "scope":"This assertion is about the equivalent OVAL Test shape. The original STIG OVAL XML has not been independently traced and cannot be assumed to contain the same illegal combination.",
      "required_action":"Trace converter provenance and original XML. Do not erase the attached State or accept an invented result without verifying equivalent semantics.",
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--archive",required=True)
    p.add_argument("--output")
    a=p.parse_args()
    report=audit(a.archive)
    if a.output:Path(a.output).write_text(json.dumps(report,indent=2,sort_keys=True)+chr(10))
    print(json.dumps(report,indent=2,sort_keys=True))

if __name__=="__main__":main()
