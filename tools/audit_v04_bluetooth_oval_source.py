#!/usr/bin/env python3
"""Trace Windows 11 Bluetooth applicability to *actual* NIWC SCAP 1.4 OVAL.

Reports source Test/Object/State, any Set/Filter edges, and exact command text.
Does not reinterpret or change 0.4.0 grammar. Source is pinned by Git blob SHA
and is obtainable from niwc-atlantic/scap-content-library (V2R10 enhanced V18).
Refs #229 #232.
"""
import argparse
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

PINNED_GIT_BLOB = "712cc3176b1e44616aaf2f3ba5e62b299ad0643c"
ZIP_NAME = "U_MS_Windows_11_V2R10_STIG_SCAP_1-4_Benchmark-enhancedV18-signed.zip"
COMMAND = "(Get-PnpDevice -class bluetooth -status OK).class"

def local(element):
    return element.tag.rsplit("}", 1)[-1]

def original_trace(xml):
    root = ET.fromstring(xml)
    objects = {e.get("id"): e for e in root.iter()
               if local(e).endswith("_object") and e.get("id")}
    tests = {e.get("id"): e for e in root.iter()
             if local(e).endswith("_test") and e.get("id")}
    states = {e.get("id"): e for e in root.iter()
              if local(e).endswith("_state") and e.get("id")}
    def refs(elem):
        out = set()
        for child in elem.iter():
            for attr in ("object_ref", "state_ref", "test_ref"):
                if child.get(attr):
                    out.add(child.get(attr))
            if local(child) in ("object_reference", "filter", "set") and child.text and child.text.strip().startswith("oval:"):
                out.add(child.text.strip())
        return out
    direct = {ident for ident, obj in objects.items()
              if COMMAND.lower() in ET.tostring(obj, encoding="unicode").lower()}
    if not direct:
        raise ValueError("pinned SCAP XML has no Bluetooth PowerShell source Object")
    expanded = set(direct)
    for _ in range(len(objects)+1):
        changed = {ident for ident, obj in objects.items()
                   if ident not in expanded and refs(obj) & expanded}
        if not changed:
            break
        expanded.update(changed)
    impacted_tests = {ident for ident, e in tests.items() if refs(e) & expanded
                      or "bluetooth" in (e.get("comment") or "").lower()
                      and "installed" in (e.get("comment") or "").lower()}
    referenced_states = set()
    for ident in expanded:
        referenced_states.update(refs(objects[ident]) & states.keys())
    for ident in impacted_tests:
        referenced_states.update(refs(tests[ident]) & states.keys())
    report = {
        "status": "SOURCE_OVAL_SUBGRAPH_EXTRACTED_NOT_EQUIVALENCE_PROOF",
        "source_xml_sha256": hashlib.sha256(xml).hexdigest(),
        "source_command": COMMAND,
        "matched_command_objects": sorted(direct),
        "related_objects": {ident: {"comment": objects[ident].get("comment"),
                                   "tag": local(objects[ident]),
                                   "object_refs": sorted(refs(objects[ident]) & objects.keys()),
                                   "filter_refs": sorted(refs(objects[ident]) & states.keys()),
                                   "xml": ET.tostring(objects[ident], encoding="unicode")}
                            for ident in sorted(expanded)},
        "related_tests": {ident: {"comment": tests[ident].get("comment"),
                                 "check": tests[ident].get("check"),
                                 "xml": ET.tostring(tests[ident], encoding="unicode")}
                          for ident in sorted(impacted_tests)},
        "related_states": {ident: {"comment": states[ident].get("comment"),
                                  "xml": ET.tostring(states[ident], encoding="unicode")}
                           for ident in sorted(referenced_states)},
        "source_ovals_object_set_operators": sorted(
            {e.get("set_operator", "UNION(default)") for ident in expanded
             for e in objects[ident].iter() if local(e) == "set"}),
        "source_ovals_filter_actions": sorted(
            {e.get("action", "exclude(default)") for ident in expanded
             for e in objects[ident].iter() if local(e) == "filter"}),
        "full_scanner_result_parity": False,
    }
    return report

def trace_zip(data):
    git_sha = hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()
    if git_sha != PINNED_GIT_BLOB:
        raise ValueError("Windows 11 SCAP ZIP blob changed: " + git_sha)
    import io
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        names = [p for p in z.namelist() if p.endswith(".xml")]
        if len(names) != 1:
            raise ValueError("expected one SCAP XML: " + repr(names))
        report = original_trace(z.read(names[0]))
        report.update({"source_zip": ZIP_NAME,
                       "source_zip_git_blob_sha1": git_sha,
                       "source_zip_sha256": hashlib.sha256(data).hexdigest(),
                       "source_xml_name": names[0]})
        return report

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source-zip", type=Path, required=True)
    p.add_argument("--report", type=Path, required=True)
    a=p.parse_args()
    result=trace_zip(a.source_zip.read_bytes())
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(result,sort_keys=True,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(result,sort_keys=True,indent=2,ensure_ascii=False))

if __name__=="__main__":
    main()
