#!/usr/bin/env python3
"""#237 six pinned ORIGINAL NIWC SCAP 1.4 ZIP OVAL source inventory.

Reads immutable original ZIPs, never reinterprets converted 0.3 content as
original, and does not run scanners. Counts original OVAL declarations and
preserves per-stream source SHA-256 for future differential conversion gates.
"""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET

REVISION="8c8e5dff860af6b1290ee9273a282db24278f8d5"
FILES={
 "rhel_9":"U_RHEL_9_V2R9_STIG_SCAP_1-4_Benchmark-enhancedV13-signed.zip",
 "oracle_linux_9":"U_Oracle_Linux_9_V1R4_STIG_SCAP_1-4_Benchmark-enhancedV5-signed.zip",
 "ms_windows_11":"U_MS_Windows_11_V2R10_STIG_SCAP_1-4_Benchmark-enhancedV18-signed.zip",
 "ms_windows_server_2025":"U_MS_Windows_Server_2025_V1R1_STIG_SCAP_1-4_Benchmark-enhancedV1-signed.zip",
 "ms_windows_server_dns":"U_MS_Windows_Server_DNS_V2R3_STIG_SCAP_1-4_Benchmark-enhancedV8-signed.zip",
 "apache_server_2-4_unix_server":"U_Apache_Server_2-4_UNIX_Server_V3R2_STIG_SCAP_1-4_Benchmark-enhancedV2-signed.zip",
}
# Independently verified in the earlier frozen source extraction reproduction.
KNOWN_SHA={
 "rhel_9":"70aa6a16221df2c53b094b11b48b16aca1f6d7147c11123b655659ca7711dbb5",
 "ms_windows_server_2025":"2f46264b5fa21c8a033236121794ebe372314bf7458dac0aca4f81179fe7ece0",
 "ms_windows_server_dns":"f674b67e74acbd3037093d50e33dc20765bd9d45a6c9ed2be5d463d009a6c6b8",
 "apache_server_2-4_unix_server":"8894123788ba415373625eaecdbbd834f190668697803c3319393c11889f1b80",
}
OVAL="http://oval.mitre.org/XMLSchema/oval-definitions-5"
COMMON="http://oval.mitre.org/XMLSchema/oval-common-5"

def local(element):
    return element.tag.rsplit("}",1)[-1]

def archive_scan(path, *, expected_sha=None):
    if not path.is_file():
        raise ValueError("missing pinned original SCAP 1.4 archive: "+str(path))
    raw=path.read_bytes()
    digest=sha256(raw).hexdigest()
    if expected_sha is not None and digest!=expected_sha:
        raise ValueError("original SCAP archive SHA-256 does not match independent pin")
    tally=Counter();types=Counter();versions=Counter()
    registry_views=Counter();registry_selectors=Counter()
    merge_sort=Counter();capture_patterns=Counter()
    source_files=[];oval_documents=0;seen_ids={}
    with zipfile.ZipFile(path) as z:
        if z.testzip() is not None:
            raise ValueError("original source ZIP CRC validation failed")
        names=z.namelist()
        if len(names)>250:
            raise ValueError("source archive unexpectedly contains too many members")
        for name in sorted(names):
            if not name.lower().endswith(".xml") or name.startswith("/") or ".." in Path(name).parts:
                continue
            payload=z.read(name)
            if len(payload)>100_000_000:
                raise ValueError("source OVAL XML exceeds bounded extraction size")
            try:
                root=ET.fromstring(payload)
            except ET.ParseError:
                continue
            docs=[el for el in root.iter() if local(el)=="oval_definitions"]
            for oval_root in docs:
                oval_documents+=1
                source_files.append({"member":name,"sha256":sha256(payload).hexdigest()})
                gen=next((x for x in oval_root if local(x)=="generator"),None)
                if gen is not None:
                    ver=next((x for x in gen.iter() if local(x)=="schema_version"),None)
                    if ver is not None:versions[(ver.text or "").strip()]+=1
                for section in oval_root:
                    kind=local(section)
                    if kind not in {"definitions","tests","objects","states","variables"}:
                        continue
                    for item in section:
                        subtype=local(item)
                        tally[kind]+=1
                        types[subtype]+=1
                        identity=item.get("id")
                        if identity:
                            signature=ET.tostring(item,encoding="utf-8")
                            key=(kind,identity)
                            if key in seen_ids and seen_ids[key]!=signature:
                                tally["conflicting_duplicate_ids"]+=1
                            seen_ids[key]=signature
                        if subtype=="registry_object":
                            behaviors=next((e for e in item if local(e)=="behaviors"),None)
                            registry_views["source_explicit" if behaviors is not None and (
                                behaviors.get("windows_view") is not None
                            ) else "source_omitted"]+=1
                            for e in item:
                                if local(e) in {"key","name"}:
                                    registry_selectors[local(e)+":"+
                                        e.get("operation","equals")]+=1
                        # These OVAL functions are descendants of a
                        # declared local_variable, not top-level declarations.
                        # Inspect the complete expression tree while counting
                        # each function exactly once per original declaration.
                        if kind=="variables":
                            for operation in item.iter():
                                if operation is item:
                                    continue
                                operation_name=local(operation)
                                if operation_name=="merge":
                                    merge_sort["sort="+operation.get("sort","document")+
                                               ";order="+operation.get("order","ascending")]+=1
                                elif (operation_name=="regex_capture" and
                                      operation.get("pattern") is not None):
                                    capture_patterns["literal_patterns"]+=1
    if not oval_documents or not tally["definitions"] or not tally["tests"]:
        raise ValueError("pinned original ZIP contains no OVAL definitions and Tests")
    return {
       "zip_sha256":digest,
       "archived_members":len(names),
       "oval_xml_documents":oval_documents,
       "original_xml_members":source_files,
       "oval_schema_versions":dict(sorted(versions.items())),
       "declarations":dict(sorted(tally.items())),
       "object_test_variable_types":dict(sorted(types.items())),
       "registry_views":dict(sorted(registry_views.items())),
       "registry_key_name_selector_operations":dict(sorted(registry_selectors.items())),
       "merge_sort_forms":dict(sorted(merge_sort.items())),
       "regex_capture":dict(sorted(capture_patterns.items())),
       "has_source_XML":True,
       "scanner_execution_verified":False,
       "original_to_converted_graph_parity_verified":False,
    }


def inventory(root):
    streams={}
    for stig,name in FILES.items():
        source=Path(root)/name
        streams[stig]={"original_package":"Current/"+name,
                       "niwc_git_revision":REVISION,
                       "previously_known_sha256":KNOWN_SHA.get(stig),
                       **archive_scan(source,expected_sha=KNOWN_SHA.get(stig))}
    return {
        "format":"scap-ng-b-original-six-scap14-oval-census/0.1",
        "source_kind":"immutable_original_NIWC_SCAP_1.4",
        "git_revision":REVISION,
        "all_six_source_archives_verified":True,
        "original_to_B_parity_verified":False,
        "scanner_executable":False,
        "streams":streams,
    }


def markdown(r):
    lines=[
        "# Original six-STIG SCAP 1.4 OVAL source census",
        "",
        f"**Pinned immutable NIWC git revision:** \`{r['git_revision']}\`.",
        "**Source:** original six signed SCAP 1.4 ZIP archives, *not* the converted 0.3 YAML.",
        "**Not** an OVAL runtime evaluation, source graph translation, or scanner parity claim.",
        "",
        "| Stream | OVAL Tests | Objects | States | Variables | XML docs | Archive SHA-256 |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for k,s in r["streams"].items():
        d=s["declarations"]
        lines.append(f"| {k} | {d.get('tests',0)} | {d.get('objects',0)} | "
                     f"{d.get('states',0)} | {d.get('variables',0)} | "
                     f"{s['oval_xml_documents']} | \`{s['zip_sha256']}\` |")
    lines.extend([
        "",
        "Machine-readable [source inventory](original-scap14-oval-census.json)",
        "includes original XML member hashes, OVAL schema versions,",
        "capability families, missing/explicit registry view behavior,",
        "registry key/name comparison modes and source Variable operators.",
        "No Assessment is added to B's executable tally by this inventory.",
        "",
    ])
    return "\n".join(lines)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--original-archive-dir",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    p.add_argument("--markdown",required=True,type=Path)
    a=p.parse_args()
    result=inventory(a.original_archive_dir)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    a.markdown.parent.mkdir(parents=True,exist_ok=True)
    a.markdown.write_text(markdown(result))
    print(json.dumps({name:{
        "tests":d["declarations"].get("tests",0),
        "objects":d["declarations"].get("objects",0)}
        for name,d in result["streams"].items()},sort_keys=True))


if __name__=="__main__":
    main()
